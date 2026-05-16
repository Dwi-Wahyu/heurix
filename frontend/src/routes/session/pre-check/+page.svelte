<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import {
		FaceLandmarker,
		FilesetResolver,
		DrawingUtils
	} from "@mediapipe/tasks-vision";
	import { VideoOff, Mic, Info, ArrowRight } from '@lucide/svelte';

	// ── Props & State ──
	let sessionId = $state<string | null>(null);
	let videoElement = $state<HTMLVideoElement | null>(null);
	let canvasElement = $state<HTMLCanvasElement | null>(null);
	let canvasCtx: CanvasRenderingContext2D | null = null;
	
	// MediaPipe State
	let faceLandmarker: FaceLandmarker | undefined;
	let drawingUtils: DrawingUtils | undefined;
	let requestId: number;
	let lastVideoTime = -1;
	let faceDetected = $state(false);

	// Audio State
	let audioContext: AudioContext | null = null;
	let analyser: AnalyserNode | null = null;
	let microphone: MediaStreamAudioSourceNode | null = null;
	let volume = $state(0);
	let isVoiceDetected = $derived(volume > 10); // Threshold simple

	let stream: MediaStream | null = null;
	let error = $state<string | null>(null);
	let initializing = $state(true);

	onMount(async () => {
		sessionId = page.url.searchParams.get('sessionId');
		if (!sessionId) {
			goto('/dashboard');
			return;
		}

		try {
			await initMediaPipe();
			await startCamera();
			await startAudioCheck();
			initializing = false;
		} catch (err: any) {
			console.error("Initialization failed:", err);
			error = "Gagal mengakses kamera atau mikrofon. Pastikan izin telah diberikan.";
			initializing = false;
		}
	});

	onDestroy(() => {
		if (requestId) cancelAnimationFrame(requestId);
		faceLandmarker?.close();
		stream?.getTracks().forEach(t => t.stop());
		audioContext?.close();
	});

	async function initMediaPipe() {
		const vision = await FilesetResolver.forVisionTasks("/wasm");
		faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
			baseOptions: { 
				modelAssetPath: `/models/face_landmarker.task`, 
				delegate: "GPU" 
			},
			runningMode: "VIDEO",
			outputFaceBlendshapes: true,
			numFaces: 1
		});
		if (canvasElement) {
			canvasCtx = canvasElement.getContext("2d");
			drawingUtils = new DrawingUtils(canvasCtx!);
		}
	}

	async function startCamera() {
		stream = await navigator.mediaDevices.getUserMedia({ 
			video: { width: 1280, height: 720 },
			audio: true 
		});
		if (videoElement) {
			videoElement.srcObject = stream;
			videoElement.addEventListener("loadeddata", predictWebcam);
		}
	}

	async function startAudioCheck() {
		if (!stream) return;
		audioContext = new AudioContext();
		analyser = audioContext.createAnalyser();
		analyser.fftSize = 256;
		microphone = audioContext.createMediaStreamSource(stream);
		microphone.connect(analyser);

		const dataArray = new Uint8Array(analyser.frequencyBinCount);
		const checkVolume = () => {
			if (!analyser) return;
			analyser.getByteFrequencyData(dataArray);
			let sum = 0;
			for (let i = 0; i < dataArray.length; i++) {
				sum += dataArray[i];
			}
			volume = sum / dataArray.length;
			requestId = requestAnimationFrame(checkVolume);
		};
		checkVolume();
	}

	async function predictWebcam() {
		if (!faceLandmarker || !drawingUtils || !videoElement || !canvasElement || !canvasCtx) return;

		if (canvasElement.width !== videoElement.videoWidth || canvasElement.height !== videoElement.videoHeight) {
			canvasElement.width = videoElement.videoWidth;
			canvasElement.height = videoElement.videoHeight;
		}

		if (lastVideoTime !== videoElement.currentTime) {
			lastVideoTime = videoElement.currentTime;
			const results = faceLandmarker.detectForVideo(videoElement, performance.now());
			canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
			
			if (results.faceLandmarks?.[0]) {
				faceDetected = true;
				const landmarks = results.faceLandmarks[0];
				drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_TESSELATION, { color: "#C0C0C070", lineWidth: 1 });
				drawingUtils.drawConnectors(landmarks, FaceLandmarker.FACE_LANDMARKS_LIPS, { color: "#FF3030", lineWidth: 2 });
			} else {
				faceDetected = false;
			}
		}
		requestId = requestAnimationFrame(predictWebcam);
	}

	function handleContinue() {
		goto(`/session/interview?sessionId=${sessionId}`);
	}
</script>

<svelte:head>
	<title>Cek Perangkat — Heurix</title>
</svelte:head>

<div class="flex min-h-screen flex-col bg-neutral-950 font-sans text-white">
	<main class="flex flex-1 flex-col items-center justify-center p-4 md:p-8">
		<div class="w-full max-w-4xl space-y-8">
			<!-- Header -->
			<div class="text-center">
				<h1 class="text-2xl font-bold tracking-tight md:text-3xl">Pengecekan Terakhir</h1>
				<p class="mt-2 text-neutral-400">Pastikan wajah Anda terlihat jelas dan mikrofon merespon suara Anda.</p>
			</div>

			<!-- Camera Preview -->
			<div class="relative aspect-video overflow-hidden rounded-3xl border border-white/10 bg-neutral-900 shadow-2xl">
				{#if initializing}
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-neutral-900 z-20">
						<div class="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
						<p class="mt-4 text-sm text-neutral-400">Menyiapkan kamera...</p>
					</div>
				{/if}

				{#if error}
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-neutral-900/90 z-30 p-6 text-center">
						<VideoOff size={48} class="text-error mb-4" />
						<p class="text-error font-medium">{error}</p>
						<button onclick={() => window.location.reload()} class="mt-6 rounded-full bg-white/10 px-6 py-2 text-sm font-semibold hover:bg-white/20 transition-colors">
							Muat Ulang Halaman
						</button>
					</div>
				{/if}

				<video 
					bind:this={videoElement} 
					autoplay 
					playsinline 
					muted 
					class="h-full w-full object-cover -scale-x-100"
				></video>
				<canvas 
					bind:this={canvasElement} 
					class="absolute inset-0 h-full w-full -scale-x-100 pointer-events-none"
				></canvas>

				<!-- Status Badges -->
				<div class="absolute top-4 left-4 flex flex-col gap-2 z-10">
					<div class="flex items-center gap-2 rounded-full bg-black/60 px-3 py-1.5 backdrop-blur-md border border-white/10">
						<div class="h-2 w-2 rounded-full {faceDetected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}"></div>
						<span class="text-[11px] font-bold uppercase tracking-wider">
							{faceDetected ? 'Wajah Terdeteksi' : 'Wajah Tidak Terdeteksi'}
						</span>
					</div>
				</div>
			</div>

			<!-- Mic Indicator & Info -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="rounded-2xl border border-white/5 bg-white/5 p-6 backdrop-blur-sm">
					<h3 class="flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-neutral-500 mb-4">
						<Mic size={18} />
						Indikator Suara
					</h3>
					<div class="flex items-center gap-4">
						<div class="flex-1 h-3 bg-neutral-800 rounded-full overflow-hidden">
							<div 
								class="h-full bg-gradient-to-r from-primary to-primary-container transition-all duration-75"
								style="width: {Math.min(volume * 2, 100)}%"
							></div>
						</div>
						
					</div>
					<div class=" w-full text-end mt-4">
							{#if isVoiceDetected}
								<span class="text-xs font-bold text-emerald-400 animate-pulse" transition:fade>TERDETEKSI</span>
							{:else}
								<span class="text-xs font-bold text-neutral-600">MENUNGGU...</span>
							{/if}
						</div>
					<p class="mt-4 text-xs text-neutral-500 italic">Silakan bicara sejenak untuk mengetes mikrofon Anda.</p>
				</div>

				<div class="rounded-2xl border border-white/5 bg-white/5 p-4 backdrop-blur-sm flex flex-col justify-center">
					<div class="flex items-start gap-4">
						<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
							<Info size={20} />
						</div>
						<div>
							<h4 class="text-sm font-bold">Analisis Mimik Wajah</h4>
							<p class="mt-1 text-xs text-neutral-400 leading-relaxed">
								Aplikasi kami akan menganalisis ekspresi wajah Anda untuk memberikan feedback tentang kepercayaan diri dan ketenangan Anda.
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Footer Actions -->
			<div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/10">
				<button 
					onclick={() => goto('/session/disclaimer')}
					class="w-full sm:w-auto rounded-full px-8 py-3 font-bold text-neutral-400 hover:text-white hover:bg-white/5 transition-all"
				>
					Kembali
				</button>
				<button 
					onclick={handleContinue}
					disabled={!faceDetected || initializing}
					class="w-full sm:w-auto flex items-center justify-center gap-3 rounded-full bg-primary px-12 py-4 font-bold text-white shadow-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:scale-100"
				>
					<span>Lanjutkan ke Interview</span>
					<ArrowRight size={20} />
				</button>
			</div>
		</div>
	</main>
</div>

<style>
	:global(body) {
		background-color: #0a0a0a;
	}
</style>