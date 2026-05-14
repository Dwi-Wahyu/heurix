<script lang="ts">
	import { page } from '$app/state';
	import { pwaState, installApp } from '$lib/pwa.svelte';
	import { sidebarState } from '$lib/sidebar.svelte';
	import { ChevronRight, Download, LogOut } from '@lucide/svelte';

	const breadcrumbMap: Record<string, string> = {
		'/dashboard': 'Beranda',
		'/profile': 'Profil Saya',
		'/history': 'Riwayat Sesi',
		'/progress': 'Progres Kemampuan',
		'/session': 'Sesi',
		'/session/results': 'Hasil Evaluasi',
		'/onboarding': 'Onboarding'
	};

	let breadcrumbs = $derived.by(() => {
		const path = page.url.pathname;

		// Case: /progress - Hide breadcrumbs as requested (following previous simulation rule)
		if (path === '/progress') return [];

		if (path === '/dashboard') return [{ name: 'Beranda', href: '/dashboard' }];

		const parts = path.split('/').filter(Boolean);
		const items = [{ name: 'Beranda', href: '/dashboard' }];

		let currentPath = '';
		parts.forEach((part) => {
			currentPath += `/${part}`;
			if (currentPath === '/dashboard') return;

			const name = breadcrumbMap[currentPath] || part.charAt(0).toUpperCase() + part.slice(1);
			items.push({ name, href: currentPath });
		});

		return items;
	});
</script>

<header
	class="fixed top-0 right-0 left-0 z-50 flex h-16 items-center justify-between border-b border-gray-200/50 bg-white/85 px-6 backdrop-blur-xl transition-all duration-300 {sidebarState.isOpen
		? 'md:left-64'
		: 'md:left-20'}"
>
	<div class="flex items-center gap-2 overflow-hidden">
		<!-- Mobile Logo -->
		<div class="flex items-center gap-0.5 overflow-hidden transition-all duration-300 md:hidden">
			<img src="/logo.png" alt="" class="h-4 w-3" />
			<h1 class="font-bold tracking-tight text-primary">Heurix</h1>
		</div>

		<!-- Breadcrumbs - Hidden on mobile, shown on md and above -->
		<div class="no-scrollbar hidden items-center gap-2 overflow-x-auto md:flex">
			{#each breadcrumbs as item, i}
				{#if i > 0}
					<ChevronRight size={14} class="shrink-0 text-gray-400" />
				{/if}
				{#if i === breadcrumbs.length - 1}
					<span class="shrink-0 truncate text-sm font-bold text-primary">{item.name}</span>
				{:else}
					<a
						href={item.href}
						class="shrink-0 text-sm font-medium text-gray-500 transition-colors hover:text-primary hover:underline"
						>{item.name}</a
					>
				{/if}
			{/each}
		</div>
	</div>

	<div class="flex shrink-0 items-center gap-3">
		{#if pwaState.showInstallButton}
			<button
				onclick={installApp}
				class="flex h-9 items-center gap-2 rounded-full border border-primary/50 bg-primary/10 px-4 transition-all hover:bg-primary/20 active:scale-95"
			>
				<Download size={16} class="text-primary" />
				<span class="hidden text-xs font-bold text-primary sm:inline">Install App</span>
			</button>
		{/if}

		<a
			title="logout"
			href="/logout"
			class="flex items-center justify-center p-2 text-gray-500 transition-colors hover:text-primary"
		>
			<LogOut size={20} />
		</a>
	</div>
</header>
