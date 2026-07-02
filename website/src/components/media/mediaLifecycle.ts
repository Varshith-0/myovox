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
 * Preload a clip's entire frame sequence into memory (idempotent). Holding every
 * frame is what makes scrubbing robust: once loaded, drawing any position is a
 * synchronous, network-free `drawImage` — no seek, no decode-wait, no buffer
 * starvation, however fast the scroll moves.
 */
export function ensureClipFrames(
  cache: Map<string, FrameClip>,
  id: string,
  count: number,
  tier: FrameTier,
): void {
  if (cache.has(id)) return
  const images: HTMLImageElement[] = new Array(count)
  for (let i = 0; i < count; i++) {
    const img = new Image()
    img.decoding = 'async'
    img.src = assetUrl(frameUrlPath(tier, id, i))
    images[i] = img
  }
  cache.set(id, { images, count })
}

/** Drop a clip's frames so the browser can reclaim the decoded memory. */
export function releaseClipFrames(cache: Map<string, FrameClip>, id: string): void {
  const clip = cache.get(id)
  if (!clip) return
  for (const img of clip.images) img.src = ''
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
