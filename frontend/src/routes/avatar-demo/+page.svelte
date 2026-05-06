<script lang="ts">
	import Avatar from '$lib/Avatar.svelte';
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';

	// --- STATE ---
	let textToSpeak = $state('Halo! Sekarang saya bisa berkedip secara otomatis agar terlihat lebih hidup. Silakan coba Mode Simulasi atau Putar Suara.');
	let openness = $state(0);
	let isSpeaking = $state(false);
	let isSimulating = $state(false);
	let isBlinking = $state(false);
	let voiceSelected = $state('');
	let availableVoices = $state<SpeechSynthesisVoice[]>([]);
	
	let animationId: number;
	let blinkTimeout: ReturnType<typeof setTimeout>;

	// --- LOGIKA KEDIP (Auto Blink) ---
	function scheduleBlink() {
		const nextBlink = 2000 + Math.random() * 4000; // Kedip setiap 2-6 detik
		blinkTimeout = setTimeout(() => {
			if (!browser) return;
			isBlinking = true;
			setTimeout(() => {
				isBlinking = false;
				scheduleBlink();
			}, 150); // Lama kedipan 150ms
		}, nextBlink);
	}

	// --- LOGIKA ANIMASI MULUT ---
	function animateMouth() {
		if (isSpeaking || isSimulating) {
			// Gerakan acak untuk simulasi bicara
			openness = 0.1 + Math.random() * 0.8;
		} else {
			openness = 0;
		}
		animationId = requestAnimationFrame(animateMouth);
	}

	// --- LOGIKA SPEECH SYNTHESIS ---
	function loadVoices() {
		if (!browser) return;
		const voices = window.speechSynthesis.getVoices();
		if (voices.length > 0) {
			availableVoices = voices;
			if (!voiceSelected) {
				const idVoice = voices.find(v => v.lang.includes('id'));
				const enVoice = voices.find(v => v.lang.includes('en'));
				voiceSelected = (idVoice || enVoice || voices[0]).name;
			}
		}
	}

	function handleSpeak() {
		if (!browser || !textToSpeak) return;
		
		isSimulating = false;
		window.speechSynthesis.cancel();

		const utterance = new SpeechSynthesisUtterance(textToSpeak);
		const selectedVoice = availableVoices.find(v => v.name === voiceSelected);
		if (selectedVoice) utterance.voice = selectedVoice;

		utterance.onstart = () => { isSpeaking = true; };
		utterance.onend = () => { isSpeaking = false; openness = 0; };
		utterance.onerror = () => { isSpeaking = false; openness = 0; };

		window.speechSynthesis.speak(utterance);
	}

	// --- MODE SIMULASI (Jika TTS Rusak) ---
	function handleSimulate() {
		if (isSpeaking || isSimulating) return;
		
		isSimulating = true;
		// Simulasi durasi bicara berdasarkan panjang teks (rata-rata 80ms per karakter)
		const duration = textToSpeak.length * 80; 
		
		setTimeout(() => {
			isSimulating = false;
			openness = 0;
		}, duration);
	}

	onMount(() => {
		if (browser) {
			animateMouth();
			loadVoices();
			scheduleBlink();
			
			if (window.speechSynthesis.onvoiceschanged !== undefined) {
				window.speechSynthesis.onvoiceschanged = loadVoices;
			}
			
			// Retry load voices for some browsers
			const interval = setInterval(() => {
				if (availableVoices.length === 0) loadVoices();
				else clearInterval(interval);
			}, 1000);
		}
	});

	onDestroy(() => {
		if (browser) {
			window.speechSynthesis.cancel();
			cancelAnimationFrame(animationId);
			clearTimeout(blinkTimeout);
		}
	});
</script>

<div class="demo-container">
	<header>
		<a href="/" class="back-link">← Kembali ke Dashboard</a>
		<h1>AI AVATAR SPEECH DEMO</h1>
		<p class="subtitle">Teknologi Viseme Ringan (SVG-Based Animation)</p>
	</header>

	<main class="demo-layout">
		<section class="visual-card">
			<div class="avatar-wrapper">
				<Avatar {openness} {isBlinking} size={320} color={(isSpeaking || isSimulating) ? '#10b981' : '#4f46e5'} />
			</div>
			<div class="status-badge" class:speaking={isSpeaking || isSimulating}>
				{(isSpeaking || isSimulating) ? 'SEDANG BERBICARA' : 'STANDBY'}
			</div>
			{#if isSimulating}
				<p class="sim-hint">Mencoba mensimulasikan gerakan tanpa suara...</p>
			{/if}
		</section>

		<section class="control-card">
			<div class="input-group">
				<label for="text-input">Masukkan Teks Demo:</label>
				<textarea id="text-input" bind:value={textToSpeak} placeholder="Tulis sesuatu..."></textarea>
			</div>

			<div class="settings-row">
				<div class="input-group">
					<label for="voice-select">Pilih Suara (Browser):</label>
					{#if availableVoices.length > 0}
						<select id="voice-select" bind:value={voiceSelected}>
							{#each availableVoices as voice}
								<option value={voice.name}>{voice.name} ({voice.lang})</option>
							{/each}
						</select>
					{:else}
						<div class="warning-box">
							⚠️ Browser Anda tidak mendeteksi suara sistem. 
							<br><small>Gunakan tombol "Simulasi" di bawah untuk melihat gerakan avatar.</small>
						</div>
					{/if}
				</div>
			</div>

			<div class="btn-group">
				<button class="speak-btn" onclick={handleSpeak} disabled={isSpeaking || isSimulating || availableVoices.length === 0}>
					🔊 Putar Suara Asli
				</button>
				
				<button class="sim-btn" onclick={handleSimulate} disabled={isSpeaking || isSimulating}>
					✨ Mode Simulasi (Visual Only)
				</button>
			</div>

			<div class="troubleshoot">
				<h5>Bantuan Khusus Linux:</h5>
				<ul>
					<li>Coba buka halaman ini di <strong>Firefox</strong> (biasanya lebih stabil untuk TTS).</li>
					<li>Cek apakah perintah <code>spd-say "halo"</code> di terminal berbunyi.</li>
					<li>Gunakan <strong>Mode Simulasi</strong> untuk demo visual tanpa tergantung TTS browser.</li>
				</ul>
			</div>
		</section>
	</main>
</div>

<style>
	:global(body) { background-color: #0f1117; color: #e2e8f0; font-family: 'Inter', sans-serif; margin: 0; }
	.demo-container { max-width: 1000px; margin: 0 auto; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }
	header { text-align: center; }
	.back-link { color: #6366f1; text-decoration: none; font-size: 0.9rem; font-weight: 600; }
	h1 { margin: 1rem 0 0.5rem; font-size: 2.2rem; font-weight: 900; background: linear-gradient(to right, #818cf8, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
	.subtitle { color: #94a3b8; font-size: 1rem; }
	.demo-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 2rem; }
	.visual-card { background: #1e293b; padding: 2.5rem; border-radius: 2rem; display: flex; flex-direction: column; align-items: center; gap: 1.5rem; border: 1px solid rgba(255,255,255,0.05); }
	.status-badge { padding: 0.5rem 1.5rem; border-radius: 2rem; font-size: 0.75rem; font-weight: 800; background: #334155; color: #94a3b8; }
	.status-badge.speaking { background: rgba(16, 185, 129, 0.2); color: #10b981; }
	.sim-hint { font-size: 0.75rem; color: #10b981; font-style: italic; margin: 0; }
	.control-card { background: #1e293b; padding: 2rem; border-radius: 2rem; display: flex; flex-direction: column; gap: 1.5rem; }
	.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
	label { font-size: 0.85rem; font-weight: 600; color: #94a3b8; }
	textarea { background: #0f172a; border: 1px solid #334155; border-radius: 1rem; padding: 1rem; color: #f1f5f9; min-height: 80px; }
	.warning-box { padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 0.75rem; color: #ef4444; font-size: 0.8rem; }
	select { background: #0f172a; border: 1px solid #334155; border-radius: 0.75rem; padding: 0.75rem; color: #f1f5f9; }
	.btn-group { display: flex; flex-direction: column; gap: 0.75rem; }
	.speak-btn, .sim-btn { padding: 1rem; border-radius: 1rem; font-weight: 700; cursor: pointer; transition: all 0.2s; border: none; }
	.speak-btn { background: #4f46e5; color: white; }
	.speak-btn:disabled { background: #334155; opacity: 0.5; }
	.sim-btn { background: #10b981; color: white; }
	.sim-btn:disabled { background: #334155; opacity: 0.5; }
	.troubleshoot { margin-top: 1rem; padding: 1rem; background: rgba(0, 0, 0, 0.2); border-radius: 1rem; border-left: 4px solid #6366f1; }
	.troubleshoot h5 { margin: 0 0 0.5rem; font-size: 0.85rem; }
	.troubleshoot ul { margin: 0; padding-left: 1.2rem; font-size: 0.75rem; color: #94a3b8; line-height: 1.4; }
	@media (max-width: 800px) { .demo-layout { grid-template-columns: 1fr; } }
</style>
