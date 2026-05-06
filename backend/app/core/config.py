from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HireReady AI Agent"
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/hireready"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    WHISPER_MODEL: str = "small"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
