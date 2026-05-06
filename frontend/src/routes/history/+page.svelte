<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';

	let { data } = $props();
	const { sessions } = data;
</script>

<div class="flex min-h-screen bg-[#f4f7fb]">
	<Sidebar />

	<div class="flex min-h-screen flex-1 flex-col md:ml-64">
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-5 pt-20 pb-20 md:px-8">
			<section class="mb-10">
				<h1 class="text-4xl font-bold tracking-tight text-gray-900 md:text-[40px]">
					Riwayat Latihan
				</h1>
				<p class="mt-2 text-lg text-gray-500">Pantau perkembangan performa wawancaramu dari waktu ke waktu.</p>
			</section>

			<div class="space-y-4">
				{#each sessions as session}
					<a
						href="/session/results?sessionId={session.id}"
						class="group flex cursor-pointer flex-col justify-between gap-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-soft transition-all hover:border-gray-200 hover:shadow-md md:flex-row md:items-center"
					>
						<div class="flex items-center gap-5">
							<div
								class="h-14 w-14 bg-red-50 flex items-center justify-center rounded-xl text-primary shadow-sm transition-all duration-300 group-hover:scale-105 group-hover:bg-primary group-hover:text-white"
							>
								<span class="material-symbols-outlined text-[26px]">
									{session.track === 'military' ? 'account_balance' : 'business_center'}
								</span>
							</div>
							<div>
								<div class="mb-1.5 flex items-center gap-3">
									<span
										class="px-2.5 py-1 bg-red-50 text-red-700 rounded-md text-xs font-semibold tracking-wide"
									>
										{session.track.toUpperCase()}
									</span>
									<span class="text-xs font-medium text-gray-400">
										{new Date(session.createdAt).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}
									</span>
								</div>
								<p class="text-base font-bold text-gray-900">Sesi Wawancara #{session.id.slice(0, 8)}</p>
							</div>
						</div>
						<div class="mt-2 flex items-center justify-between gap-8 md:mt-0 md:justify-end">
							<div class="flex flex-col items-end text-right">
								<p class="mb-0.5 text-[10px] font-bold tracking-widest text-gray-400 uppercase">
									Skor
								</p>
								<p class="text-2xl font-extrabold text-secondary">{Math.round(session.overallScore || 0)}</p>
							</div>
							<div
								class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-50 transition-colors group-hover:bg-red-50"
							>
								<span
									class="material-symbols-outlined text-[18px] text-gray-400 transition-colors group-hover:text-primary"
									>arrow_forward_ios</span
								>
							</div>
						</div>
					</a>
				{:else}
					<div class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-gray-200">
						<span class="material-symbols-outlined text-[48px] text-gray-300 mb-4">history</span>
						<p class="text-gray-500 font-medium">Belum ada riwayat sesi.</p>
						<a href="/session/disclaimer" class="mt-4 text-primary font-bold">Mulai sesi pertama Anda</a>
					</div>
				{/each}
			</div>
		</main>

		<BottomNav />
	</div>
</div>

<style>
	.fill-1 {
		font-variation-settings: 'FILL' 1;
	}
</style>
