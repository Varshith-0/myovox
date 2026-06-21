import { useGSAP } from '@gsap/react'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import type { RefObject } from 'react'
import { scroll } from '@/store/scroll'
import { useStore } from '@/store/useStore'
import { STAGES, STAGE_COUNT } from '@/data/stages'

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

/**
 * Fractional stage index (0..STAGE_COUNT-1) read from the live DOM rects, so the
 * mapping stays correct even when stages have different heights (Act-2 video
 * stages are taller). The section whose top has crossed the viewport top is the
 * current one; the fraction scrolled into it eases toward the next stage. This
 * is then normalized into `scroll.progress` so the existing `sampleScene` /
 * `stageIndexFor` (which expect a 0..1 over the stages) keep working unchanged.
 */
function stageFloatFromDom(): number {
  for (let i = 0; i < STAGE_COUNT; i++) {
    const el = document.getElementById(STAGES[i].id)
    if (!el) continue
    const r = el.getBoundingClientRect()
    if (r.top <= 0 && r.bottom > 0) return i + clamp01(-r.top / (r.height || 1))
    if (r.top > 0) return i // viewport top hasn't reached section i yet
  }
  return STAGE_COUNT - 1
}

/**
 * The one ScrollTrigger that turns the story container's scroll into a single
 * normalized `progress` (0→1). It writes that value into the hot-path
 * {@link scroll} module every frame (no React churn) and pushes the nearest
 * stage index into the store (drives the active caption / progress rail).
 *
 * This is the *only* place DOM scroll touches the app — everything downstream
 * reads `scroll.progress`, never the DOM, keeping the scene fully decoupled.
 *
 * @param ref the tall story container spanning all stage sections.
 */
export function useScrollProgress(ref: RefObject<HTMLElement | null>): void {
  const setStageIndex = useStore((s) => s.setStageIndex)

  useGSAP(
    () => {
      const el = ref.current
      if (!el) return
      const trigger = ScrollTrigger.create({
        trigger: el,
        start: 'top top',
        end: 'bottom bottom',
        scrub: true,
        onUpdate: () => {
          // Section-aware progress (robust to per-stage scrollVh). The continuous
          // value drives the 3D scene blend; the *active* stage is the section you
          // are currently in (floor, not nearest) so the caption/clip don't flip to
          // the next stage halfway through a tall Act-2 section.
          const f = stageFloatFromDom()
          scroll.progress = f / Math.max(1, STAGE_COUNT - 1)
          setStageIndex(Math.min(STAGE_COUNT - 1, Math.floor(f)))
        },
      })
      return () => trigger.kill()
    },
    { scope: ref, dependencies: [setStageIndex] },
  )
}
