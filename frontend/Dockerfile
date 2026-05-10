FROM oven/bun:1.3.10-alpine AS builder

# Tentukan folder kerja di container
WORKDIR /app

# Ambil build-args dari workflow
ARG PUBLIC_BACKEND_URL
ARG PUBLIC_BACKEND_WS

# Set sebagai ENV agar tersedia saat proses 'bun run build'
ENV PUBLIC_BACKEND_URL=$PUBLIC_BACKEND_URL
ENV PUBLIC_BACKEND_WS=$PUBLIC_BACKEND_WS

# 1. Salin file package saja dulu untuk efisiensi cache
COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile

# 2. Salin SELURUH isi folder frontend
# Ini termasuk svelte.config.js dan vite.config.ts
COPY . .

# 3. Sinkronisasi SvelteKit (Sangat Penting untuk Svelte 5 / SvelteKit terbaru)
# Perintah ini menghasilkan file index.html virtual dan manifest yang dibutuhkan Vite
RUN bunx svelte-kit sync

# 4. Jalankan build
RUN bun run build

# --- Runtime Stage ---
FROM oven/bun:1.3.10-alpine

WORKDIR /app

COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

CMD ["bun", "./build/index.js"]