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
	class="bg-white/80 fixed bottom-0 left-0 w-full z-50 border-t border-gray-200/50 backdrop-blur-md flex justify-around items-center h-[72px] pb-safe px-2 shadow-[0_-10px_30px_rgba(0,0,0,0.02)] md:hidden"
>
	{#each navItems as item}
		<a
			href={item.href}
			class="flex flex-col items-center justify-center w-16 h-full group relative transition-colors {page
				.url.pathname === item.href
				? 'text-primary'
				: 'text-gray-400 hover:text-gray-900'}"
		>
			{#if page.url.pathname === item.href}
				<div class="absolute top-0 w-8 h-1 bg-primary rounded-b-full"></div>
			{/if}
			<span
				class="material-symbols-outlined mb-1 transition-all group-active:scale-90 text-[24px]"
				style="font-variation-settings: 'FILL' {page.url.pathname === item.href ? 1 : 0};"
			>
				{item.icon}
			</span>
			<span class="text-[10px] font-bold tracking-wide">{item.name}</span>
		</a>
	{/each}
</nav>
