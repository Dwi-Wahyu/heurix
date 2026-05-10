# Gunakan image Bun resmi
FROM oven/bun:1.3.10-alpine AS builder

WORKDIR /app

# Tambahkan tools pembangunan (hanya untuk kompilasi library)
RUN apk add --no-cache python3 make g++

# Salin file package dan lockfile
COPY package.json bun.lock ./

COPY vite.config.ts ./

# Install dependencies
RUN bun install --frozen-lockfile

# Salin semua source code
COPY . .

# Tambahkan ini - deklarasi ARG sebelum digunakan
ARG PUBLIC_BACKEND_URL
ARG PUBLIC_BACKEND_WS

# Set sebagai ENV agar Vite bisa membacanya saat build
ENV PUBLIC_BACKEND_URL=$PUBLIC_BACKEND_URL
ENV PUBLIC_BACKEND_WS=$PUBLIC_BACKEND_WS

# Build aplikasi menggunakan adapter-bun
RUN bun run build

# --- Runtime Stage ---
FROM oven/bun:1.3.10-alpine

WORKDIR /app

# Hanya salin hasil build dan node_modules yang dibutuhkan
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Environment variables
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

# Jalankan dengan runtime Bun
CMD ["bun", "./build/index.js"]