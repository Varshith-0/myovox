import type { MutableRefObject } from 'react'
import { smooth } from '@/lib/num'
import { RISE_VH, MEDIA_CONFIG } from './core'

function queryCached(ref: MutableRefObject<HTMLElement | null>, selector: string): HTMLElement | null {
  if (!ref.current || !ref.current.isConnected) ref.current = document.querySelector(selector)
  return ref.current
}

/* These run every RAF; a fresh document.querySelector per frame was measurable
   on low-end devices. Cached until the node leaves the DOM (stage remounts). */
const domCache = new Map<string, HTMLElement | null>()
function queryFrame(selector: string): HTMLElement | null {
  const hit = domCache.get(selector)
  if (hit && hit.isConnected) return hit
  const el = document.querySelector<HTMLElement>(selector)
  domCache.set(selector, el)
  return el
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
  const sub = queryFrame('[data-caption-sub]')
  if (!sub) return
  sub.style.opacity =
    activeLocal >= 0 && !reduced ? String(1 - smooth(activeLocal, 0.06, 0.24)) : ''
}

export function applyHeroScale(activeLocal: number, reduced: boolean): void {
  const heroTitle = queryFrame('[data-hero-title]')
  if (!heroTitle) return
  const p = reduced ? 0 : activeLocal >= 0 ? 1 - smooth(activeLocal, 0.0, 0.18) : 1
  heroTitle.style.setProperty('--hero-p', String(p))
}

export function applyScrollCue(activeLocal: number, reduced: boolean): void {
  const cue = queryFrame('[data-scroll-cue]')
  if (!cue) return
  cue.style.opacity = reduced ? '1' : String(1 - smooth(Math.max(activeLocal, 0), 0.0, 0.12))
}

export function resetDomFx(
  sceneRootRef: MutableRefObject<HTMLElement | null>,
  captionWrapRef: MutableRefObject<HTMLElement | null>,
): void {
  domCache.clear()
  if (sceneRootRef.current) {
    sceneRootRef.current.style.opacity = ''
    sceneRootRef.current.style.transition = ''
  }
  if (captionWrapRef.current) captionWrapRef.current.style.transform = ''
}
