const CACHE_NAME = 'digitatea-v4';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './game_icon.png',
    './manifest.json'
];

const EXTERNAL_ASSETS = [
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
];

// Install Event
self.addEventListener('install', event => {
    // Force new SW to enter waiting state
    self.skipWaiting(); 
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                
                // Fetch externals independently so they don't break the main offline installation on iOS Safari
                EXTERNAL_ASSETS.forEach(url => {
                    fetch(new Request(url, { mode: 'no-cors' }))
                        .then(response => {
                            if (response) cache.put(url, response);
                        })
                        .catch(err => console.error('Silent fail on external asset cache:', err));
                });

                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Activate Event - Clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch Event
self.addEventListener('fetch', event => {
    // Strategy: Cache First, Network Fallback
    // For JSON data (levels), maybe Network First is better?
    // Let's use Stale-While-Revalidate for JSON to ensure speed but get updates.
    
    // Strategy: Network First for JSON (always try to get fresh data)
    // Fallback to cache if offline.
    if (event.request.url.includes('.json')) {
        event.respondWith(
            fetch(event.request)
                .then(networkResponse => {
                    const clonedResponse = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, clonedResponse);
                    });
                    return networkResponse;
                })
                .catch(() => {
                    return caches.match(event.request);
                })
        );
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request).then(
                    networkResponse => {
                        // Dynamic caching for other assets (images, audio)
                        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                            return networkResponse;
                        }
                        const responseToCache = networkResponse.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        return networkResponse;
                    }
                );
            })
    );
});

// Message handling for force update/clear/precache
self.addEventListener('message', event => {
    if (event.data && event.data.action === 'skipWaiting') {
        self.skipWaiting();
    }
    if (event.data && event.data.action === 'clearCache') {
        caches.keys().then(keys => {
            keys.forEach(key => caches.delete(key));
        });
    }
    if (event.data && event.data.action === 'precacheAll') {
        // Fetch the list and cache everything
        const port = event.ports[0];
        fetch('./data/cache_list.json', { cache: 'no-store' })
            .then(res => res.json())
            .then(filesToCache => {
                let loaded = 0;
                const total = filesToCache.length;
                
                caches.open(CACHE_NAME).then(cache => {
                    // Download sequentially or in small batches to avoid overwhelming the browser
                    const cacheSequence = filesToCache.reduce((promise, file) => {
                        return promise.then(() => {
                            return cache.add(file).then(() => {
                                loaded++;
                                // Send progress back to UI
                                if (port) port.postMessage({status: 'progress', loaded, total});
                            }).catch(err => {
                                console.error('Failed to cache:', file, err);
                                // Continue even if one fails
                            });
                        });
                    }, Promise.resolve());

                    cacheSequence.then(() => {
                        if (port) port.postMessage({status: 'done', total});
                    });
                });
            })
            .catch(err => {
                if (port) port.postMessage({status: 'error', error: err.toString()});
            });
    }
});
