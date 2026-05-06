<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/state';
	import { FaceAnimator } from '$lib/FaceAnimator';
	import { speakWithBackend, unlockAudio } from '$lib/lipSync';
	import { startAutoBlink } from '$lib/autoBlink';
	import { EMOTIONS } from '$lib/emotionPresets';
	import { PUBLIC_BACKEND_WS } from '$env/static/public';
	import { loadGLBCached } from '$lib/avatarCache';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
	import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';

	import { browser } from '$app/environment';
	import { fade } from 'svelte/transition';

	// ── Media ──
	let videoElementDesktop = $state<HTMLVideoElement | null>(null);
	let videoElementMobile = $state<HTMLVideoElement | null>(null);
	let canvasElement: HTMLCanvasElement;
	let stream = $state<MediaStream | null>(null);
	let micMuted = $state(false);
	let camOff = $state(false);

	// ── Session & WebSocket ──
	let sessionId = $state<string | null>(null);
	let ws = $state<WebSocket | null>(null);
	let wsStatus = $state<'connecting' | 'connected' | 'disconnected'>('connecting');

	// ── Percakapan ──
	type Message = { role: 'interviewer' | 'user'; text: string; time: string };
	let messages = $state<Message[]>([]);
	let isListening = $state(false);
	let isSpeaking = $state(false);
	let transcriptOpen = $state(false);
	let liveTranscript = $state('');
	let isVoiceActive = $state(false);
	let messagesContainer = $state<HTMLElement | null>(null);
	let audioBlocked = $state(false);
	let errorMessage = $state<string | null>(null);
	let processingResult = $state(false);

	// ── Avatar (Three.js) ──
	let animator: FaceAnimator | null = null;
	let stopBlink: (() => void) | null = null;
	let avatarReady = $state(false);
	let avatarLoadProgress = $state(0);

	// ── STT (MediaRecorder & Web Speech API) ──
	let mediaRecorder: MediaRecorder | null = null;
	let audioChunks: Blob[] = [];
	let recognition: any = null;

	// ── Timer ──
	let seconds = $state(0);
	let timerInterval: ReturnType<typeof setInterval>;
	const timeDisplay = () => {
		const m = Math.floor(seconds / 60)
			.toString()
			.padStart(2, '0');
		const s = (seconds % 60).toString().padStart(2, '0');
		return `${m}:${s}`;
	};

	// Auto-scroll saat pesan bertambah
	$effect(() => {
		if (messages.length || liveTranscript) {
			setTimeout(() => {
				if (messagesContainer) {
					messagesContainer.scrollTo({
						top: messagesContainer.scrollHeight,
						behavior: 'smooth'
					});
				}
			}, 100);
		}
	});

	// Sinkronisasi kamera ke elemen video (Svelte 5 Effect)
	$effect(() => {
		if (stream) {
			if (videoElementDesktop && videoElementDesktop.srcObject !== stream) {
				videoElementDesktop.srcObject = stream;
			}
			if (videoElementMobile && videoElementMobile.srcObject !== stream) {
				videoElementMobile.srcObject = stream;
			}
		}
	});

	// Otomatis mulai interview jika avatar siap dan WS terkoneksi
	let sessionStarted = $state(false);
	$effect(() => {
		if (wsStatus === 'connected' && avatarReady && ws && !sessionStarted) {
			sessionStarted = true;
			ws.send(JSON.stringify({ type: 'START_INTERVIEW', sessionId }));
		}
	});

	onMount(async () => {
		if (browser) {
			document.body.style.overflow = 'hidden';
		}
		timerInterval = setInterval(() => seconds++, 1000);
		sessionId = page.url.searchParams.get('sessionId');

		if (sessionId) {
			// 1. Ambil info sesi & avatar
			try {
				const { PUBLIC_BACKEND_URL } = await import('$env/static/public');
				let apiUrl = PUBLIC_BACKEND_URL;
				if (window.location.protocol === 'https:' && apiUrl.startsWith('http://')) {
					apiUrl = apiUrl.replace('http://', 'https://');
				}
				
				const res = await fetch(`${apiUrl}/api/sessions/${sessionId}`);
				if (!res.ok) throw new Error('Session not found');
				
				const sessionData = await res.json();
				const glbUrl = `/${sessionData.avatar.glbUrl}`;

				// 2. Avatar Three.js
				initAvatar(glbUrl);
			} catch (err) {
				console.error('Failed to load session details:', err);
				errorMessage = 'Gagal memuat detail sesi.';
			}

			// 3. WebSocket
			initWebSocket();
		}

		// 4. Kamera user
		navigator.mediaDevices
			.getUserMedia({ video: true, audio: true })
			.then((s) => {
				stream = s;
			})
			.catch((e) => {
				console.error('Camera access failed:', e);
			});

		// 5. Live STT (Web Speech API)
		initSpeechRecognition();
	});

	function initSpeechRecognition() {
		if (!browser) return;
		const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
		if (!SpeechRecognition) {
			console.warn('Speech Recognition not supported in this browser');
			return;
		}

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
				liveTranscript = currentTranscript;
			}
		};

		recognition.onerror = (e: any) => {
			console.error('Speech Recognition Error:', e);
			isVoiceActive = false;
		};

		recognition.onend = () => {
			isVoiceActive = false;
			if (isListening && !micMuted) {
				try {
					recognition.start();
				} catch (e) {}
			}
		};
	}

	onDestroy(() => {
		document.body.style.overflow = '';
		clearInterval(timerInterval);
		stream?.getTracks().forEach((t) => t.stop());
		ws?.close();
		stopBlink?.();
	});

	async function initAvatar(glbUrl: string) {
		if (!canvasElement) return;

		const renderer = new THREE.WebGLRenderer({
			canvas: canvasElement,
			alpha: true,
			antialias: true,
			powerPreference: 'high-performance'
		});
		
		const width = canvasElement.clientWidth || window.innerWidth;
		const height = canvasElement.clientHeight || window.innerHeight || 1;
		renderer.setSize(width, height);
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

		// Tone mapping for better visuals
		renderer.toneMapping = THREE.ACESFilmicToneMapping;
		renderer.toneMappingExposure = 1.2;
		renderer.shadowMap.enabled = true;
		renderer.shadowMap.type = THREE.PCFShadowMap;

		const scene = new THREE.Scene();

		const camera = new THREE.PerspectiveCamera(
			25, 
			width / height,
			0.01,
			100
		);
		camera.position.set(0, 1.6, 2.0);

		// ── PENCAHAYAAN ──
		const ambient = new THREE.AmbientLight(0xffffff, 0.8);
		scene.add(ambient);

		const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
		scene.add(hemiLight);

		const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
		keyLight.position.set(-1, 2, 4);
		keyLight.castShadow = true;
		keyLight.shadow.bias = -0.0001;
		keyLight.shadow.normalBias = 0.05;
		keyLight.shadow.mapSize.width = 1024;
		keyLight.shadow.mapSize.height = 1024;
		scene.add(keyLight);
		scene.add(keyLight.target); 

		const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
		fillLight.position.set(1, 1, 2);
		scene.add(fillLight);

		const rimLight = new THREE.DirectionalLight(0xffffff, 0.7);
		rimLight.position.set(0, 2, -3);
		scene.add(rimLight);

		const dracoLoader = new DRACOLoader();
		dracoLoader.setDecoderPath('/draco/');

		const loader = new GLTFLoader();
		loader.setDRACOLoader(dracoLoader);
		loader.setMeshoptDecoder(MeshoptDecoder);

		try {
			await new Promise<void>((resolve, reject) => {
				loader.load(
					glbUrl,
					(gltf) => {
						const model = gltf.scene;
						scene.add(model);

						model.traverse((obj) => {
							if ((obj as THREE.Mesh).isMesh) {
								const mesh = obj as THREE.Mesh;
								const hidden = ['Pants_14249_Shape', 'hnsshoes_6176_Shape', 'Shoes'];
								if (hidden.some(h => mesh.name.includes(h))) mesh.visible = false;
								
								mesh.castShadow = true;
								mesh.receiveShadow = true;
								
								if (mesh.material) {
									const mat = mesh.material as THREE.MeshStandardMaterial;
									if (mat.map) mat.map.anisotropy = 16;
								}
							}
						});

						// ── DYNAMIC CAMERA FOCUS ──
						model.updateMatrixWorld(true);
						const box = new THREE.Box3().setFromObject(model);
						const size = box.getSize(new THREE.Vector3());
						const center = box.getCenter(new THREE.Vector3());

						if (size.y < 0.1) {
							camera.position.set(center.x, center.y + 0.1, center.z + 0.5);
							camera.lookAt(center.x, center.y + 0.1, center.z);
						} else {
							const headBottomY = box.min.y + size.y * 0.82; 
							const headTopY = box.max.y;
							const focusCenterY = (headBottomY + headTopY) / 2;
							const focusHeight = headTopY - headBottomY;

							const vFovRad = (camera.fov * Math.PI) / 180;
							const desiredCoverage = 0.85; 
							const distance = (focusHeight / 2) / Math.tan(vFovRad / 2) / desiredCoverage;

							camera.position.set(center.x, focusCenterY, center.z + distance);
							camera.lookAt(center.x, focusCenterY - (focusHeight * 0.05), center.z);
							
							keyLight.position.set(center.x - 1, focusCenterY + 1, center.z + 2);
							keyLight.target.position.set(center.x, focusCenterY, center.z);
							keyLight.target.updateMatrixWorld();
						}
						
						camera.updateProjectionMatrix();

						animator = new FaceAnimator(model);
						stopBlink = startAutoBlink(animator);
						avatarReady = true;
						resolve();
					},
					(xhr) => {
						if (xhr.lengthComputable) {
							avatarLoadProgress = Math.round((xhr.loaded / xhr.total) * 100);
						} else {
							avatarLoadProgress = Math.min(avatarLoadProgress + 1, 98);
						}
					},
					(err) => reject(err)
				);
			});
		} catch (err) {
			console.error('Avatar load error:', err);
		}

		let lastTime = performance.now();
		function animate() {
			requestAnimationFrame(animate);
			const time = performance.now();
			const delta = (time - lastTime) / 1000;
			lastTime = time;

			animator?.update(Math.min(delta, 0.1));
			renderer.render(scene, camera);
		}
		animate();

		const ro = new ResizeObserver(() => {
			if (!canvasElement) return;
			camera.aspect = canvasElement.clientWidth / canvasElement.clientHeight;
			camera.updateProjectionMatrix();
			renderer.setSize(canvasElement.clientWidth, canvasElement.clientHeight);
		});
		ro.observe(canvasElement);
	}

	function initWebSocket() {
		let wsUrl = PUBLIC_BACKEND_WS;
		if (browser && window.location.protocol === 'https:' && wsUrl.startsWith('ws://')) {
			wsUrl = wsUrl.replace('ws://', 'wss://');
		}
		ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);

		ws.onopen = () => {
			wsStatus = 'connected';
		};

		ws.onclose = () => {
			wsStatus = 'disconnected';
			errorMessage = "Koneksi terputus. Silakan muat ulang halaman.";
		};

		ws.onmessage = async (event) => {
			const msg = JSON.parse(event.data);
			if (msg.type === 'ERROR') {
				console.error('Backend Error:', msg.message);
				wsStatus = 'disconnected';
				errorMessage = `Backend Error: ${msg.message}`;
				return;
			}
			await handleBackendMessage(msg);
		};
	}

	function handleUserInteraction() {
		if (audioBlocked) {
			unlockAudio();
			audioBlocked = false;
		}
	}

	async function handleBackendMessage(msg: any) {
		switch (msg.type) {
			case 'QUESTION': {
				const text = msg.text;
				messages = [...messages, { role: 'interviewer', text, time: timeDisplay() }];
				errorMessage = null;

				if (msg.persona === 'intimidating' && animator) {
					animator.setExpression(EMOTIONS.angry);
				} else if (msg.persona === 'friendly' && animator) {
					animator.setExpression(EMOTIONS.happy);
				}

				isSpeaking = true;
				try {
					if (animator) {
						// Gunakan audio & visemes dari backend jika tersedia untuk menghindari fetch ulang
						await speakWithBackend(text, animator, msg.audio && msg.visemes ? {
							audio: msg.audio,
							visemes: msg.visemes
						} : undefined);
					}
				} catch (err: any) {
					console.error('Speech playback failed:', err);
					if (err.message === 'AUTOPLAY_BLOCKED') {
						audioBlocked = true;
					} else {
						errorMessage = `Gagal memutar suara: ${err.message}`;
					}
				} finally {
					isSpeaking = false;
					startRecording();
				}
				break;
			}
			case 'TRANSCRIPT': {
				const lastIdx = messages.findLastIndex((m) => m.role === 'user');
				if (lastIdx !== -1) {
					messages[lastIdx] = { ...messages[lastIdx], text: msg.text };
				}
				break;
			}
			case 'PROCESSING':
				isListening = false;
				break;
			case 'FEEDBACK': {
				const feedbackText = msg.feedback;
				if (feedbackText) {
					console.log('Interviewer Feedback:', feedbackText);
				}
				break;
			}
			case 'SESSION_END':
				stopRecording();
				processingResult = false;
				goto(`/session/results?sessionId=${sessionId}`);
				break;
		}
	}

	function startRecording() {
		if (!stream || mediaRecorder?.state === 'recording') return;

		micMuted = false;
		const audioTracks = stream.getAudioTracks();
		if (audioTracks.length === 0) {
			console.error('Tidak ada track audio ditemukan');
			errorMessage = "Mikrofon tidak terdeteksi.";
			return;
		}
		audioTracks.forEach((t) => (t.enabled = true));

		isListening = true;
		isVoiceActive = false;
		audioChunks = [];
		liveTranscript = '';

		try {
			recognition?.start();
		} catch (e) {}

		const types = [
			'audio/mp4', 
			'audio/webm;codecs=opus',
			'audio/webm',
			'audio/ogg;codecs=opus',
			'audio/wav'
		];
		
		let supportedType = '';
		for (const type of types) {
			if (MediaRecorder.isTypeSupported(type)) {
				supportedType = type;
				break;
			}
		}

		const tryStart = (mimeType: string) => {
			mediaRecorder = new MediaRecorder(stream!, mimeType ? { mimeType } : {});

			mediaRecorder.ondataavailable = (e) => {
				if (e.data.size > 0) {
					audioChunks.push(e.data);
				}
			};

			mediaRecorder.onstop = async () => {
				isListening = false;
				if (audioChunks.length === 0) return;

				const audioBlob = new Blob(audioChunks, { type: mimeType || 'audio/webm' });
				const buffer = await audioBlob.arrayBuffer();

				if (buffer.byteLength > 0 && ws?.readyState === WebSocket.OPEN) {
					ws.send(buffer);
					messages = [...messages, { role: 'user', text: liveTranscript || '...', time: timeDisplay() }];
					liveTranscript = '';
				}
			};

			mediaRecorder.onerror = (e) => {
				console.error('MediaRecorder Error:', e);
				isListening = false;
			};

			mediaRecorder.start(1000);
		};

		try {
			tryStart(supportedType);
		} catch (e: any) {
			try {
				tryStart('');
			} catch (fallbackErr: any) {
				console.error('Gagal total memulai MediaRecorder:', fallbackErr);
				errorMessage = `Browser Anda tidak mendukung perekaman audio: ${fallbackErr.message}`;
				isListening = false;
			}
		}
	}

	function stopRecording() {
		if (mediaRecorder?.state === 'recording') {
			mediaRecorder.stop();
			try {
				recognition?.stop();
			} catch (e) {}
		}
	}

	function toggleMic() {
		if (!stream) return;
		micMuted = !micMuted;
		stream.getAudioTracks().forEach((t) => (t.enabled = !micMuted));
		if (micMuted) {
			recognition?.stop();
		} else if (isListening) {
			try {
				recognition?.start();
			} catch (e) {}
		}
	}

	function toggleCamera() {
		if (!stream) return;
		camOff = !camOff;
		stream.getVideoTracks().forEach((t) => (t.enabled = !camOff));
	}

	async function endSession() {
		stopRecording();
		processingResult = true;
		ws?.send(JSON.stringify({ type: 'END_SESSION', sessionId }));
	}
</script>

<svelte:head>
	<title>Sesi Interview — HiReady</title>
</svelte:head>

<div 
	class="flex h-[100dvh] w-full flex-col overflow-hidden bg-black font-sans text-white"
	onclick={handleUserInteraction}
	onkeydown={handleUserInteraction}
	role="presentation"
>
	{#if processingResult}
		<div class="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/90 backdrop-blur-xl" transition:fade>
			<div class="relative mb-8 h-24 w-24">
				<div class="absolute inset-0 animate-ping rounded-full bg-primary/20"></div>
				<div class="absolute inset-2 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
			</div>
			<h2 class="text-2xl font-bold tracking-tight text-white">Memproses Hasil Interview</h2>
			<p class="mt-2 text-white/50">AI sedang menganalisis performa Anda...</p>
		</div>
	{/if}

	<main class="relative flex flex-1 flex-col overflow-hidden md:block md:h-full md:w-full">
		<section
			class="group relative z-0 h-full w-full overflow-hidden bg-inverse-surface md:absolute md:inset-0"
		>
			{#if !avatarReady}
				<div class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/80">
					<div
						class="mb-4 h-48 w-32 animate-pulse rounded-2xl border border-white/10 bg-white/5"
					></div>
					<div class="h-1.5 w-48 overflow-hidden rounded-full bg-white/10">
						<div
							class="h-full bg-primary transition-all duration-300"
							style="width: {avatarLoadProgress || 10}%"
						></div>
					</div>
					<p class="mt-2 text-xs text-white/50">Memuat pewawancara...</p>
				</div>
			{/if}

			<canvas
				bind:this={canvasElement}
				class="absolute inset-0 h-full w-full transition-opacity duration-500 {avatarReady
					? 'opacity-100'
					: 'opacity-0'}"
			></canvas>

			{#if audioBlocked}
				<div 
					class="absolute inset-0 z-40 flex items-center justify-center bg-black/20 backdrop-blur-[2px]"
					transition:fade
				>
					<button 
						onclick={handleUserInteraction}
						class="flex flex-col items-center gap-4 rounded-3xl bg-primary/90 p-8 shadow-2xl animate-bounce border border-white/20"
					>
						<div class="flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
							<span class="material-symbols-outlined text-4xl text-white">volume_up</span>
						</div>
						<span class="text-sm font-bold uppercase tracking-widest text-white">Klik untuk mengaktifkan suara</span>
					</button>
				</div>
			{/if}

			{#if errorMessage}
				<div 
					class="absolute top-20 left-1/2 z-50 w-[90%] -translate-x-1/2 rounded-xl bg-error p-4 shadow-2xl md:w-auto md:min-w-[300px]"
					transition:fade
				>
					<div class="flex items-start gap-3">
						<span class="material-symbols-outlined mt-0.5 text-white">error</span>
						<div class="flex-1">
							<p class="text-xs font-bold uppercase tracking-tight text-white/70">Terjadi Kesalahan</p>
							<p class="mt-1 text-sm font-medium text-white">{errorMessage}</p>
						</div>
						<button onclick={() => errorMessage = null} class="text-white/50 hover:text-white">
							<span class="material-symbols-outlined text-sm">close</span>
						</button>
					</div>
				</div>
			{/if}

			{#if liveTranscript && isListening}
				<div 
					class="absolute bottom-20 left-4 right-4 z-30 flex justify-center pointer-events-none md:bottom-24"
					transition:fade
				>
					<div class="max-w-2xl rounded-2xl bg-black/60 px-5 py-3 backdrop-blur-xl border border-white/10 shadow-2xl">
						<div class="flex items-center gap-2 mb-1">
							<div class="h-1.5 w-1.5 rounded-full bg-blue-500 animate-ping"></div>
							<span class="text-[10px] font-black text-blue-400 uppercase tracking-widest">Listening</span>
						</div>
						<p class="text-sm md:text-base font-medium italic text-white/90 text-center leading-relaxed">
							"{liveTranscript}"
						</p>
					</div>
				</div>
			{/if}

			<div class="absolute top-3 right-3 left-3 z-10 flex items-start justify-between">
				<div class="flex gap-2">
					<div
						class="flex items-center gap-2 rounded-full border border-white/10 bg-black/40 px-3 py-1.5 backdrop-blur-md"
					>
						<div class="h-2 w-2 animate-pulse rounded-full bg-error"></div>
						<span class="text-[11px] font-semibold tracking-wider text-white">LIVE</span>
					</div>
					<div
						class="hidden items-center gap-1.5 rounded-full border border-white/10 bg-black/40 px-3 py-1.5 backdrop-blur-md sm:flex"
					>
						<span
							class="material-symbols-outlined text-[13px] text-secondary-container"
							style="font-variation-settings:'FILL' 1;">wifi</span
						>
						<span class="text-[11px] font-semibold text-secondary-container"
							>{wsStatus === 'connected' ? 'STABIL' : 'MENGHUBUNGKAN...'}</span
						>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<button
						onclick={() => (transcriptOpen = !transcriptOpen)}
						class="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-black/40 backdrop-blur-md transition-colors active:bg-white/10 md:hidden"
					>
						<span class="material-symbols-outlined text-[20px]"
							>{transcriptOpen ? 'chat_bubble' : 'chat_bubble_outline'}</span
						>
					</button>
					<div
						class="rounded-lg border border-white/10 bg-black/40 px-3 py-1.5 backdrop-blur-md"
					>
						<span class="text-base font-bold text-white tabular-nums">{timeDisplay()}</span>
					</div>
				</div>
			</div>

			<div
				class="absolute bottom-28 right-6 z-20 h-40 w-28 overflow-hidden rounded-xl border border-white/20 shadow-2xl transition-transform duration-300 md:bottom-28 md:left-6 md:h-52 md:w-36 lg:h-64 lg:w-48"
			>
				<video
					bind:this={videoElementDesktop}
					autoplay
					playsinline
					muted
					class="hidden h-full w-full object-cover md:block {camOff ? 'invisible' : ''}"
				></video>
				<video
					bind:this={videoElementMobile}
					autoplay
					playsinline
					muted
					class="h-full w-full object-cover md:hidden {camOff ? 'invisible' : ''}"
				></video>

				{#if camOff}
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
						<span class="material-symbols-outlined text-[20px] text-white/60 md:text-[28px]"
							>videocam_off</span
						>
						<p class="mt-1 text-[8px] text-white/60 md:text-[10px]">Kamera mati</p>
					</div>
				{/if}
				<div
					class="absolute bottom-1.5 left-1.5 flex items-center gap-1 rounded bg-black/60 px-1.5 py-0.5 backdrop-blur-sm md:bottom-2 md:left-2 md:rounded-md md:px-2 md:py-1"
				>
					<span
						class="material-symbols-outlined text-[11px] md:text-[13px] {micMuted
							? 'text-red-400'
							: 'text-white'}">{micMuted ? 'mic_off' : 'mic'}</span
					>
					<span class="text-[9px] text-white md:text-[11px]">Kamu</span>
				</div>
			</div>
		</section>

		<section
			class="
				fixed inset-0 z-[60] flex flex-col bg-black/95 backdrop-blur-2xl
				transition-all duration-300 md:relative md:inset-auto md:z-30 md:bg-black/80
				{transcriptOpen ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0 pointer-events-none md:hidden'}
				md:absolute md:top-6 md:right-6 md:h-[60vh] md:w-[320px] md:translate-y-0 md:rounded-2xl md:opacity-100 md:pointer-events-auto lg:w-[360px]
			"
		>
			<div
				class="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-white/5 px-6 backdrop-blur-md md:h-12 md:rounded-t-2xl md:px-4"
			>
				<h2 class="text-base font-bold text-white md:text-sm">Riwayat Percakapan</h2>
				<button
					onclick={() => (transcriptOpen = false)}
					class="rounded-full p-2 text-white/80 transition-colors hover:bg-white/10"
				>
					<span class="material-symbols-outlined text-[24px] md:text-[20px]">close</span>
				</button>
			</div>

			<div
				bind:this={messagesContainer}
				class="flex-1 scroll-smooth space-y-4 overflow-y-auto p-4"
			>
				{#each messages as msg, i (i)}
					{#if msg.role === 'interviewer'}
						<div class="flex max-w-[90%] gap-3">
							<div
								class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary"
							>
								<span class="material-symbols-outlined text-[18px] text-white">smart_toy</span>
							</div>
							<div class="flex flex-col gap-1">
								<div class="flex items-baseline gap-2">
									<span class="text-[12px] text-white/80">Interviewer</span>
									<span class="text-[10px] text-white/50">{msg.time}</span>
								</div>
								<div
									class="rounded-xl rounded-tl-sm border border-white/10 bg-white/10 p-3 shadow-lg backdrop-blur-md"
								>
									<p class="text-[13px] leading-relaxed text-white">{msg.text}</p>
								</div>
							</div>
						</div>
					{:else}
						<div class="ml-auto flex max-w-[90%] flex-row-reverse gap-3">
							<div
								class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-tertiary"
							>
								<span class="material-symbols-outlined text-[18px] text-white">person</span>
							</div>
							<div class="flex flex-col items-end gap-1">
								<div class="flex items-baseline gap-2">
									<span class="text-[10px] text-white/50">{msg.time}</span>
									<span class="text-[12px] text-white/80">Kamu</span>
								</div>
								<div
									class="rounded-xl rounded-tr-sm border border-primary/30 bg-primary/20 p-3 shadow-lg backdrop-blur-md"
								>
									<p class="text-[13px] leading-relaxed text-white">{msg.text}</p>
								</div>
							</div>
						</div>
					{/if}
				{/each}

				{#if isListening}
					<div class="ml-auto flex max-w-[90%] flex-row-reverse gap-3 opacity-80">
						<div
							class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/20 bg-white/5"
						>
							<span class="material-symbols-outlined animate-pulse text-[16px] text-white/70"
								>mic</span
							>
						</div>
						<div class="flex flex-col items-end gap-1">
							<div class="flex items-baseline gap-2">
								<span class="text-[10px] text-white/50">{timeDisplay()}</span>
								<span class="text-[12px] text-white/80">Kamu</span>
							</div>
							<div
								class="rounded-xl rounded-tr-sm border border-dashed border-white/30 bg-white/5 p-3 shadow-sm backdrop-blur-md"
							>
								<p class="text-[13px] italic leading-relaxed text-white/70">
									{liveTranscript || 'Mendengarkan...'}
								</p>
							</div>
						</div>
					</div>
				{/if}

				{#if isSpeaking}
					<div class="flex max-w-[90%] items-center gap-3">
						<div
							class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/20 bg-white/5"
						>
							<span class="material-symbols-outlined animate-pulse text-[16px] text-white/70"
								>volume_up</span
							>
						</div>
						<span class="text-[13px] text-white/70">Pewawancara sedang berbicara...</span>
					</div>
				{/if}
			</div>
		</section>
	</main>

	<nav
		class="z-50 flex shrink-0 items-center justify-center gap-3 border-t border-white/10 bg-black/60 px-4 py-3 backdrop-blur-xl md:fixed md:bottom-8 md:left-1/2 md:-translate-x-1/2 md:rounded-full md:border-white/10 md:bg-black/40 md:px-6 md:py-4 md:shadow-2xl"
	>
		<button
			onclick={toggleMic}
			title={micMuted ? 'Aktifkan Mikrofon' : 'Matikan Mikrofon'}
			class="flex h-11 w-11 items-center justify-center rounded-full shadow-lg transition-all active:scale-95 md:h-12 md:w-12
			       {micMuted ? 'bg-error text-white' : 'bg-white text-primary'}"
		>
			<span class="material-symbols-outlined text-[22px] md:text-[24px]"
				>{micMuted ? 'mic_off' : 'mic'}</span
			>
		</button>

		<button
			onclick={toggleCamera}
			title={camOff ? 'Aktifkan Kamera' : 'Matikan Kamera'}
			class="flex h-11 w-11 items-center justify-center rounded-full shadow-lg transition-all active:scale-95 md:h-12 md:w-12
			       {camOff ? 'bg-error text-white' : 'bg-white text-primary'}"
		>
			<span class="material-symbols-outlined text-[22px] md:text-[24px]"
				>{camOff ? 'videocam_off' : 'videocam'}</span
			>
		</button>

		<div class="mx-1 h-7 w-px bg-white/20 md:mx-2 md:h-8"></div>

		{#if isListening}
			<button
				onclick={stopRecording}
				class="flex animate-pulse items-center gap-2 rounded-full bg-secondary py-2.5 px-5 text-white shadow-lg transition-all hover:opacity-90 active:scale-95 md:gap-3 md:py-3 md:px-8"
			>
				<span class="material-symbols-outlined text-[20px] md:text-[22px]">send</span>
				<span class="text-[14px] font-semibold tracking-wide md:text-[16px]">Kirim Jawaban</span>
			</button>
		{/if}

		<button
			onclick={endSession}
			class="flex items-center gap-2 rounded-full bg-primary py-2.5 pr-5 pl-4 text-white shadow-lg transition-all hover:bg-on-primary-fixed-variant active:scale-95 md:gap-3 md:py-3 md:pr-8 md:pl-6"
		>
			<span
				class="material-symbols-outlined text-[20px] md:text-[22px]"
				style="font-variation-settings:'FILL' 1;">call_end</span
			>
			<span class="text-[14px] font-semibold tracking-wide md:text-[16px]">Akhiri Sesi</span>
		</button>
	</nav>
</div>
