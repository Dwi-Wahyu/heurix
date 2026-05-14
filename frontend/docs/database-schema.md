# Heurix — Database Schema Documentation

> For LLM Agent / CLI Agent use. Read this before writing any query, migration, or data operation.

---

## CONTEXT

Heurix adalah platform simulasi wawancara imersif berbasis Avatar 3D.
Database dibagi dua lapisan:

1. **Auth Layer** — tabel `user`, `session`, `account`, `verification` (dikelola Better Auth, JANGAN dimodifikasi langsung)
2. **App Layer** — tabel Heurix yang berelasi ke `user.id`

Stack: **PostgreSQL + Drizzle ORM + SvelteKit**

---

## RULES FOR AGENT

```
RULE 1: Jangan pernah INSERT/UPDATE/DELETE pada tabel auth (user, session, account, verification).
RULE 2: Semua tabel app menggunakan text primary key — generate dengan cuid2 atau nanoid, BUKAN uuid().
RULE 3: Field timestamp menggunakan .defaultNow() — jangan isi manual kecuali startedAt / completedAt.
RULE 4: jsonb field selalu di-parse sebelum digunakan, jangan query field di dalamnya langsung.
RULE 5: Saat sesi selesai, update interview_session LALU buat session_report dalam satu transaksi.
RULE 6: user_profile dibuat otomatis saat user pertama kali login (1-to-1 dengan user).
```

---

## TABLE REFERENCE

### `user` ← AUTH, READ ONLY

| Column        | Type        | Notes                                    |
| ------------- | ----------- | ---------------------------------------- |
| id            | text PK     | Foreign key target untuk semua tabel app |
| name          | text        | Nama lengkap                             |
| email         | text UNIQUE |                                          |
| emailVerified | boolean     |                                          |
| image         | text        | URL avatar profil                        |
| createdAt     | timestamp   |                                          |
| updatedAt     | timestamp   |                                          |

---

### `master_institution` ← Master data institusi/perusahaan

| Column      | Type      | Notes                                               |
| ----------- | --------- | --------------------------------------------------- |
| id          | text PK   |                                                     |
| name        | text      | Nama instansi, e.g. "Bank Mandiri", "Akmil"         |
| logoUrl     | text      | URL logo instansi                                   |
| description | text      | Penjelasan singkat instansi                         |
| llmContext  | text      | Konteks khusus LLM (budaya kerja, nilai perusahaan) |
| createdAt   | timestamp |                                                     |
| updatedAt   | timestamp |                                                     |

---

### `master_position` ← Master data posisi yang dibuka

| Column        | Type                     | Notes                                         |
| ------------- | ------------------------ | --------------------------------------------- |
| id            | text PK                  |                                               |
| institutionId | text FK → institution.id | Cascade delete                                |
| name          | text                     | Nama jabatan, e.g. "Analis Data"              |
| description   | text                     | Deskripsi pekerjaan                           |
| llmContext    | text                     | Konteks khusus posisi (skill wajib, perilaku) |
| isActive      | boolean                  | Default true                                  |
| createdAt     | timestamp                |                                               |
| updatedAt     | timestamp                |                                               |

---

### `user_profile` ← 1-to-1 dengan user

Dibuat saat user register. Menyimpan data karir dan statistik agregat Heurix.

| Column                | Type                          | Notes                                                  |
| --------------------- | ----------------------------- | ------------------------------------------------------ |
| id                    | text PK                       |                                                        |
| userId                | text FK → user.id             | UNIQUE, cascade delete                                 |
| targetPositionId      | text FK → master_position.id  | Link ke master posisi                                  |
| targetInstitutionId   | text FK → master_institution.id | Link ke master instansi                                |
| preferredTrack        | enum \| null                  | Lihat ENUM: interview_track                            |
| totalSessions         | integer                       | Default 0. INCREMENT setiap sesi completed             |
| totalMinutesPracticed | integer                       | Default 0. Tambah durationSeconds/60 tiap sesi selesai |
| avgOverallScore       | real \| null                  | Rekalkulasi rata-rata setiap sesi baru selesai         |
| isPremium             | boolean                       | Default false                                          |
| premiumExpiresAt      | timestamp \| null             | Null jika free tier                                    |
| createdAt             | timestamp                     |                                                        |
| updatedAt             | timestamp                     |                                                        |

**Kapan diupdate:**

- Saat `interview_session.status` berubah ke `completed` → increment `totalSessions`, `totalMinutesPracticed`, rekalkulasi `avgOverallScore`

---

### `interview_avatar` ← Master data avatar pewawancara

Diisi oleh admin/seeder. Tidak dibuat oleh user.

| Column                | Type          | Notes                                              |
| --------------------- | ------------- | -------------------------------------------------- |
| id                    | text PK       |                                                    |
| name                  | text          | Nama karakter, e.g. "Ibu Sari", "Kolonel Ahmad"    |
| track                 | enum          | interview_track — avatar spesifik per jalur        |
| glbUrl                | text          | URL model 3D `.glb` untuk Three.js                 |
| thumbnailUrl          | text \| null  | Preview image                                      |
| ttsVoiceId            | text          | ID voice Kokoro TTS                                |
| ttsFriendlyParams     | jsonb \| null | `{ "speed": 1.0, "pitch": 1.0 }`                   |
| ttsFormalParams       | jsonb \| null | `{ "speed": 0.9, "pitch": 0.95 }`                  |
| ttsIntimidatingParams | jsonb \| null | `{ "speed": 0.85, "pitch": 0.9 }`                  |
| promptFriendly        | text \| null  | System prompt LLM untuk persona ramah              |
| promptFormal          | text \| null  | System prompt LLM untuk persona formal             |
| promptIntimidating    | text \| null  | System prompt LLM untuk persona intimidasi         |
| isActive              | boolean       | Default true. Set false untuk menonaktifkan avatar |
| createdAt             | timestamp     |                                                    |

**Cara pakai Persona Shift:**

```
Saat LLM trigger persona shift → baca kolom prompt{Persona} dan tts{Persona}Params
dari row avatar yang aktif → kirim ke Kokoro TTS + update currentPersona di interview_session
```

---

### `interview_session` ← Satu sesi simulasi wawancara

| Column             | Type                          | Notes                                                         |
| ------------------ | ----------------------------- | ------------------------------------------------------------- |
| id                 | text PK                       |                                                               |
| userId             | text FK → user.id             | cascade delete                                                |
| track              | enum                          | interview_track, ditentukan saat buat sesi                    |
| difficulty         | enum                          | difficulty, default 'medium'                                  |
| avatarId           | text FK → interview_avatar.id | Avatar yang dipakai sesi ini                                  |
| sessionContext     | text \| null                  | Konteks dinamis (e.g. CV, info lowongan spesifik)             |
| status             | enum                          | session_status, lihat lifecycle di bawah                      |
| startedAt          | timestamp \| null             | Diisi saat status → active                                    |
| completedAt        | timestamp \| null             | Diisi saat status → completed                                 |
| durationSeconds    | integer \| null               | completedAt - startedAt dalam detik                           |
| currentPersona     | enum                          | persona_type, default 'friendly'. Update real-time saat shift |
| personaShiftCount  | integer                       | Default 0. INCREMENT setiap terjadi persona shift             |
| overallScore       | real \| null                  | Diisi HANYA setelah status = completed                        |
| communicationScore | real \| null                  | Diisi HANYA setelah status = completed                        |
| consistencyScore   | real \| null                  | Diisi HANYA setelah status = completed                        |
| confidenceScore    | real \| null                  | Diisi HANYA setelah status = completed                        |
| createdAt          | timestamp                     |                                                               |
| updatedAt          | timestamp                     |                                                               |

**Session Lifecycle:**

```
waiting → active → completed
                 ↘ abandoned  (timeout atau user tutup browser)
```

---

### `session_turn` ← Satu giliran tanya-jawab

| Column                | Type                           | Notes                                                      |
| --------------------- | ------------------------------ | ---------------------------------------------------------- |
| id                    | text PK                        |                                                            |
| sessionId             | text FK → interview_session.id | cascade delete                                             |
| turnNumber            | integer                        | Urutan dalam sesi, mulai dari 1. UNIQUE per session        |
| questionText          | text                           | Teks pertanyaan avatar                                     |
| questionAudioUrl      | text \| null                   | URL file `.wav` hasil Kokoro TTS                           |
| visemeDataUrl         | text \| null                   | URL JSON data viseme untuk Three.js lip-sync               |
| personaAtTurn         | enum                           | persona_type aktif saat turn ini terjadi                   |
| answerTranscript      | text \| null                   | Hasil Whisper STT dari jawaban kandidat                    |
| answerAudioUrl        | text \| null                   | Rekaman audio kandidat (opsional, untuk playback)          |
| answerDurationSeconds | integer \| null                | Durasi jawaban dalam detik                                 |
| fillerWordCount       | integer                        | Default 0. Total filler words dalam jawaban                |
| fillerWords           | jsonb \| null                  | Breakdown per kata: `{ "em": 3, "anu": 1, "ya": 5 }`       |
| wordsPerMinute        | real \| null                   | Tempo bicara kandidat                                      |
| pauseCount            | integer                        | Default 0. Jumlah jeda signifikan dalam jawaban            |
| answerQuality         | real \| null                   | Skor 0–100 dari LLM untuk kualitas jawaban                 |
| isPersonaShiftTurn    | boolean                        | Default false. True jika shift terjadi di turn ini         |
| llmAnalysis           | text \| null                   | Catatan internal LLM (alasan probing, deteksi kontradiksi) |
| createdAt             | timestamp                      |                                                            |

---

### `session_report` ← Laporan analitik pasca-sesi

| Column                | Type                           | Notes                                                        |
| --------------------- | ------------------------------ | ------------------------------------------------------------ |
| id                    | text PK                        |                                                              |
| sessionId             | text FK → interview_session.id | UNIQUE, cascade delete                                       |
| userId                | text FK → user.id              | Denormalisasi untuk query langsung by user                   |
| totalFillerWords      | integer                        | Default 0                                                    |
| fillerWordBreakdown   | jsonb \| null                  | `{ "em": 10, "anu": 3, "ya": 7 }`                            |
| avgWordsPerMinute     | real \| null                   | Rata-rata WPM seluruh turn                                   |
| avgPauseDuration      | real \| null                   | Rata-rata durasi jeda dalam detik                            |
| totalTurns            | integer                        | Jumlah turn yang terjadi                                     |
| overallScore          | real                           | 0–100                                                        |
| communicationScore    | real                           | 0–100. Berbasis WPM, filler, pause                           |
| consistencyScore      | real                           | 0–100. Dinilai LLM secara semantik                           |
| confidenceScore       | real                           | 0–100. Berbasis kecepatan respons, kelengkapan jawaban       |
| stressResistanceScore | real \| null                   | 0–100. NULL jika tidak ada persona shift dalam sesi          |
| strengths             | jsonb \| null                  | `["Struktur jawaban jelas", "Tempo bicara baik"]`            |
| weaknesses            | jsonb \| null                  | `["Terlalu banyak filler words", "Jawaban terlalu singkat"]` |
| recommendations       | jsonb \| null                  | `["Latih kalimat pembuka", "Kurangi kata 'em' dan 'anu'"]`   |
| evaluationNarrative   | text \| null                   | Narasi evaluasi panjang dari LLM                             |
| generatedAt           | timestamp                      | Waktu laporan dibuat                                         |

---

### `question_bank` ← Bank soal (opsional, untuk caching)

| Column                | Type                         | Notes                                                        |
| --------------------- | ---------------------------- | ------------------------------------------------------------ |
| id                    | text PK                      |                                                              |
| track                 | enum                         | interview_track                                              |
| difficulty            | enum                         | difficulty                                                   |
| category              | text                         | `"mental_ideologi"`, `"behavioral"`, `"stress"`, `"opening"` |
| questionText          | text                         | Teks pertanyaan                                              |
| institutionId         | text FK → master_institution.id | (Opsional) Pertanyaan spesifik instansi                      |
| positionId            | text FK → master_position.id | (Opsional) Pertanyaan spesifik posisi                        |
| isPersonaShiftTrigger | boolean                      | Default false. Pertanyaan ini bisa trigger Persona Shift     |
| usageCount            | integer                      | Default 0. INCREMENT setiap pertanyaan ini dipakai           |
| createdAt             | timestamp                    |                                                              |

---

## ENUMS

(Tetap sama seperti sebelumnya)

---

## RELATION MAP

```
user (AUTH)
 ├── user_profile          (1-to-1)
 │     ├── target_position (many-to-1)
 │     └── target_institution (many-to-1)
 └── interview_session[]   (1-to-many)
       ├── session_turn[]  (1-to-many)
       ├── session_report  (1-to-1)
       └── interview_avatar (many-to-1)

master_institution
 └── master_position[]     (1-to-many)
       └── question_bank[] (1-to-many, optional)
```

---

## NOTES FOR AGENT

- Gunakan `llmContext` dari `master_institution` dan `master_position` serta `sessionContext` dari `interview_session` untuk membangun prompt LLM yang akurat.
- LLM diharapkan memprioritaskan pertanyaan dari `question_bank` yang relevan dengan `institutionId` atau `positionId` jika tersedia.
