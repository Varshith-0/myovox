/** Shared config, types, and scroll→scrub math for the MediaLayer subsystem. */
import type { MutableRefObject } from 'react'
import { type Stage } from '@/data/stages'
import { clamp01 } from '@/lib/num'

/** Centralized tuning knobs for the frame scrubber. */
export const MEDIA_CONFIG = {
  /** Stages within this distance keep their poster mounted/visible. */
  visibilityDistance: 2,
  /** Preload a clip's full frame sequence within this stage distance of active. */
  preloadDistance: 2,
  /** Release a clip's frames (free memory) beyond this stage distance. */
  releaseDistance: 3,
  /** Crossfade speed from poster → live canvas once frames are drawable. */
  frameRevealLerp: 0.16,
  /** Decode this many upcoming frames off the main thread so drawImage never
   *  blocks on a synchronous decode (the source of scrub jank, worst at 2x). */
  decodeAhead: 10,
  /** Cap the canvas backing-store scale so long clips stay memory-safe. */
  maxDpr: 2,
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

/** A clip's preloaded frame images, indexed 0..count-1. */
export interface FrameClip {
  images: HTMLImageElement[]
  count: number
  /** Indices already asked to decode (so we request each off-thread decode once). */
  requested: Set<number>
}

/** A DPR tier folder name under frames/ (e.g. '1x' = standard, '2x' = retina). */
export type FrameTier = string

/** frames/manifest.json: frame counts per clip + the DPR tiers available. */
export interface FrameManifest {
  fps: number
  /** Tier folder → source height, e.g. { '1x': 540, '2x': 1080 }. */
  tiers: Record<FrameTier, number>
  clips: Record<string, number>
}

/**
 * Pick a frame tier by screen density. Large/retina screens get the hi-res set;
 * phones and standard displays stay on the light set (memory- and bandwidth-safe).
 * Keyed on the device-pixel width the 16:9 clip actually spans in its band —
 * height-limited on wide screens, width-limited on phones — not raw DPR, so a
 * high-DPR phone (small clip) correctly stays 1x.
 */
export function pickTier(manifest: FrameManifest): FrameTier {
  const tiers = Object.keys(manifest.tiers)
  if (tiers.length === 0) return '1x'
  const dpr = Math.min(window.devicePixelRatio || 1, MEDIA_CONFIG.maxDpr)
  const clipDevWidth = Math.min(window.innerWidth, window.innerHeight * 1.3) * dpr
  if (clipDevWidth > 1100 && manifest.tiers['2x']) return '2x'
  return manifest.tiers['1x'] ? '1x' : tiers[0]
}

export interface MediaScrubberRefs {
  posters: MutableRefObject<Map<string, HTMLImageElement>>
  /** One shared canvas that renders the active clip's current frame. */
  canvas: MutableRefObject<HTMLCanvasElement | null>
  /** Loaded frame sequences, keyed by clip id (only near-active clips are held). */
  frames: MutableRefObject<Map<string, FrameClip>>
  /** Frame counts per clip, or null until the manifest loads. */
  manifest: MutableRefObject<FrameManifest | null>
  /** Chosen DPR tier ('1x'/'2x'), set once the manifest loads. */
  tier: MutableRefObject<FrameTier>
  /** True when the layout anchors clips to the top of their band (mobile CSS). */
  alignTop: MutableRefObject<boolean>
  /** Last frame drawn (`id:idx`) so we skip redundant redraws while idle/fading. */
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

/** BASE-relative path for a 1-indexed, 4-padded frame webp in a DPR tier. */
export function frameUrlPath(tier: FrameTier, id: string, index: number): string {
  return `anim/frames/${tier}/${id}/${String(index + 1).padStart(4, '0')}.webp`
}
