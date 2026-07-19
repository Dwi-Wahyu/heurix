# Fix: WebSocket connection rejected during interview startup (`/ws/ws/{sessionId}` double path)

## Root cause

`frontend/src/routes/session/interview/+page.svelte` builds the WebSocket URL like this:

```js
// line 561-565
let wsUrl = PUBLIC_BACKEND_WS;
if (browser && window.location.protocol === 'https:' && wsUrl.startsWith('ws://')) {
	wsUrl = wsUrl.replace('ws://', 'wss://');
}
ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);
```

This code is correct **only if** `PUBLIC_BACKEND_WS` is a bare origin with no path
(e.g. `wss://heurix-api.dwiwahyu.my.id`), matching the value already set in the
project root `.env`:

```
PUBLIC_BACKEND_WS=wss://heurix-api.dwiwahyu.my.id
```

The problem: several other files in the repo document/pass a `PUBLIC_BACKEND_WS`
value that **already includes a trailing `/ws`**, e.g.:

- `docs/deployment.md` (manual build command example):
  `--build-arg PUBLIC_BACKEND_WS="wss://api.heurix.dwiwahyu.my.id/ws"`
- `docker-compose.example.yml`
- `frontend/ecosystem.config.cjs` (commented example)
- Stale baked build output: `frontend/.svelte-kit/output/server/chunks/public.js`
  and `frontend/build/server/chunks/public-*.js` currently contain a hardcoded
  `"wss://api.hiready.dwiwahyu.my.id/ws"` from an old manual build.

`PUBLIC_BACKEND_WS` is injected as a Docker **build ARG** (`frontend/Dockerfile`),
so it gets compiled directly into the SvelteKit JS bundle at image build time —
it is NOT read at runtime, and editing `.env` alone does not fix a running
container. If the currently deployed frontend image was ever built using one of
the `/ws`-suffixed examples above, the compiled bundle has
`wss://.../ws` baked in, and the code then appends its own `/ws/${sessionId}`,
producing the broken double path `wss://heurix-api.dwiwahyu.my.id/ws/ws/{sessionId}`.
Cloudflare/Uvicorn correctly reject this with 403 (no such WebSocket route
exists), which surfaces in the browser as:

```
WebSocket connection to 'wss://heurix-api.dwiwahyu.my.id/ws/ws/{sessionId}' failed
Koneksi terputus. Silakan muat ulang halaman.
```

Confirmed via direct testing: `wss://heurix-api.dwiwahyu.my.id/ws/{sessionId}`
(single `/ws`) returns a clean `101 Switching Protocols` through Cloudflare,
the tunnel, and Uvicorn. `/ws/ws/{sessionId}` (double) is rejected at the
Uvicorn/Starlette WebSocket router with a 403 before any app code runs.

## Task for the agent

### 1. Standardize the convention
Keep `PUBLIC_BACKEND_WS` as a **bare origin with no path** everywhere. Do not
change `frontend/src/routes/session/interview/+page.svelte` — its logic is
already correct for this convention.

### 2. Fix stale/incorrect examples and docs
In each file below, remove the trailing `/ws` from `PUBLIC_BACKEND_WS` values
so they match the root `.env` convention (`wss://heurix-api.dwiwahyu.my.id`,
no path suffix):

- `docs/deployment.md` — fix the `--build-arg PUBLIC_BACKEND_WS="...."` example
- `docker-compose.example.yml`
- `frontend/ecosystem.config.cjs` — fix the commented example value
- `frontend/.env.production` — if present and used for any build, remove `/ws` suffix
- `frontend/.env` (local dev file, currently `wss://192.168.1.43:8000`) — leave
  the host as-is if intentional for local dev, but confirm no `/ws` suffix
- `instruction/frontend-backend-integration.md` — fix example values
  (`PUBLIC_BACKEND_WS=ws://localhost:8000`, currently correct with no
  `/ws` — verify it stays that way after edits)

### 3. Rebuild the frontend image (not just recreate)
Because `PUBLIC_BACKEND_WS` is a build-time ARG, a config/env change alone does
not update a running container. Run:

```bash
cd ~/.secret/heurix/source-code
docker compose build frontend
docker compose up -d frontend
```

Confirm the root `.env` used for this build has:

```
PUBLIC_BACKEND_WS=wss://heurix-api.dwiwahyu.my.id
```

(no trailing `/ws`).

### 4. Verify the fix
After rebuild, confirm the compiled bundle no longer contains a `/ws` suffix
on `PUBLIC_BACKEND_WS`:

```bash
grep -r "PUBLIC_BACKEND_WS" frontend/.svelte-kit/output/server/chunks/public.js frontend/build/server/chunks/public-*.js
```

Expected output should show `wss://heurix-api.dwiwahyu.my.id` with **no**
trailing `/ws`.

Then confirm the real handshake works end-to-end:

```bash
curl -i -N --http1.1 \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  https://heurix-api.dwiwahyu.my.id/ws/test-session-id
```

Expected: `HTTP/1.1 101 Switching Protocols` followed by
`{"type":"ERROR","message":"Session not found"}` (expected, since
`test-session-id` is not a real session — this confirms the route matched).

Finally, start a real interview session from the browser UI and confirm the
"Koneksi terputus. Silakan muat ulang halaman." error no longer appears, and
DevTools → Network → WS shows a successful `101` for
`wss://heurix-api.dwiwahyu.my.id/ws/{real-session-id}`.

## Do not change
- `backend/app/api/websocket.py` — route `@router.websocket("/ws/{sessionId}")`
  is correct and requires no changes.
- `main.py` CORS/middleware config — not related to this bug.
- Cloudflare zone settings (WebSockets toggle, HTTP/2 to Origin, SSL/TLS mode,
  Bot Fight Mode) — all confirmed correctly configured during diagnosis; do
  not modify.
