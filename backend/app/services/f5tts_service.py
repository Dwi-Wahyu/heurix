import io
import os
import threading
import asyncio
import numpy as np

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

        if not os.path.exists(settings.F5TTS_MODEL_PATH):
            raise FileNotFoundError(f"Model file tidak ditemukan di: {settings.F5TTS_MODEL_PATH}")
        if not os.path.exists(settings.F5TTS_VOCAB_PATH):
            raise FileNotFoundError(f"Vocab file tidak ditemukan di: {settings.F5TTS_VOCAB_PATH}")

        from f5_tts.api import F5TTS  # import paket f5-tts

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
    import torch
    import torchaudio

    model, _ = _load_model()


    wav, sr, _ = model.infer(
        ref_file=ref_audio_path,
        ref_text=ref_text,
        gen_text=text,
        nfe_step=getattr(settings, "F5TTS_NFE_STEP", 16),
        speed=speed,
        remove_silence=True,
    )

    buffer = io.BytesIO()
    wav_tensor = torch.tensor(wav).unsqueeze(0) if not torch.is_tensor(wav) else wav.unsqueeze(0)
    torchaudio.save(buffer, wav_tensor, sr, format="wav")
    return buffer.getvalue(), sr


async def synthesize_async(text: str, ref_audio_path: str, ref_text: str, speed: float = 1.0) -> tuple[bytes, int]:
    """
    Versi asinkron dari synthesize() yang memindahkan CPU inference ke thread pool
    menggunakan asyncio.to_thread agar tidak memblokir event loop asyncio.
    """
    return await asyncio.to_thread(synthesize, text, ref_audio_path, ref_text, speed)

