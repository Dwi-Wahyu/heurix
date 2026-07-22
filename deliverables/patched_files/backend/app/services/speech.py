import edge_tts
import librosa
import numpy as np
import base64
import io
import asyncio

def _to_percent_string(multiplier: float) -> str:
    """
    Konversi rasio (1.0 = normal) ke string persen bertanda yang dipahami
    edge_tts, misal 1.15 -> "+15%", 0.9 -> "-10%".
    """
    percent = round((multiplier - 1.0) * 100)
    sign = "+" if percent >= 0 else ""
    return f"{sign}{percent}%"


class SpeechService:
    def __init__(self, voice="id-ID-ArdiNeural"):
        self.voice = voice

    async def generate_speech_with_visemes(self, text: str, speed: float = 1.0, pitch: float = 1.0):
        """
        Menghasilkan audio (base64) dan data viseme (amplitude envelope).

        speed: rasio kecepatan bicara, 1.0 = normal (dipakai APE Pilar 1 & 3).
        pitch: rasio pitch relatif, 1.0 = normal.
        """
        rate_str = _to_percent_string(speed)
        # edge_tts menerima pitch dalam Hz bertanda, misal "+10Hz" / "-10Hz".
        # Kita petakan rasio pitch ke rentang wajar (~ +/-50Hz) agar tidak terdengar aneh.
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

        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        visemes = []

        try:
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
        except Exception as e:
            print(f"Error generating visemes: {e}")
            # Fallback: visemes kosong, audio tetap dikirim

        return audio_base64, visemes

speech_service = SpeechService()
