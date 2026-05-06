# Dokumentasi Animasi Wajah — Viseme & Ekspresi

## Model: `boy-character-copy-optimized.glb`

### Stack: Three.js + SvelteKit

---

## 1. Konsep Viseme

**Viseme** adalah representasi visual dari sebuah fonem (satuan bunyi). Saat karakter berbicara, mulut tidak bergerak per huruf melainkan per _bentuk bibir_ yang dihasilkan bunyi tersebut. Satu viseme bisa merepresentasikan beberapa fonem sekaligus karena bentuk bibirnya identik secara visual.

```
Fonem  →  Viseme  →  Shape Key(s) pada model
  "a"  →   AA    →  Open + Mouth_Open
  "m"  →   MB    →  Explosive (lips closed)
  "f"  →   FV    →  Dental_Lip
```

Model ini menggunakan konvensi **Character Creator (CC4)** dari Reallusion yang sudah menyertakan shape key viseme secara native di indeks 0–7.

---

## 2. Inventaris Shape Keys Lengkap

Mesh target: **`CC_Base_Body`** (semua 6 primitif memiliki shape keys identik)
Mesh tambahan: **`CC_Base_Tongue`** (7 shape keys lidah)

### 2.1 Shape Keys Viseme (Indeks 0–7)

Shape keys ini adalah inti lip-sync. Dirancang untuk dikombinasikan.

| Indeks | Nama         | Fonem yang direpresentasikan | Deskripsi bentuk bibir                |
| ------ | ------------ | ---------------------------- | ------------------------------------- |
| 0      | `Open`       | AH, AA (a, ā)                | Mulut terbuka lebar, rahang turun     |
| 1      | `Explosive`  | B, P, M (b, p, m)            | Bibir menutup rapat (plosif bilabial) |
| 2      | `Dental_Lip` | F, V (f, v)                  | Gigi atas menyentuh bibir bawah       |
| 3      | `Tight-O`    | OO, U (u, ū, w)              | Bibir maju membulat ketat             |
| 4      | `Tight`      | EE, IH (i, ī)                | Bibir terentang horizontal/senyum     |
| 5      | `Wide`       | AE, EH (e, é)                | Mulut terbuka lebar ke samping        |
| 6      | `Affricate`  | CH, J, SH, ZH (c, j, sy)     | Bibir maju sedikit, celah sempit      |
| 7      | `Lip_Open`   | TH, DH (th, dh)              | Lidah terlihat di antara bibir        |

> **Catatan untuk Bahasa Indonesia:** Fonem /r/, /ng/, /ny/ tidak memiliki viseme khusus. Gunakan `Open` (0) sebagai fallback untuk vokal dan `Explosive` (1) untuk konsonan tanpa bentuk bibir yang mencolok.

### 2.2 Shape Keys Ekspresi Mata

| Indeks | Nama           | Fungsi                     |
| ------ | -------------- | -------------------------- |
| 16     | `Eye_Blink`    | Kedip kedua mata sekaligus |
| 17     | `Eye_Blink_L`  | Kedip mata kiri saja       |
| 18     | `Eye_Blink_R`  | Kedip mata kanan saja      |
| 19     | `Eye_Wide_L`   | Mata kiri membuka lebar    |
| 20     | `Eye_Wide_R`   | Mata kanan membuka lebar   |
| 21     | `Eye_Squint_L` | Mata kiri menyipit         |
| 22     | `Eye_Squint_R` | Mata kanan menyipit        |

### 2.3 Shape Keys Ekspresi Alis

| Indeks | Nama                 | Fungsi                       |
| ------ | -------------------- | ---------------------------- |
| 8      | `Brow_Raise_Inner_L` | Alis kiri bagian dalam naik  |
| 9      | `Brow_Raise_Inner_R` | Alis kanan bagian dalam naik |
| 10     | `Brow_Raise_Outer_L` | Alis kiri bagian luar naik   |
| 11     | `Brow_Raise_Outer_R` | Alis kanan bagian luar naik  |
| 12     | `Brow_Drop_L`        | Alis kiri turun/mengernyit   |
| 13     | `Brow_Drop_R`        | Alis kanan turun/mengernyit  |
| 14     | `Brow_Raise_L`       | Seluruh alis kiri naik       |
| 15     | `Brow_Raise_R`       | Seluruh alis kanan naik      |

### 2.4 Shape Keys Hidung & Pipi

| Indeks | Nama                  | Fungsi                         |
| ------ | --------------------- | ------------------------------ |
| 23     | `Nose_Scrunch`        | Hidung mengkerut               |
| 24     | `Nose_Flanks_Raise`   | Kedua sisi hidung naik         |
| 25     | `Nose_Flank_Raise_L`  | Sisi kiri hidung naik          |
| 26     | `Nose_Flank_Raise_R`  | Sisi kanan hidung naik         |
| 27     | `Nose_Nostrils_Flare` | Lubang hidung melebar          |
| 28     | `Cheek_Raise_L`       | Pipi kiri naik (senyum matang) |
| 29     | `Cheek_Raise_R`       | Pipi kanan naik                |
| 30     | `Cheek_Suck`          | Pipi terhisap ke dalam         |
| 31     | `Cheek_Blow_L`        | Pipi kiri menggembung          |
| 32     | `Cheek_Blow_R`        | Pipi kanan menggembung         |

### 2.5 Shape Keys Mulut & Bibir (Ekspresi)

| Indeks | Nama                     | Fungsi                                |
| ------ | ------------------------ | ------------------------------------- |
| 33     | `Mouth_Smile`            | Senyum simetris                       |
| 34     | `Mouth_Smile_L`          | Sudut mulut kiri naik                 |
| 35     | `Mouth_Smile_R`          | Sudut mulut kanan naik                |
| 36     | `Mouth_Frown`            | Cemberut simetris                     |
| 37     | `Mouth_Frown_L`          | Sudut mulut kiri turun                |
| 38     | `Mouth_Frown_R`          | Sudut mulut kanan turun               |
| 39     | `Mouth_Blow`             | Meniup (pipi kembung, mulut maju)     |
| 40     | `Mouth_Pucker`           | Mencibir/mencium udara                |
| 41     | `Mouth_Pucker_Open`      | Mencibir dengan mulut sedikit terbuka |
| 42     | `Mouth_Widen`            | Mulut melebar                         |
| 43     | `Mouth_Widen_Sides`      | Sudut mulut melebar ke samping        |
| 44     | `Mouth_Dimple_L`         | Lesung pipit kiri                     |
| 45     | `Mouth_Dimple_R`         | Lesung pipit kanan                    |
| 46     | `Mouth_Plosive`          | Bibir rapat (mendahului bunyi plosif) |
| 47     | `Mouth_Lips_Tight`       | Bibir rapat tegang                    |
| 48     | `Mouth_Lips_Tuck`        | Bibir terlipat ke dalam               |
| 49     | `Mouth_Lips_Open`        | Bibir terbuka natural                 |
| 50     | `Mouth_Lips_Part`        | Bibir terpisah sedikit                |
| 51     | `Mouth_Bottom_Lip_Down`  | Bibir bawah turun                     |
| 52     | `Mouth_Top_Lip_Up`       | Bibir atas naik                       |
| 53     | `Mouth_Top_Lip_Under`    | Bibir atas melipat ke bawah           |
| 54     | `Mouth_Bottom_Lip_Under` | Bibir bawah melipat ke atas           |
| 55     | `Mouth_Snarl_Upper_L`    | Snarl/geraman bibir atas kiri         |
| 56     | `Mouth_Snarl_Upper_R`    | Snarl/geraman bibir atas kanan        |
| 57     | `Mouth_Snarl_Lower_L`    | Snarl bibir bawah kiri                |
| 58     | `Mouth_Snarl_Lower_R`    | Snarl bibir bawah kanan               |
| 59     | `Mouth_Bottom_Lip_Bite`  | Menggigit bibir bawah                 |
| 60     | `Mouth_Down`             | Seluruh area mulut turun              |
| 61     | `Mouth_Up`               | Seluruh area mulut naik               |
| 62     | `Mouth_L`                | Mulut bergeser ke kiri                |
| 63     | `Mouth_R`                | Mulut bergeser ke kanan               |
| 64     | `Mouth_Lips_Jaw_Adjust`  | Penyesuaian rahang-bibir              |
| 65     | `Mouth_Bottom_Lip_Trans` | Transisi bibir bawah                  |
| 66     | `Mouth_Skewer`           | Mulut miring/mencong                  |
| 67     | `Mouth_Open`             | Mulut terbuka (rahang turun)          |

### 2.6 Shape Keys Lidah (`CC_Base_Tongue`)

| Indeks | Nama            | Fungsi                    |
| ------ | --------------- | ------------------------- |
| 0      | `Tongue_up`     | Lidah ke atas             |
| 1      | `Tongue_Raise`  | Lidah terangkat           |
| 2      | `Tongue_Out`    | Lidah terjulur            |
| 3      | `Tongue_Narrow` | Lidah menyempit           |
| 4      | `Tongue_Lower`  | Lidah ke bawah            |
| 5      | `Tongue_Curl-U` | Lidah menggulung ke atas  |
| 6      | `Tongue_Curl-D` | Lidah menggulung ke bawah |

---

## 3. Tabel Pemetaan Viseme → Shape Keys

Tabel ini adalah referensi utama untuk sistem lip-sync.

| Viseme ID | Label     | Shape Keys Utama                       | Shape Keys Tambahan (opsional)         | Contoh Fonem (ID)        |
| --------- | --------- | -------------------------------------- | -------------------------------------- | ------------------------ |
| `sil`     | Silence   | semua = 0                              | —                                      | (diam)                   |
| `PP`      | B/P/M     | `Explosive` = 1.0                      | `Mouth_Plosive` = 0.5                  | b, p, m                  |
| `FF`      | F/V       | `Dental_Lip` = 1.0                     | `Mouth_Bottom_Lip_Down` = 0.3          | f, v                     |
| `TH`      | TH/DH     | `Lip_Open` = 1.0                       | `Tongue_up` = 0.6 _(pada tongue mesh)_ | th (tidak ada di BI)     |
| `DD`      | D/T/N     | `Open` = 0.3, `Mouth_Open` = 0.2       | `Tongue_Raise` = 0.5                   | d, t, n                  |
| `kk`      | K/G/NG    | `Open` = 0.5, `Mouth_Open` = 0.4       | —                                      | k, g, ng                 |
| `CH`      | CH/J/SH   | `Affricate` = 1.0                      | `Mouth_Pucker` = 0.2                   | c (dalam "cinta"), j, sy |
| `SS`      | S/Z       | `Tight` = 0.6, `Mouth_Lips_Part` = 0.4 | —                                      | s, z                     |
| `nn`      | N akhir   | `Open` = 0.2, `Mouth_Open` = 0.1       | `Tongue_Raise` = 0.3                   | n di akhir kata          |
| `RR`      | R         | `Open` = 0.4, `Mouth_Open` = 0.3       | —                                      | r                        |
| `AA`      | A         | `Open` = 1.0, `Mouth_Open` = 0.8       | `Wide` = 0.3                           | a                        |
| `EE`      | E/I       | `Tight` = 1.0, `Wide` = 0.5            | `Mouth_Widen_Sides` = 0.3              | e, i                     |
| `II`      | I panjang | `Tight` = 1.0, `Wide` = 0.7            | `Mouth_Smile` = 0.2                    | i (panjang)              |
| `OO`      | O/U       | `Tight-O` = 1.0, `Mouth_Open` = 0.5    | `Mouth_Pucker` = 0.3                   | o, u                     |
| `UU`      | U panjang | `Tight-O` = 1.0                        | `Mouth_Pucker` = 0.6                   | u (panjang)              |
| `WW`      | W         | `Tight-O` = 0.8                        | `Mouth_Pucker` = 0.4                   | w                        |

---

## 4. Implementasi Three.js

### 4.1 Utilitas: Mendapatkan Referensi Morph Target

```typescript
// visemeController.ts

import * as THREE from "three";

/**
 * Kumpulkan semua mesh yang memiliki morphTargetDictionary
 * dari model yang sudah dimuat.
 */
export function collectMorphMeshes(model: THREE.Group): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  model.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.isMesh && mesh.morphTargetDictionary) {
      meshes.push(mesh);
    }
  });
  return meshes;
}

/**
 * Set nilai satu shape key pada semua mesh yang memilikinya.
 * @param meshes    - array hasil collectMorphMeshes()
 * @param shapeName - nama shape key, e.g. "Open"
 * @param value     - nilai 0.0 – 1.0
 */
export function setMorph(
  meshes: THREE.Mesh[],
  shapeName: string,
  value: number,
): void {
  for (const mesh of meshes) {
    const idx = mesh.morphTargetDictionary?.[shapeName];
    if (idx !== undefined && mesh.morphTargetInfluences) {
      mesh.morphTargetInfluences[idx] = Math.max(0, Math.min(1, value));
    }
  }
}

/**
 * Reset semua morph target ke 0 (posisi netral).
 */
export function resetAllMorphs(meshes: THREE.Mesh[]): void {
  for (const mesh of meshes) {
    if (mesh.morphTargetInfluences) {
      mesh.morphTargetInfluences.fill(0);
    }
  }
}
```

### 4.2 Tabel Viseme sebagai Konstanta

```typescript
// visemeMap.ts

export type ShapeKeyWeights = Record<string, number>;

/**
 * Peta viseme → shape key weights.
 * Semua nilai 0.0 – 1.0.
 * Shape keys yang tidak disebutkan akan di-reset ke 0.
 */
export const VISEME_MAP: Record<string, ShapeKeyWeights> = {
  sil: {},
  PP: { Explosive: 1.0, Mouth_Plosive: 0.5 },
  FF: { Dental_Lip: 1.0, Mouth_Bottom_Lip_Down: 0.3 },
  TH: { Lip_Open: 1.0 },
  DD: { Open: 0.3, Mouth_Open: 0.2 },
  kk: { Open: 0.5, Mouth_Open: 0.4 },
  CH: { Affricate: 1.0, Mouth_Pucker: 0.2 },
  SS: { Tight: 0.6, Mouth_Lips_Part: 0.4 },
  nn: { Open: 0.2, Mouth_Open: 0.1 },
  RR: { Open: 0.4, Mouth_Open: 0.3 },
  AA: { Open: 1.0, Mouth_Open: 0.8, Wide: 0.3 },
  EE: { Tight: 1.0, Wide: 0.5, Mouth_Widen_Sides: 0.3 },
  II: { Tight: 1.0, Wide: 0.7, Mouth_Smile: 0.2 },
  OO: { "Tight-O": 1.0, Mouth_Open: 0.5, Mouth_Pucker: 0.3 },
  UU: { "Tight-O": 1.0, Mouth_Pucker: 0.6 },
  WW: { "Tight-O": 0.8, Mouth_Pucker: 0.4 },
};

/** Shape keys yang relevan untuk viseme (untuk reset selektif) */
export const VISEME_SHAPE_KEYS = [
  "Open",
  "Explosive",
  "Dental_Lip",
  "Tight-O",
  "Tight",
  "Wide",
  "Affricate",
  "Lip_Open",
  "Mouth_Open",
  "Mouth_Plosive",
  "Mouth_Pucker",
  "Mouth_Pucker_Open",
  "Mouth_Lips_Part",
  "Mouth_Widen_Sides",
  "Mouth_Bottom_Lip_Down",
  "Mouth_Smile",
];
```

### 4.3 Controller dengan Lerp (Smooth Transition)

```typescript
// FaceAnimator.ts

import * as THREE from "three";
import {
  VISEME_MAP,
  VISEME_SHAPE_KEYS,
  type ShapeKeyWeights,
} from "./visemeMap";
import {
  collectMorphMeshes,
  setMorph,
  resetAllMorphs,
} from "./visemeController";

export class FaceAnimator {
  private meshes: THREE.Mesh[];
  private currentWeights: ShapeKeyWeights = {};
  private targetWeights: ShapeKeyWeights = {};
  private lerpSpeed = 12; // semakin tinggi = semakin cepat transisi

  constructor(model: THREE.Group) {
    this.meshes = collectMorphMeshes(model);
  }

  /**
   * Set viseme target. Transisi dilakukan via lerp di update().
   * @param visemeId - key dari VISEME_MAP, e.g. "AA", "PP", "sil"
   */
  setViseme(visemeId: string): void {
    const weights = VISEME_MAP[visemeId] ?? {};

    // Reset semua viseme key ke 0, lalu set yang aktif
    this.targetWeights = {};
    for (const key of VISEME_SHAPE_KEYS) {
      this.targetWeights[key] = 0;
    }
    Object.assign(this.targetWeights, weights);
  }

  /**
   * Panggil di dalam loop animasi Three.js (requestAnimationFrame).
   * @param delta - waktu sejak frame terakhir dalam detik (dari THREE.Clock)
   */
  update(delta: number): void {
    for (const key of VISEME_SHAPE_KEYS) {
      const current = this.currentWeights[key] ?? 0;
      const target = this.targetWeights[key] ?? 0;

      if (Math.abs(current - target) < 0.001) {
        this.currentWeights[key] = target;
      } else {
        this.currentWeights[key] = THREE.MathUtils.lerp(
          current,
          target,
          1 - Math.exp(-this.lerpSpeed * delta),
        );
      }

      setMorph(this.meshes, key, this.currentWeights[key]);
    }
  }

  /** Set ekspresi emosi (alis, mata, pipi) — terpisah dari viseme */
  setExpression(weights: ShapeKeyWeights): void {
    for (const [key, value] of Object.entries(weights)) {
      setMorph(this.meshes, key, value);
    }
  }

  /** Kembali ke wajah netral seketika */
  resetFace(): void {
    resetAllMorphs(this.meshes);
    this.currentWeights = {};
    this.targetWeights = {};
  }
}
```

### 4.4 Integrasi ke Komponen Svelte

```svelte
<!-- +page.svelte (potongan relevan) -->
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
  import { FaceAnimator } from '$lib/FaceAnimator';

  let faceAnimator: FaceAnimator | null = null;
  const clock = new THREE.Clock();

  onMount(() => {
    // ... setup scene, camera, renderer seperti biasa ...

    const loader = new GLTFLoader();
    loader.load('/face/boy/boy-character-copy-optimized.glb', (gltf) => {
      scene.add(gltf.scene);

      // Inisialisasi FaceAnimator setelah model dimuat
      faceAnimator = new FaceAnimator(gltf.scene);
    });

    function animate() {
      requestAnimationFrame(animate);
      const delta = clock.getDelta();

      // Update face animation setiap frame
      faceAnimator?.update(delta);

      renderer.render(scene, camera);
    }
    animate();
  });

  // Contoh: trigger viseme dari luar
  function speak(visemeId: string) {
    faceAnimator?.setViseme(visemeId);

    // Kembalikan ke diam setelah 200ms (durasi satu suku kata)
    setTimeout(() => faceAnimator?.setViseme('sil'), 200);
  }
</script>
```

---

## 5. Preset Ekspresi Emosi

Kombinasi shape keys yang siap pakai untuk berbagai ekspresi wajah.

```typescript
// emotionPresets.ts

import type { ShapeKeyWeights } from "./visemeMap";

export const EMOTIONS: Record<string, ShapeKeyWeights> = {
  /** Wajah netral — semua 0 */
  neutral: {},

  /** Bahagia / senang */
  happy: {
    Mouth_Smile: 0.8,
    Cheek_Raise_L: 0.6,
    Cheek_Raise_R: 0.6,
    Eye_Squint_L: 0.3,
    Eye_Squint_R: 0.3,
    Brow_Raise_L: 0.2,
    Brow_Raise_R: 0.2,
  },

  /** Sedih */
  sad: {
    Mouth_Frown: 0.7,
    Brow_Raise_Inner_L: 0.8,
    Brow_Raise_Inner_R: 0.8,
    Brow_Drop_L: 0.3,
    Brow_Drop_R: 0.3,
  },

  /** Terkejut */
  surprised: {
    Mouth_Open: 0.6,
    Mouth_Lips_Open: 0.7,
    Eye_Wide_L: 1.0,
    Eye_Wide_R: 1.0,
    Brow_Raise_L: 1.0,
    Brow_Raise_R: 1.0,
  },

  /** Marah */
  angry: {
    Mouth_Frown: 0.5,
    Brow_Drop_L: 0.9,
    Brow_Drop_R: 0.9,
    Nose_Scrunch: 0.4,
    Mouth_Snarl_Upper_L: 0.3,
    Mouth_Snarl_Upper_R: 0.3,
    Eye_Squint_L: 0.5,
    Eye_Squint_R: 0.5,
  },

  /** Takut */
  fearful: {
    Eye_Wide_L: 0.8,
    Eye_Wide_R: 0.8,
    Brow_Raise_Inner_L: 1.0,
    Brow_Raise_Inner_R: 1.0,
    Mouth_Open: 0.3,
    Mouth_Lips_Part: 0.5,
  },

  /** Jijik */
  disgusted: {
    Nose_Scrunch: 0.9,
    Nose_Flanks_Raise: 0.7,
    Mouth_Frown: 0.4,
    Mouth_Snarl_Upper_L: 0.6,
    Mouth_Snarl_Upper_R: 0.6,
    Eye_Squint_L: 0.4,
    Eye_Squint_R: 0.4,
  },

  /** Bingung / skeptis */
  confused: {
    Brow_Raise_Outer_L: 0.7,
    Brow_Drop_R: 0.5,
    Mouth_Skewer: 0.4,
    Mouth_R: 0.2,
  },
};
```

---

## 6. Sistem Lip-Sync dengan Web Speech API

Integrasi viseme ke TTS browser secara real-time.

```typescript
// lipSync.ts

import { FaceAnimator } from "./FaceAnimator";

/**
 * Peta dari nama boundary/phoneme Web Speech API → viseme ID kita.
 * Web Speech API mengirim event `boundary` dengan properti `name`.
 */
const SPEECH_TO_VISEME: Record<string, string> = {
  // Vokal
  a: "AA",
  A: "AA",
  e: "EE",
  E: "EE",
  i: "II",
  I: "II",
  o: "OO",
  O: "OO",
  u: "UU",
  U: "UU",
  // Konsonan bilabial
  b: "PP",
  p: "PP",
  m: "PP",
  // Labiodental
  f: "FF",
  v: "FF",
  // Dental
  t: "DD",
  d: "DD",
  n: "nn",
  // Velar
  k: "kk",
  g: "kk",
  // Afrikat & sibilant
  s: "SS",
  z: "SS",
  j: "CH",
  c: "CH",
  // Approksiman
  r: "RR",
  l: "RR",
  w: "WW",
  y: "EE",
};

export function speakWithLipSync(
  text: string,
  animator: FaceAnimator,
  lang = "id-ID",
): void {
  if (!window.speechSynthesis) {
    console.warn("Web Speech API tidak tersedia di browser ini.");
    return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.9;

  // Event boundary dipanggil tiap kata/suku kata
  utterance.addEventListener("boundary", (event) => {
    const charIndex = event.charIndex;
    const char = text[charIndex]?.toLowerCase() ?? "";
    const visemeId = SPEECH_TO_VISEME[char] ?? "sil";
    animator.setViseme(visemeId);
  });

  utterance.addEventListener("end", () => {
    // Kembali ke diam setelah selesai berbicara
    setTimeout(() => animator.setViseme("sil"), 150);
  });

  window.speechSynthesis.cancel(); // batalkan yang sedang berjalan
  window.speechSynthesis.speak(utterance);
}
```

---

## 7. Auto-Blink

Kedip mata otomatis agar karakter terlihat hidup.

```typescript
// autoBlink.ts

import type { FaceAnimator } from "./FaceAnimator";

export function startAutoBlink(animator: FaceAnimator): () => void {
  let timeoutId: ReturnType<typeof setTimeout>;

  function scheduleNextBlink() {
    // Kedip setiap 2–6 detik secara acak
    const delay = 2000 + Math.random() * 4000;

    timeoutId = setTimeout(() => {
      // Durasi kedip: 80–150ms
      const blinkDuration = 80 + Math.random() * 70;

      animator.setExpression({ Eye_Blink: 1.0 });

      setTimeout(() => {
        animator.setExpression({ Eye_Blink: 0 });
        scheduleNextBlink();
      }, blinkDuration);
    }, delay);
  }

  scheduleNextBlink();

  // Kembalikan fungsi cleanup untuk menghentikan blink
  return () => clearTimeout(timeoutId);
}
```

---

## 8. Catatan Penting

**Semua primitif harus diupdate.** Mesh `CC_Base_Body` memiliki 6 primitif dan semuanya memiliki shape keys yang sama. Fungsi `collectMorphMeshes` akan mengambil kesemuanya secara otomatis — pastikan tidak memfilter hanya satu primitif.

**Urutan index = urutan `morphTargetInfluences`.** Three.js GLTFLoader memetakan `targetNames` ke `morphTargetDictionary` secara otomatis, sehingga Anda bisa mengakses via nama (`mesh.morphTargetDictionary["Open"]`) maupun indeks (0).

**Tidak ada animasi tersimpan di file.** Model ini tidak memiliki animation clip — seluruh animasi wajah harus dikendalikan secara programatik melalui `morphTargetInfluences` seperti yang dijelaskan di atas.

**Tongue mesh terpisah.** Shape keys lidah (`Tongue_*`) ada di mesh `CC_Base_Tongue`, bukan di `CC_Base_Body`. `collectMorphMeshes` akan mengambilnya juga, namun pastikan `setMorph` dipanggil dengan nama yang benar.

**Nilai shape key adalah additive.** Beberapa shape keys bisa aktif bersamaan dan nilainya dijumlahkan. Ini memungkinkan kombinasi ekspresi + viseme secara simultan — misalnya karakter tersenyum sambil berbicara.
