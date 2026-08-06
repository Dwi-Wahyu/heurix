# Graph Report - /home/dwiwahyuilahi/Kuliah/Gemastik/source-code  (2026-08-06)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1332 nodes · 1862 edges · 143 communities (88 shown, 55 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c3652c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- brain.py
- vision_wasm_internal.js
- vision_wasm_nosimd_internal.js
- fs
- Instruksi: Hapus Fitur 3D (Three.js) dari Heurix
- Session
- Laporan Pelaksanaan: Penghapusan Fitur 3D (Three.js) dari Heurix
- $lib/lipSync
- 3D Avatar Model Optimization Guide
- Instruksi Lanjutan: Ganti Avatar 2D dengan Audio Bar Visualizer
- 2. Rincian Perubahan File
- utils.ts
- +page.svelte
- Path and Directory Management
- schema.ts
- visemeMap.ts
- devDependencies
- auth.ts
- 2. Implemented Fixes & Changes
- scripts
- Instruksi Perbaikan: Halusinasi Whisper, Latensi Kalimat Pertama, & Voice Cloning F5TTS Belum Aktif
- +page.svelte
- $lib/components/Header.svelte
- vision_wasm_module_internal.js
- finish_and_report
- Project Documentation and Assets
- Exception Info Metadata
- Exception Info Metadata
- Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru
- PWA State Management
- File I/O Operations
- WASM Binary Instantiation
- abort
- Frontend Chart Dependencies
- Database Seed Entrypoint
- Institution Data Seeding
- 2. Rincian Perubahan & Implementasi Kode
- Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)
- 2. Comprehensive Breakdown of Fixes
- WebGPU Buffer Entries
- WebGPU Buffer Entries
- get_speech_service_for_avatar
- Auth Table Migrations
- WebGPU Blend States
- WebGPU Vertex Attributes
- WebGPU Blend States
- WebGPU Vertex Attributes
- schema.ts
- config.py
- Audio Transcription Service
- Avatar Seeding Script
- f5tts_service.py
- Implementation Log — Adaptive Personalization Engine (APE)
- TTY IOCTL Syscalls
- WebGPU Render Pass
- TTY IOCTL Syscalls
- WebGPU Render Pass
- Heurix — Audit & Implementasi Adaptive Personalization Engine (APE)
- Session Report Migrations
- SvelteKit Type Definitions
- index.ts
- +page.svelte
- Fix: Client-side memory leak / lag causing laptop hang on interview page
- Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)
- Low-level Write Operations
- Low-level Write Operations
- Task Schema Migration
- Institution Schema Migration
- Avatar Schema Migration
- Report Schema Migration
- Institution Schema Update
- Avatar Schema Update
- Avatar Schema Update
- Groq SDK Integration
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
- migration_ape.sql
- 0010_fair_network.sql
- AGENTS.md
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

## God Nodes (most connected - your core abstractions)
1. `fs` - 181 edges
2. `path` - 29 edges
3. `Session` - 20 edges
4. `send_next_question_stream()` - 17 edges
5. `finish_and_report()` - 16 edges
6. `finish_and_report()` - 16 edges
7. `send_next_question_stream()` - 16 edges
8. `scripts` - 16 edges
9. `Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru` - 15 edges
10. `"session_turn"` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Frontend-Backend Integration Guide` --references--> `$lib/lipSync`  [EXTRACTED]
  instruction/frontend-backend-integration.md → frontend/src/lib/lipSync.ts
- `open()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `createNode()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `hashAddNode()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `hashRemoveNode()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Heurix System Architecture** — heurix_db, heurix_backend, heurix_frontend, heurix_migrator [EXTRACTED 1.00]
- **AI Interview Simulation Flow** — interview_agent, face_animator, heurix_backend, heurix_frontend [INFERRED 0.85]
- **Interview Session Logic & Flow** — backend_app_services_brain, backend_app_api_websocket, instruction_implementasi_alur_percakapan [EXTRACTED 1.00]

## Communities (143 total, 55 thin omitted)

### Community 0 - "brain.py"
Cohesion: 0.06
Nodes (57): build_chat_history(), build_system_prompt(), calculate_sri(), compute_pressure_level(), extract_weakness_tags(), generate_next_turn(), generate_next_turn_stream(), get_phase() (+49 more)

### Community 1 - "vision_wasm_internal.js"
Cohesion: 0.02
Nodes (24): chmod(), createNode(), createStandardStreams(), doChmod(), fchmod(), hashAddNode(), hashRemoveNode(), RFC-2279 (+16 more)

### Community 2 - "vision_wasm_nosimd_internal.js"
Cohesion: 0.02
Nodes (16): RFC-2279, RFC-3629, NOTE: In our implementation, st_blocks = Math.ceil(st_size/st_blksize),, NOTE: This is also used as the process return code in shell environments, TODO: check for O_SEARCH? (== search for dir only), NOTE: None of the defaults here are true. We're just returning safe and, TODO: Use mozResponseArrayBuffer, responseStream, etc. if available., TODO: Due to Closure regression https://github.com/google/closure-compiler/issue (+8 more)

### Community 3 - "fs"
Cohesion: 0.02
Nodes (122): chdir(), chown(), create(), createDefaultDevices(), createDefaultDirectories(), createSpecialDirectories(), createStream(), destroyNode() (+114 more)

### Community 4 - "Instruksi: Hapus Fitur 3D (Three.js) dari Heurix"
Cohesion: 0.15
Nodes (12): ⚠️ Catatan Penting Sebelum Mulai, Checklist Verifikasi Setelah Refactor, Instruksi: Hapus Fitur 3D (Three.js) dari Heurix, LANGKAH BACKEND, LANGKAH FRONTEND, Peta Dependensi (baca dulu), Step 1 — Refactor `lipSync.ts` (lepas ketergantungan ke `FaceAnimator`), Step 2 — Refactor `autoBlink.ts` (+4 more)

### Community 5 - "Session"
Cohesion: 0.10
Nodes (45): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+37 more)

### Community 6 - "Laporan Pelaksanaan: Penghapusan Fitur 3D (Three.js) dari Heurix"
Cohesion: 0.25
Nodes (7): 1. Ringkasan Eksekutif, 2. Rincian Perubahan Kode & File, 3. Hasil Verifikasi & Build, 4. Langkah Protokol Pasca-Implementasi (POST IMPLEMENTATION PROTOCOL), A. File yang Dihapus (Murni 3D), B. Refactoring & Update File, Laporan Pelaksanaan: Penghapusan Fitur 3D (Three.js) dari Heurix

### Community 7 - "$lib/lipSync"
Cohesion: 0.31
Nodes (7): $lib/lipSync, b64toBlob(), getOutputAnalyser(), speakWithBackend(), unlockAudio(), $lib/OutputBarVisualizer.svelte, Frontend-Backend Integration Guide

### Community 9 - "Instruksi Lanjutan: Ganti Avatar 2D dengan Audio Bar Visualizer"
Cohesion: 0.20
Nodes (9): ⚠️ 5 Hal Penting Soal Kompatibilitas (WAJIB dibaca dulu), Checklist Verifikasi, Instruksi Lanjutan: Ganti Avatar 2D dengan Audio Bar Visualizer, Step 1 — Copy file library, Step 2 — Perluas `lipSync.ts`: tambah `AnalyserNode` + sederhanakan `speakWithBackend`, Step 3 — Buat komponen wrapper visualizer (opsional tapi direkomendasikan), Step 4 — Update `session/interview/+page.svelte`, Step 5 — Bersihkan sisa avatar 2D yang sudah tidak dipakai (opsional, tapi disarankan sesuai permintaan "tidak perlu munculkan gambar avatar sama sekali") (+1 more)

### Community 10 - "2. Rincian Perubahan File"
Cohesion: 0.20
Nodes (9): 1. Ringkasan Eksekutif, 2. Rincian Perubahan File, 3. Hasil Verifikasi & Build, 4. Protokol Pasca-Implementasi (POST IMPLEMENTATION PROTOCOL), A. Komponen Visualizer Baru, B. Refactoring `lipSync.ts`, C. Update `session/interview/+page.svelte`, D. Pembersihan File Unused (+1 more)

### Community 13 - "Path and Directory Management"
Cohesion: 0.07
Nodes (30): analyzePath(), calculateAt(), createDataFile(), createDevice(), createFile(), createPath(), lookupPath(), mkdirTree() (+22 more)

### Community 14 - "schema.ts"
Cohesion: 0.08
Nodes (27): account, accountRelations, session, sessionRelations, user, userRelations, verification, difficultyEnum (+19 more)

### Community 15 - "visemeMap.ts"
Cohesion: 0.38
Nodes (4): EMOTIONS, ShapeKeyWeights, VISEME_MAP, VISEME_SHAPE_KEYS

### Community 16 - "devDependencies"
Cohesion: 0.04
Nodes (47): @better-auth/cli, drizzle-kit, drizzle-orm, @faker-js/faker, devDependencies, @better-auth/cli, drizzle-kit, drizzle-orm (+39 more)

### Community 17 - "auth.ts"
Cohesion: 0.13
Nodes (6): $lib/auth-client, authClient, auth, GET, POST, actions

### Community 18 - "2. Implemented Fixes & Changes"
Cohesion: 0.17
Nodes (11): 1. Executive Summary, 2. Implemented Fixes & Changes, 3. Summary of Modified Files, 4. Verification & Testing Results, 5. Conclusion, FIX 1: Decouple Auto-send from Web Speech API (VAD Implementation), FIX 2: WebSocket Heartbeat (Ping/Pong Keepalive), FIX 3: Natural Spoken TTS via Prompt Engineering (+3 more)

### Community 19 - "scripts"
Cohesion: 0.05
Nodes (43): better-auth, @better-auth/core, face-api.js, groq-sdk, @mediapipe/tasks-vision, dependencies, better-auth, @better-auth/core (+35 more)

### Community 20 - "Instruksi Perbaikan: Halusinasi Whisper, Latensi Kalimat Pertama, & Voice Cloning F5TTS Belum Aktif"
Cohesion: 0.13
Nodes (14): Cara pastikan diagnosis di atas benar, Checklist Verifikasi Akhir, Fix, Fix, Instruksi Perbaikan: Halusinasi Whisper, Latensi Kalimat Pertama, & Voice Cloning F5TTS Belum Aktif, Instrumentasi untuk konfirmasi "lambat kalimat pertama", Kemungkinan penyebab (cek berurutan sesuai probabilitas), MASALAH 1 — Halusinasi Whisper (+6 more)

### Community 21 - "+page.svelte"
Cohesion: 0.20
Nodes (7): $lib/auth-client, $app/environment, $app/forms, $app/navigation, $env/static/public, @mediapipe/tasks-vision, svelte/transition

### Community 22 - "$lib/components/Header.svelte"
Cohesion: 0.19
Nodes (8): $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $lib/components/Sidebar.svelte, $lib/sidebar.svelte, sidebarState, string, $lib/assets/logo.png?enhanced, $app/state

### Community 27 - "vision_wasm_module_internal.js"
Cohesion: 0.10
Nodes (19): handle(), hardware_concurrency(), RFC-2279, RFC-3629, ModuleFactory(), NOTE: In our implementation, st_blocks = Math.ceil(st_size/st_blksize),, NOTE: This is also used as the process return code in shell environments, TODO: check for O_SEARCH? (== search for dir only) (+11 more)

### Community 28 - "finish_and_report"
Cohesion: 0.12
Nodes (36): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+28 more)

### Community 29 - "Project Documentation and Assets"
Cohesion: 0.20
Nodes (12): backend/INITIAL.md, docs/models/3d/boy-character.md, FaceAnimator, frontend/docs/database-schema.md, frontend/PRD.md, Heurix Backend (FastAPI), Heurix Database (Postgres), Heurix Frontend (SvelteKit) (+4 more)

### Community 34 - "Task for the agent: Heurix — Integrasi F5-TTS-INDO-FINETUNE-V2 (Voice Cloning TTS) sebagai Engine Suara Baru"
Cohesion: 0.12
Nodes (15): 10. Task 7 — Preload model saat startup (`main.py`), 11. Task 8 — Script konfigurasi avatar (`scripts/set_avatar_voice_config.py`), 12. Catatan Performa — WAJIB dikomunikasikan ke user, jangan silent, 13. Verification Checklist (jalankan setelah semua task selesai), 1. Executive Summary, 2. Prasyarat Manual (dilakukan user, bukan agent), 3. File yang Akan Diubah/Ditambah, 4. Task 1 — Dependencies (+7 more)

### Community 35 - "PWA State Management"
Cohesion: 0.25
Nodes (4): $lib/pwa.svelte, pwaState, $lib/assets/favicon.svg, ./layout.css

### Community 37 - "File I/O Operations"
Cohesion: 0.25
Nodes (8): abort(), assert(), createLazyFile(), forceLoadFile(), getMouseWheelDelta(), position(), readFile(), writeFile()

### Community 38 - "WASM Binary Instantiation"
Cohesion: 0.25
Nodes (8): createWasm(), findWasmBinary(), getBinarySync(), getWasmBinary(), getWasmImports(), instantiateArrayBuffer(), instantiateAsync(), locateFile()

### Community 39 - "abort"
Cohesion: 0.12
Nodes (16): abort(), assert(), createLazyFile(), createWasm(), findWasmBinary(), forceLoadFile(), getBinarySync(), getMouseWheelDelta() (+8 more)

### Community 41 - "Frontend Chart Dependencies"
Cohesion: 0.25
Nodes (7): dependencies, chart.js, lucide-svelte, svelte-chartjs, chart.js, lucide-svelte, svelte-chartjs

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
Cohesion: 0.13
Nodes (16): _extract_visemes(), F5TTSSpeechService, get_speech_service_for_avatar(), _guard_reference_audio(), Factory: pilih engine berdasarkan kolom tts_engine di avatar.     Fallback aman, Ekstrak RMS envelope untuk viseme dari raw audio bytes (format apa pun yang didu, Engine default: edge_tts (cloud, stateless, tanpa voice cloning)., Engine voice cloning. Butuh ref_audio_path + ref_text per avatar (BUKAN global, (+8 more)

### Community 51 - "Auth Table Migrations"
Cohesion: 0.40
Nodes (4): "account", "session", "user", "verification"

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

### Community 60 - "config.py"
Cohesion: 0.40
Nodes (4): Config, _find_f5tts_path(), Settings, BaseSettings

### Community 63 - "f5tts_service.py"
Cohesion: 0.31
Nodes (8): is_available(), _load_model(), Lazy-load F5-TTS model + vocoder sekali saja (thread-safe)., Cek apakah model bisa/sudah di-load, tanpa melempar exception ke caller., Generate audio dengan voice cloning dari ref_audio_path.     Return: (wav_bytes,, Versi asinkron dari synthesize() yang memindahkan CPU inference ke thread pool, synthesize(), synthesize_async()

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

### Community 73 - "+page.svelte"
Cohesion: 0.38
Nodes (3): $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $lib/components/Sidebar.svelte

### Community 74 - "Fix: Client-side memory leak / lag causing laptop hang on interview page"
Cohesion: 0.17
Nodes (11): 1. Lift `renderer`, `scene`, `camera`, and the `ResizeObserver` to component scope, 2. Capture and cancel the animation frame loop, 3. Extend `onDestroy` with full cleanup, 4. Optional (recommended) performance improvements, same file, Do not change, File, Fix: Client-side memory leak / lag causing laptop hang on interview page, Root cause (+3 more)

### Community 76 - "Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)"
Cohesion: 0.25
Nodes (7): FIX 1 — Decouple auto-send dari Web Speech API (fix Brave, tanpa merusak Chrome), FIX 2 — WebSocket heartbeat (ping/pong) untuk cegah idle-disconnect di cloudflared tunnel, FIX 3 — Suara AI lebih natural (prompt engineering, BUKAN SSML), FIX 4 — AI harus jawab pertanyaan kandidat di fase closing/farewell, FIX 5 — Persingkat kalimat yang digenerate AI, Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length), Verification checklist (setelah semua fix diterapkan)

### Community 78 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 79 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 97 - "Implementation Report: Avatar Hassan Camera Config Adjustment"
Cohesion: 0.33
Nodes (5): 1. Issue Description, 2. Implemented Fix, 3. Results & Verification, Implementation Report: Avatar Hassan Camera Config Adjustment, Root Cause

### Community 123 - "Task for the agent"
Cohesion: 0.22
Nodes (8): 1. Standardize the convention, 2. Fix stale/incorrect examples and docs, 3. Rebuild the frontend image (not just recreate), 4. Verify the fix, Do not change, Fix: WebSocket connection rejected during interview startup (`/ws/ws/{sessionId}` double path), Root cause, Task for the agent

### Community 124 - "SpeechService"
Cohesion: 0.33
Nodes (4): Menghasilkan audio (base64) dan data viseme (amplitude envelope).          speed, Konversi rasio (1.0 = normal) ke string persen bertanda yang dipahami     edge_t, SpeechService, _to_percent_string()

### Community 126 - "migration_ape.sql"
Cohesion: 0.50
Nodes (3): interview_session, session_report, user_profile

### Community 127 - "0010_fair_network.sql"
Cohesion: 0.50
Nodes (3): "interview_session", "session_report", "user_profile"

## Knowledge Gaps
- **309 isolated node(s):** `Config`, `user_profile`, `interview_session`, `session_report`, `interviewTrackEnum` (+304 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fs` connect `fs` to `vision_wasm_internal.js`, `Path and Directory Management`, `scripts`, `vision_wasm_module_internal.js`, `File I/O Operations`, `abort`, `TTY IOCTL Syscalls`, `TTY IOCTL Syscalls`, `Low-level Write Operations`, `Low-level Write Operations`, `File Stream Closing`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`, `File Synchronization`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `dependencies` connect `scripts` to `fs`, `Path and Directory Management`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `$lib/lipSync` connect `$lib/lipSync` to `+page.svelte`, `Session`, `visemeMap.ts`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `send_next_question_stream()` (e.g. with `InterviewAvatar` and `MasterInstitution`) actually correct?**
  _`send_next_question_stream()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `user_profile`, `interview_session` to the rest of the system?**
  _309 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `brain.py` be split into smaller, more focused modules?**
  _Cohesion score 0.062146892655367235 - nodes in this community are weakly interconnected._
- **Should `vision_wasm_internal.js` be split into smaller, more focused modules?**
  _Cohesion score 0.015037593984962405 - nodes in this community are weakly interconnected._