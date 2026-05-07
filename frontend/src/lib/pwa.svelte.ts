export let pwaState = $state({
    deferredPrompt: null as any,
    showInstallButton: false
});

export function initPwa() {
    if (typeof window !== 'undefined') {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            pwaState.deferredPrompt = e;
            pwaState.showInstallButton = true;
            console.log('PWA: beforeinstallprompt event captured');
        });

        window.addEventListener('appinstalled', () => {
            pwaState.deferredPrompt = null;
            pwaState.showInstallButton = false;
            console.log('PWA: App installed');
        });
    }
}

export async function installApp() {
    if (!pwaState.deferredPrompt) return;
    
    pwaState.deferredPrompt.prompt();
    const { outcome } = await pwaState.deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
        pwaState.showInstallButton = false;
    }
    pwaState.deferredPrompt = null;
}
