//// --- CRASH DETECTION & RECOVERY (HEARTBEAT) ---
// If the app was closed without 'beforeunload' or 'pagehide', it might have crashed (OOM).

const CRASH_FLAG = 'digita_crash_detected';
const SESSION_FLAG = 'digita_session_active';

function clearAppCache() {
    console.warn("CRASH RECOVERY: Unregistering SW and clearing caches.");
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            for (let registration of registrations) {
                registration.unregister();
            }
        });
    }
    if ('caches' in window) {
        caches.keys().then(names => {
            for (let name of names) {
                caches.delete(name);
            }
        });
    }
}

// Check if we crashed last time
if (localStorage.getItem(CRASH_FLAG) === 'true' || localStorage.getItem(SESSION_FLAG) === 'true') {
    clearAppCache();
    // Reset flags
    localStorage.removeItem(CRASH_FLAG);
    localStorage.removeItem(SESSION_FLAG);
    console.log("System recovered from crash. Cache cleared.");
    // Optional: Show message to user
    alert("O aplicativo foi recuperado de um erro anterior.");
}

// Set session flag
localStorage.setItem(SESSION_FLAG, 'true');

// Clear session flag on clean exit
window.addEventListener('pagehide', () => {
    localStorage.removeItem(SESSION_FLAG);
});
window.addEventListener('beforeunload', () => {
    localStorage.removeItem(SESSION_FLAG);
});

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
