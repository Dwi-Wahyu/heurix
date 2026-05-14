<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import { fade } from 'svelte/transition';

	// Chart.js
	import { Line } from 'svelte-chartjs';
	import {
		Chart as ChartJS,
		Title,
		Tooltip,
		Legend,
		LineElement,
		LinearScale,
		PointElement,
		CategoryScale,
		Filler
	} from 'chart.js';

	ChartJS.register(
		Title,
		Tooltip,
		Legend,
		LineElement,
		LinearScale,
		PointElement,
		CategoryScale,
		Filler
	);

	let { data } = $props();
	let sessions = $derived(data.sessions || []);
	let user = $derived(data.user);
	let profile = $derived(data.profile);

	// Dimension Picker for Progress
	let selectedDimension = $state('Filler Words');
	const dimensions = [
		'Filler Words', 'Tutur Kata', 'Intonasi', 'Kecepatan Bicara',
		'Pemilihan Kalimat', 'Kelengkapan Jawaban', 'Konsistensi', 'Kepercayaan Diri',
		'Raut Wajah', 'Kontak Mata'
	];

	// ── DATA AGGREGATION ──
	const getDimensionScores = (sessionList: any[]) => {
		if (sessionList.length === 0) return Array(10).fill(0);
		
		const sum = (field: string) => sessionList.reduce((acc, s) => acc + (s[field] || 0), 0) / sessionList.length;
		
		return [
			Math.round(sum('communicationScore')), // Tutur Kata
			Math.round(sum('communicationScore') * 0.95), // Intonasi (Derived)
			Math.min(100, Math.round((sum('avgWordsPerMinute') || 130) / 1.6)), // Kecepatan Bicara (Normalized)
			Math.max(0, 100 - (sum('totalFillerWords') || 0) * 5), // Filler Words (Penalty based)
			Math.round(sum('communicationScore') * 1.05), // Pemilihan Kalimat (Derived)
			Math.round(sum('overallScore') * 0.9), // Kelengkapan Jawaban (Derived)
			Math.round(sum('consistencyScore')), // Konsistensi
			Math.round(sum('confidenceScore')), // Kepercayaan Diri
			Math.round(sum('facialExpressionScore') || 75), // Raut Wajah
			Math.round(sum('eyeContactScore') || 80) // Kontak Mata
		];
	};

	let avgDimScores = $derived(getDimensionScores(sessions));
	
	const dimensionDataMap = $derived(dimensions.reduce((acc, dim, i) => {
		acc[dim] = avgDimScores[i];
		return acc;
	}, {} as Record<string, number>));

	const getLevel = (score: number) => {
		if (score >= 80) return 'Mahir';
		if (score >= 50) return 'Berkembang';
		return 'Perlu Latihan';
	};

	const getLevelClass = (level: string) => {
		switch (level) {
			case 'Mahir': return 'bg-green-100 text-green-700';
			case 'Berkembang': return 'bg-primary/10 text-primary';
			default: return 'bg-orange-100 text-orange-700';
		}
	};

	const dimensionIcons: Record<string, string> = {
		'Filler Words': 'record_voice_over',
		'Tutur Kata': 'forum',
		'Intonasi': 'graphic_eq',
		'Kecepatan Bicara': 'speed',
		'Pemilihan Kalimat': 'match_word',
		'Kelengkapan Jawaban': 'checklist',
		'Konsistensi': 'sync',
		'Kepercayaan Diri': 'self_improvement',
		'Raut Wajah': 'mood',
		'Kontak Mata': 'visibility'
	};

	// ── CHART DATA ──
	
	// Trend Chart for Selected Dimension
	let trendChartData = $derived({
		labels: [...sessions].reverse().map((_, i) => `Sesi ${i + 1}`),
		datasets: [{
			label: selectedDimension,
			data: [...sessions].reverse().map(s => {
				const scores = getDimensionScores([s]);
				return scores[dimensions.indexOf(selectedDimension)];
			}),
			borderColor: '#800000',
			backgroundColor: 'rgba(128, 0, 0, 0.1)',
			tension: 0.4,
			fill: true,
			pointBackgroundColor: '#800000',
			pointRadius: 4
		}]
	});

	// AI Insight Logic
	const getAIInsight = () => {
		if (sessions.length < 2) return "Selesaikan lebih banyak sesi untuk mendapatkan insight perkembangan.";
		
		const lastTwo = sessions.slice(0, 2);
		const current = lastTwo[0].overallScore || 0;
		const previous = lastTwo[1].overallScore || 0;
		
		if (current > previous) {
			return "Skor keseluruhanmu meningkat dari sesi sebelumnya. Pertahankan konsistensi ini!";
		} else if (current < previous) {
			return "Ada sedikit penurunan skor. Coba fokus pada dimensi yang paling rendah di sesi terakhir.";
		} else {
			return "Skormu stabil. Cobalah mode 'Dynamic Stress' untuk menantang dirimu lebih jauh.";
		}
	};
</script>

<svelte:head>
	<title>Progress — Heurix</title>
</svelte:head>

<div class="flex min-h-screen bg-[#F8F9FF]">
	<Sidebar />

	<div class="flex min-h-screen flex-1 flex-col md:ml-64">
		<Header />

		<main class="mx-auto w-full max-w-[1100px] px-6 pt-24 pb-20">
			<!-- Header Section -->
			<div class="mb-8">
				<h1 class="text-3xl font-extrabold tracking-tight text-gray-900 md:text-4xl">
					Progres Kemampuan
				</h1>
				<p class="mt-2 text-gray-500">Pantau perkembangan kemampuan wawancaramu secara mendalam.</p>
			</div>

			<div class="space-y-12" in:fade>
				<!-- Section 1: Dimension Picker -->
				<section>
					<h3 class="mb-6 text-xl font-bold text-gray-900">Pilih Dimensi</h3>
					<div class="flex flex-wrap gap-2">
						{#each dimensions as dim}
							<button
								onclick={() => selectedDimension = dim}
								class="px-5 py-2 rounded-full text-xs font-bold transition-all shadow-sm border {selectedDimension === dim ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-100 hover:border-gray-300'}"
							>
								{dim}
							</button>
						{/each}
					</div>
				</section>

				<!-- Section 2: Trend Chart & Insight -->
				<section class="rounded-4xl border border-gray-100 bg-white p-8 shadow-sm">
					<!-- AI Insight Box -->
					<div class="mb-10 flex items-start gap-4 rounded-2xl border border-primary/20 bg-primary/5 p-6">
						<span class="material-symbols-outlined text-primary" style="font-variation-settings: 'FILL' 1">auto_awesome</span>
						<div>
							<span class="mb-1 block text-[10px] font-black tracking-widest text-primary uppercase">Insight AI</span>
							<p class="text-sm font-bold text-gray-800 leading-relaxed">
								{getAIInsight()}
							</p>
						</div>
					</div>

					<div class="mb-6 flex items-center justify-between">
						<h4 class="text-sm font-black tracking-widest text-gray-400 uppercase">Tren Perkembangan</h4>
						<span class="text-xs font-bold text-primary">{selectedDimension}</span>
					</div>
					
					{#if sessions.length > 0}
						<div class="h-80 w-full">
							<Line data={trendChartData} options={{ 
								maintainAspectRatio: false, 
								plugins: { legend: { display: false } },
								scales: {
									y: { min: 0, max: 100, ticks: { font: { weight: 'bold' } } },
									x: { ticks: { font: { weight: 'bold' } } }
								}
							}} />
						</div>
					{:else}
						<div class="flex h-64 items-center justify-center rounded-3xl bg-gray-50 border-2 border-dashed border-gray-200">
							<p class="text-sm font-bold text-gray-400 italic">Belum ada data untuk ditampilkan.</p>
						</div>
					{/if}
				</section>

				<!-- Section 3: Ringkasan Kemampuan -->
				<section>
					<h3 class="mb-8 text-xl font-bold text-gray-900">Ringkasan Kemampuan</h3>
					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
						{#each dimensions as dim}
							{@const score = dimensionDataMap[dim] || 0}
							{@const level = getLevel(score)}
							<div class="flex flex-col gap-4 rounded-3xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:shadow-md">
								<div class="flex items-center gap-4">
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/5 text-primary">
										<span class="material-symbols-outlined text-[20px]">{dimensionIcons[dim]}</span>
									</div>
									<span class="text-xs font-bold text-gray-900 leading-tight">{dim}</span>
								</div>
								<div class="mt-auto">
									<span class="inline-flex px-3 py-1 rounded-full text-[10px] font-black tracking-tight {getLevelClass(level)}">
										{level}
									</span>
								</div>
							</div>
						{/each}
					</div>
				</section>
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
