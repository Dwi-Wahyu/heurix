<script lang="ts">
	import { enhance } from '$app/forms';

	let { data, form } = $props();

	let step = $state(1);

	// Data selection state
	let path = $state<'corporate' | 'military' | 'civil_service' | 'stan' | null>(null);
	let selectedInstitutionId = $state<string | null>(null);
	let selectedPositionId = $state<string | null>(null);

	// Search state
	let institutionSearch = $state('');
	let positionSearch = $state('');

	// Hidden form for submission
	let formElement: HTMLFormElement;

	const nextStep = () => {
		if (step < 4) {
			step += 1;
		} else {
			if (formElement) {
				formElement.requestSubmit();
			}
		}
	};

	const prevStep = () => {
		if (step > 1) {
			step -= 1;
		}
	};

	// Filtered institutions based on path (Step 3)
	let filteredInstitutions = $derived(
		data.institutions
			.filter((inst) => {
				if (!path) return true;
				return path === 'corporate' ? inst.track === 'corporate' : inst.track !== 'corporate';
			})
			.filter((inst) =>
				institutionSearch ? inst.name.toLowerCase().includes(institutionSearch.toLowerCase()) : true
			)
	);

	// Filtered positions based on selected institution + search
	let filteredPositions = $derived(
		data.positions
			.filter((p) => (selectedInstitutionId ? p.institutionId === selectedInstitutionId : true))
			.filter((p) =>
				positionSearch ? p.name.toLowerCase().includes(positionSearch.toLowerCase()) : true
			)
	);
</script>

<svelte:head>
	<title>Onboarding — HiReady</title>
</svelte:head>

<!-- Hidden form for server action -->
<form bind:this={formElement} method="POST" use:enhance class="hidden">
	<input type="hidden" name="path" value={path} />
	<input type="hidden" name="institutionId" value={selectedInstitutionId} />
	<input type="hidden" name="positionId" value={selectedPositionId} />
</form>

<div
	class="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4 selection:bg-primary-fixed selection:text-on-primary-fixed md:p-10"
>
	<main class="flex w-full max-w-[840px] flex-col gap-10">
		<!-- Header: Progress + Title -->
		<header class="flex flex-col gap-6 text-center md:text-left">
			<!-- Progress -->
			<div class="flex flex-col items-center gap-2 md:items-start">
				<span
					class="font-label-bold text-label-bold text-sm font-semibold tracking-wider text-primary uppercase"
				>
					Langkah {step} dari 4
				</span>
				<div class="flex w-full max-w-[240px] gap-2">
					{#each [1, 2, 3, 4] as s}
						<div
							class="h-1.5 flex-1 rounded-full transition-colors {step >= s
								? 'bg-primary'
								: 'bg-surface-variant'}"
						></div>
					{/each}
				</div>
			</div>

			<!-- Step title/description -->
			<div class="mt-2 flex flex-col gap-2">
				{#if step === 1}
					<h1 class="font-headline-lg text-headline-lg text-on-surface">
						Halo!<br />
						<span class="text-primary">Selamat datang di HiReady</span>
					</h1>
					<p class="font-body-lg text-body-lg mx-auto max-w-xl text-on-surface-variant md:mx-0">
						Berlatih wawancara kerja jadi lebih mudah dan efektif dengan pewawancara virtual AI kami
						yang canggih.
					</p>
				{:else if step === 2}
					<h1 class="font-headline-lg text-headline-lg text-on-surface">Pilih Jalur Karir Kamu</h1>
					<p class="font-body-lg text-body-lg text-on-surface-variant">
						Sesuaikan simulasi dengan target impianmu.
					</p>
				{:else if step === 3}
					<h1 class="font-headline-lg text-headline-lg text-on-surface">
						Pilih Target Perusahaan atau Instansi
					</h1>
					<p class="font-body-lg text-body-lg max-w-2xl text-on-surface-variant">
						Pilih satu tempat tujuan karir Anda. Sistem AI kami akan menyesuaikan konteks wawancara
						dengan budaya dan standar institusi tersebut.
					</p>
				{:else if step === 4}
					<h1 class="font-headline-lg text-headline-lg text-on-surface">
						Pilih Posisi yang Ingin Kamu Latih
					</h1>
					<p class="font-body-lg text-body-lg text-on-surface-variant">
						Sesuaikan simulasi wawancara dengan target karir spesifikmu.
					</p>
				{/if}
			</div>
		</header>

		<!-- Content Area -->
		<section class="min-h-[280px]">
			{#if step === 1}
				<!-- Welcome illustration -->
				<div
					class="flex h-[300px] w-full items-center justify-center overflow-hidden rounded-2xl bg-surface-container-low shadow-sm"
				>
					<img
						alt="HiReady Illustration"
						class="h-full w-full object-cover opacity-90 mix-blend-multiply"
						src="/onboarding-logo.png"
						
					/>
				</div>
			{:else if step === 2}
				<!-- Path Selection -->
				<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
					<!-- Corporate card -->
					<button
						onclick={() => (path = 'corporate')}
						class="group relative flex flex-col items-start rounded-xl border-2 bg-surface-container-lowest p-6 text-left transition-all outline-none {path ===
						'corporate'
							? 'border-primary shadow-[0px_10px_32px_rgba(0,0,0,0.05)] ring-4 ring-primary/10'
							: 'border-outline-variant hover:border-primary-fixed-dim hover:shadow-soft'}"
					>
						{#if path === 'corporate'}
							<div class="absolute top-6 right-6 text-primary">
								<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;"
									>check_circle</span
								>
							</div>
						{/if}
						<div
							class="mb-4 flex h-14 w-14 items-center justify-center rounded-full transition-colors {path ===
							'corporate'
								? 'bg-primary-container text-on-primary-container'
								: 'bg-surface-variant text-on-surface-variant group-hover:bg-primary-fixed group-hover:text-on-primary-fixed'}"
						>
							<span class="material-symbols-outlined text-[28px]">domain</span>
						</div>
						<h2 class="font-headline-md text-headline-md mb-1 text-on-surface">
							Swasta / Korporat
						</h2>
						<p class="font-body-md text-body-md text-on-surface-variant">
							Untuk pelamar perusahaan swasta, startup, atau BUMN.
						</p>
					</button>

					<!-- Kedinasan card -->
					<button
						onclick={() => (path = 'military')}
						class="group relative flex flex-col items-start rounded-xl border-2 bg-surface-container-lowest p-6 text-left transition-all outline-none {path &&
						path !== 'corporate'
							? 'border-primary shadow-[0px_10px_32px_rgba(0,0,0,0.05)] ring-4 ring-primary/10'
							: 'border-outline-variant hover:border-primary-fixed-dim hover:shadow-soft'}"
					>
						{#if path && path !== 'corporate'}
							<div class="absolute top-6 right-6 text-primary">
								<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;"
									>check_circle</span
								>
							</div>
						{/if}
						<div
							class="mb-4 flex h-14 w-14 items-center justify-center rounded-full transition-colors {path &&
							path !== 'corporate'
								? 'bg-primary-container text-on-primary-container'
								: 'bg-surface-variant text-on-surface-variant group-hover:bg-primary-fixed group-hover:text-on-primary-fixed'}"
						>
							<span class="material-symbols-outlined text-[28px]">account_balance</span>
						</div>
						<h2 class="font-headline-md text-headline-md mb-1 text-on-surface">Kedinasan</h2>
						<p class="font-body-md text-body-md text-on-surface-variant">
							Untuk pendaftar Akmil, Akpol, STAN, dan institusi lainnya.
						</p>
					</button>
				</div>
			{:else if step === 3}
				<!-- Institution Selection -->
				<div class="flex flex-col gap-6">
					<!-- Search -->
					<div class="relative w-full max-w-lg">
						<span
							class="pointer-events-none absolute top-1/2 left-4 material-symbols-outlined -translate-y-1/2 text-outline"
							>search</span
						>
						<input
							bind:value={institutionSearch}
							class="font-body-md w-full rounded-xl border border-outline-variant bg-surface py-3.5 pr-4 pl-12 text-on-surface shadow-inner transition-all outline-none placeholder:text-outline focus:border-primary focus:ring-2 focus:ring-primary/20"
							placeholder="Cari perusahaan atau instansi..."
							type="text"
						/>
					</div>

					<!-- Institution grid -->
					<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
						{#each filteredInstitutions as inst}
							<button
								onclick={() => {
									selectedInstitutionId = inst.id;
									if (path !== 'corporate') {
										path = inst.track;
									}
								}}
								class="group relative flex flex-col items-center justify-center overflow-hidden rounded-xl border-2 p-4 text-center transition-all {selectedInstitutionId ===
								inst.id
									? 'border-primary bg-primary-fixed shadow-[0px_10px_32px_rgba(0,0,0,0.05)] ring-4 ring-primary/10'
									: 'border-outline-variant bg-surface hover:border-primary-fixed hover:bg-surface-container-low'}"
							>
								{#if selectedInstitutionId === inst.id}
									<span
										class="absolute top-2 right-2 material-symbols-outlined text-[18px] text-primary"
										style="font-variation-settings: 'FILL' 1;">check_circle</span
									>
								{/if}
								<div
									class="mb-2 flex h-14 w-14 items-center justify-center overflow-hidden rounded-full bg-surface-container-lowest p-2 shadow-sm"
								>
									{#if inst.logoUrl}
										<img
											alt="{inst.name} Logo"
											class="h-full w-full object-contain"
											src={inst.logoUrl}
										/>
									{:else}
										<span class="material-symbols-outlined text-outline">business</span>
									{/if}
								</div>
								<span
									class="font-label-bold text-label-bold text-[12px] leading-tight transition-colors {selectedInstitutionId ===
									inst.id
										? 'text-on-primary-fixed'
										: 'text-on-surface-variant group-hover:text-on-surface'}"
								>
									{inst.name}
								</span>
							</button>
						{/each}

						{#if filteredInstitutions.length === 0}
							<div class="col-span-full py-8 text-center">
								<span class="mb-2 material-symbols-outlined text-[40px] text-outline"
									>search_off</span
								>
								<p class="font-body-md text-body-md text-on-surface-variant">
									Tidak ada hasil ditemukan.
								</p>
							</div>
						{/if}
					</div>
				</div>
			{:else if step === 4}
				<!-- Position Selection -->
				<div class="flex flex-col gap-6">
					<!-- Search -->
					<div class="relative w-full max-w-lg">
						<span
							class="pointer-events-none absolute top-1/2 left-4 material-symbols-outlined -translate-y-1/2 text-outline"
							>search</span
						>
						<input
							bind:value={positionSearch}
							class="font-body-md w-full rounded-xl border border-outline-variant bg-surface py-3.5 pr-4 pl-12 text-on-surface shadow-inner transition-all outline-none placeholder:text-outline focus:border-primary focus:ring-2 focus:ring-primary/20"
							placeholder="Cari posisi..."
							type="text"
						/>
					</div>

					<!-- Position list -->
					<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
						{#each filteredPositions as pos}
							<button
								onclick={() => (selectedPositionId = pos.id)}
								class="group relative flex cursor-pointer items-start gap-4 rounded-xl border-2 p-4 shadow-sm transition-all {selectedPositionId ===
								pos.id
									? 'border-primary bg-primary-container ring-4 ring-primary/10'
									: 'border-outline-variant bg-surface hover:border-primary-fixed hover:bg-surface-container-low'}"
							>
								{#if selectedPositionId === pos.id}
									<div class="absolute top-4 right-4">
										<span
											class="material-symbols-outlined text-primary"
											style="font-variation-settings: 'FILL' 1;">check_circle</span
										>
									</div>
								{/if}
								<div
									class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-colors {selectedPositionId ===
									pos.id
										? 'bg-surface-container-lowest text-primary'
										: 'bg-surface-container text-on-surface-variant group-hover:bg-primary-fixed group-hover:text-primary'}"
								>
									<span class="material-symbols-outlined">work</span>
								</div>
								<div class="flex flex-col pr-8 text-left">
									<span
										class="font-label-md text-sm font-semibold {selectedPositionId === pos.id
											? 'text-on-primary-container'
											: 'text-on-surface group-hover:text-primary'}"
									>
										{pos.name}
									</span>
									{#if pos.description}
										<span
											class="mt-0.5 line-clamp-2 text-xs {selectedPositionId === pos.id
												? 'text-on-primary-container opacity-80'
												: 'text-on-surface-variant'}"
										>
											{pos.description}
										</span>
									{/if}
								</div>
							</button>
						{/each}

						{#if filteredPositions.length === 0}
							<div class="col-span-full py-8 text-center">
								<span class="mb-2 material-symbols-outlined text-[40px] text-outline"
									>search_off</span
								>
								<p class="font-body-md text-body-md text-on-surface-variant">
									Tidak ada posisi ditemukan.
								</p>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</section>

		<!-- Footer Actions -->
		<footer class="flex flex-col gap-3 border-t border-outline-variant pt-6">
			{#if form?.message}
				<div class="flex items-center gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-error">
					<span class="material-symbols-outlined text-[18px]">error</span>
					{form.message}
				</div>
			{/if}

			<div class="flex items-center {step > 1 ? 'justify-between' : 'justify-end'}">
				{#if step > 1}
					<button
						onclick={prevStep}
						class="font-label-bold flex items-center gap-2 rounded-lg px-6 py-3 text-sm font-semibold text-on-surface-variant transition-colors hover:text-on-surface"
					>
						<span class="material-symbols-outlined text-[20px]">arrow_back</span>
						Kembali
					</button>
				{/if}

				<button
					onclick={nextStep}
					class="font-label-bold flex items-center gap-2 rounded-lg bg-primary px-10 py-[14px] text-sm font-semibold text-on-primary shadow-[0px_4px_20px_rgba(87,0,0,0.2)] transition-all outline-none hover:bg-on-primary-fixed-variant active:scale-[0.98]"
				>
					{step === 4 ? 'Selesai' : 'Lanjutkan'}
					<span class="material-symbols-outlined text-[18px]">arrow_forward</span>
				</button>
			</div>
		</footer>
	</main>
</div>

<style>
	:global(.material-symbols-outlined) {
		font-variation-settings:
			'FILL' 0,
			'wght' 400,
			'GRAD' 0,
			'opsz' 24;
	}
</style>
