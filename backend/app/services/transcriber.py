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
        # Memaksa bahasa ke Indonesia (id), gunakan VAD filter & prompt untuk cegah halusinasi
        segments, info = self.model.transcribe(
            audio_path, 
            beam_size=5, 
            language="id",
            initial_prompt="Ini adalah percakapan simulasi wawancara kerja dalam Bahasa Indonesia yang formal dan profesional.",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200),
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6,
        )

        # Buang segment dengan confidence rendah / kemungkinan besar no-speech (halusinasi)
        valid_segments = []
        for s in segments:
            if s.no_speech_prob > 0.6 or s.avg_logprob < -1.0:
                continue
            valid_segments.append(s.text)

        full_text = " ".join(valid_segments).strip()

        if not full_text:
            return "", 0, {}

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

