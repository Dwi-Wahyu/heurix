<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import { sidebarState } from '$lib/sidebar.svelte';
	import { Award } from '@lucide/svelte';

	let { data } = $props();

	const { user, profile } = data;

	const isProfileComplete =
		profile !== null &&
		profile.preferredTrack !== null &&
		profile.targetInstitutionId !== null &&
		profile.targetPositionId !== null;

	// Track label map
	const trackLabels: Record<string, string> = {
		corporate: 'Swasta / Korporat',
		military: 'Kedinasan (Militer)',
		civil_service: 'CPNS Umum',
		stan: 'PKN STAN'
	};

	// Initials fallback
	function getInitials(name: string) {
		return name
			.split(' ')
			.slice(0, 2)
			.map((n) => n[0])
			.join('')
			.toUpperCase();
	}

	// Format date
	function formatDate(d: Date | string) {
		return new Date(d).toLocaleDateString('id-ID', {
			day: 'numeric',
			month: 'long',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Profil Saya — HiReady</title>
</svelte:head>

<div class="flex min-h-screen bg-[#f4f7fb]">
	<Sidebar />

	<div
		class="flex min-h-screen flex-1 flex-col transition-all duration-300 {sidebarState.isOpen
			? 'md:ml-64'
			: 'md:ml-20'}"
	>
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-5 pt-20 pb-20 md:px-8">
			<!-- Page Title -->
			<section class="mb-8">
				<h1 class="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">Profil Saya</h1>
				<p class="mt-1 text-base text-gray-500">Kelola informasi akun dan preferensi karirmu.</p>
			</section>

			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<!-- Left Column: Identity Card -->
				<div class="flex flex-col gap-6 lg:col-span-1">
					<!-- Avatar & Name Card -->
					<div
						class="relative overflow-hidden rounded-3xl border border-gray-100 bg-white p-8 text-center shadow-soft"
					>
						<!-- Background decoration -->
						<div
							class="absolute -top-8 -right-8 h-32 w-32 rounded-full bg-red-50 opacity-60 blur-2xl"
						></div>
						<div
							class="absolute -bottom-6 -left-6 h-24 w-24 rounded-full bg-red-100/40 blur-xl"
						></div>

						<div class="relative z-10 flex flex-col items-center">
							<!-- Avatar -->
							<div
								class="mb-4 flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-primary to-[#570000] shadow-lg ring-4 ring-red-100"
							>
								{#if user.image}
									<img src={user.image} alt={user.name} class="h-full w-full object-cover" />
								{:else}
									<span class="text-3xl font-bold text-white">{getInitials(user.name)}</span>
								{/if}
							</div>

							<h2 class="text-xl font-bold text-gray-900">{user.name}</h2>
							<p class="mt-1 text-sm text-gray-500">{user.email}</p>

							<p class="mt-4 text-xs text-gray-400">
								Bergabung sejak {formatDate(user.createdAt)}
							</p>
						</div>
					</div>

					<!-- Stats Card -->
					<div class="rounded-3xl border border-gray-100 bg-white p-6 shadow-soft">
						<h3 class="mb-4 text-base font-bold text-gray-800">Statistik Latihan</h3>
						<div class="flex flex-col gap-4">
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2 text-gray-500">
									<span class="material-symbols-outlined text-[18px] text-primary">psychology</span>
									<span class="text-sm">Total Sesi</span>
								</div>
								<span class="text-lg font-bold text-gray-900">{profile?.totalSessions ?? 0}</span>
							</div>
							<div class="h-px bg-gray-100"></div>
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2 text-gray-500">
									<span class="material-symbols-outlined text-[18px] text-primary">timer</span>
									<span class="text-sm">Menit Berlatih</span>
								</div>
								<span class="text-lg font-bold text-gray-900"
									>{profile?.totalMinutesPracticed ?? 0}</span
								>
							</div>
							<div class="h-px bg-gray-100"></div>
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2 text-gray-500">
									<span class="material-symbols-outlined text-[18px] text-primary">star</span>
									<span class="text-sm">Skor Rata-rata</span>
								</div>
								<span class="text-lg font-bold text-gray-900">
									{profile?.avgOverallScore !== null && profile?.avgOverallScore !== undefined
										? profile.avgOverallScore.toFixed(1)
										: '—'}
								</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Right Column: Career Info + Incomplete Banner -->
				<div class="flex flex-col gap-6 lg:col-span-2">
					<!-- Incomplete Profile Banner -->
					{#if !isProfileComplete}
						<div
							class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary to-[#570000] p-8 text-white shadow-glow"
						>
							<div
								class="absolute top-0 right-0 -mt-12 -mr-12 h-48 w-48 rounded-full bg-white/10 blur-3xl"
							></div>
							<div class="relative z-10">
								<div
									class="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20"
								>
									<span class="material-symbols-outlined text-[24px] text-white">person_add</span>
								</div>
								<h3 class="mb-2 text-xl font-bold">Profil Belum Lengkap</h3>
								<p class="mb-6 max-w-md text-sm leading-relaxed text-red-100">
									Lengkapi preferensi karir kamu agar simulasi wawancara lebih personal dan relevan
									dengan target impianmu.
								</p>
								<a
									href="/onboarding"
									class="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-bold text-primary shadow-md transition-all hover:scale-[1.03] hover:shadow-lg active:scale-[0.98]"
								>
									<span class="material-symbols-outlined text-[18px]">edit</span>
									Lengkapi Profil
								</a>
							</div>
						</div>
					{/if}

					<!-- Career Info Card -->
					<div class="rounded-3xl border border-gray-100 bg-white p-8 shadow-soft">
						<div class="mb-6 flex items-center justify-between">
							<h3 class="text-lg font-bold text-gray-900">Preferensi Karir</h3>
							{#if isProfileComplete}
								<a
									href="/onboarding"
									class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-primary transition-colors hover:bg-red-50"
								>
									<span class="material-symbols-outlined text-[16px]">edit</span>
									Edit
								</a>
							{/if}
						</div>

						{#if isProfileComplete && profile}
							<div class="flex flex-col gap-5">
								<!-- Track -->
								<div class="flex items-start gap-4">
									<div
										class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-primary"
									>
										<span class="material-symbols-outlined text-[20px]">route</span>
									</div>
									<div>
										<p class="text-xs font-semibold tracking-wide text-gray-400 uppercase">
											Jalur Karir
										</p>
										<p class="mt-0.5 text-base font-semibold text-gray-900">
											{trackLabels[profile.preferredTrack!] ?? profile.preferredTrack}
										</p>
									</div>
								</div>

								<div class="h-px bg-gray-100"></div>

								<!-- Institution -->
								<div class="flex items-start gap-4">
									<div
										class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-primary"
									>
										{#if profile.targetInstitution?.logoUrl}
											<img
												src={profile.targetInstitution.logoUrl}
												alt={profile.targetInstitution.name}
												class="h-7 w-7 object-contain"
											/>
										{:else}
											<span class="material-symbols-outlined text-[20px]">domain</span>
										{/if}
									</div>
									<div>
										<p class="text-xs font-semibold tracking-wide text-gray-400 uppercase">
											Target Institusi
										</p>
										<p class="mt-0.5 text-base font-semibold text-gray-900">
											{profile.targetInstitution?.name ?? '—'}
										</p>
									</div>
								</div>

								<div class="h-px bg-gray-100"></div>

								<!-- Position -->
								<div class="flex items-start gap-4">
									<div
										class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-primary"
									>
										<span class="material-symbols-outlined text-[20px]">work</span>
									</div>
									<div>
										<p class="text-xs font-semibold tracking-wide text-gray-400 uppercase">
											Target Posisi
										</p>
										<p class="mt-0.5 text-base font-semibold text-gray-900">
											{profile.targetPosition?.name ?? '—'}
										</p>
										{#if profile.targetPosition?.description}
											<p class="mt-0.5 text-sm text-gray-500">
												{profile.targetPosition.description}
											</p>
										{/if}
									</div>
								</div>
							</div>
						{:else}
							<div class="flex flex-col items-center justify-center py-12 text-center">
								<div
									class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-50 text-gray-300"
								>
									<span class="material-symbols-outlined text-[32px]">info</span>
								</div>
								<p class="text-sm font-medium text-gray-500">Belum ada preferensi karir.</p>
								<p class="mt-1 text-xs text-gray-400">
									Klik "Lengkapi Profil" di atas untuk memulai.
								</p>
							</div>
						{/if}
					</div>

					<!-- Premium Status Card -->
					<div class="rounded-3xl border border-gray-100 bg-white p-8 shadow-soft">
						<div class="flex flex-col justify-between">
							<div class="flex items-center">
								<div
									class="flex h-20 w-14 items-center justify-center rounded-2xl {profile?.isPremium
										? 'bg-amber-50 text-amber-500'
										: 'bg-gray-50 text-gray-400'}"
								>
									<Award />
								</div>
								<div>
									<p class="text-xs font-semibold tracking-wide text-gray-400 uppercase">
										Status Langganan
									</p>
									<p class="mt-0.5 text-base font-semibold text-gray-900">
										{profile?.isPremium ? 'Premium' : 'Gratis'}
									</p>
									{#if profile?.isPremium && profile.premiumExpiresAt}
										<p class="text-xs text-gray-400">
											Berakhir {formatDate(profile.premiumExpiresAt)}
										</p>
									{/if}
								</div>
							</div>
							{#if !profile?.isPremium}
								<div class="flex w-full justify-end">
									<button
										class=" mt-4 w-full rounded-xl bg-linear-to-r from-primary to-primary/90 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:scale-[1.03] hover:shadow-md active:scale-[0.98] md:mt-0 md:w-fit"
									>
										Upgrade
									</button>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</main>

		<BottomNav />
	</div>
</div>

<style>
	:global(.shadow-glow) {
		box-shadow:
			0 4px 32px 0 rgba(128, 0, 0, 0.18),
			0 1.5px 6px 0 rgba(128, 0, 0, 0.1);
	}
	:global(.shadow-soft) {
		box-shadow:
			0 2px 16px 0 rgba(0, 0, 0, 0.06),
			0 1px 4px 0 rgba(0, 0, 0, 0.04);
	}
</style>
