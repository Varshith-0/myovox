import { useEffect } from 'react'
import { useStore } from '@/store/useStore'
import { smooth } from '@/lib/num'
import { assetUrl } from '@/lib/asset'
import {
  HOLD,
  REVEAL,
  MEDIA_CONFIG,
  localProgressFor,
  setOpacity,
  type MediaScrubberRefs,
  type VideoStage,
} from './core'
import {
  detachVideoSrc,
  ensureVideoSrc,
  maybeSeekVideo,
  setVideoPreload,
  updateStageVisibility,
  VISIBLE_DISTANCE,
  WARM_DISTANCE,
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
  videoStages: readonly VideoStage[]
  act2Indices: ReadonlySet<number>
  refs: MediaScrubberRefs
}

interface FrameState {
  active: number
  activeLocal: number
}

function runReducedStageFrame(
  refs: MediaScrubberRefs,
  stage: VideoStage,
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

function runVideoStageFrame(
  refs: MediaScrubberRefs,
  stage: VideoStage,
  active: number,
  section: HTMLElement,
): number {
  const id = stage.stage.id
  const video = refs.videos.current.get(id)
  const poster = refs.posters.current.get(id)
  if (!video) return -1

  const distance = Math.abs(stage.index - active)
  setVideoPreload(video, distance)

  if (distance > WARM_DISTANCE) {
    updateStageVisibility(video, distance, VISIBLE_DISTANCE)
    if (poster) updateStageVisibility(poster, distance, VISIBLE_DISTANCE)
    detachVideoSrc(video)
    refs.baseOp.current.delete(id)
    refs.videoReveal.current.delete(id)
    return -1
  }

  const visible = updateStageVisibility(video, distance, VISIBLE_DISTANCE)
  if (poster) updateStageVisibility(poster, distance, VISIBLE_DISTANCE)
  ensureVideoSrc(video, assetUrl(stage.media.src))
  if (!visible) return -1

  const isActive = stage.index === active
  const local = localProgressFor(section)

  const bTarget = isActive ? 1 : 0
  const bp = refs.baseOp.current.get(id) ?? 0
  const bn = bp + (bTarget - bp) * MEDIA_CONFIG.stagePresenceLerp
  refs.baseOp.current.set(id, bn)

  maybeSeekVideo(video, local)

  // Crossfade poster → video. The poster (final frame) covers the decode gap so a
  // cold jump shows the scene instantly instead of black; the video fades over it
  // once it can paint. Warm clips seed at 1 (no flash); cold clips seed at 0. The
  // reveal envelope keeps both hidden at the title-card beat (no ending spoiler).
  const ready = video.readyState >= 2
  const seed = refs.videoReveal.current.get(id) ?? (ready ? 1 : 0)
  const vn = seed + ((ready ? 1 : 0) - seed) * MEDIA_CONFIG.videoRevealLerp
  refs.videoReveal.current.set(id, vn)

  const envelope = bn * smooth(local, HOLD, REVEAL)
  setOpacity(video, envelope * vn)
  if (poster) setOpacity(poster, envelope * (1 - vn))
  return isActive ? local : -1
}

function runMediaPhase(
  reduced: boolean,
  refs: MediaScrubberRefs,
  videoStages: readonly VideoStage[],
  active: number,
): FrameState {
  let activeLocal = -1
  for (const stage of videoStages) {
    const section = document.getElementById(stage.stage.id)
    if (!section) continue
    const local = reduced
      ? runReducedStageFrame(refs, stage, active, section)
      : runVideoStageFrame(refs, stage, active, section)
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

/** Hot-path RAF loop that scrubs active stage media and applies title-card FX. */
export function useMediaScrubber({
  reduced,
  videoStages,
  act2Indices,
  refs,
}: UseMediaScrubberArgs): void {
  useEffect(() => {
    if (videoStages.length === 0) return
    let raf = 0
    const tick = () => {
      const active = useStore.getState().stageIndex
      const frame = runMediaPhase(reduced, refs, videoStages, active)
      runFxPhase(reduced, act2Indices, refs, frame)

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      resetDomFx(refs.sceneRoot, refs.captionWrap)
    }
  }, [reduced, videoStages, act2Indices, refs])
}
