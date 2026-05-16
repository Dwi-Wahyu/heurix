from faster_whisper import WhisperModel
from app.core.config import settings
import os

# Memastikan cache model tersimpan di direktori 'models'
os.environ["HF_HOME"] = "models"

class Transcriber:
    def __init__(self):
        # Gunakan 'cpu' jika tidak ada CUDA
        self.model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")

    def transcribe_and_detect_fillers(self, audio_path):
        # Memaksa bahasa ke Indonesia (id) dan memberikan prompt awal untuk mengurangi halusinasi
        segments, _ = self.model.transcribe(
            audio_path, 
            beam_size=5, 
            language="id",
            initial_prompt="Ini adalah percakapan simulasi wawancara kerja dalam Bahasa Indonesia yang formal dan profesional."
        )
        full_text = " ".join([s.text for s in segments]).strip()

        # Logika deteksi filler sederhana
        fillers = ["eh", "hmm", "umm", "anu", "jadi", "kayaknya", "mungkin", "apa ya"]
        breakdown = {}
        total_count = 0
        
        text_lower = full_text.lower()
        for f in fillers:
            count = text_lower.count(f)
            if count > 0:
                breakdown[f] = count
                total_count += count

        return full_text, total_count, breakdown

transcriber = Transcriber()
