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
	import { pwaState, installApp } from '$lib/pwa.svelte';
	import {
		FaceLandmarker,
		FilesetResolver
	} from "@mediapipe/tasks-vision";
	import {
		Volume2,
		AlertCircle,
		X,
		Wifi,
		Download,
		MessageSquare,
		Video,
		VideoOff,
		Mic,
		MicOff,
		Bot,
		User,
		Send,
		PhoneOff,
		Zap,
		UserCheck
	} from '@lucide/svelte';

	const backgroundImages = import.meta.glob<any>('$lib/assets/avatar-backgrounds/*.{jpeg,jpg,png,webp}', {
		eager: true,
		query: { enhanced: true }
	});

	// ── Media ──
	let videoElementDesktop = $state<HTMLVideoElement | null>(null);
	let videoElementMobile = $state<HTMLVideoElement | null>(null);
	let canvasElement: HTMLCanvasElement;
	let stream = $state<MediaStream | null>(null);
	let micMuted = $state(false);
	let camOff = $state(false);

	// ── Face Analysis (MediaPipe) ──
	let faceLandmarker: FaceLandmarker | undefined;
	let lastFaceSampleTime = 0;
	const FACE_SAMPLE_INTERVAL = 3000; // Sample every 3 seconds

	// ── Session & WebSocket ──
	let sessionId = $state<string | null>(null);
	let ws = $state<WebSocket | null>(null);
	let wsStatus = $state<'connecting' | 'connected' | 'disconnected'>('connecting');

	// ── Percakapan ──
	type Message = { role: 'interviewer' | 'user'; text: string; time: string };
	let messages = $state<Message[]>([]);
	let isListening = $state(false);
	let isSpeaking = $state(false);
	let isThinking = $state(false);
	let transcriptOpen = $state(false);
	let autoSend = $state(true);
	let silenceTimeout: ReturnType<typeof setTimeout> | null = null;
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
	let avatarName = $state('');
	let avatarDescription = $state('');
	let avatarThumbnail = $state('');
	let avatarBackground = $state('/avatar-backgrounds/default.jpg');

	// ── STT (MediaRecorder & Web Speech API) ──
	let mediaRecorder: MediaRecorder | null = null;
	let audioChunks: Blob[] = [];
	let recognition: any = null;

	// ── Timer & Session Limit ──
	const SESSION_LIMIT_SECONDS = 120; // 2 Menit
	let remainingSeconds = $state(SESSION_LIMIT_SECONDS);
	let sessionStartTime = $state<number | null>(null);
	let timerInterval: ReturnType<typeof setInterval>;

	const timeDisplay = () => {
		const m = Math.floor(remainingSeconds / 60)
			.toString()
			.padStart(2, '0');
		const s = (remainingSeconds % 60).toString().padStart(2, '0');
		return `${m}:${s}`;
	};

	function updateTimer() {
		if (sessionStartTime) {
			const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
			remainingSeconds = Math.max(0, SESSION_LIMIT_SECONDS - elapsed);
			
			if (remainingSeconds <= 0) {
				clearInterval(timerInterval);
				endSession();
			}
		} else if (sessionStarted) {
			// Jika session sudah started tapi belum ada startTime dari backend (baru mulai)
			// Kita inisialisasi startTime lokal
			sessionStartTime = Date.now();
		}
	}

	// ── Effect & Lifecycle ──

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
			// Mulai timer jika belum diset dari onMount
			if (!sessionStartTime) {
				sessionStartTime = Date.now();
			}
		}
	});

	onMount(async () => {
		if (browser) {
			document.body.style.overflow = 'hidden';
		}
		
		sessionId = page.url.searchParams.get('sessionId');

		if (sessionId) {
			// 1. Ambil info sesi & avatar
			try {
				const res = await fetch(`/api/proxy/api/sessions/${sessionId}`);
				if (!res.ok) throw new Error('Session not found');
				
				const sessionData = await res.json();
				const glbUrl = `/${sessionData.avatar.glbUrl}`;
				const cameraConfig = sessionData.avatar.cameraConfig;

				// Store avatar info for loading screen
				avatarName = sessionData.avatar.name;
				avatarDescription = sessionData.avatar.description;
				avatarThumbnail = `/${sessionData.avatar.thumbnailUrl}`;
				
				if (sessionData.avatar.backgroundPath) {
					avatarBackground = `/${sessionData.avatar.backgroundPath}`;
				}

				// Persistent Timer Logic
				if (sessionData.startedAt) {
					sessionStartTime = new Date(sessionData.startedAt).getTime();
					sessionStarted = true; // Anggap session sudah start jika ada startedAt
					updateTimer();
				}

				// 2. Avatar Three.js
				initAvatar(glbUrl, cameraConfig);
			} catch (err) {
				console.error('Failed to load session details:', err);
				errorMessage = 'Gagal memuat detail sesi.';
			}

			// 3. WebSocket
			initWebSocket();
		}

		// Mulai interval timer
		timerInterval = setInterval(updateTimer, 1000);

		// 4. Kamera user
		if (browser && navigator.mediaDevices) {
			navigator.mediaDevices
				.getUserMedia({ video: true, audio: true })
				.then((s) => {
					stream = s;
				})
				.catch((e) => {
					console.error('Camera access failed:', e);
				});
		}

		// 5. Live STT (Web Speech API)
		initSpeechRecognition();

		// 6. MediaPipe Face Analysis
		await initMediaPipe();
	});

	async function initMediaPipe() {
		if (!browser) return;
		try {
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
			console.log("MediaPipe FaceLandmarker initialized");
		} catch (err) {
			console.error("Failed to init MediaPipe:", err);
		}
	}

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

				// Auto-send logic
				if (autoSend) {
					if (silenceTimeout) clearTimeout(silenceTimeout);
					silenceTimeout = setTimeout(() => {
						if (isListening && !isSpeaking && liveTranscript.trim().length > 3) {
							stopRecording();
						}
					}, 2000); // 2 detik setelah selesai bicara
				}
			}
		};

		let recognitionRetryCount = 0;
		const MAX_RECOGNITION_RETRIES = 3;

		recognition.onerror = (e: any) => {
			console.error('Speech Recognition Error:', e);
			isVoiceActive = false;
			
			if (e.error === 'network') {
				recognitionRetryCount++;
				if (recognitionRetryCount > MAX_RECOGNITION_RETRIES) {
					console.warn('Speech Recognition disabled due to persistent network errors');
					errorMessage = "Layanan transkrip langsung browser tidak tersedia (Network Error). Anda tetap bisa berbicara, dan jawaban Anda akan diproses setelah selesai.";
				}
			}
		};

		recognition.onend = () => {
			isVoiceActive = false;
			// Restart hanya jika tidak sedang dalam error beruntun
			if (isListening && !micMuted && recognitionRetryCount <= MAX_RECOGNITION_RETRIES) {
				try {
					recognition.start();
				} catch (e) {}
			}
		};
	}

	onDestroy(() => {
		if (browser) {
			document.body.style.overflow = '';
		}
		clearInterval(timerInterval);
		stream?.getTracks().forEach((t) => t.stop());
		ws?.close();
		stopBlink?.();
	});

	async function initAvatar(glbUrl: string, cameraConfig?: any) {
		if (!canvasElement || !browser) return;

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

						// Gunakan config dari DB atau default
						const headHeightRatio = cameraConfig?.headHeightRatio ?? 0.82;
						const distanceOffset = cameraConfig?.distanceOffset ?? 1.0;
						const lookAtOffset = cameraConfig?.lookAtOffset ?? 0.05;

						if (size.y < 0.1) {
							camera.position.set(center.x, center.y + 0.1, center.z + 0.5);
							camera.lookAt(center.x, center.y + 0.1, center.z);
						} else {
							const headBottomY = box.min.y + size.y * headHeightRatio; 
							const headTopY = box.max.y;
							const focusCenterY = (headBottomY + headTopY) / 2;
							const focusHeight = headTopY - headBottomY;

							const vFovRad = (camera.fov * Math.PI) / 180;
							const desiredCoverage = 0.85; 
							const distance = ((focusHeight / 2) / Math.tan(vFovRad / 2) / desiredCoverage) * distanceOffset;

							camera.position.set(center.x, focusCenterY, center.z + distance);
							camera.lookAt(center.x, focusCenterY - (focusHeight * lookAtOffset), center.z);
							
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

			if (animator) {
				animator.update(Math.min(delta, 0.1));

				// ── PROCEDURAL IDLE & THINKING ANIMATION ──
				const t = time / 1000;
				
				// 1. Subtle breathing/sway (Always on)
				// Kecepatan sangat lambat agar tidak mengganggu
				const swayX = Math.sin(t * 0.5) * 0.015;
				const swayY = Math.cos(t * 0.8) * 0.01;
				
				let targetRotX = swayX;
				let targetRotY = swayY;
				let targetRotZ = 0;

				if (isThinking) {
					// Menoleh sedikit ke samping dan ke atas (pose berpikir)
					targetRotX += 0.04; 
					targetRotY += 0.1; 
					targetRotZ = 0.03;
					
					// Naikkan alis sedikit
					animator.setExpression({
						'BrowInnerUp': 0.3,
						'BrowOuterUpLeft': 0.1,
						'BrowOuterUpRight': 0.1
					});
				}

				// Cari model di scene untuk diaplikasikan rotasi
				// Traversal scene.children untuk menemukan model utama
				scene.traverse((obj) => {
					if (obj.name === 'Scene' || (obj.type === 'Group' && obj.parent === scene)) {
						obj.rotation.x = THREE.MathUtils.lerp(obj.rotation.x, targetRotX, 0.05);
						obj.rotation.y = THREE.MathUtils.lerp(obj.rotation.y, targetRotY, 0.05);
						obj.rotation.z = THREE.MathUtils.lerp(obj.rotation.z, targetRotZ, 0.05);
					}
				});
			}

			renderer.render(scene, camera);

			// ── FACE ANALYSIS (MediaPipe) ──
			if (faceLandmarker && browser && !camOff) {
				const activeVideo = videoElementDesktop || videoElementMobile;
				if (activeVideo && activeVideo.readyState >= 2) {
					const now = performance.now();
					if (now - lastFaceSampleTime > FACE_SAMPLE_INTERVAL) {
						lastFaceSampleTime = now;
						
						const results = faceLandmarker.detectForVideo(activeVideo, now);
						if (results.faceBlendshapes?.[0]) {
							const shapes = results.faceBlendshapes[0].categories;
							const smileLeft = shapes.find(s => s.categoryName === 'mouthSmileLeft')?.score || 0;
							const smileRight = shapes.find(s => s.categoryName === 'mouthSmileRight')?.score || 0;
							const avgSmile = (smileLeft + smileRight) / 2;

							// Eye contact consistency check
							// We consider consistent eye contact if face is detected and landmarks are present
							// For more precision, we could check pupil position or head pitch/yaw/roll
							const hasLandmarks = results.faceLandmarks?.[0]?.length > 0;
							
							if (ws && wsStatus === 'connected') {
								ws.send(JSON.stringify({
									type: 'FACE_METRICS',
									metrics: {
										smileScore: avgSmile,
										isLookingAtCamera: hasLandmarks, 
										timestamp: now
									}
								}));
							}
						}
					}
				}
			}
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

	let currentTurnNumber = $state(0);

	let sessionCompleted = $state(false);

	async function handleBackendMessage(msg: any) {
		switch (msg.type) {
			case 'QUESTION': {
				const text = msg.text;
				messages = [...messages, { role: 'interviewer', text, time: timeDisplay() }];
				errorMessage = null;
				currentTurnNumber = msg.turnNumber;

				if (msg.persona === 'intimidating' && animator) {
					animator.setExpression(EMOTIONS.angry);
				} else if (msg.persona === 'friendly' && animator) {
					animator.setExpression(EMOTIONS.happy);
				}

				isSpeaking = true;
				isThinking = false;
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
					if (!sessionCompleted) {
						startRecording();
					}
				}
				break;
			}
			case 'QUESTION_CHUNK': {
				// Handle streaming chunk
				const { text, audio, visemes, persona, isLast, turnNumber } = msg;
				
				// Update transcript history
				if (text.trim()) {
					if (turnNumber === currentTurnNumber) {
						const lastMsg = messages[messages.length - 1];
						if (lastMsg && lastMsg.role === 'interviewer') {
							lastMsg.text += ' ' + text;
						}
					} else {
						messages = [...messages, { role: 'interviewer', text, time: timeDisplay() }];
						currentTurnNumber = turnNumber;
					}
				}
				
				errorMessage = null;
				isThinking = false;

				// Push to queue and process
				audioQueue.push({ text, audio, visemes, persona, isLast });
				processAudioQueue();
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
				isThinking = true;
				break;
			case 'FEEDBACK': {
				const feedbackText = msg.feedback;
				if (feedbackText) {
					console.log('Interviewer Feedback:', feedbackText);
				}
				break;
			}
			case 'SESSION_COMPLETED':
				sessionCompleted = true;
				break;
			case 'SESSION_END':
				stopRecording();
				if (isSpeaking || audioQueue.length > 0 || lastChunkReceived) {
					// Tunggu sebentar jika masih berbicara
					setTimeout(() => {
						processingResult = false;
						goto(`/session/results?sessionId=${sessionId}`);
					}, 2000);
				} else {
					processingResult = false;
					goto(`/session/results?sessionId=${sessionId}`);
				}
				break;
		}
	}

	let audioQueue: any[] = [];
	let isProcessingQueue = false;
	let lastChunkReceived = false;

	async function processAudioQueue() {
		if (isProcessingQueue || audioQueue.length === 0) return;
		isProcessingQueue = true;
		isSpeaking = true;

		while (audioQueue.length > 0) {
			const chunk = audioQueue.shift()!;
			if (chunk.isLast) lastChunkReceived = true;

			// Handle persona
			if (chunk.persona === 'intimidating' && animator) {
				animator.setExpression(EMOTIONS.angry);
			} else if (chunk.persona === 'friendly' && animator) {
				animator.setExpression(EMOTIONS.happy);
			}

			try {
				if (animator && chunk.audio && chunk.visemes) {
					await speakWithBackend(chunk.text, animator, {
						audio: chunk.audio,
						visemes: chunk.visemes
					});
				}
			} catch (err: any) {
				console.error('Queue speech failed:', err);
				if (err.message === 'AUTOPLAY_BLOCKED') {
					audioBlocked = true;
					break;
				}
			}
		}

		isSpeaking = false;
		isProcessingQueue = false;
		
		if (lastChunkReceived && audioQueue.length === 0) {
			lastChunkReceived = false;
			if (!sessionCompleted) {
				startRecording();
			}
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
		if (silenceTimeout) {
			clearTimeout(silenceTimeout);
			silenceTimeout = null;
		}
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
		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ type: 'END_SESSION', sessionId }));
		} else {
			goto(`/session/results?sessionId=${sessionId}`);
		}
	}
</script>

<svelte:head>
	<title>Sesi Interview — Heurix</title>
</svelte:head>

<div 
	class="flex h-[100dvh] w-full flex-col overflow-hidden bg-black font-sans text-white"
	onclick={handleUserInteraction}
	onkeydown={handleUserInteraction}
	role="presentation"
>
	{#if !avatarReady}
		<div class="fixed inset-0 z-[100] flex items-center justify-center bg-[#f8f9ff] text-gray-900" transition:fade>
			<div class="w-full max-w-2xl overflow-hidden rounded-3xl bg-white p-8 shadow-[0px_20px_50px_rgba(0,0,0,0.1)]">
				<div class="flex flex-col gap-8 md:flex-row md:items-center">
					<!-- Avatar Image -->
					<div class="relative h-48 w-48 shrink-0 self-center overflow-hidden rounded-2xl bg-gray-100 md:h-56 md:w-56">
						{#if avatarThumbnail}
							<img src={avatarThumbnail} alt={avatarName} class="h-full w-full object-cover" />
						{:else}
							<div class="flex h-full w-full items-center justify-center bg-gray-200">
								<Bot size={64} class="text-gray-400" />
							</div>
						{/if}
						<div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
					</div>

					<!-- Avatar Info -->
					<div class="flex flex-1 flex-col justify-center text-center md:text-left">
						<span class="mb-2 text-[10px] font-bold tracking-[0.2em] text-primary uppercase">Mempersiapkan Sesi</span>
						<h2 class="mb-3 text-3xl font-extrabold tracking-tight text-gray-900">{avatarName || 'Pewawancara'}</h2>
						<p class="mb-8 text-base leading-relaxed text-gray-500">
							{avatarDescription || 'Sedang memuat data pewawancara profesional Anda. Harap tunggu sejenak.'}
						</p>

						<!-- Progress Bar -->
						<div class="space-y-3">
							<div class="flex items-center justify-between text-xs font-bold text-gray-400 uppercase tracking-wider">
								<span>Memuat Avatar 3D</span>
								<span class="text-primary">{avatarLoadProgress}%</span>
							</div>
							<div class="h-2 w-full overflow-hidden rounded-full bg-gray-100">
								<div
									class="h-full bg-primary transition-all duration-300"
									style="width: {avatarLoadProgress || 10}%"
								></div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

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
			<!-- Background Image -->
			{#if avatarReady}
				{#if backgroundImages[`/src/lib/assets${avatarBackground}`]}
					<div class="absolute inset-0 z-[-1] transition-opacity duration-1000" transition:fade>
						<enhanced:img 
							src={backgroundImages[`/src/lib/assets${avatarBackground}`].default} 
							class="absolute inset-0 h-full w-full object-cover" 
							alt="Background" 
						/>
						<div class="absolute inset-0 bg-black/20 backdrop-blur-[2px]"></div>
					</div>
				{:else}
					<div 
						class="absolute inset-0 z-[-1] bg-cover bg-center transition-opacity duration-1000"
						style="background-image: url({avatarBackground});"
						transition:fade
					>
						<div class="absolute inset-0 bg-black/20 backdrop-blur-[2px]"></div>
					</div>
				{/if}
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
							<Volume2 size={40} class="text-white" />
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
						<AlertCircle size={20} class="mt-0.5 text-white" />
						<div class="flex-1">
							<p class="text-xs font-bold uppercase tracking-tight text-white/70">Terjadi Kesalahan</p>
							<p class="mt-1 text-sm font-medium text-white">{errorMessage}</p>
						</div>
						<button onclick={() => errorMessage = null} class="text-white/50 hover:text-white">
							<X size={16} />
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
						<Wifi size={13} class="text-secondary-container" fill="currentColor" />
						<span class="text-[11px] font-semibold text-secondary-container"
							>{wsStatus === 'connected' ? 'STABIL' : 'MENGHUBUNGKAN...'}</span
						>
					</div>
				</div>
				<div class="flex items-center gap-2">
					{#if pwaState.showInstallButton}
						<button
							onclick={installApp}
							class="flex h-10 items-center gap-2 rounded-full border border-primary/50 bg-primary/20 px-4 backdrop-blur-md transition-all hover:bg-primary/40 active:scale-95"
						>
							<Download size={18} class="text-white" />
							<span class="hidden text-xs font-bold text-white sm:inline">Install App</span>
						</button>
					{/if}
					<button
						onclick={() => (transcriptOpen = !transcriptOpen)}
						class="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-black/40 backdrop-blur-md transition-colors active:bg-white/10"
					>
						<MessageSquare size={20} class="text-white" />
					</button>
					<div
						class="flex items-center gap-2 rounded-lg border border-white/10 bg-black/40 px-3 py-1.5 backdrop-blur-md"
					>
						<span class="text-[10px] font-bold text-white/50 uppercase tracking-wider">Timer</span>
						<span class="text-base font-bold tabular-nums {remainingSeconds < 60 ? 'text-error animate-pulse' : 'text-white'}">
							{timeDisplay()}
						</span>
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
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-white/60">
						<VideoOff size={28} />
						<p class="mt-1 text-[8px] md:text-[10px]">Kamera mati</p>
					</div>
				{/if}
				<div
					class="absolute bottom-1.5 left-1.5 flex items-center gap-1 rounded bg-black/60 px-1.5 py-0.5 backdrop-blur-sm md:bottom-2 md:left-2 md:rounded-md md:px-2 md:py-1"
				>
					{#if micMuted}
						<MicOff size={11} class="text-red-400" />
					{:else}
						<Mic size={11} class="text-white" />
					{/if}
					<span class="text-[9px] text-white md:text-[11px]">Kamu</span>
				</div>
			</div>
		</section>

		<section
			class="
				fixed inset-y-0 right-0 z-[60] flex flex-col bg-black/95 backdrop-blur-2xl
				transition-all duration-300 md:bg-black/80
				{transcriptOpen ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0 pointer-events-none'}
				w-full sm:max-w-[360px] md:w-[320px] lg:w-[380px]
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
					<X size={20} />
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
								<Bot size={18} class="text-white" />
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
								<User size={18} class="text-white" />
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
							<Mic size={16} class="animate-pulse text-white/70" />
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
							<Volume2 size={16} class="animate-pulse text-white/70" />
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
			{#if micMuted}
				<MicOff size={24} />
			{:else}
				<Mic size={24} />
			{/if}
		</button>

		<button
			onclick={toggleCamera}
			title={camOff ? 'Aktifkan Kamera' : 'Matikan Kamera'}
			class="flex h-11 w-11 items-center justify-center rounded-full shadow-lg transition-all active:scale-95 md:h-12 md:w-12
			       {camOff ? 'bg-error text-white' : 'bg-white text-primary'}"
		>
			{#if camOff}
				<VideoOff size={24} />
			{:else}
				<Video size={24} />
			{/if}
		</button>

		<button
			onclick={() => (autoSend = !autoSend)}
			title={autoSend ? 'Matikan Kirim Otomatis' : 'Aktifkan Kirim Otomatis'}
			class="flex h-11 w-11 items-center justify-center rounded-full shadow-lg transition-all active:scale-95 md:h-12 md:w-12
			       {autoSend ? 'bg-secondary text-white' : 'bg-white text-secondary'}"
		>
			{#if autoSend}
				<Zap size={24} />
			{:else}
				<UserCheck size={24} />
			{/if}
		</button>

		<div class="mx-1 h-7 w-px bg-white/20 md:mx-2 md:h-8"></div>

		{#if isListening}
			<button
				onclick={stopRecording}
				class="flex animate-pulse items-center gap-2 rounded-full bg-secondary py-2.5 px-5 text-white shadow-lg transition-all hover:opacity-90 active:scale-95 md:gap-3 md:py-3 md:px-8"
			>
				<Send size={20} />
				<span class="text-[14px] font-semibold tracking-wide md:text-[16px]">Kirim Jawaban</span>
			</button>
		{/if}

		<button
			onclick={endSession}
			class="flex items-center gap-2 rounded-full bg-primary py-2.5 pr-5 pl-4 text-white shadow-lg transition-all hover:bg-on-primary-fixed-variant active:scale-95 md:gap-3 md:py-3 md:pr-8 md:pl-6"
		>
			<PhoneOff size={20} />
			<span class="text-[14px] font-semibold tracking-wide md:text-[16px]">Akhiri Sesi</span>
		</button>
	</nav>
</div>
