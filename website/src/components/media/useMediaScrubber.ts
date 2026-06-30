import { useEffect } from 'react'
import { useStore } from '@/store/useStore'
import { HOLD, REVEAL, localProgressFor, setOpacity, smooth } from './mediaMath'
import { MEDIA_CONFIG } from './mediaConfig'
import { type MediaScrubberRefs, type MediaUrl, type VideoStage } from './mediaTypes'
import {
  detachVideoSrc,
  ensureImageSrc,
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
  mediaUrl: MediaUrl
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
  mediaUrl: MediaUrl,
): number {
  const img = refs.posters.current.get(stage.stage.id)
  if (!img) return -1

  const distance = Math.abs(stage.index - active)
  if (!updateStageVisibility(img, distance, VISIBLE_DISTANCE)) return -1

  const isActive = stage.index === active
  const local = localProgressFor(section)
  const bn = isActive ? 1 : 0
  refs.baseOp.current.set(stage.stage.id, bn)

  ensureImageSrc(img, mediaUrl(stage.media.poster))
  setOpacity(img, bn)
  return isActive ? local : -1
}

function runVideoStageFrame(
  refs: MediaScrubberRefs,
  stage: VideoStage,
  active: number,
  section: HTMLElement,
  mediaUrl: MediaUrl,
): number {
  const video = refs.videos.current.get(stage.stage.id)
  if (!video) return -1

  const distance = Math.abs(stage.index - active)
  setVideoPreload(video, distance)

  if (distance > WARM_DISTANCE) {
    updateStageVisibility(video, distance, VISIBLE_DISTANCE)
    detachVideoSrc(video)
    refs.baseOp.current.delete(stage.stage.id)
    refs.shownOnce.current.delete(stage.stage.id)
    return -1
  }

  const visible = updateStageVisibility(video, distance, VISIBLE_DISTANCE)
  ensureVideoSrc(video, mediaUrl(stage.media.src))
  if (!visible) return -1

  const isActive = stage.index === active
  const local = localProgressFor(section)

  const bTarget = isActive ? 1 : 0
  const bp = refs.baseOp.current.get(stage.stage.id) ?? 0
  const bn = bp + (bTarget - bp) * MEDIA_CONFIG.stagePresenceLerp
  refs.baseOp.current.set(stage.stage.id, bn)

  maybeSeekVideo(video, local)

  if (video.readyState >= 2) refs.shownOnce.current.set(stage.stage.id, true)
  const vis = refs.shownOnce.current.get(stage.stage.id) ? 1 : 0
  setOpacity(video, bn * smooth(local, HOLD, REVEAL) * vis)
  return isActive ? local : -1
}

function runMediaPhase(
  reduced: boolean,
  refs: MediaScrubberRefs,
  videoStages: readonly VideoStage[],
  active: number,
  mediaUrl: MediaUrl,
): FrameState {
  let activeLocal = -1
  for (const stage of videoStages) {
    const section = document.getElementById(stage.stage.id)
    if (!section) continue
    const local = reduced
      ? runReducedStageFrame(refs, stage, active, section, mediaUrl)
      : runVideoStageFrame(refs, stage, active, section, mediaUrl)
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
  mediaUrl,
  videoStages,
  act2Indices,
  refs,
}: UseMediaScrubberArgs): void {
  useEffect(() => {
    if (videoStages.length === 0) return
    let raf = 0
    const tick = () => {
      const active = useStore.getState().stageIndex
      const frame = runMediaPhase(reduced, refs, videoStages, active, mediaUrl)
      runFxPhase(reduced, act2Indices, refs, frame)

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      resetDomFx(refs.sceneRoot, refs.captionWrap)
    }
  }, [reduced, mediaUrl, videoStages, act2Indices, refs])
}
