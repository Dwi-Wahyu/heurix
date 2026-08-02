# Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru

## ⚠️ HARD CONSTRAINT — BACA SEBELUM MENGERJAKAN APA PUN

Model ini bekerja dengan **voice cloning zero-shot**: 1 klip audio referensi + transkripnya menentukan suara siapa yang akan meniru mengucapkan teks apa pun yang di-generate LLM. Ini **BUKAN** "speech-to-speech" translasi/konversi gaya — istilah yang tepat adalah **reference-conditioned TTS / voice cloning TTS**.

- **JANGAN PERNAH** mengunduh atau mereferensikan `ref_prabowo.mp3`, `ref_windah.mp3`, atau `ref_reporter.mp3` dari halaman dokumentasi HuggingFace model ini sebagai audio referensi produksi. File-file itu adalah rekaman figur publik yang bisa diidentifikasi (bukan aktor suara generik) — memakainya untuk menghasilkan ucapan bebas di aplikasi = voice cloning/impersonasi orang nyata tanpa consent, dan bertentangan dengan lisensi CC-BY-NC model ini sendiri.
- Semua path audio referensi dalam task ini **wajib** berupa placeholder yang diisi manual oleh pemilik project dengan rekaman miliknya sendiri (rekaman sendiri, VO talent berizin, atau voice bank berlisensi). Jangan hardcode nama file dari demo di atas di mana pun dalam kode.
- Tambahkan guard sederhana (lihat Task 5) yang menolak konfigurasi jika nama file referensi mengandung token mencurigakan (`prabowo`, `windah`, `reporter`) sebagai pengaman tambahan terhadap kesalahan copy-paste.

Jika constraint ini dilanggar di titik mana pun, STOP dan laporkan ke user — jangan lanjutkan implementasi.

---

## 1. Executive Summary

Backend `backend/` (FastAPI, project **HireReady/Heurix**) saat ini punya satu `SpeechService` (`app/services/speech.py`) yang membungkus `edge_tts` (cloud TTS Microsoft, stateless, tanpa voice cloning). Tugas ini menambahkan **engine TTS kedua** berbasis `F5-TTS-INDO-FINETUNE-V2` (voice cloning, self-hosted, model lokal 1.35 GB) sebagai opsi **per-avatar**, tanpa merusak jalur `edge_tts` yang sudah berjalan (dipakai sebagai fallback).

Prinsip desain:

1. `edge_tts` tetap default & fallback — jangan dihapus.
2. F5-TTS diaktifkan **per avatar** lewat kolom baru di `interview_avatar`, bukan global switch.
3. Model F5-TTS di-load **sekali** saat startup (bukan per-request) — krusial karena checkpoint 1.35 GB dan inference-nya berat di CPU.
4. Kalau F5-TTS gagal load / gagal infer saat runtime → fallback otomatis ke `edge_tts` + log warning, jangan sampai sesi wawancara macet.

---

## 2. Prasyarat Manual (dilakukan user, bukan agent)

Sebelum agent menjalankan task ini, user (Wahil) harus sudah:

1. Unduh **dua file** dari `https://huggingface.co/Eempostor/F5-TTS-INDO-FINETUNE-V2`:
   - `f5_tts_indo_v2.pt` (1.35 GB) → simpan ke `backend/models/F5-TTS-INDO-FINETUNE-V2/f5_tts_indo_v2.pt`
   - `vocab.txt` (13.8 kB) → simpan ke `backend/models/F5-TTS-INDO-FINETUNE-V2/vocab_id.txt`
     (vocab ini WAJIB — beda dari vocab bawaan F5-TTS base, karena hasil finetune Indonesia punya tokenizer sendiri. Tanpa file ini model tidak akan load dengan benar.)
2. Siapkan **audio referensi sendiri** (bukan dari demo HF):
   - Format: WAV/MP3 mono, durasi 6–15 detik, suara jelas tanpa noise/musik latar.
   - Simpan ke `backend/reference_audio/formal_male_reference.wav` (nama bebas, tapi hindari kata seperti di daftar guard Task 5).
   - Siapkan transkrip PERSIS (kata demi kata, termasuk tanda baca) dari audio tersebut → akan dipakai sebagai `reference_text`.
3. Konfirmasi hardware: apakah backend akan jalan di CPU saja atau ada GPU (CUDA)? Ini menentukan isi `F5TTS_DEVICE` di `.env` dan realistis-tidaknya streaming per-kalimat (lihat Catatan Performa di Task 7).

Agent TIDAK perlu mengunduh file-file di atas — hanya perlu menyiapkan kode yang mengasumsikan file-file itu ada di path yang disebut.

---

## 3. File yang Akan Diubah/Ditambah

```
backend/
├── requirements.txt                          [MODIFIED] tambah torch, torchaudio, f5-tts
├── main.py                                    [MODIFIED] preload model saat startup
├── app/
│   ├── core/
│   │   └── config.py                          [MODIFIED] tambah setting F5TTS_*
│   ├── models/
│   │   └── domain.py                          [MODIFIED] kolom baru di InterviewAvatar
│   ├── services/
│   │   ├── speech.py                          [MODIFIED] refactor jadi multi-engine
│   │   └── f5tts_service.py                   [NEW] wrapper inference F5-TTS
│   └── api/
│       └── websocket.py                       [MODIFIED] pilih engine per avatar
├── scripts/
│   ├── migrate_add_tts_columns.py             [NEW] ALTER TABLE untuk DB existing
│   └── set_avatar_voice_config.py             [NEW] apply config referensi ke semua avatar
└── reference_audio/                           [NEW dir] tempat file referensi user
```

---

## 4. Task 1 — Dependencies

Tambahkan ke `backend/requirements.txt` (jangan hapus baris lain):

```
torch==2.5.1
torchaudio==2.5.1
f5-tts==1.1.5
```

> Cek versi terbaru `f5-tts` di PyPI saat eksekusi — pin ke versi yang kompatibel dengan checkpoint `SWivid/F5-TTS` base (finetune ini mem-finetune arsitektur `F5TTS_Base` / DiT standar, bukan varian custom). Jika `pip install f5-tts` gagal resolve, fallback: clone `https://github.com/SWivid/F5-TTS` sebagai git submodule dan install `-e .` dari situ.

Update juga `Dockerfile`: image builder sudah punya `build-essential`/`gcc`; runtime stage sudah punya `ffmpeg` + `libsndfile1` (cukup untuk decode audio). Tambahkan komentar di Dockerfile yang menjelaskan bahwa base image `python:3.12-slim` ini CPU-only — jika nanti pindah ke GPU, base image perlu diganti ke image berbasis `nvidia/cuda` + install `torch` build CUDA.

---

## 5. Task 2 — Config (`app/core/config.py`)

Tambahkan setting berikut ke class `Settings`:

```python
class Settings(BaseSettings):
    # ...existing fields tetap...

    # ── F5-TTS (voice cloning engine) ──────────────────────────────
    F5TTS_MODEL_PATH: str = "backend/models/F5-TTS-INDO-FINETUNE-V2/f5_tts_indo_v2.pt"
    F5TTS_VOCAB_PATH: str = "backend/models/F5-TTS-INDO-FINETUNE-V2/vocab_id.txt"
    F5TTS_DEVICE: str = "cpu"          # "cpu" atau "cuda"
    F5TTS_DEFAULT_ENGINE: str = "edge_tts"  # default engine kalau avatar tidak set apa-apa
    F5TTS_REFERENCE_AUDIO_DIR: str = "reference_audio"
```

---

## 6. Task 3 — Schema (`backend/app/models/domain.py`)

Tambahkan 3 kolom baru ke class `InterviewAvatar` (di antara `ttsIntimidatingParams` dan `promptFriendly`):

```python
    ttsEngine = Column("tts_engine", String, default="edge_tts", nullable=False)
    ttsReferenceAudioPath = Column("tts_reference_audio_path", String)
    ttsReferenceText = Column("tts_reference_text", String)
```

Karena project ini **tidak pakai Alembic** (lihat `scripts/create_tables.py` — cuma `Base.metadata.create_all`), untuk database yang SUDAH ada datanya, `create_all` tidak akan menambah kolom ke tabel existing. Buat script migrasi manual:

**`backend/scripts/migrate_add_tts_columns.py`**

```python
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from app.core.database import engine

STATEMENTS = [
    "ALTER TABLE interview_avatar ADD COLUMN IF NOT EXISTS tts_engine VARCHAR NOT NULL DEFAULT 'edge_tts'",
    "ALTER TABLE interview_avatar ADD COLUMN IF NOT EXISTS tts_reference_audio_path VARCHAR",
    "ALTER TABLE interview_avatar ADD COLUMN IF NOT EXISTS tts_reference_text VARCHAR",
]

def migrate():
    with engine.begin() as conn:
        for stmt in STATEMENTS:
            print(f"Running: {stmt}")
            conn.execute(text(stmt))
    print("Migration selesai.")

if __name__ == "__main__":
    migrate()
```

(Sintaks `ADD COLUMN IF NOT EXISTS` valid untuk Postgres — cocok dengan `DATABASE_URL` di `config.py` yang default-nya `postgresql://...`.)

---

## 7. Task 4 — `app/services/f5tts_service.py` (baru)

Wrapper singleton, load model sekali:

```python
import io
import threading
import numpy as np
import torch
import torchaudio

from app.core.config import settings

_model_lock = threading.Lock()
_model = None
_vocoder = None


def _load_model():
    """Lazy-load F5-TTS model + vocoder sekali saja (thread-safe)."""
    global _model, _vocoder
    if _model is not None:
        return _model, _vocoder

    with _model_lock:
        if _model is not None:
            return _model, _vocoder

        from f5_tts.api import F5TTS  # sesuaikan import dengan API resmi paket f5-tts

        print(f"[F5TTS] Loading model dari {settings.F5TTS_MODEL_PATH} (device={settings.F5TTS_DEVICE})...")
        _model = F5TTS(
            model="F5TTS_Base",
            ckpt_file=settings.F5TTS_MODEL_PATH,
            vocab_file=settings.F5TTS_VOCAB_PATH,
            device=settings.F5TTS_DEVICE,
        )
        print("[F5TTS] Model siap.")
        return _model, _vocoder


def is_available() -> bool:
    """Cek apakah model bisa/sudah di-load, tanpa melempar exception ke caller."""
    try:
        _load_model()
        return True
    except Exception as e:
        print(f"[F5TTS] Model tidak tersedia: {e}")
        return False


def synthesize(text: str, ref_audio_path: str, ref_text: str, speed: float = 1.0) -> tuple[bytes, int]:
    """
    Generate audio dengan voice cloning dari ref_audio_path.
    Return: (wav_bytes, sample_rate)
    """
    model, _ = _load_model()

    wav, sr, _ = model.infer(
        ref_file=ref_audio_path,
        ref_text=ref_text,
        gen_text=text,
        speed=speed,
        remove_silence=True,
    )

    buffer = io.BytesIO()
    wav_tensor = torch.tensor(wav).unsqueeze(0) if not torch.is_tensor(wav) else wav.unsqueeze(0)
    torchaudio.save(buffer, wav_tensor, sr, format="wav")
    return buffer.getvalue(), sr
```

> Sesuaikan nama class/method (`F5TTS`, `.infer(...)`) dengan API aktual versi `f5-tts` yang ter-install saat eksekusi — cek `python -c "from f5_tts.api import F5TTS; help(F5TTS)"` sebelum finalisasi, karena API publik paket ini berubah antar versi.

---

## 8. Task 5 — Refactor `app/services/speech.py`

Pecah jadi: helper viseme (dipakai bersama), engine `edge_tts` (existing, jangan diubah logikanya), engine `f5tts` (baru), dan factory function.

```python
import edge_tts
import librosa
import numpy as np
import base64
import io

from app.services import f5tts_service

# Guard: tolak audio referensi yang namanya mengindikasikan file demo model
_FORBIDDEN_REFERENCE_TOKENS = ("prabowo", "windah", "reporter")


def _guard_reference_audio(path: str):
    lowered = (path or "").lower()
    if any(tok in lowered for tok in _FORBIDDEN_REFERENCE_TOKENS):
        raise ValueError(
            f"Reference audio '{path}' terindikasi file demo dokumentasi model "
            "(figur publik teridentifikasi). Gunakan rekaman referensi milik sendiri."
        )


def _to_percent_string(multiplier: float) -> str:
    percent = round((multiplier - 1.0) * 100)
    sign = "+" if percent >= 0 else ""
    return f"{sign}{percent}%"


def _extract_visemes(audio_data: bytes) -> list:
    """Ekstrak RMS envelope untuk viseme dari raw audio bytes (format apa pun yang didukung librosa)."""
    visemes = []
    try:
        audio_buffer = io.BytesIO(audio_data)
        y, sr = librosa.load(audio_buffer, sr=None)
        rms = librosa.feature.rms(y=y, hop_length=512)[0]
        if np.max(rms) > 0:
            visemes = (rms / np.max(rms)).tolist()
        else:
            visemes = rms.tolist()
    except Exception as e:
        print(f"Error generating visemes: {e}")
    return visemes


class SpeechService:
    """Engine default: edge_tts (cloud, stateless, tanpa voice cloning)."""

    def __init__(self, voice="id-ID-ArdiNeural"):
        self.voice = voice

    async def generate_speech_with_visemes(self, text: str, speed: float = 1.0, pitch: float = 1.0, **kwargs):
        rate_str = _to_percent_string(speed)
        pitch_hz = round((pitch - 1.0) * 50)
        pitch_sign = "+" if pitch_hz >= 0 else ""
        pitch_str = f"{pitch_sign}{pitch_hz}Hz"

        communicate = edge_tts.Communicate(text, self.voice, rate=rate_str, pitch=pitch_str)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        if not audio_data:
            return None, None

        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        visemes = _extract_visemes(audio_data)
        return audio_base64, visemes


class F5TTSSpeechService:
    """
    Engine voice cloning. Butuh ref_audio_path + ref_text per avatar (BUKAN global,
    BUKAN dari demo dokumentasi model — lihat _guard_reference_audio).

    Catatan: F5-TTS tidak punya kontrol "pitch" native seperti edge_tts (persen/Hz).
    Prosodi ditentukan oleh audio referensi + teks. Parameter `pitch` di sini
    diterapkan sebagai post-process pitch-shift ringan via librosa, hanya jika
    pitch menyimpang jauh dari 1.0 (agar tidak merusak naturalitas hasil clone).
    """

    def __init__(self, ref_audio_path: str, ref_text: str):
        _guard_reference_audio(ref_audio_path)
        self.ref_audio_path = ref_audio_path
        self.ref_text = ref_text

    async def generate_speech_with_visemes(self, text: str, speed: float = 1.0, pitch: float = 1.0, **kwargs):
        try:
            wav_bytes, sr = f5tts_service.synthesize(
                text=text,
                ref_audio_path=self.ref_audio_path,
                ref_text=self.ref_text,
                speed=speed,
            )
        except Exception as e:
            print(f"[F5TTS] Inference gagal, fallback ke edge_tts: {e}")
            fallback = SpeechService()
            return await fallback.generate_speech_with_visemes(text, speed=speed, pitch=pitch)

        if abs(pitch - 1.0) > 0.03:
            try:
                y, sr_loaded = librosa.load(io.BytesIO(wav_bytes), sr=None)
                n_steps = (pitch - 1.0) * 4  # skala kasar, tune sesuai kebutuhan
                y_shifted = librosa.effects.pitch_shift(y, sr=sr_loaded, n_steps=n_steps)
                buf = io.BytesIO()
                import soundfile as sf
                sf.write(buf, y_shifted, sr_loaded, format="WAV")
                wav_bytes = buf.getvalue()
            except Exception as e:
                print(f"[F5TTS] Pitch-shift post-process gagal, pakai audio asli: {e}")

        audio_base64 = base64.b64encode(wav_bytes).decode("utf-8")
        visemes = _extract_visemes(wav_bytes)
        return audio_base64, visemes


def get_speech_service_for_avatar(avatar) -> "SpeechService | F5TTSSpeechService":
    """
    Factory: pilih engine berdasarkan kolom tts_engine di avatar.
    Fallback aman ke edge_tts kalau avatar None, engine tidak dikenal,
    atau konfigurasi referensi F5TTS tidak lengkap.
    """
    engine = getattr(avatar, "ttsEngine", None) or "edge_tts"

    if engine == "f5tts_indo_v2":
        ref_path = getattr(avatar, "ttsReferenceAudioPath", None)
        ref_text = getattr(avatar, "ttsReferenceText", None)
        if not ref_path or not ref_text:
            print(f"[SpeechService] Avatar {getattr(avatar, 'id', '?')} set ke f5tts tapi referensi belum lengkap, fallback edge_tts.")
            return SpeechService(voice=getattr(avatar, "ttsVoiceId", None) or "id-ID-ArdiNeural")
        try:
            return F5TTSSpeechService(ref_audio_path=ref_path, ref_text=ref_text)
        except ValueError as e:
            print(f"[SpeechService] {e} — fallback edge_tts.")
            return SpeechService(voice=getattr(avatar, "ttsVoiceId", None) or "id-ID-ArdiNeural")

    return SpeechService(voice=getattr(avatar, "ttsVoiceId", None) or "id-ID-ArdiNeural")


# Instance default untuk endpoint yang belum avatar-aware (mis. /api/speech generik)
speech_service = SpeechService()
```

---

## 9. Task 6 — `app/api/websocket.py`: pakai engine per avatar

Di `send_next_question_stream`, avatar sudah di-fetch di awal fungsi (`avatar = db.query(InterviewAvatar)...`). Tambahkan setelah baris itu:

```python
from app.services.speech import get_speech_service_for_avatar, speech_service as default_speech_service
# (ganti import `from app.services.speech import speech_service` yang lama)

# ...di dalam send_next_question_stream, setelah avatar di-fetch:
active_speech_service = get_speech_service_for_avatar(avatar)
```

Lalu ganti semua pemanggilan `speech_service.generate_speech_with_visemes(...)` **di dalam fungsi ini** menjadi `active_speech_service.generate_speech_with_visemes(...)` (ada 2 titik pemanggilan: loop per-kalimat & sisa buffer kalimat terakhir).

Di `re_send_last_question`, tambahkan fetch avatar dan lakukan hal yang sama:

```python
async def re_send_last_question(websocket: WebSocket, db: Session, last_turn: SessionTurn, session: InterviewSession):
    avatar = db.query(InterviewAvatar).filter(InterviewAvatar.id == session.avatarId).first()
    active_speech_service = get_speech_service_for_avatar(avatar)
    tts_speed, tts_pitch = get_tts_params(session.scenario, session.pressureLevel)
    audio_base64, visemes = await active_speech_service.generate_speech_with_visemes(
        last_turn.questionText, speed=tts_speed, pitch=tts_pitch
    )
    # ...sisanya sama seperti sebelumnya
```

`main.py` endpoint `/api/speech` boleh tetap pakai `default_speech_service` (edge_tts) karena endpoint itu generik, tidak terikat avatar tertentu — tidak perlu diubah kecuali user memang minta.

---

## 10. Task 7 — Preload model saat startup (`main.py`)

Tambahkan FastAPI lifespan event supaya model F5-TTS di-load sekali saat server start, bukan saat request pertama masuk (menghindari latensi besar di request pertama tiap avatar F5TTS):

```python
from contextlib import asynccontextmanager
from app.services import f5tts_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload F5-TTS hanya kalau ada avatar yang memakainya — cek cepat ke DB
    db = SessionLocal()
    try:
        any_f5tts_avatar = db.query(InterviewAvatar).filter(InterviewAvatar.ttsEngine == "f5tts_indo_v2").first()
        if any_f5tts_avatar:
            print("Preloading F5-TTS model...")
            f5tts_service.is_available()
    finally:
        db.close()
    yield

app = FastAPI(title="Heurix AI Agent Backend", lifespan=lifespan)
```

(Ganti baris `app = FastAPI(title="Heurix AI Agent Backend")` yang lama dengan versi di atas.)

---

## 11. Task 8 — Script konfigurasi avatar (`scripts/set_avatar_voice_config.py`)

Script ini **tidak** hardcode file referensi apa pun — wajib disuplai lewat argumen CLI oleh user setelah dia menyiapkan rekamannya sendiri (lihat Prasyarat §2).

```python
import sys, os, argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import InterviewAvatar

FORBIDDEN_TOKENS = ("prabowo", "windah", "reporter")


def main():
    parser = argparse.ArgumentParser(
        description="Terapkan konfigurasi voice cloning F5-TTS ke SEMUA avatar aktif."
    )
    parser.add_argument("--ref-audio", required=True, help="Path ke file audio referensi milik sendiri")
    parser.add_argument("--ref-text", required=True, help="Transkrip PERSIS dari audio referensi")
    parser.add_argument("--engine", default="f5tts_indo_v2")
    parser.add_argument("--dry-run", action="store_true", help="Tampilkan perubahan tanpa commit ke DB")
    args = parser.parse_args()

    lowered = args.ref_audio.lower()
    if any(tok in lowered for tok in FORBIDDEN_TOKENS):
        print(f"DITOLAK: '{args.ref_audio}' terindikasi file demo dokumentasi model (figur publik).")
        print("Gunakan rekaman referensi milik sendiri.")
        sys.exit(1)

    if not os.path.exists(args.ref_audio):
        print(f"DITOLAK: file '{args.ref_audio}' tidak ditemukan di filesystem.")
        sys.exit(1)

    db = SessionLocal()
    try:
        avatars = db.query(InterviewAvatar).all()
        print(f"Ditemukan {len(avatars)} avatar.")
        for avatar in avatars:
            print(f"  - {avatar.id} ({avatar.name}): {avatar.ttsEngine} -> {args.engine}")
            if not args.dry_run:
                avatar.ttsEngine = args.engine
                avatar.ttsReferenceAudioPath = args.ref_audio
                avatar.ttsReferenceText = args.ref_text

        if args.dry_run:
            print("Dry-run, tidak ada perubahan disimpan.")
        else:
            db.commit()
            print("Konfigurasi diterapkan ke semua avatar.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

Cara pakai (setelah user menyiapkan file referensi sendiri):

```bash
python scripts/set_avatar_voice_config.py \
  --ref-audio reference_audio/formal_male_reference.wav \
  --ref-text "isi transkrip persis dari audio referensi" \
  --dry-run   # jalankan dulu tanpa --dry-run untuk cek, baru commit
```

---

## 12. Catatan Performa — WAJIB dikomunikasikan ke user, jangan silent

F5-TTS adalah model diffusion/flow-matching yang jauh lebih berat dari `edge_tts` (yang cuma API call ke cloud). Di alur `websocket.py` saat ini, audio di-generate **per kalimat** secara streaming (`send_next_question_stream` memanggil TTS berkali-kali per giliran bicara). Di CPU, tiap panggilan F5-TTS bisa makan waktu beberapa detik — dikali jumlah kalimat per jawaban, ini bisa terasa sangat lambat dibanding `edge_tts` yang nyaris instan.

Rekomendasi yang sebaiknya didiskusikan dengan user sebelum/selama implementasi (bukan diputuskan sepihak oleh agent):

1. Kalau hardware target CPU-only → pertimbangkan generate **satu kali per giliran penuh** (bukan per kalimat) khusus untuk avatar F5TTS, mengorbankan efek "streaming per kalimat" demi mengurangi overhead loading/inference berulang.
2. Kalau ada GPU tersedia → set `F5TTS_DEVICE=cuda`, ini akan jauh lebih realistis untuk streaming per kalimat.
3. Sebagai mitigasi sementara, biarkan fallback-ke-`edge_tts` yang sudah ada di `F5TTSSpeechService` tetap aktif — kalau inference lambat/timeout, sesi tidak macet.

---

## 13. Verification Checklist (jalankan setelah semua task selesai)

- [ ] `pip install -r requirements.txt` berhasil tanpa conflict versi torch.
- [ ] `python scripts/migrate_add_tts_columns.py` berhasil menambah 3 kolom baru tanpa error, dan tidak menghapus data avatar existing.
- [ ] Endpoint lama (`/api/speech`, `POST /api/sessions`, `/ws/{sessionId}`) tetap berfungsi normal untuk avatar yang `ttsEngine='edge_tts'` (default) — regresi nol.
- [ ] `f5tts_service.is_available()` mengembalikan `True` saat file model+vocab ada di path yang benar, dan `False` (bukan exception tak tertangkap) saat file tidak ada.
- [ ] Menjalankan `scripts/set_avatar_voice_config.py` dengan `--ref-audio` yang namanya mengandung `prabowo`/`windah`/`reporter` **ditolak** dengan exit code non-zero.
- [ ] Menjalankan dengan file referensi sendiri yang valid → semua avatar ter-update, dan sesi wawancara baru dengan avatar tersebut menghasilkan audio ber-voice-clone.
- [ ] Simulasikan F5-TTS gagal load (mis. ganti path model jadi salah) → sesi tetap jalan lewat fallback `edge_tts`, tidak crash, ada log warning.
- [ ] Ukur latensi 1x panggilan `f5tts_service.synthesize()` di hardware target, laporkan ke user sebelum dianggap selesai (lihat §12).
