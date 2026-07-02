import { useEffect, useRef } from 'react'
import { useStore } from '@/store/useStore'
import { smooth } from '@/lib/num'
import {
  HOLD,
  REVEAL,
  MEDIA_CONFIG,
  localProgressFor,
  setOpacity,
  type MediaScrubberRefs,
  type ClipStage,
} from './core'
import {
  decodeAheadClip,
  drawFrame,
  ensureClipWindow,
  releaseClipFrames,
  updateStageVisibility,
  VISIBLE_DISTANCE,
  PRELOAD_DISTANCE,
  RELEASE_DISTANCE,
} from './mediaLifecycle'
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
  if (!updateStageVisibility(img, distance, VISIBLE_DISTANCE)) return -1

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
  const count = refs.manifest.current?.clips[id] ?? 0
  const isActive = stage.index === active

  // Drop clips beyond the ring entirely; re-seed on cold re-entry (no stale flash).
  if (distance > RELEASE_DISTANCE) {
    releaseClipFrames(refs.frames.current, id)
    refs.frameReveal.current.delete(id)
    refs.baseOp.current.delete(id)
    return NOT_READY
  }

  // Presence lerp smooths the stage handoff at boundaries.
  const bp = refs.baseOp.current.get(id) ?? 0
  const bn = bp + ((isActive ? 1 : 0) - bp) * MEDIA_CONFIG.stagePresenceLerp
  refs.baseOp.current.set(id, bn)

  if (!isActive) {
    // Near, not active → preload the opening window so entering at the top is instant.
    if (count > 0 && distance <= PRELOAD_DISTANCE) {
      ensureClipWindow(refs.frames.current, id, count, refs.tier.current, 0)
    }
    return NOT_READY
  }

  const local = localProgressFor(section)
  const idx = count > 0 ? Math.min(count - 1, Math.max(0, Math.round(local * (count - 1)))) : 0
  // Load a bounded window around the current frame, current frame first — so a
  // fast-scroll stop paints immediately and held memory stays flat on mobile.
  if (count > 0) ensureClipWindow(refs.frames.current, id, count, refs.tier.current, idx)

  const envelope = bn * smooth(local, HOLD, REVEAL)

  // Draw the exact scroll-mapped frame to the shared canvas. Frames just ahead are
  // decoded off the main thread first, so drawImage is a pure GPU upload and never
  // stalls on a synchronous decode — that stall is the scrub jank, worst at 2x.
  const canvas = refs.canvas.current
  const clip = refs.frames.current.get(id)
  let drew = false
  if (canvas && clip && count > 0) {
    decodeAheadClip(clip, idx, MEDIA_CONFIG.decodeAhead)
    const img = clip.images[idx]
    if (img && img.complete && img.naturalWidth > 0) {
      const key = `${id}:${idx}`
      if (refs.lastDraw.current !== key) {
        drawFrame(canvas, img, stage.media.fit, refs.alignTop.current)
        refs.lastDraw.current = key
      }
      drew = true
    }
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

  // Past the title card but the current frame still can't be drawn (fast-scrolled
  // past the preload window) → signals the "rendering…" overlay.
  const notReady = count > 0 && local > REVEAL && !drew
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
  const notReadyFrames = useRef(0)
  const lastLoading = useRef(false)

  useEffect(() => {
    if (clipStages.length === 0) return
    let raf = 0
    // Write the "rendering…" flag to the store only when it flips (never per-frame).
    const syncLoading = (loading: boolean) => {
      if (loading === lastLoading.current) return
      lastLoading.current = loading
      useStore.getState().setMediaLoading(loading)
    }
    const tick = () => {
      const active = useStore.getState().stageIndex
      const frame = runMediaPhase(reduced, refs, clipStages, active)
      runFxPhase(reduced, act2Indices, refs, frame)

      // Debounced "rendering…" signal → store (on change only, never per-frame spam).
      notReadyFrames.current = frame.activeNotReady ? notReadyFrames.current + 1 : 0
      syncLoading(notReadyFrames.current > MEDIA_CONFIG.loadDebounceFrames)

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      resetDomFx(refs.sceneRoot, refs.captionWrap)
      notReadyFrames.current = 0
      syncLoading(false)
    }
  }, [reduced, clipStages, act2Indices, refs])
}
