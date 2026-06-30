import { useEffect, useRef } from 'react'
import { STAGES, stageMedia } from '@/data/stages'
import { useStore } from '@/store/useStore'
import styles from './MediaLayer.module.css'
import { useMediaScrubber } from './useMediaScrubber'
import { type VideoStage } from './mediaTypes'

/**
 * The Act-2 video scrubber. A fixed, full-viewport layer above the 3D canvas and
 * below the content/captions.
 *
 * Each Act-2 stage is a 3-beat segment driven by the section's local scroll:
 *   - land (local ≈ 0): a centred title card — just the badge + headline. The
 *     clip is hidden and the caption sits low/centred (no spoiler of the end).
 *   - scroll (local 0→1): the caption rises to the top and the clip fades in and
 *     SCRUBS forward — the animation actually plays as you move.
 *   - rest: the <video> simply holds its current frame (no jump to the final
 *     frame). Reduced motion shows a static poster (the composed final frame).
 *
 * The active stage's canvas is faded to 0 so the dispersed point-cloud head can't
 * ghost through. Visibility is keyed to the store's active stageIndex (reliable),
 * far stages are display:none (the compositor would otherwise juggle 19 videos +
 * the canvas), and src is loaded only near the active stage.
 */

const BASE = import.meta.env.BASE_URL
// Cache-bust the clips/posters: their filenames are stable, so a re-rendered
// clip would otherwise keep serving from the browser cache. In dev, bust per
// page-load (always see the latest render while iterating); in prod, bust per
// build (cacheable, but a deploy invalidates it).
const ASSET_VER = import.meta.env.DEV ? String(Date.now()) : __BUILD_ID__
const mediaUrl = (p: string) => `${BASE}${p.replace(/^\//, '')}?v=${ASSET_VER}`

const VIDEO_STAGES: VideoStage[] = STAGES.flatMap((stage, index) => {
  const m = stageMedia(stage)
  return m.kind === 'video' ? [{ stage, index, media: m }] : []
})

const ACT2_INDICES = new Set(VIDEO_STAGES.map((v) => v.index))

export function MediaLayer() {
  const reduced = useStore((s) => s.reducedMotion)
  // While narrating (armed + playing) → lift the clip to free a band at the
  // bottom for the subtitles.
  const captionsMode = useStore((s) => s.subtitlesOn)
  const posters = useRef(new Map<string, HTMLImageElement>())
  const videos = useRef(new Map<string, HTMLVideoElement>())
  const baseOp = useRef(new Map<string, number>())
  const shownOnce = useRef(new Map<string, boolean>())
  const sceneRoot = useRef<HTMLElement | null>(null)
  const captionWrap = useRef<HTMLElement | null>(null)
  const canvasFade = useRef(1) // 1 = canvas visible (Act 1), 0 = hidden (Act 2)

  useMediaScrubber({
    reduced,
    mediaUrl,
    videoStages: VIDEO_STAGES,
    act2Indices: ACT2_INDICES,
    refs: {
      posters,
      videos,
      baseOp,
      shownOnce,
      sceneRoot,
      captionWrap,
      canvasFade,
    },
  })

  useEffect(() => {
    baseOp.current.clear()
    shownOnce.current.clear()
  }, [reduced])

  if (VIDEO_STAGES.length === 0) return null

  return (
    <div className={`${styles.layer} ${captionsMode ? styles.withCaptions : ''}`}>
      {VIDEO_STAGES.map((vs) => {
        const fitClass = vs.media.fit === 'cover' ? styles.cover : styles.contain
        return (
          <div key={vs.stage.id} className={styles.stage}>
            {reduced ? (
              <img
                ref={(el) => {
                  if (el) posters.current.set(vs.stage.id, el)
                  else posters.current.delete(vs.stage.id)
                }}
                className={`${styles.media} ${fitClass}`}
                alt={vs.media.alt ?? vs.stage.caption}
              />
            ) : (
              <video
                ref={(el) => {
                  if (el) videos.current.set(vs.stage.id, el)
                  else videos.current.delete(vs.stage.id)
                }}
                className={`${styles.media} ${fitClass}`}
                muted
                playsInline
                preload="auto"
                aria-hidden="true"
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
