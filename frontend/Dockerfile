FROM oven/bun:1.3.10-alpine AS builder

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package.json bun.lock svelte.config.js ./

COPY . .

RUN bun install --frozen-lockfile

RUN bunx svelte-kit sync

ARG PUBLIC_BACKEND_URL
ARG PUBLIC_BACKEND_WS
ENV PUBLIC_BACKEND_URL=$PUBLIC_BACKEND_URL
ENV PUBLIC_BACKEND_WS=$PUBLIC_BACKEND_WS

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