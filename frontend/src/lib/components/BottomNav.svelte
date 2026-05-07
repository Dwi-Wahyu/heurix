<script lang="ts">
	import { page } from '$app/state';
	import { Home, Brain, History, User } from '@lucide/svelte';

	const navItems = [
		{ name: 'Beranda', href: '/dashboard', icon: Home },
		{ name: 'Progress', href: '/progress', icon: Brain },
		{ name: 'Riwayat', href: '/history', icon: History },
		{ name: 'Profil', href: '/profile', icon: User }
	];
</script>

<nav
	class="pb-safe fixed bottom-0 left-0 z-50 flex h-[72px] w-full items-center justify-around border-t border-gray-200/50 bg-white/80 px-2 shadow-[0_-10px_30px_rgba(0,0,0,0.02)] backdrop-blur-md md:hidden"
>
	{#each navItems as item}
		{@const Icon = item.icon}
		<a
			href={item.href}
			class="group relative flex h-full w-16 flex-col items-center justify-center transition-colors {page
				.url.pathname === item.href
				? 'text-primary'
				: 'text-gray-400 hover:text-gray-900'}"
		>
			{#if page.url.pathname === item.href}
				<div class="absolute top-0 h-1 w-8 rounded-b-full bg-primary"></div>
			{/if}
			<Icon
				size={24}
				strokeWidth={page.url.pathname === item.href ? 2.5 : 2}
				class="mb-1 transition-all group-active:scale-90"
			/>
			<span class="text-[10px] font-bold tracking-wide">{item.name}</span>
		</a>
	{/each}
</nav>
