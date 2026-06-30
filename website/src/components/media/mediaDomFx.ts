import type { MutableRefObject } from 'react'
import { smooth, RISE_VH } from './mediaMath'
import { MEDIA_CONFIG } from './mediaConfig'

function queryCached(ref: MutableRefObject<HTMLElement | null>, selector: string): HTMLElement | null {
  if (!ref.current) ref.current = document.querySelector(selector)
  return ref.current
}

export function applySceneFade(
  active: number,
  reduced: boolean,
  act2Indices: ReadonlySet<number>,
  canvasFade: MutableRefObject<number>,
  sceneRootRef: MutableRefObject<HTMLElement | null>,
): void {
  const target = act2Indices.has(active) ? 0 : 1
  canvasFade.current += (target - canvasFade.current) * (reduced ? 1 : MEDIA_CONFIG.sceneFadeLerp)
  const root = queryCached(sceneRootRef, '[data-scene-root]')
  if (!root) return
  root.style.transition = 'none'
  root.style.opacity =
    canvasFade.current > 0.99 ? '1' : canvasFade.current < 0.01 ? '0' : String(canvasFade.current)
}

export function applyCaptionLift(
  activeLocal: number,
  reduced: boolean,
  captionWrapRef: MutableRefObject<HTMLElement | null>,
): void {
  const wrap = queryCached(captionWrapRef, '[data-caption-wrap]')
  if (!wrap) return
  const rise = activeLocal >= 0 && !reduced ? (1 - smooth(activeLocal, 0, 0.12)) * RISE_VH : 0
  wrap.style.transform = rise > 0.05 ? `translateY(${rise}vh)` : ''
}

export function applySubFade(activeLocal: number, reduced: boolean): void {
  const sub = document.querySelector('[data-caption-sub]') as HTMLElement | null
  if (!sub) return
  sub.style.opacity =
    activeLocal >= 0 && !reduced ? String(1 - smooth(activeLocal, 0.06, 0.24)) : ''
}

export function applyHeroScale(activeLocal: number, reduced: boolean): void {
  const heroTitle = document.querySelector('[data-hero-title]') as HTMLElement | null
  if (!heroTitle) return
  const p = reduced ? 0 : activeLocal >= 0 ? 1 - smooth(activeLocal, 0.0, 0.18) : 1
  heroTitle.style.setProperty('--hero-p', String(p))
}

export function applyScrollCue(activeLocal: number, reduced: boolean): void {
  const cue = document.querySelector('[data-scroll-cue]') as HTMLElement | null
  if (!cue) return
  cue.style.opacity = reduced ? '1' : String(1 - smooth(Math.max(activeLocal, 0), 0.0, 0.12))
}

export function resetDomFx(
  sceneRootRef: MutableRefObject<HTMLElement | null>,
  captionWrapRef: MutableRefObject<HTMLElement | null>,
): void {
  if (sceneRootRef.current) {
    sceneRootRef.current.style.opacity = ''
    sceneRootRef.current.style.transition = ''
  }
  if (captionWrapRef.current) captionWrapRef.current.style.transform = ''
}
