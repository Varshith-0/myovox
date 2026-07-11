/** Shared config, types, and scroll→scrub math for the MediaLayer subsystem. */
import type { MutableRefObject } from 'react'
import { type Stage } from '@/data/stages'
import { clamp01 } from '@/lib/num'
import type { ScrubEngine } from './scrubEngine'
import type { QualityController } from './quality'

/** Centralized tuning knobs for the frame scrubber. */
export const MEDIA_CONFIG = {
  /** Stages within this distance keep their poster mounted/visible. */
  visibilityDistance: 2,
  /** Preload a clip's frames/strip within this stage distance of active. */
  preloadDistance: 2,
  /** Release a clip's decoded frames beyond this stage distance. */
  releaseDistance: 3,
  /** Crossfade speed from poster → live canvas once a frame is drawable. */
  frameRevealLerp: 0.16,
  /** Show the "rendering…" overlay only after the active clip has been un-drawable
   *  this long — so a real stall triggers it but brief in-scroll gaps don't flash it. */
  loaderShowAfterMs: 200,
  /** Hard cap: auto-dismiss the overlay this long after it appears, no matter what. */
  loaderMaxMs: 1000,
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

export interface MediaScrubberRefs {
  posters: MutableRefObject<Map<string, HTMLImageElement>>
  /** One shared canvas that renders the active clip's current frame. */
  canvas: MutableRefObject<HTMLCanvasElement | null>
  /** The image-sequence scrub engine (null until the chapter manifest loads). */
  engine: MutableRefObject<ScrubEngine | null>
  /** True when the layout anchors clips to the top of their band (mobile CSS). */
  alignTop: MutableRefObject<boolean>
  baseOp: MutableRefObject<Map<string, number>>
  /** Per-stage crossfade level (0 = poster shown, 1 = live canvas shown). */
  frameReveal: MutableRefObject<Map<string, number>>
  sceneRoot: MutableRefObject<HTMLElement | null>
  captionWrap: MutableRefObject<HTMLElement | null>
  canvasFade: MutableRefObject<number>
  /** Adaptive-quality brain (null until the engine exists); told about stalls. */
  quality: MutableRefObject<QualityController | null>
}

/** Local scroll progress through a section, 0 at top hit and 1 when scrolled out. */
export function localProgressFor(el: HTMLElement): number {
  const r = el.getBoundingClientRect()
  return clamp01((0 - r.top) / (r.height || 1))
}

export function setOpacity(el: HTMLElement, v: number): void {
  el.style.opacity = v > 0.985 ? '1' : v < 0.01 ? '0' : String(v)
}
