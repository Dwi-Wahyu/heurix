# Task for the agent: Heurix — Batch Fix (Auto-send VAD, WS Heartbeat, Natural TTS, Farewell Q&A, Response Length)

Do not refactor unrelated code. Preserve existing patterns, naming, dan indentation. Setiap section di bawah independen — bisa dikerjakan/di-commit terpisah.

---

## FIX 1 — Decouple auto-send dari Web Speech API (fix Brave, tanpa merusak Chrome)

**File**: `frontend/src/routes/session/interview/+page.svelte`

**Root cause**: Auto-send/silence-detection saat ini HANYA dipicu dari `recognition.onresult` (Web Speech API browser). Di Brave, `recognition` gagal total dengan `error: 'network'` dan `onresult` tidak pernah terpanggil sama sekali — akibatnya timer auto-send tidak pernah di-set, `mediaRecorder` tidak pernah auto-stop, audio tidak pernah terkirim ke backend. `webkitSpeechRecognition` tidak boleh lagi jadi dependency untuk fitur kirim jawaban — dia HARUS jadi lapisan kosmetik opsional saja (live caption).

**Do not change**: pipeline `MediaRecorder` → `ws.send(buffer)` di `mediaRecorder.onstop`, format audio, dan logic `TRANSCRIPT` handler — semua itu sudah benar dan tidak bergantung ke Web Speech API.

**Task**:
1. Tambahkan Voice Activity Detection (VAD) berbasis `Web Audio API` (`AudioContext` + `AnalyserNode`), independen dari `SpeechRecognition`:
   - Saat `startRecording()` dipanggil dan `stream` tersedia, buat/reuse `AudioContext`, sambungkan `MediaStreamAudioSourceNode` dari `stream` ke `AnalyserNode` (fftSize kecil, misal 512).
   - Jalankan loop polling (via `requestAnimationFrame` atau `setInterval` ~100ms) yang membaca RMS/volume level dari `AnalyserNode.getByteTimeDomainData` atau `getByteFrequencyData`.
   - Tentukan threshold volume "silence" (mis. RMS < konstanta yang bisa dituning) dan durasi (mis. 1000–1200ms below threshold, samakan dengan `silenceTimeout` yang sudah ada) untuk trigger `stopRecording()` — HANYA jika `autoSend` aktif dan sudah ada minimal beberapa detik audio terekam (hindari auto-stop instan di awal sebelum user mulai bicara — pakai flag "sudah pernah terdeteksi suara di atas threshold" dulu sebelum silence timer mulai dihitung, mirip logic `isVoiceActive` yang sudah ada).
   - Matikan/`disconnect()` node ini di `stopRecording()` dan di `onDestroy` (cegah memory leak — ikuti pola cleanup yang sudah ada untuk `stream`, `animationFrameId`, `resizeObserver`).
2. `initSpeechRecognition()` dan `recognition.onresult` **tetap dipertahankan apa adanya** untuk update `liveTranscript` (live caption UI) — tapi HAPUS logic auto-send (`silenceTimeout` set) dari dalam `recognition.onresult`. Auto-send sepenuhnya dipindah ke VAD baru di poin 1.
3. Di `recognition.onerror`, untuk `e.error === 'network'` yang persisten — pesan `errorMessage` yang sudah ada ("Layanan transkrip langsung browser tidak tersedia...") boleh dipertahankan, tapi tambahkan catatan yang jelas bahwa fitur kirim jawaban tetap berjalan normal (karena tidak lagi bergantung ke fitur ini).
4. **Verifikasi**: fitur auto-send harus tetap berfungsi identik di Chrome (tidak ada regresi), dan sekarang juga berfungsi di Brave meskipun live caption tetap kosong di Brave (itu expected/acceptable — sudah dikomunikasikan ke user via `errorMessage`).

---

## FIX 2 — WebSocket heartbeat (ping/pong) untuk cegah idle-disconnect di cloudflared tunnel

**Files**: `frontend/src/routes/session/interview/+page.svelte`, `backend/app/api/websocket.py`

**Root cause**: Tidak ada mechanism keepalive sama sekali di WS. `START_INTERVIEW` baru dikirim setelah `avatarReady` (setelah GLB avatar selesai load+decode Draco) — selama window loading itu koneksi WS idle tanpa traffic apapun. Cloudflare Tunnel (cloudflared) menutup koneksi idle secara default setelah periode tertentu tanpa data — begitu `avatarReady` akhirnya true dan `ws.send(START_INTERVIEW)` dipanggil, socket sudah mati → `ws.onclose` fires → "Koneksi terputus". Ini juga bisa terjadi di tengah sesi kalau user lama berpikir sebelum menjawab.

**Deployment note**: konfigurasi Anda **tidak pakai Nginx reverse proxy** — traffic masuk lewat **Cloudflare Tunnel (cloudflared)** langsung ke container. Jangan tambahkan asumsi/config Nginx apapun di fix ini.

**Task**:
1. **Backend** (`api/websocket.py`), di dalam `while True:` loop, tambahkan handling untuk pesan JSON `{"type": "PING"}` → balas `await websocket.send_json({"type": "PONG"})`. Taruh di percabangan `if "text" in message_data:` sejajar dengan handler `START_INTERVIEW`/`END_SESSION`/`FACE_METRICS` yang sudah ada.
2. **Frontend**, di `initWebSocket()`:
   - Saat `ws.onopen`, mulai `setInterval` yang mengirim `ws.send(JSON.stringify({ type: 'PING' }))` setiap ~20 detik SELAMA `ws.readyState === WebSocket.OPEN` — mulai dari saat socket terbuka, TIDAK menunggu `avatarReady`, supaya window loading avatar juga ter-cover.
   - Clear interval ini di `ws.onclose` dan di `onDestroy` (tambahkan ke cleanup yang sudah ada bareng `ws?.close()`).
   - Di `handleBackendMessage`/`ws.onmessage`, abaikan pesan `type === 'PONG'` secara silent (tidak perlu push ke `messages`, tidak perlu switch-case tambahan di `handleBackendMessage` — cukup early-return di `ws.onmessage` sebelum `JSON.parse` dipakai untuk hal lain, atau tambahkan case kosong `case 'PONG': break;` di switch yang sudah ada).
3. **Jangan ubah** `ws.onclose` yang sudah ada — biarkan tetap set `errorMessage` untuk disconnect yang genuine (bukan idle timeout).

---

## FIX 3 — Suara AI lebih natural (prompt engineering, BUKAN SSML)

**File**: `backend/app/services/brain.py`

**Konteks teknis penting**: TTS engine yang dipakai adalah `edge-tts` (`speech.py`), yang **tidak mendukung custom SSML** (`<break>`, `<emphasis>`, `<say-as>` akan ditolak/dibaca literal oleh service Microsoft — sejak edge-tts v5.0.0 custom SSML sengaja di-block). Yang didukung HANYA `rate`/`pitch`/`volume` di level `<prosody>`, dan itu sudah diimplementasikan lewat parameter `speed`/`pitch` di `get_tts_params()` + `_to_percent_string()`. **Jangan sisipkan tag SSML apapun ke teks** — tidak akan berefek dan berisiko dibacakan literal oleh voice ("kurang tanda kurang siku break time delapan ratus milidetik...").

Pendekatan yang benar: manfaatkan bahwa Azure neural voice sudah natural menangkap jeda dari tanda baca teks biasa. Perbaikan dilakukan di level prompt LLM (`brain.py`), bukan di `speech.py`.

**Task**:
1. Di `build_system_prompt()`, tambahkan section instruksi baru (bisa disisipkan di `format_instruction`, atau section baru sejajar `=== ATURAN SESI ===`), isinya kurang lebih:
   - Instruksikan LLM sesekali (TIDAK di setiap giliran, agar tidak terdengar dibuat-buat) menyisipkan interjeksi lisan alami di awal feedback/pertanyaan — contoh: "Baik,", "Oke,", "Hmm,", "Menarik,". Batasi frekuensi eksplisit (mis. "gunakan secukupnya, jangan di setiap kalimat") supaya tidak mengganggu nada profesional wawancara.
   - Instruksikan pemakaian tanda baca secara strategis untuk membentuk jeda napas alami: koma untuk jeda pendek, titik untuk jeda penuh antar kalimat, dan boleh sesekali pakai elipsis (`...`) untuk jeda berpikir SEBELUM pertanyaan yang lebih menantang (khususnya relevan untuk scenario `grilling`/`stress_test` — selaras dengan `SCENARIO_CONFIG` yang sudah ada).
   - Larang penggunaan markup/tag apapun (HTML/SSML/markdown) dalam output — tegaskan output harus plain spoken text karena akan dibacakan langsung oleh TTS.
2. Pastikan instruksi ini konsisten baik di `format_instruction` mode non-streaming maupun mode streaming (`is_streaming=True`) — keduanya di-generate di fungsi yang sama, cek kedua branch `if is_streaming:`.
3. **Tidak ada perubahan di `speech.py`/`websocket.py`** — TTS pipeline (viseme, base64 audio, `split_into_sentences`) tetap sama persis.

---

## FIX 4 — AI harus jawab pertanyaan kandidat di fase closing/farewell

**File**: `backend/app/services/brain.py`

**Root cause**: `PHASE_INSTRUCTIONS[InterviewPhase.closing]` (turn ke-9) menyuruh AI bertanya "Apakah ada pertanyaan yang ingin Anda ajukan kepada kami?" — tapi begitu kandidat menjawab dengan pertanyaan balik, jawaban itu masuk sebagai `new_answer_transcript` biasa untuk generate turn berikutnya (turn ke-10 = fase `farewell`). Instruksi `PHASE_INSTRUCTIONS[InterviewPhase.farewell]` sama sekali tidak menyuruh LLM memeriksa/menjawab isi jawaban kandidat sebelumnya — hanya berisi script satu arah (apresiasi + next steps + salam penutup). LLM akhirnya mengabaikan pertanyaan kandidat sepenuhnya.

**Task**:
1. Edit string `PHASE_INSTRUCTIONS[InterviewPhase.farewell]`, tambahkan instruksi baru SEBELUM langkah "Ucapkan apresiasi..." yang sudah ada, kurang lebih:
   - Periksa isi jawaban kandidat di giliran sebelumnya (fase closing). Jika kandidat mengajukan pertanyaan di dalamnya:
     - Jika pertanyaan itu bisa dijawab wajar dalam konteks institusi/posisi yang tersedia (`{institution.llmContext}`, `{position.llmContext}`) → jawab singkat (1-2 kalimat) dengan natural SEBELUM masuk ke script penutup.
     - Jika pertanyaan itu di luar kewenangan/informasi yang kamu punya (mis. gaji spesifik, jadwal internal) → akui dengan sopan bahwa itu akan diinfokan tim rekrutmen terkait, JANGAN mengarang jawaban, dan tetap lanjut ke script penutup.
   - Jika kandidat TIDAK mengajukan pertanyaan apapun (mis. jawab "tidak ada" atau langsung closing statement tentang dirinya) → langsung lanjut script penutup seperti biasa (behavior existing dipertahankan).
2. Instruksi tambahan ini HARUS eksplisit menyebut bahwa ini tetap SATU giliran terakhir (tidak boleh berubah jadi tanya-jawab panjang) — jawab pertanyaan kandidat secara ringkas lalu tetap lanjut ke closing statement dalam giliran yang sama.
3. **Jangan ubah** logic Python di `handle_user_answer()`/`send_next_question_stream()` — ini murni perubahan teks instruksi/prompt.

---

## FIX 5 — Persingkat kalimat yang digenerate AI

**File**: `backend/app/services/brain.py`

**Task**:
1. Di `format_instruction` (kedua varian, non-streaming dan streaming), tambahkan batasan panjang eksplisit, misal:
   - `feedback`: maksimal 1 kalimat pendek.
   - `question`: maksimal 1-2 kalimat, hindari sub-klausa bertumpuk.
2. Tambahkan instruksi umum di system prompt (section `=== ATURAN SESI ===` yang sudah ada, tambah 1 baris): larang jawaban/pertanyaan yang bertele-tele; gaya bicara natural seperti pewawancara sungguhan berbicara langsung, bukan menulis esai.
3. Opsional (diskusikan sebelum diterapkan — ada trade-off): turunkan `max_tokens` di `generate_next_turn_stream()` dan `generate_next_turn()` dari `256` sedikit (misal `180`) HANYA jika setelah perubahan instruksi di atas hasil masih sering panjang. Jangan turunkan dulu di iterasi pertama — uji instruksi prompt-nya dulu, karena menurunkan `max_tokens` terlalu agresif berisiko memotong kalimat/JSON di tengah (terutama pada mode streaming yang parsing `[QUESTION]` tag manual).

---

## Verification checklist (setelah semua fix diterapkan)
- [ ] Chrome: mulai interview beberapa kali berturut-turut (termasuk dengan cache dingin agar load avatar lambat) — pastikan tidak ada lagi "Koneksi terputus" saat starting.
- [ ] Brave: mulai interview, JANGAN sentuh tombol "Kirim Jawaban" manual — pastikan audio tetap ter-auto-send lewat VAD walau live caption tetap kosong/error network.
- [ ] Chrome: pastikan auto-send masih berfungsi sama persis seperti sebelumnya (tidak ada regresi delay/timing).
- [ ] Cek beberapa giliran percakapan: feedback+pertanyaan AI terasa lebih natural (ada jeda/interjeksi kadang-kadang, tidak di semua giliran) dan lebih ringkas.
- [ ] Sampai ke fase closing (turn 9), jawab dengan pertanyaan balik ke AI (mis. "boleh tanya soal jenjang karir?") — pastikan turn farewell (turn 10) menjawabnya dulu sebelum closing statement.
- [ ] Sampai ke fase closing, jawab tanpa pertanyaan balik — pastikan farewell tetap berjalan seperti sebelumnya (no regression).
