//// --- CRASH DETECTION & RECOVERY ---
// O antigo sistema apagava os caches. Isso foi removido para proteger o modo Offline em iPads.

const CRASH_FLAG = 'digita_crash_detected';

// Check se a flag do app travado existe (apenas registra no console, não apaga mais o offline cache)
if (localStorage.getItem(CRASH_FLAG) === 'true') {
    console.warn("App Recovery: O aplicativo foi reiniciado após um possível fechamento inesperado.");
    localStorage.removeItem(CRASH_FLAG);
}

// --- SW REGISTRATION ---
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
