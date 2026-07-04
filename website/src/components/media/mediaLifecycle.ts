/** Scrub-video lifecycle + canvas drawing for the scroll-scrub hot path. */
import { assetUrl } from '@/lib/asset'
import { MEDIA_CONFIG } from './core'

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
 * Get (or create) a clip's scrub video. `preload=auto` pulls the whole file —
 * every clip is a single small all-keyframe MP4, so this is one request, and the
 * hardware decoder holds only a couple of frames in its own buffer. That is what
 * makes scrubbing robust on any device: no per-frame fetches to outrun, no
 * decoded-bitmap window for the OS to evict under memory pressure.
 */
export function ensureClipVideo(
  cache: Map<string, HTMLVideoElement>,
  id: string,
  src: string,
): HTMLVideoElement {
  let video = cache.get(id)
  if (video) return video
  video = document.createElement('video')
  video.muted = true
  video.playsInline = true
  video.preload = 'auto'
  video.src = assetUrl(src)
  video.load()
  cache.set(id, video)
  return video
}

/** Drop a clip's video entirely so the browser reclaims decoder + buffer memory. */
export function releaseClipVideo(cache: Map<string, HTMLVideoElement>, id: string): void {
  const video = cache.get(id)
  if (!video) return
  video.removeAttribute('src')
  video.load()
  cache.delete(id)
}

/**
 * Seek the video to the scroll-mapped time, coalesced: while a seek is in flight
 * we issue nothing, so however fast the RAF loop runs, seeks land at the decoder's
 * own pace and always jump straight to the *latest* target — never a queue of
 * stale frames. Every frame is a keyframe, so each seek decodes exactly one frame.
 */
export function scrubVideo(video: HTMLVideoElement, progress: number): void {
  if (video.readyState < HTMLMediaElement.HAVE_METADATA || video.seeking) return
  if (!Number.isFinite(video.duration)) return
  const frame = 1 / MEDIA_CONFIG.fps
  // Last full frame, not duration itself — seeking to the exact end can blank.
  const target = Math.max(0, progress * (video.duration - frame))
  if (Math.abs(video.currentTime - target) < frame / 2) return
  video.currentTime = target
}

/** True when the video has a decoded frame ready to draw. */
export function videoDrawable(video: HTMLVideoElement): boolean {
  return video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && video.videoWidth > 0
}

/**
 * Draw the video's current frame into the shared canvas with contain/cover fit.
 * Uses the backing size the ResizeObserver already set — no per-frame layout read.
 * `alignTop` mirrors the mobile CSS that anchors a contained clip to the top of
 * its band. drawImage from a video element is a GPU-side copy of the frame the
 * hardware decoder already produced — nothing decodes on the main thread.
 */
export function drawFrame(
  canvas: HTMLCanvasElement,
  video: HTMLVideoElement,
  fit: 'contain' | 'cover' | undefined,
  alignTop: boolean,
): void {
  const bw = canvas.width
  const bh = canvas.height
  const iw = video.videoWidth
  const ih = video.videoHeight
  if (!bw || !bh || !iw || !ih) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const scale = fit === 'cover' ? Math.max(bw / iw, bh / ih) : Math.min(bw / iw, bh / ih)
  const dw = iw * scale
  const dh = ih * scale
  const dx = (bw - dw) / 2
  const dy = fit !== 'cover' && alignTop ? 0 : (bh - dh) / 2

  ctx.clearRect(0, 0, bw, bh)
  ctx.drawImage(video, dx, dy, dw, dh)
}
