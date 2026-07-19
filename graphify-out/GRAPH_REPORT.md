# Graph Report - /home/dwiwahyuilahi/Kuliah/Gemastik/source-code  (2026-07-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1693 nodes · 3760 edges · 158 communities (85 shown, 73 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 339 edges (avg confidence: 0.78)
- Token cost: 4,126 input · 1,914 output

## Graph Freshness
- Built from commit: `424b4261`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Draco Encoder JS
- MediaPipe Vision WASM
- MediaPipe Vision No-SIMD
- Emscripten File System Syscalls
- SvelteKit Server Hooks
- WebSocket Interview Logic
- Minified Utility Functions
- Minified Core Logic
- Minified Runtime Utilities
- Minified Script Fragments
- Minified Helper Functions
- Draco Decoder JS
- Minified Data Mappings
- Path and Directory Management
- Database Auth Schema
- Face Animation and Expressions
- Project Dev Dependencies
- Auth Client Integration
- Minified Variable Mappings
- Core Project Dependencies
- Draco Geometry Decoders
- 3D Model Loading
- UI Layout Components
- Minified Property Accessors
- C++ Exception Handling
- WASM Memory Management
- Minified Internal Symbols
- WASM Module Implementation Notes
- Database and Build Scripts
- Project Documentation and Assets
- Draco Mesh Encoding
- Exception Info Metadata
- Exception Info Metadata
- WASM Runtime Lifecycle
- Interview Session Migrations
- PWA State Management
- Binary Data Utilities
- File I/O Operations
- WASM Binary Instantiation
- File I/O Operations
- WASM Binary Instantiation
- Frontend Chart Dependencies
- Runtime Initialization Callbacks
- Database Seed Entrypoint
- Institution Data Seeding
- Minified Reference Identifiers
- Minified Symbol Mappings
- Minified Pair Identifiers
- WebGPU Buffer Entries
- WebGPU Buffer Entries
- Speech and Viseme Service
- Auth Table Migrations
- Minified Identifier Set
- Browser Data Loading
- UTF8 String Encoding
- WebGPU Blend States
- WebGPU Vertex Attributes
- WebGPU Blend States
- WebGPU Vertex Attributes
- Package Metadata
- Backend Configuration Settings
- Audio Transcription Service
- Avatar Seeding Script
- Minified Pair Identifiers
- Minified Variable Set
- TTY IOCTL Syscalls
- WebGPU Render Pass
- TTY IOCTL Syscalls
- WebGPU Render Pass
- Better-Auth CLI Tools
- Session Report Migrations
- SvelteKit Type Definitions
- User Profile Loader
- API Route Handlers
- Server Page Actions
- Minified Short Identifiers
- Minified Short Identifiers
- Minified Short Identifiers
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
- Minified Pair Identifiers
- Minified Pair Identifiers
- Minified Pair Identifiers
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
- PostgreSQL Database
- Prettier Formatting
- Svelte Prettier Plugin
- Svelte Framework
- SvelteKit Auto Adapter
- SvelteKit Framework
- Svelte Vite Plugin
- Tailwind Typography Plugin
- Tailwind Vite Plugin
- TypeScript Language
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
- `getPath()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `getStreamChecked()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `fstat()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `doChown()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json
- `doTruncate()` --references--> `fs`  [EXTRACTED]
  frontend/static/wasm/vision_wasm_internal.js → migrator/package.json

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Heurix System Architecture** — heurix_db, heurix_backend, heurix_frontend, heurix_migrator [EXTRACTED 1.00]
- **AI Interview Simulation Flow** — interview_agent, face_animator, heurix_backend, heurix_frontend [INFERRED 0.85]
- **Avatar Animation & Lip-Sync System** — frontend_src_lib_faceanimator, frontend_src_lib_lipsync, instruction_viseme, frontend_static_face_professional_man_instruction [EXTRACTED 1.00]
- **Interview Session Logic & Flow** — backend_app_services_brain, backend_app_api_websocket, instruction_implementasi_alur_percakapan [EXTRACTED 1.00]

## Communities (158 total, 73 thin omitted)

### Community 0 - "Draco Encoder JS"
Cohesion: 0.01
Nodes (23): $a(), ak(), demangle(), demangleAll(), fo(), ij(), ik(), iq() (+15 more)

### Community 1 - "MediaPipe Vision WASM"
Cohesion: 0.01
Nodes (25): createDefaultDirectories(), doChown(), doTruncate(), _fd_seek(), findObject(), fstat(), getPath(), getStreamChecked() (+17 more)

### Community 2 - "MediaPipe Vision No-SIMD"
Cohesion: 0.02
Nodes (23): createDefaultDirectories(), createNode(), fchown(), getStreamChecked(), RFC-2279, RFC-3629, lchown(), llseek() (+15 more)

### Community 3 - "Emscripten File System Syscalls"
Cohesion: 0.02
Nodes (116): ___syscall140(), ___syscall6(), chdir(), chmod(), chown(), create(), createDefaultDevices(), createNode() (+108 more)

### Community 4 - "SvelteKit Server Hooks"
Cohesion: 0.05
Nodes (43): handle(), bm(), en(), fn(), ii(), kd(), lh(), mg() (+35 more)

### Community 5 - "WebSocket Interview Logic"
Cohesion: 0.09
Nodes (56): finish_and_report(), handle_user_answer(), Mengakhiri sesi, men-generate laporan, dan mengirim sinyal selesai ke frontend., Menghasilkan pertanyaan berikutnya secara streaming dan mengirim audio per kalim, Sederhana membagi teks menjadi kalimat berdasarkan tanda baca., re_send_last_question(), send_next_question_stream(), split_into_sentences() (+48 more)

### Community 6 - "Minified Utility Functions"
Cohesion: 0.12
Nodes (51): ad(), bd(), _c(), cd(), ce(), dd(), de(), ed() (+43 more)

### Community 7 - "Minified Core Logic"
Cohesion: 0.11
Nodes (45): Ac(), Ae(), aj(), aq(), _b(), bj(), ch(), cj() (+37 more)

### Community 8 - "Minified Runtime Utilities"
Cohesion: 0.13
Nodes (30): af(), cf(), cg(), cm(), dm(), _e(), ff(), fi() (+22 more)

### Community 9 - "Minified Script Fragments"
Cohesion: 0.12
Nodes (32): bh(), bn(), bq(), ci(), dg(), dj(), fh(), fj() (+24 more)

### Community 10 - "Minified Helper Functions"
Cohesion: 0.11
Nodes (35): ha(), ag(), Bc(), be(), bg(), Cc(), df(), di() (+27 more)

### Community 11 - "Draco Decoder JS"
Cohesion: 0.07
Nodes (14): addRunDependency(), createWasm(), emscripten_realloc_buffer(), _emscripten_resize_heap(), ensureString(), getHeapMax(), intArrayFromString(), l() (+6 more)

### Community 12 - "Minified Data Mappings"
Cohesion: 0.23
Nodes (31): ab(), bb(), cb(), _d(), db(), eb(), fb(), gb() (+23 more)

### Community 13 - "Path and Directory Management"
Cohesion: 0.07
Nodes (30): analyzePath(), calculateAt(), createDataFile(), createDevice(), createFile(), createPath(), lookupPath(), mkdirTree() (+22 more)

### Community 14 - "Database Auth Schema"
Cohesion: 0.08
Nodes (26): account, accountRelations, session, sessionRelations, user, userRelations, verification, difficultyEnum (+18 more)

### Community 15 - "Face Animation and Expressions"
Cohesion: 0.15
Nodes (13): EMOTIONS, FaceAnimator, b64toBlob(), speakWithBackend(), unlockAudio(), collectMorphMeshes(), resetAllMorphs(), setMorph() (+5 more)

### Community 16 - "Project Dev Dependencies"
Cohesion: 0.08
Nodes (25): drizzle-kit, drizzle-orm, @faker-js/faker, devDependencies, drizzle-kit, drizzle-orm, @faker-js/faker, prettier-plugin-tailwindcss (+17 more)

### Community 17 - "Auth Client Integration"
Cohesion: 0.15
Nodes (4): authClient, auth, client, db

### Community 18 - "Minified Variable Mappings"
Cohesion: 0.09
Nodes (22): c(), bo(), ej(), go(), ho(), kn(), mn(), _n() (+14 more)

### Community 19 - "Core Project Dependencies"
Cohesion: 0.10
Nodes (21): better-auth, face-api.js, groq-sdk, @mediapipe/tasks-vision, dependencies, better-auth, chart.js, face-api.js (+13 more)

### Community 20 - "Draco Geometry Decoders"
Cohesion: 0.10
Nodes (20): AttributeOctahedronTransform(), AttributeQuantizationTransform(), AttributeTransformData(), Decoder(), DecoderBuffer(), destroy(), DracoFloat32Array(), DracoInt16Array() (+12 more)

### Community 21 - "3D Model Loading"
Cohesion: 0.13
Nodes (10): three/examples/jsm/loaders/DRACOLoader.js, $app/environment, cache, three/examples/jsm/loaders/GLTFLoader.js, $lib/assets/login-art.png?enhanced, three/examples/jsm/libs/meshopt_decoder.module.js, $app/navigation, $env/static/public (+2 more)

### Community 22 - "UI Layout Components"
Cohesion: 0.18
Nodes (4): sidebarState, string, $lib/assets/logo.png?enhanced, svelte/transition

### Community 23 - "Minified Property Accessors"
Cohesion: 0.12
Nodes (18): ah(), bi(), dh(), fl(), gp(), hl(), ip(), mi() (+10 more)

### Community 25 - "WASM Memory Management"
Cohesion: 0.15
Nodes (17): alignUp(), allocate(), assert(), ccall(), dynamicAlloc(), enlargeMemory(), getCFunc(), getNativeTypeSize() (+9 more)

### Community 26 - "Minified Internal Symbols"
Cohesion: 0.10
Nodes (23): am(), an(), dl(), fp(), gh(), hj(), hm(), il() (+15 more)

### Community 27 - "WASM Module Implementation Notes"
Cohesion: 0.12
Nodes (16): RFC-2279, RFC-3629, NOTE: In our implementation, st_blocks = Math.ceil(st_size/st_blksize),, NOTE: This is also used as the process return code in shell environments, TODO: check for O_SEARCH? (== search for dir only), NOTE: None of the defaults here are true. We're just returning safe and, TODO: Use mozResponseArrayBuffer, responseStream, etc. if available., TODO: Due to Closure regression https://github.com/google/closure-compiler/issue (+8 more)

### Community 28 - "Database and Build Scripts"
Cohesion: 0.12
Nodes (16): scripts, auth:schema, build, check, check:watch, db:generate, db:migrate, db:push (+8 more)

### Community 29 - "Project Documentation and Assets"
Cohesion: 0.20
Nodes (12): backend/INITIAL.md, docs/models/3d/boy-character.md, FaceAnimator, frontend/docs/database-schema.md, frontend/PRD.md, Heurix Backend (FastAPI), Heurix Database (Postgres), Heurix Frontend (SvelteKit) (+4 more)

### Community 30 - "Draco Mesh Encoding"
Cohesion: 0.14
Nodes (14): castObject(), destroy(), DracoInt8Array(), Encoder(), GeometryAttribute(), getCache(), Mesh(), MeshBuilder() (+6 more)

### Community 33 - "WASM Runtime Lifecycle"
Cohesion: 0.20
Nodes (10): addOnPostRun(), addOnPreRun(), callRuntimeCallbacks(), ensureInitRuntime(), exit(), exitRuntime(), postRun(), preMain() (+2 more)

### Community 34 - "Interview Session Migrations"
Cohesion: 0.22
Nodes (8): "interview_avatar", "interview_session", "master_institution", "master_position", "question_bank", "session_report", "session_turn", "user_profile"

### Community 35 - "PWA State Management"
Cohesion: 0.25
Nodes (3): pwaState, $lib/assets/favicon.svg, ./layout.css

### Community 36 - "Binary Data Utilities"
Cohesion: 0.25
Nodes (8): abort(), assert(), getBinary(), getBinaryPromise(), intArrayFromBase64(), isDataURI(), isFileURI(), tryParseAsDataURI()

### Community 37 - "File I/O Operations"
Cohesion: 0.25
Nodes (8): abort(), assert(), createLazyFile(), forceLoadFile(), getMouseWheelDelta(), position(), readFile(), writeFile()

### Community 38 - "WASM Binary Instantiation"
Cohesion: 0.25
Nodes (8): createWasm(), findWasmBinary(), getBinarySync(), getWasmBinary(), getWasmImports(), instantiateArrayBuffer(), instantiateAsync(), locateFile()

### Community 39 - "File I/O Operations"
Cohesion: 0.25
Nodes (8): abort(), assert(), createLazyFile(), forceLoadFile(), getMouseWheelDelta(), position(), readFile(), writeFile()

### Community 40 - "WASM Binary Instantiation"
Cohesion: 0.25
Nodes (8): createWasm(), findWasmBinary(), getBinarySync(), getWasmBinary(), getWasmImports(), instantiateArrayBuffer(), instantiateAsync(), locateFile()

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

### Community 45 - "Minified Reference Identifiers"
Cohesion: 0.19
Nodes (14): ai(), bf(), bk(), eq(), Fc(), Hc(), kg(), md() (+6 more)

### Community 46 - "Minified Symbol Mappings"
Cohesion: 0.33
Nodes (6): bp(), eo(), jk(), jn(), kp(), mp()

### Community 48 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 49 - "WebGPU Buffer Entries"
Cohesion: 0.33
Nodes (6): makeBufferEntry(), makeEntries(), makeEntry(), makeSamplerEntry(), makeStorageTextureEntry(), makeTextureEntry()

### Community 51 - "Auth Table Migrations"
Cohesion: 0.40
Nodes (4): "account", "session", "user", "verification"

### Community 52 - "Minified Identifier Set"
Cohesion: 0.40
Nodes (5): ao(), dp(), io(), ji(), op()

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

### Community 59 - "Package Metadata"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 60 - "Backend Configuration Settings"
Cohesion: 0.50
Nodes (3): Config, Settings, BaseSettings

### Community 64 - "Minified Variable Set"
Cohesion: 0.50
Nodes (4): lm(), mj(), nm(), yp()

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

### Community 69 - "Better-Auth CLI Tools"
Cohesion: 0.67
Nodes (3): @better-auth/cli, @better-auth/core, @better-auth/cli

### Community 75 - "Minified Short Identifiers"
Cohesion: 0.67
Nodes (3): dq(), xd(), yo()

### Community 76 - "Minified Short Identifiers"
Cohesion: 0.67
Nodes (3): ml(), rn(), to()

### Community 77 - "Minified Short Identifiers"
Cohesion: 0.67
Nodes (3): oq(), xn(), yc()

### Community 78 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

### Community 79 - "Low-level Write Operations"
Cohesion: 0.67
Nodes (3): msync(), put_char(), write()

## Knowledge Gaps
- **154 isolated node(s):** `Config`, `"task"`, `"account"`, `"session"`, `"user"` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fs` connect `Emscripten File System Syscalls` to `MediaPipe Vision WASM`, `MediaPipe Vision No-SIMD`, `SvelteKit Server Hooks`, `Path and Directory Management`, `Core Project Dependencies`, `File I/O Operations`, `File I/O Operations`, `TTY IOCTL Syscalls`, `TTY IOCTL Syscalls`, `Low-level Write Operations`, `Low-level Write Operations`, `File Stream Closing`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`, `File Synchronization`, `Character Input Reading`, `Initialization and Timing`, `Filesystem Mounting`, `Filesystem Statistics`?**
  _High betweenness centrality (0.365) - this node is a cross-community bridge._
- **Why does `___syscall140()` connect `Emscripten File System Syscalls` to `Draco Encoder JS`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `___syscall6()` connect `Emscripten File System Syscalls` to `Draco Encoder JS`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 153 inferred relationships involving `ha()` (e.g. with `Ac()` and `ad()`) actually correct?**
  _`ha()` has 153 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `"task"`, `"account"` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Draco Encoder JS` be split into smaller, more focused modules?**
  _Cohesion score 0.014696813977389518 - nodes in this community are weakly interconnected._
- **Should `MediaPipe Vision WASM` be split into smaller, more focused modules?**
  _Cohesion score 0.014925373134328358 - nodes in this community are weakly interconnected._