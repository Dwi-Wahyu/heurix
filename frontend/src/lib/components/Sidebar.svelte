<script lang="ts">
	import { page } from '$app/state';

	const navItems = [
		{ name: 'Beranda', href: '/dashboard', icon: 'home' },
		{ name: 'Simulasi', href: '/onboarding', icon: 'psychology' },
		{ name: 'Riwayat', href: '/history', icon: 'history' },
		{ name: 'Profil', href: '/profile', icon: 'person' }
	];
</script>

<nav
	class="fixed top-0 left-0 z-50 hidden h-screen w-64 flex-col gap-2 border-r border-gray-100 bg-white p-4 shadow-sm md:flex"
>
	<div class="mt-4 mb-8 px-2">
		<div class="flex items-end gap-1">
			<img src="/logo.png" alt="" class="h-10 w-9" />
			<h1 class="text-3xl font-extrabold tracking-tight text-primary">iReady</h1>
		</div>
		<p class="mt-4 text-xs text-gray-500">Career Excellence</p>
	</div>

	{#each navItems as item}
		<a
			href={item.href}
			class="flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all active:translate-x-1 {page
				.url.pathname === item.href
				? 'bg-surface-container font-semibold text-primary'
				: 'text-gray-600 hover:bg-gray-50 hover:text-primary'}"
		>
			<span
				class="material-symbols-outlined"
				style="font-variation-settings: 'FILL' {page.url.pathname === item.href ? 1 : 0};"
			>
				{item.icon}
			</span>
			<span>{item.name}</span>
		</a>
	{/each}
</nav>
