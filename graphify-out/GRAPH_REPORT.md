# Graph Report - /home/dwiwahyuilahi/Kuliah/Gemastik/source-code  (2026-07-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1870 nodes · 4022 edges · 158 communities (101 shown, 57 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d73a1869`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- draco_encoder.js
- vision_wasm_internal.js
- vision_wasm_nosimd_internal.js
- fs
- draco_wasm_wrapper.js
- Session
- ln
- pj
- fk
- ci
- A
- Draco Decoder JS
- aq
- Path and Directory Management
- schema.ts
- $lib/FaceAnimator
- devDependencies
- auth.ts
- ej
- scripts
- Draco Geometry Decoders
- +page.svelte
- $lib/components/Header.svelte
- l
- C++ Exception Handling
- WASM Memory Management
- f
- vision_wasm_module_internal.js
- brain.py
- Project Documentation and Assets
- Draco Mesh Encoding
- Exception Info Metadata
- Exception Info Metadata
- WASM Runtime Lifecycle
- 0002_fast_gambit.sql
- PWA State Management
- Binary Data Utilities
- File I/O Operations
- WASM Binary Instantiation
- abort
- finish_and_report
- Frontend Chart Dependencies
- Runtime Initialization Callbacks
- Database Seed Entrypoint
- Institution Data Seeding
- brain.py
- $app/navigation
- auth.schema.ts
- WebGPU Buffer Entries
- WebGPU Buffer Entries
- SpeechService
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
- finish_and_report
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
- n
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
- ha
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
- $lib/lipSync
- migration_ape.sql
- 0010_fair_network.sql
- mi
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
- c

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

## Communities (158 total, 57 thin omitted)

### Community 0 - "draco_encoder.js"
Cohesion: 0.01
Nodes (85): ai(), ak(), am(), ao(), bi(), bn(), bp(), ch() (+77 more)

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
Cohesion: 0.20
Nodes (18): kd(), od(), qb(), ul(), B(), E(), G(), H() (+10 more)

### Community 5 - "Session"
Cohesion: 0.14
Nodes (29): Account, Base, Session, User, Verification, Difficulty, InterviewAvatar, InterviewSession (+21 more)

### Community 6 - "ln"
Cohesion: 0.09
Nodes (76): $a(), ad(), aj(), bd(), _c(), cd(), ce(), de() (+68 more)

### Community 7 - "pj"
Cohesion: 0.18
Nodes (17): Ac(), _b(), bf(), bk(), eq(), Fc(), Hc(), kg() (+9 more)

### Community 8 - "fk"
Cohesion: 0.12
Nodes (18): cf(), cg(), ff(), fk(), ij(), je(), Kc(), kj() (+10 more)

### Community 9 - "ci"
Cohesion: 0.13
Nodes (35): af(), bh(), bq(), ci(), dd(), dg(), dj(), _e() (+27 more)

### Community 11 - "Draco Decoder JS"
Cohesion: 0.07
Nodes (14): addRunDependency(), createWasm(), emscripten_realloc_buffer(), _emscripten_resize_heap(), ensureString(), getHeapMax(), intArrayFromString(), l() (+6 more)

### Community 12 - "aq"
Cohesion: 0.18
Nodes (44): ab(), Ae(), aq(), bb(), cb(), _d(), db(), Dc() (+36 more)

### Community 13 - "Path and Directory Management"
Cohesion: 0.07
Nodes (30): analyzePath(), calculateAt(), createDataFile(), createDevice(), createFile(), createPath(), lookupPath(), mkdirTree() (+22 more)

### Community 14 - "schema.ts"
Cohesion: 0.10
Nodes (20): difficultyEnum, interviewAvatar, interviewAvatarRelations, interviewSession, interviewSessionRelations, interviewTrackEnum, masterInstitution, masterInstitutionRelations (+12 more)

### Community 15 - "$lib/FaceAnimator"
Cohesion: 0.18
Nodes (12): $lib/autoBlink, $lib/emotionPresets, EMOTIONS, $lib/FaceAnimator, FaceAnimator, collectMorphMeshes(), resetAllMorphs(), setMorph() (+4 more)

### Community 16 - "devDependencies"
Cohesion: 0.04
Nodes (47): @better-auth/cli, drizzle-kit, drizzle-orm, @faker-js/faker, devDependencies, @better-auth/cli, drizzle-kit, drizzle-orm (+39 more)

### Community 17 - "auth.ts"
Cohesion: 0.14
Nodes (4): auth, GET, POST, actions

### Community 18 - "ej"
Cohesion: 0.33
Nodes (6): ej(), om(), _p(), pp(), qo(), sn()

### Community 19 - "scripts"
Cohesion: 0.05
Nodes (43): better-auth, @better-auth/core, face-api.js, groq-sdk, @mediapipe/tasks-vision, dependencies, better-auth, @better-auth/core (+35 more)

### Community 20 - "Draco Geometry Decoders"
Cohesion: 0.10
Nodes (20): AttributeOctahedronTransform(), AttributeQuantizationTransform(), AttributeTransformData(), Decoder(), DecoderBuffer(), destroy(), DracoFloat32Array(), DracoInt16Array() (+12 more)

### Community 21 - "+page.svelte"
Cohesion: 0.18
Nodes (9): three/examples/jsm/loaders/DRACOLoader.js, $app/environment, $lib/avatarCache, cache, three/examples/jsm/loaders/GLTFLoader.js, three/examples/jsm/libs/meshopt_decoder.module.js, $env/static/public, $app/state (+1 more)

### Community 22 - "$lib/components/Header.svelte"
Cohesion: 0.20
Nodes (7): $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $lib/components/Sidebar.svelte, $lib/sidebar.svelte, sidebarState, string, svelte/transition

### Community 25 - "WASM Memory Management"
Cohesion: 0.15
Nodes (17): alignUp(), allocate(), assert(), ccall(), dynamicAlloc(), enlargeMemory(), getCFunc(), getNativeTypeSize() (+9 more)

### Community 26 - "f"
Cohesion: 0.15
Nodes (19): an(), bm(), en(), fn(), kn(), lq(), _m(), pm() (+11 more)

### Community 27 - "vision_wasm_module_internal.js"
Cohesion: 0.07
Nodes (28): handle(), gp(), lm(), mj(), ml(), nm(), rn(), sp() (+20 more)

### Community 28 - "brain.py"
Cohesion: 0.11
Nodes (31): build_chat_history(), build_system_prompt(), calculate_sri(), compute_pressure_level(), extract_weakness_tags(), generate_next_turn(), generate_next_turn_stream(), get_phase() (+23 more)

### Community 29 - "Project Documentation and Assets"
Cohesion: 0.20
Nodes (12): backend/INITIAL.md, docs/models/3d/boy-character.md, FaceAnimator, frontend/docs/database-schema.md, frontend/PRD.md, Heurix Backend (FastAPI), Heurix Database (Postgres), Heurix Frontend (SvelteKit) (+4 more)

### Community 30 - "Draco Mesh Encoding"
Cohesion: 0.14
Nodes (14): castObject(), destroy(), DracoInt8Array(), Encoder(), GeometryAttribute(), getCache(), Mesh(), MeshBuilder() (+6 more)

### Community 33 - "WASM Runtime Lifecycle"
Cohesion: 0.20
Nodes (10): addOnPostRun(), addOnPreRun(), callRuntimeCallbacks(), ensureInitRuntime(), exit(), exitRuntime(), postRun(), preMain() (+2 more)

### Community 34 - "0002_fast_gambit.sql"
Cohesion: 0.29
Nodes (6): "interview_avatar", "interview_session", "master_institution", "question_bank", "session_report", "user_profile"

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

### Community 40 - "finish_and_report"
Cohesion: 0.18
Nodes (27): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+19 more)

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

### Community 45 - "brain.py"
Cohesion: 0.13
Nodes (25): build_chat_history(), build_system_prompt(), compute_pressure_level(), extract_weakness_tags(), generate_next_turn(), generate_next_turn_stream(), get_phase(), InterviewPhase (+17 more)

### Community 46 - "$app/navigation"
Cohesion: 0.20
Nodes (6): $lib/auth-client, $lib/auth-client, authClient, $lib/assets/login-art.png?enhanced, $lib/assets/logo.png?enhanced, $app/navigation

### Community 47 - "auth.schema.ts"
Cohesion: 0.25
Nodes (7): account, accountRelations, session, sessionRelations, user, userRelations, verification

### Community 48 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 49 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 50 - "SpeechService"
Cohesion: 0.33
Nodes (4): Menghasilkan audio (base64) dan data viseme (amplitude envelope).          speed, Konversi rasio (1.0 = normal) ke string persen bertanda yang dipahami     edge_t, SpeechService, _to_percent_string()

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

### Community 63 - "finish_and_report"
Cohesion: 0.21
Nodes (18): finish_and_report(), handle_user_answer(), InterviewSession, WebSocket, Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question() (+10 more)

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
Cohesion: 0.27
Nodes (3): client, db, userProfile

### Community 73 - "+page.svelte"
Cohesion: 0.38
Nodes (3): $lib/components/BottomNav.svelte, $lib/components/Header.svelte, $lib/components/Sidebar.svelte

### Community 74 - "Fix: Client-side memory leak / lag causing laptop hang on interview page"
Cohesion: 0.17
Nodes (11): 1. Lift `renderer`, `scene`, `camera`, and the `ResizeObserver` to component scope, 2. Capture and cancel the animation frame loop, 3. Extend `onDestroy` with full cleanup, 4. Optional (recommended) performance improvements, same file, Do not change, File, Fix: Client-side memory leak / lag causing laptop hang on interview page, Root cause (+3 more)

### Community 75 - "n"
Cohesion: 0.48
Nodes (3): ii(), n(), p()

### Community 78 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 79 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 94 - "ha"
Cohesion: 0.08
Nodes (44): ha(), ag(), Bc(), be(), bg(), bj(), Cc(), di() (+36 more)

### Community 123 - "Task for the agent"
Cohesion: 0.22
Nodes (8): 1. Standardize the convention, 2. Fix stale/incorrect examples and docs, 3. Rebuild the frontend image (not just recreate), 4. Verify the fix, Do not change, Fix: WebSocket connection rejected during interview startup (`/ws/ws/{sessionId}` double path), Root cause, Task for the agent

### Community 124 - "SpeechService"
Cohesion: 0.33
Nodes (4): Menghasilkan audio (base64) dan data viseme (amplitude envelope).          speed, Konversi rasio (1.0 = normal) ke string persen bertanda yang dipahami     edge_t, SpeechService, _to_percent_string()

### Community 125 - "$lib/lipSync"
Cohesion: 0.60
Nodes (5): $lib/lipSync, b64toBlob(), speakWithBackend(), unlockAudio(), Frontend-Backend Integration Guide

### Community 126 - "migration_ape.sql"
Cohesion: 0.50
Nodes (3): interview_session, session_report, user_profile

### Community 127 - "0010_fair_network.sql"
Cohesion: 0.50
Nodes (3): "interview_session", "session_report", "user_profile"

### Community 128 - "mi"
Cohesion: 0.33
Nodes (7): ah(), dh(), hl(), _i(), mi(), nd(), xi()

### Community 162 - "c"
Cohesion: 0.14
Nodes (14): c(), bo(), go(), ho(), mn(), _n(), no(), oj() (+6 more)

## Knowledge Gaps
- **211 isolated node(s):** `Config`, `user_profile`, `interview_session`, `session_report`, `interviewTrackEnum` (+206 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fs` connect `fs` to `vision_wasm_internal.js`, `vision_wasm_nosimd_internal.js`, `Path and Directory Management`, `scripts`, `vision_wasm_module_internal.js`, `File I/O Operations`, `abort`, `TTY IOCTL Syscalls`, `TTY IOCTL Syscalls`, `Low-level Write Operations`, `Low-level Write Operations`, `File Stream Closing`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`, `File Synchronization`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`?**
  _High betweenness centrality (0.319) - this node is a cross-community bridge._
- **Why does `___syscall140()` connect `fs` to `draco_encoder.js`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `___syscall6()` connect `fs` to `draco_encoder.js`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 153 inferred relationships involving `ha()` (e.g. with `Ac()` and `ad()`) actually correct?**
  _`ha()` has 153 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `user_profile`, `interview_session` to the rest of the system?**
  _211 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `draco_encoder.js` be split into smaller, more focused modules?**
  _Cohesion score 0.013546130732476232 - nodes in this community are weakly interconnected._
- **Should `vision_wasm_internal.js` be split into smaller, more focused modules?**
  _Cohesion score 0.014925373134328358 - nodes in this community are weakly interconnected._