Untuk membangun MVP backend AI Agent yang responsif dan multimodal untuk proyek **HireReady**, koordinasi antara pengolahan data biner (audio) dan data teks (metadata emosi) sangat krusial. Berikut adalah dokumentasi langkah komprehensif untuk menyiapkan infrastruktur backend menggunakan FastAPI.

### 1. Inisialisasi Lingkungan & Struktur Proyek

Gunakan sistem operasi Anda saat ini untuk mengelola dependensi dengan efisien. Pastikan Python 3.10+ telah terinstal.

**Struktur Folder Rekomendasi:**

```text
backend/
├── app/
│   ├── api/            # Endpoint WebSocket & HTTP
│   ├── services/       # Logika ML (Whisper, Ollama, Librosa)
│   ├── core/           # Konfigurasi & Database
│   └── utils/          # Helper (PDF Generator, STAR Logic)
├── models/             # Cache untuk model Whisper & Llama
├── scripts/            # Database seeding/migration
└── main.py             # Entry point
```

### 2. Instalasi Dependensi Utama

Buat _virtual environment_ dan instal library yang mendukung pemrosesan asinkron dan AI lokal:

```bash
# Instalasi library sistem untuk audio (Debian/Ubuntu/Pop!_OS)
sudo apt update && sudo apt install ffmpeg -y

# Instalasi library Python
pip install fastapi uvicorn websockets faster-whisper ollama librosa sqlalchemy psycopg2-binary qdrant-client
```

### 3. Arsitektur Koneksi WebSocket

[cite_start]Karena frontend Anda mengirimkan data emosi secara real-time[cite: 36, 40], backend harus mampu menerima metadata tersebut tanpa terblokir oleh pemrosesan audio yang berat.

**Implementasi `app/api/websocket.py`:**
Gunakan `asyncio.Queue` untuk memisahkan penerimaan data dengan pemrosesan (Producer-Consumer pattern).

```python
from fastapi import WebSocket
import asyncio
import json

class InterviewAgent:
    def __init__(self):
        self.audio_queue = asyncio.Queue()
        self.session_data = {"emotion_history": [], "transcript": ""}

    async def receiver(self, websocket: WebSocket):
        """Menerima data dari SvelteKit secara asinkron."""
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message["type"] == "METADATA":
                    # [cite_start]Simpan data emosi dari MediaPipe [cite: 25-30]
                    self.session_data["emotion_history"].append(message["data"])
                elif message["type"] == "AUDIO":
                    await self.audio_queue.put(message["blob"])
        except Exception as e:
            print(f"Connection closed: {e}")

    async def processor(self, websocket: WebSocket):
        """Memproses audio dan logika AI di background."""
        while True:
            audio_blob = await self.audio_queue.get()
            # 1. Jalankan Whisper (STT)
            # 2. Hitung WPM (Acoustic)
            # 3. Kirim feedback real-time ke SvelteKit jika perlu
            self.audio_queue.task_done()
```

### 4. Integrasi Mesin AI (Self-Hosted)

#### A. Transkripsi & Deteksi Filler Words (`services/transcriber.py`)

`faster-whisper` sangat efisien untuk dijalankan secara lokal. Untuk mendeteksi _filler words_, kita akan memproses transkrip mentah.

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cuda", compute_type="float16")

def transcribe_and_detect_fillers(audio_path):
    segments, _ = model.transcribe(audio_path, beam_size=5)
    full_text = " ".join([s.text for s in segments])

    # Logika deteksi filler sederhana
    fillers = ["eh", "umm", "anu", "jadi"]
    count = sum(full_text.lower().count(f) for f in fillers)

    return full_text, count
```

#### B. Brain / LLM (`services/brain.py`)

Hubungkan ke Ollama untuk melakukan evaluasi metode STAR (Situation, Task, Action, Result).

```python
import ollama

async def get_ai_feedback(user_answer, context):
    prompt = f"Evaluasi jawaban ini menggunakan metode STAR: {user_answer}. Berikan kritik pedas (Roast) namun edukatif."
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt},
    ])
    return response['message']['content']
```

### 5. Skema Database (Relational & Vector)

- **PostgreSQL:** Gunakan untuk menyimpan profil kandidat, riwayat sesi wawancara, dan skor akhir.
- **Qdrant/ChromaDB:** Simpan bank soal wawancara dalam bentuk _embeddings_. Saat user memilih posisi (misal: "Frontend Dev"), backend akan melakukan _similarity search_ untuk mengambil soal yang relevan.

### 6. Logika Evaluasi Pasca-Wawancara

Setelah sesi selesai, gabungkan `emotion_history` dari frontend dengan data transkrip.

- [cite_start]**Korelasi:** Jika emosi menunjukkan "ANGRY" atau "SAD" [cite: 27, 28] saat menjawab pertanyaan teknis, ini menjadi catatan khusus dalam laporan evaluasi.
- **Output:** Gunakan library `ReportLab` di Python untuk mengonversi agregasi data ini menjadi file PDF yang siap diunduh.

**Saran Pertama:**
Fokuslah pada **sinkronisasi timestamp**. [cite_start]Pastikan data emosi yang dikirim oleh `predictWebcam` di SvelteKit [cite: 22, 34] menyertakan _timestamp_ yang sama dengan rekaman audio agar Anda bisa memetakan emosi user tepat pada kata-kata tertentu yang mereka ucapkan.

Apakah Anda ingin saya mendetailkan skema database untuk menyimpan bank soal di Vector DB?
