/** Frame-sequence lifecycle + canvas drawing for the scroll-scrub hot path. */
import { assetUrl } from '@/lib/asset'
import { MEDIA_CONFIG, frameUrlPath, type FrameClip, type FrameTier } from './core'

export const VISIBLE_DISTANCE = MEDIA_CONFIG.visibilityDistance
export const PRELOAD_DISTANCE = MEDIA_CONFIG.preloadDistance
export const RELEASE_DISTANCE = MEDIA_CONFIG.releaseDistance

/** Hide distant stages so the compositor can skip them. */
export function updateStageVisibility(el: HTMLElement, distance: number, maxDistance = 2): boolean {
  if (distance > maxDistance) {
    if (el.style.display !== 'none') el.style.display = 'none'
    return false
  }
  if (el.style.display === 'none') el.style.display = ''
  return true
}

/**
 * Keep a bounded window of frames loaded around `idx`, current frame first.
 *
 * This is what makes scrubbing robust on any device: instead of fetching every
 * frame of a clip (thousands of images → mobile floods the network and the browser
 * evicts them under memory pressure → a fast-scroll stop shows nothing), we fetch
 * only [idx-loadBack, idx+loadAhead] and free anything outside [idx-keepBack,
 * idx+keepAhead]. The frame you stop on is fetched at high priority, so it paints
 * immediately instead of waiting for frames 0..idx to load in order.
 */
export function ensureClipWindow(
  cache: Map<string, FrameClip>,
  id: string,
  count: number,
  tier: FrameTier,
  idx: number,
): void {
  let clip = cache.get(id)
  if (!clip) {
    clip = { images: new Array(count), count, requested: new Set() }
    cache.set(id, clip)
  }
  const images = clip.images

  const loStart = Math.max(0, idx - MEDIA_CONFIG.loadBack)
  const loEnd = Math.min(count - 1, idx + MEDIA_CONFIG.loadAhead)
  for (let j = loStart; j <= loEnd; j++) {
    if (images[j]) continue
    const img = new Image()
    img.decoding = 'async'
    img.fetchPriority = j === idx ? 'high' : Math.abs(j - idx) <= 8 ? 'auto' : 'low'
    img.src = assetUrl(frameUrlPath(tier, id, j))
    images[j] = img
  }

  // Free frames well outside the window so held memory stays flat regardless of
  // clip length — the fix for mobile eviction.
  const keepLo = Math.max(0, idx - MEDIA_CONFIG.keepBack)
  const keepHi = Math.min(count - 1, idx + MEDIA_CONFIG.keepAhead)
  for (let j = 0; j < count; j++) {
    const img = images[j]
    if (img && (j < keepLo || j > keepHi)) {
      img.src = ''
      images[j] = undefined
      clip.requested.delete(j)
    }
  }
}

/**
 * Warm the next few frames' decodes off the main thread. drawImage(img) otherwise
 * decodes the WebP synchronously on first paint — a multi-ms stall per new frame
 * at 1080p that reads as scrub jank. Decoding ahead turns each draw into a pure
 * GPU upload. Each index is requested once; a small back-window covers reversals.
 */
export function decodeAheadClip(clip: FrameClip, idx: number, ahead: number): void {
  const start = Math.max(0, idx - 2)
  const end = Math.min(clip.count - 1, idx + ahead)
  for (let j = start; j <= end; j++) {
    if (clip.requested.has(j)) continue
    const img = clip.images[j]
    if (!img || !img.complete || !img.naturalWidth) continue
    clip.requested.add(j)
    img.decode().catch(() => clip.requested.delete(j))
  }
}

/** Drop a clip's frames entirely so the browser can reclaim the memory. */
export function releaseClipFrames(cache: Map<string, FrameClip>, id: string): void {
  const clip = cache.get(id)
  if (!clip) return
  for (const img of clip.images) if (img) img.src = ''
  cache.delete(id)
}

/**
 * Draw one frame into the shared canvas with contain/cover fit. Uses the backing
 * size the ResizeObserver already set — no per-frame layout read. `alignTop`
 * mirrors the mobile CSS that anchors a contained clip to the top of its band.
 */
export function drawFrame(
  canvas: HTMLCanvasElement,
  img: HTMLImageElement,
  fit: 'contain' | 'cover' | undefined,
  alignTop: boolean,
): void {
  const bw = canvas.width
  const bh = canvas.height
  const iw = img.naturalWidth
  const ih = img.naturalHeight
  if (!bw || !bh || !iw || !ih) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const scale = fit === 'cover' ? Math.max(bw / iw, bh / ih) : Math.min(bw / iw, bh / ih)
  const dw = iw * scale
  const dh = ih * scale
  const dx = (bw - dw) / 2
  const dy = fit !== 'cover' && alignTop ? 0 : (bh - dh) / 2

  ctx.clearRect(0, 0, bw, bh)
  ctx.drawImage(img, dx, dy, dw, dh)
}
