import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/ root directory (/app in Docker)


def _find_f5tts_path(filename_options: list[str]) -> str:
    env_model_path = os.getenv("MODEL_PATH")
    search_dirs = []
    if env_model_path:
        search_dirs.append(Path(env_model_path))
    
    search_dirs.extend([
        BASE_DIR / "models",
        BASE_DIR / "backend" / "models",
        Path("models"),
        Path("backend/models"),
    ])

    for model_dir in search_dirs:
        for filename in filename_options:
            target = model_dir / "F5-TTS-INDO-FINETUNE-V2" / filename
            if target.exists():
                return str(target)
    
    # Fallback default if not found on disk yet
    return str(BASE_DIR / "models" / "F5-TTS-INDO-FINETUNE-V2" / filename_options[0])


class Settings(BaseSettings):
    PROJECT_NAME: str = "HireReady AI Agent"
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/hireready"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    WHISPER_MODEL: str = "small"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str = ""

    # ── F5-TTS (voice cloning engine) ──────────────────────────────
    F5TTS_MODEL_PATH: str = ""
    F5TTS_VOCAB_PATH: str = ""
    F5TTS_DEVICE: str = "cpu"          # "cpu" atau "cuda"
    F5TTS_DEFAULT_ENGINE: str = "edge_tts"  # default engine kalau avatar tidak set apa-apa
    F5TTS_REFERENCE_AUDIO_DIR: str = "reference_audio"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.F5TTS_MODEL_PATH:
            self.F5TTS_MODEL_PATH = _find_f5tts_path(["f5_tts_indo_v2.pt"])
        if not self.F5TTS_VOCAB_PATH:
            self.F5TTS_VOCAB_PATH = _find_f5tts_path(["vocab_id.txt", "vocab.txt"])

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

