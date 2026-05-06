<script lang="ts">
	interface Props {
		openness?: number; 
		viseme?: 'rest' | 'ah' | 'ee' | 'oh' | 'uh' | 'm';
		color?: string;
		size?: number;
		isBlinking?: boolean;
	}

	let { 
		openness = 0, 
		viseme = 'rest', 
		color = '#4F46E5', 
		size = 300,
		isBlinking = false 
	}: Props = $props();

	// Definisi Path Mulut untuk berbagai Viseme
	// M x y Q x1 y1 x2 y2 (Quadratic Bezier)
	const mouthShapes = {
		rest: "M 85 135 Q 100 137 115 135", // Tertutup rapat
		ah:   "M 80 130 Q 100 160 120 130", // Terbuka lebar (A)
		ee:   "M 75 135 Q 100 140 125 135", // Melebar ke samping (E, I)
		oh:   "M 90 130 Q 100 155 110 130", // Bulat kecil (O, U)
		uh:   "M 85 132 Q 100 145 115 132", // Terbuka sedang
		m:    "M 85 135 Q 100 135 115 135"  // Terkatup (M, P, B)
	};

	// Logic: Jika viseme tidak ditentukan secara eksplisit, gunakan openness
	let currentMouthPath = $derived.by(() => {
		if (viseme !== 'rest') return mouthShapes[viseme];
		
		// Interpolasi manual sederhana jika hanya menggunakan openness (0-1)
		const height = 2 + (openness * 25);
		return `M ${100 - 20} 135 Q 100 ${135 + height} ${100 + 20} 135`;
	});
</script>

<div class="avatar-box" style="width: {size}px; height: {size}px;">
	<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="avatar-svg">
		<!-- Shadows & Depth -->
		<defs>
			<radialGradient id="faceGrad" cx="50%" cy="50%" r="50%">
				<stop offset="0%" stop-color="#fff" />
				<stop offset="100%" stop-color="#f0f2f5" />
			</radialGradient>
			<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
				<feGaussianBlur in="SourceAlpha" stdDeviation="3" />
				<feOffset dx="0" dy="4" result="offsetblur" />
				<feComponentTransfer>
					<feFuncA type="linear" slope="0.1" />
				</feComponentTransfer>
				<feMerge>
					<feMergeNode />
					<feMergeNode in="SourceGraphic" />
				</feMerge>
			</filter>
		</defs>

		<!-- Head Base -->
		<circle cx="100" cy="100" r="90" fill="url(#faceGrad)" stroke="#e2e8f0" stroke-width="1" />
		
		<!-- Hair / Professional Cap -->
		<path d="M20 80 C20 30 60 15 100 15 C140 15 180 30 180 80 L180 90 L20 90 Z" fill="#2d3748" />

		<!-- Eyes Section -->
		<g class="eyes" filter="url(#softShadow)">
			{#if isBlinking}
				<!-- Blinking state (Horizontal lines) -->
				<path d="M60 85 H80" stroke="#2d3748" stroke-width="3" stroke-linecap="round" />
				<path d="M120 85 H140" stroke="#2d3748" stroke-width="3" stroke-linecap="round" />
			{:else}
				<!-- Open state -->
				<g class="eye-left">
					<circle cx="70" cy="85" r="7" fill="white" />
					<circle cx="72" cy="83" r="3" fill="#2d3748" /> <!-- Pupil -->
				</g>
				<g class="eye-right">
					<circle cx="130" cy="85" r="7" fill="white" />
					<circle cx="128" cy="83" r="3" fill="#2d3748" /> <!-- Pupil -->
				</g>
			{/if}
		</g>

		<!-- Eyebrows -->
		<path d="M55 70 Q70 65 85 72" stroke="#2d3748" stroke-width="2.5" fill="none" stroke-linecap="round" />
		<path d="M115 72 Q130 65 145 70" stroke="#2d3748" stroke-width="2.5" fill="none" stroke-linecap="round" />

		<!-- Nose -->
		<path d="M100 95 C105 95 108 105 100 115" stroke="#cbd5e0" stroke-width="2" fill="none" stroke-linecap="round" />

		<!-- Mouth (The core of Viseme) -->
		<g class="mouth-container">
			<!-- Inner Mouth (Dark area when open) -->
			{#if openness > 0.3 || viseme !== 'rest'}
				<path d={currentMouthPath} fill="#4a1515" opacity="0.2" />
			{/if}
			
			<!-- Main Mouth Line -->
			<path
				d={currentMouthPath}
				stroke={color}
				stroke-width="4"
				fill="none"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="mouth-path"
			/>
		</g>

		<!-- Jaw Detail -->
		<path d="M60 160 Q100 180 140 160" stroke="#e2e8f0" stroke-width="2" fill="none" opacity="0.5" />
	</svg>
</div>

<style>
	.avatar-box {
		display: flex;
		align-items: center;
		justify-content: center;
		perspective: 1000px;
	}

	.avatar-svg {
		width: 100%;
		height: 100%;
		filter: drop-shadow(0 20px 25px rgba(0, 0, 0, 0.1));
	}

	.mouth-path {
		transition: d 0.08s ease-in-out; /* Sangat cepat agar sinkron dengan audio */
	}

	.eyes circle {
		transition: r 0.1s ease;
	}
</style>
