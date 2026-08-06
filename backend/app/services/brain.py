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
    ScenarioType,
    SessionReport
)

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

# ── APE PILAR 3: KONTROL SKENARIO SUASANA ───────────────────────────────────
# Satu sumber kebenaran untuk parameter TTS + instruksi sistem per skenario.
# Dipakai oleh build_system_prompt() (untuk LLM) dan get_tts_params() (untuk TTS).

SCENARIO_CONFIG: dict[ScenarioType, dict] = {
    ScenarioType.friendly: {
        "label": "Friendly HR",
        "tts_speed": 0.95,
        "tts_pitch": 1.05,
        "system_instruction": (
            "Bersikap hangat, beri pujian kecil di sela jawaban, tanyakan dengan nada eksploratif."
        ),
    },
    ScenarioType.grilling: {
        "label": "Grilling BUMN",
        "tts_speed": 1.0,
        "tts_pitch": 0.95,
        "system_instruction": (
            "Bersikap formal, potong jawaban jika terlalu panjang, minta bukti konkret setiap klaim."
        ),
    },
    ScenarioType.stress_test: {
        "label": "Stress Test Akmil",
        "tts_speed": 1.15,
        "tts_pitch": 0.9,
        "system_instruction": (
            "Konfrontasi setiap jawaban ambigu. Lakukan Persona Shift secara mendadak di menit ke-4. "
            "Tekankan integritas dan ketahanan mental."
        ),
    },
}

# ── APE PILAR 1: PROGRESI BEBAN (ADAPTIVE DIFFICULTY SCALING) ──────────────
# Level tekanan (0/1/2) dihitung dari SRI sesi SEBELUMNYA dan disimpan sebagai
# snapshot pada InterviewSession.pressureLevel saat sesi baru dibuat.
# INI TERPISAH dari InterviewSession.difficulty (easy/medium/hard/extreme) yang
# sudah ada sebelumnya — level tekanan memodulasi probing_aggressiveness &
# response_pause di ATAS difficulty dasar tanpa mengubahnya.

PRESSURE_LEVEL_RULES: dict[int, str] = {
    0: "Tekanan RENDAH. Turunkan agresivitas probing, lebih suportif, beri lebih banyak ruang berpikir.",
    1: "Tekanan NORMAL. Probing standar sesuai difficulty sesi.",
    2: "Tekanan TINGGI. Naikkan agresivitas probing satu tingkat, kejar jawaban lebih tajam.",
}

# response_pause dalam detik, dikonsumsi oleh frontend/orkestrasi turn jika diperlukan.
PRESSURE_LEVEL_RESPONSE_PAUSE: dict[int, float] = {
    0: 1.5,
    1: 1.2,
    2: 0.8,
}


def get_tts_params(scenario: ScenarioType | str | None, pressure_level: int | None) -> tuple[float, float]:
    """
    Menggabungkan parameter TTS dari skenario (Pilar 3) dengan penyesuaian
    level tekanan (Pilar 1), sesuai mapping di context.md 5.1.D:
      Friendly: speed 0.95 (tetap)
      Grilling: speed 1.0 (tetap)
      Stress Test: speed 1.15 + (level * 0.05)
    """
    try:
        scenario_enum = ScenarioType(scenario) if scenario else ScenarioType.friendly
    except ValueError:
        scenario_enum = ScenarioType.friendly

    config = SCENARIO_CONFIG[scenario_enum]
    level = pressure_level if pressure_level is not None else 1
    speed = config["tts_speed"]

    if scenario_enum == ScenarioType.stress_test:
        speed = 1.15 + (level * 0.05)

    return speed, config["tts_pitch"]


def calculate_sri(
    filler_words_per_minute: float,
    tempo_bicara: float,
    konsistensi_argumen: float,
) -> float:
    """
    Menghitung Stress Resilience Index (SRI), 0-100, sesuai rumus di context.md 3.1.

    filler_words_per_minute: rata-rata filler words per menit pada sesi.
    tempo_bicara: rata-rata kata per menit (words per minute) pada sesi.
    konsistensi_argumen: skala 0-5 (mis. consistencyScore/100*5 jika sumbernya 0-100).
    """
    filler_component = (1 - min(filler_words_per_minute / 10, 1)) * 0.4
    tempo_component = (1 - min(abs(tempo_bicara - 150) / 100, 1)) * 0.3
    consistency_component = (min(max(konsistensi_argumen, 0), 5) / 5) * 0.3

    sri = (filler_component + tempo_component + consistency_component) * 100
    return round(max(0.0, min(100.0, sri)), 2)


def compute_pressure_level(sri: float | None) -> int:
    """
    Aturan penyesuaian level dari context.md 3.1:
      SRI > 70        -> Level 2 (tekanan lebih tinggi)
      40 <= SRI <= 70 -> Level 1 (normal)
      SRI < 40        -> Level 0 (tekanan lebih rendah)
    Sesi lama / SRI NULL -> Level 1 (backward-compatible default).
    """
    if sri is None:
        return 1
    if sri > 70:
        return 2
    if sri < 40:
        return 0
    return 1


async def extract_weakness_tags(transcript_text: str) -> list[str]:
    """
    APE Pilar 2: mengekstrak 1-3 tag topik/situasi pemicu penurunan kualitas
    jawaban dari transkrip sesi, menggunakan LLM (sesuai prompt di context.md 3.2).
    """
    if not transcript_text.strip():
        return []

    prompt = f"""
Kamu adalah asisten analisis wawancara. Berikut transkrip lengkap satu sesi simulasi wawancara kerja:

{transcript_text}

Identifikasi 1-3 topik atau situasi di mana kandidat menunjukkan penurunan kualitas jawaban terbanyak
(misal: jawaban menjadi ragu-ragu, filler words melonjak, atau tempo melambat).
Berikan dalam format tag pendek (contoh: "kegagalan", "konflik tim", "tekanan waktu").

Balas HANYA dalam format JSON:
{{"tags": ["tag1", "tag2", "tag3"]}}
"""
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=150,
        )
        data = json.loads(response.choices[0].message.content)
        tags = data.get("tags", [])
        # Sanitasi: pastikan list[str], maksimal 3, pendek
        clean_tags = [str(t).strip().lower() for t in tags if str(t).strip()][:3]
        return clean_tags
    except Exception as e:
        print(f"Error in extract_weakness_tags: {e}")
        return []

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

Yang harus kamu lakukan dalam giliran terakhir ini:
1. Periksa isi jawaban kandidat di giliran sebelumnya (fase closing). Jika kandidat mengajukan pertanyaan tentang posisi, institusi, atau proses seleksi:
   - Jika pertanyaan tersebut bisa dijawab wajar berdasarkan konteks institusi/posisi ({institution_name}), jawab secara singkat (1-2 kalimat) dan alami SEBELUM masuk ke kalimat penutup.
   - Jika pertanyaan di luar kewenangan/informasi kamu (misal: nominal gaji spesifik, jadwal internal detail), akui dengan sopan bahwa hal tersebut akan diinfokan lebih lanjut oleh tim rekrutmen. JANGAN mengarang jawaban.
   - Jika kandidat TIDAK mengajukan pertanyaan (misal: menjawab "tidak ada" atau langsung mengucapkan terima kasih), langsung lanjut ke kalimat penutup.
2. Ucapkan apresiasi yang tulus atas waktu dan jawaban kandidat — sebutkan 1-2 hal spesifik yang berkesan.
3. Jelaskan langkah selanjutnya secara singkat (contoh: tim rekrutmen akan menghubungi dalam 3-5 hari kerja).
4. Akhiri dengan salam penutup yang hangat dan profesional sesuai persona kamu.

PENTING: Ini tetap SATU giliran terakhir dan bersifat satu arah. Jawab pertanyaan kandidat (jika ada) dan sampaikan penutup dalam giliran yang sama. DILARANG meminta kandidat menjawab atau bertanya lagi.
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
    pressure_level: int | None = None,
    weakness_tags: list[str] | None = None,
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
  "feedback": "Feedback singkat jawaban sebelumnya (maksimal 1 kalimat pendek). Kosongkan jika ini giliran pertama.",
  "question": "Pertanyaan wawancara berikutnya (maksimal 1-2 kalimat pendek, lugas dan hindari kalimat bertumpuk).",
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
[FEEDBACK] <feedback singkat jawaban sebelumnya (maksimal 1 kalimat pendek). Kosongkan jika ini giliran pertama.>
[QUESTION] <pertanyaan wawancara berikutnya (maksimal 1-2 kalimat pendek). Pastikan pertanyaan ini mengalir alami setelah feedback.>
"""

    # Tentukan fase jika belum diberikan dari luar
    if phase is None:
        phase = get_phase(turn_number, total_turns_target)
    
    # Ambil instruksi fase dan isi variabel dinamis
    phase_instruction = PHASE_INSTRUCTIONS[phase].format(
        avatar_name=avatar.name,
        institution_name=institution.name
    )

    # ── APE Pilar 3: Kontrol SkenARIO SUASANA ───────────────────────────────
    scenario_value = getattr(session, "scenario", None) or ScenarioType.friendly
    scenario_config = SCENARIO_CONFIG.get(ScenarioType(scenario_value), SCENARIO_CONFIG[ScenarioType.friendly])
    scenario_instruction = scenario_config["system_instruction"]
    scenario_label = scenario_config["label"]

    # ── APE Pilar 1: Progresi Beban ─────────────────────────────────────────
    level = pressure_level if pressure_level is not None else getattr(session, "pressureLevel", 1) or 1
    pressure_instruction = PRESSURE_LEVEL_RULES.get(level, PRESSURE_LEVEL_RULES[1])

    # ── APE Pilar 2: Profil Kelemahan Spesifik ──────────────────────────────
    tags = weakness_tags or []
    if tags:
        weakness_instruction = (
            f"Fokuskan eksplorasi pada topik-topik berikut: {', '.join(tags)}. "
            "Gali dari berbagai sudut pandang, tetapi jangan ulangi pertanyaan yang persis sama."
        )
    else:
        weakness_instruction = "Belum ada data kelemahan spesifik dari sesi sebelumnya — eksplorasi bebas sesuai fase."

    return f"""
Kamu adalah {avatar.name}, pewawancara profesional dari {institution.name}.

=== KONTEKS INSTITUSI ===
{institution.llmContext or "Tidak ada konteks khusus."}

=== KONTEKS POSISI: {position.name} ===
{position.llmContext or "Tidak ada konteks khusus."}

=== INSTRUKSI PERSONA: {session.currentPersona.value.upper() if hasattr(session.currentPersona, 'value') else str(session.currentPersona).upper()} ===
{persona_instruction}

=== SKENARIO SUASANA: {scenario_label.upper()} ===
{scenario_instruction}

=== PROGRESI BEBAN (Level Tekanan {level}) ===
{pressure_instruction}

=== PROFIL KELEMAHAN KANDIDAT (Deliberate Practice) ===
{weakness_instruction}

{phase_instruction}

=== ATURAN SESI & GAYA BICARA ===
- Track: {session.track}
- Difficulty: {session.difficulty} — {difficulty_rules}
- Ini adalah giliran ke-{turn_number} dari target {total_turns_target} giliran.
- Persona sudah bergeser {session.personaShiftCount} kali dalam sesi ini.
- Jangan sebut nama platform atau bahwa ini adalah simulasi.
- Ajukan SATU pertanyaan saja per giliran (kecuali fase FAREWELL).
- Bahasa: Indonesia formal, boleh campur istilah teknis Inggris.
- RINGKAS & LUGAS: Berbicaralah seperti pewawancara sungguhan secara lisan. DILARANG membuat tanggapan atau pertanyaan bertele-tele/panjang seperti esai.
- JEDA NAPAS & INTERJEKSI LISAN: Hanya jika kandidat memberikan jawaban nyata (BUKAN "(tidak menjawab)" atau "Kandidat tidak menjawab"), Anda boleh menyisipkan interjeksi singkat. Jika kandidat tidak menjawab, diam, atau di awal sesi (Turn 1/2), DILARANG keras membuka dengan "Baik, oke,", "Terima kasih,", atau tanggapan palsu seolah-olah kandidat baru saja menjawab.
- TANPA MARKUP: DILARANG menggunakan tag HTML, SSML, atau formatting markdown (seperti bold/italic) di dalam text feedback atau question. Output harus teks lisan polos karena akan dibacakan langsung oleh TTS.

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
    weakness_tags: list[str] | None = None,
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
        pressure_level=getattr(session, "pressureLevel", 1),
        weakness_tags=weakness_tags,
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
