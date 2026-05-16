import json
from enum import Enum
from groq import AsyncGroq
from app.core.config import settings
from app.models import (
    MasterInstitution,
    MasterPosition,
    InterviewAvatar,
    InterviewSession,
    SessionTurn,
    PersonaType,
    Difficulty,
    SessionReport
)

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

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
      Turn 2-4     → WARMUP   (pertanyaan ringan: background, motivasi)
      Turn 5-8     → CORE     (pertanyaan inti sesuai posisi & difficulty)
      Turn 9       → CLOSING  (beri ruang kandidat, pertanyaan penutup)
      Turn 10+     → FAREWELL (ucapan penutup, tidak butuh jawaban)
    """
    if turn_number <= 0:
        return InterviewPhase.opening

    # Sesi sangat pendek (< 5 turn)
    if total_turns < 5:
        if turn_number == 1:
            return InterviewPhase.opening
        elif turn_number >= total_turns:
            return InterviewPhase.farewell
        else:
            return InterviewPhase.core

    # Sesi normal (≥ 5 turn)
    if turn_number == 1:
        return InterviewPhase.opening
    elif turn_number <= max(2, int(total_turns * 0.4)): # Perpanjang warmup
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
1. Sapa kandidat dengan sangat hangat.
2. Perkenalkan diri kamu (sebutkan nama kamu: {avatar_name}) sebagai pewawancara dari {institution_name}.
3. Jelaskan bahwa hari ini kita akan berdiskusi santai untuk mengenal satu sama lain.
4. Tutup dengan SATU pertanyaan pembuka ringan (ice-breaking), contoh: "Bagaimana kabar Anda hari ini?" atau "Apakah Anda sudah siap untuk memulai?"

PENTING: Jangan bertanya tentang background atau motivasi dulu. Fokus pada perkenalan dan kenyamanan.
""",

    InterviewPhase.warmup: """
=== FASE SAAT INI: PEMANASAN (Warm-up) ===
Fokus pada pengenalan latar belakang dan motivasi kandidat. Belum ke pertanyaan teknikal berat.

Contoh pertanyaan yang wajib diajukan di fase ini (satu per turn):
- "Boleh Anda ceritakan sedikit tentang diri Anda dan perjalanan karir Anda sejauh ini?"
- "Apa yang membuat Anda tertarik melamar posisi ini di institusi kami?"
- "Apa yang Anda ketahui tentang institusi dan posisi yang Anda lamar?"

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

async def summarize_interview(
    session: InterviewSession,
    institution: MasterInstitution,
    position: MasterPosition,
    turns: list[SessionTurn]
) -> dict:
    """
    Menganalisis seluruh sesi wawancara dan memberikan skor serta narasi evaluasi.
    """
    history_text = ""
    for turn in turns:
        history_text += f"Pertanyaan {turn.turnNumber}: {turn.questionText}\n"
        history_text += f"Jawaban: {turn.answerTranscript or '(Tidak menjawab)'}\n"
        history_text += f"Skor Kualitas: {turn.answerQuality or 0}\n\n"

    system_prompt = f"""
Kamu adalah AI Pakar Rekrutmen dan Psikolog Industri.
Tugas kamu adalah mengevaluasi hasil simulasi wawancara kerja berikut.

=== KONTEKS ===
Institusi: {institution.name}
Posisi: {position.name}
Tingkat Kesulitan: {session.difficulty}

=== DATA WAWANCARA ===
{history_text}

=== INSTRUKSI EVALUASI ===
1. Berikan skor 0-100 dan feedback singkat (1 kalimat) untuk 8 Dimensi Komunikasi:
   - articulation: Kejelasan, artikulasi, dan kemudahan dipahami.
   - intonation: Variasi nada suara dan ekspresi verbal.
   - pacing: Kecepatan bicara (ideal 130-150 kata/menit).
   - filler_words: Penggunaan kata pengisi (ee, ehm, dll).
   - sentence_structure: Struktur kalimat dan penggunaan kosa kata industri.
   - answer_completeness: Kelengkapan jawaban menggunakan metode STAR.
   - consistency: Keselarasan jawaban dari awal hingga akhir.
   - confidence: Keyakinan dalam menjawab.

2. Hitung overall_score sebagai rata-rata tertimbang.
3. Berikan strengths (minimal 3 poin) dan weaknesses (minimal 3 poin).
4. Berikan recommendations untuk perbaikan ke depannya.
5. Berikan evaluation_narrative singkat (2-3 paragraf).
6. Untuk setiap pertanyaan, berikan analisis singkat berupa "strength" (poin positif) dan "improvement" (area perbaikan).

=== FORMAT OUTPUT ===
Wajib JSON:
{{
  "overall_score": <angka>,
  "dimensions": {{
    "articulation": {{ "score": <angka>, "feedback": "..." }},
    "intonation": {{ "score": <angka>, "feedback": "..." }},
    "pacing": {{ "score": <angka>, "feedback": "..." }},
    "filler_words": {{ "score": <angka>, "feedback": "..." }},
    "sentence_structure": {{ "score": <angka>, "feedback": "..." }},
    "answer_completeness": {{ "score": <angka>, "feedback": "..." }},
    "consistency": {{ "score": <angka>, "feedback": "..." }},
    "confidence": {{ "score": <angka>, "feedback": "..." }}
  }},
  "strengths": ["...", "...", "..."],
  "weaknesses": ["...", "...", "..."],
  "recommendations": ["...", "..."],
  "evaluation_narrative": "...",
  "question_analysis": [
    {{
      "turn_number": 1,
      "strength": "...",
      "improvement": "..."
    }},
    ...
  ]
}}
"""

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"},
            max_tokens=3000,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error in Summarization: {e}")
        # Return fallback data
        avg_quality = sum([t.answerQuality or 0 for t in turns]) / len(turns) if turns else 50
        return {
            "overall_score": avg_quality,
            "dimensions": {
                "articulation": { "score": avg_quality, "feedback": "Artikulasi cukup jelas." },
                "intonation": { "score": avg_quality, "feedback": "Intonasi cukup baik." },
                "pacing": { "score": avg_quality, "feedback": "Kecepatan bicara stabil." },
                "filler_words": { "score": avg_quality, "feedback": "Penggunaan filler words minim." },
                "sentence_structure": { "score": avg_quality, "feedback": "Struktur kalimat mudah dipahami." },
                "answer_completeness": { "score": avg_quality, "feedback": "Jawaban cukup lengkap." },
                "consistency": { "score": avg_quality, "feedback": "Jawaban konsisten." },
                "confidence": { "score": avg_quality, "feedback": "Terlihat percaya diri." }
            },
            "strengths": ["Mampu mengikuti alur wawancara"],
            "weaknesses": ["Perlu analisis lebih mendalam"],
            "recommendations": ["Berlatih lebih sering"],
            "evaluation_narrative": "Evaluasi otomatis gagal dihasilkan karena kendala teknis.",
            "question_analysis": []
        }

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
    persona_map = {
        PersonaType.friendly: avatar.promptFriendly,
        PersonaType.formal: avatar.promptFormal,
        PersonaType.intimidating: avatar.promptIntimidating,
    }
    persona_instruction = persona_map.get(session.currentPersona, avatar.promptFormal)

    difficulty_rules = {
        Difficulty.easy: "Ajukan pertanyaan ringan. Tidak ada tekanan.",
        Difficulty.medium: "Gunakan pertanyaan STAR standar. Boleh probing satu level.",
        Difficulty.hard: "Probing mendalam. Tekan inkonsistensi jawaban.",
        Difficulty.extreme: "Simulasikan panel wawancara. Pertanyaan teknikal dan stress test.",
    }.get(session.difficulty, "")

    format_instruction = """
=== FORMAT OUTPUT ===
Selalu balas dalam format JSON berikut:
{
  "feedback": "Feedback singkat jawaban sebelumnya (1-2 kalimat). Kosongkan jika ini giliran pertama.",
  "question": "Pertanyaan wawancara berikutnya.",
  "persona_assessment": "friendly | formal | intimidating — penilaian kamu atas jawaban kandidat untuk keperluan sistem.",
  "answer_quality_score": <angka 0-100>
}
"""

    if is_streaming:
        format_instruction = """
=== FORMAT OUTPUT ===
Wajib mengikuti format tag berikut untuk mendukung streaming:
[SCORE] <angka 0-100>
[ASSESSMENT] <friendly | formal | intimidating>
[FEEDBACK] <feedback singkat jawaban sebelumnya (1-2 kalimat). Kosongkan jika ini giliran pertama.>
[QUESTION] <pertanyaan wawancara berikutnya. Pastikan pertanyaan ini mengalir alami setelah feedback.>
"""

    # Tentukan fase jika belum diberikan dari luar
    if phase is None:
        phase = get_phase(turn_number, total_turns_target)
    
    # Ambil instruksi fase dan isi variabel dinamis
    phase_instruction = PHASE_INSTRUCTIONS[phase].format(
        avatar_name=avatar.name,
        institution_name=institution.name
    )

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
    """
    Menghasilkan stream token dari Groq.
    """
    turn_number = len(past_turns) + (1 if new_answer_transcript else 0) + 1
    
    system_prompt = build_system_prompt(
        institution=institution,
        position=position,
        avatar=avatar,
        session=session,
        turn_number=turn_number,
        is_streaming=True,
        phase=phase_override,
    )

    messages = build_chat_history(past_turns)
    if current_question:
        messages.append({"role": "assistant", "content": current_question})
    if new_answer_transcript:
        messages.append({"role": "user", "content": new_answer_transcript})
    if not messages:
        messages.append({
            "role": "user",
            "content": "[SISTEM: Kandidat telah hadir dan siap memulai. Mulailah sesi sesuai fase PEMBUKA — sambut kandidat, perkenalkan diri, dan ajukan pertanyaan pembuka ringan.]"
        })

    return await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        stream=True,
        max_tokens=256,
    )

def build_chat_history(
    turns: list[SessionTurn],
    max_turns: int = 8,
) -> list[dict]:
    """
    Konversi sessionTurn[] dari DB ke format messages[] OpenAI/Groq.
    Ambil max_turns terakhir untuk menghindari context overflow.
    Urutan: assistant (pertanyaan) → user (jawaban) → dst.
    """
    recent_turns = turns[-max_turns:] if len(turns) > max_turns else turns
    messages = []
    for turn in recent_turns:
        messages.append({
            "role": "assistant",
            "content": turn.questionText,
        })
        if turn.answerTranscript:
            messages.append({
                "role": "user",
                "content": turn.answerTranscript,
            })
    return messages

async def generate_next_turn(
    session: InterviewSession,
    institution: MasterInstitution,
    position: MasterPosition,
    avatar: InterviewAvatar,
    past_turns: list[SessionTurn],
    new_answer_transcript: str | None = None,
    current_question: str | None = None,
) -> dict:
    """
    Menghasilkan pertanyaan berikutnya dari LLM berdasarkan full context.
    Mengembalikan dict hasil parse dari JSON output LLM.
    """
    # Turn number adalah jumlah turn sebelumnya + turn yang baru saja dijawab (jika ada) + 1
    # Jika new_answer_transcript ada, berarti kita sedang mencari pertanyaan untuk turn berikutnya
    turn_number = len(past_turns) + (1 if new_answer_transcript else 0) + 1
    
    system_prompt = build_system_prompt(
        institution=institution,
        position=position,
        avatar=avatar,
        session=session,
        turn_number=turn_number,
    )

    # Build history dari turn yang sudah ada (turn-turn lama)
    messages = build_chat_history(past_turns)

    # Jika ada pertanyaan turn saat ini, tambahkan
    if current_question:
        messages.append({"role": "assistant", "content": current_question})

    # Tambahkan jawaban baru jika ada (bukan giliran pertama)
    if new_answer_transcript:
        messages.append({"role": "user", "content": new_answer_transcript})

    # Jika messages masih kosong (giliran pertama sekali), tambahkan trigger
    if not messages:
        messages.append({
            "role": "user",
            "content": "[SISTEM: Kandidat telah hadir dan siap memulai. Mulailah sesi sesuai fase PEMBUKA — sambut kandidat, perkenalkan diri, dan ajukan pertanyaan pembuka ringan.]"
        })

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        print(f"Error in LLM call: {e}")
        return {
            "feedback": "Koneksi terganggu sejenak.",
            "question": "Bisa tolong ulangi atau lanjutkan penjelasan kamu?",
            "persona_assessment": str(session.currentPersona),
            "answer_quality_score": 50
        }

PERSONA_PROGRESSION = [PersonaType.friendly, PersonaType.formal, PersonaType.intimidating]

SHIFT_THRESHOLDS = {
    Difficulty.easy:    {"shift_score": 30, "max_shifts": 1},
    Difficulty.medium:  {"shift_score": 45, "max_shifts": 2},
    Difficulty.hard:    {"shift_score": 55, "max_shifts": 3},
    Difficulty.extreme: {"shift_score": 60, "max_shifts": 3},
}

def should_shift_persona(
    session: InterviewSession,
    answer_quality_score: float,
) -> PersonaType | None:
    """
    Mengembalikan persona baru jika harus shift, None jika tidak.
    """
    config = SHIFT_THRESHOLDS.get(session.difficulty, SHIFT_THRESHOLDS[Difficulty.medium])

    if session.personaShiftCount >= config["max_shifts"]:
        return None  # Sudah mencapai batas shift

    if answer_quality_score < config["shift_score"]:
        current_persona = session.currentPersona
        try:
            current_idx = PERSONA_PROGRESSION.index(current_persona)
            next_idx = min(current_idx + 1, len(PERSONA_PROGRESSION) - 1)

            if next_idx != current_idx:
                return PERSONA_PROGRESSION[next_idx]
        except ValueError:
            return PersonaType.formal

    return None
