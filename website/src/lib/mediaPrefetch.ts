/**
 * Register the media service worker, prune stale-build cache entries, then
 * trickle-fetch the light story assets — one at a time, so the scrubber's own
 * on-demand loads always win the connection. Each fetch passes through the SW,
 * which stores the whole file; from then on any mid-story jump or repeat visit
 * serves from disk with zero network.
 *
 * Skipped in dev, when the browser lacks service workers, and when the user
 * asked to save data.
 */
import { STAGES } from '@/data/stages'
import { ONE_BREATH_STAGES } from '@/data/oneBreathStages'
import { animDir, assetUrl, ASSET_VERSION, MEDIA_ORIGIN } from '@/lib/asset'

export function startMediaPrefetch(): void {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return
  const connection = (navigator as { connection?: { saveData?: boolean } }).connection
  if (connection?.saveData) return

  // The ?media= param tells the SW which CDN origin also counts as anim media
  // (and re-installs the SW when the media host changes — exactly when needed).
  const swUrl = `${import.meta.env.BASE_URL}sw.js${
    MEDIA_ORIGIN ? `?media=${encodeURIComponent(MEDIA_ORIGIN)}` : ''
  }`
  navigator.serviceWorker
    .register(swUrl)
    .then(() => navigator.serviceWorker.ready)
    .then(async (registration) => {
      registration.active?.postMessage({ keepVersion: ASSET_VERSION })
      // One Breath first: it's the short path most first-time visitors take.
      // Scrub strips before narration/posters — they're what makes any stage
      // instantly drawable; the crisp frames load on demand while scrubbing.
      const clips = [...ONE_BREATH_STAGES, ...STAGES]
      const urls = clips.flatMap((s) => [
        `${animDir(s)}/scrub/${s.id}/strip.webp`,
        s.media.poster,
        `${animDir(s)}/audio/${s.id}.mp3`,
        `${animDir(s)}/captions/${s.id}.json`,
      ])
      for (const url of urls) {
        try {
          await fetch(assetUrl(url))
        } catch {
          return // offline / flaky network — the scrubber still loads on demand
        }
      }
    })
    .catch(() => {})
}
