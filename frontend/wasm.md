2. Instruksi Langkah-demi-Langkah (Self-Hosting)

Agar aplikasi dapat berjalan sepenuhnya secara lokal tanpa memuat dari CDN Google, ikuti langkah berikut:

Langkah 1: Instalasi Library
Jalankan perintah berikut di terminal proyek Anda:
1 bun add @mediapipe/tasks-vision

Langkah 2: Menyiapkan Folder static/
Buat struktur folder berikut di dalam direktori static/ proyek SvelteKit Anda:

1 static/
2 ├── models/
3 │ └── face_landmarker.task
4 └── wasm/
5 ├── vision_wasm_internal.wasm
6 ├── vision_wasm_internal.js
7 ├── vision_wasm_nosimd_internal.wasm
8 └── vision_wasm_nosimd_internal.js

Langkah 3: Mengunduh File Model
Unduh file model Face Landmarker resmi dari Google dan simpan di static/models/:

- Face Landmarker Task: Unduh di sini
  (https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmar
  ker.task)

Langkah 4: Menyalin File WASM
Salin file runtime WASM dari paket npm yang baru saja diinstal ke folder static/wasm/. Anda bisa
melakukannya secara manual atau dengan perintah shell:
1 cp node_modules/@mediapipe/tasks-vision/wasm/\* static/wasm/

Keunggulan vs face-api.js:

1.  WASM Power: MediaPipe menggunakan WebAssembly yang dioptimalkan, jauh lebih cepat daripada kernel JS
    murni.
2.  GPU Acceleration: Dengan opsi delegate: "GPU", beban komputasi berat dialihkan ke kartu grafis,
    menjaga CPU tetap dingin.
3.  Dense Mesh: MediaPipe memberikan 468+ titik koordinat (termasuk iris mata) dibandingkan 68 titik
    standar pada face-api.js, memberikan akurasi jauh lebih tinggi untuk aplikasi seperti filter wajah
    atau analisis ekspresi
