FROM oven/bun:1.3.10-alpine

WORKDIR /app

# Install system dependencies jika diperlukan oleh driver DB
RUN apk add --no-cache python3 make g++ build-base libc6-compat


# Salin dependencies dan install
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Salin seluruh source code (agar skema, seeder, dan config terbaca)
COPY . .

ENV NODE_ENV=production

# Perintah default untuk menjalankan migrasi dan seeding
CMD ["sh", "-c", "bun run db:push && bun run db:seed-avatar && bun run db:seed-institution"]