<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
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

  // --- REAKTIF STATE (Svelte 5 Runes) ---
  let fps = $state(0);
  let transcript = $state('');
  let isListening = $state(false);
  let isVoiceActive = $state(false); // Indikator suara masuk
  let dominantEmotion = $state({ label: 'NEUTRAL', emoji: '😐', color: 'text-neutral-400' });
  
  let frameCount = 0;
  let lastFpsUpdate = 0;
  let transcriptTimeout: ReturnType<typeof setTimeout> | undefined;

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
          transcript = '';
          isVoiceActive = false;
        }, 3000);
      }
    };

    recognition.onerror = () => { isListening = false; isVoiceActive = false; };
    recognition.onend = () => { if (isListening) recognition.start(); };
  }

  function toggleSpeech() {
    if (!recognition) return;
    isListening ? recognition.stop() : recognition.start();
    isListening = !isListening;
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
        // Gambar Mesh halus
        drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_TESSELATION, { color: "#C0C0C020", lineWidth: 1 });
        drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_LIPS, { color: "#FF3030", lineWidth: 2 });

        // LOGIKA DETEKSI EMOSI (Berdasarkan 52 Blendshapes MediaPipe)
        if (results.faceBlendshapes?.[0]) {
          const s = results.faceBlendshapes[0].categories.reduce((acc: any, curr) => {
            acc[curr.categoryName] = curr.score;
            return acc;
          }, {});

          // Thresholding untuk emosi yang lebih akurat
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
        }
      } else {
        dominantEmotion = { label: 'NO FACE', emoji: '😶', color: 'text-neutral-600' };
      }

      // FPS
      frameCount++;
      const now = performance.now();
      if (now - lastFpsUpdate > 1000) {
        fps = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
        frameCount = 0; lastFpsUpdate = now;
      }
    }
    requestId = requestAnimationFrame(predictWebcam);
  }

  onMount(async () => {
    setupSpeechRecognition();
    await initMediaPipe();
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
    videoElement.srcObject = stream;
    videoElement.addEventListener("loadeddata", predictWebcam);
    toggleSpeech();
  });

  onDestroy(() => {
    if (requestId) cancelAnimationFrame(requestId);
    faceLandmarker?.close();
    recognition?.stop();
    (videoElement?.srcObject as MediaStream)?.getTracks().forEach(t => t.stop());
  });
</script>

<div class="flex flex-col h-screen bg-black text-white font-sans overflow-hidden">
  <!-- Status Bar -->
  <header class="flex justify-between items-center px-6 py-3 border-b border-white/5 bg-neutral-900/50 backdrop-blur-xl z-20">
    <div class="flex items-center gap-4">
      <div class="px-2 py-1 bg-red-600 text-[10px] font-black rounded uppercase tracking-tighter">Live Engine</div>
      <h1 class="text-xs font-bold tracking-widest text-neutral-400 uppercase">MediaPipe Multimodal v2</h1>
    </div>
    <div class="flex items-center gap-6">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full {isListening ? 'bg-blue-500 animate-pulse' : 'bg-neutral-600'}"></div>
        <span class="text-[10px] font-bold uppercase text-neutral-500">Audio: {isListening ? 'On' : 'Off'}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-lg font-black text-emerald-500 tabular-nums">{fps}</span>
        <span class="text-[10px] font-bold text-neutral-600 uppercase">FPS</span>
      </div>
    </div>
  </header>

  <main class="flex-1 relative flex">
    <!-- Main Viewport -->
    <div class="flex-1 relative bg-[#050505]">
      <video bind:this={videoElement} autoplay playsinline muted class="w-full h-full object-cover mirror"></video>
      <canvas bind:this={canvasElement} class="absolute top-0 left-0 w-full h-full mirror pointer-events-none"></canvas>
      
      <!-- Emotion HUD -->
      <div class="absolute top-8 left-8">
        <div class="bg-black/60 backdrop-blur-xl border border-white/10 p-5 rounded-3xl shadow-2xl min-w-[200px]">
          <span class="text-[10px] font-black uppercase text-neutral-500 tracking-widest block mb-2">Face Analysis</span>
          <div class="flex items-center gap-4">
            <span class="text-4xl">{dominantEmotion.emoji}</span>
            <div>
              <p class="text-2xl font-black italic tracking-tighter {dominantEmotion.color}">{dominantEmotion.label}</p>
              <p class="text-[10px] text-neutral-500 font-bold uppercase">Confidence: High</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Subtitles (Voice Detect) -->
      {#if transcript}
        <div class="absolute bottom-20 left-0 right-0 flex justify-center px-10 z-10">
          <div class="bg-black/80 backdrop-blur-2xl border border-white/10 px-8 py-5 rounded-2xl max-w-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] transform transition-all scale-105">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-1.5 h-1.5 rounded-full bg-blue-500 {isVoiceActive ? 'animate-ping' : ''}"></div>
              <span class="text-[10px] font-black text-blue-400 uppercase tracking-widest">Voice Detected</span>
            </div>
            <p class="text-xl md:text-2xl font-bold leading-snug text-white tracking-tight italic">
              "{transcript}"
            </p>
          </div>
        </div>
      {/if}

      <!-- Quick Action Floating Button -->
      <div class="absolute bottom-8 right-8 flex gap-4">
        <button 
          onclick={toggleSpeech}
          class="p-4 rounded-full backdrop-blur-xl border transition-all active:scale-95
          {isListening ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-neutral-900 border-white/10 text-neutral-500'}"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-20a3 3 0 00-3 3v8a3 3 0 003 3s3-3 3-3V5a3 3 0 00-3-3z" />
          </svg>
        </button>
      </div>
    </div>
  </main>
</div>

<style>
  .mirror { transform: scaleX(-1); }
  :global(body) { background: black; }
</style>
