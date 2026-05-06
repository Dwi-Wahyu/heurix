<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
	import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
	import { FaceAnimator } from '$lib/FaceAnimator';
	import { VISEME_MAP } from '$lib/visemeMap';
	import { EMOTION_PRESETS } from '$lib/emotionPresets';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);
	let animator: FaceAnimator | null = $state.raw(null);
	let currentViseme = $state('sil');
	let currentEmotion = $state('neutral');

	onMount(() => {
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0xf0f2f5);

		const camera = new THREE.PerspectiveCamera(
			45,
			window.innerWidth / window.innerHeight,
			0.1,
			1000
		);
		camera.position.set(0, 1.6, 0.6); 

		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
		renderer.setSize(window.innerWidth, window.innerHeight);
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.toneMapping = THREE.ReinhardToneMapping;
		renderer.toneMappingExposure = 1.2;
		renderer.shadowMap.enabled = true;

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.target.set(0, 1.6, 0);

		const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
		scene.add(ambientLight);

		const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
		directionalLight.position.set(2, 4, 5);
		directionalLight.castShadow = true;
		scene.add(directionalLight);

		// Setup Loaders
		const dracoLoader = new DRACOLoader();
		dracoLoader.setDecoderPath('/draco/');

		const loader = new GLTFLoader();
		loader.setDRACOLoader(dracoLoader);
		loader.setMeshoptDecoder(MeshoptDecoder);

		loader.load(
			'/face/hassan/model.glb',
			(gltf) => {
				const model = gltf.scene;
				scene.add(model);
				
				const headBone = model.getObjectByName('Head'); 
				if (headBone) {
					const worldPos = new THREE.Vector3();
					headBone.getWorldPosition(worldPos);
					controls.target.set(worldPos.x, worldPos.y, worldPos.z);
					camera.position.set(worldPos.x, worldPos.y, worldPos.z + 0.5);
				}

				animator = new FaceAnimator(model);
				loading = false;
			},
			undefined,
			(err) => {
				console.error(err);
				error = 'Gagal memuat model Hassan GLB. Periksa console untuk detail.';
				loading = false;
			}
		);

		let lastTime = performance.now();

		function animate() {
			requestAnimationFrame(animate);
			const time = performance.now();
			const delta = (time - lastTime) / 1000;
			lastTime = time;

			if (animator) {
				animator.update(delta);
			}
			controls.update();
			renderer.render(scene, camera);
		}

		animate();

		const handleResize = () => {
			camera.aspect = window.innerWidth / window.innerHeight;
			camera.updateProjectionMatrix();
			renderer.setSize(window.innerWidth, window.innerHeight);
		};

		window.addEventListener('resize', handleResize);

		return () => {
			window.removeEventListener('resize', handleResize);
			renderer.dispose();
			dracoLoader.dispose();
		};
	});

	function setViseme(id: string) {
		currentViseme = id;
		if (animator) {
			animator.setViseme(id);
		}
	}

	function setEmotion(id: string) {
		currentEmotion = id;
		if (animator) {
			const weights = EMOTION_PRESETS[id as keyof typeof EMOTION_PRESETS] || {};
			animator.setExpression(weights);
		}
	}

	const visemes = Object.keys(VISEME_MAP);
	const emotions = ['neutral', 'happy', 'sad', 'angry', 'surprised', 'disgusted'];
</script>

<div class="container">
	{#if loading}
		<div class="overlay">
			<div class="loader">Memuat Hassan GLB (Compressed)...</div>
		</div>
	{/if}

	{#if error}
		<div class="overlay error">
			<p>{error}</p>
		</div>
	{/if}

	<canvas bind:this={canvas}></canvas>

	<div class="ui">
		<div class="card">
			<h2>Hassan Animation Demo</h2>
			<p>Model: GLB (CC Base + Meshopt)</p>
			
			<div class="control-group">
				<h3>Visemes</h3>
				<div class="grid">
					{#each visemes as vis (vis)}
						<button 
							class:active={currentViseme === vis}
							onclick={() => setViseme(vis)}
						>
							{vis}
						</button>
					{/each}
				</div>
			</div>

			<div class="control-group">
				<h3>Emotions</h3>
				<div class="grid">
					{#each emotions as emo (emo)}
						<button 
							class:active={currentEmotion === emo}
							onclick={() => setEmotion(emo)}
						>
							{emo}
						</button>
					{/each}
				</div>
			</div>
			
			<button class="reset-btn" onclick={() => { animator?.resetFace(); currentViseme = 'sil'; currentEmotion = 'neutral'; }}>
				Reset Face
			</button>
		</div>
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
		background: rgba(255, 255, 255, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.loader {
		font-size: 1.25rem;
		font-weight: 600;
		color: #4a5568;
	}

	.ui {
		position: absolute;
		top: 1rem;
		right: 1rem;
		width: 320px;
		max-height: calc(100vh - 2rem);
		overflow-y: auto;
		z-index: 10;
	}

	.card {
		background: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(10px);
		padding: 1.5rem;
		border-radius: 1rem;
		box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.5);
	}

	h2 { margin: 0; font-size: 1.25rem; color: #1a202c; }
	h3 { margin: 1rem 0 0.5rem 0; font-size: 0.875rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.05em; }
	p { margin: 0.25rem 0 1rem 0; font-size: 0.75rem; color: #718096; }

	.grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.5rem;
	}

	button {
		padding: 0.5rem;
		font-size: 0.75rem;
		background: #edf2f7;
		border: 1px solid #e2e8f0;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	button:hover { background: #e2e8f0; }
	button.active { background: #3182ce; color: white; border-color: #2b6cb0; }

	.reset-btn {
		width: 100%;
		margin-top: 1.5rem;
		padding: 0.75rem;
		background: #e53e3e;
		color: white;
		font-weight: 600;
		border: none;
	}

	.reset-btn:hover { background: #c53030; }
</style>