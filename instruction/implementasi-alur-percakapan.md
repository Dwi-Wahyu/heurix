# Agent Instruction — Implementasi Alur Percakapan Interview (Fase Pembuka & Penutup)

> Instruksi ini ditujukan untuk AI coding agent (Claude Code, Cursor, dll).
> Baca seluruh instruksi sebelum menyentuh satu baris kode pun.
> Jangan modifikasi file selain yang disebutkan secara eksplisit.

---

## Konteks masalah

Aplikasi ini adalah simulator wawancara kerja berbasis AI dengan avatar 3D. Backend Python (FastAPI) berkomunikasi dengan frontend Svelte via WebSocket. LLM (Groq/Llama) menghasilkan pertanyaan wawancara per giliran (turn).

**Masalah saat ini:** Setiap turn diperlakukan sama oleh LLM — tidak ada fase pembuka (small talk) dan tidak ada fase penutup. Interview langsung masuk ke pertanyaan substantif sejak turn pertama dan berakhir tiba-tiba tanpa ucapan penutup.

**Solusi:** Menambahkan sistem `InterviewPhase` ke dalam system prompt LLM berdasarkan nomor turn. Tidak ada perubahan database, WebSocket protocol, atau frontend.

---

## Scope perubahan — hanya 2 file

```
app/
└── services/
│   └── brain.py        ← MODIFIKASI UTAMA
└── api/
    └── websocket.py    ← MODIFIKASI MINOR (2 bagian kecil)
```

Semua file lain: **JANGAN disentuh.**

---

## File 1: `app/services/brain.py`

### 1a. Tambahkan import `Enum` dari stdlib di bagian paling atas

Cari baris import pertama di file. Pastikan baris berikut ada — jika belum ada, tambahkan:

```python
from enum import Enum
```

Letakkan tepat setelah import stdlib lainnya, sebelum import dari `groq` atau `app.*`.

---

### 1b. Tambahkan class `InterviewPhase`, fungsi `get_phase()`, dan dict `PHASE_INSTRUCTIONS`

Letakkan blok kode ini **setelah** baris `client = AsyncGroq(api_key=settings.GROQ_API_KEY)` dan **sebelum** fungsi `summarize_interview()`. Sisipkan tepat di antara keduanya tanpa mengubah apapun di sekitarnya.

```python
# ── INTERVIEW PHASE SYSTEM ──────────────────────────────────────────────────

class InterviewPhase(str, Enum):
    opening  = "opening"
    warmup   = "warmup"
    core     = "core"
    closing  = "closing"
    farewell = "farewell"


def get_phase(turn_number: int, total_turns: int = 10) -> InterviewPhase:
    """
    Menentukan fase interview berdasarkan nomor giliran saat ini.

    Pembagian fase untuk sesi 10 turn (default):
      Turn 1       → OPENING  (sambut, perkenalan, cairkan suasana)
      Turn 2-3     → WARMUP   (pertanyaan ringan: background, motivasi)
      Turn 4-8     → CORE     (pertanyaan inti sesuai posisi & difficulty)
      Turn 9       → CLOSING  (beri ruang kandidat, pertanyaan penutup)
      Turn 10+     → FAREWELL (ucapan penutup, tidak butuh jawaban)

    Skema ini proporsional terhadap total_turns. Jika total_turns < 4,
    maka WARMUP dilewati dan CORE dimulai dari turn 2.
    """
    if turn_number <= 0:
        return InterviewPhase.opening

    if total_turns < 4:
        # Sesi sangat pendek: opening → core → farewell
        if turn_number == 1:
            return InterviewPhase.opening
        elif turn_number >= total_turns:
            return InterviewPhase.farewell
        else:
            return InterviewPhase.core

    # Sesi normal (≥ 4 turn)
    if turn_number == 1:
        return InterviewPhase.opening
    elif turn_number <= max(2, int(total_turns * 0.25)):
        return InterviewPhase.warmup
    elif turn_number >= total_turns:
        return InterviewPhase.farewell
    elif turn_number >= total_turns - 1:
        return InterviewPhase.closing
    else:
        return InterviewPhase.core


PHASE_INSTRUCTIONS: dict[InterviewPhase, str] = {

    InterviewPhase.opening: """
=== FASE SAAT INI: PEMBUKA (Opening) ===
Ini adalah giliran PERTAMA sesi. DILARANG langsung mengajukan pertanyaan kompetensi atau pengalaman kerja.

Yang harus kamu lakukan dalam satu giliran ini:
1. Sapa kandidat dengan hangat sesuai persona kamu (friendly/formal/intimidating).
2. Perkenalkan diri kamu (nama) dan institusi secara singkat — 1-2 kalimat saja.
3. Sebutkan gambaran umum sesi: "Kita akan berdiskusi sebentar dalam beberapa pertanyaan."
4. Tutup dengan SATU pertanyaan basa-basi ringan, pilih salah satu yang paling natural:
   - "Bagaimana kabar Anda hari ini?"
   - "Apakah Anda sudah siap untuk memulai?"
   - "Sudah berapa lama Anda mempersiapkan diri untuk sesi ini?"

PENTING: Tone harus hangat dan menyambut. Tujuannya membuat kandidat merasa nyaman, bukan menguji.
""",

    InterviewPhase.warmup: """
=== FASE SAAT INI: PEMANASAN (Warm-up) ===
Kandidat sudah sedikit hangat. Arahkan percakapan ke topik profesional secara bertahap — BELUM ke pertanyaan teknikal berat.

Contoh pertanyaan yang sesuai untuk fase ini:
- "Boleh Anda ceritakan sedikit tentang diri Anda dan perjalanan karir Anda sejauh ini?"
- "Apa yang membuat Anda tertarik melamar posisi ini di institusi kami?"
- "Apa yang Anda ketahui tentang institusi dan posisi yang Anda lamar?"
- "Bagaimana Anda menggambarkan kekuatan terbesar Anda?"

Hindari pertanyaan stress test, teknikal mendalam, atau skenario konflik di fase ini.
Gunakan feedback dari jawaban sebelumnya untuk membuat transisi terasa natural.
""",

    InterviewPhase.core: """
=== FASE SAAT INI: INTI WAWANCARA (Core) ===
Ini adalah inti sesi. Ajukan pertanyaan substantif yang relevan dengan posisi dan tingkat kesulitan yang sudah ditentukan.

Panduan:
- Gunakan metode STAR (Situation, Task, Action, Result) jika relevan.
- Lakukan probing satu level lebih dalam jika jawaban kandidat terlalu umum.
- Variasikan jenis pertanyaan: behavioral, situational, dan technical sesuai posisi.
- Persona shift (jika ada) diterapkan di fase ini, bukan di fase lain.
- Selalu berikan feedback singkat atas jawaban sebelumnya sebelum bertanya lagi.
""",

    InterviewPhase.closing: """
=== FASE SAAT INI: PENUTUP (Closing) ===
Sesi hampir selesai. Tone harus lebih santai — ini bukan saatnya menekan kandidat.

Ajukan pertanyaan penutup yang memberi ruang kepada kandidat, contoh:
- "Apakah ada hal penting tentang diri Anda yang belum sempat Anda sampaikan?"
- "Apakah ada pertanyaan yang ingin Anda ajukan kepada kami tentang posisi atau institusi ini?"
- "Bagaimana Anda membayangkan kontribusi Anda dalam posisi ini 6 bulan pertama?"
- "Apa harapan Anda jika bergabung dengan tim kami?"

Apresiasi perjalanan diskusi sebelum mengajukan pertanyaan penutup.
""",

    InterviewPhase.farewell: """
=== FASE SAAT INI: PENUTUPAN SESI (Farewell) ===
Ini adalah giliran TERAKHIR sesi. DILARANG mengajukan pertanyaan baru apapun.

Yang harus kamu lakukan:
1. Ucapkan apresiasi yang tulus atas waktu dan jawaban kandidat — sebutkan 1-2 hal spesifik yang berkesan.
2. Jelaskan langkah selanjutnya secara singkat, contoh:
   - "Kami akan meninjau hasil diskusi ini dan menghubungi Anda dalam 3-5 hari kerja."
   - "Tim rekrutmen kami akan menghubungi Anda segera untuk informasi lebih lanjut."
3. Akhiri dengan salam penutup yang hangat dan profesional sesuai persona kamu.

PENTING: Jangan meminta kandidat menjawab apapun. Ini adalah ucapan penutup satu arah.
""",

}

# ── END INTERVIEW PHASE SYSTEM ───────────────────────────────────────────────
```

---

### 1c. Modifikasi fungsi `build_system_prompt()`

Fungsi `build_system_prompt()` sudah ada di file. Lakukan dua hal:

**Pertama**, tambahkan parameter `phase` ke signature fungsi. Ubah baris definisi fungsi dari:

```python
def build_system_prompt(
    institution: MasterInstitution,
    position: MasterPosition,
    avatar: InterviewAvatar,
    session: InterviewSession,
    turn_number: int,
    total_turns_target: int = 10,
    is_streaming: bool = False,
) -> str:
```

Menjadi:

```python
def build_system_prompt(
    institution: MasterInstitution,
    position: MasterPosition,
    avatar: InterviewAvatar,
    session: InterviewSession,
    turn_number: int,
    total_turns_target: int = 10,
    is_streaming: bool = False,
    phase: InterviewPhase | None = None,
) -> str:
```

**Kedua**, di dalam body fungsi `build_system_prompt()`, cari baris `return f"""` yang memulai string return utama. Tepat sebelum baris tersebut, sisipkan dua baris ini:

```python
    # Tentukan fase jika belum diberikan dari luar
    if phase is None:
        phase = get_phase(turn_number, total_turns_target)
    phase_instruction = PHASE_INSTRUCTIONS[phase]
```

**Ketiga**, di dalam f-string return, cari blok `=== ATURAN SESI ===`. Sisipkan `{phase_instruction}` tepat **sebelum** blok tersebut:

```python
    return f"""
Kamu adalah {avatar.name}, pewawancara profesional dari {institution.name}.

=== KONTEKS INSTITUSI ===
{institution.llmContext or "Tidak ada konteks khusus."}

=== KONTEKS POSISI: {position.name} ===
{position.llmContext or "Tidak ada konteks khusus."}

=== INSTRUKSI PERSONA: {session.currentPersona.value.upper() if hasattr(session.currentPersona, 'value') else str(session.currentPersona).upper()} ===
{persona_instruction}

{phase_instruction}

=== ATURAN SESI ===
- Track: {session.track}
- Difficulty: {session.difficulty} — {difficulty_rules}
- Ini adalah giliran ke-{turn_number} dari target {total_turns_target} giliran.
- Persona sudah bergeser {session.personaShiftCount} kali dalam sesi ini.
- Jangan sebut nama platform atau bahwa ini adalah simulasi.
- Ajukan SATU pertanyaan saja per giliran (kecuali fase FAREWELL).
- Bahasa: Indonesia formal, boleh campur istilah teknis Inggris.

{format_instruction}
""".strip()
```

> **Catatan penting:** Pastikan `{phase_instruction}` diletakkan di antara blok `=== INSTRUKSI PERSONA ===` dan `=== ATURAN SESI ===`. Jangan ubah urutan blok lain.

---

## File 2: `app/api/websocket.py`

### 2a. Ganti trigger message turn pertama

Di dalam fungsi `generate_next_turn_stream()` di `brain.py`, dan juga di fungsi `generate_next_turn()` di `brain.py`, cari blok berikut (muncul dua kali — ganti keduanya):

```python
    if not messages:
        messages.append({
            "role": "user",
            "content": "Halo, saya siap memulai sesi wawancara. Silakan mulai dengan menyapa saya dan ajukan pertanyaan pertama."
        })
```

Ganti **keduanya** menjadi:

```python
    if not messages:
        messages.append({
            "role": "user",
            "content": "[SISTEM: Kandidat telah hadir dan siap memulai. Mulailah sesi sesuai fase PEMBUKA — sambut kandidat, perkenalkan diri, dan ajukan pertanyaan pembuka ringan.]"
        })
```

> Blok ini ada di dua fungsi berbeda: `generate_next_turn_stream()` dan `generate_next_turn()`. Ganti keduanya.

---

### 2b. Tambahkan fase farewell sebelum menutup sesi di `websocket.py`

Di dalam fungsi `handle_user_answer()` di file `websocket.py`, cari blok berikut:

```python
    # Limit to 10 questions
    if question_count >= 10:
        await finish_and_report(websocket, db, session)
```

Ganti seluruh blok `if question_count >= 10:` tersebut menjadi:

```python
    # Limit to 10 questions
    if question_count >= 10:
        # Generate ucapan penutup (farewell) dulu sebelum menutup sesi
        # Agar kandidat mendapat closing statement yang proper, bukan langsung redirect
        from app.services.brain import InterviewPhase
        await send_next_question_stream(
            websocket=websocket,
            db=db,
            session=session,
            turn_num=question_count + 1,
            user_transcript=transcript,
            current_question=current_turn_obj.questionText if current_turn_obj else None,
            phase_override=InterviewPhase.farewell,
        )
        await finish_and_report(websocket, db, session)
```

---

### 2c. Tambahkan parameter `phase_override` ke `send_next_question_stream()`

Fungsi `send_next_question_stream()` di `websocket.py` perlu menerima parameter opsional `phase_override`. Ubah signature-nya dari:

```python
async def send_next_question_stream(websocket: WebSocket, db: Session, session: InterviewSession, turn_num: int, user_transcript: str | None = None, current_question: str | None = None):
```

Menjadi:

```python
async def send_next_question_stream(websocket: WebSocket, db: Session, session: InterviewSession, turn_num: int, user_transcript: str | None = None, current_question: str | None = None, phase_override=None):
```

Lalu di dalam body `send_next_question_stream()`, cari baris pemanggilan `generate_next_turn_stream()`:

```python
    stream = await generate_next_turn_stream(
        session=session,
        institution=institution,
        position=position,
        avatar=avatar,
        past_turns=past_turns,
        new_answer_transcript=user_transcript,
        current_question=current_question
    )
```

Ganti menjadi:

```python
    stream = await generate_next_turn_stream(
        session=session,
        institution=institution,
        position=position,
        avatar=avatar,
        past_turns=past_turns,
        new_answer_transcript=user_transcript,
        current_question=current_question,
        phase_override=phase_override,
    )
```

---

### 2d. Tambahkan parameter `phase_override` ke `generate_next_turn_stream()` di `brain.py`

Fungsi `generate_next_turn_stream()` perlu menerima dan meneruskan `phase_override` ke `build_system_prompt()`. Ubah signature-nya dari:

```python
async def generate_next_turn_stream(
    session: InterviewSession,
    institution: MasterInstitution,
    position: MasterPosition,
    avatar: InterviewAvatar,
    past_turns: list[SessionTurn],
    new_answer_transcript: str | None = None,
    current_question: str | None = None,
):
```

Menjadi:

```python
async def generate_next_turn_stream(
    session: InterviewSession,
    institution: MasterInstitution,
    position: MasterPosition,
    avatar: InterviewAvatar,
    past_turns: list[SessionTurn],
    new_answer_transcript: str | None = None,
    current_question: str | None = None,
    phase_override: InterviewPhase | None = None,
):
```

Lalu di dalam body-nya, cari pemanggilan `build_system_prompt()`:

```python
    system_prompt = build_system_prompt(
        institution=institution,
        position=position,
        avatar=avatar,
        session=session,
        turn_number=turn_number,
        is_streaming=True
    )
```

Ganti menjadi:

```python
    system_prompt = build_system_prompt(
        institution=institution,
        position=position,
        avatar=avatar,
        session=session,
        turn_number=turn_number,
        is_streaming=True,
        phase=phase_override,
    )
```

---

## Urutan eksekusi — kerjakan dalam urutan ini

1. Edit `app/services/brain.py`:
   - [ ] Pastikan `from enum import Enum` ada di bagian import
   - [ ] Sisipkan blok `InterviewPhase`, `get_phase()`, `PHASE_INSTRUCTIONS` setelah `client = AsyncGroq(...)`
   - [ ] Tambah parameter `phase` ke signature `build_system_prompt()`
   - [ ] Sisipkan dua baris `phase = get_phase(...)` dan `phase_instruction = ...` sebelum `return f"""`
   - [ ] Sisipkan `{phase_instruction}` di f-string antara blok PERSONA dan ATURAN SESI
   - [ ] Tambah parameter `phase_override` ke signature `generate_next_turn_stream()`
   - [ ] Teruskan `phase=phase_override` ke pemanggilan `build_system_prompt()` di dalam `generate_next_turn_stream()`
   - [ ] Ganti trigger message `if not messages:` di `generate_next_turn_stream()` (lihat 2a)
   - [ ] Ganti trigger message `if not messages:` di `generate_next_turn()` (lihat 2a)

2. Edit `app/api/websocket.py`:
   - [ ] Tambah parameter `phase_override=None` ke signature `send_next_question_stream()`
   - [ ] Teruskan `phase_override=phase_override` ke pemanggilan `generate_next_turn_stream()`
   - [ ] Ganti blok `if question_count >= 10:` di `handle_user_answer()` (lihat 2b)

---

## Yang TIDAK boleh diubah

- Skema database (`app/models/domain.py`) — tidak ada kolom baru
- WebSocket message types di frontend (`session/interview/+page.svelte`) — tidak ada perubahan
- Protocol WebSocket (`START_INTERVIEW`, `END_SESSION`, `QUESTION_CHUNK`, dst) — tidak ada perubahan
- Logika persona shift (`should_shift_persona()`) — tidak ada perubahan
- Fungsi `summarize_interview()` — tidak ada perubahan
- Seluruh file frontend Svelte — tidak ada perubahan

---

## Verifikasi setelah implementasi

Jalankan server dan uji sesi baru. Pastikan:

- [ ] Turn 1: Avatar menyapa, memperkenalkan diri, mengajukan pertanyaan ringan (bukan pertanyaan STAR atau teknikal)
- [ ] Turn 2-3: Avatar mengajukan pertanyaan tentang background atau motivasi kandidat
- [ ] Turn 4-8: Avatar mengajukan pertanyaan substantif sesuai posisi dan difficulty
- [ ] Turn 9: Avatar memberikan ruang kepada kandidat sebelum menutup
- [ ] Turn 10: Avatar mengucapkan penutup tanpa mengajukan pertanyaan baru, lalu aplikasi redirect ke halaman results
- [ ] Semua turn masih menghasilkan audio via `speech_service` seperti sebelumnya
- [ ] Persona shift (friendly → formal → intimidating) masih berjalan normal di turn core
- [ ] Tidak ada error import di `brain.py` maupun `websocket.py`

---

## Catatan tambahan untuk agent

- `InterviewPhase` adalah `str, Enum` — kompatibel langsung sebagai string di f-string Python, tidak perlu `.value`
- `PHASE_INSTRUCTIONS` menggunakan key bertipe `InterviewPhase`, bukan string — pastikan lookup menggunakan instance enum, bukan string literal
- `phase_override=None` berarti jika tidak diisi, `build_system_prompt()` akan menghitung fase otomatis via `get_phase()` — ini adalah perilaku default yang benar untuk semua turn normal
- Farewell phase hanya di-override secara eksplisit dari `handle_user_answer()` saat `question_count >= 10`, bukan dari logika lain
