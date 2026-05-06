<script lang="ts">
    import { goto } from '$app/navigation';
    import { fade, fly } from 'svelte/transition';

    let { data } = $props();
    let avatars = $derived(data.avatars);

    let selectedAvatarId = $state(data.avatars?.[0]?.id || '');

    function handleSelect(id: string) {
        selectedAvatarId = id;
    }

    function handleContinue() {
        if (!selectedAvatarId) return;
        goto(`/session/disclaimer?avatarId=${selectedAvatarId}`);
    }
</script>

<svelte:head>
    <title>Pilih Pewawancara — HiReady</title>
</svelte:head>

<div class="min-h-screen bg-[#f4f7fb] py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <div class="text-center mb-12" in:fade={{ duration: 600 }}>
            <h1 class="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">Pilih Pewawancara Anda</h1>
            <p class="text-lg text-gray-600">Setiap pewawancara memiliki gaya dan karakteristik yang berbeda.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            {#each avatars as avatar, i (avatar.id)}
                <div 
                    class="relative group cursor-pointer"
                    onclick={() => handleSelect(avatar.id)}
                    onkeydown={(e) => e.key === 'Enter' && handleSelect(avatar.id)}
                    role="button"
                    tabindex="0"
                    in:fly={{ y: 20, delay: i * 100, duration: 600 }}
                >
                    <div class="absolute inset-0 bg-primary rounded-3xl blur-xl opacity-0 transition-opacity duration-300 group-hover:opacity-10 {selectedAvatarId === avatar.id ? 'opacity-20' : ''}"></div>
                    
                    <div class="relative bg-white rounded-3xl border-2 transition-all duration-300 overflow-hidden {selectedAvatarId === avatar.id ? 'border-primary shadow-glow scale-[1.02]' : 'border-gray-100 shadow-soft hover:border-gray-200'}">
                        <!-- Avatar Thumbnail Placeholder -->
                        <div class="h-48 bg-gray-50 flex items-center justify-center border-b border-gray-100">
                            {#if avatar.thumbnailUrl}
                                <img src={avatar.thumbnailUrl} alt={avatar.name} class="w-full h-full object-cover" />
                            {:else}
                                <span class="material-symbols-outlined text-[80px] text-gray-200">account_circle</span>
                            {/if}
                            
                            {#if selectedAvatarId === avatar.id}
                                <div class="absolute top-4 right-4 bg-primary text-white rounded-full p-1" transition:fade>
                                    <span class="material-symbols-outlined text-sm">check</span>
                                </div>
                            {/if}
                        </div>

                        <div class="p-6">
                            <h3 class="text-xl font-bold text-gray-900 mb-1">{avatar.name}</h3>
                            <p class="text-xs font-bold tracking-widest text-primary uppercase mb-3">{avatar.track}</p>
                            <p class="text-sm text-gray-500 leading-relaxed">
                                {#if avatar.id === 'avatar_professional_man'}
                                    Pewawancara berpengalaman dengan gaya yang formal namun tetap suportif.
                                {:else if avatar.id === 'avatar_young_man'}
                                    Rekruter muda yang energik, fokus pada potensi kreatif dan teknis.
                                {:else if avatar.id === 'avatar_hassan'}
                                    Manajer senior yang bijaksana, menilai integritas dan visi jangka panjang.
                                {:else}
                                    Siap membantu Anda berlatih wawancara dengan feedback profesional.
                                {/if}
                            </p>
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <div class="mt-16 flex justify-center" in:fade={{ delay: 400 }}>
            <button
                onclick={handleContinue}
                disabled={!selectedAvatarId}
                class="group flex items-center justify-center gap-3 rounded-2xl bg-primary px-12 py-4 text-xl font-bold text-white shadow-glow transition-all hover:scale-[1.02] hover:shadow-xl active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Pilih & Lanjutkan
                <span class="material-symbols-outlined transition-transform group-hover:translate-x-1">arrow_forward</span>
            </button>
        </div>
        
        <div class="mt-8 text-center">
            <a href="/dashboard" class="text-sm font-semibold text-gray-500 hover:text-gray-700 transition-colors">
                Kembali ke Dashboard
            </a>
        </div>
    </div>
</div>

<style>
    .shadow-glow {
        box-shadow: 0 0 20px rgba(128, 0, 0, 0.15);
    }
</style>