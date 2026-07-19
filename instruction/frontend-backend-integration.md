# HiReady — Frontend ↔ Backend Integration Guide

## Tujuan Dokumen

Panduan ini untuk agent yang akan menghubungkan SvelteKit frontend dengan FastAPI backend HiReady.
Seluruh halaman sudah ada dan sudah didesain. Tugas agent adalah **menyambungkan data dan komunikasi real-time** — bukan membuat ulang UI.

---

## Peta Proyek

```
Frontend (SvelteKit, port 5173)          Backend (FastAPI, port 8000)
─────────────────────────────            ────────────────────────────
src/
├── routes/
│   ├── +page.svelte                     (landing, tidak perlu backend)
│   ├── login/+page.svelte               ← better-auth (sudah jalan)
│   ├── register/+page.svelte            ← better-auth (sudah jalan)
│   ├── onboarding/
│   │   ├── +page.server.ts              ← fetch GET /api/institutions, /api/positions
│   │   └── +page.svelte                 ← kirim POST ke +page.server.ts (sudah ada form)
│   ├── dashboard/+page.svelte           ← fetch GET /api/sessions (history user)
│   ├── session/
│   │   ├── disclaimer/+page.svelte      ← navigasi ke interview, sudah ada
│   │   ├── interview/+page.svelte       ← INTEGRASI UTAMA: WebSocket + TTS + Viseme + STT
│   │   └── results/+page.svelte         ← fetch GET /api/sessions/{id}/report
│   └── history/+page.svelte             ← fetch GET /api/sessions (list lengkap)
└── lib/
    ├── FaceAnimator.ts                  ← SUDAH ADA: class animasi morph target Three.js
    ├── lipSync.ts                       ← SUDAH ADA: fetch POST /api/speech + drive animator
    ├── visemeController.ts              ← SUDAH ADA: helper setMorph, collectMorphMeshes
    ├── visemeMap.ts                     ← SUDAH ADA: mapping viseme ID → shape key weights
    ├── autoBlink.ts                     ← SUDAH ADA: auto blink loop untuk avatar
    └── emotionPresets.ts               ← SUDAH ADA: preset ekspresi wajah (happy, sad, dll)
```

---

## Arsitektur Komunikasi

```
                    ┌─────────────────┐
                    │   SvelteKit     │
                    │   (Browser)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼───────────────┐
              │              │               │
    REST API          WebSocket         REST API
    (setup)        (sesi aktif)         (hasil)
              │              │               │
    POST /api/sessions   ws://...    GET /api/sessions
    GET  /api/avatars    /ws/{id}        /{id}/report
    GET  /api/positions               GET /api/sessions
              │              │
    ┌─────────▼──────────────▼─────────┐
    │           FastAPI Backend         │
    │                                   │
    │  ┌──────────┐  ┌───────────────┐  │
    │  │  brain.py│  │  whisper STT  │  │
    │  │  (LLM)   │  │  (audio→text) │  │
    │  └──────────┘  └───────────────┘  │
    │  ┌──────────────────────────────┐  │
    │  │  Kokoro TTS → audio + viseme │  │
    │  └──────────────────────────────┘  │
    └───────────────────────────────────┘
```

---

## Bagian 1 — Onboarding (`/onboarding`)

### Yang Harus Dilakukan

File `+page.server.ts` perlu mengambil data institusi dan posisi dari backend untuk ditampilkan di UI (yang sudah ada).

**`src/routes/onboarding/+page.server.ts`** — tambahkan/ganti load function:

```typescript
import type { PageServerLoad, Actions } from './$types';
import { redirect, fail } from '@sveltejs/kit';

const BACKEND_URL = 'http://localhost:8000';

export const load: PageServerLoad = async ({ fetch, locals }) => {
  const session = await locals.auth.api.getSession({ headers: locals.headers });
  if (!session) throw redirect(302, '/login');

  const [instRes, posRes] = await Promise.all([
    fetch(`${BACKEND_URL}/api/institutions`),
    fetch(`${BACKEND_URL}/api/positions`),
  ]);

  return {
    institutions: await instRes.json(),
    positions: await posRes.json(),
  };
};

export const actions: Actions = {
  default: async ({ request, fetch, locals }) => {
    const session = await locals.auth.api.getSession({ headers: locals.headers });
    if (!session) throw redirect(302, '/login');

    const data = await request.formData();
    const institutionId = data.get('institutionId') as string;
    const positionId = data.get('positionId') as string;

    if (!institutionId || !positionId) {
      return fail(400, { message: 'Pilih institusi dan posisi terlebih dahulu.' });
    }

    // Simpan ke profil user via backend
    await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: session.user.id,
        targetInstitutionId: institutionId,
        targetPositionId: positionId,
      }),
    });

    throw redirect(302, '/dashboard');
  },
};
```

**Endpoint backend yang dibutuhkan:**
- `GET /api/institutions` → return `MasterInstitution[]`
- `GET /api/positions` → return `MasterPosition[]`
- `PATCH /api/profile` → update `targetInstitutionId` dan `targetPositionId` di `user_profile`

---

## Bagian 2 — Halaman Interview (`/session/interview`)

Ini adalah **inti dari seluruh integrasi**. Halaman ini perlu:

1. Inisialisasi sesi via REST
2. Buka koneksi WebSocket
3. Menerima pertanyaan dari backend → jalankan TTS → drive viseme avatar
4. Rekam audio user → kirim ke backend via WebSocket → backend jalankan STT + LLM
5. Menampilkan transkrip percakapan secara real-time

### 2.1 — State yang Perlu Ditambahkan

Ganti seluruh `<script>` di `+page.svelte` dengan ini (pertahankan semua HTML/template, hanya script yang diubah):

```typescript
<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount, onDestroy } from 'svelte';
  import { FaceAnimator } from '$lib/FaceAnimator';
  import { speakWithBackend } from '$lib/lipSync';
  import { startAutoBlink } from '$lib/autoBlink';
  import { EMOTIONS } from '$lib/emotionPresets';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

  const BACKEND_URL  = 'http://localhost:8000';
  const BACKEND_WS   = 'ws://localhost:8000';

  // ── Media ──
  let videoElement: HTMLVideoElement;
  let canvasElement: HTMLCanvasElement;   // untuk Three.js avatar
  let stream: MediaStream | null = null;
  let micMuted = $state(false);
  let camOff   = $state(false);

  // ── Timer ──
  let seconds = $state(0);
  let timerInterval: ReturnType<typeof setInterval>;
  const timeDisplay = $derived(() => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  });

  // ── Session & WebSocket ──
  let sessionId    = $state<string | null>(null);
  let ws           = $state<WebSocket | null>(null);
  let wsStatus     = $state<'connecting' | 'connected' | 'disconnected'>('connecting');

  // ── Percakapan ──
  type Message = { role: 'interviewer' | 'user'; text: string; time: string };
  let messages = $state<Message[]>([]);
  let isListening  = $state(false);   // true saat menunggu jawaban user
  let isSpeaking   = $state(false);   // true saat avatar sedang TTS
  let transcriptOpen = $state(false);

  // ── Avatar (Three.js) ──
  let animator: FaceAnimator | null = null;
  let stopBlink: (() => void) | null = null;

  // ── STT (MediaRecorder) ──
  let mediaRecorder: MediaRecorder | null = null;
  let audioChunks: Blob[] = [];

  // ─────────────────────────────────────────────
  // INIT
  // ─────────────────────────────────────────────
  onMount(async () => {
    timerInterval = setInterval(() => seconds++, 1000);

    // Kamera user
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoElement) videoElement.srcObject = stream;
    } catch (e) {
      console.error('Camera access failed:', e);
    }

    // Avatar Three.js — load GLB dari /static/face/
    await initAvatar();

    // Buat sesi di backend → dapat sessionId
    await initSession();
  });

  onDestroy(() => {
    clearInterval(timerInterval);
    stream?.getTracks().forEach(t => t.stop());
    ws?.close();
    stopBlink?.();
  });
```

### 2.2 — Inisialisasi Avatar Three.js

```typescript
  async function initAvatar() {
    // Canvas sudah ada di template HTML (tambahkan id="avatar-canvas")
    const canvas = document.getElementById('avatar-canvas') as HTMLCanvasElement;
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, canvas.clientWidth / canvas.clientHeight, 0.1, 10);
    camera.position.set(0, 1.6, 2.5);

    scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(1, 2, 3);
    scene.add(dirLight);

    // Ganti nama file GLB sesuai avatar yang dipilih user
    // File tersimpan di /static/face/{avatarId}.glb
    const loader = new GLTFLoader();
    loader.setDRACOLoader(/* setup draco dari /static/draco/ */);

    loader.load('/face/default.glb', (gltf) => {
      scene.add(gltf.scene);
      animator = new FaceAnimator(gltf.scene);
      stopBlink = startAutoBlink(animator);
    });

    const clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      animator?.update(clock.getDelta());
      renderer.render(scene, camera);
    }
    animate();
  }
```

### 2.3 — Inisialisasi Sesi & WebSocket

```typescript
  async function initSession() {
    // 1. Buat sesi baru via REST
    const res = await fetch(`${BACKEND_URL}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // userId didapat dari cookie session better-auth yang dikirim otomatis
    });
    const { session_id } = await res.json();
    sessionId = session_id;

    // 2. Buka WebSocket
    ws = new WebSocket(`${BACKEND_WS}/ws/${sessionId}`);

    ws.onopen = () => {
      wsStatus = 'connected';
      ws!.send(JSON.stringify({ type: 'START_INTERVIEW', sessionId }));
    };

    ws.onclose = () => {
      wsStatus = 'disconnected';
    };

    ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      await handleBackendMessage(msg);
    };
  }
```

### 2.4 — Handler Pesan dari Backend

```typescript
  async function handleBackendMessage(msg: Record<string, unknown>) {
    switch (msg.type) {

      // Backend mengirim pertanyaan baru
      case 'QUESTION': {
        const text = msg.text as string;

        // Tambah ke transcript UI
        messages = [...messages, {
          role: 'interviewer',
          text,
          time: timeDisplay(),
        }];

        // Ubah ekspresi avatar sesuai persona (opsional)
        if (msg.persona === 'intimidating' && animator) {
          animator.setExpression(EMOTIONS.angry);
        } else if (msg.persona === 'friendly' && animator) {
          animator.setExpression(EMOTIONS.happy);
        }

        // Jalankan TTS → sekaligus drive lipsync via speakWithBackend()
        // speakWithBackend sudah ada di lib/lipSync.ts, memanggil POST /api/speech
        isSpeaking = true;
        if (animator) {
          await speakWithBackend(text, animator);
        }
        isSpeaking = false;

        // Setelah avatar selesai bicara → mulai rekam
        startRecording();
        break;
      }

      // Backend memberi feedback setelah jawaban diproses
      case 'FEEDBACK': {
        // Feedback tidak perlu ditampilkan sebagai bubble chat tersendiri
        // cukup simpan untuk laporan akhir
        // Opsional: tampilkan badge singkat di UI
        break;
      }

      // Sesi selesai dari backend (misal: sudah 10 pertanyaan)
      case 'SESSION_END': {
        stopRecording();
        goto(`/session/results?sessionId=${sessionId}`);
        break;
      }

      // Status STT (backend sedang memproses audio)
      case 'PROCESSING': {
        isListening = false;
        break;
      }
    }
  }
```

### 2.5 — STT: Rekam Audio User → Kirim ke Backend

```typescript
  function startRecording() {
    if (!stream || mediaRecorder?.state === 'recording') return;
    isListening = true;
    audioChunks = [];

    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      isListening = false;
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

      // Opsi A — Kirim audio sebagai ArrayBuffer via WebSocket
      // Backend akan menjalankan faster-whisper untuk transkripsi
      const buffer = await audioBlob.arrayBuffer();
      ws?.send(buffer);

      // Tambahkan placeholder transcript di UI (akan diupdate saat backend reply)
      messages = [...messages, {
        role: 'user',
        text: '...',    // diupdate saat TRANSCRIPT event tiba
        time: timeDisplay(),
      }];
    };

    mediaRecorder.start();
  }

  function stopRecording() {
    if (mediaRecorder?.state === 'recording') {
      mediaRecorder.stop();
    }
  }

  // Tombol mic toggle — matikan recording juga
  function toggleMic() {
    if (!stream) return;
    micMuted = !micMuted;
    stream.getAudioTracks().forEach(t => (t.enabled = !micMuted));
    if (micMuted && mediaRecorder?.state === 'recording') {
      stopRecording();
    }
  }

  function toggleCamera() {
    if (!stream) return;
    camOff = !camOff;
    stream.getVideoTracks().forEach(t => (t.enabled = !camOff));
  }

  async function endSession() {
    stopRecording();
    ws?.send(JSON.stringify({ type: 'END_SESSION', sessionId }));
    ws?.close();
    goto(`/session/results?sessionId=${sessionId}`);
  }
</script>
```

### 2.6 — Perubahan HTML Template

Di template HTML yang sudah ada, lakukan perubahan berikut:

**1. Ganti `<img>` avatar placeholder dengan `<canvas>` untuk Three.js:**
```html
<!-- HAPUS ini: -->
<img alt="Interviewer Avatar" src="..." class="..." />

<!-- GANTI dengan: -->
<canvas id="avatar-canvas" class="absolute inset-0 h-full w-full"></canvas>
```

**2. Tambahkan indikator status di status bar:**
```html
<!-- Ganti badge STABIL dengan status WebSocket dinamis -->
<span class="...">{wsStatus === 'connected' ? 'STABIL' : 'MENGHUBUNGKAN...'}</span>
```

**3. Ganti "Sedang mendengarkan..." placeholder dengan kondisi dinamis:**
```html
<!-- Listening indicator — tampilkan hanya saat isListening === true -->
{#if isListening}
  <div class="flex max-w-[90%] items-center gap-3">
    ...
    <span class="animate-pulse text-[13px] text-white/70">Sedang mendengarkan...</span>
  </div>
{/if}

{#if isSpeaking}
  <div class="flex max-w-[90%] items-center gap-3">
    ...
    <span class="animate-pulse text-[13px] text-white/70">Pewawancara sedang berbicara...</span>
  </div>
{/if}
```

**4. Render messages array ke bubble chat:**
```html
<!-- Dalam <div class="flex-1 space-y-4 overflow-y-auto p-4"> -->
{#each messages as msg (msg.time + msg.role)}
  {#if msg.role === 'interviewer'}
    <div class="flex max-w-[90%] gap-3">
      <!-- bubble interviewer (gunakan style yang sudah ada) -->
      <p class="text-[13px] leading-relaxed text-white">{msg.text}</p>
    </div>
  {:else}
    <div class="ml-auto flex max-w-[90%] flex-row-reverse gap-3">
      <!-- bubble user (gunakan style yang sudah ada) -->
      <p class="text-[13px] leading-relaxed text-white">{msg.text}</p>
    </div>
  {/if}
{/each}
```

**5. Tombol "Akhiri Sesi" — ganti `goto` langsung dengan `endSession()`:**
```html
<button onclick={endSession} class="...">
  Akhiri Sesi
</button>
```

---

## Bagian 3 — TTS & Viseme (Arsitektur Detail)

### Alur Lengkap Saat Backend Mengirim Pertanyaan

```
Backend kirim { type: 'QUESTION', text: '...' }
        │
        ▼
Frontend handleBackendMessage()
        │
        ▼
speakWithBackend(text, animator)     ← lib/lipSync.ts (SUDAH ADA)
        │
        ├── fetch POST /api/speech { text }
        │         │
        │         ▼ (Backend)
        │     Kokoro TTS → generate audio WAV + amplitude array
        │     Return: { audio: base64, visemes: number[] }
        │
        ├── Decode base64 → Blob → AudioContext → play()
        │
        └── Setiap frame via requestAnimationFrame:
              elapsed / frameInterval = frame index
              visemes[frame] * 3.5 → animator.setMouth(amplitude)
              animator.update(delta) → lerp morph targets di Three.js mesh
```

### Yang Perlu Dikonfirmasi di Backend (`/api/speech`)

Backend sudah ada endpoint `/api/speech`. Pastikan response-nya persis:

```json
{
  "audio": "<base64 encoded MP3/WAV>",
  "visemes": [0.0, 0.12, 0.45, 0.8, 0.6, ...]
}
```

Field `visemes` adalah array amplitudo float per frame audio. `lipSync.ts` sudah mengasumsikan:
- Sample rate: 24000 Hz
- Hop length: 512 samples
- Frame interval: `(512 / 24000) * 1000 = 21.33ms`

Jika Kokoro menggunakan parameter berbeda, update konstanta `frameInterval` di `lipSync.ts`.

---

## Bagian 4 — Dashboard (`/dashboard`)

### Yang Harus Dilakukan

Ganti data hardcoded riwayat sesi dengan data real dari backend.

**`src/routes/dashboard/+page.server.ts`** — buat file baru:

```typescript
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

const BACKEND_URL = 'http://localhost:8000';

export const load: PageServerLoad = async ({ fetch, locals }) => {
  const session = await locals.auth.api.getSession({ headers: locals.headers });
  if (!session) throw redirect(302, '/login');

  const [profileRes, sessionsRes] = await Promise.all([
    fetch(`${BACKEND_URL}/api/profile/${session.user.id}`),
    fetch(`${BACKEND_URL}/api/sessions?userId=${session.user.id}&limit=5`),
  ]);

  return {
    user: session.user,
    profile: await profileRes.json(),      // totalSessions, avgOverallScore
    recentSessions: await sessionsRes.json(),
  };
};
```

**Di `+page.svelte`**, ganti data hardcoded:
- `8 Sesi Selesai` → `data.profile.totalSessions`
- `85` (skor rata-rata) → `data.profile.avgOverallScore`
- Array riwayat sesi hardcoded → `data.recentSessions`

**Endpoint backend yang dibutuhkan:**
- `GET /api/profile/{userId}` → return data `user_profile`
- `GET /api/sessions?userId=...&limit=5` → return list `interview_session` terakhir

---

## Bagian 5 — Hasil Sesi (`/session/results`)

### Yang Harus Dilakukan

Halaman results saat ini menggunakan data hardcoded. Ganti dengan data dari `session_report`.

**`src/routes/session/results/+page.server.ts`** — buat file baru:

```typescript
import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

const BACKEND_URL = 'http://localhost:8000';

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
  const session = await locals.auth.api.getSession({ headers: locals.headers });
  if (!session) throw redirect(302, '/login');

  const sessionId = url.searchParams.get('sessionId');
  if (!sessionId) throw redirect(302, '/dashboard');

  const res = await fetch(`${BACKEND_URL}/api/sessions/${sessionId}/report`);
  const report = await res.json();

  return { report };
};
```

**Di `+page.svelte`**, ganti semua data hardcoded:
- `dimensions` array → map dari `data.report` fields: `communicationScore`, `consistencyScore`, `confidenceScore`, `stressResistanceScore`
- `questions` array → `data.report.sessionTurns` (pertanyaan + transkrip jawaban + feedback per turn)
- `fillerWords` array → `data.report.fillerWordBreakdown`
- Header (institusi, posisi, tanggal, durasi) → dari data report

**Endpoint backend yang dibutuhkan:**
- `GET /api/sessions/{sessionId}/report` → return `session_report` + `session_turn[]` terkait

---

## Bagian 6 — Environment Variables

Tambahkan file `.env` di root frontend:

```env
# Backend URL
PUBLIC_BACKEND_URL=http://localhost:8000
PUBLIC_BACKEND_WS=ws://localhost:8000
```

Ganti semua hardcoded `http://localhost:8000` dengan:
```typescript
import { PUBLIC_BACKEND_URL, PUBLIC_BACKEND_WS } from '$env/static/public';
```

---

## Bagian 7 — Draco Loader Setup (untuk GLB Avatar)

File Draco sudah ada di `/static/draco/`. Setup di `initAvatar()`:

```typescript
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');   // path ke /static/draco/

const loader = new GLTFLoader();
loader.setDRACOLoader(dracoLoader);
```

File GLB avatar disimpan di `/static/face/{avatarId}.glb`. Nama file harus sesuai dengan field `interviewAvatar.id` atau `interviewAvatar.glbUrl` yang dikembalikan endpoint `GET /api/avatars`.

---

## Bagian 8 — Ringkasan Endpoint Backend yang Dibutuhkan Frontend

| Method | Path | Dipakai di | Keterangan |
|--------|------|------------|------------|
| `GET` | `/api/institutions` | `/onboarding` | List semua `master_institution` |
| `GET` | `/api/positions` | `/onboarding` | List semua `master_position` |
| `GET` | `/api/avatars` | `/session/interview` | List avatar + glbUrl |
| `PATCH` | `/api/profile` | `/onboarding` | Update target institusi & posisi |
| `GET` | `/api/profile/{userId}` | `/dashboard` | Statistik agregat user |
| `POST` | `/api/sessions` | `/session/interview` | Buat sesi baru, return `session_id` |
| `GET` | `/api/sessions` | `/dashboard`, `/history` | List sesi user |
| `GET` | `/api/sessions/{id}/report` | `/session/results` | Laporan lengkap pasca sesi |
| `POST` | `/api/speech` | `lib/lipSync.ts` | TTS → return audio + viseme amplitudo |
| `WS` | `/ws/{sessionId}` | `/session/interview` | Komunikasi real-time sesi wawancara |

---

## Bagian 9 — WebSocket Message Protocol

### Frontend → Backend

| Event | Payload | Kapan |
|-------|---------|-------|
| `START_INTERVIEW` | `{ type, sessionId }` | Setelah WS terbuka |
| `END_SESSION` | `{ type, sessionId }` | User klik "Akhiri Sesi" |
| `ArrayBuffer` | raw audio bytes (webm) | Setelah user selesai menjawab |

### Backend → Frontend

| Event | Payload | Kapan |
|-------|---------|-------|
| `QUESTION` | `{ type, text, persona, turnNumber }` | Setiap pertanyaan baru |
| `TRANSCRIPT` | `{ type, text }` | Setelah STT selesai, update bubble user |
| `FEEDBACK` | `{ type, score, feedback }` | Setelah LLM menilai jawaban |
| `PROCESSING` | `{ type }` | Saat backend memproses audio |
| `SESSION_END` | `{ type, sessionId }` | Sesi selesai (10 pertanyaan tercapai) |
| `ERROR` | `{ type, message }` | Jika terjadi error di backend |

---

## Catatan Penting untuk Agent

1. **Jangan ubah HTML/template** yang sudah ada di halaman-halaman kecuali penggantian `<img>` avatar dengan `<canvas>` dan rendering `messages` array.

2. **`lib/lipSync.ts` sudah siap dipakai** — cukup panggil `speakWithBackend(text, animator)` dari handler WebSocket.

3. **`lib/FaceAnimator.ts` sudah siap** — cukup buat instance-nya setelah GLB dimuat, lalu panggil `animator.update(delta)` di animation loop.

4. **CORS** — pastikan FastAPI mengizinkan origin `http://localhost:5173` di middleware CORS.

5. **Better-auth** sudah berjalan — cookie session dikirim otomatis di setiap `fetch` dari `+page.server.ts`. Untuk request dari browser langsung (WebSocket, `fetch` di `<script>`), tambahkan `credentials: 'include'` jika perlu autentikasi.

6. **Urutan implementasi yang disarankan:**
   - Onboarding (paling mudah, REST saja)
   - Dashboard (REST, data sederhana)
   - Interview page (paling kompleks, kerjakan terakhir)
   - Results page (REST, mapping data dari report)