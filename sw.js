/* Nova Archive service worker: makes the app start offline.
   - Same-origin files: network first (so a new deploy shows up right away), cache as fallback.
   - Firebase SDK + Google Fonts: stale-while-revalidate runtime cache.
   - Firebase Auth helper URLs (/__/...) and Firestore/API traffic are never touched. */
const VERSION = 'nova-v23';
const SHELL = ['./', 'index.html', 'css/base.css', 'css/theme-dune.css', 'css/theme-nova.css', 'css/theme-paper.css', 'css/theme-terminal.css', 'js/actions.js', 'js/addbook.js', 'js/bookpage.js', 'js/cards.js', 'js/config.js', 'js/data.js', 'js/enrich.js', 'js/games.js', 'js/importlists.js', 'js/main.js', 'js/overlay.js', 'js/state.js', 'js/sync.js', 'js/theme.js', 'js/util.js', 'js/views.js', 'data.json', 'firebase-config.js', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  if (url.origin === self.location.origin) {
    if (url.pathname.startsWith('/__/')) return;              // Firebase Auth / init helpers
    e.respondWith(
      fetch(req, { cache: 'no-cache' }).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
        return res;
      }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || (req.mode === 'navigate' ? caches.match('index.html') : Response.error())))
    );
    return;
  }

  const runtimeHosts = ['www.gstatic.com', 'fonts.googleapis.com', 'fonts.gstatic.com'];
  if (runtimeHosts.includes(url.hostname) && (url.hostname !== 'www.gstatic.com' || url.pathname.startsWith('/firebasejs/'))) {
    e.respondWith(
      caches.open(VERSION).then(c => c.match(req).then(hit => {
        const net = fetch(req).then(res => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }).catch(() => hit);
        return hit || net;
      }))
    );
  }
});
