<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import { pwaInfo } from 'virtual:pwa-info';
    import { onMount } from 'svelte';
    import { initPwa } from '$lib/pwa.svelte';

    let { children } = $props();

    const webManifestLink = $derived(pwaInfo ? pwaInfo.webManifest.linkTag : '');

    onMount(() => {
        initPwa();
    });
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    
    {@html webManifestLink}
    
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
</svelte:head>

{@render children()}