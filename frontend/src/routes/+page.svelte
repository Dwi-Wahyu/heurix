<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		goto('/login');
	});
</script>

<div class="flex h-screen items-center justify-center bg-background text-primary">
	<div class="animate-pulse text-2xl font-bold">HiReady...</div>
</div>
