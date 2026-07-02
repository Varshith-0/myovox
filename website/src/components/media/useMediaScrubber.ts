import { useEffect } from 'react'
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
  ensureClipFrames,
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

/** Preload near clips, release far ones; hysteresis avoids boundary thrash. */
function updateFramePreload(refs: MediaScrubberRefs, id: string, count: number, distance: number): void {
  if (count <= 0) return
  if (distance <= PRELOAD_DISTANCE) {
    ensureClipFrames(refs.frames.current, id, count, refs.tier.current)
  } else if (distance > RELEASE_DISTANCE) {
    releaseClipFrames(refs.frames.current, id)
    // Reset crossfade/presence so a cold re-entry re-seeds fresh (no stale flash).
    refs.frameReveal.current.delete(id)
    refs.baseOp.current.delete(id)
  }
}

function runClipStageFrame(
  refs: MediaScrubberRefs,
  stage: ClipStage,
  active: number,
  section: HTMLElement,
): number {
  const id = stage.stage.id
  const distance = Math.abs(stage.index - active)
  const count = refs.manifest.current?.clips[id] ?? 0

  updateFramePreload(refs, id, count, distance)

  const poster = refs.posters.current.get(id)
  const visible = poster ? updateStageVisibility(poster, distance, VISIBLE_DISTANCE) : false

  // Presence lerp smooths the stage handoff at boundaries.
  const isActive = stage.index === active
  const bp = refs.baseOp.current.get(id) ?? 0
  const bn = bp + ((isActive ? 1 : 0) - bp) * MEDIA_CONFIG.stagePresenceLerp
  refs.baseOp.current.set(id, bn)

  if (!isActive) {
    if (poster && visible) setOpacity(poster, bn)
    return -1
  }

  const local = localProgressFor(section)
  const envelope = bn * smooth(local, HOLD, REVEAL)

  // Draw the exact scroll-mapped frame to the shared canvas. Frames just ahead are
  // decoded off the main thread first, so drawImage is a pure GPU upload and never
  // stalls on a synchronous decode — that stall is the scrub jank, worst at 2x.
  const canvas = refs.canvas.current
  const clip = refs.frames.current.get(id)
  let drew = false
  if (canvas && clip && count > 0) {
    const idx = Math.min(count - 1, Math.max(0, Math.round(local * (count - 1))))
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

  // Crossfade: poster is the base (always at envelope); the canvas fades in over it
  // once frames draw. Seeded so a warm clip shows no flash and a cold one shows the
  // poster instantly. The reveal envelope keeps both hidden at the title-card beat.
  const cp = refs.frameReveal.current.get(id) ?? (drew ? 1 : 0)
  const cn = cp + ((drew ? 1 : 0) - cp) * MEDIA_CONFIG.frameRevealLerp
  refs.frameReveal.current.set(id, cn)

  if (poster && visible) setOpacity(poster, envelope)
  if (canvas) setOpacity(canvas, envelope * cn)
  return local
}

function runMediaPhase(
  reduced: boolean,
  refs: MediaScrubberRefs,
  clipStages: readonly ClipStage[],
  active: number,
): FrameState {
  let activeLocal = -1
  for (const stage of clipStages) {
    const section = document.getElementById(stage.stage.id)
    if (!section) continue
    const local = reduced
      ? runReducedStageFrame(refs, stage, active, section)
      : runClipStageFrame(refs, stage, active, section)
    if (local >= 0) activeLocal = local
  }
  return { active, activeLocal }
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
  useEffect(() => {
    if (clipStages.length === 0) return
    let raf = 0
    const tick = () => {
      const active = useStore.getState().stageIndex
      const frame = runMediaPhase(reduced, refs, clipStages, active)
      runFxPhase(reduced, act2Indices, refs, frame)

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      resetDomFx(refs.sceneRoot, refs.captionWrap)
    }
  }, [reduced, clipStages, act2Indices, refs])
}
