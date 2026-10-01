// Production Report System - Service Worker
const CACHE_NAME = 'prod-report-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

// Network-first strategy: Always fetch live from the server so 100 employees get updates instantly!
self.addEventListener('fetch', (event) => {
    // Let all API and submit requests go directly to network
    if (event.request.url.includes('/api/') || event.request.method !== 'GET') {
        return;
    }
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                return response;
            })
            .catch(() => {
                return caches.match(event.request);
            })
    );
});
