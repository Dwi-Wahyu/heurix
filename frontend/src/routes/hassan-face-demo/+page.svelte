<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
	import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

	let canvas: HTMLCanvasElement;
	let loading = $state(true);
	let error = $state<string | null>(null);
	let currentModelType = $state('OBJ'); // 'GLB' atau 'OBJ'

	onMount(() => {
		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0xf0f2f5);

		const camera = new THREE.PerspectiveCamera(
			75,
			window.innerWidth / window.innerHeight,
			0.1,
			1000
		);
		camera.position.set(0, 1.5, 3);

		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
		renderer.setSize(window.innerWidth, window.innerHeight);
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.toneMapping = THREE.ReinhardToneMapping;
		renderer.toneMappingExposure = 1.2;
		renderer.shadowMap.enabled = true;

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.target.set(0, 1, 0);

		// Lighting
		const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
		scene.add(ambientLight);

		const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
		directionalLight.position.set(5, 10, 5);
		directionalLight.castShadow = true;
		scene.add(directionalLight);

		let currentModel: THREE.Group | THREE.Object3D | null = null;

		function loadGLB(path: string) {
			const loader = new GLTFLoader();
			loader.load(
				path,
				(gltf) => {
					if (currentModel) scene.remove(currentModel);
					currentModel = gltf.scene;
					scene.add(currentModel);
					setupModel(currentModel);
					loading = false;
				},
				undefined,
				handleError
			);
		}

		function loadOBJMTL(objPath: string, mtlPath: string) {
			const mtlLoader = new MTLLoader();
			// Set resource path for textures to the same directory as MTL
			const baseUrl = mtlPath.substring(0, mtlPath.lastIndexOf('/') + 1);
			mtlLoader.setPath(baseUrl);
			
			mtlLoader.load(mtlPath.split('/').pop()!, (materials) => {
				materials.preload();
				const objLoader = new OBJLoader();
				objLoader.setMaterials(materials);
				objLoader.load(objPath, (object) => {
					if (currentModel) scene.remove(currentModel);
					currentModel = object;
					scene.add(currentModel);
					setupModel(currentModel);
					loading = false;
				}, undefined, handleError);
			}, undefined, handleError);
		}

		function setupModel(model: THREE.Object3D) {
			const box = new THREE.Box3().setFromObject(model);
			const center = box.getCenter(new THREE.Vector3());
			const size = box.getSize(new THREE.Vector3());
			
			controls.target.set(center.x, center.y, center.z);
			camera.position.set(center.x, center.y, center.z + size.y * 1.5);
			
			// Log morph targets if any (GLB usually has them, OBJ rarely does in this format)
			model.traverse((child) => {
				if ((child as THREE.Mesh).isMesh) {
					child.castShadow = true;
					child.receiveShadow = true;
					if ((child as THREE.Mesh).morphTargetDictionary) {
						console.log('Morph targets found in:', child.name, (child as THREE.Mesh).morphTargetDictionary);
					}
				}
			});
		}

		function handleError(err: any) {
			console.error('An error happened', err);
			error = 'Gagal memuat model. Pastikan file tersedia di static folder.';
			loading = false;
		}

		// Initial load
		loadOBJMTL('/face/hassan/full-body.obj', '/face/hassan/full-body.mtl');

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
			<div class="loader">Memuat Model Full Body Hassan...</div>
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
		<h1>Hassan Full Body Demo</h1>
		<p>Model: OBJ + MTL</p>
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
