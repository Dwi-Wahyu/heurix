# HiReady — Panduan Standarisasi & Optimasi Model 3D Avatar

## Ringkasan Keputusan Arsitektur

| Pertanyaan                                              | Keputusan                      | Alasan                                                    |
| ------------------------------------------------------- | ------------------------------ | --------------------------------------------------------- |
| Instruksi per model atau standarisasi?                  | **Standarisasi shape key**     | `FaceAnimator.ts` tidak perlu tahu model mana yang dimuat |
| `glbUrl` di `masterInstitution` atau `interviewAvatar`? | **Tetap di `interviewAvatar`** | Schema sudah tepat, tidak perlu diubah                    |
| Instruksi shape key di DB?                              | **Tidak perlu**                | Kontrak shape key sudah terdefinisi di `visemeMap.ts`     |
| Ukuran 47MB?                                            | **Kompresi + lazy load**       | Lihat Bagian 3                                            |

---

## Bagian 1 — Kontrak Shape Key Wajib (Standar Semua Model)

Semua model GLB yang dibuat — apapun kostumnya (seragam Akpol, jas korporat, dll) —
**wajib memiliki shape key wajah berikut dengan nama yang PERSIS SAMA**.
Yang boleh berbeda antar model hanya mesh body, kostum, dan tekstur.

### Shape Key Wajib (Minimal)

```
Grup Viseme (wajib ada):
  Open
  Explosive
  Dental_Lip
  Tight_O
  Wide
  Affricate
  Lip_Open
  Mouth_Plosive
  Mouth_Pucker
  Mouth_Lips_Part
  Mouth_Lips_Open
  Mouth_Bottom_Lip_Down
  Mouth_Widen_Sides

Grup Emosi (wajib ada):
  Mouth_Smile
  Mouth_Frown
  Eye_Blink
  Eye_Wide_L
  Eye_Wide_R
  Eye_Squint_L
  Eye_Squint_R
  Brow_Raise_L
  Brow_Raise_R
  Brow_Drop_L
  Brow_Drop_R
  Brow_Raise_Inner_L
  Brow_Raise_Inner_R
  Cheek_Raise_L
  Cheek_Raise_R
  Nose_Scrunch
```

Shape key tambahan (opsional, boleh ada atau tidak):

```
  Mouth_Smile_L / Mouth_Smile_R
  Mouth_Frown_L / Mouth_Frown_R
  Mouth_Dimple_L / Mouth_Dimple_R
  Cheek_Blow_L / Cheek_Blow_R
  Nose_Flanks_Raise
  Mouth_Snarl_Upper_L / Mouth_Snarl_Upper_R
```

### Kenapa Ini Penting

`FaceAnimator.ts` mengiterasi `VISEME_SHAPE_KEYS` dan memanggil `setMorph()` berdasarkan nama.
Jika satu model punya nama `Tight_O` dan model lain pakai `TightO` (tanpa underscore),
animasi diam tanpa error — hanya gagal diam-diam.

---

## Bagian 2 — Relasi Avatar ↔ Institusi (Tidak Perlu Diubah)

Schema yang sudah ada sudah benar. Tidak ada yang perlu ditambahkan ke `masterInstitution`.

```
Alur saat user memilih institusi:

  user pilih "Akpol"  (track = 'military')
       │
       ▼
  GET /api/avatars?track=military
       │
       ▼
  interviewAvatar {
    id: 'akpol-colonel',
    name: 'Kolonel Ahmad',
    track: 'military',
    glbUrl: '/face/akpol-colonel.glb',   ← path ke file di /static/face/
    ttsVoiceId: '...',
    promptFormal: '...',
    promptIntimidating: '...',
  }
       │
       ▼
  Frontend load GLB dari glbUrl
  FaceAnimator dibuat dari model → shape key sudah standar → langsung jalan
```

### Yang Perlu Ditambahkan ke `interviewAvatar` di DB (Opsional)

Jika ingin fleksibilitas kamera per model (misalnya model full body butuh kamera lebih jauh):

```sql
-- Tambahkan kolom opsional di tabel interview_avatar
ALTER TABLE interview_avatar ADD COLUMN camera_y REAL DEFAULT 1.6;
ALTER TABLE interview_avatar ADD COLUMN camera_z REAL DEFAULT 2.5;
ALTER TABLE interview_avatar ADD COLUMN camera_fov INTEGER DEFAULT 35;
```

Frontend baca nilai ini saat `initAvatar()` untuk posisi kamera yang tepat per model.
Ini opsional — bisa di-hardcode dulu, dioptimasi nanti.

---

## Bagian 3 — Optimasi Load Model 47MB di Frontend

### Strategi Berlapis (Urutkan dari yang Paling Berdampak)

```
47MB raw GLB
  └─ Step 1: Kompresi Draco + gzip/brotli   → ~8–12MB  (70% lebih kecil)
  └─ Step 2: Progressive loading + skeleton  → UX tetap baik selama load
  └─ Step 3: Preload on hover / route        → model sudah siap saat dibutuhkan
  └─ Step 4: Cache di browser                → load kedua = instan
```

---

### Step 1 — Kompresi Draco (Lakukan di Blender/CLI, Bukan di Kode)

Draco adalah kompresi geometry lossless yang dikembangkan Google.
Kamu sudah punya `draco_encoder.js` di `/static/draco/` — artinya frontend sudah siap decode.
Yang belum dilakukan: **mengompresi file GLB-nya sendiri**.

**Cara kompresi via CLI (`gltf-pipeline`):**

```bash
# Install sekali
npm install -g gltf-pipeline

# Kompresi dengan Draco (lakukan untuk setiap file GLB)
gltf-pipeline -i model.glb -o model-draco.glb --draco.compressionLevel 7

# Atau jika ingin lebih agresif (kualitas sedikit turun, ukuran lebih kecil)
gltf-pipeline -i model.glb -o model-draco.glb \
  --draco.compressionLevel 10 \
  --draco.quantizePositionBits 14 \
  --draco.quantizeNormalBits 10 \
  --draco.quantizeTexcoordBits 12
```

**Hasil yang diharapkan:**
| File | Ukuran |
|------|--------|
| model.glb (original) | ~47MB |
| model-draco.glb | ~12–18MB |
| Setelah gzip/brotli di server | ~8–12MB |

**Setup gzip/brotli di server (SvelteKit + Vite):**

```javascript
// vite.config.ts
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    rollupOptions: {
      // GLB di /static/ tidak diproses Vite
      // Kompresi dilakukan di level server (Nginx/Caddy)
    },
  },
});
```

```nginx
# Nginx config — tambahkan untuk static files
location ~* \.(glb|gltf)$ {
    gzip_static on;
    brotli_static on;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

### Step 2 — Progressive Loading dengan Skeleton Avatar

Jangan biarkan layar kosong selama 47MB diunduh. Tampilkan placeholder dulu.

**`src/routes/session/interview/+page.svelte`** — tambahkan state loading:

```typescript
let avatarLoadProgress = $state(0); // 0–100
let avatarReady = $state(false);
```

**Di `initAvatar()`** — gunakan `onProgress` callback dari GLTFLoader:

```typescript
async function initAvatar(glbUrl: string) {
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath("/draco/");

  const loader = new GLTFLoader();
  loader.setDRACOLoader(dracoLoader);

  loader.load(
    glbUrl,
    // onLoad
    (gltf) => {
      scene.add(gltf.scene);
      animator = new FaceAnimator(gltf.scene);
      stopBlink = startAutoBlink(animator);
      avatarReady = true;
    },
    // onProgress
    (xhr) => {
      avatarLoadProgress = Math.round((xhr.loaded / xhr.total) * 100);
    },
    // onError
    (error) => {
      console.error("Failed to load avatar:", error);
    },
  );
}
```

**Di template HTML** — tampilkan loading state yang informatif:

```html
<!-- Di dalam section avatar, sebelum canvas -->
{#if !avatarReady}
<div
  class="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-10"
>
  <!-- Skeleton avatar (SVG sederhana sebagai placeholder) -->
  <div
    class="w-32 h-48 rounded-2xl bg-white/5 border border-white/10 animate-pulse mb-4"
  ></div>
  <!-- Progress bar -->
  <div class="w-48 h-1.5 bg-white/10 rounded-full overflow-hidden">
    <div
      class="h-full bg-primary rounded-full transition-all duration-300"
      style="width: {avatarLoadProgress}%"
    ></div>
  </div>
  <p class="text-xs text-white/50 mt-2">
    Memuat pewawancara... {avatarLoadProgress}%
  </p>
</div>
{/if}

<canvas
  id="avatar-canvas"
  class="absolute inset-0 h-full w-full transition-opacity duration-500 {avatarReady ? 'opacity-100' : 'opacity-0'}"
></canvas>
```

---

### Step 3 — Preload Model Sebelum Halaman Interview

Model paling baik dimuat **sebelum user masuk ke halaman interview**.
Ada dua momen ideal untuk preload:

**Opsi A — Preload saat halaman `/session/disclaimer`:**

```typescript
// src/routes/session/disclaimer/+page.svelte
import { onMount } from "svelte";

onMount(() => {
  // Fetch GLB di background, browser otomatis cache ke memory
  // Saat user klik "Mulai", model sudah ada di cache
  const link = document.createElement("link");
  link.rel = "prefetch";
  link.href = "/face/default.glb"; // ganti dengan URL avatar user
  link.as = "fetch";
  document.head.appendChild(link);
});
```

**Opsi B — Preload via `<link rel="preload">` di `+page.svelte` interview:**

```svelte
<svelte:head>
  <link rel="preload" href="/face/default.glb" as="fetch" crossorigin="anonymous" />
</svelte:head>
```

---

### Step 4 — Cache Agresif di Browser

GLB avatar jarang berubah — manfaatkan browser cache secara maksimal.

```typescript
// src/lib/avatarCache.ts
// Simple in-memory cache untuk sesi yang sama

const cache = new Map<string, ArrayBuffer>();

export async function loadGLBCached(url: string): Promise<ArrayBuffer> {
  if (cache.has(url)) {
    console.log("[AvatarCache] Hit:", url);
    return cache.get(url)!;
  }

  console.log("[AvatarCache] Miss, fetching:", url);
  const res = await fetch(url);
  const buffer = await res.arrayBuffer();
  cache.set(url, buffer);
  return buffer;
}
```

Gunakan di `initAvatar()`:

```typescript
import { loadGLBCached } from "$lib/avatarCache";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

async function initAvatar(glbUrl: string) {
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath("/draco/");

  const loader = new GLTFLoader();
  loader.setDRACOLoader(dracoLoader);

  // Load dari cache atau fetch
  const buffer = await loadGLBCached(glbUrl);

  // Parse dari ArrayBuffer (tidak perlu fetch ulang)
  loader.parseAsync(buffer, "").then((gltf) => {
    scene.add(gltf.scene);
    animator = new FaceAnimator(gltf.scene);
    stopBlink = startAutoBlink(animator);
    avatarReady = true;
  });
}
```

Jika user memulai sesi kedua dengan avatar yang sama, model langsung dari memory — load time 0ms.

---

### Step 5 — Pertimbangkan LOD (Level of Detail) untuk Masa Depan

Jika ukuran tetap masalah setelah Draco, pertimbangkan pendekatan ini di iterasi berikutnya:

```
Saat ini (satu model full):
  model.glb = 47MB → semua detail langsung dimuat

Alternatif LOD (dua versi):
  model-hd.glb  = 47MB  → dimuat setelah model-ld siap
  model-ld.glb  = 5MB   → dimuat pertama, tampil dulu

Implementasi:
  1. Load model-ld.glb dulu → tampilkan dalam 2–3 detik
  2. Di background, load model-hd.glb
  3. Swap scene object saat HD selesai → transisi opacity
```

Ini lebih kompleks — tidak perlu sekarang, tapi catat untuk roadmap.

---

## Bagian 4 — Framing Kamera: Menyorot Wajah Model

Data berikut diambil langsung dari inspeksi file `model.glb` yang ada.

### Struktur Model yang Relevan

```
Armature (root)
└── CC_Base_BoneRoot
    └── CC_Base_Hip        Y world: 3.08 cm
        └── CC_Base_Waist
            └── CC_Base_Spine01
                └── CC_Base_Spine02
                    └── CC_Base_NeckTwist01  Y world: 52.10 cm
                        └── CC_Base_NeckTwist02
                            └── CC_Base_Head  Y world: 58.39 cm  ← target kamera

Mesh utama wajah : CC_Base_Body  (node 101, mesh 0)
Shape keys wajah : 68 shape keys di Mesh.001
Mesh pendukung   : CC_Base_Eye, CC_Base_Teeth, CC_Base_Tongue
```

> **Penting:** CC exports dalam satuan **centimeter**. Three.js bekerja dalam meter.
> Head berada di Y = 58.39 cm = **0.584 meter** dari origin.

---

### Konfigurasi Kamera Three.js untuk Close-up Wajah

Gunakan nilai ini di `initAvatar()`. Nilai sudah dihitung dari posisi head bone aktual model:

```typescript
async function initAvatar(glbUrl: string) {
  const canvas = document.getElementById("avatar-canvas") as HTMLCanvasElement;
  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
  });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const scene = new THREE.Scene();

  // ── KAMERA ──────────────────────────────────────────────────────────────
  // Model CC diekspor dalam cm → scale ke meter dengan scene.scale atau
  // sesuaikan posisi kamera dalam cm (pilih salah satu).
  //
  // OPSI A: scale model ke meter (DIREKOMENDASIKAN — konsisten dengan Three.js)
  // Tambahkan setelah gltf.scene ditambahkan ke scene:
  //   gltf.scene.scale.setScalar(0.01);
  //
  // Dengan scale 0.01, head ada di Y = 0.584m
  // Kamera diarahkan ke titik ini dengan jarak yang pas untuk close-up wajah.

  const camera = new THREE.PerspectiveCamera(
    28, // FOV sempit → wajah lebih besar, distorsi minimal
    canvas.clientWidth / canvas.clientHeight,
    0.01,
    100,
  );

  // Target = posisi kepala setelah scaling (58.39cm × 0.01 = 0.584m)
  // Offset sedikit ke atas (+0.05) agar dahi ikut terlihat
  const HEAD_Y = 0.584 + 0.05; // 0.634m

  // Posisi kamera: sedikit di atas eye level, jarak 0.55m → framing bahu ke atas
  camera.position.set(0, HEAD_Y + 0.02, 0.55);
  camera.lookAt(0, HEAD_Y - 0.03, 0); // lookAt sedikit ke bawah (ke hidung)

  // ── PENCAHAYAAN ─────────────────────────────────────────────────────────
  // Tiga titik cahaya standar untuk wajah manusia
  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);

  // Key light — dari kiri depan, hangat
  const keyLight = new THREE.DirectionalLight(0xfff5e0, 1.2);
  keyLight.position.set(-0.5, HEAD_Y + 0.3, 0.8);
  scene.add(keyLight);

  // Fill light — dari kanan, lebih redup
  const fillLight = new THREE.DirectionalLight(0xe8f0ff, 0.5);
  fillLight.position.set(0.8, HEAD_Y, 0.4);
  scene.add(fillLight);

  // Rim light — dari belakang atas, memberi depth
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.3);
  rimLight.position.set(0, HEAD_Y + 0.5, -0.8);
  scene.add(rimLight);

  // ── LOAD MODEL ──────────────────────────────────────────────────────────
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath("/draco/");

  const loader = new GLTFLoader();
  loader.setDRACOLoader(dracoLoader);

  loader.load(
    glbUrl,
    (gltf) => {
      // Scale dari cm ke meter
      gltf.scene.scale.setScalar(0.01);
      scene.add(gltf.scene);

      animator = new FaceAnimator(gltf.scene);
      stopBlink = startAutoBlink(animator);
      avatarReady = true;
    },
    (xhr) => {
      avatarLoadProgress = Math.round((xhr.loaded / xhr.total) * 100);
    },
    (error) => console.error("Avatar load error:", error),
  );

  // ── RENDER LOOP ─────────────────────────────────────────────────────────
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    animator?.update(clock.getDelta());
    renderer.render(scene, camera);
  }
  animate();

  // ── RESIZE HANDLER ──────────────────────────────────────────────────────
  const ro = new ResizeObserver(() => {
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  });
  ro.observe(canvas);
}
```

---

### Variasi Framing per Kebutuhan

Ubah hanya `camera.position.z` dan `FOV` — sisanya tetap:

| Framing                      | FOV  | camera.z | Tampilan                                               |
| ---------------------------- | ---- | -------- | ------------------------------------------------------ |
| **Close-up wajah** (default) | `28` | `0.55`   | Bahu ke atas, wajah mengisi layar                      |
| **Medium shot**              | `35` | `0.75`   | Dada ke atas                                           |
| **Wide / full body**         | `50` | `1.8`    | Seluruh tubuh (tidak direkomendasikan untuk interview) |

Untuk HiReady, gunakan **close-up wajah** — konsisten dengan nuansa sesi wawancara tatap muka.

---

### Menyembunyikan Body, Hanya Tampilkan Kepala (Opsional)

Jika ingin performa lebih baik dan hanya menampilkan kepala tanpa harus crop kamera:

```typescript
// Setelah gltf dimuat, sembunyikan mesh body selain kepala
gltf.scene.traverse((obj) => {
  const node = obj as THREE.Mesh;
  const hiddenMeshes = [
    "hnsshoes_6176_Shape", // sepatu
    "Pants_14249_Shape", // celana
    "TrendyLongSleevesShirt_v01_7902_Shape", // baju
    "RL_HairMesh", // rambut (opsional, tampilkan jika mau)
  ];
  if (hiddenMeshes.includes(node.name)) {
    node.visible = false;
  }
});
```

> **Catatan:** Menyembunyikan mesh tidak mengurangi ukuran file yang diunduh —
> semua mesh tetap dimuat. Ini hanya mengoptimalkan render, bukan load time.
> Untuk mengurangi ukuran file, potong mesh di Blender sebelum export.

---

### Nama Mesh Lengkap dari Model Ini

Referensi untuk agent saat traverse scene:

| Node Name                               | Konten                        | Visible untuk Interview   |
| --------------------------------------- | ----------------------------- | ------------------------- |
| `CC_Base_Body`                          | Wajah + kulit (68 shape keys) | **Ya — wajib**            |
| `CC_Base_Eye`                           | Bola mata                     | **Ya — wajib**            |
| `CC_Base_Teeth`                         | Gigi                          | **Ya**                    |
| `CC_Base_Tongue`                        | Lidah (7 shape keys)          | Ya (opsional)             |
| `RL_HairMesh`                           | Rambut                        | Ya                        |
| `TrendyLongSleevesShirt_v01_7902_Shape` | Baju                          | Sembunyikan jika close-up |
| `Pants_14249_Shape`                     | Celana                        | Sembunyikan               |
| `hnsshoes_6176_Shape`                   | Sepatu                        | Sembunyikan               |

---

## Ringkasan Checklist untuk Agent

### Saat Membuat Model Baru (Instruksi untuk Artist/Pipeline)

- [ ] Export dari Character Creator dengan shape key wajah dari daftar "Kontrak Shape Key Wajib"
- [ ] Pastikan nama shape key **persis sama** (case-sensitive, underscore sama)
- [ ] Simpan file mentah di tempat terpisah
- [ ] Jalankan `gltf-pipeline` untuk kompresi Draco sebelum taruh di `/static/face/`
- [ ] Daftarkan avatar baru di tabel `interview_avatar` dengan `glbUrl` yang benar

### Saat Implementasi di Frontend

- [ ] Tambahkan state `avatarLoadProgress` dan `avatarReady`
- [ ] Gunakan `loader.load()` dengan callback `onProgress`
- [ ] Tambahkan skeleton placeholder di HTML saat loading
- [ ] Tambahkan `<link rel="prefetch">` di halaman disclaimer
- [ ] Buat `avatarCache.ts` untuk menghindari fetch ulang di sesi berikutnya
- [ ] Pastikan Nginx/server dikonfigurasi untuk gzip/brotli pada file `.glb`
- [ ] Scale model dengan `gltf.scene.scale.setScalar(0.01)` setelah dimuat (CC export dalam cm)
- [ ] Set kamera: FOV `28`, posisi `(0, 0.634, 0.55)`, lookAt `(0, 0.554, 0)`
- [ ] Sembunyikan mesh baju/celana/sepatu jika framing close-up wajah
