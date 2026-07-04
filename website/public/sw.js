/**
 * Media service worker: cache-first for everything under anim/ (immutable
 * renders, cache-busted by ?v=<build>), so repeat visits and mid-story jumps
 * serve from disk with zero network.
 *
 * Videos arrive as Range requests, and the Cache API cannot store partial (206)
 * responses — so each file is fetched and stored WHOLE exactly once, and any
 * requested byte range is served by slicing the cached body. Safari requires a
 * real 206 for media ranges, so the slice is never shortcut to a 200.
 */
const CACHE = 'myovox-media'

self.addEventListener('install', () => self.skipWaiting())

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim())
})

// The page posts its build id after registering; entries from older builds
// (different ?v=) are pruned so deploys don't accumulate dead megabytes.
self.addEventListener('message', (event) => {
  const keep = event.data && event.data.keepVersion
  if (!keep) return
  event.waitUntil(
    caches.open(CACHE).then(async (cache) => {
      for (const req of await cache.keys()) {
        if (!req.url.includes(`v=${keep}`)) await cache.delete(req)
      }
    }),
  )
})

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  if (url.origin !== location.origin || !url.pathname.includes('/anim/')) return
  // Any failure (quota exceeded, cache API oddity) falls back to plain network.
  event.respondWith(serveMedia(event.request).catch(() => fetch(event.request)))
})

async function serveMedia(request) {
  const cache = await caches.open(CACHE)
  let full = await cache.match(request.url)
  if (!full) {
    // Re-fetch by URL without the Range header → a cacheable 200 with the whole body.
    const res = await fetch(request.url)
    if (!res.ok || res.status === 206) return fetch(request)
    await cache.put(request.url, res.clone())
    full = res
  }

  const range = /bytes=(\d+)-(\d+)?/.exec(request.headers.get('range') || '')
  if (!range) return full

  const buf = await full.arrayBuffer()
  const size = buf.byteLength
  const start = Number(range[1])
  const end = range[2] ? Math.min(Number(range[2]), size - 1) : size - 1
  return new Response(buf.slice(start, end + 1), {
    status: 206,
    headers: {
      'Content-Type': full.headers.get('Content-Type') || 'video/mp4',
      'Content-Range': `bytes ${start}-${end}/${size}`,
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes',
    },
  })
}
