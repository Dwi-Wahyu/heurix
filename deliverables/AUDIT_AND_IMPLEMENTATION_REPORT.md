# Heurix — Audit & Implementasi Adaptive Personalization Engine (APE)

## 1. Laporan Audit

### 1.1 Apa yang bisa diaudit secara statis vs. yang butuh runtime

Checklist 4.1 di context.md meminta pengukuran latensi, FPS, RAM, dan error rate koneksi —
ini **tidak bisa diverifikasi dari source code saja**, karena butuh instance backend/frontend
yang berjalan. Saya tidak menjalankan server (tidak ada di scope file yang diberikan), jadi
butuh Anda jalankan secara manual — instruksinya ada di §5. Yang bisa saya audit dari kode:

| Aspek                                   | Temuan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Pipeline STT→LLM→TTS**                | Sesuai — `transcriber.py` (faster-whisper) → `brain.py` (Groq) → `speech.py` (edge_tts), dipanggil berurutan di `websocket.py`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **STT model**                           | `Transcriber` pakai **faster-whisper**, bukan Whisper murni — lebih cepat & cocok untuk CPU. `WHISPER_MODEL` default `"small"` di `config.py`, sudah sesuai rekomendasi upgrade di context.md §4.1. ✅ Tidak perlu diubah.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **TTS engine — MISMATCH dari proposal** | context.md & skema Drizzle menyebut **Kokoro TTS**, tapi `speech.py` memakai **`edge_tts`** (Microsoft Edge Neural TTS, `id-ID-ArdiNeural`). Ini bukan bug, tapi dokumentasi/skema menyesatkan — sudah saya perbaiki komentarnya di `schema.ts`. Konsekuensi bagus: `edge_tts` mendukung parameter `rate`/`pitch` native, jadi Pilar 1 & 3 (kontrol speed/pitch) bisa langsung dipasang tanpa ganti engine.                                                                                                                                                                                                                                                                                                              |
| **Blocking call di async handler**      | `Transcriber.transcribe_and_detect_fillers()` (faster-whisper, CPU-bound) dipanggil secara **sinkron** langsung di dalam `async def websocket_endpoint`. Ini akan **memblokir event loop** FastAPI selama proses transkripsi berjalan (bisa 1-3 detik+), yang berarti WebSocket sesi user LAIN akan macet bersamaan. **Rekomendasi**: bungkus dengan `await asyncio.to_thread(transcriber.transcribe_and_detect_fillers, temp_filename)`. Tidak saya ubah di patch ini (di luar scope APE), tapi ini kandidat kuat untuk kontributor terhadap masalah "latensi >10 detik" di checklist 4.1 kalau ada beberapa sesi paralel.                                                                                              |
| **Dynamic Stress Interview**            | Logic probing ada di system prompt (`PHASE_INSTRUCTIONS`, `difficulty_rules`), bukan classifier eksplisit. Berfungsi, tapi "akurasi klasifikasi" di checklist 4.1 hanya bisa diuji lewat 5 skenario manual (lihat §5.1) karena keputusan diserahkan ke LLM, bukan kode rule-based yang bisa dites unit test.                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Persona Shift (3 lapisan)**           | `should_shift_persona()` di `brain.py` mengubah `currentPersona` di DB, lalu `websocket.py` mengirim field `persona` di setiap `QUESTION_CHUNK`. Frontend (`interview/+page.svelte` baris ~663-778) mengubah ekspresi avatar berdasarkan `persona`. TTS param per-persona sudah ada (`ttsFriendlyParams` dkk di skema) **tapi tidak pernah dibaca/dipakai** — `speech_service.generate_speech_with_visemes()` sebelum patch ini tidak menerima parameter apa pun. Jadi "3 lapisan" itu sebenarnya baru 2 lapisan aktif (ekspresi + LLM), TTS speed/pitch dari `ttsFriendlyParams`/dst diam-diam tidak pernah dipakai. Saya tidak mengaktifkan kolom lama ini (di luar scope APE), tapi ini temuan penting untuk dicatat. |
| **QDRANT config tak terpakai**          | `config.py` masih punya `QDRANT_HOST`/`QDRANT_PORT` — sisa rencana RAG yang sudah dibatalkan sesuai context.md §3. Tidak berbahaya, tapi bisa dibersihkan (deatched dead config). Tidak saya hapus (bukan bagian dari instruksi APE, dan menghapus config berisiko kalau masih dipakai file lain di luar bundle ini).                                                                                                                                                                                                                                                                                                                                                                                                    |

### 1.2 Audit Database & Skema (4.2)

| Yang dicek                                                 | Status sebelum patch                                                                                                                                                                                                                                                                                                                                                                                                                      | Setelah patch                                                         |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `users`/`user_profile` punya `weakness_tags` (JSON/Array)? | ❌ Tidak ada                                                                                                                                                                                                                                                                                                                                                                                                                              | ✅ Ditambahkan (`weaknessTags`, jsonb)                                |
| `users`/`user_profile` punya `sri_history` (JSON/Array)?   | ❌ Tidak ada                                                                                                                                                                                                                                                                                                                                                                                                                              | ✅ Ditambahkan (`sriHistory`, jsonb) + `lastSri`, `nextPressureLevel` |
| `sessions` punya kolom `scenario`?                         | ❌ Tidak ada                                                                                                                                                                                                                                                                                                                                                                                                                              | ✅ Ditambahkan (`scenario`, enum `friendly/grilling/stress_test`)     |
| `sessions` punya `transcript_full` & `metrics` (JSON)?     | ⚠️ Tidak literal seperti itu, tapi setara: transkrip tersebar per-turn di `session_turn.answer_transcript`, metrik tersimpan sebagai kolom-kolom terstruktur di `session_report` (bukan satu blob JSON). **Ini sebenarnya desain yang lebih baik** (queryable per kolom) daripada satu blob JSON — saya **tidak mengubahnya** menjadi blob demi konsistensi, cukup menambah `sri_score` sebagai kolom baru mengikuti pola yang sudah ada. | — (tidak diubah, sudah cukup)                                         |

### 1.3 Temuan arsitektur penting (memengaruhi cara APE diimplementasikan)

1. **`Difficulty` enum (`easy/medium/hard/extreme`) sudah ada di `InterviewSession` tapi TIDAK PERNAH di-set oleh frontend** — selalu jatuh ke default `medium`. Ini bukan mekanisme Pilar 1 yang diminta context.md (yang minta level 0/1/2 berbasis SRI dari sesi sebelumnya, computed otomatis). Saya **tidak merepurpose** kolom ini karena sudah dipakai `SHIFT_THRESHOLDS`/`difficulty_rules` untuk hal lain (persona shift & probing text) — merepurpose berisiko mengubah perilaku yang sudah berjalan. Sebagai gantinya saya menambah kolom **baru** `pressureLevel` (0/1/2) yang independen, sesuai instruksi "JANGAN mengubah arsitektur pipeline secara fundamental, cukup tambahkan parameter dinamis."
2. **Ekspresi avatar per skenario (kolom "Ekspresi Avatar" di tabel 3.3 context.md) sebenarnya sudah punya jalur yang tepat**: `persona` (friendly/formal/intimidating) sudah dikirim per-turn dan sudah menggerakkan animasi avatar di frontend. Saya **tidak menduplikasi mekanisme ini** — skenario memengaruhi _tone_ system prompt dan TTS, sementara ekspresi visual tetap mengikuti persona-shift yang sudah berjalan (mekanisme yang sudah ada, dipakai ulang, bukan dibangun ulang).
3. **`app/api/` yang diberikan hanya berisi `websocket.py`.** Frontend memanggil REST endpoint `/api/sessions` (POST, GET), `/api/sessions/:id/report` (GET), dan `/api/profile/:userId` (GET) lewat proxy SvelteKit (`hooks.server.ts` → `/api/proxy/*`). File-file router REST ini **tidak ada dalam bundle `app.zip`** yang diberikan (kemungkinan di `main.py` atau `app/api/routes/` di luar folder yang di-zip). **Saya tidak bisa mengedit apa yang tidak diberikan** — jadi implementasi saya mencakup semua yang bisa dijangkau dari `websocket.py` (yang ternyata menangani sebagian besar logic sesi: `START_INTERVIEW`, `END_SESSION`, dst), dan saya sediakan **snippet siap-tempel** persis untuk endpoint REST yang perlu disentuh (§4.3). Tolong konfirmasi lokasi file itu kalau ingin saya edit langsung.
4. **Bug pra-eksisting (di luar scope APE, dilaporkan saja)**: di `progress/+page.svelte`, array `dimensions` (label) dan array hasil `getDimensionScores()` (nilai) **tidak sejajar urutannya** — index 0 dimensions adalah `'Filler Words'` tapi index 0 scores adalah nilai `communicationScore` (dikomentari "Tutur Kata"). Efeknya, semua 10 dimensi lama di halaman progress menampilkan skor dimensi yang salah (bergeser satu posisi). Dimensi baru saya (`Ketahanan Stres (SRI)`) saya taruh sejajar dengan benar di posisi terakhir (index 10 di kedua array), jadi tidak menambah bug — tapi bug lama ini sebaiknya diperbaiki terpisah.

---

## 2. Daftar File yang Diubah

**Backend (`app/app/`)**

- `models/domain.py` — enum `ScenarioType`; kolom baru di `UserProfile`, `InterviewSession`, `SessionReport`.
- `models/__init__.py` — export `ScenarioType`.
- `services/speech.py` — `generate_speech_with_visemes()` menerima `speed`/`pitch`.
- `services/brain.py` — `SCENARIO_CONFIG`, `PRESSURE_LEVEL_RULES`, `calculate_sri()`, `compute_pressure_level()`, `extract_weakness_tags()`, `get_tts_params()`; `build_system_prompt()` & `generate_next_turn_stream()` menerima `pressure_level`/`weakness_tags`.
- `api/websocket.py` — pakai TTS params dinamis, kirim `weakness_tags` ke prompt, hitung & simpan SRI + weakness tags di `finish_and_report()`.

**Frontend (`src/`)**

- `lib/server/db/schema.ts` — `scenarioEnum`; kolom baru sejajar dengan model Python di atas; perbaikan komentar Kokoro→edge_tts.
- `routes/session/disclaimer/+page.server.ts` — kirim `weaknessTags`, `nextPressureLevel` ke halaman.
- `routes/session/disclaimer/+page.svelte` — **pemilih skenario** (3 kartu), **banner disclaimer** "bukan bank soal", kirim `scenario` di body POST `/api/sessions`.
- `routes/session/results/+page.svelte` — kartu indikator SRI (hijau/kuning/merah).
- `routes/progress/+page.svelte` — dimensi baru "Ketahanan Stres (SRI)" di picker + trend chart.

**Belum disentuh (butuh file yang tidak tersedia)**

- REST handler `POST /api/sessions` — perlu menerima `scenario` dari body dan set `InterviewSession.scenario` + `InterviewSession.pressureLevel = userProfile.nextPressureLevel`. Snippet ada di §4.3.
- REST handler `GET /api/sessions` (dipakai `progress/+page.server.ts`) — perlu ikutkan `sriScore` (join dari `session_report`) di response per-sesi agar chart SRI di halaman progress terisi data asli, bukan fallback.

---

## 3. Migration Script

File terpisah: **`migration_ape.sql`** (SQL manual, idempotent, aman untuk data eksisting —
kolom dibuat lalu di-backfill sebelum di-set `NOT NULL`).

Kalau Anda pakai Drizzle Kit sebagai sumber kebenaran skema:

```bash
cd frontend
bun run db:generate   # akan mendeteksi kolom baru di schema.ts
# bandingkan file migrasi yang digenerate dengan migration_ape.sql,
# lalu:
bun run db:migrate    # atau db:push untuk dev
```

---

## 4. Kode Perubahan (ringkasan diff penting)

### 4.1 `speech.py` — parameter speed/pitch

```python
async def generate_speech_with_visemes(self, text: str, speed: float = 1.0, pitch: float = 1.0):
    rate_str = _to_percent_string(speed)          # 1.15 -> "+15%"
    pitch_hz = round((pitch - 1.0) * 50)
    pitch_str = f"{'+' if pitch_hz >= 0 else ''}{pitch_hz}Hz"
    communicate = edge_tts.Communicate(text, self.voice, rate=rate_str, pitch=pitch_str)
    ...
```

### 4.2 `brain.py` — SRI, pressure level, weakness tags, scenario config

Lihat file lengkap di patch. Poin kunci:

- `calculate_sri(filler_words_per_minute, tempo_bicara, konsistensi_argumen)` — implementasi rumus context.md §3.1 persis, dengan clamping 0-100.
- `compute_pressure_level(sri)` — aturan >70→2, 40-70→1, <40→0, `None`→1 (backward compatible).
- `get_tts_params(scenario, pressure_level)` — mapping context.md §5.1.D, termasuk formula khusus Stress Test: `1.15 + (level * 0.05)`.
- `extract_weakness_tags(transcript_text)` — prompt LLM persis seperti context.md §3.2, dibungkus `response_format=json_object`, fallback `[]` jika LLM gagal.

### 4.3 REST endpoint yang **perlu Anda tambahkan sendiri** (file tidak tersedia di bundle)

Di handler `POST /api/sessions` Anda (kemungkinan `app/api/sessions.py` atau di dalam `main.py`):

```python
from app.models import UserProfile, InterviewSession, ScenarioType
import uuid

@router.post("/api/sessions")
async def create_session(payload: CreateSessionRequest, db: Session = Depends(get_db)):
    user_profile = db.query(UserProfile).filter(UserProfile.userId == payload.userId).first()

    # APE: scenario dari body request, pressureLevel dari profil (hasil sesi sebelumnya)
    scenario = payload.scenario if payload.scenario in ScenarioType.__members__ else ScenarioType.friendly
    pressure_level = (user_profile.nextPressureLevel if user_profile else 1) or 1

    new_session = InterviewSession(
        id=str(uuid.uuid4()),
        userId=payload.userId,
        avatarId=payload.avatarId,
        track=payload.track,
        scenario=scenario,
        pressureLevel=pressure_level,
        # ...field lain yang sudah ada sebelumnya, tidak diubah
    )
    db.add(new_session)
    db.commit()
    return {"id": new_session.id}
```

Dan pastikan `CreateSessionRequest` (Pydantic model) punya field `scenario: str | None = None`.

---

## 5. Instruksi Pengujian Manual

1. **Migrasi**: jalankan `migration_ape.sql` di DB dev, atau `db:generate && db:migrate`. Cek `\d interview_session` di psql — pastikan ada `scenario` (NOT NULL, default `friendly`) dan `pressure_level` (NOT NULL, default `1`).
2. **Pemilihan skenario**: buka `/session/disclaimer?avatarId=...`, pastikan 3 kartu skenario tampil, klik salah satu, cek network tab bahwa POST ke `/api/proxy/api/sessions` membawa `"scenario": "grilling"` (atau sesuai pilihan) di body.
3. **Banner disclaimer**: pastikan teks "Heurix adalah alat latihan ketahanan mental..." tampil di bawah pemilih skenario, sebelum checklist perangkat.
4. **TTS speed berubah**: pilih skenario `stress_test`, mulai sesi, dengarkan apakah suara avatar terdengar lebih cepat dibanding skenario `friendly` pada sesi lain (subjektif tapi cukup untuk verifikasi manual — bedanya defaultnya 1.15x vs 0.95x, seharusnya jelas terdengar).
5. **SRI & weakness tags tersimpan**: selesaikan satu sesi penuh (10 turn) sampai `SESSION_END`. Query manual:
   ```sql
   select last_sri, next_pressure_level, weakness_tags, sri_history from user_profile where user_id = '<id>';
   select sri_score from session_report where session_id = '<id>';
   ```
   Pastikan semuanya terisi (tidak NULL).
6. **Level tekanan sesi berikutnya**: mulai sesi baru untuk user yang sama, cek `select pressure_level, scenario from interview_session order by created_at desc limit 1;` — harus mengikuti `next_pressure_level` dari langkah 5 (asalkan endpoint `POST /api/sessions` sudah dipatch sesuai §4.3).
7. **Halaman hasil**: buka `/session/results?sessionId=...`, pastikan kartu SRI tampil dengan warna sesuai rentang (hijau >70, merah <40, kuning di antaranya).
8. **Halaman progress**: pilih "Ketahanan Stres (SRI)" di dropdown/pill dimension, pastikan trend chart menampilkan data (mungkin datar di 50 sampai endpoint `/api/sessions` diperbarui untuk menyertakan `sriScore`, lihat catatan §2).
9. **Backward compatibility**: pastikan sesi LAMA (dibuat sebelum migrasi) tetap bisa dibuka di halaman results/progress tanpa error — `pressure_level`/`scenario` harus ter-backfill ke `1`/`'friendly'` oleh migration script, dan `sri_score` NULL ditangani UI (`{#if report.sriScore != null}`).

---

## 6. Instruksi Untuk Agen CLI (untuk diterapkan langsung ke source code asli)

Terapkan patch APE (Adaptive Personalization Engine) berikut ke repo Heurix:

1. Ambil isi file-file di `deliverables/patched_files/` (struktur path sudah sama dengan
   repo asli di bawah `backend/app/...` dan `frontend/src/...`) dan timpa file yang sesuai
   di repo asli SATU PER SATU, jangan overwrite folder penuh — bandingkan dulu diff-nya
   dengan `git diff` sebelum commit, karena repo asli mungkin punya perubahan lain sejak
   file ini di-export.

2. Jalankan migrasi database:
   - Jika pakai Drizzle: `cd frontend && bun run db:generate && bun run db:migrate`
   - Verifikasi hasil generate SAMA dengan `deliverables/migration_ape.sql` (khususnya
     urutan ALTER TABLE dan backfill UPDATE sebelum SET NOT NULL). Jika drizzle-kit
     menghasilkan migrasi yang mencoba SET NOT NULL tanpa backfill dulu, edit file
     migrasi hasil generate untuk menyisipkan langkah UPDATE seperti di migration_ape.sql
     SEBELUM baris ALTER COLUMN ... SET NOT NULL, agar tidak gagal pada data eksisting.

3. Cari dan patch REST endpoint pembuatan sesi (biasanya `backend/app/api/sessions.py`
   atau di `backend/main.py` — TIDAK ada di file yang saya terima, jadi CARI dulu dengan
   `grep -rn "api/sessions" backend/` sebelum mengedit). Terapkan snippet di
   AUDIT_AND_IMPLEMENTATION_REPORT.md §4.3: terima field `scenario` dari body request,
   dan set `InterviewSession.pressureLevel` dari `UserProfile.nextPressureLevel` user
   yang bersangkutan (default 1 jika profil belum ada).

4. Cari dan patch REST endpoint listing sesi untuk halaman progress (biasanya
   `GET /api/sessions`) agar setiap sesi di response menyertakan `sriScore` (join dari
   tabel `session_report`), supaya `frontend/src/routes/progress/+page.svelte` bisa
   menampilkan trend SRI dengan data asli, bukan fallback 50.

5. Setelah patch diterapkan:
   - `cd backend && python -m py_compile app/**/*.py` (atau linter yang dipakai) untuk
     memastikan tidak ada syntax error.
   - `cd frontend && bun run check` untuk validasi TypeScript/Svelte.
   - Jalankan backend + frontend secara lokal, lalu jalankan checklist manual di
     AUDIT_AND_IMPLEMENTATION_REPORT.md §5 satu per satu.

6. JANGAN mengubah `Difficulty` enum, `SHIFT_THRESHOLDS`, atau logic persona-shift yang
   sudah ada — APE menambah kolom & parameter baru (`pressureLevel`, `scenario`) yang
   berjalan PARALEL dengan sistem itu, bukan menggantikannya.

7. Setelah semua manual test di §5 lulus, tulis laporan penerapan singkat (mis.
   `deliverables/IMPLEMENTATION_LOG.md`) yang mencatat: file mana saja yang benar-benar diubah di repo
   asli (harus cocok dengan daftar di §2), hasil tiap langkah manual test di §5 (lulus/gagal catatan), dan status migrasi database (sudah dijalankan di environment mana). Simpan
   laporan ini di repo untuk referensi tim — TIDAK perlu membuat commit terpisah, push, atau
   pull request; itu di luar tanggung jawab agen ini.
8. jalankan post implementation protocol pada `AGENTS.md`
