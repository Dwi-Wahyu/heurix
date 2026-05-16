<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import { fade } from 'svelte/transition';
	import { Landmark, Briefcase, ChevronRight, History } from '@lucide/svelte';

	let { data } = $props();
	let sessions = $derived(data.sessions || []);
	let user = $derived(data.user);
</script>

<svelte:head>
	<title>Riwayat Sesi — Heurix</title>
</svelte:head>

<div class="flex min-h-screen bg-[#F8F9FF]">
	<Sidebar />

	<div class="flex min-h-screen flex-1 flex-col md:ml-64">
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-6 pt-24 pb-20">
			<!-- Header Section -->
			<div class="mb-8">
				<h1 class="text-3xl font-extrabold tracking-tight text-gray-900 md:text-4xl">
					Riwayat Latihan
				</h1>
				<p class="mt-2 text-gray-500">Lihat detail dari setiap sesi latihan yang telah kamu selesaikan.</p>
			</div>

			<div class="space-y-4" in:fade>
				{#each sessions as session}
					<a
						href="/session/results?sessionId={session.id}"
						class="group flex flex-col justify-between gap-4 rounded-3xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:border-gray-200 hover:shadow-md md:flex-row md:items-center"
					>
						<div class="flex items-center gap-5">
							<div
								class="h-14 w-14 bg-red-50 flex items-center justify-center rounded-2xl text-primary shadow-sm transition-all duration-300 group-hover:scale-105 group-hover:bg-primary group-hover:text-white"
							>
								{#if session.track === 'military'}
									<Landmark size={28} />
								{:else}
									<Briefcase size={28} />
								{/if}
							</div>
							<div>
								<div class="mb-1.5 flex items-center gap-3">
									<span
										class="px-2.5 py-1 bg-primary/10 text-primary rounded-lg text-[10px] font-black tracking-widest uppercase"
									>
										{session.track === 'military' ? 'Kedinasan' : 'Korporat'}
									</span>
									<span class="text-xs font-bold text-gray-400 uppercase tracking-tight">
										{new Date(session.createdAt).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}
									</span>
								</div>
								<p class="text-lg font-extrabold text-gray-900 leading-tight">Sesi Wawancara #{session.id.slice(0, 8)}</p>
							</div>
						</div>
						<div class="flex items-center justify-between gap-8 md:justify-end">
							<div class="flex flex-col items-end text-right">
								<p class="mb-0.5 text-[10px] font-black tracking-widest text-gray-400 uppercase">
									Skor
								</p>
								<p class="text-3xl font-black text-primary">{Math.round(session.overallScore || 0)}</p>
							</div>
							<div
								class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 transition-colors group-hover:bg-primary/10"
							>
								<ChevronRight size={20} class="text-gray-400 transition-colors group-hover:text-primary" />
							</div>
						</div>
					</a>
				{:else}
					<div class="flex flex-col items-center justify-center py-24 bg-white rounded-4xl border-2 border-dashed border-gray-200" in:fade>
						<div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-50 text-primary">
							<History size={40} />
						</div>
						<h3 class="text-xl font-bold text-gray-900">Belum ada riwayat sesi</h3>
						<p class="mt-2 text-gray-500 font-medium">Selesaikan sesi latihan pertamamu untuk melihat riwayat di sini.</p>
						<a href="/progress" class="mt-8 rounded-full bg-primary px-8 py-3 text-sm font-black text-white shadow-xl transition-all hover:scale-105 active:scale-95">
							Mulai Sesi Pertama
						</a>
					</div>
				{/each}
			</div>
		</main>

		<BottomNav />
	</div>
</div>

<style>
	:global(body) {
		background-color: #F8F9FF;
	}
</style>
