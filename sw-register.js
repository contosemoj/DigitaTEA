// sw-register.js

// Crash Detection Logic
(function checkCrashLoop() {
    const crashFlag = localStorage.getItem('digita_crash_detected');
    if (crashFlag === 'true') {
        console.warn('Crash detected from previous session. Clearing Service Worker and Caches.');
        
        // Unregister all SWs
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(registrations) {
                for(let registration of registrations) {
                    registration.unregister();
                }
            });
        }
        
        // Clear Caches
        if ('caches' in window) {
            caches.keys().then(function(names) {
                for (let name of names) {
                    caches.delete(name);
                }
            });
        }

        // Reset flag
        localStorage.removeItem('digita_crash_detected');
        
        // Optional: Show message to user
        alert("O aplicativo foi recuperado de um erro anterior.");
    }
})();

// Register SW
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
