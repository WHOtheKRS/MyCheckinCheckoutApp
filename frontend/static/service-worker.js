const CACHE_NAME = "pwa-cache-v1";
const urlsToCache = [
    "/",
    "/static/styles.css",
    "/static/app.js",
    "/static/downloads.png",
    "/static/smartphone-call.png"
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log("Opened cache");
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName))
            );
        })
    );
});
// Speeds up page load times by serving cached files.
// Works offline (cached assets load even without internet).
// Automatically updates when a new version is deployed.
// Reduces server load by serving assets from the cache.