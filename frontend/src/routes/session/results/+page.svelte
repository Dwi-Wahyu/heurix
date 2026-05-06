<script lang="ts">
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';

	let { data } = $props();
	const { report, sessionTurns, error } = data;

	const dimensions = report
		? [
				{
					label: 'Komunikasi',
					score: Math.round(report.communicationScore),
					icon: 'chat_bubble',
					color: 'blue'
				},
				{
					label: 'Konsistensi',
					score: Math.round(report.consistencyScore),
					icon: 'verified',
					color: 'green'
				},
				{
					label: 'Kepercayaan Diri',
					score: Math.round(report.confidenceScore),
					icon: 'psychology',
					color: 'purple'
				},
				{
					label: 'Ketahanan Stres',
					score: Math.round(report.stressResistanceScore || 0),
					icon: 'bolt',
					color: 'orange'
				}
			]
		: [];
</script>

<div class="flex min-h-screen bg-[#f4f7fb]">
	<Sidebar />

	<div class="flex min-h-screen flex-1 flex-col md:ml-64">
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-5 pt-20 pb-20 md:px-8">
			{#if error}
				<div class="flex h-[60vh] flex-col items-center justify-center text-center">
					<span class="material-symbols-outlined text-[64px] text-gray-300 mb-4">analytics</span>
					<h1 class="text-2xl font-bold text-gray-900">Laporan belum tersedia</h1>
					<p class="text-gray-500 mt-2">AI kami sedang menyusun laporan evaluasi Anda. Mohon tunggu sebentar.</p>
					<button onclick={() => window.location.reload()} class="mt-6 rounded-xl bg-primary px-6 py-3 font-bold text-white shadow-lg">
						Refresh Halaman
					</button>
				</div>
			{:else if report}
				<!-- Header Section -->
				<section class="mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-end">
					<div>
						<div class="mb-3 flex items-center gap-2">
							<a href="/dashboard" class="text-sm font-semibold text-primary">Dashboard</a>
							<span class="material-symbols-outlined text-[16px] text-gray-400">chevron_right</span>
							<span class="text-sm font-medium text-gray-400">Hasil Sesi</span>
						</div>
						<h1 class="text-4xl font-bold tracking-tight text-gray-900 md:text-[40px]">
							Evaluasi Wawancara
						</h1>
						<p class="mt-2 text-lg text-gray-500">Analisis mendalam performa Anda oleh HireReady AI.</p>
					</div>
					<div class="flex gap-3">
						<button
							class="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-5 py-3 text-sm font-bold text-gray-700 shadow-sm transition-all hover:bg-gray-50"
						>
							<span class="material-symbols-outlined text-[20px]">share</span>
							Bagikan
						</button>
						<button
							class="flex items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-bold text-white shadow-lg transition-all hover:bg-red-800"
						>
							<span class="material-symbols-outlined text-[20px]">download</span>
							Unduh PDF
						</button>
					</div>
				</section>

				<div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
					<!-- Overall Score Card -->
					<div
						class="relative overflow-hidden rounded-3xl border border-gray-100 bg-white p-8 shadow-soft lg:col-span-4"
					>
						<div
							class="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-red-50 opacity-50 blur-3xl"
						></div>
						<div class="relative z-10 flex h-full flex-col">
							<h2 class="mb-1 text-sm font-bold tracking-widest text-gray-400 uppercase">
								Skor Keseluruhan
							</h2>
							<div class="my-8 flex items-center justify-center">
								<div class="relative flex h-40 w-40 items-center justify-center">
									<svg class="h-full w-full" viewBox="0 0 100 100">
										<circle
											cx="50"
											cy="50"
											r="45"
											fill="none"
											stroke="#f3f4f6"
											stroke-width="8"
										/>
										<circle
											cx="50"
											cy="50"
											r="45"
											fill="none"
											stroke="#800000"
											stroke-width="8"
											stroke-dasharray="282.7"
											stroke-dashoffset={282.7 - (282.7 * report.overallScore) / 100}
											stroke-linecap="round"
											class="transition-all duration-1000 ease-out"
										/>
									</svg>
									<div class="absolute inset-0 flex flex-col items-center justify-center">
										<span class="text-[52px] leading-none font-bold text-primary">
											{Math.round(report.overallScore)}
										</span>
										<span class="text-xs font-bold text-gray-400 uppercase">Excellent</span>
									</div>
								</div>
							</div>
							<div class="mt-auto space-y-3">
								<div class="flex items-center justify-between rounded-xl bg-gray-50 p-3">
									<span class="text-sm font-medium text-gray-500">Jumlah Pertanyaan</span>
									<span class="text-sm font-bold text-gray-900">{report.totalTurns}</span>
								</div>
								<div class="flex items-center justify-between rounded-xl bg-gray-50 p-3">
									<span class="text-sm font-medium text-gray-500">Filler Words</span>
									<span class="text-sm font-bold text-gray-900">{report.totalFillerWords}</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Dimension Scores Grid -->
					<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:col-span-8">
						{#each dimensions as dim}
							<div class="rounded-3xl border border-gray-100 bg-white p-6 shadow-soft">
								<div class="mb-4 flex items-center justify-between">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-50 text-primary"
									>
										<span class="material-symbols-outlined text-[22px]">{dim.icon}</span>
									</div>
									<span class="text-xl font-bold text-gray-900">{dim.score}%</span>
								</div>
								<h3 class="mb-3 text-base font-bold text-gray-900">{dim.label}</h3>
								<div class="h-2 w-full overflow-hidden rounded-full bg-gray-100">
									<div
										class="h-full bg-primary transition-all duration-1000"
										style="width: {dim.score}%"
									></div>
								</div>
							</div>
						{/each}

						<!-- Communication Insights Card -->
						<div class="rounded-3xl border border-gray-100 bg-white p-6 shadow-soft sm:col-span-2">
							<h3 class="mb-5 text-base font-bold text-gray-900">Analisis Kata Pengisi (Fillers)</h3>
							<div class="flex flex-wrap gap-3">
								{#if report.fillerWordBreakdown && Object.keys(report.fillerWordBreakdown).length > 0}
									{#each Object.entries(report.fillerWordBreakdown) as [word, count]}
										<div class="flex items-center gap-2 rounded-2xl bg-gray-50 px-4 py-2 border border-gray-100">
											<span class="text-sm font-medium text-gray-600">"{word}"</span>
											<span class="h-5 w-px bg-gray-200"></span>
											<span class="text-sm font-bold text-primary">{count}x</span>
										</div>
									{/each}
								{:else}
									<p class="text-sm text-gray-400 italic">Tidak ada kata pengisi yang terdeteksi. Bagus!</p>
								{/if}
							</div>
						</div>
					</div>

					<!-- Evaluation Narrative Section -->
					<section class="lg:col-span-12">
						<div class="mb-6 rounded-3xl border border-gray-100 bg-white p-8 shadow-soft">
							<h2 class="mb-6 text-2xl font-bold text-gray-900">Analisis Mendalam</h2>
							<div class="prose prose-sm max-w-none text-gray-600 leading-relaxed whitespace-pre-wrap">
								{report.evaluationNarrative || 'Belum ada evaluasi naratif.'}
							</div>

							<div class="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
								<div class="rounded-2xl bg-green-50 p-6 border border-green-100">
									<h4 class="mb-4 flex items-center gap-2 font-bold text-green-800">
										<span class="material-symbols-outlined">thumb_up</span>
										Kelebihan Anda
									</h4>
									<ul class="space-y-2">
										{#each report.strengths || [] as strength}
											<li class="flex items-start gap-2 text-sm text-green-700">
												<span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-green-500"></span>
												{strength}
											</li>
										{/each}
									</ul>
								</div>
								<div class="rounded-2xl bg-red-50 p-6 border border-red-100">
									<h4 class="mb-4 flex items-center gap-2 font-bold text-red-800">
										<span class="material-symbols-outlined">trending_up</span>
										Area Pengembangan
									</h4>
									<ul class="space-y-2">
										{#each report.weaknesses || [] as weakness}
											<li class="flex items-start gap-2 text-sm text-red-700">
												<span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
												{weakness}
											</li>
										{/each}
									</ul>
								</div>
							</div>
						</div>
					</section>

					<!-- Detailed Turn-by-turn Analysis -->
					<section class="lg:col-span-12">
						<h2 class="mb-6 text-2xl font-bold text-gray-900">Detail Tanya Jawab</h2>
						<div class="space-y-6">
							{#each sessionTurns as turn}
								<div class="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-soft">
									<div class="flex items-center justify-between border-b border-gray-50 bg-gray-50/50 px-6 py-4">
										<span class="text-xs font-bold tracking-widest text-gray-400 uppercase"
											>Pertanyaan {turn.turnNumber}</span
										>
										<div class="flex items-center gap-2">
											<span class="text-xs font-bold text-gray-400 uppercase">Kualitas Jawaban</span>
											<span class="rounded-lg bg-white px-2 py-1 text-sm font-bold text-primary shadow-sm border border-gray-100"
												>{Math.round(turn.answerQuality || 0)}/100</span
											>
										</div>
									</div>
									<div class="p-6">
										<div class="mb-6">
											<p class="mb-2 text-xs font-bold text-primary uppercase tracking-wide">Pewawancara</p>
											<p class="text-base font-semibold text-gray-900">
												{turn.questionText}
											</p>
										</div>
										<div class="mb-6 rounded-2xl bg-gray-50 p-5 border border-gray-100">
											<p class="mb-2 text-xs font-bold text-gray-400 uppercase tracking-wide">Jawaban Anda</p>
											<p class="text-sm leading-relaxed text-gray-700">
												{turn.answerTranscript || 'Tidak ada transkrip jawaban.'}
											</p>
										</div>
										{#if turn.llmAnalysis}
											<div class="flex items-start gap-3 rounded-2xl bg-blue-50/50 p-5 border border-blue-100/50">
												<span class="material-symbols-outlined text-blue-600 mt-0.5">info</span>
												<div>
													<p class="mb-1 text-xs font-bold text-blue-800 uppercase tracking-wide">Analisis AI</p>
													<p class="text-sm text-blue-800/80 leading-relaxed">
														{turn.llmAnalysis}
													</p>
												</div>
											</div>
										{/if}
									</div>
								</div>
							{:else}
								<p class="text-gray-500 italic">Belum ada detail pertanyaan.</p>
							{/each}
						</div>
					</section>
				</div>
			{/if}
		</main>

		<BottomNav />
	</div>
</div>

<style>
	.fill-1 {
		font-variation-settings: 'FILL' 1;
	}
</style>
