import { useEffect, useRef } from 'react'
import { useStore } from '@/store/useStore'
import { smooth } from '@/lib/num'
import { netMeter } from './quality'
import {
  HOLD,
  REVEAL,
  MEDIA_CONFIG,
  localProgressFor,
  setOpacity,
  type MediaScrubberRefs,
  type ClipStage,
} from './core'
import { updateStageVisibility } from './mediaLifecycle'
import {
  applyCaptionLift,
  applyHeroScale,
  applySceneFade,
  applyScrollCue,
  applySubFade,
  resetDomFx,
} from './mediaDomFx'

interface UseMediaScrubberArgs {
  reduced: boolean
  clipStages: readonly ClipStage[]
  act2Indices: ReadonlySet<number>
  refs: MediaScrubberRefs
}

interface FrameState {
  active: number
  activeLocal: number
  activeNotReady: boolean
}

/** Reduced motion: static poster only, no scrubbing. */
function runReducedStageFrame(
  refs: MediaScrubberRefs,
  stage: ClipStage,
  active: number,
  section: HTMLElement,
): number {
  const img = refs.posters.current.get(stage.stage.id)
  if (!img) return -1

  const distance = Math.abs(stage.index - active)
  if (!updateStageVisibility(img, distance, MEDIA_CONFIG.visibilityDistance)) return -1

  const isActive = stage.index === active
  const local = localProgressFor(section)
  const bn = isActive ? 1 : 0
  refs.baseOp.current.set(stage.stage.id, bn)

  setOpacity(img, bn)
  return isActive ? local : -1
}

interface ClipFrameResult {
  local: number
  /** Active clip past the title card but its current frame can't be drawn yet. */
  notReady: boolean
}

const NOT_READY: ClipFrameResult = { local: -1, notReady: false }

function runClipStageFrame(
  refs: MediaScrubberRefs,
  stage: ClipStage,
  active: number,
  section: HTMLElement,
): ClipFrameResult {
  const id = stage.stage.id
  const distance = Math.abs(stage.index - active)
  const isActive = stage.index === active
  const posterImg = refs.posters.current.get(id)
  const posterShown = posterImg
    ? updateStageVisibility(posterImg, distance, MEDIA_CONFIG.visibilityDistance)
    : false

  // Beyond the ring the engine has already freed the clip's frames (setWindow);
  // drop the crossfade state too so cold re-entry re-seeds (no stale flash).
  if (distance > MEDIA_CONFIG.releaseDistance) {
    refs.frameReveal.current.delete(id)
    refs.baseOp.current.delete(id)
    return NOT_READY
  }

  // Presence lerp smooths the stage handoff at boundaries.
  const bp = refs.baseOp.current.get(id) ?? 0
  const bn = bp + ((isActive ? 1 : 0) - bp) * MEDIA_CONFIG.stagePresenceLerp
  refs.baseOp.current.set(id, bn)

  if (!isActive) {
    if (posterShown && posterImg) setOpacity(posterImg, 0)
    // Neighbour prefetch is the engine's job (setWindow on stage change).
    return NOT_READY
  }

  const local = localProgressFor(section)
  const envelope = bn * smooth(local, HOLD, REVEAL)

  // Draw the scroll-mapped pre-decoded frame to the shared canvas. The tiny
  // always-loaded strip guarantees something is drawable almost immediately,
  // so `drawn` is false only for the sub-second before the strip decodes.
  const canvas = refs.canvas.current
  const engine = refs.engine.current
  const ctx = canvas?.getContext('2d')
  let drew = false
  if (canvas && ctx && engine) {
    drew = engine.drawFrame(
      ctx, id, local, canvas.width, canvas.height,
      stage.media.fit ?? 'contain', refs.alignTop.current,
    ).drawn
  }

  // Fade the canvas in over the black layer, latched upward: once real frames draw
  // we keep it faded in, so a momentarily un-decoded frame can't drop back to black
  // mid-scrub. Seeded so a warm clip shows no flash. The reveal envelope keeps it
  // hidden at the title-card beat; the clips start from black, so the load state is
  // just the black layer — the animation's actual beginning, no end-frame spoiler.
  const cp = refs.frameReveal.current.get(id) ?? (drew ? 1 : 0)
  const cn = drew ? cp + (1 - cp) * MEDIA_CONFIG.frameRevealLerp : cp
  refs.frameReveal.current.set(id, cn)

  if (canvas) setOpacity(canvas, envelope * cn)
  // Blurred final-frame ambience while nothing can draw yet — visual content
  // instead of a bare title on black; fades out as the live canvas reveals.
  if (posterShown && posterImg) setOpacity(posterImg, envelope * (1 - cn))

  // Past the title card but not even the strip is drawable yet (first hit after
  // a fast jump) → signals the "rendering…" overlay.
  const notReady = local > REVEAL && !drew
  return { local, notReady }
}

function runMediaPhase(
  reduced: boolean,
  refs: MediaScrubberRefs,
  clipStages: readonly ClipStage[],
  active: number,
): FrameState {
  let activeLocal = -1
  let activeNotReady = false
  for (const stage of clipStages) {
    const section = document.getElementById(stage.stage.id)
    if (!section) continue
    if (reduced) {
      const local = runReducedStageFrame(refs, stage, active, section)
      if (local >= 0) activeLocal = local
    } else {
      const { local, notReady } = runClipStageFrame(refs, stage, active, section)
      if (local >= 0) {
        activeLocal = local
        activeNotReady = notReady
      }
    }
  }
  return { active, activeLocal, activeNotReady }
}

function runFxPhase(
  reduced: boolean,
  act2Indices: ReadonlySet<number>,
  refs: MediaScrubberRefs,
  frame: FrameState,
): void {
  applySceneFade(frame.active, reduced, act2Indices, refs.canvasFade, refs.sceneRoot)
  applyCaptionLift(frame.activeLocal, reduced, refs.captionWrap)
  applySubFade(frame.activeLocal, reduced)
  applyHeroScale(frame.activeLocal, reduced)
  applyScrollCue(frame.activeLocal, reduced)
}

/** Hot-path RAF loop that scrubs the active clip's frames and applies title-card FX. */
export function useMediaScrubber({
  reduced,
  clipStages,
  act2Indices,
  refs,
}: UseMediaScrubberArgs): void {
  const lastLoading = useRef(false)

  useEffect(() => {
    if (clipStages.length === 0) return
    let raf = 0
    const orderedIds = clipStages.map((s) => s.stage.id)
    // Cold-path window: preload/release rings move only on stage change (or when
    // the engine finishes its async setup), never per-frame.
    let windowEngine: unknown = null
    let windowActive = -1
    // Loader shows after a real stall and stays up until a frame actually draws —
    // on a cold first visit even the strip takes seconds to arrive, and a bare
    // title on black reads as broken.
    let stallStart = 0
    // Write the "rendering…" flag to the store only when it flips (never per-frame).
    // When it flips ON, also diagnose why (weak pipe vs outran the preloader) and
    // let the quality controller demote if the network is the culprit.
    // Recent stall onsets: the loader re-appearing repeatedly within seconds is
    // the surest sign of a starved pipe — even before the meter has samples
    // (cold loads on slow networks stall before any fetch completes).
    let stallTimes: number[] = []
    const syncLoading = (loading: boolean) => {
      const flipped = loading !== lastLoading.current
      if (!flipped && !loading) return
      lastLoading.current = loading
      const state = useStore.getState()
      if (loading) {
        const now = performance.now()
        if (flipped) {
          stallTimes = [...stallTimes.filter((t) => now - t < 6000), now]
          refs.quality.current?.onStall()
        }
        // Re-evaluated while visible: slow samples (or a second stall in quick
        // succession) upgrade the message to the honest "weak connection".
        const network = netMeter.networkBound(state.activeQuality) || stallTimes.length >= 2
        state.setMediaLoading(true, network ? 'network' : 'preparing') // store dedupes
      } else {
        state.setMediaLoading(false)
      }
    }
    const tick = () => {
      const active = useStore.getState().stageIndex
      const engine = refs.engine.current
      if (engine && (engine !== windowEngine || active !== windowActive)) {
        engine.setWindow(active, orderedIds)
        windowEngine = engine
        windowActive = active
      }
      const frame = runMediaPhase(reduced, refs, clipStages, active)
      runFxPhase(reduced, act2Indices, refs, frame)

      if (frame.activeNotReady) {
        if (!stallStart) stallStart = performance.now()
      } else {
        stallStart = 0
      }
      const stalledMs = stallStart ? performance.now() - stallStart : 0
      syncLoading(stalledMs > MEDIA_CONFIG.loaderShowAfterMs)

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      resetDomFx(refs.sceneRoot, refs.captionWrap)
      syncLoading(false)
    }
  }, [reduced, clipStages, act2Indices, refs])
}
