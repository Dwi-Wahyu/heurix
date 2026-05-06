import edge_tts
import librosa
import numpy as np
import base64
import io
import asyncio

class SpeechService:
    def __init__(self, voice="id-ID-ArdiNeural"):
        self.voice = voice

    async def generate_speech_with_visemes(self, text: str):
        """
        Menghasilkan audio (base64) dan data viseme (amplitude envelope).
        """
        communicate = edge_tts.Communicate(text, self.voice)
        audio_data = b""
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        if not audio_data:
            return None, None

        # Load audio data dengan librosa
        # Kita gunakan buffer BytesIO agar tidak perlu menulis ke disk
        audio_buffer = io.BytesIO(audio_data)
        y, sr = librosa.load(audio_buffer, sr=None)

        # Ekstrak Root Mean Square (RMS) untuk mendapatkan tingkat kekerasan suara (amplitudo)
        # Hop_length menentukan "frame rate" viseme kita. 
        # Misal sr=22050, hop_length=512 -> ~43 fps viseme.
        rms = librosa.feature.rms(y=y, hop_length=512)[0]
        
        # Normalisasi ke 0 - 1
        if np.max(rms) > 0:
            visemes = (rms / np.max(rms)).tolist()
        else:
            visemes = rms.tolist()

        # Encode audio ke base64 agar mudah dikirim via JSON
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        return audio_base64, visemes

speech_service = SpeechService()
