import { useEffect, useRef } from 'react'
import { useStore } from '@/store/useStore'
import { smooth } from '@/lib/num'
import {
  HOLD,
  REVEAL,
  MEDIA_CONFIG,
  localProgressFor,
  setOpacity,
  tierSrc,
  type MediaScrubberRefs,
  type ClipStage,
} from './core'
import {
  drawFrame,
  ensureClipVideo,
  releaseClipVideo,
  scrubVideo,
  updateStageVisibility,
  videoDrawable,
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
  const isActive = stage.index === active
  const posterImg = refs.posters.current.get(id)
  const posterShown = posterImg
    ? updateStageVisibility(posterImg, distance, VISIBLE_DISTANCE)
    : false

  // Drop clips beyond the ring entirely; re-seed on cold re-entry (no stale flash).
  if (distance > RELEASE_DISTANCE) {
    releaseClipVideo(refs.videos.current, id)
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
    // Near, not active → start fetching the clip so entering it is instant.
    if (distance <= PRELOAD_DISTANCE) {
      ensureClipVideo(refs.videos.current, id, tierSrc(stage.media.src, refs.tier.current))
    }
    return NOT_READY
  }

  const local = localProgressFor(section)
  // Seek the hardware decoder to the scroll-mapped frame; seeks coalesce, so
  // however fast the scroll moves we always land on the latest target.
  const video = ensureClipVideo(refs.videos.current, id, tierSrc(stage.media.src, refs.tier.current))
  scrubVideo(video, local)

  const envelope = bn * smooth(local, HOLD, REVEAL)

  // Draw the decoder's current frame to the shared canvas — a GPU-side copy,
  // nothing decodes on the main thread, so the draw can never stall the scroll.
  const canvas = refs.canvas.current
  let drew = false
  if (canvas && videoDrawable(video)) {
    const key = `${id}:${video.currentTime.toFixed(3)}`
    if (refs.lastDraw.current !== key) {
      drawFrame(canvas, video, stage.media.fit, refs.alignTop.current)
      refs.lastDraw.current = key
    }
    drew = true
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
  // Blurred final-frame ambience while the video can't draw yet — visual content
  // instead of a bare title on black; fades out as the live canvas reveals.
  if (posterShown && posterImg) setOpacity(posterImg, envelope * (1 - cn))

  // Past the title card but the video has no drawable frame yet (still fetching
  // after a fast jump) → signals the "rendering…" overlay.
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
