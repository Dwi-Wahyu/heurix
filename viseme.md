**Peran:** Ahli Full-stack AI Engineer dengan spesialisasi sistem _self-hosted_ dan _low-resource_.

**Tujuan:** Implementasikan fitur AI Avatar Lip-sync menggunakan metode **Viseme Animation** untuk proyek "HireReady"[cite: 4, 8]. Sistem harus mengirimkan stream audio dan data sinkronisasi mulut secara bersamaan via WebSocket.

**Spesifikasi Teknis:**

1. **Backend (FastAPI):**
   - Gunakan **Piper TTS** secara lokal untuk mengubah teks jawaban AI (dari Ollama) menjadi audio `.wav`.
   - Implementasikan skrip pemetaan fonem ke viseme. Gunakan output fonem dari Piper untuk menentukan durasi dan tipe bentuk mulut (misal: 'A', 'E', 'O', 'M', 'T').
   - Kirimkan paket data via WebSocket berisi `audio_base64` dan daftar `visemes` (format: `[{time: float, value: string}]`).
2. **Frontend (SvelteKit + Svelte 5 Runes):**
   _ Gunakan **Three.js** dan `@pixiv/three-vrm` untuk memuat model `.vrm` yang sudah saya unduh [cite: 120, 136-137].
   _ Buat logika sinkronisasi: saat audio diputar, gerakkan `blendShapeProxy` model VRM berdasarkan data viseme yang diterima dari backend[cite: 155]. \* Gunakan `requestAnimationFrame` untuk memastikan transisi antar bentuk mulut terasa halus (interpolasi)[cite: 152].
3. **Optimasi:** Pastikan semua proses berjalan secara asinkron agar tidak memblokir deteksi emosi MediaPipe yang sudah ada di frontend [cite: 121, 141-149].

---

## 2. Gambaran Teknis Pemetaan Viseme (Minggu 4 Update)

Agar AI memahami cara kerja sinkronisasi tanpa GPU monster, berikut adalah logika yang perlu diterapkan:

### A. Di Sisi Backend (FastAPI + Piper)

Piper memiliki fitur untuk mengeluarkan data fonem dengan flag `--json`.

- **Proses:** Teks $\rightarrow$ Piper $\rightarrow$ File Audio + File JSON Fonem.
- **Mapping:** Buat kamus (_dictionary_) sederhana di Python:
  - Fonem `aa`, `ah`, `ay` $\rightarrow$ Viseme `A`
  - Fonem `ee`, `ih` $\rightarrow$ Viseme `I`
  - Fonem `ow`, `uw` $\rightarrow$ Viseme `U`
  - Fonem `p`, `b`, `m` $\rightarrow$ Viseme `M` (mulut tertutup).

### B. Di Sisi Frontend (SvelteKit)

Gunakan data `time` dari JSON tersebut untuk memicu perubahan pada model 3D:

```typescript
// Contoh logika sederhana di Svelte 5
const visemes = data DariBackend.visemes;
function updateMouth() {
  const currentTime = audioPlayer.currentTime;
  const currentViseme = findClosestViseme(visemes, currentTime);

  // Menggerakkan Blendshapes VRM
  vrm.expressionManager.setValue('ih', currentViseme === 'I' ? 1.0 : 0.0);
  vrm.expressionManager.setValue('aa', currentViseme === 'A' ? 1.0 : 0.0);
}
```

---

## 3. Keunggulan untuk GEMASTIK Divisi 8

Dengan menerapkan rencana ini, Anda menonjolkan beberapa poin keunggulan kompetitif[cite: 107]:

1. **Inovasi Efisiensi:** Mampu menjalankan sistem multimodal (Visi, Suara, Teks, dan Animasi) pada perangkat spesifikasi menengah tanpa API berbayar[cite: 108, 111].
2. **Privasi Penuh:** Seluruh data video, audio, dan pengolahan AI dilakukan 100% lokal di perangkat[cite: 112].
3. **User Experience:** Memberikan "lawan bicara" yang lebih manusiawi (AI Avatar) dibandingkan hanya sekadar teks di layar, sehingga simulasi terasa lebih nyata[cite: 109, 116].

Langkah selanjutnya, apakah Anda ingin saya bantu membuatkan **skema JSON** untuk pertukaran data antara FastAPI dan SvelteKit agar sinkronisasinya benar-benar presisi?
