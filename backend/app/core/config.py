from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HireReady AI Agent"
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/hireready"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    WHISPER_MODEL: str = "small"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str = ""

    # ── F5-TTS (voice cloning engine) ──────────────────────────────
    F5TTS_MODEL_PATH: str = "backend/models/F5-TTS-INDO-FINETUNE-V2/f5_tts_indo_v2.pt"
    F5TTS_VOCAB_PATH: str = "backend/models/F5-TTS-INDO-FINETUNE-V2/vocab_id.txt"
    F5TTS_DEVICE: str = "cpu"          # "cpu" atau "cuda"
    F5TTS_DEFAULT_ENGINE: str = "edge_tts"  # default engine kalau avatar tidak set apa-apa
    F5TTS_REFERENCE_AUDIO_DIR: str = "reference_audio"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
