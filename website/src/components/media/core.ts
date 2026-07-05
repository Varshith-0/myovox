/** Shared config, types, and scroll→scrub math for the MediaLayer subsystem. */
import type { MutableRefObject } from 'react'
import { type Stage } from '@/data/stages'
import { clamp01 } from '@/lib/num'

/** Centralized tuning knobs for the video scrubber. */
export const MEDIA_CONFIG = {
  /** Stages within this distance keep their poster mounted/visible. */
  visibilityDistance: 2,
  /** Preload a clip's video (metadata + data) within this stage distance of active. */
  preloadDistance: 2,
  /** Release a clip's video (free decoder + buffer) beyond this stage distance. */
  releaseDistance: 3,
  /** Crossfade speed from poster → live canvas once the video is drawable. */
  frameRevealLerp: 0.16,
  /** All clips are rendered at this rate; scrub seeks snap to its frame grid. */
  fps: 30,
  /** Show the "rendering…" overlay only after the active clip has been un-drawable
   *  this many RAF frames (~200ms) — so a real stall triggers it but brief
   *  in-scroll gaps don't flash it. */
  loadDebounceFrames: 12,
  /** Canvas backing scale cap. 3 = render at full density on DPR-3 phones (no
   *  2x→3x upscale blur); the source tier is chosen separately by pickTier. */
  maxDpr: 3,
  holdStart: 0.04,
  revealEnd: 0.16,
  captionRiseVh: 22,
  sceneFadeLerp: 0.26,
  stagePresenceLerp: 0.2,
} as const

export const HOLD = MEDIA_CONFIG.holdStart
export const REVEAL = MEDIA_CONFIG.revealEnd
export const RISE_VH = MEDIA_CONFIG.captionRiseVh

export type ClipStage = {
  stage: Stage
  index: number
  media: Stage['media']
}

/** Source resolution tier: 540p for phones/standard displays, 1080p for retina. */
export type VideoTier = '540' | '1080'

/**
 * Pick a video tier by the device-pixel width the 16:9 clip actually spans in
 * its band — height-limited on wide screens, width-limited on phones. The 540p
 * source is 960px wide, so any span past 960 device pixels would UPSCALE it:
 * those screens get 1080p. At or under 960 the 540p file is pixel-for-pixel
 * identical to the 1080p one on that screen — the smaller download loses
 * nothing. Highest displayable quality everywhere, no wasted bytes.
 */
export function pickTier(): VideoTier {
  const dpr = Math.min(window.devicePixelRatio || 1, MEDIA_CONFIG.maxDpr)
  const clipDevWidth = Math.min(window.innerWidth, window.innerHeight * 1.3) * dpr
  return clipDevWidth > 960 ? '1080' : '540'
}

/** BASE-relative video path for a clip in a tier (anim/<chapter>/video/<tier>/<id>.mp4). */
export function tierSrc(src: string, tier: VideoTier): string {
  return tier === '540' ? src.replace('video/1080/', 'video/540/') : src
}

export interface MediaScrubberRefs {
  posters: MutableRefObject<Map<string, HTMLImageElement>>
  /** One shared canvas that renders the active clip's current frame. */
  canvas: MutableRefObject<HTMLCanvasElement | null>
  /** Preloaded scrub videos, keyed by clip id (only near-active clips are held). */
  videos: MutableRefObject<Map<string, HTMLVideoElement>>
  /** Chosen resolution tier ('540'/'1080'), set on mount. */
  tier: MutableRefObject<VideoTier>
  /** True when the layout anchors clips to the top of their band (mobile CSS). */
  alignTop: MutableRefObject<boolean>
  /** Last frame drawn (`id:time`) so we skip redundant redraws while idle/fading. */
  lastDraw: MutableRefObject<string>
  baseOp: MutableRefObject<Map<string, number>>
  /** Per-stage crossfade level (0 = poster shown, 1 = live canvas shown). */
  frameReveal: MutableRefObject<Map<string, number>>
  sceneRoot: MutableRefObject<HTMLElement | null>
  captionWrap: MutableRefObject<HTMLElement | null>
  canvasFade: MutableRefObject<number>
}

/** Local scroll progress through a section, 0 at top hit and 1 when scrolled out. */
export function localProgressFor(el: HTMLElement): number {
  const r = el.getBoundingClientRect()
  return clamp01((0 - r.top) / (r.height || 1))
}

export function setOpacity(el: HTMLElement, v: number): void {
  el.style.opacity = v > 0.985 ? '1' : v < 0.01 ? '0' : String(v)
}
