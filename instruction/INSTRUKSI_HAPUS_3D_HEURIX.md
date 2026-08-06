# Instruksi: Hapus Fitur 3D (Three.js) dari Heurix

**Untuk:** Agen CLI (Claude Code / Gemini CLI)
**Repo:** heurix (frontend SvelteKit `src/`, backend FastAPI `app/`)
**Tujuan:** Menghapus seluruh rendering avatar 3D berbasis Three.js/GLB, mengganti dengan avatar 2D SVG yang sudah ada (`Avatar.svelte`), TANPA merusak: audio TTS, lip-sync (viseme), auto-blink, ekspresi persona, dan fitur analisis wajah webcam (MediaPipe) yang dipakai untuk skor "Raut Wajah" & "Kontak Mata" di laporan hasil.

> **Baca seluruh dokumen ini dulu sebelum eksekusi.** Urutan langkah penting karena banyak file saling bergantung (lipSync ↔ FaceAnimator ↔ Three.js).

---

## ⚠️ Catatan Penting Sebelum Mulai

1. **"Load model GLB berat" terjadi di BROWSER (client), bukan di backend FastAPI.** Backend Python tidak pernah memproses file `.glb` — backend hanya menyimpan `glbUrl` (string path) di tabel `interview_avatar` dan mengirimkannya ke frontend. Jadi menghapus 3D **akan membuat frontend jauh lebih ringan** (bundle JS lebih kecil, tidak ada fetch+parse GLB ~beberapa MB, tidak ada inisialisasi WebGL), tapi **tidak otomatis mempercepat backend saat start sesi** — kalau backend memang terasa lambat saat start sesi, penyebabnya kemungkinan besar di tempat lain (load model Whisper/F5-TTS, koneksi Groq API, dsb), bukan GLB. Tetap ikuti instruksi ini untuk sisi backend (pembersihan kolom/response yang tidak lagi relevan), tapi jangan berharap ini menyelesaikan masalah startup backend jika penyebabnya bukan ini.
2. **JANGAN hapus MediaPipe (`@mediapipe/tasks-vision`, `FaceLandmarker`).** Ini sistem terpisah yang menganalisis wajah user dari webcam untuk skor "Raut Wajah" dan "Kontak Mata" di laporan hasil interview — sama sekali tidak terkait Three.js, meski kebetulan kodenya saat ini nempel di file yang sama (`interview/+page.svelte`).
3. **JANGAN hapus audio TTS / WebSocket / STT / VAD / recording.** Yang dihapus HANYA rendering visual 3D dan logic yang murni ada untuk menganimasikan model 3D tersebut.
4. Backend `InterviewAvatar.glbUrl` (kolom DB, `nullable=False`) — **JANGAN drop kolom dari database/migration** dalam task ini. Cukup berhenti dipakai di response API yang dikonsumsi frontend. Drop kolom butuh migration terpisah dan review manual (breaking change kalau ada data lama / API lain yang masih baca kolom ini).

---

## Peta Dependensi (baca dulu)

File yang **MURNI Three.js** (aman dihapus total setelah refactor step di bawah):
- `src/src/lib/FaceAnimator.ts` — wrapper Three.js morph target
- `src/src/lib/visemeController.ts` — helper morph mesh Three.js
- `src/src/lib/avatarCache.ts` — cache ArrayBuffer khusus GLB

File yang **BERCAMPUR** (3D + logic lain yang harus dipertahankan, perlu di-refactor, bukan dihapus):
- `src/src/lib/lipSync.ts` — `speakWithBackend()` memutar audio TTS DAN menggerakkan mulut 3D lewat parameter `animator: FaceAnimator`. Audio harus tetap jalan, hanya parameter animator yang diganti.
- `src/src/lib/autoBlink.ts` — `startAutoBlink()` menerima `FaceAnimator`, hanya untuk trigger kedip. Logic timernya generik, cuma perlu ganti target.
- `src/src/routes/session/interview/+page.svelte` (1495 baris) — **file paling kritis**. Di dalamnya:
  - Rendering 3D (`initAvatar()`, `animate()` render loop, resource Three.js) → **DIHAPUS**
  - Analisis wajah MediaPipe (`initMediaPipe()`, blok `// ── FACE ANALYSIS (MediaPipe) ──` di dalam `animate()`) → **DIPERTAHANKAN**, tapi harus dilepas dari render loop Three.js karena sekarang sampling wajah numpang di `requestAnimationFrame` milik Three.js.
  - Ekspresi persona (`EMOTIONS.angry`, `EMOTIONS.happy` saat ganti persona, `isThinking` state) → **opsional dipertahankan** dalam bentuk sederhana (ganti warna/viseme avatar 2D), atau boleh di-drop kalau agen menilai `Avatar.svelte` tidak punya prop yang cocok — ini bukan fitur inti, jangan dipaksakan.

File yang **TIDAK terkait 3D sama sekali** (jangan disentuh):
- `src/src/lib/server/*` (auth, db)
- Semua route selain `session/interview` dan `session/select-avatar`
- WebSocket handler backend (`app/app/api/websocket.py`) kecuali bagian yang eksplisit disebut di bawah

---

## LANGKAH FRONTEND

### Step 1 — Refactor `lipSync.ts` (lepas ketergantungan ke `FaceAnimator`)

Ubah signature `speakWithBackend` agar tidak butuh objek `FaceAnimator`, cukup callback angka amplitude mulut:

```ts
// SEBELUM:
export async function speakWithBackend(
  text: string,
  animator: FaceAnimator,
  pregeneratedData?: { audio: string; visemes: number[] }
): Promise<void>

// SESUDAH:
export async function speakWithBackend(
  text: string,
  onMouthUpdate: (amplitude: number) => void,
  pregeneratedData?: { audio: string; visemes: number[] }
): Promise<void>
```

- Hapus `import { FaceAnimator } from "./FaceAnimator";`
- Ganti setiap `animator.setMouth(x)` → `onMouthUpdate(x)` (ada di `startFallbackAnimation`, `updateMouth`, `onended`, `onerror`, dan catch block — total 5 titik).
- Sisa logic (fetch `/api/proxy/api/speech`, decode base64, `Audio` element, `requestAnimationFrame` loop untuk timing viseme) **JANGAN diubah** — itu semua logic audio, bukan 3D.

### Step 2 — Refactor `autoBlink.ts`

```ts
// SEBELUM:
export function startAutoBlink(animator: FaceAnimator): () => void

// SESUDAH:
export function startAutoBlink(onBlinkChange: (isBlinking: boolean) => void): () => void
```
Ganti `animator.setExpression({ Eye_Blink: 1.0 })` → `onBlinkChange(true)`, dan `animator.setExpression({ Eye_Blink: 0 })` → `onBlinkChange(false)`. Hapus `import type { FaceAnimator }`.

### Step 3 — Hapus file murni Three.js

```bash
rm src/src/lib/FaceAnimator.ts
rm src/src/lib/visemeController.ts
rm src/src/lib/avatarCache.ts
```

### Step 4 — Refactor `session/interview/+page.svelte`

Lakukan berurutan:

**4a. Bersihkan import (baris ~1-19):**
Hapus:
```ts
import { FaceAnimator } from '$lib/FaceAnimator';
import { loadGLBCached } from '$lib/avatarCache';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
```
Tambahkan:
```ts
import Avatar from '$lib/Avatar.svelte';
```
`import { EMOTIONS } from '$lib/emotionPresets';` — pertahankan HANYA jika Step 4d (opsional ekspresi) dipakai; kalau tidak, hapus juga.

**4b. Ganti state Three.js (baris ~54-60) dengan state avatar 2D:**
Hapus:
```ts
let renderer: THREE.WebGLRenderer | undefined;
let scene: THREE.Scene | undefined;
let camera: THREE.PerspectiveCamera | undefined;
let resizeObserver: ResizeObserver | undefined;
let animationFrameId: number | undefined;
let modelRoot: THREE.Object3D | undefined;
let animator: FaceAnimator | null = null;
```
Tambahkan:
```ts
let mouthOpenness = $state(0);
let isBlinking = $state(false);
let stopBlink: (() => void) | null = null; // tetap dipakai
```
`canvasElement: HTMLCanvasElement` — cek dulu apakah dipakai tempat lain (mis. screenshot/recording). Kalau hanya dipakai Three.js, boleh dihapus juga.

**4c. Hapus fungsi `initAvatar()` (Three.js scene/GLTFLoader) SELURUHNYA.**
Di `onMount`, ganti pemanggilan:
```ts
// SEBELUM
initAvatar(glbUrl, cameraConfig);
```
menjadi: hapus baris ini saja. `avatarName`, `avatarDescription`, `avatarThumbnail` tetap diisi dari `sessionData.avatar` seperti sebelumnya (baris di atasnya, tidak diubah) — itu dipakai `Avatar.svelte`/UI, bukan 3D.
`glbUrl` dan `cameraConfig` yang di-destructure dari `sessionData.avatar` boleh dihapus jika tidak dipakai lagi setelah ini.

**4d. Pisahkan sampling MediaPipe dari render loop Three.js.**
Fungsi `animate()` saat ini menggabungkan render 3D + sampling wajah dalam satu `requestAnimationFrame`. Karena sampling wajah cuma jalan tiap `FACE_SAMPLE_INTERVAL` (3000ms), ganti jadi `setInterval` mandiri — lebih murah daripada RAF 60fps:

```ts
let faceSampleIntervalId: ReturnType<typeof setInterval> | undefined;

function startFaceSampling() {
  faceSampleIntervalId = setInterval(() => {
    if (!faceLandmarker || !browser || camOff) return;
    const activeVideo = videoElementDesktop || videoElementMobile;
    if (!activeVideo || activeVideo.readyState < 2) return;

    const now = performance.now();
    const results = faceLandmarker.detectForVideo(activeVideo, now);
    if (results.faceBlendshapes?.[0]) {
      const shapes = results.faceBlendshapes[0].categories;
      const smileLeft = shapes.find((s) => s.categoryName === 'mouthSmileLeft')?.score || 0;
      const smileRight = shapes.find((s) => s.categoryName === 'mouthSmileRight')?.score || 0;
      const avgSmile = (smileLeft + smileRight) / 2;
      const hasLandmarks = results.faceLandmarks?.[0]?.length > 0;

      if (ws && wsStatus === 'connected') {
        ws.send(JSON.stringify({
          type: 'FACE_METRICS',
          metrics: { smileScore: avgSmile, isLookingAtCamera: hasLandmarks, timestamp: now }
        }));
      }
    }
  }, FACE_SAMPLE_INTERVAL);
}
```
Panggil `startFaceSampling()` di akhir `initMediaPipe()` (setelah `faceLandmarker` berhasil dibuat), bukan lagi lewat `animate()`. **Logic di dalam blok ini WAJIB identik** dengan blok asli (baris ~643-679 di file lama) — cuma pindah rumah dari RAF ke interval, jangan ubah threshold/formula smile/eye-contact.

Hapus fungsi `animate()` beserta pemanggilan `animate()` dan seluruh isi `resizeObserver` (khusus untuk resize canvas 3D — tidak dibutuhkan lagi untuk SVG avatar yang scaling-nya CSS-based).

**4e. Update `onDestroy` (baris ~398-453):**
Hapus blok:
```ts
if (animationFrameId !== undefined) { cancelAnimationFrame(animationFrameId); }
resizeObserver?.disconnect();
if (scene) { scene.traverse(...) ... }
renderer?.dispose();
renderer = undefined;
scene = undefined;
camera = undefined;
modelRoot = undefined;
```
Tambahkan:
```ts
if (faceSampleIntervalId) clearInterval(faceSampleIntervalId);
```
**PERTAHANKAN** baris `faceLandmarker?.close(); faceLandmarker = undefined;` — itu bagian cleanup MediaPipe, tetap wajib ada supaya WASM/GPU resource-nya dilepas.

**4f. Ganti semua pemanggilan `speakWithBackend` & auto-blink & ekspresi:**
Cari semua `if (animator) { ... speakWithBackend(chunk.text, animator, ...) ... }` (ada di `handleBackendMessage` dan `processAudioQueue`, sekitar baris 750-871). Ganti pola:
```ts
// SEBELUM
if (animator && chunk.audio && chunk.visemes) {
  await speakWithBackend(chunk.text, animator, { audio: chunk.audio, visemes: chunk.visemes });
}

// SESUDAH
if (chunk.audio && chunk.visemes) {
  await speakWithBackend(chunk.text, (amp) => { mouthOpenness = amp; }, { audio: chunk.audio, visemes: chunk.visemes });
}
```
Hapus guard `animator &&` di semua tempat — sekarang avatar 2D selalu tersedia (tidak perlu tunggu load GLB async), jadi TTS bisa langsung jalan tanpa dependency ke model 3D.

Untuk `startAutoBlink`:
```ts
// SEBELUM
stopBlink = startAutoBlink(animator);

// SESUDAH
stopBlink = startAutoBlink((blinking) => { isBlinking = blinking; });
```
Pindahkan pemanggilan ini ke `onMount` (mis. setelah kamera/`initSpeechRecognition`), karena sebelumnya baru jalan setelah GLB selesai load di `initAvatar()`.

**4g (opsional, boleh di-skip).** Baris `animator.setExpression(EMOTIONS.angry/happy)` saat ganti persona (~baris 750-753, 863-866) dan blok "thinking" pose (~618-630): `Avatar.svelte` tidak punya prop ekspresi/alis, jadi ini tidak punya padanan langsung. **Jangan dipaksa diadaptasi** — cukup hapus baris-baris ini. Kalau ingin tetap ada indikasi visual persona, bisa map ke prop `color` yang sudah ada di `Avatar.svelte` (mis. merah saat `intimidating`, hijau saat `friendly`) — ini enhancement opsional, bukan requirement.

**4h. Ganti markup template.**
Cari elemen `<canvas bind:this={canvasElement} ...>` (atau wrapper container-nya) di bagian `<template>`/markup file ini, ganti dengan:
```svelte
<Avatar openness={mouthOpenness} {isBlinking} size={320} />
```
Sesuaikan ukuran/posisi dengan CSS container yang sudah ada supaya layout tidak berantakan (agen: cek `class` di sekitar canvas lama untuk styling container, pertahankan wrapper div-nya, cuma ganti isi `<canvas>` → `<Avatar>`).

### Step 5 — Bersihkan dependency & asset statis

```bash
# Cek dulu apakah "three" masih dipakai file lain sebelum uninstall
grep -rn "from 'three'\|from \"three\"" src/src --include=*.ts --include=*.svelte

# Kalau sudah bersih:
npm uninstall three
# JANGAN uninstall @mediapipe/tasks-vision — itu tetap dipakai
```
Cari & hapus asset statis GLB/Draco/Meshopt yang besar (biasanya di `static/`):
```bash
find src/static -iname "*.glb" -o -iname "draco*" -o -iname "meshopt*"
```
Konfirmasi dulu isi tiap file sebelum hapus (agen: tampilkan list-nya, jangan auto-delete tanpa saya lihat kalau ada keraguan file itu dipakai fitur lain).

**JANGAN hapus** `static/wasm/*` dan `static/models/face_landmarker.task` — itu punya MediaPipe.

---

## LANGKAH BACKEND

Backend TIDAK punya logic 3D aktif (tidak ada rendering/parsing GLB di server) — perubahan di sini murni pembersihan referensi yang jadi tidak relevan:

1. **Cari semua endpoint yang mengembalikan `glbUrl` ke frontend** (kemungkinan di router avatar/session yang tidak ada di snapshot ini — agen, grep manual di seluruh repo backend):
   ```bash
   grep -rn "glbUrl\|glb_url" app/
   ```
   Untuk tiap response schema/endpoint yang menyertakan `glbUrl`: **boleh tetap disertakan** di response (tidak menyebabkan bug), tapi kalau mau bersih total, hapus dari Pydantic response model yang dipakai endpoint session/avatar. Ini opsional — dampaknya kecil karena cuma menghemat beberapa byte payload.
2. **JANGAN drop kolom `glb_url` dari tabel `interview_avatar`** (`app/app/models/domain.py` baris ~236) di task ini — itu perlu migration terpisah dan koordinasi (data existing, kemungkinan dipakai fitur lain di masa depan). Cukup biarkan kolom ada tapi tidak lagi "wajib diisi secara aktif" oleh flow baru (opsional: agen boleh usulkan migration terpisah kalau saya minta secara eksplisit nanti).
3. Backend TIDAK perlu diubah untuk sisi TTS/viseme (`speech.py`, `f5tts_service.py`) — endpoint `/api/speech` yang menghasilkan `audio` + `visemes` **tetap dipakai penuh** oleh avatar 2D yang baru (`speakWithBackend` masih butuh data ini untuk animasi mulut SVG). Jangan disentuh.

---

## Checklist Verifikasi Setelah Refactor

Jalankan manual test ini setelah build sukses:
- [ ] `npm run build` / `npm run dev` tidak ada error import (`three`, `FaceAnimator`, `visemeController`, `avatarCache` sudah tidak direferensikan di mana pun).
- [ ] Halaman `/session/interview?sessionId=...` load tanpa error console, avatar 2D SVG muncul (bukan canvas kosong/hitam).
- [ ] TTS tetap terdengar dan mulut avatar SVG bergerak sinkron saat pewawancara "bicara".
- [ ] Auto-blink avatar tetap jalan (mata berkedip berkala tanpa trigger eksternal).
- [ ] Webcam tetap aktif, dan setelah sesi selesai, laporan hasil tetap menampilkan skor "Raut Wajah" & "Kontak Mata" yang masuk akal (bukan default value flat 75/80 terus-menerus — cek `faceMetrics` benar-benar terkirim lewat WebSocket selama sesi).
- [ ] `onDestroy` tidak memicu error saat pindah halaman/keluar sesi (cek console: tidak ada "cannot read property of undefined" dari sisa referensi Three.js).
- [ ] Ukuran bundle frontend berkurang (`npm run build` → bandingkan ukuran `.svelte-kit/output` sebelum/sesudah, atau cek network tab: tidak ada lagi request `.glb`/`draco_decoder.wasm`).
- [ ] Halaman `session/select-avatar` tetap berfungsi normal (thumbnail muncul, pemilihan avatar tersimpan) — halaman ini sudah tidak pernah render 3D sejak awal, jadi seharusnya tidak terdampak sama sekali; kalau ada error di sini setelah refactor berarti ada import yang salah kena imbas.

## Yang TIDAK Boleh Disentuh (ulang, karena ini paling sering tidak sengaja rusak)

- `@mediapipe/tasks-vision`, `FaceLandmarker`, `initMediaPipe()`, logic smile/eye-contact scoring
- WebSocket handler (`initWebSocket`, `handleBackendMessage`, VAD, speech recognition)
- Backend `speech.py`, `f5tts_service.py`, `transcriber.py`, `brain.py` — semuanya tidak terkait 3D
- Kolom `glb_url` di database (jangan drop/migration di task ini)
- Semua route selain `session/interview` dan `session/select-avatar`
