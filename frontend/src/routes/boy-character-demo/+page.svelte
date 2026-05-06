<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);

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

		function loadGLB(path: string) {
			const loader = new GLTFLoader();
			
			// Setup Draco decoder
			const dracoLoader = new DRACOLoader();
			dracoLoader.setDecoderPath('/draco/');
			loader.setDRACOLoader(dracoLoader);

			loader.load(
				path,
				(gltf) => {
					currentModel = gltf.scene;
					scene.add(currentModel);
					setupModel(currentModel);
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

			// Target area: dari bahu (70% tinggi badan dari bawah) hingga kepala
			// Bahu kira-kira di 72% tinggi, kepala puncak di 100%
			const shoulderY = box.min.y + fullHeight * 0.72;
			const headTopY   = box.max.y;

			// Tengah area bahu-kepala
			const focusCenterY = (shoulderY + headTopY) / 2;

			// Tinggi area yang ingin ditampilkan
			const focusHeight = headTopY - shoulderY;

			// Hitung jarak kamera agar area tersebut mengisi ~75% tinggi layar
			// (25% sisanya sebagai padding — kepala tidak mentok atas)
			const vFovRad = (camera.fov * Math.PI) / 180;
			const desiredCoverage = 0.75; // area bahu-kepala mengisi 75% tinggi layar
			const distance = focusHeight / 2 / Math.tan(vFovRad / 2) / desiredCoverage;

			// Posisikan kamera dan target orbit
			controls.target.set(fullCenter.x, focusCenterY, fullCenter.z);
			camera.position.set(fullCenter.x, focusCenterY, fullCenter.z + distance);
			camera.updateProjectionMatrix();

			// Shadow
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

		// Load the boy character model
		loadGLB('/face/boy/boy-character-copy-optimized.glb');

		function animate() {
			requestAnimationFrame(animate);
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
		};
	});
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
		<p>Model: GLB</p>
		<p>Gunakan mouse untuk memutar, zoom, dan menggeser kamera.</p>
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
		pointer-events: none;
		color: #2d3748;
		background: rgba(255, 255, 255, 0.7);
		padding: 1rem;
		border-radius: 0.5rem;
		backdrop-filter: blur(4px);
		border: 1px solid rgba(255, 255, 255, 0.3);
	}

	h1 {
		margin: 0;
		font-size: 1.5rem;
	}

	p {
		margin: 0.5rem 0 0 0;
		font-size: 0.875rem;
		opacity: 0.8;
	}

	.back-link {
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: #4a5568;
		color: white;
		text-decoration: none;
		border-radius: 0.25rem;
		pointer-events: auto;
	}
</style>
