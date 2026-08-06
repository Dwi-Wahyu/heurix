# Instruksi Perbaikan: Halusinasi Whisper, Latensi Kalimat Pertama, & Voice Cloning F5TTS Belum Aktif

**Untuk:** Agen CLI (Claude Code / Gemini CLI)
**Repo:** heurix backend (`backend/app/`)
**Konteks:** 3 masalah dilaporkan setelah integrasi F5-TTS-INDO-FINETUNE-V2 (lihat `INTEGRASI_F5TTS_INDO_REPORT.md`):
1. Whisper sering berhalusinasi ("Terima kasih kerana menonton!" padahal user bicara hal lain)
2. Kalimat pertama pewawancara lama sekali keluar
3. Suara belum kedengaran pakai aksen dari `reference_audio/formal_male_reference.wav` walau file sudah ada di server

> Saya sudah trace ke `transcriber.py`, `speech.py`, `f5tts_service.py`, `websocket.py` — bukan tebakan. Detail evidence ada di tiap bagian.

---

## MASALAH 1 — Halusinasi Whisper

### Root cause
`backend/app/services/transcriber.py` — `model.transcribe()` dipanggil tanpa `vad_filter`, tanpa `no_speech_threshold`/`avg_logprob` check, dan `condition_on_previous_text` masih default `True`. Frasa "terima kasih (sudah/kerana) menonton" adalah halusinasi terkenal faster-whisper/Whisper saat audio hening/noise — modelnya dilatih dari caption YouTube dan "menutup" ucapan yang tidak jelas dengan kalimat semacam itu.

### Fix
Edit `backend/app/services/transcriber.py`:

```python
def transcribe_and_detect_fillers(self, audio_path):
    segments, info = self.model.transcribe(
        audio_path,
        beam_size=5,
        language="id",
        initial_prompt="Ini adalah percakapan simulasi wawancara kerja dalam Bahasa Indonesia yang formal dan profesional.",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200),
        condition_on_previous_text=False,   # cegah halusinasi "menular" dari segment sebelumnya
        compression_ratio_threshold=2.4,     # default whisper, buang segment yang terlalu repetitif
        no_speech_threshold=0.6,
    )

    # Buang segment dengan confidence rendah / kemungkinan besar no-speech
    valid_segments = []
    for s in segments:
        # avg_logprob rendah + no_speech_prob tinggi = kemungkinan besar halusinasi, bukan ucapan asli
        if s.no_speech_prob > 0.6 or s.avg_logprob < -1.0:
            continue
        valid_segments.append(s.text)

    full_text = " ".join(valid_segments).strip()

    # Kalau setelah filter tidak tersisa apa-apa, anggap memang tidak ada ucapan valid
    if not full_text:
        return "", 0, {}

    # ... sisa logic filler words TIDAK berubah, tetap pakai full_text di atas ...
```

**Catatan:** `vad_filter=True` butuh `onnxruntime` ter-install (biasanya sudah ikut terbawa `faster-whisper`, tapi cek `pip show onnxruntime` di container kalau muncul error saat testing). Ini SATU-SATUNYA fix yang paling berdampak — jangan skip.

**Verifikasi:** setelah deploy, coba diamkan mic ~5 detik saat direkam (simulasikan audio hening/noise), transcript hasil harus jadi string kosong `""` (ditangani frontend dengan pesan "suara tidak terdengar jelas"), BUKAN kalimat halusinasi.

---

## MASALAH 2 & 3 (terkait) — Blocking Event Loop pada Pemanggilan Whisper & F5TTS

### Root cause
`backend/app/api/websocket.py` baris ~127:
```python
transcript_text, filler_count, filler_breakdown = transcriber.transcribe_and_detect_fillers(temp_filename)
```
Ini dipanggil **sinkron** di dalam `async def` handler WebSocket, **tanpa** `asyncio.to_thread`/`run_in_executor`. Whisper inference itu CPU-bound dan bisa makan waktu 1-3+ detik. Karena Gunicorn cuma jalan **1 worker** (`Booting worker with pid: 8` di log kamu), selama Whisper jalan, **seluruh event loop asyncio ikut macet** — WebSocket lain, request lain, semuanya nunggu.

Hal yang sama berlaku untuk `f5tts_service.synthesize()` yang dipanggil dari `F5TTSSpeechService.generate_speech_with_visemes()` di `speech.py` — juga sinkron tanpa executor. Kalau nanti F5TTS aktif, inferensi torch CPU (2-5 detik/kalimat menurut laporan implementasi kamu sendiri) akan memblokir event loop selama itu **untuk SEMUA sesi yang sedang berjalan**, bukan cuma sesi yang lagi minta TTS.

### Fix
Bungkus kedua pemanggilan sinkron berat ini dengan `asyncio.to_thread` (Python 3.9+, aman dipakai di FastAPI):

**`websocket.py`:**
```python
import asyncio
# ...
transcript_text, filler_count, filler_breakdown = await asyncio.to_thread(
    transcriber.transcribe_and_detect_fillers, temp_filename
)
```

**`f5tts_service.py`** — bungkus level lebih dalam supaya loading model (yang bisa berat di panggilan pertama) juga tidak nge-block:
```python
import asyncio

async def synthesize_async(text: str, ref_audio_path: str, ref_text: str, speed: float = 1.0) -> tuple[bytes, int]:
    return await asyncio.to_thread(synthesize, text, ref_audio_path, ref_text, speed)
```

**`speech.py`** — di `F5TTSSpeechService.generate_speech_with_visemes`, ganti:
```python
wav_bytes, sr = f5tts_service.synthesize(...)
```
menjadi:
```python
wav_bytes, sr = await f5tts_service.synthesize_async(
    text=text, ref_audio_path=self.ref_audio_path, ref_text=self.ref_text, speed=speed,
)
```

> Catatan arsitektur: `asyncio.to_thread` hanya memindahkan blocking call ke thread pool — tetap satu proses, jadi CPU tetap dipakai penuh saat inferensi (tidak membuat torch lebih cepat), tapi **event loop tidak ikut macet** sehingga sesi lain / heartbeat WebSocket tetap responsif. Untuk load beneran tinggi (banyak user bersamaan), pertimbangkan menambah worker Gunicorn atau antrian request — di luar scope perbaikan ini.

### Instrumentasi untuk konfirmasi "lambat kalimat pertama"
Log yang kamu kirim belum cukup granular untuk memastikan stage mana yang paling lambat (STT / LLM Groq / TTS). Tambahkan timing log di `send_next_question_stream` (`websocket.py`), sebelum & sesudah tiap stage:
```python
import time
t0 = time.monotonic()
# ... panggilan ke Groq/brain.py untuk generate pertanyaan ...
t1 = time.monotonic()
audio, visemes = await active_speech_service.generate_speech_with_visemes(...)
t2 = time.monotonic()
print(f"[TIMING] LLM: {t1-t0:.2f}s | TTS: {t2-t1:.2f}s | engine={active_speech_service.__class__.__name__}")
```
Jalankan sesi baru, lihat log ini — kalau `TTS` yang paling lambat dan `engine=F5TTSSpeechService`, berarti memang F5TTS (lanjut ke Masalah 3 di bawah, dan pastikan preload di startup benar-benar jalan). Kalau `LLM` yang lambat, itu di luar scope F5TTS — kemungkinan cold-start koneksi ke Groq API atau prompt yang terlalu panjang.

---

## MASALAH 3 — Voice Cloning Belum Aktif (Aksen Belum Kepakai)

### Cara pastikan diagnosis di atas benar
Masuk ke container, cek langsung:
```bash
docker exec -it heurix-backend bash

# 1. Cek apakah kolom DB avatar sudah keisi
python -c "
from app.core.database import SessionLocal
from app.models.domain import InterviewAvatar
db = SessionLocal()
for a in db.query(InterviewAvatar).all():
    print(a.id, a.name, '| engine:', getattr(a, 'ttsEngine', 'KOLOM TIDAK ADA'), '| ref_audio:', getattr(a, 'ttsReferenceAudioPath', None), '| ref_text:', getattr(a, 'ttsReferenceText', None))
"

# 2. Cek apakah model checkpoint & vocab benar-benar ada DI DALAM CONTAINER
#    (bukan cuma di host!) — path relatif "backend/..." rawan salah resolve di container
ls -la backend/models/F5-TTS-INDO-FINETUNE-V2/ 2>&1 || echo "FOLDER TIDAK DITEMUKAN — cek WORKDIR container"
pwd   # bandingkan working dir aktual dengan F5TTS_MODEL_PATH di config.py

# 3. Test langsung apakah is_available() berhasil
python -c "
from app.services import f5tts_service
print('is_available:', f5tts_service.is_available())
"
```

### Kemungkinan penyebab (cek berurutan sesuai probabilitas)

1. **Paling mungkin: `set_avatar_voice_config.py` belum pernah dijalankan.** Menaruh file `.wav` di `backend/reference_audio/` **tidak otomatis** mengisi kolom `tts_engine`/`tts_reference_audio_path`/`tts_reference_text` di database — itu cuma naruh file. Harus dijalankan manual:
   ```bash
   docker exec -it heurix-backend python backend/scripts/set_avatar_voice_config.py \
     --ref-audio reference_audio/formal_male_reference.wav \
     --ref-text "TRANSKRIP PERSIS APA YANG DIUCAPKAN DI FILE WAV INI" \
     --dry-run   # jalankan dulu dry-run, cek outputnya, baru tanpa --dry-run
   ```
   **`--ref-text` harus transkrip AKURAT** dari isi `formal_male_reference.wav` (F5-TTS pakai ini buat alignment fonetik referensi — kalau transkrip meleset dari audio, hasil clone bisa aneh/gagal walau tidak error).

2. **Model checkpoint belum di-download dari HuggingFace.** Log test integrasi kamu sendiri (`INTEGRASI_F5TTS_INDO_REPORT.md` bagian 4) menunjukkan saat testing, vocab file **tidak ditemukan** — itu WAJAR karena memang testing pakai mock/belum download model asli, tapi pastikan di server produksi (`dentalserver`) filenya BENERAN ada:
   ```bash
   docker exec -it heurix-backend ls -la backend/models/F5-TTS-INDO-FINETUNE-V2/
   # harus ada: f5_tts_indo_v2.pt (~1.35GB) dan vocab_id.txt
   ```
   Kalau belum ada, download dari `https://huggingface.co/Eempostor/F5-TTS-INDO-FINETUNE-V2` sesuai langkah manual di laporan integrasi bagian 5.

3. **Path relatif `"backend/..."` di `config.py` salah resolve di dalam container.** `F5TTS_MODEL_PATH` di-set `"backend/models/..."` — path relatif ini di-resolve terhadap **current working directory proses saat runtime**, bukan terhadap lokasi file `config.py`. Kalau `WORKDIR` di Dockerfile bukan folder yang punya subfolder `backend/` persis (misal WORKDIR sudah `/app` dan isi `backend/` di-copy langsung ke `/app/` tanpa subfolder), path ini akan salah dan `os.path.exists()` selalu `False` → selalu fallback. **Cek dengan command nomor 2 di atas** (`pwd` + `ls`) untuk pastikan. Kalau ternyata salah, cara paling aman adalah pakai path absolut atau path relatif terhadap file config sendiri:
   ```python
   from pathlib import Path
   BASE_DIR = Path(__file__).resolve().parent.parent.parent  # sesuaikan jumlah .parent sampai ke root backend/
   F5TTS_MODEL_PATH: str = str(BASE_DIR / "models" / "F5-TTS-INDO-FINETUNE-V2" / "f5_tts_indo_v2.pt")
   ```

4. **Migrasi kolom DB belum dijalankan** (kalau poin 1 di atas gagal dengan error kolom tidak ada, bukan cuma `None`):
   ```bash
   docker exec -it heurix-backend python backend/scripts/migrate_add_tts_columns.py
   ```

### Setelah semua langkah di atas beres
Restart container, mulai sesi baru, dan **cek log HARUS muncul baris ini** (kalau tidak muncul, berarti masih belum ke-trigger):
```
[F5TTS] Loading model dari backend/models/F5-TTS-INDO-FINETUNE-V2/f5_tts_indo_v2.pt (device=cpu)...
[F5TTS] Model siap.
```

---

## Checklist Verifikasi Akhir

- [ ] Diamkan mic beberapa detik saat sesi jalan → transcript kosong, bukan "terima kasih menonton" atau kalimat halusinasi lain.
- [ ] Log timing (`[TIMING] LLM: ... | TTS: ...`) menunjukkan stage mana yang paling lambat di kalimat pertama — lampirkan hasilnya kalau masih lambat setelah fix blocking call, supaya bisa didiagnosis lebih lanjut (kemungkinan sisa: Groq API cold start).
- [ ] Log container menunjukkan `[F5TTS] Loading model...` → `[F5TTS] Model siap.` saat sesi dengan avatar F5TTS dimulai.
- [ ] Suara yang keluar terdengar mirip aksen `formal_male_reference.wav`, bukan suara `edge_tts` default (`id-ID-ArdiNeural`).
- [ ] WebSocket sesi LAIN (kalau ada 2 sesi paralel) tetap responsif (tidak nge-freeze) selagi salah satu sesi lagi proses Whisper/F5TTS — ini indikasi `asyncio.to_thread` sudah bekerja.

## Yang TIDAK Boleh Disentuh
- Guard `_guard_reference_audio()` di `speech.py` — jangan dilonggarkan/dihapus, itu constraint etika voice cloning yang sengaja ada.
- Mekanisme fallback otomatis ke `edge_tts` — tetap pertahankan sebagai safety net, jangan dihapus walau F5TTS sudah aktif (kalau suatu saat model corrupt/hilang, sesi interview tidak boleh mati total).
- `edge_tts` sebagai default engine untuk avatar yang belum dikonfigurasi F5TTS.
