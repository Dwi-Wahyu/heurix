# Fix: Client-side memory leak / lag causing laptop hang on interview page

## File

`src/routes/session/interview/+page.svelte`

## Root cause

`renderer`, `scene`, `camera`, and the `ResizeObserver` are all declared as
**local variables inside `initAvatar()`** (lines ~329, ~347, ~349, ~551), while
`onDestroy()` is defined at the top-level component scope (line 316). Because
of this scoping, `onDestroy` has **no reference** to any of these objects and
cannot clean them up, even though it should. On top of that, the render loop
started with `requestAnimationFrame(animate)` (line 464) never stores its
returned ID, so it can never be cancelled.

Current `onDestroy` only cleans up 4 things:

```js
onDestroy(() => {
  if (browser) {
    document.body.style.overflow = "";
  }
  clearInterval(timerInterval);
  stream?.getTracks().forEach((t) => t.stop());
  ws?.close();
  stopBlink?.();
});
```

It is missing cleanup for:

1. **The `requestAnimationFrame` render loop** — never cancelled, keeps
   rendering the Three.js scene forever, even after the component is
   destroyed and the canvas may be detached from the DOM.
2. **The `ResizeObserver`** — never disconnected; its closure also holds a
   reference to `camera` and `renderer`, preventing them from being
   garbage-collected.
3. **The Three.js `WebGLRenderer`** — `renderer.dispose()` is never called,
   so the WebGL context and its GPU-side resources are never released.
4. **The MediaPipe `FaceLandmarker`** — never `.close()`'d, leaving its WASM
   instance and GPU delegate context running indefinitely.

Because SvelteKit reuses the browser tab across client-side navigation, every
time the user starts a new interview session without a full page reload, a
**new** render loop + new MediaPipe instance + new WebGL context stack on top
of the leaked ones from the previous session — this is why the lag gets worse
progressively and why the DevTools Memory tab showed a large, growing JS heap.

## Task for the agent

### 1. Lift `renderer`, `scene`, `camera`, and the `ResizeObserver` to component scope

Near the existing top-level state declarations (around line 56, next to
`faceLandmarker`), add:

```js
// ── Three.js resources (lifted to component scope for cleanup in onDestroy) ──
let renderer: THREE.WebGLRenderer | undefined;
let scene: THREE.Scene | undefined;
let camera: THREE.PerspectiveCamera | undefined;
let resizeObserver: ResizeObserver | undefined;
let animationFrameId: number | undefined;
```

Then inside `initAvatar()`, change the local declarations to assign to these
component-scoped variables instead of shadowing them with `const`:

- Line ~329: `const renderer = new THREE.WebGLRenderer({...})` → `renderer = new THREE.WebGLRenderer({...})`
- Line ~347: `const scene = new THREE.Scene();` → `scene = new THREE.Scene();`
- Line ~349: `const camera = new THREE.PerspectiveCamera(...)` → `camera = new THREE.PerspectiveCamera(...)`
- The `ResizeObserver` block (~line 551): `const ro = new ResizeObserver(...)` → `resizeObserver = new ResizeObserver(...)`, and `ro.observe(canvasElement)` → `resizeObserver.observe(canvasElement)`

Make sure any code later in the file that references `scene`, `camera`, or
`renderer` (e.g. inside `animate()`) still works with these now being
possibly-`undefined` component-scoped variables — add early returns/guards
where needed (e.g. `if (!renderer || !scene || !camera) return;` at the top
of `animate()`).

### 2. Capture and cancel the animation frame loop

At line ~464, change:

```js
function animate() {
	requestAnimationFrame(animate);
	...
```

to:

```js
function animate() {
	animationFrameId = requestAnimationFrame(animate);
	...
```

### 3. Extend `onDestroy` with full cleanup

Update `onDestroy` (line 316) to:

```js
onDestroy(() => {
	if (browser) {
		document.body.style.overflow = '';
	}
	clearInterval(timerInterval);
	stream?.getTracks().forEach((t) => t.stop());
	ws?.close();
	stopBlink?.();

	// ── Added: stop the render loop ──
	if (animationFrameId !== undefined) {
		cancelAnimationFrame(animationFrameId);
	}

	// ── Added: disconnect the ResizeObserver ──
	resizeObserver?.disconnect();

	// ── Added: release MediaPipe WASM/GPU resources ──
	faceLandmarker?.close();
	faceLandmarker = undefined;

	// ── Added: release Three.js GPU resources ──
	if (scene) {
		scene.traverse((obj: any) => {
			if (obj.geometry) obj.geometry.dispose();
			if (obj.material) {
				const materials = Array.isArray(obj.material) ? obj.material : [obj.material];
				for (const mat of materials) {
					for (const key of Object.keys(mat)) {
						const value = mat[key];
						if (value && typeof value.dispose === 'function') {
							value.dispose(); // textures
						}
					}
					mat.dispose();
				}
			}
		});
	}
	renderer?.dispose();
	renderer = undefined;
	scene = undefined;
	camera = undefined;
});
```

### 4. Optional (recommended) performance improvements, same file

These aren't leaks, but reduce steady-state CPU/GPU load during an active
session — apply if straightforward, otherwise leave for a follow-up pass:

- **`animate()` (~line 500)** currently calls `scene.traverse(...)` every
  single frame to find the model root group for idle sway rotation. Cache a
  direct reference to that group object once (e.g. store it as
  `modelRoot` when the GLB finishes loading in `initAvatar`, next to where
  `animator = new FaceAnimator(model)` is set), and reference it directly in
  `animate()` instead of traversing the whole scene graph every frame.
- **`getUserMedia` call (~line 217)** currently requests
  `{ video: true, audio: true }` with no constraints, which can default to a
  high-resolution camera feed on some devices/browsers. Consider adding
  explicit constraints to cap resolution, e.g.
  `{ video: { width: { ideal: 1280 }, height: { ideal: 720 } }, audio: true }`.

## Do not change

- `FACE_SAMPLE_INTERVAL = 3000` (line 58) — already reasonably throttled at
  one MediaPipe detection every 3 seconds; no change needed.
- `autoBlink.ts` / `startAutoBlink` — already returns a proper cleanup
  function (`stopBlink`) and is already correctly called in `onDestroy`.
  No changes needed there.
- WebSocket logic (`initWebSocket`, `ws?.close()`) — already correctly
  cleaned up in `onDestroy`. No changes needed.

## Verification

1. Rebuild and deploy the frontend as usual.
2. Open the interview page, open DevTools → Performance/Memory, and take a
   heap snapshot.
3. Complete or leave an interview session (navigate to `/session/results` or
   back to `/dashboard`) **without** a full page reload.
4. Take a second heap snapshot. JS heap size should drop back down after
   navigating away (garbage collected), rather than staying flat/growing.
5. Repeat starting 2-3 more interview sessions in the same tab without
   reloading — CPU usage (visible in the browser's task manager,
   `Shift+Esc` in Chrome) should stay roughly constant per active session
   instead of climbing with each new session.

### Summary of Changes made to +page.svelte:

1. Scoped Resources to Component: Lifted Three.js resources (renderer, scene, camera, and modelRoot), the  
   ResizeObserver (resizeObserver), and the animation loop reference (animationFrameId) out of local scope into
   the top-level component scope.
2. Captured & Cancelled animationFrame: Stored the animation request frame ID and correctly cancelled the  
   animation loop using cancelAnimationFrame(animationFrameId) in onDestroy.
3. Released Resources in onDestroy:
   • Disconnected the ResizeObserver.
   • Closed and released MediaPipe FaceLandmarker WASM/GPU delegate resources.
   • Cleaned up the Three.js geometries, materials, textures, and disposed of the WebGLRenderer.
4. Local Constants for Init Callback Safety: Initialized Three.js objects inside initAvatar as local  
   constants (localRenderer, localScene, localCamera) and then assigned them to component variables. This  
   resolved all TypeScript compiler errors about "possibly undefined" variables inside the loader/resize  
   callbacks.
5. Cached Model Root Reference: Replaced the expensive scene.traverse() call occurring on every single frame
   inside animate() with a direct rotation on a cached reference to modelRoot (which is saved when the GLB  
   loader completes).
6. Constrained Camera Resolution: Optimized the getUserMedia call by requesting an ideal 1280x720 resolution
   feed instead of leaving it unconstrained.

These changes prevent JS heap size growth and CPU accumulation across multiple interview sessions in the same
tab, solving the browser lag/hanging issues.
