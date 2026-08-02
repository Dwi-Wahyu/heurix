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
