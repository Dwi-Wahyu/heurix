# Instruksi Lanjutan: Ganti Avatar 2D dengan Audio Bar Visualizer

**Untuk:** Agen CLI (Claude Code / Gemini CLI)
**Prasyarat:** `INSTRUKSI_HAPUS_3D_HEURIX.md` sudah dieksekusi (lihat `LAPORAN_HAPUS_3D_HEURIX.md` — status selesai).
**Tujuan:** Hapus tampilan avatar (SVG `Avatar.svelte`) sepenuhnya, ganti dengan komponen `BarVisualizer` dari [flo-bit/svelte-audio-visualizations](https://github.com/flo-bit/svelte-audio-visualizations) yang bereaksi terhadap audio TTS output. Sederhanakan loading screen jadi teks "Memulai Sesi Interview" + overlay hitam polos, tanpa elemen avatar/progress bar model apa pun.

---

## ⚠️ 5 Hal Penting Soal Kompatibilitas (WAJIB dibaca dulu)

Saya sudah cek langsung ke source code repo tersebut (bukan cuma README), berikut temuannya:

1. **Bukan paket npm.** `svelte-audio-visualizations` **tidak dipublikasikan ke npm registry**. README-nya eksplisit bilang: *"Installation: copy the `lib/visualizations` folder into your project."* Jadi jangan coba `npm install svelte-audio-visualizations` — itu akan gagal (404). Cara pakainya memang copy-paste file.

2. **Versi Svelte tidak sama, tapi tetap kompatibel — dengan syarat.** `package.json` library ini pakai `"svelte": "^4.2.7"` (Svelte 4), sedangkan project Heurix pakai **Svelte 5 runes mode** (`$state`, `$props`, dst — sudah terbukti dari `Avatar.svelte` yang baru saja dibuat). File `BarVisualizer.svelte` di library ditulis pakai syntax legacy (`export let values`, reactive statement `$:`), BUKAN runes. Ini **tetap bisa jalan** di project Svelte 5, karena Svelte 5 mendukung komponen legacy-mode dan runes-mode hidup berdampingan dalam satu project (per-file, dideteksi otomatis dari ada/tidaknya rune di file itu) — **DENGAN SYARAT** `svelte.config.js` project TIDAK memaksa `compilerOptions: { runes: true }` secara global. **Agen WAJIB cek ini duluan** sebelum copy file:
   ```bash
   cat svelte.config.js | grep -A3 compilerOptions
   ```
   - Kalau tidak ada `runes: true` dipaksa global → copy file apa adanya, tidak perlu diubah sama sekali.
   - Kalau ternyata dipaksa `runes: true` global → baru convert `export let` → `$props()` dan `$:` → `$derived`/`$effect` di file yang dicopy (kemungkinan besar TIDAK diperlukan, tapi cek dulu supaya tidak ada asumsi salah).

3. **JANGAN copy seluruh folder `lib/visualizations`.** Folder itu juga berisi `wavtools/` (kelas `WavRecorder`, `WavStreamPlayer`, `AudioFilePlayer` — dependency berat, dibuild dari `openai-realtime-console`) dan komponen wrapper di folder `audio/` yang **dirancang khusus untuk kelas-kelas tersebut**, bukan untuk elemen `<audio>` biasa. Project Heurix sudah punya pipeline audio TTS sendiri yang jalan baik (`globalAudioPlayer` di `lipSync.ts`, dari base64 mp3 backend) — **JANGAN diganti** dengan `wavtools`, itu perubahan besar & berisiko tanpa manfaat.

   **Cukup copy 2 file ini saja (zero extra dependency, murni Canvas 2D API):**
   - `src/lib/visualizations/core/BarVisualizer.svelte` → bar horizontal yang dimaksud (baris-baris vertikal berjajar horizontal, tinggi berubah sesuai amplitude — ini yang biasa disebut "horizontal bar chart" audio visualizer).
   - `src/lib/visualizations/core/utils.ts` → helper `normalizeArray` (opsional, dipakai kalau mau resample jumlah bar).

   Boleh tambahan opsional: `core/Glow.svelte` (cuma filter SVG blur, tidak ada dependency) kalau mau efek glow di sekitar bar.

4. **`BarVisualizer` butuh data (`values: Float32Array`), bukan instance audio.** Karena kita SKIP folder `audio/` dan `wavtools/`, kita harus suplai `values` sendiri tiap frame. Caranya: pasang `AnalyserNode` Web Audio API ke elemen `<audio>` TTS yang **sudah ada** (`globalAudioPlayer` di `lipSync.ts`), lalu baca `getFloatFrequencyData()`/`getByteFrequencyData()` tiap `requestAnimationFrame` dan feed ke prop `values`. Detail implementasi di Step 2 di bawah.

5. **⚠️ Jebakan `createMediaElementSource` — bisa membuat audio TTS SENYAP total.**
   - `audioContext.createMediaElementSource(audioEl)` **mengalihkan** output elemen audio ke Web Audio graph. Kalau analyser tidak disambungkan lanjut ke `audioContext.destination`, suara TTS **tidak akan terdengar sama sekali** — regresi serius, harus dites manual.
   - Method ini **hanya boleh dipanggil SEKALI** per elemen `<audio>` (panggilan kedua akan throw `InvalidStateError`). Harus di-lazy-init sebagai singleton (ikuti pola `globalAudioPlayer` yang sudah ada).
   - `AudioContext` browser modern butuh **resume() setelah user gesture** (autoplay policy) — sudah ada `handleUserInteraction()` di `interview/+page.svelte`, tinggal numpang di situ.

---

## Step 1 — Copy file library

```bash
mkdir -p src/src/lib/visualizations/core
# Ambil dari repo (agen: clone/download sesuai akses yang tersedia)
# hanya file berikut yang dibutuhkan:
#   BarVisualizer.svelte
#   utils.ts
#   (opsional) Glow.svelte
```
Taruh di `src/src/lib/visualizations/core/BarVisualizer.svelte` (path `$lib/visualizations/core/BarVisualizer.svelte`). **Jangan ubah isi file ini** kecuali hasil pengecekan Poin 2 di atas mengharuskan konversi ke runes.

---

## Step 2 — Perluas `lipSync.ts`: tambah `AnalyserNode` + sederhanakan `speakWithBackend`

Karena avatar (dan mulutnya) sudah tidak ada, kita **tidak lagi butuh** callback `onMouthUpdate` yang ditambahkan di refactor sebelumnya — itu boleh dihapus, menyederhanakan fungsi. Data amplitude untuk bar chart sekarang datang dari `AnalyserNode` real-time, bukan dari array `visemes` yang di-precompute backend (backend boleh tetap generate `visemes`, tidak masalah walau tidak dipakai — TIDAK PERLU ubah backend).

```ts
// lipSync.ts

// ── Analyser singleton untuk visualizer ──
let audioContext: AudioContext | null = null;
let analyserNode: AnalyserNode | null = null;
let sourceNode: MediaElementAudioSourceNode | null = null;

/**
 * Lazy-init AudioContext + AnalyserNode yang tersambung ke globalAudioPlayer.
 * WAJIB dipanggil hanya sekali per audio element (createMediaElementSource
 * akan throw kalau dipanggil dua kali pada element yang sama).
 */
export function getOutputAnalyser(): AnalyserNode {
  if (!globalAudioPlayer) unlockAudio();
  if (analyserNode) return analyserNode;

  audioContext = new AudioContext();
  analyserNode = audioContext.createAnalyser();
  analyserNode.fftSize = 128; // -> 64 bin frequency data, cukup untuk bar chart ringkas
  analyserNode.smoothingTimeConstant = 0.7; // biar transisi antar bar tidak "patah-patah"

  sourceNode = audioContext.createMediaElementSource(globalAudioPlayer!);
  sourceNode.connect(analyserNode);
  // ── PENTING: sambungkan balik ke destination, kalau tidak audio jadi BISU ──
  analyserNode.connect(audioContext.destination);

  return analyserNode;
}

/** Panggil dari handleUserInteraction() di interview page agar AudioContext resume setelah gesture user. */
export function resumeAudioContext() {
  audioContext?.resume();
}

// speakWithBackend disederhanakan: hapus parameter animator/onMouthUpdate,
// murni memutar audio saja. Visualisasi kini ditangani terpisah oleh AnalyserNode.
export async function speakWithBackend(
  text: string,
  pregeneratedData?: { audio: string; visemes: number[] }
): Promise<void> {
  // ... logic fetch/decode audio SAMA seperti sebelumnya ...
  // HAPUS semua blok startFallbackAnimation/stopFallbackAnimation/updateMouth
  // dan setiap pemanggilan animator.setMouth(...) — tidak relevan lagi.
  // Sisakan murni: fetch -> decode base64 -> set audioPlayer.src -> play() -> resolve on 'ended'.
}
```

Catatan implementasi `speakWithBackend`: array `visemes` dari `pregeneratedData` sekarang **tidak dipakai untuk animasi** (boleh tetap diterima sebagai parameter untuk kompatibilitas tipe data dari backend, cukup diabaikan/`_visemes`). Jangan hapus dari backend — itu di luar scope task ini.

---

## Step 3 — Buat komponen wrapper visualizer (opsional tapi direkomendasikan)

Supaya interview page tidak perlu urus RAF loop + AnalyserNode secara manual, bungkus jadi satu komponen kecil:

`src/src/lib/OutputBarVisualizer.svelte`:
```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import BarVisualizer from '$lib/visualizations/core/BarVisualizer.svelte';
  import { getOutputAnalyser } from '$lib/lipSync';

  let values = $state(new Float32Array(32));
  let rafId: number;

  onMount(() => {
    const analyser = getOutputAnalyser();
    const bufferLength = analyser.frequencyBinCount; // 64 utk fftSize=128
    const dataArray = new Uint8Array(bufferLength);

    function loop() {
      analyser.getByteFrequencyData(dataArray);
      // normalisasi 0-255 -> 0-1, ambil subset biar tidak terlalu padat (mis. 32 bar)
      const normalized = new Float32Array(32);
      const step = Math.floor(bufferLength / 32) || 1;
      for (let i = 0; i < 32; i++) {
        normalized[i] = (dataArray[i * step] || 0) / 255;
      }
      values = normalized;
      rafId = requestAnimationFrame(loop);
    }
    loop();
  });

  onDestroy(() => {
    if (rafId) cancelAnimationFrame(rafId);
  });
</script>

<div class="h-32 w-full max-w-md">
  <BarVisualizer {values} color="#4F46E5" barSpacing={3} center={false} />
</div>
```
Sesuaikan `color`, tinggi (`h-32`), dan `barSpacing` dengan desain kamu. Prop `center={true}` di `BarVisualizer` membuat bar tumbuh dari tengah (dua arah) kalau mau tampilan alternatif.

---

## Step 4 — Update `session/interview/+page.svelte`

**4a. Ganti import Avatar:**
```ts
// HAPUS
import Avatar from '$lib/Avatar.svelte';
// TAMBAH
import OutputBarVisualizer from '$lib/OutputBarVisualizer.svelte';
import { resumeAudioContext } from '$lib/lipSync';
```

**4b. Hapus state yang sudah tidak relevan:**
```ts
// HAPUS (sisa refactor sebelumnya, sudah tidak dipakai)
let mouthOpenness = $state(0);
let isBlinking = $state(false);
```
(`stopBlink`/`startAutoBlink` juga boleh dihapus pemanggilannya di `onMount`/`onDestroy` — kalau mau, `autoBlink.ts` boleh dihapus filenya juga karena sudah tidak ada konsumen sama sekali.)

**4c. Ganti markup avatar dengan visualizer:**
Cari lokasi bekas `<Avatar openness={mouthOpenness} {isBlinking} size={320} />` (hasil refactor sebelumnya), ganti:
```svelte
<OutputBarVisualizer />
```
Sesuaikan wrapper/posisi container dengan layout yang ada (biasanya di area tengah panel interview, tempat avatar dulu berada).

**4d. Update semua pemanggilan `speakWithBackend`:**
Cari `speakWithBackend(chunk.text, (amp) => { mouthOpenness = amp; }, {...})` (hasil refactor sebelumnya di `handleBackendMessage`/`processAudioQueue`), sederhanakan jadi:
```ts
await speakWithBackend(chunk.text, { audio: chunk.audio, visemes: chunk.visemes });
```

**4e. Hook `resumeAudioContext()` ke interaksi user:**
Di `handleUserInteraction()` (sudah ada di file), tambahkan pemanggilan:
```ts
function handleUserInteraction() {
  resumeAudioContext();
  // ... logic yang sudah ada, JANGAN dihapus ...
}
```

**4f. Sederhanakan loading screen (bagian `{#if !avatarReady}`).**
Cari dulu kondisi state `avatarReady` & `avatarLoadProgress` yang MASIH ADA setelah refactor 3D sebelumnya (kemungkinan sudah disederhanakan agen sebelumnya karena `initAvatar()` sudah dihapus — cek dulu, jangan asumsi baris tetap sama):
```bash
grep -n "avatarReady\|avatarLoadProgress" src/src/routes/session/interview/+page.svelte
```
Ganti seluruh blok card loading (yang berisi thumbnail avatar, judul nama avatar, progress bar "Memuat Avatar 3D") menjadi overlay hitam polos + teks status:
```svelte
{#if !avatarReady}
  <div
    class="fixed inset-0 z-[100] flex items-center justify-center bg-black"
    transition:fade
  >
    <div class="flex flex-col items-center gap-4 text-white">
      <div class="h-10 w-10 animate-spin rounded-full border-4 border-white/20 border-t-white"></div>
      <p class="text-lg font-medium tracking-wide">Memulai Sesi Interview</p>
    </div>
  </div>
{/if}
```
Hapus dependency ke `avatarThumbnail`, `avatarDescription`, `avatarLoadProgress` di blok ini (variabel-variabel itu boleh tetap ada di state untuk keperluan lain — mis. kalau `avatarName`/`avatarThumbnail` masih dipakai di tempat lain seperti header chat/riwayat percakapan, JANGAN dihapus deklarasinya, cukup jangan dipakai lagi di loading card ini).
`avatarReady` sendiri: pastikan tetap di-set `true` di titik yang tepat (biasanya setelah `sessionData` berhasil di-fetch dan WebSocket mulai connect) — kalau logic pengaturannya sebelumnya nunggu event GLTFLoader (`onProgress`/`onLoad`) yang sudah tidak ada, ganti jadi langsung `avatarReady = true` setelah fetch session sukses (tidak perlu tunggu apa pun lagi, karena tidak ada model yang di-load).

---

## Step 5 — Bersihkan sisa avatar 2D yang sudah tidak dipakai (opsional, tapi disarankan sesuai permintaan "tidak perlu munculkan gambar avatar sama sekali")

```bash
# Pastikan dulu tidak dipakai di tempat lain (mis. select-avatar, dashboard)
grep -rln "Avatar.svelte\|from '\$lib/Avatar'" src/src --include=*.svelte

# Kalau memang sudah tidak ada konsumen sama sekali:
rm src/src/lib/Avatar.svelte
rm src/src/lib/autoBlink.ts   # hanya jika sudah tidak dipanggil di mana pun
```
**JANGAN hapus** `avatarName`/`avatarThumbnail`/`avatarDescription` dari state maupun dari fetch session — itu tetap dipakai untuk menampilkan identitas pewawancara di UI lain (header sesi, kartu info), bukan cuma untuk avatar 3D/2D yang dihapus.

---

## Checklist Verifikasi

- [ ] `npm run build` / `npm run dev` sukses, tidak ada error import (`BarVisualizer`, `Avatar` lama sudah tidak direferensikan kalau dihapus).
- [ ] Cek `svelte.config.js` sudah dikonfirmasi (Poin 2) — kalau `runes: true` dipaksa global dan file `BarVisualizer.svelte` tidak dikonversi, build **akan gagal** dengan error terkait `export let`/reactive statement tidak valid di rune mode. Kalau ini terjadi, konversi filenya (lihat Poin 2).
- [ ] **PALING PENTING:** buka sesi interview, pastikan **suara TTS tetap terdengar** (bukan cuma bar-nya bergerak tanpa suara) — ini regresi paling gampang kejadian dari jebakan `createMediaElementSource` di Poin 5.
- [ ] Bar visualizer bergerak sinkron dengan ritme bicara AI (naik-turun mengikuti amplitude), diam/flat saat AI tidak bicara.
- [ ] Loading screen saat masuk sesi menampilkan overlay hitam + "Memulai Sesi Interview" saja — tidak ada gambar/thumbnail avatar, tidak ada progress bar "Memuat Avatar 3D".
- [ ] Tidak ada error console `InvalidStateError` (indikasi `createMediaElementSource` terpanggil dua kali) saat pindah antar giliran/pertanyaan dalam satu sesi.
- [ ] Fitur MediaPipe (skor Raut Wajah/Kontak Mata) dari refactor sebelumnya **masih berfungsi normal** — task ini tidak menyentuh bagian itu sama sekali, tapi tetap perlu diverifikasi tidak ada regresi tidak sengaja.
- [ ] Halaman `session/select-avatar` tidak terdampak (masih pakai thumbnail image biasa, tidak pernah pakai `Avatar.svelte`/3D).

## Yang TIDAK Boleh Disentuh

- Backend (`app/`) — task ini murni frontend, tidak ada perubahan backend sama sekali.
- `visemes` array dari response `/api/speech` — biarkan backend tetap mengirimnya walau tidak dipakai frontend lagi.
- WebSocket handler, VAD, speech recognition, MediaPipe face analysis — semua di luar scope, jangan ikut ter-refactor.
- `avatarName`, `avatarThumbnail`, `avatarDescription` sebagai *data* (bukan sebagai tampilan avatar visual) — tetap dipakai di UI lain.

---

*Setelah selesai, jalankan protokol standar repo kamu seperti biasa (`graphify update .` dll.) sesuai kebiasaan kerja kamu — di luar scope instruksi teknis ini.*
