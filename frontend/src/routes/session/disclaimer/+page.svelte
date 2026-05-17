<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import {
		Video,
		VideoOff,
		Mic,
		MicOff,
		CheckCircle,
		XCircle,
		AlertCircle,
		RotateCcw,
		Headphones,
		Wifi,
		VolumeX,
		Check,
		X,
		AlertCircleIcon
	} from '@lucide/svelte';

	let { data } = $props();
	let avatar = $derived(data.avatar);
	let track = $derived(data.track);

	let confirmed = $state(false);

	// Permission states: 'idle' | 'checking' | 'granted' | 'denied'
	type PermState = 'idle' | 'checking' | 'granted' | 'denied';
	let camPerm = $state<PermState>('idle');
	let micPerm = $state<PermState>('idle');
	let permError = $state<string | null>(null);
	let loading = $state(false);

	// Store the stream so we can release it after check
	let testStream: MediaStream | null = null;

	const bothGranted = $derived(camPerm === 'granted' && micPerm === 'granted');

	// Can proceed only if both permissions granted AND checkbox checked
	const canStart = $derived(bothGranted && confirmed && !loading);

	async function requestPermissions() {
		camPerm = 'checking';
		micPerm = 'checking';
		permError = null;
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
			camPerm = 'granted';
			micPerm = 'granted';
			testStream = stream;
		} catch (err: any) {
			permError = null;
			// Check which ones were denied
			try {
				const videoStream = await navigator.mediaDevices.getUserMedia({
					video: true,
					audio: false
				});
				camPerm = 'granted';
				videoStream.getTracks().forEach((t) => t.stop());
			} catch {
				camPerm = 'denied';
			}
			try {
				const audioStream = await navigator.mediaDevices.getUserMedia({
					video: false,
					audio: true
				});
				micPerm = 'granted';
				audioStream.getTracks().forEach((t) => t.stop());
			} catch {
				micPerm = 'denied';
			}
			if (camPerm === 'denied' || micPerm === 'denied') {
				permError =
					'Akses ditolak. Izinkan kamera dan mikrofon di pengaturan browser lalu muat ulang halaman.';
			}
		}
	}

	onMount(() => {
		// Ensure body is scrollable (fix for navigation from interview page)
		document.body.style.overflow = 'auto';
		document.body.style.position = '';
		document.body.style.width = '';
		document.body.style.height = '';

		requestPermissions();

		// Preload GLB model in the background
		// This ensures the model is cached by the browser and ready for the interview
		const link = document.createElement('link');
		link.rel = 'prefetch';
		link.href = `/${avatar.glbUrl}`;
		link.as = 'fetch';
		document.head.appendChild(link);
	});

	onDestroy(() => {
		// Release test stream when leaving page
		testStream?.getTracks().forEach((t) => t.stop());
	});

	async function handleStart() {
		if (loading) return;
		loading = true;
		// Release test stream — interview page will request its own
		testStream?.getTracks().forEach((t) => t.stop());
		testStream = null;

		try {
			// Get user session to get userId
			const { authClient } = await import('$lib/auth-client');
			const session = await authClient.getSession();
			if (!session.data?.user) {
				goto('/login');
				return;
			}

			const res = await fetch(`/api/proxy/api/sessions`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					userId: session.data.user.id,
					avatarId: avatar.id,
					track: track || 'corporate'
				})
			});

			const { id } = await res.json();
			goto(`/session/interview?sessionId=${id}`);
		} catch (err) {
			console.error('Failed to start session:', err);
			permError = 'Gagal memulai sesi. Silakan coba lagi nanti.';
			loading = false;
		}
	}

	const checklistItems = [
		{
			icon: Headphones,
			title: 'Gunakan headset',
			desc: 'Mikrofon headset menghasilkan suara lebih jernih untuk analisis ucapan.'
		},
		{
			icon: Video,
			title: 'Aktifkan kamera',
			desc: 'Wajah perlu terlihat selama sesi berlangsung.'
		},
		{
			icon: Wifi,
			title: 'Pastikan koneksi stabil',
			desc: 'Sesi video call membutuhkan internet yang tidak terputus.'
		},
		{
			icon: VolumeX,
			title: 'Cari tempat tenang',
			desc: 'Hindari kebisingan latar belakang.'
		}
	];
</script>

<svelte:head>
	<title>Kesiapan Sebelum Sesi — Heurix</title>
</svelte:head>

<div
	class="flex min-h-screen items-center justify-center font-body-md text-on-background selection:bg-primary-fixed selection:text-on-primary-fixed md:bg-background md:p-4"
>
	<main
		class="flex w-full max-w-2xl flex-col gap-8 rounded-2xl bg-surface-container-lowest p-6 shadow-[0px_10px_32px_rgba(0,0,0,0.1)] md:p-8"
	>
		<!-- Header -->
		<header class="text-center">
			<h1 class="mb-2 font-headline-lg text-lg font-bold text-on-surface">Kesiapan Sebelum Sesi</h1>
			<p class="font-body-md text-body-md text-on-surface-variant">
				Pastikan hal-hal berikut untuk mendapatkan hasil analisis AI yang paling akurat.
			</p>
		</header>

		<!-- Permission Status Card -->
		<section class="rounded-xl border border-outline-variant p-4">
			<h2 class="mb-3 text-sm font-semibold text-on-surface">Pemeriksaan Izin Perangkat</h2>
			<div class="flex flex-col gap-2 sm:flex-row sm:gap-4">
				<!-- Camera -->
				<div
					class="flex flex-1 items-center gap-3 rounded-lg p-3 {camPerm === 'granted'
						? 'bg-green-50'
						: camPerm === 'denied'
							? 'bg-red-50'
							: 'bg-surface-container-low'}"
				>
					{#if camPerm === 'granted'}
						<Video size={22} class="text-green-600" />
					{:else}
						<VideoOff
							size={22}
							class={camPerm === 'denied' ? 'text-error' : 'text-on-surface-variant'}
						/>
					{/if}
					<div class="min-w-0">
						<p class="text-xs font-semibold text-on-surface">Kamera</p>
						<p
							class="text-xs {camPerm === 'granted'
								? 'text-green-600'
								: camPerm === 'denied'
									? 'text-error'
									: 'text-on-surface-variant'}"
						>
							{camPerm === 'checking'
								? 'Memeriksa...'
								: camPerm === 'granted'
									? 'Izin diberikan'
									: camPerm === 'denied'
										? 'Akses ditolak'
										: 'Menunggu'}
						</p>
					</div>
					{#if camPerm === 'checking'}
						<div
							class="ml-auto h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"
						></div>
					{:else if camPerm === 'granted'}
						<Check size={18} class="ml-auto text-green-600" fill="currentColor" />
					{:else if camPerm === 'denied'}
						<X size={18} class="ml-auto text-error" fill="currentColor" />
					{/if}
				</div>

				<!-- Microphone -->
				<div
					class="flex flex-1 items-center gap-3 rounded-lg p-3 {micPerm === 'granted'
						? 'bg-green-50'
						: micPerm === 'denied'
							? 'bg-red-50'
							: 'bg-surface-container-low'}"
				>
					{#if micPerm === 'granted'}
						<Mic size={22} class="text-green-600" />
					{:else}
						<MicOff
							size={22}
							class={micPerm === 'denied' ? 'text-error' : 'text-on-surface-variant'}
						/>
					{/if}
					<div class="min-w-0">
						<p class="text-xs font-semibold text-on-surface">Mikrofon</p>
						<p
							class="text-xs {micPerm === 'granted'
								? 'text-green-600'
								: micPerm === 'denied'
									? 'text-error'
									: 'text-on-surface-variant'}"
						>
							{micPerm === 'checking'
								? 'Memeriksa...'
								: micPerm === 'granted'
									? 'Izin diberikan'
									: micPerm === 'denied'
										? 'Akses ditolak'
										: 'Menunggu'}
						</p>
					</div>
					{#if micPerm === 'checking'}
						<div
							class="ml-auto h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"
						></div>
					{:else if micPerm === 'granted'}
						<Check size={18} class="ml-auto text-green-600" fill="currentColor" />
					{:else if micPerm === 'denied'}
						<X size={18} class="ml-auto text-error" fill="currentColor" />
					{/if}
				</div>
			</div>

			{#if permError}
				<div class="mt-3 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-xs text-error">
					<AlertCircleIcon size={16} class="shrink-0" />
					<span>{permError}</span>
				</div>
			{/if}

			{#if camPerm === 'denied' || micPerm === 'denied'}
				<button
					onclick={requestPermissions}
					class="mt-3 flex items-center gap-1.5 rounded-lg border border-primary px-4 py-2 text-xs font-semibold text-primary transition-colors hover:bg-red-50"
				>
					<RotateCcw size={16} />
					Coba Lagi
				</button>
			{/if}
		</section>

		<!-- Readiness Checklist -->
		<section class="flex flex-col gap-3">
			{#each checklistItems as item}
				<div
					class="flex items-start gap-4 rounded-xl border border-outline-variant bg-surface-container-low p-4"
				>
					<div class="mt-0.5 shrink-0 text-primary">
						<item.icon size={24} />
					</div>
					<div>
						<h3 class="mb-1 font-label-bold text-label-bold text-on-surface">{item.title}</h3>
						<p class="text-sm text-on-surface-variant">{item.desc}</p>
					</div>
				</div>
			{/each}
		</section>

		<!-- Confirmation Checkbox -->
		<div class="flex items-center gap-3">
			<input
				bind:checked={confirmed}
				class="h-5 w-5 cursor-pointer rounded border-outline accent-primary focus:ring-2 focus:ring-primary-container"
				id="confirmation-checkbox"
				type="checkbox"
				disabled={!bothGranted}
			/>
			<label
				class="cursor-pointer font-body-md text-body-md select-none {bothGranted
					? 'text-on-surface'
					: 'text-on-surface-variant opacity-50'}"
				for="confirmation-checkbox"
			>
				Saya telah memastikan semua kesiapan di atas.
			</label>
		</div>

		<!-- Actions -->
		<footer
			class="flex flex-col justify-end gap-4 border-t border-outline-variant pt-6 md:flex-row"
		>
			<button
				onclick={() => goto('/dashboard')}
				class="rounded-xl border border-outline px-8 py-3 font-label-bold text-label-bold text-outline transition-colors hover:bg-surface-variant"
			>
				Batalkan
			</button>
			<button
				onclick={handleStart}
				disabled={!canStart}
				class="relative flex items-center justify-center rounded-xl bg-primary px-8 py-3 font-label-bold text-label-bold text-on-primary shadow-[0px_4px_20px_rgba(87,0,0,0.2)] transition-all hover:bg-on-primary-fixed-variant active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
			>
				{#if loading}
					<div
						class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
					></div>
					Memproses...
				{:else}
					Saya siap, mulai sesi
				{/if}
			</button>
		</footer>
	</main>
</div>
