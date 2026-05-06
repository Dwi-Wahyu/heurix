<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
	import { FaceAnimator } from '$lib/FaceAnimator';
	import { EMOTIONS } from '$lib/emotionPresets';
	import { speakWithBackend } from '$lib/lipSync';
	import { startAutoBlink } from '$lib/autoBlink';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);
	let textToSpeak = $state('Halo, selamat datang di kompetisi Gemastik!');
	let currentEmotion = $state('neutral');

	let faceAnimator: FaceAnimator | null = null;
	let lastTime = 0;

	onMount(() => {
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0xf0f2f5);

		const camera = new THREE.PerspectiveCamera(
			75,
			window.innerWidth / window.innerHeight,
			0.1,
			1000
		);
		camera.position.set(0, 1.6, 2.2);

		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
		renderer.setSize(window.innerWidth, window.innerHeight);
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.toneMapping = THREE.ReinhardToneMapping;
		renderer.toneMappingExposure = 1.2;
		renderer.shadowMap.enabled = true;

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.target.set(0, 1, 0);
		controls.minDistance = 0.5;
		controls.maxDistance = 4;
		controls.maxPolarAngle = Math.PI / 1.8;

		// Lighting
		const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
		scene.add(ambientLight);

		const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
		directionalLight.position.set(5, 10, 5);
		directionalLight.castShadow = true;
		scene.add(directionalLight);

		let currentModel: THREE.Group | null = null;
		let stopBlink: (() => void) | null = null;

		function loadGLB(path: string) {
			const loader = new GLTFLoader();

			const dracoLoader = new DRACOLoader();
			dracoLoader.setDecoderPath('/draco/');
			loader.setDRACOLoader(dracoLoader);

			loader.load(
				path,
				(gltf) => {
					currentModel = gltf.scene;
					scene.add(currentModel);
					setupModel(currentModel);

					faceAnimator = new FaceAnimator(currentModel);
					stopBlink = startAutoBlink(faceAnimator);

					loading = false;
				},
				undefined,
				(err) => {
					console.error('An error happened during GLB load:', err);
					handleError(err);
				}
			);
		}

		function setupModel(model: THREE.Object3D) {
			const box = new THREE.Box3().setFromObject(model);
			const fullHeight = box.max.y - box.min.y;
			const fullCenter = box.getCenter(new THREE.Vector3());

			const shoulderY = box.min.y + fullHeight * 0.72;
			const headTopY = box.max.y;
			const focusCenterY = (shoulderY + headTopY) / 2;
			const focusHeight = headTopY - shoulderY;

			const vFovRad = (camera.fov * Math.PI) / 180;
			const desiredCoverage = 0.75;
			const distance = focusHeight / 2 / Math.tan(vFovRad / 2) / desiredCoverage;

			controls.target.set(fullCenter.x, focusCenterY, fullCenter.z);
			camera.position.set(fullCenter.x, focusCenterY, fullCenter.z + distance);
			camera.updateProjectionMatrix();

			model.traverse((child) => {
				if ((child as THREE.Mesh).isMesh) {
					child.castShadow = true;
					child.receiveShadow = true;
				}
			});
		}

		function handleError(err: any) {
			console.error('An error happened', err);
			error = 'Gagal memuat model. Pastikan file tersedia di static folder.';
			loading = false;
		}

		loadGLB('/face/boy/boy-character-copy-optimized-v3.glb');

		function animate(time: number) {
			requestAnimationFrame(animate);
			
			const delta = lastTime ? (time - lastTime) / 1000 : 0;
			lastTime = time;

			if (faceAnimator) {
				faceAnimator.update(Math.min(delta, 0.1));
			}

			controls.update();
			renderer.render(scene, camera);
		}

		requestAnimationFrame(animate);

		const handleResize = () => {
			camera.aspect = window.innerWidth / window.innerHeight;
			camera.updateProjectionMatrix();
			renderer.setSize(window.innerWidth, window.innerHeight);
		};

		window.addEventListener('resize', handleResize);

		return () => {
			window.removeEventListener('resize', handleResize);
			stopBlink?.();
			renderer.dispose();
		};
	});

	function handleSpeak() {
		if (faceAnimator) {
			speakWithBackend(textToSpeak, faceAnimator);
		}
	}

	function setEmotion(emotion: string) {
		if (faceAnimator) {
			currentEmotion = emotion;
			faceAnimator.resetFace();
			faceAnimator.setExpression(EMOTIONS[emotion]);
		}
	}
</script>

<div class="container">
	{#if loading}
		<div class="overlay">
			<div class="loader">Memuat Model Boy Character...</div>
		</div>
	{/if}

	{#if error}
		<div class="overlay error">
			<p>{error}</p>
			<a href="/" class="back-link">Kembali</a>
		</div>
	{/if}

	<canvas bind:this={canvas}></canvas>

	<div class="ui">
		<h1>Boy Character Demo</h1>
		<p>Model: GLB with Face Animation</p>

		<div class="controls">
			<div class="speech-box">
				<input type="text" bind:value={textToSpeak} placeholder="Ketik sesuatu..." />
				<button onclick={handleSpeak}>Bicara</button>
			</div>

			<div class="emotion-grid">
				{#each Object.keys(EMOTIONS) as emotion}
					<button class:active={currentEmotion === emotion} onclick={() => setEmotion(emotion)}>
						{emotion}
					</button>
				{/each}
			</div>
		</div>

		<p class="hint">Gunakan mouse untuk kontrol kamera.</p>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		overflow: hidden;
		font-family: 'Inter', sans-serif;
	}

	.container {
		position: relative;
		width: 100vw;
		height: 100vh;
	}

	canvas {
		display: block;
	}

	.overlay {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(255, 255, 255, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 10;
	}

	.error {
		background: rgba(255, 240, 240, 0.9);
		color: #e53e3e;
		flex-direction: column;
	}

	.loader {
		font-size: 1.25rem;
		font-weight: 600;
		color: #4a5568;
	}

	.ui {
		position: absolute;
		bottom: 2rem;
		left: 2rem;
		color: #2d3748;
		background: rgba(255, 255, 255, 0.8);
		padding: 1.5rem;
		border-radius: 1rem;
		backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.5);
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		width: 350px;
	}

	h1 {
		margin: 0 0 0.5rem 0;
		font-size: 1.25rem;
		font-weight: 700;
	}

	.controls {
		margin: 1rem 0;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.speech-box {
		display: flex;
		gap: 0.5rem;
	}

	.speech-box input {
		flex: 1;
		padding: 0.5rem;
		border: 1px solid #cbd5e0;
		border-radius: 0.375rem;
		font-family: inherit;
	}

	.speech-box button {
		padding: 0.5rem 1rem;
		background: #4299e1;
		color: white;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		font-weight: 600;
		transition: background 0.2s;
	}

	.speech-box button:hover {
		background: #3182ce;
	}

	.emotion-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.5rem;
	}

	.emotion-grid button {
		padding: 0.4rem;
		font-size: 0.75rem;
		background: #edf2f7;
		border: 1px solid #cbd5e0;
		border-radius: 0.375rem;
		cursor: pointer;
		text-transform: capitalize;
		transition: all 0.2s;
	}

	.emotion-grid button:hover {
		background: #e2e8f0;
	}

	.emotion-grid button.active {
		background: #4a5568;
		color: white;
		border-color: #4a5568;
	}

	.hint {
		margin-top: 1rem;
		font-size: 0.75rem;
		color: #718096;
		font-style: italic;
	}

	.back-link {
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: #4a5568;
		color: white;
		text-decoration: none;
		border-radius: 0.25rem;
	}
</style>
