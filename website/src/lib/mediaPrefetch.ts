/**
 * Register the media service worker, prune stale-build cache entries, then
 * trickle-fetch every clip of the chosen resolution tier — one at a time, so
 * the scrubber's own on-demand loads always win the connection. Each fetch
 * passes through the SW, which stores the whole file; from then on any
 * mid-story jump or repeat visit serves from disk with zero network.
 *
 * Skipped in dev, when the browser lacks service workers, and when the user
 * asked to save data.
 */
import { STAGES } from '@/data/stages'
import { REEL_STAGES } from '@/data/reelStages'
import { pickTier, tierSrc } from '@/components/media/core'
import { assetUrl, ASSET_VERSION } from '@/lib/asset'

export function startMediaPrefetch(): void {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return
  const connection = (navigator as { connection?: { saveData?: boolean } }).connection
  if (connection?.saveData) return

  navigator.serviceWorker
    .register(`${import.meta.env.BASE_URL}sw.js`)
    .then(() => navigator.serviceWorker.ready)
    .then(async (registration) => {
      registration.active?.postMessage({ keepVersion: ASSET_VERSION })
      const tier = pickTier()
      // Reel first: it's the short path most first-time visitors take. Videos
      // before narration/posters — they're what the scrubber blocks on.
      const clips = [...REEL_STAGES, ...STAGES]
      const urls = [
        ...clips.map((s) => tierSrc(s.media.src, tier)),
        ...clips.flatMap((s) => [
          s.media.poster,
          `anim/${s.id}.mp3`,
          `anim/${s.id}.captions.json`,
        ]),
      ]
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
