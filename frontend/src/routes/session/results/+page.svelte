<script lang="ts">
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import { sidebarState } from '$lib/sidebar.svelte';
	import {
		BarChart3,
		Calendar,
		Download,
		ThumbsUp,
		TrendingUp,
		Mic2,
		AudioLines,
		Gauge,
		Activity,
		Type,
		CheckSquare,
		RefreshCw,
		Medal,
		Smile,
		Eye
	} from '@lucide/svelte';

	let { data } = $props();
	const { report, sessionTurns, error } = data;

	function getLevel(score: number) {
		if (score >= 80)
			return { label: 'Mahir', class: 'bg-green-100 text-green-800 border-green-200' };
		if (score >= 60)
			return { label: 'Berkembang', class: 'bg-blue-100 text-blue-800 border-blue-200' };
		return { label: 'Perlu Latihan', class: 'bg-orange-100 text-orange-800 border-orange-200' };
	}

	const dimensions = report
		? [
				{
					label: 'Tutur Kata',
					score: Math.round(report.articulationScore || report.communicationScore),
					feedback: report.articulationFeedback || 'Artikulasi jelas dan mudah dipahami.',
					icon: Mic2,
					level: getLevel(report.articulationScore || report.communicationScore)
				},
				{
					label: 'Intonasi',
					score: Math.round(report.intonationScore || report.overallScore),
					feedback: report.intonationFeedback || 'Intonasi cukup dinamis dan ekspresif.',
					icon: AudioLines,
					level: getLevel(report.intonationScore || report.overallScore)
				},
				{
					label: 'Kecepatan Bicara',
					score: Math.round(report.pacingScore || 80),
					feedback: report.pacingFeedback || 'Kecepatan ideal, terdengar tenang.',
					icon: Gauge,
					level: getLevel(report.pacingScore || 80)
				},
				{
					label: 'Filler Words',
					score: Math.round(report.fillerWordsScore || 100 - report.totalFillerWords * 2),
					feedback:
						report.fillerWordsFeedback ||
						`Kamu menggunakan filler words sebanyak ${report.totalFillerWords} kali.`,
					icon: Activity,
					level: getLevel(report.fillerWordsScore || 100 - report.totalFillerWords * 2)
				},
				{
					label: 'Pemilihan Kalimat',
					score: Math.round(report.sentenceStructureScore || report.communicationScore),
					feedback: report.sentenceStructureFeedback || 'Struktur kalimat baik dan profesional.',
					icon: Type,
					level: getLevel(report.sentenceStructureScore || report.communicationScore)
				},
				{
					label: 'Kelengkapan Jawaban',
					score: Math.round(report.answerCompletenessScore || report.overallScore),
					feedback:
						report.answerCompletenessFeedback ||
						'Menjawab pertanyaan dengan poin-poin yang relevan.',
					icon: CheckSquare,
					level: getLevel(report.answerCompletenessScore || report.overallScore)
				},
				{
					label: 'Konsistensi',
					score: Math.round(report.consistencyScore),
					feedback: report.consistencyFeedback || 'Argumen awal dan akhir konsisten.',
					icon: RefreshCw,
					level: getLevel(report.consistencyScore)
				},
				{
					label: 'Kepercayaan Diri',
					score: Math.round(report.confidenceScore),
					feedback: report.confidenceFeedback || 'Nada suara mantap dan meyakinkan.',
					icon: Medal,
					level: getLevel(report.confidenceScore)
				},
				{
					label: 'Raut Wajah',
					score: Math.round(report.facialExpressionScore || 75),
					feedback:
						report.facialExpressionFeedback ||
						'Ekspresi wajah Anda terlihat tenang dan profesional.',
					icon: Smile,
					level: getLevel(report.facialExpressionScore || 75)
				},
				{
					label: 'Kontak Mata',
					score: Math.round(report.eyeContactScore || 80),
					feedback: report.eyeContactFeedback || 'Kontak mata Anda cukup konsisten selama sesi.',
					icon: Eye,
					level: getLevel(report.eyeContactScore || 80)
				}
			]
		: [];

	function parseAnalysis(analysis: string) {
		try {
			return JSON.parse(analysis);
		} catch (e) {
			return { strength: analysis, improvement: '' };
		}
	}

	function handleDownload() {
		window.print();
	}
</script>

<div class="flex min-h-screen bg-[#f8f9ff]">
	<div class="no-print">
		<Sidebar />
	</div>

	<div
		class="flex min-h-screen flex-1 flex-col transition-all duration-300 print:m-0 print:bg-white {sidebarState.isOpen
			? 'md:ml-64'
			: 'md:ml-20'}"
	>
		<div class="no-print">
			<Header />
		</div>

		<main class="mx-auto w-full max-w-6xl px-4 pt-24 pb-32 md:px-8 print:max-w-none print:p-0">
			{#if error}
				<div class="no-print flex h-[60vh] flex-col items-center justify-center text-center">
					<BarChart3 size={64} class="mb-4 text-gray-300" />
					<h1 class="text-2xl font-bold text-gray-900">Laporan belum tersedia</h1>
					<p class="mt-2 text-gray-500">
						AI kami sedang menyusun laporan evaluasi Anda. Mohon tunggu sebentar.
					</p>
					<button
						onclick={() => window.location.reload()}
						class="mt-6 rounded-xl bg-primary px-6 py-3 font-bold text-white shadow-lg"
					>
						Refresh Halaman
					</button>
				</div>
			{:else if report}
				<!-- Header Section -->
				<section class="mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-end">
					<div>
						<h1
							class="font-plus-jakarta text-4xl font-bold tracking-tight text-gray-900 md:text-[40px]"
						>
							Simulasi Selesai
						</h1>
						<div class="mt-2 flex items-center gap-2 font-medium text-gray-500">
							<Calendar size={18} />
							<span
								>{new Date(report.generatedAt).toLocaleDateString('id-ID', {
									weekday: 'long',
									day: 'numeric',
									month: 'long',
									year: 'numeric'
								})}</span
							>
						</div>
					</div>
					<div class="no-print flex gap-3">
						<button
							onclick={handleDownload}
							class="flex items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-bold text-white shadow-lg transition-all hover:bg-red-900"
						>
							<Download size={20} />
							Unduh PDF
						</button>
					</div>
				</section>

				<!-- Overall Score Row -->
				<div class="mb-10 grid grid-cols-1 gap-6 lg:grid-cols-12">
					<div
						class="flex flex-col items-center justify-center rounded-3xl border border-gray-100 bg-white p-8 text-center shadow-sm lg:col-span-4 print:border-gray-300"
					>
						<h2 class="mb-6 text-sm font-bold tracking-widest text-gray-400 uppercase">
							Skor Keseluruhan
						</h2>
						<div class="relative flex h-40 w-40 items-center justify-center">
							<svg class="h-full w-full" viewBox="0 0 100 100">
								<circle cx="50" cy="50" r="45" fill="none" stroke="#f3f4f6" stroke-width="8" />
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
								<span class="text-[52px] leading-none font-bold text-primary"
									>{Math.round(report.overallScore)}</span
								>
								<span class="text-xs font-bold text-gray-400 uppercase">Excellent</span>
							</div>
						</div>
						<div class="mt-8 grid w-full grid-cols-2 gap-4">
							<div
								class="rounded-2xl bg-gray-50 p-3 print:border print:border-gray-200 print:bg-white"
							>
								<p class="mb-1 text-[10px] font-bold text-gray-400 uppercase">Pertanyaan</p>
								<p class="text-lg font-bold text-gray-900">{report.totalTurns}</p>
							</div>
							<div
								class="rounded-2xl bg-gray-50 p-3 print:border print:border-gray-200 print:bg-white"
							>
								<p class="mb-1 text-[10px] font-bold text-gray-400 uppercase">Filler Words</p>
								<p class="text-lg font-bold text-gray-900">{report.totalFillerWords}</p>
							</div>
						</div>
					</div>

					<div
						class="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm lg:col-span-8 print:border-gray-300"
					>
						<h2 class="mb-6 text-xl font-bold text-gray-900">Analisis Mendalam</h2>
						<p class="mb-8 leading-relaxed whitespace-pre-wrap text-gray-600">
							{report.evaluationNarrative || 'Laporan evaluasi sedang diproses.'}
						</p>
						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							<div class="rounded-2xl border border-green-100 bg-green-50/50 p-5 print:bg-white">
								<h4 class="mb-3 flex items-center gap-2 text-sm font-bold text-green-800">
									<ThumbsUp size={18} /> Kelebihan
								</h4>
								<ul class="space-y-2">
									{#each report.strengths || [] as s}
										<li class="flex items-start gap-2 text-sm text-green-700">
											<span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-green-500"></span>
											{s}
										</li>
									{/each}
								</ul>
							</div>
							<div class="rounded-2xl border border-red-100 bg-red-50/50 p-5 print:bg-white">
								<h4 class="mb-3 flex items-center gap-2 text-sm font-bold text-red-800">
									<TrendingUp size={18} /> Pengembangan
								</h4>
								<ul class="space-y-2">
									{#each report.weaknesses || [] as w}
										<li class="flex items-start gap-2 text-sm text-red-700">
											<span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
											{w}
										</li>
									{/each}
								</ul>
							</div>
						</div>
					</div>
				</div>

				<!-- 8 Dimensions Grid -->
				<section class="mb-16 print:break-before-page">
					<h2 class="mb-8 text-2xl font-bold text-gray-900">8 Dimensi Komunikasi</h2>
					<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 print:grid-cols-2">
						{#each dimensions as dim}
							<div
								class="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:shadow-md print:border-gray-300"
							>
								<div class="flex items-start justify-between">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary"
									>
										<dim.icon size={22} />
									</div>
									<span
										class="rounded-full border px-3 py-1 text-[10px] font-bold tracking-wider uppercase {dim
											.level.class}"
									>
										{dim.level.label}
									</span>
								</div>
								<div>
									<h3 class="mb-1 text-base font-bold text-gray-900">{dim.label}</h3>
									<p class="text-xs leading-relaxed text-gray-500">{dim.feedback}</p>
								</div>
								<div class="mt-auto pt-2">
									<div class="mb-1 flex items-center justify-between">
										<span class="text-[10px] font-bold text-gray-400 uppercase">Score</span>
										<span class="text-xs font-bold text-primary">{dim.score}%</span>
									</div>
									<div class="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
										<div
											class="h-full bg-primary transition-all duration-1000"
											style="width: {dim.score}%"
										></div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</section>

				<div class="grid grid-cols-1 gap-10 lg:grid-cols-3">
					<!-- Detailed Turn-by-turn Analysis -->
					<section class="lg:col-span-2 print:col-span-3">
						<h2 class="mb-8 text-2xl font-bold text-gray-900">Analisis per Pertanyaan</h2>
						<div class="space-y-6">
							{#each sessionTurns as turn}
								{@const analysis = parseAnalysis(turn.llmAnalysis)}
								<div
									class="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm print:break-inside-avoid print:border-gray-300"
								>
									<div class="flex items-start gap-4">
										<div
											class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-sm font-bold text-gray-700"
										>
											{turn.turnNumber}
										</div>
										<div class="flex-1">
											<h3 class="mb-4 text-base leading-snug font-bold text-gray-900">
												{turn.questionText}
											</h3>
											<div
												class="mb-6 rounded-2xl border border-gray-50 bg-gray-50/50 p-4 text-sm leading-relaxed text-gray-600 italic print:border-gray-200 print:bg-white"
											>
												"{turn.answerTranscript || 'Kandidat tidak menjawab.'}"
											</div>
											<div class="space-y-3">
												{#if analysis.strength}
													<div class="flex items-start gap-3">
														<span class="mt-0.5 font-bold text-green-600">✓</span>
														<p class="text-sm text-gray-700">{analysis.strength}</p>
													</div>
												{/if}
												{#if analysis.improvement}
													<div class="flex items-start gap-3">
														<span class="mt-0.5 font-bold text-orange-500">△</span>
														<p class="text-sm text-gray-700">{analysis.improvement}</p>
													</div>
												{/if}
											</div>
										</div>
									</div>
								</div>
							{:else}
								<p class="text-gray-500 italic">Belum ada detail pertanyaan.</p>
							{/each}
						</div>
					</section>

					<!-- Filler Words Summary -->
					<section class="print:mt-8 print:break-before-page">
						<div
							class="sticky top-24 rounded-3xl border border-gray-100 bg-white p-8 shadow-sm print:static print:max-w-none print:border-gray-300"
						>
							<h2 class="mb-8 text-xl font-bold text-gray-900">Ringkasan Filler Words</h2>
							<div class="space-y-6">
								{#if report.fillerWordBreakdown && Object.keys(report.fillerWordBreakdown).length > 0}
									{#each Object.entries(report.fillerWordBreakdown) as [word, count]}
										{@const percentage = Math.min((count / report.totalFillerWords) * 100, 100)}
										<div>
											<div class="mb-2 flex items-end justify-between">
												<span class="text-sm font-bold text-gray-700">"{word}"</span>
												<span class="text-xs font-bold text-gray-500">{count} kali</span>
											</div>
											<div class="h-2 w-full overflow-hidden rounded-full bg-gray-50">
												<div
													class="h-full rounded-full bg-orange-400 transition-all duration-1000"
													style="width: {percentage}%"
												></div>
											</div>
										</div>
									{/each}
								{:else}
									<p class="text-sm text-gray-400 italic">
										Tidak ada kata pengisi yang terdeteksi. Bagus!
									</p>
								{/if}
							</div>

							<div
								class="mt-10 rounded-2xl border border-blue-100 bg-blue-50/30 p-5 print:bg-white"
							>
								<p class="text-sm leading-relaxed text-gray-700">
									<strong class="text-blue-800">Saran Pelatih:</strong> Penggunaan filler words yang terlalu
									sering dapat mengurangi kesan otoritas. Cobalah untuk mengambil jeda diam sejenak saat
									berpikir alih-alih menggunakan "ee".
								</p>
							</div>

							<div class="no-print mt-10 flex flex-col gap-3">
								<button
									onclick={() => goto('/dashboard')}
									class="w-full rounded-2xl border border-gray-200 py-3.5 text-sm font-bold text-gray-700 transition-all hover:bg-gray-50"
								>
									Kembali ke Dashboard
								</button>
								<button
									onclick={() => goto('/session/select-avatar')}
									class="w-full rounded-2xl bg-primary py-3.5 text-sm font-bold text-white shadow-lg shadow-red-900/10 transition-all hover:bg-red-900"
								>
									Latihan Lagi
								</button>
							</div>
						</div>
					</section>
				</div>
			{/if}
		</main>

		<div class="no-print">
			<BottomNav />
		</div>
	</div>
</div>

<style>
	:global(body) {
		font-family: 'Plus Jakarta Sans', sans-serif;
	}

	@media print {
		.no-print {
			display: none !important;
		}
		:global(body) {
			background-color: white !important;
			color: black !important;
		}
		.print\:m-0 {
			margin: 0 !important;
		}
		.print\:bg-white {
			background-color: white !important;
		}
		.print\:p-0 {
			padding: 0 !important;
		}
		.print\:max-w-none {
			max-w: none !important;
		}
		.print\:border-gray-300 {
			border-color: #d1d5db !important;
		}
		.print\:grid-cols-2 {
			grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
		}
		.print\:col-span-3 {
			grid-column: span 3 / span 3 !important;
		}
		.print\:static {
			position: static !important;
		}
		.print\:break-before-page {
			break-before: page !important;
		}
		.print\:break-inside-avoid {
			break-inside: avoid !important;
		}
		.print\:mt-8 {
			margin-top: 2rem !important;
		}
	}
</style>
