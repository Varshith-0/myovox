/** Imperative media element lifecycle helpers for the scroll-scrub hot path. */
import { MEDIA_CONFIG } from './mediaConfig'

const SEEK_EPS = MEDIA_CONFIG.seekEpsSeconds

export const VISIBLE_DISTANCE = MEDIA_CONFIG.visibilityDistance
export const WARM_DISTANCE = MEDIA_CONFIG.warmDistance

/** Hide distant stages so the compositor can skip them. */
export function updateStageVisibility(el: HTMLElement, distance: number, maxDistance = 2): boolean {
  if (distance > maxDistance) {
    if (el.style.display !== 'none') el.style.display = 'none'
    return false
  }
  if (el.style.display === 'none') el.style.display = ''
  return true
}

export function ensureImageSrc(img: HTMLImageElement, url: string): void {
  if (img.getAttribute('src') !== url) img.setAttribute('src', url)
}

export function ensureVideoSrc(video: HTMLVideoElement, url: string): void {
  if (video.getAttribute('src') !== url) {
    video.setAttribute('src', url)
    video.load()
  }
}

/** Release decoder/network state for very-far clips. */
export function detachVideoSrc(video: HTMLVideoElement): void {
  if (!video.getAttribute('src')) return
  video.removeAttribute('src')
  video.load()
}

/**
 * Conservative preload policy:
 * - active/adjacent: `auto`
 * - visible edge and warm ring: `metadata`
 * - detached clips: `none`
 */
export function setVideoPreload(video: HTMLVideoElement, distance: number): void {
  const desired = distance <= 1 ? 'auto' : distance <= WARM_DISTANCE ? 'metadata' : 'none'
  if (video.preload !== desired) video.preload = desired
}

/** Seek only when decoder-ready and not currently seeking to avoid decoder thrash. */
export function maybeSeekVideo(video: HTMLVideoElement, local: number): void {
  if (
    video.readyState >= 1 &&
    Number.isFinite(video.duration) &&
    video.duration > 0 &&
    !video.seeking
  ) {
    const t = local * video.duration
    if (Math.abs(video.currentTime - t) > SEEK_EPS) video.currentTime = t
  }
}
