# Graph Report - source-code  (2026-08-03)

## Corpus Check
- 141 files · ~2,673,225 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1975 nodes · 4135 edges · 183 communities (116 shown, 67 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 380 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `259c6171`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- draco_encoder.js
- vision_wasm_internal.js
- vision_wasm_nosimd_internal.js
- fs
- draco_wasm_wrapper.js
- Session
- kh
- un
- ln
- ci
- xh
- Draco Decoder JS
- aq
- Path and Directory Management
- schema.ts
- $lib/FaceAnimator
- devDependencies
- auth.ts
- 2. Implemented Fixes & Changes
- dependencies
- Draco Geometry Decoders
- +page.svelte
- $lib/components/Header.svelte
- sj
- C++ Exception Handling
- WASM Memory Management
- fp
- vision_wasm_module_internal.js
- finish_and_report
- Project Documentation and Assets
- Draco Mesh Encoding
- Exception Info Metadata
- Exception Info Metadata
- WASM Runtime Lifecycle
- Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru
- PWA State Management
- Binary Data Utilities
- File I/O Operations
- WASM Binary Instantiation
- abort
- scripts
- Frontend Chart Dependencies
- Runtime Initialization Callbacks
- Database Seed Entrypoint
- Institution Data Seeding
- 2. Rincian Perubahan & Implementasi Kode
- Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)
- 2. Comprehensive Breakdown of Fixes
- WebGPU Buffer Entries
- WebGPU Buffer Entries
- get_speech_service_for_avatar
- Auth Table Migrations
- createWasm
- Browser Data Loading
- UTF8 String Encoding
- WebGPU Blend States
- WebGPU Vertex Attributes
- WebGPU Blend States
- WebGPU Vertex Attributes
- schema.ts
- Backend Configuration Settings
- Audio Transcription Service
- Avatar Seeding Script
- _load_model
- Implementation Log — Adaptive Personalization Engine (APE)
- TTY IOCTL Syscalls
- WebGPU Render Pass
- TTY IOCTL Syscalls
- WebGPU Render Pass
- Heurix — Audit & Implementasi Adaptive Personalization Engine (APE)
- Session Report Migrations
- SvelteKit Type Definitions
- index.ts
- $app/navigation
- Fix: Client-side memory leak / lag causing laptop hang on interview page
- ej
- Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)
- kp
- Low-level Write Operations
- Low-level Write Operations
- Svelte Form Handling
- Task Schema Migration
- Institution Schema Migration
- Avatar Schema Migration
- Report Schema Migration
- Institution Schema Update
- Avatar Schema Update
- Avatar Schema Update
- Groq SDK Integration
- Object Pointer Wrapping
- ji
- ha
- ModuleFactory
- xd
- Implementation Report: Avatar Hassan Camera Config Adjustment
- File Stream Closing
- Async Callback Handling
- Exit Status Constructor
- Wire Type Conversion
- Character Input Reading
- Canvas Fullscreen Management
- Initialization and Timing
- Graphics Stencil State
- Filesystem Mounting
- Execution Lifecycle
- Type Registration
- Filesystem Statistics
- File Synchronization
- Return Value Handling
- Process Exit Status
- Memory Pointer Conversion
- Character Input Reading
- Canvas Fullscreen Management
- Initialization and Timing
- Graphics Stencil State
- Filesystem Mounting
- Execution Lifecycle
- Type Registration
- Filesystem Statistics
- Svelte Configuration
- Task for the agent
- SpeechService
- package.json
- migration_ape.sql
- 0010_fair_network.sql
- emscripten_realloc_buffer
- vj
- AGENTS.md
- yc
- Backend Step Documentation
- Backend Readme
- Python Dependencies
- Frontend AI Documentation
- Frontend Project Context
- Frontend Readme
- Frontend Entry HTML
- Emotion Presets
- 3D Model Documentation
- Face Animation Instructions
- WebAssembly Documentation
- Lucide Icon Library
- jl
- c
- ve
- postgres
- prettier
- prettier-plugin-tailwindcss
- svelte
- svelte-adapter-bun
- tailwindcss
- @tailwindcss/typography
- @tailwindcss/vite
- @types/node
- @types/three
- typescript

## God Nodes (most connected - your core abstractions)
1. `fs` - 183 edges
2. `ln()` - 159 edges
3. `ha()` - 156 edges
4. `aq()` - 135 edges
5. `sj()` - 87 edges
6. `kh()` - 60 edges
7. `un()` - 36 edges
8. `I()` - 34 edges
9. `im()` - 29 edges
10. `path` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Frontend-Backend Integration Guide` --references--> `$lib/FaceAnimator`  [EXTRACTED]
  instruction/frontend-backend-integration.md → frontend/src/lib/FaceAnimator.ts
- `3D Avatar Model Optimization Guide` --references--> `$lib/FaceAnimator`  [EXTRACTED]
  instruction/model-optimization.md → frontend/src/lib/FaceAnimator.ts
- `Frontend-Backend Integration Guide` --references--> `$lib/lipSync`  [EXTRACTED]
  instruction/frontend-backend-integration.md → frontend/src/lib/lipSync.ts
- `getPath()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `getStreamChecked()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Heurix System Architecture** — heurix_db, heurix_backend, heurix_frontend, heurix_migrator [EXTRACTED 1.00]
- **AI Interview Simulation Flow** — interview_agent, face_animator, heurix_backend, heurix_frontend [INFERRED 0.85]
- **Avatar Animation & Lip-Sync System** — frontend_src_lib_faceanimator, frontend_src_lib_lipsync, instruction_viseme, frontend_static_face_professional_man_instruction [EXTRACTED 1.00]
- **Interview Session Logic & Flow** — backend_app_services_brain, backend_app_api_websocket, instruction_implementasi_alur_percakapan [EXTRACTED 1.00]

## Communities (183 total, 67 thin omitted)

### Community 0 - "draco_encoder.js"
Cohesion: 0.01
Nodes (34): $a(), ak(), demangle(), demangleAll(), fo(), ij(), ik(), iq() (+26 more)

### Community 1 - "vision_wasm_internal.js"
Cohesion: 0.01
Nodes (25): createDefaultDirectories(), doChown(), doTruncate(), _fd_seek(), findObject(), fstat(), getPath(), getStreamChecked() (+17 more)

### Community 2 - "vision_wasm_nosimd_internal.js"
Cohesion: 0.02
Nodes (23): createDefaultDirectories(), createNode(), fchown(), getStreamChecked(), RFC-2279, RFC-3629, lchown(), llseek() (+15 more)

### Community 3 - "fs"
Cohesion: 0.02
Nodes (116): ___syscall140(), ___syscall6(), chdir(), chmod(), chown(), create(), createDefaultDevices(), createNode() (+108 more)

### Community 4 - "draco_wasm_wrapper.js"
Cohesion: 0.06
Nodes (30): kd(), lh(), mg(), od(), qb(), ul(), vn(), ye() (+22 more)

### Community 5 - "Session"
Cohesion: 0.06
Nodes (75): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+67 more)

### Community 6 - "kh"
Cohesion: 0.18
Nodes (31): ag(), ce(), de(), ee(), eg(), _f(), fe(), ge() (+23 more)

### Community 7 - "un"
Cohesion: 0.14
Nodes (25): _b(), bk(), Ec(), ei(), eq(), Fc(), gq(), hn() (+17 more)

### Community 8 - "ln"
Cohesion: 0.08
Nodes (44): ah(), ai(), aj(), bf(), bi(), cf(), cg(), ch() (+36 more)

### Community 9 - "ci"
Cohesion: 0.13
Nodes (37): af(), bh(), bq(), ci(), dd(), dg(), dj(), _e() (+29 more)

### Community 10 - "xh"
Cohesion: 0.14
Nodes (14): bn(), dm(), fl(), _g(), gl(), ip(), nj(), pg() (+6 more)

### Community 11 - "Draco Decoder JS"
Cohesion: 0.08
Nodes (10): addRunDependency(), createWasm(), ensureString(), intArrayFromString(), l(), lengthBytesUTF8(), p(), stringToUTF8Array() (+2 more)

### Community 12 - "aq"
Cohesion: 0.25
Nodes (33): ab(), Ae(), aq(), bb(), be(), cb(), _d(), db() (+25 more)

### Community 13 - "Path and Directory Management"
Cohesion: 0.07
Nodes (30): analyzePath(), calculateAt(), createDataFile(), createDevice(), createFile(), createPath(), lookupPath(), mkdirTree() (+22 more)

### Community 14 - "schema.ts"
Cohesion: 0.08
Nodes (27): account, accountRelations, session, sessionRelations, user, userRelations, verification, difficultyEnum (+19 more)

### Community 15 - "$lib/FaceAnimator"
Cohesion: 0.15
Nodes (17): $lib/autoBlink, $lib/emotionPresets, EMOTIONS, $lib/FaceAnimator, FaceAnimator, $lib/lipSync, b64toBlob(), speakWithBackend() (+9 more)

### Community 16 - "devDependencies"
Cohesion: 0.08
Nodes (25): @better-auth/cli, drizzle-kit, drizzle-orm, @faker-js/faker, devDependencies, @better-auth/cli, drizzle-kit, drizzle-orm (+17 more)

### Community 17 - "auth.ts"
Cohesion: 0.13
Nodes (6): $lib/auth-client, authClient, auth, GET, POST, actions

### Community 18 - "2. Implemented Fixes & Changes"
Cohesion: 0.17
Nodes (11): 1. Executive Summary, 2. Implemented Fixes & Changes, 3. Summary of Modified Files, 4. Verification & Testing Results, 5. Conclusion, FIX 1: Decouple Auto-send from Web Speech API (VAD Implementation), FIX 2: WebSocket Heartbeat (Ping/Pong Keepalive), FIX 3: Natural Spoken TTS via Prompt Engineering (+3 more)

### Community 19 - "dependencies"
Cohesion: 0.09
Nodes (23): better-auth, @better-auth/core, face-api.js, groq-sdk, @mediapipe/tasks-vision, dependencies, better-auth, @better-auth/core (+15 more)

### Community 20 - "Draco Geometry Decoders"
Cohesion: 0.10
Nodes (20): AttributeOctahedronTransform(), AttributeQuantizationTransform(), AttributeTransformData(), Decoder(), DecoderBuffer(), destroy(), DracoFloat32Array(), DracoInt16Array() (+12 more)

### Community 21 - "+page.svelte"
Cohesion: 0.18
Nodes (8): three/examples/jsm/loaders/DRACOLoader.js, $app/environment, $lib/avatarCache, cache, three/examples/jsm/loaders/GLTFLoader.js, three/examples/jsm/libs/meshopt_decoder.module.js, $env/static/public, @mediapipe/tasks-vision

### Community 22 - "$lib/components/Header.svelte"
Cohesion: 0.17
Nodes (9): $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $lib/components/Sidebar.svelte, $lib/sidebar.svelte, sidebarState, string, $lib/assets/login-art.png?enhanced, $lib/assets/logo.png?enhanced (+1 more)

### Community 23 - "sj"
Cohesion: 0.17
Nodes (23): ad(), bd(), _c(), cd(), fd(), gd(), Hc(), hd() (+15 more)

### Community 25 - "WASM Memory Management"
Cohesion: 0.15
Nodes (17): alignUp(), allocate(), assert(), ccall(), dynamicAlloc(), enlargeMemory(), getCFunc(), getNativeTypeSize() (+9 more)

### Community 26 - "fp"
Cohesion: 0.13
Nodes (16): am(), dl(), eh(), fp(), hj(), hm(), il(), jj() (+8 more)

### Community 27 - "vision_wasm_module_internal.js"
Cohesion: 0.12
Nodes (16): RFC-2279, RFC-3629, NOTE: In our implementation, st_blocks = Math.ceil(st_size/st_blksize),, NOTE: This is also used as the process return code in shell environments, TODO: check for O_SEARCH? (== search for dir only), NOTE: None of the defaults here are true. We're just returning safe and, TODO: Use mozResponseArrayBuffer, responseStream, etc. if available., TODO: Due to Closure regression https://github.com/google/closure-compiler/issue (+8 more)

### Community 28 - "finish_and_report"
Cohesion: 0.07
Nodes (64): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+56 more)

### Community 29 - "Project Documentation and Assets"
Cohesion: 0.20
Nodes (12): backend/INITIAL.md, docs/models/3d/boy-character.md, FaceAnimator, frontend/docs/database-schema.md, frontend/PRD.md, Heurix Backend (FastAPI), Heurix Database (Postgres), Heurix Frontend (SvelteKit) (+4 more)

### Community 30 - "Draco Mesh Encoding"
Cohesion: 0.14
Nodes (14): castObject(), destroy(), DracoInt8Array(), Encoder(), GeometryAttribute(), getCache(), Mesh(), MeshBuilder() (+6 more)

### Community 33 - "WASM Runtime Lifecycle"
Cohesion: 0.20
Nodes (10): addOnPostRun(), addOnPreRun(), callRuntimeCallbacks(), ensureInitRuntime(), exit(), exitRuntime(), postRun(), preMain() (+2 more)

### Community 34 - "Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru"
Cohesion: 0.12
Nodes (15): 10. Task 7 — Preload model saat startup (`main.py`), 11. Task 8 — Script konfigurasi avatar (`scripts/set_avatar_voice_config.py`), 12. Catatan Performa — WAJIB dikomunikasikan ke user, jangan silent, 13. Verification Checklist (jalankan setelah semua task selesai), 1. Executive Summary, 2. Prasyarat Manual (dilakukan user, bukan agent), 3. File yang Akan Diubah/Ditambah, 4. Task 1 — Dependencies (+7 more)

### Community 35 - "PWA State Management"
Cohesion: 0.25
Nodes (4): $lib/pwa.svelte, pwaState, $lib/assets/favicon.svg, ./layout.css

### Community 36 - "Binary Data Utilities"
Cohesion: 0.25
Nodes (8): abort(), assert(), getBinary(), getBinaryPromise(), intArrayFromBase64(), isDataURI(), isFileURI(), tryParseAsDataURI()

### Community 37 - "File I/O Operations"
Cohesion: 0.25
Nodes (8): abort(), assert(), createLazyFile(), forceLoadFile(), getMouseWheelDelta(), position(), readFile(), writeFile()

### Community 38 - "WASM Binary Instantiation"
Cohesion: 0.25
Nodes (8): createWasm(), findWasmBinary(), getBinarySync(), getWasmBinary(), getWasmImports(), instantiateArrayBuffer(), instantiateAsync(), locateFile()

### Community 39 - "abort"
Cohesion: 0.25
Nodes (8): abort(), assert(), createLazyFile(), forceLoadFile(), getMouseWheelDelta(), position(), readFile(), writeFile()

### Community 40 - "scripts"
Cohesion: 0.12
Nodes (16): scripts, auth:schema, build, check, check:watch, db:generate, db:migrate, db:push (+8 more)

### Community 41 - "Frontend Chart Dependencies"
Cohesion: 0.25
Nodes (7): dependencies, chart.js, lucide-svelte, svelte-chartjs, chart.js, lucide-svelte, svelte-chartjs

### Community 42 - "Runtime Initialization Callbacks"
Cohesion: 0.29
Nodes (7): addOnPostRun(), addOnPreRun(), callRuntimeCallbacks(), initRuntime(), postRun(), preRun(), run()

### Community 43 - "Database Seed Entrypoint"
Cohesion: 0.33
Nodes (4): auth, client, db, faker

### Community 44 - "Institution Data Seeding"
Cohesion: 0.33
Nodes (4): client, db, institutions, positionsByInstitution

### Community 45 - "2. Rincian Perubahan & Implementasi Kode"
Cohesion: 0.14
Nodes (13): 1. Ringkasan Eksekutif, 2. Rincian Perubahan & Implementasi Kode, 3. Evaluasi Constraint & Keamanan Etis Voice Cloning, 4. Hasil Pengujian Integrasi (`backend/scripts/test_f5tts_integration.py`), 5. Rekomendasi Performa & Catatan Deployment, A. Dependencies & Dockerfile, B. Konfigurasi Sistem (`backend/app/core/config.py`), C. Skema Database & Migrasi (`backend/app/models/domain.py` & `backend/scripts/migrate_add_tts_columns.py`) (+5 more)

### Community 46 - "Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)"
Cohesion: 0.25
Nodes (7): FIX 1 — Decouple auto-send dari Web Speech API (fix Brave, tanpa merusak Chrome), FIX 2 — WebSocket heartbeat (ping/pong) untuk cegah idle-disconnect di cloudflared tunnel, FIX 3 — Suara AI lebih natural (prompt engineering, BUKAN SSML), FIX 4 — AI harus jawab pertanyaan kandidat di fase closing/farewell, FIX 5 — Persingkat kalimat yang digenerate AI, Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length), Verification checklist (setelah semua fix diterapkan)

### Community 47 - "2. Comprehensive Breakdown of Fixes"
Cohesion: 0.18
Nodes (10): 1. Overview & Objectives, 2. Comprehensive Breakdown of Fixes, 3. Verification & Compliance Matrix, 4. Conclusion, FIX 1: Voice Activity Detection (VAD) Auto-Send Decoupling, FIX 2: WebSocket Heartbeat Ping/Pong Keepalive, FIX 3: Natural AI Voice Prompting (No SSML), FIX 4: Farewell Phase Q&A Handling (+2 more)

### Community 48 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 49 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 50 - "get_speech_service_for_avatar"
Cohesion: 0.15
Nodes (14): _extract_visemes(), F5TTSSpeechService, get_speech_service_for_avatar(), _guard_reference_audio(), Factory: pilih engine berdasarkan kolom tts_engine di avatar.     Fallback aman, Ekstrak RMS envelope untuk viseme dari raw audio bytes (format apa pun yang didu, Engine default: edge_tts (cloud, stateless, tanpa voice cloning)., Engine voice cloning. Butuh ref_audio_path + ref_text per avatar (BUKAN global, (+6 more)

### Community 51 - "Auth Table Migrations"
Cohesion: 0.40
Nodes (4): "account", "session", "user", "verification"

### Community 52 - "createWasm"
Cohesion: 0.25
Nodes (8): createWasm(), findWasmBinary(), getBinarySync(), getWasmBinary(), getWasmImports(), instantiateArrayBuffer(), instantiateAsync(), locateFile()

### Community 53 - "Browser Data Loading"
Cohesion: 0.40
Nodes (5): doBrowserLoad(), intArrayFromBase64(), isDataURI(), tryParseAsDataURI(), useRequest()

### Community 54 - "UTF8 String Encoding"
Cohesion: 0.40
Nodes (5): ensureString(), intArrayFromString(), lengthBytesUTF8(), stringToUTF8(), stringToUTF8Array()

### Community 55 - "WebGPU Blend States"
Cohesion: 0.40
Nodes (5): makeBlendComponent(), makeBlendState(), makeColorState(), makeColorStates(), makeFragmentState()

### Community 56 - "WebGPU Vertex Attributes"
Cohesion: 0.40
Nodes (5): makeVertexAttribute(), makeVertexAttributes(), makeVertexBuffer(), makeVertexBuffers(), makeVertexState()

### Community 57 - "WebGPU Blend States"
Cohesion: 0.40
Nodes (5): makeBlendComponent(), makeBlendState(), makeColorState(), makeColorStates(), makeFragmentState()

### Community 58 - "WebGPU Vertex Attributes"
Cohesion: 0.40
Nodes (5): makeVertexAttribute(), makeVertexAttributes(), makeVertexBuffer(), makeVertexBuffers(), makeVertexState()

### Community 59 - "schema.ts"
Cohesion: 0.09
Nodes (21): difficultyEnum, interviewAvatar, interviewAvatarRelations, interviewSession, interviewSessionRelations, interviewTrackEnum, masterInstitution, masterInstitutionRelations (+13 more)

### Community 60 - "Backend Configuration Settings"
Cohesion: 0.50
Nodes (3): Config, Settings, BaseSettings

### Community 63 - "_load_model"
Cohesion: 0.38
Nodes (6): is_available(), _load_model(), Lazy-load F5-TTS model + vocoder sekali saja (thread-safe)., Cek apakah model bisa/sudah di-load, tanpa melempar exception ke caller., Generate audio dengan voice cloning dari ref_audio_path.     Return: (wav_bytes,, synthesize()

### Community 64 - "Implementation Log — Adaptive Personalization Engine (APE)"
Cohesion: 0.29
Nodes (6): 1. Files Modified/Added, 2. Database Migration Status, 3. Post-Implementation Protocol, Backend (`backend/`), Frontend (`frontend/src/`), Implementation Log — Adaptive Personalization Engine (APE)

### Community 65 - "TTY IOCTL Syscalls"
Cohesion: 0.50
Nodes (4): ioctl_tcgets(), ioctl_tcsets(), ioctl_tiocgwinsz(), ___syscall_ioctl()

### Community 66 - "WebGPU Render Pass"
Cohesion: 0.50
Nodes (4): makeColorAttachment(), makeColorAttachments(), makeDepthStencilAttachment(), makeRenderPassDescriptor()

### Community 67 - "TTY IOCTL Syscalls"
Cohesion: 0.50
Nodes (4): ioctl_tcgets(), ioctl_tcsets(), ioctl_tiocgwinsz(), ___syscall_ioctl()

### Community 68 - "WebGPU Render Pass"
Cohesion: 0.50
Nodes (4): makeColorAttachment(), makeColorAttachments(), makeDepthStencilAttachment(), makeRenderPassDescriptor()

### Community 69 - "Heurix — Audit & Implementasi Adaptive Personalization Engine (APE)"
Cohesion: 0.14
Nodes (13): 1.1 Apa yang bisa diaudit secara statis vs. yang butuh runtime, 1.2 Audit Database & Skema (4.2), 1.3 Temuan arsitektur penting (memengaruhi cara APE diimplementasikan), 1. Laporan Audit, 2. Daftar File yang Diubah, 3. Migration Script, 4.1 `speech.py` — parameter speed/pitch, 4.2 `brain.py` — SRI, pressure level, weakness tags, scenario config (+5 more)

### Community 72 - "index.ts"
Cohesion: 0.23
Nodes (3): client, db, userProfile

### Community 73 - "$app/navigation"
Cohesion: 0.19
Nodes (6): $lib/auth-client, $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $app/navigation, $lib/components/Sidebar.svelte, svelte/transition

### Community 74 - "Fix: Client-side memory leak / lag causing laptop hang on interview page"
Cohesion: 0.17
Nodes (11): 1. Lift `renderer`, `scene`, `camera`, and the `ResizeObserver` to component scope, 2. Capture and cancel the animation frame loop, 3. Extend `onDestroy` with full cleanup, 4. Optional (recommended) performance improvements, same file, Do not change, File, Fix: Client-side memory leak / lag causing laptop hang on interview page, Root cause (+3 more)

### Community 75 - "ej"
Cohesion: 0.33
Nodes (6): ej(), om(), _p(), pp(), qo(), sn()

### Community 76 - "Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)"
Cohesion: 0.25
Nodes (7): FIX 1 — Decouple auto-send dari Web Speech API (fix Brave, tanpa merusak Chrome), FIX 2 — WebSocket heartbeat (ping/pong) untuk cegah idle-disconnect di cloudflared tunnel, FIX 3 — Suara AI lebih natural (prompt engineering, BUKAN SSML), FIX 4 — AI harus jawab pertanyaan kandidat di fase closing/farewell, FIX 5 — Persingkat kalimat yang digenerate AI, Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length), Verification checklist (setelah semua fix diterapkan)

### Community 77 - "kp"
Cohesion: 0.33
Nodes (6): bp(), eo(), jk(), jn(), kp(), mp()

### Community 78 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 79 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 93 - "ji"
Cohesion: 0.40
Nodes (5): ao(), dp(), io(), ji(), op()

### Community 94 - "ha"
Cohesion: 0.10
Nodes (40): ha(), Ac(), Bc(), bg(), bj(), Cc(), fg(), gf() (+32 more)

### Community 95 - "ModuleFactory"
Cohesion: 0.13
Nodes (14): handle(), dh(), gp(), hl(), lm(), mj(), ml(), nm() (+6 more)

### Community 96 - "xd"
Cohesion: 0.67
Nodes (3): dq(), xd(), yo()

### Community 97 - "Implementation Report: Avatar Hassan Camera Config Adjustment"
Cohesion: 0.33
Nodes (5): 1. Issue Description, 2. Implemented Fix, 3. Results & Verification, Implementation Report: Avatar Hassan Camera Config Adjustment, Root Cause

### Community 123 - "Task for the agent"
Cohesion: 0.22
Nodes (8): 1. Standardize the convention, 2. Fix stale/incorrect examples and docs, 3. Rebuild the frontend image (not just recreate), 4. Verify the fix, Do not change, Fix: WebSocket connection rejected during interview startup (`/ws/ws/{sessionId}` double path), Root cause, Task for the agent

### Community 124 - "SpeechService"
Cohesion: 0.33
Nodes (4): Menghasilkan audio (base64) dan data viseme (amplitude envelope).          speed, Konversi rasio (1.0 = normal) ke string persen bertanda yang dipahami     edge_t, SpeechService, _to_percent_string()

### Community 125 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 126 - "migration_ape.sql"
Cohesion: 0.50
Nodes (3): interview_session, session_report, user_profile

### Community 127 - "0010_fair_network.sql"
Cohesion: 0.50
Nodes (3): "interview_session", "session_report", "user_profile"

### Community 128 - "emscripten_realloc_buffer"
Cohesion: 0.50
Nodes (4): emscripten_realloc_buffer(), _emscripten_resize_heap(), getHeapMax(), updateMemoryViews()

### Community 129 - "vj"
Cohesion: 0.67
Nodes (3): ll(), vj(), zl()

### Community 132 - "yc"
Cohesion: 0.67
Nodes (3): oq(), xn(), yc()

### Community 160 - "jl"
Cohesion: 0.67
Nodes (3): ef(), jl(), yj()

### Community 162 - "c"
Cohesion: 0.08
Nodes (29): c(), an(), bm(), bo(), cm(), en(), fn(), go() (+21 more)

## Knowledge Gaps
- **268 isolated node(s):** `Config`, `user_profile`, `interview_session`, `session_report`, `interviewTrackEnum` (+263 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fs` connect `fs` to `vision_wasm_internal.js`, `vision_wasm_nosimd_internal.js`, `Path and Directory Management`, `dependencies`, `File I/O Operations`, `abort`, `TTY IOCTL Syscalls`, `TTY IOCTL Syscalls`, `Low-level Write Operations`, `Low-level Write Operations`, `ModuleFactory`, `File Stream Closing`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`, `File Synchronization`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`?**
  _High betweenness centrality (0.282) - this node is a cross-community bridge._
- **Why does `___syscall140()` connect `fs` to `draco_encoder.js`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `___syscall6()` connect `fs` to `draco_encoder.js`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 153 inferred relationships involving `ha()` (e.g. with `Ac()` and `ad()`) actually correct?**
  _`ha()` has 153 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `user_profile`, `interview_session` to the rest of the system?**
  _268 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `draco_encoder.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013863134657836645 - nodes in this community are weakly interconnected._
- **Should `vision_wasm_internal.js` be split into smaller, more focused modules?**
  _Cohesion score 0.014925373134328358 - nodes in this community are weakly interconnected._