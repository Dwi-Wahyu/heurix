<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import { sidebarState } from '$lib/sidebar.svelte';
	import { CheckCircle, Mic, Briefcase, Landmark, ChevronRight, History } from '@lucide/svelte';

	let { data } = $props();
	const { user, profile, recentSessions } = data;
</script>

<div class="flex min-h-screen bg-[#f4f7fb]">
	<Sidebar />

	<div
		class="flex min-h-screen flex-1 flex-col transition-all duration-300 {sidebarState.isOpen
			? 'md:ml-64'
			: 'md:ml-20'}"
	>
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-5 pt-20 pb-20 md:px-8">
			<!-- Greeting Section -->
			<section class="mb-10">
				<h1 class="mb-2 text-4xl font-bold tracking-tight text-gray-900 md:text-[40px]">
					Selamat pagi, {user?.name || 'Andi'}!
				</h1>
				<p class="text-lg text-gray-500">Siap untuk mempertajam kemampuan wawancaramu hari ini?</p>
			</section>

			<!-- Bento Grid Layout -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-12">
				<!-- Performance Card -->
				<div
					class="group relative flex flex-col justify-between overflow-hidden rounded-3xl border border-gray-100 bg-white p-8 shadow-soft md:col-span-5"
				>
					<div
						class="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-red-50 opacity-50 blur-3xl transition-opacity group-hover:opacity-70"
					></div>
					<div class="relative z-10">
						<h2 class="mb-6 text-xl font-bold text-gray-900">Performa Anda</h2>
						<div class="mb-8 flex w-fit items-center gap-2 rounded-full bg-red-50 px-3 py-1.5">
							<CheckCircle size={18} class="text-primary" />
							<p class="text-sm font-semibold text-primary">
								{profile?.totalSessions || 0} Sesi Selesai
							</p>
						</div>
						<div class="mt-auto flex items-end justify-between">
							<div>
								<p class="mb-1 text-xs font-bold tracking-widest text-gray-400 uppercase">
									Skor Rata-rata
								</p>
								<div class="flex items-baseline gap-1">
									<p class="text-[56px] leading-none font-bold tracking-tight text-primary">
										{Math.round(profile?.avgOverallScore || 0)}
									</p>
									<p class="text-xl font-medium text-gray-400">/100</p>
								</div>
							</div>
							<div class="flex h-20 w-32 items-end gap-1.5 pb-1">
								<!-- Modern Bar Chart -->
								<div
									class="h-[30%] w-full rounded-t-sm bg-red-100/50 transition-colors hover:bg-red-200"
								></div>
								<div
									class="h-[45%] w-full rounded-t-sm bg-red-100/70 transition-colors hover:bg-red-200"
								></div>
								<div
									class="h-[60%] w-full rounded-t-sm bg-red-200/80 transition-colors hover:bg-red-300"
								></div>
								<div
									class="h-[75%] w-full rounded-t-sm bg-red-400/90 transition-colors hover:bg-red-500"
								></div>
								<div
									class="h-[100%] w-full rounded-t-sm bg-primary shadow-[0_0_10px_rgba(128,0,0,0.3)]"
								></div>
								<div
									class="h-[85%] w-full rounded-t-sm bg-red-500 transition-colors hover:bg-red-400"
								></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main CTA Section -->
				<div
					class="relative flex min-h-[300px] flex-col justify-center overflow-hidden rounded-3xl bg-gradient-to-br from-[#800000] to-[#570000] p-8 text-left shadow-glow md:col-span-7 md:p-10"
				>
					<!-- Decorative elements -->
					<div
						class="absolute top-0 right-0 -mt-20 -mr-20 h-64 w-64 rounded-full bg-white/10 mix-blend-overlay blur-3xl"
					></div>
					<div
						class="absolute bottom-0 left-0 -mb-10 -ml-10 h-40 w-40 rounded-full bg-red-400/20 mix-blend-overlay blur-2xl"
					></div>

					<div class="relative z-10 w-full md:w-4/5">
						<h3 class="mb-4 text-3xl leading-tight font-bold text-white md:text-[32px]">
							Tingkatkan kariermu dengan simulasi AI.
						</h3>
						<p class="mb-8 max-w-md text-lg font-medium text-red-100">
							Dapatkan feedback instan dan tingkatkan kepercayaan diri Anda sebelum wawancancara
							sesungguhnya.
						</p>
						<a
							href="/session/select-avatar"
							class="group flex w-full items-center justify-center gap-3 rounded-2xl bg-white px-8 py-4 text-lg font-bold text-primary shadow-lg transition-all hover:scale-[1.02] hover:shadow-xl active:scale-[0.98] md:w-auto"
						>
							<Mic size={22} class="transition-transform group-hover:rotate-12" />
							Mulai Sesi Wawancara
						</a>
					</div>
				</div>

				<!-- History Section -->
				<div class="mt-10 md:col-span-12">
					<div class="mb-6 flex items-center justify-between px-1">
						<h2 class="text-2xl font-bold text-gray-900">Riwayat Latihan</h2>
						<a
							href="/history"
							class="text-sm font-semibold text-primary transition-colors hover:text-red-700"
							>Lihat Semua</a
						>
					</div>
					<div class="space-y-4">
						{#each recentSessions as session}
							<a
								href="/session/results?sessionId={session.id}"
								class="group flex cursor-pointer flex-col justify-between gap-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-soft transition-all hover:border-gray-200 hover:shadow-md md:flex-row md:items-center"
							>
								<div class="flex items-center gap-5">
									<div
										class="flex h-14 w-14 items-center justify-center rounded-xl bg-red-50 text-primary shadow-sm transition-all duration-300 group-hover:scale-105 group-hover:bg-primary group-hover:text-white"
									>
										{#if session.track === 'military'}
											<Landmark size={26} />
										{:else}
											<Briefcase size={26} />
										{/if}
									</div>
									<div>
										<div class="mb-1.5 flex items-center gap-3">
											<span
												class="rounded-md bg-red-50 px-2.5 py-1 text-xs font-semibold tracking-wide text-red-700"
											>
												{new Date(session.createdAt).toLocaleDateString('id-ID', {
													day: '2-digit',
													month: 'short',
													year: 'numeric'
												})}
											</span>
										</div>
										<p class="text-base font-bold text-gray-900">
											Sesi Wawancara #{session.id.slice(0, 8)}
										</p>
									</div>
								</div>
								<div class="mt-2 flex items-center justify-between gap-8 md:mt-0 md:justify-end">
									<div class="flex flex-col items-end text-right">
										<p class="mb-0.5 text-[10px] font-bold tracking-widest text-gray-400 uppercase">
											Skor
										</p>
										<p class="text-2xl font-extrabold text-secondary">
											{Math.round(session.overallScore || 0)}
										</p>
									</div>
									<div
										class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-50 transition-colors group-hover:bg-red-50"
									>
										<ChevronRight
											size={18}
											class="text-gray-400 transition-colors group-hover:text-primary"
										/>
									</div>
								</div>
							</a>
						{:else}
							<div
								class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-gray-200"
							>
								<History size={48} class="text-gray-300 mb-4" />
								<p class="text-gray-500 font-medium">Belum ada riwayat sesi.</p>
								<a href="/session/select-avatar" class="mt-4 text-primary font-bold"
									>Mulai sesi pertama Anda</a
								>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</main>

		<BottomNav />
	</div>
</div>
