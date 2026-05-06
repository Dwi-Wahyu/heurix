<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { fade, fly } from 'svelte/transition';
  import {
    FaceLandmarker,
    FilesetResolver,
    DrawingUtils
  } from "@mediapipe/tasks-vision";

  // Elements
  let videoElement: HTMLVideoElement;
  let canvasElement: HTMLCanvasElement;
  let canvasCtx: CanvasRenderingContext2D;
  
  // MediaPipe & Audio State
  let faceLandmarker: FaceLandmarker | undefined;
  let drawingUtils: DrawingUtils | undefined;
  let recognition: any = null;
  let requestId: number;
  let lastVideoTime = -1;
  let socket: WebSocket | null = null;

  // --- REAKTIF STATE (Svelte 5 Runes) ---
  let fps = $state(0);
  let transcript = $state('');
  let isListening = $state(false);
  let isVoiceActive = $state(false); 
  let dominantEmotion = $state({ label: 'NEUTRAL', emoji: '😐', color: 'text-neutral-400' });
  let aiResponse = $state('');
  let isAiProcessing = $state(false); 
  let wsStatus = $state('DISCONNECTED');
  let isInterviewStarted = $state(false);
  
  let frameCount = 0;
  let lastFpsUpdate = 0;
  let lastEmotionSent = 0;
  let transcriptTimeout: ReturnType<typeof setTimeout> | undefined;

  // --- LOGIKA TTS (Text to Speech) ---
  function speak(text: string) {
    if (!browser) return;
    
    // Stop recognition to avoid hearing itself
    const wasListening = isListening;
    if (wasListening && recognition) {
      recognition.stop();
      isListening = false;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'id-ID';
    utterance.rate = 1.1; // Sedikit lebih cepat agar tidak membosankan
    utterance.pitch = 1.0;

    utterance.onend = () => {
      // Restart recognition after speaking
      if (wasListening && recognition) {
        recognition.start();
        isListening = true;
      }
    };

    window.speechSynthesis.speak(utterance);
  }

  // --- LOGIKA AUDIO (Web Speech API) ---
  function setupSpeechRecognition() {
    if (!browser) return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) return;

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'id-ID'; 

    recognition.onresult = (event: any) => {
      isVoiceActive = true;
      let currentTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        currentTranscript += event.results[i][0].transcript;
      }
      
      if (currentTranscript.trim()) {
        transcript = currentTranscript;
        if (transcriptTimeout) clearTimeout(transcriptTimeout);
        
        transcriptTimeout = setTimeout(() => {
          if (socket && socket.readyState === WebSocket.OPEN && transcript.trim()) {
            console.log("Sending transcript to backend:", transcript);
            isAiProcessing = true; 
            aiResponse = ''; 
            socket.send(JSON.stringify({ 
              type: "TRANSCRIPT_FINISH", 
              text: transcript,
              metadata: { emotion: dominantEmotion.label }
            }));
          }
          transcript = '';
          isVoiceActive = false;
        }, 3000);
      }
    };

    recognition.onerror = (e: any) => { 
      console.error("Speech Recognition Error:", e);
      isListening = false; 
      isVoiceActive = false; 
    };
    recognition.onend = () => { if (isListening) recognition.start(); };
  }

  function toggleSpeech() {
    if (!recognition) return;
    isListening ? recognition.stop() : recognition.start();
    isListening = !isListening;
  }

  function startInterview() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      isInterviewStarted = true;
      isAiProcessing = true;
      socket.send(JSON.stringify({ type: "START_INTERVIEW" }));
      if (!isListening) toggleSpeech();
    }
  }

  // --- LOGIKA VISUAL & EMOSI (MediaPipe) ---
  async function initMediaPipe() {
    const vision = await FilesetResolver.forVisionTasks("/wasm");
    faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: `/models/face_landmarker.task`, delegate: "GPU" },
      runningMode: "VIDEO",
      outputFaceBlendshapes: true,
      numFaces: 1
    });
    canvasCtx = canvasElement.getContext("2d")!;
    drawingUtils = new DrawingUtils(canvasCtx);
  }

  async function predictWebcam() {
    if (!faceLandmarker || !drawingUtils) return;

    if (canvasElement.width !== videoElement.videoWidth || canvasElement.height !== videoElement.videoHeight) {
      canvasElement.width = videoElement.videoWidth;
      canvasElement.height = videoElement.videoHeight;
    }

    if (lastVideoTime !== videoElement.currentTime) {
      lastVideoTime = videoElement.currentTime;
      const results = faceLandmarker.detectForVideo(videoElement, performance.now());
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
      
      if (results.faceLandmarks?.[0]) {
        const landmarks = results.faceLandmarks[0];
        drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_TESSELATION, { color: "#C0C0C020", lineWidth: 1 });
        drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_LIPS, { color: "#FF3030", lineWidth: 2 });

        if (results.faceBlendshapes?.[0]) {
          const s = results.faceBlendshapes[0].categories.reduce((acc: any, curr) => {
            acc[curr.categoryName] = curr.score;
            return acc;
          }, {});

          if (s.jawOpen > 0.3 && s.eyeWideLeft > 0.4) {
            dominantEmotion = { label: 'SURPRISED', emoji: '😲', color: 'text-yellow-400' };
          } else if (s.mouthSmileLeft > 0.4 || s.mouthSmileRight > 0.4) {
            dominantEmotion = { label: 'HAPPY', emoji: '😊', color: 'text-emerald-400' };
          } else if (s.browInnerUp > 0.2 && s.mouthFrownLeft > 0.1) {
            dominantEmotion = { label: 'SAD', emoji: '😢', color: 'text-blue-400' };
          } else if (s.browDownLeft > 0.4 && s.eyeSquintLeft > 0.2) {
            dominantEmotion = { label: 'ANGRY', emoji: '😠', color: 'text-red-500' };
          } else {
            dominantEmotion = { label: 'NEUTRAL', emoji: '😐', color: 'text-neutral-400' };
          }

          const nowMs = performance.now();
          if (socket && socket.readyState === WebSocket.OPEN && nowMs - lastEmotionSent > 500) {
            socket.send(JSON.stringify({ type: "EMOTION", label: dominantEmotion.label }));
            lastEmotionSent = nowMs;
          }
        }
      } else {
        dominantEmotion = { label: 'NO FACE', emoji: '😶', color: 'text-neutral-600' };
      }

      frameCount++;
      const now = performance.now();
      if (now - lastFpsUpdate > 1000) {
        fps = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
        frameCount = 0; lastFpsUpdate = now;
      }
    }
    requestId = requestAnimationFrame(predictWebcam);
  }

  let heartbeatInterval: ReturnType<typeof setInterval> | undefined;

  function connectWebSocket() {
    wsStatus = 'CONNECTING';
    
    // Deteksi otomatis URL Backend (Gunakan IP laptop, bukan localhost)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname; // Akan jadi 192.168.1.21 sesuai IP Anda
    const wsUrl = `${protocol}//${host}:8000/ws/interview`;
    
    console.log("Connecting to WebSocket:", wsUrl);
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
      console.log('WebSocket Connected');
      wsStatus = 'CONNECTED';
      
      // Mulai Heartbeat agar koneksi tidak timeout
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      heartbeatInterval = setInterval(() => {
        if (socket?.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "PING" }));
        }
      }, 5000);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'PONG') return; // Abaikan respons heartbeat
      
      console.log("Message from AI:", data);
      if (data.type === 'AI_RESPONSE') {
        aiResponse = data.content;
        isAiProcessing = false; 
        speak(aiResponse);
      }
    };

    socket.onclose = (e) => {
      console.log('WebSocket Disconnected:', e.reason);
      wsStatus = 'DISCONNECTED';
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      // Auto reconnect
      setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      wsStatus = 'ERROR';
    };
  }

  onMount(async () => {
    document.body.style.overflow = 'hidden';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    document.body.style.height = '100%';
    document.body.style.background = 'black';

    connectWebSocket();
    setupSpeechRecognition();
    await initMediaPipe();
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
    videoElement.srcObject = stream;
    videoElement.addEventListener("loadeddata", predictWebcam);
  });

  onDestroy(() => {
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';
    document.body.style.height = '';
    document.body.style.background = '';

    if (requestId) cancelAnimationFrame(requestId);
    if (faceLandmarker) faceLandmarker.close();
    if (recognition) recognition.stop();
    if (videoElement?.srcObject) (videoElement.srcObject as MediaStream).getTracks().forEach(t => t.stop());
    if (socket) socket.close();
  });
</script>

<div class="flex flex-col h-screen bg-black text-white font-sans overflow-hidden">
  <!-- Status Bar -->
  <header class="flex justify-between items-center px-4 md:px-6 py-3 border-b border-white/5 bg-neutral-900/50 backdrop-blur-xl z-30">
    <div class="flex items-center gap-2 md:gap-4">
      <div class="px-1.5 py-0.5 md:px-2 md:py-1 bg-red-600 text-[8px] md:text-[10px] font-black rounded uppercase tracking-tighter">Live</div>
      <h1 class="text-[10px] md:text-xs font-bold tracking-widest text-neutral-400 uppercase truncate max-w-[120px] md:max-w-none">HireReady Engine</h1>
    </div>
    <div class="flex items-center gap-3 md:gap-6">
      <div class="flex items-center gap-1.5">
        <div class="w-1.5 h-1.5 rounded-full {wsStatus === 'CONNECTED' ? 'bg-emerald-500' : wsStatus === 'CONNECTING' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}"></div>
        <span class="text-[8px] md:text-[10px] font-bold text-neutral-500 uppercase">{wsStatus}</span>
      </div>
      <div class="flex items-center gap-1.5 md:gap-2">
        <div class="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full {isListening ? 'bg-blue-500 animate-pulse' : 'bg-neutral-600'}"></div>
        <span class="text-[8px] md:text-[10px] font-bold uppercase text-neutral-500">{isListening ? 'Mic On' : 'Muted'}</span>
      </div>
      <div class="hidden sm:flex items-center gap-2">
        <span class="text-base md:text-lg font-black text-emerald-500 tabular-nums">{fps}</span>
        <span class="text-[8px] md:text-[10px] font-bold text-neutral-600 uppercase">FPS</span>
      </div>
    </div>
  </header>

  <main class="flex-1 relative flex flex-col md:flex-row overflow-hidden">
    <!-- Main Viewport -->
    <div class="flex-1 relative bg-[#050505] overflow-hidden">
      <video bind:this={videoElement} autoplay playsinline muted class="w-full h-full object-cover mirror"></video>
      <canvas bind:this={canvasElement} class="absolute top-0 left-0 w-full h-full mirror pointer-events-none"></canvas>
      
      <!-- Start Overlay -->
      {#if !isInterviewStarted}
        <div class="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md" transition:fade>
          <div class="text-center p-8 bg-neutral-900/80 border border-white/10 rounded-3xl shadow-2xl max-w-md">
            <h2 class="text-3xl font-black mb-4 italic tracking-tighter">Siap Untuk Di-Roast?</h2>
            <p class="text-neutral-400 text-sm mb-8 leading-relaxed">
              Tekan tombol di bawah untuk memulai sesi simulasi wawancara kerja berbasis AI. 
              Gunakan headphone untuk pengalaman terbaik.
            </p>
            <button 
              onclick={startInterview}
              disabled={wsStatus !== 'CONNECTED'}
              class="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-neutral-800 disabled:text-neutral-500 text-white font-bold rounded-2xl transition-all active:scale-95 flex items-center justify-center gap-3"
            >
              {#if wsStatus === 'CONNECTED'}
                <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                </svg>
                MULAI WAWANCARA
              {:else}
                MENUNGGU SERVER...
              {/if}
            </button>
          </div>
        </div>
      {/if}

      <!-- Emotion HUD -->
      <div class="absolute top-4 left-4 md:top-8 md:left-8 z-10">
        <div class="bg-black/60 backdrop-blur-xl border border-white/10 p-3 md:p-5 rounded-2xl md:rounded-3xl shadow-2xl min-w-[140px] md:min-w-[200px]">
          <span class="text-[8px] md:text-[10px] font-black uppercase text-neutral-500 tracking-widest block mb-1 md:mb-2">Analysis</span>
          <div class="flex items-center gap-2 md:gap-4">
            <span class="text-2xl md:text-4xl">{dominantEmotion.emoji}</span>
            <div>
              <p class="text-lg md:text-2xl font-black italic tracking-tighter {dominantEmotion.color} leading-none">{dominantEmotion.label}</p>
              <p class="text-[8px] md:text-[10px] text-neutral-500 font-bold uppercase mt-1">Live Feed</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Subtitles (Voice Detect) -->
      {#if transcript}
        <div class="absolute bottom-24 md:bottom-20 left-0 right-0 flex justify-center px-4 md:px-10 z-10">
          <div class="bg-black/80 backdrop-blur-2xl border border-white/10 px-4 py-3 md:px-8 md:py-5 rounded-xl md:rounded-2xl max-w-full md:max-w-3xl shadow-2xl">
            <div class="flex items-center gap-2 mb-1">
              <div class="w-1 h-1 rounded-full bg-blue-500 {isVoiceActive ? 'animate-ping' : ''}"></div>
              <span class="text-[8px] md:text-[10px] font-black text-blue-400 uppercase tracking-widest">Listening</span>
            </div>
            <p class="text-sm md:text-xl font-bold leading-snug text-white tracking-tight italic line-clamp-3 md:line-clamp-none">
              "{transcript}"
            </p>
          </div>
        </div>
      {/if}

      <!-- AI Feedback Panel -->
      {#if aiResponse || isAiProcessing}
        <div 
          transition:fly={{ y: 50, duration: 500 }}
          class="absolute inset-x-4 bottom-24 md:inset-x-auto md:top-8 md:right-8 md:bottom-auto md:w-80 z-40"
        >
          <div class="bg-indigo-950/80 md:bg-indigo-950/40 backdrop-blur-3xl border border-indigo-500/30 p-4 md:p-6 rounded-2xl md:rounded-3xl shadow-2xl ring-1 ring-white/10">
            <div class="flex items-center justify-between mb-2 md:mb-4">
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-1.5 rounded-full bg-indigo-500 {isAiProcessing ? 'animate-pulse' : ''}"></div>
                <span class="text-[9px] md:text-[10px] font-black uppercase text-indigo-300 tracking-widest">AI Interviewer</span>
              </div>
              <button onclick={() => { aiResponse = ''; isAiProcessing = false; }} class="p-1 text-neutral-500 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {#if isAiProcessing}
              <div class="py-4 space-y-3">
                <div class="h-4 bg-indigo-500/20 rounded animate-pulse w-3/4"></div>
                <div class="h-4 bg-indigo-500/20 rounded animate-pulse w-full"></div>
                <p class="text-[10px] text-indigo-400 font-bold uppercase animate-pulse">Menyiapkan feedback & pertanyaan...</p>
              </div>
            {:else}
              <div class="max-h-[30vh] md:max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
                <div class="prose prose-invert prose-xs md:prose-sm">
                  <p class="text-xs md:text-sm text-indigo-100/90 leading-relaxed italic whitespace-pre-wrap">
                    {aiResponse}
                  </p>
                </div>
              </div>
            {/if}

            <div class="mt-3 md:mt-4 pt-3 md:pt-4 border-t border-white/5 flex justify-between items-center">
              <span class="text-[8px] md:text-[9px] font-bold text-indigo-400 uppercase tracking-tighter">Status: Interviewing</span>
              <div class="flex gap-1">
                <div class="w-1 h-1 rounded-full bg-indigo-500/50"></div>
                <div class="w-1 h-1 rounded-full bg-indigo-500/30"></div>
              </div>
            </div>
          </div>
        </div>
      {/if}

      <!-- Awkward Silence Warning -->
      {#if isVoiceActive && !transcript && isInterviewStarted}
         <div class="absolute top-20 left-0 right-0 flex justify-center z-10" transition:fade>
            <div class="px-4 py-2 bg-yellow-500/20 border border-yellow-500/50 rounded-full backdrop-blur-md">
              <p class="text-[10px] font-bold text-yellow-500 uppercase tracking-widest animate-pulse">
                Suara terdeteksi, tapi teks belum muncul... Coba bicara lebih keras?
              </p>
            </div>
         </div>
      {/if}

      <!-- Quick Action Floating Button -->
      <div class="absolute bottom-6 right-6 md:bottom-8 md:right-8 flex flex-col gap-3 z-30">
        <button 
          onclick={toggleSpeech}
          class="p-3 md:p-4 rounded-full backdrop-blur-xl border transition-all active:scale-95 shadow-xl
          {isListening ? 'bg-blue-600/30 border-blue-500 text-blue-400' : 'bg-neutral-900/80 border-white/10 text-neutral-500'}"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 md:w-6 md:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-20a3 3 0 00-3 3v8a3 3 0 003 3s3-3 3-3V5a3 3 0 00-3-3z" />
          </svg>
        </button>
      </div>
    </div>
  </main>
</div>

<style>
  .mirror { transform: scaleX(-1); }
  
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.2); border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.4); }

  :global(.prose-xs) { font-size: 0.75rem; line-height: 1.25rem; }
</style>