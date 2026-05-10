# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PORT=5001

WORKDIR /app

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Buat user non-root
RUN useradd -m appuser

# Salin venv dari builder
COPY --from=builder /opt/venv /opt/venv

# Salin source code
COPY --chown=appuser:appuser . .

# Buat folder model
RUN mkdir -p /app/models && chown appuser:appuser /app/models

USER appuser

EXPOSE 5001

ENV WEB_CONCURRENCY=1

CMD ["sh", "-c", "gunicorn -w ${WEB_CONCURRENCY} -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5001 --timeout 120"]