<script lang="ts">
	import { page } from '$app/state';
	import { sidebarState, toggleSidebar } from '$lib/sidebar.svelte';
	import { PanelLeftClose, PanelLeftOpen, Home, Brain, History, User, X } from '@lucide/svelte';

	import { onMount } from 'svelte';

	const navItems = [
		{ name: 'Beranda', href: '/dashboard', icon: Home },
		{ name: 'Progress', href: '/progress', icon: Brain },
		{ name: 'Riwayat', href: '/history', icon: History },
		{ name: 'Profil', href: '/profile', icon: User }
	];

	// Initial state setup
	onMount(() => {
		if (window.innerWidth >= 768) {
			sidebarState.isOpen = true;
		}
	});

	// Auto-close sidebar on mobile when navigating
	$effect(() => {
		// We track page.url.pathname
		const _path = page.url.pathname;

		if (window.innerWidth < 768 && sidebarState.isOpen) {
			sidebarState.isOpen = false;
		}
	});
</script>

{#if sidebarState.isOpen}
	<!-- Mobile Overlay -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		onclick={toggleSidebar}
		class="fixed inset-0 z-[60] bg-black/60 backdrop-blur-sm transition-opacity duration-300 md:hidden"
	></div>
{/if}

<nav
	class="fixed top-0 left-0 z-[70] h-screen flex-col gap-2 border-r border-gray-100 bg-white p-4 shadow-xl transition-all duration-300 {sidebarState.isOpen
		? 'flex w-64 translate-x-0'
		: 'hidden md:flex w-20'}"
>
	<div class="mt-4 mb-8 flex items-center justify-between px-2">
		{#if sidebarState.isOpen}
			<div class="flex items-center gap-3">
				<div class="flex items-end gap-1 overflow-hidden transition-all duration-300">
					<img src="/logo.png" alt="" class="h-10 w-9 min-w-[36px]" />
					<h1 class="text-3xl font-extrabold tracking-tight whitespace-nowrap text-primary">
						iReady
					</h1>
				</div>

				<!-- Mobile Close Button next to logo -->
				<button
					onclick={toggleSidebar}
					class="flex items-center justify-center rounded-lg p-1 text-gray-500 transition-colors hover:bg-gray-100 md:hidden"
					aria-label="Close sidebar"
				>
					<X size={20} />
				</button>
			</div>
		{/if}

		<button
			onclick={toggleSidebar}
			class="hidden items-center justify-center rounded-lg p-1 transition-colors hover:bg-gray-100 md:flex {sidebarState.isOpen
				? ''
				: 'w-full'}"
			aria-label={sidebarState.isOpen ? 'Close sidebar' : 'Open sidebar'}
		>
			{#if sidebarState.isOpen}
				<PanelLeftClose size={20} class="text-primary" />
			{:else}
				<PanelLeftOpen size={20} class="text-primary" />
			{/if}
		</button>
	</div>

	{#if sidebarState.isOpen}
		<p class="mb-4 px-2 text-xs text-gray-500 transition-opacity duration-300">Career Excellence</p>
	{/if}

	<div class="flex flex-col gap-2">
		{#each navItems as item (item.href)}
			{@const Icon = item.icon}
			<a
				href={item.href}
				class="flex items-center gap-3 rounded-lg py-3 transition-all active:translate-x-1 {sidebarState.isOpen
					? 'px-4'
					: 'justify-center px-0'} {page.url.pathname === item.href
					? 'bg-surface-container font-semibold text-primary'
					: 'text-gray-600 hover:bg-gray-50 hover:text-primary'}"
				title={!sidebarState.isOpen ? item.name : ''}
			>
				<Icon
					size={20}
					strokeWidth={page.url.pathname === item.href ? 2.5 : 2}
					class={page.url.pathname === item.href ? 'text-primary' : ''}
				/>
				{#if sidebarState.isOpen}
					<span
						class="overflow-hidden text-sm font-medium whitespace-nowrap transition-all duration-300"
						>{item.name}</span
					>
				{/if}
			</a>
		{/each}
	</div>
</nav>
