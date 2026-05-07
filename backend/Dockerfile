# ==========================================
# STAGE 1: Builder (Untuk Kompilasi)
# ==========================================
FROM python:3.12-slim AS builder

# Mencegah Python membuat file .pyc dan memastikan output log dikirim langsung ke terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies build (diperlukan untuk library yang butuh kompilasi C)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install virtual environment untuk mengisolasi dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip dan install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# ==========================================
# STAGE 2: Runtime (Image Akhir yang Ringan)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Salin hasil instalasi library dari stage builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies (ffmpeg dan libsndfile untuk project audio/big data)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Buat user non-root demi keamanan
RUN useradd -m appuser
USER appuser

# Salin seluruh source code ke dalam container
COPY --chown=appuser:appuser . .

# Buat folder model jika Anda menggunakan model machine learning (seperti Faster-Whisper)
RUN mkdir -p /app/models

# Ekspos port FastAPI
ENV PORT=5001
EXPOSE 5001

# Command Produksi: Menggunakan Gunicorn dengan Uvicorn Workers
# -w 4: Menjalankan 4 proses paralel (sesuaikan dengan core CPU hosting Anda)
# --timeout 120: Mengantisipasi proses Big Data yang mungkin memakan waktu lama
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:5001", "--timeout", "120"]