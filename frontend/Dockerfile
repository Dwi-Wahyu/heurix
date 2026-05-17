FROM oven/bun:1.3.10-alpine AS builder

WORKDIR /app

# Install dependencies sistem
RUN apk add --no-cache python3 make g++ build-base libc6-compat

# 1. Pastikan build-args didefinisikan SEBELUM digunakan
ARG PUBLIC_BACKEND_URL
ARG PUBLIC_BACKEND_WS
ARG DATABASE_URL

# 2. Salin file manifest terlebih dahulu (Layer Caching)
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile --force

# 3. Salin SEMUA file (Penting: svelte.config.js & vite.config.ts harus ikut)
COPY . .

# 4. Set ENV tepat sebelum build (Vite butuh ini saat kompilasi)
ENV PUBLIC_BACKEND_URL=$PUBLIC_BACKEND_URL
ENV PUBLIC_BACKEND_WS=$PUBLIC_BACKEND_WS
ENV DATABASE_URL=$DATABASE_URL
ENV NODE_ENV=production

# 5. Jalankan Sync dan Build
# Tambahkan 'bun run' sebelum svelte-kit sync untuk memastikan path lokal terbaca
RUN bun run build

# --- Runtime Stage ---
FROM oven/bun:1.3.10-alpine

WORKDIR /app

# Ambil hasil build
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Environment Runtime
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

CMD ["bun", "./build/index.js"]