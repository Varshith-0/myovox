/** Shared config, types, and scroll→scrub math for the MediaLayer subsystem. */
import type { MutableRefObject } from 'react'
import { type Stage } from '@/data/stages'
import { clamp01 } from '@/lib/num'

/** Centralized tuning knobs for the media scrubber. */
export const MEDIA_CONFIG = {
  visibilityDistance: 2,
  warmDistance: 4,
  seekEpsSeconds: 1 / 30,
  holdStart: 0.04,
  revealEnd: 0.16,
  captionRiseVh: 22,
  sceneFadeLerp: 0.26,
  stagePresenceLerp: 0.2,
} as const

export const HOLD = MEDIA_CONFIG.holdStart
export const REVEAL = MEDIA_CONFIG.revealEnd
export const RISE_VH = MEDIA_CONFIG.captionRiseVh

export type VideoStage = {
  stage: Stage
  index: number
  media: Stage['media']
}

export interface MediaScrubberRefs {
  posters: MutableRefObject<Map<string, HTMLImageElement>>
  videos: MutableRefObject<Map<string, HTMLVideoElement>>
  baseOp: MutableRefObject<Map<string, number>>
  shownOnce: MutableRefObject<Map<string, boolean>>
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
