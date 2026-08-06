import edge_tts
import librosa
import numpy as np
import base64
import io

from app.services import f5tts_service

import os
from pathlib import Path
from app.core.config import BASE_DIR

# Guard: tolak audio referensi yang namanya mengindikasikan file demo model
_FORBIDDEN_REFERENCE_TOKENS = ("prabowo", "windah", "reporter")


def _resolve_reference_audio_path(path: str) -> str:
    if not path:
        return path
    if os.path.exists(path):
        return path
    
    clean_path = path.replace("\\", "/")
    if clean_path.startswith("backend/"):
        clean_path = clean_path[len("backend/"):]
        
    candidates = [
        BASE_DIR / clean_path,
        BASE_DIR / "reference_audio" / os.path.basename(clean_path),
        Path("reference_audio") / os.path.basename(clean_path),
        Path("backend/reference_audio") / os.path.basename(clean_path),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return path


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
        resolved_path = _resolve_reference_audio_path(ref_audio_path)
        _guard_reference_audio(resolved_path)
        self.ref_audio_path = resolved_path
        self.ref_text = ref_text

    async def generate_speech_with_visemes(self, text: str, speed: float = 1.0, pitch: float = 1.0, **kwargs):
        try:
            wav_bytes, sr = await f5tts_service.synthesize_async(
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
