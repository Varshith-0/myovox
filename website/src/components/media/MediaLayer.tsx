import { useEffect, useMemo, useRef } from 'react'
import { useStages } from '@/story/StagesContext'
import { useStore } from '@/store/useStore'
import { assetUrl } from '@/lib/asset'
import styles from './MediaLayer.module.css'
import { useMediaScrubber } from './useMediaScrubber'
import { releaseClipVideo } from './mediaLifecycle'
import { MEDIA_CONFIG, pickTier, setOpacity, type ClipStage, type VideoTier } from './core'

/**
 * The Act-2 clip scrubber. A fixed, full-viewport layer above the 3D canvas and
 * below the content/captions.
 *
 * Each Act-2 stage is a 3-beat segment driven by the section's local scroll:
 *   - land (local ≈ 0): a centred title card — the clip is hidden and the caption
 *     sits low/centred (no spoiler of the end).
 *   - scroll (local 0→1): the caption rises and the clip fades in and SCRUBS
 *     forward — the animation plays as you move.
 *   - rest: holds its current frame. Reduced motion shows a static poster.
 *
 * Rendering scrubs all-keyframe MP4s: each clip is one small video whose every
 * frame is independently seekable, so `currentTime` seeks are frame-exact and the
 * hardware decoder does all the work. Each RAF the active clip seeks to its
 * scroll-mapped time and the decoded frame is drawn to one shared <canvas> — the
 * picture stays glued to the scroll, and held memory is just the decoder's own
 * couple-of-frames buffer. The canvas fades in over the black layer as the video
 * becomes drawable; the clips begin from black, so the loading state is the start
 * (no end-frame poster spoiler). The final-frame poster is used only as the
 * reduced-motion static. Clips beyond the preload ring have their videos released.
 */

/** Matches the mobile CSS that anchors a contained clip to the top of its band. */
const TOP_ANCHOR_QUERY = '(max-width: 820px), (max-height: 600px), (max-aspect-ratio: 7/5)'

export function MediaLayer() {
  const stages = useStages()
  // Every stage is a scrubbed clip; derive the clip list (and the "all clips are
  // Act-2" index set) from the active stage list.
  const clipStages = useMemo<ClipStage[]>(
    () => stages.map((stage, index) => ({ stage, index, media: stage.media })),
    [stages],
  )
  const act2Indices = useMemo(() => new Set(clipStages.map((v) => v.index)), [clipStages])

  const reduced = useStore((s) => s.reducedMotion)
  // While narrating → lift the clip to free a band for the subtitles.
  const captionsMode = useStore((s) => s.subtitlesOn)
  const posters = useRef(new Map<string, HTMLImageElement>())
  const canvas = useRef<HTMLCanvasElement | null>(null)
  const videos = useRef(new Map<string, HTMLVideoElement>())
  const tier = useRef<VideoTier>('540')
  const alignTop = useRef(false)
  const lastDraw = useRef('')
  const baseOp = useRef(new Map<string, number>())
  const frameReveal = useRef(new Map<string, number>())
  const sceneRoot = useRef<HTMLElement | null>(null)
  const captionWrap = useRef<HTMLElement | null>(null)
  const canvasFade = useRef(1) // 1 = canvas visible (Act 1), 0 = hidden (Act 2)

  useMediaScrubber({
    reduced,
    clipStages,
    act2Indices,
    refs: {
      posters,
      canvas,
      videos,
      tier,
      alignTop,
      lastDraw,
      baseOp,
      frameReveal,
      sceneRoot,
      captionWrap,
      canvasFade,
    },
  })

  // Pick the resolution tier once, and release every scrub video on unmount so
  // a route change hands the decoders straight back to the browser.
  useEffect(() => {
    tier.current = pickTier()
    const cache = videos.current
    return () => {
      for (const id of [...cache.keys()]) releaseClipVideo(cache, id)
    }
  }, [])

  // Size the canvas backing store to its CSS box × DPR (capped), and track the
  // top-anchor breakpoint — both read here so the hot path never touches layout.
  useEffect(() => {
    const cv = canvas.current
    if (!cv) return
    const resize = () => {
      alignTop.current = window.matchMedia(TOP_ANCHOR_QUERY).matches
      const box = cv.getBoundingClientRect()
      const dpr = Math.min(window.devicePixelRatio || 1, MEDIA_CONFIG.maxDpr)
      const w = Math.round(box.width * dpr)
      const h = Math.round(box.height * dpr)
      if (w && h && (cv.width !== w || cv.height !== h)) {
        cv.width = w
        cv.height = h
        lastDraw.current = '' // backing resize clears the canvas — force a redraw
      }
    }
    const ro = new ResizeObserver(resize)
    ro.observe(cv)
    resize()
    return () => ro.disconnect()
  }, [captionsMode, reduced])

  useEffect(() => {
    baseOp.current.clear()
    frameReveal.current.clear()
    if (canvas.current) setOpacity(canvas.current, 0)
  }, [reduced])

  if (clipStages.length === 0) return null

  return (
    <div className={`${styles.layer} ${captionsMode ? styles.withCaptions : ''}`}>
      {/* A poster per stage — the clip's FINAL frame. Reduced motion shows it as
          the static content; normal mode blurs it into a fallback layer that only
          appears while the active clip's video has no drawable frame yet. */}
      {clipStages.map((vs) => {
        const fitClass = vs.media.fit === 'cover' ? styles.cover : styles.contain
        const fallbackClass = reduced ? '' : ` ${styles.posterFallback}`
        return (
          <div key={vs.stage.id} className={styles.stage}>
            <img
              ref={(el) => {
                if (el) posters.current.set(vs.stage.id, el)
                else posters.current.delete(vs.stage.id)
              }}
              src={assetUrl(vs.media.poster)}
              className={`${styles.media} ${fitClass}${fallbackClass}`}
              alt={vs.media.alt ?? vs.stage.caption}
            />
          </div>
        )
      })}
      {/* Normal mode: one shared canvas draws the active clip's scroll-mapped frame.
          It fades in over the black layer as frames decode — the clips begin from
          black, so the loading state IS the start (no final-frame poster spoiler). */}
      {!reduced && (
        <div className={styles.stage}>
          <canvas
            ref={(el) => {
              canvas.current = el
            }}
            className={styles.media}
            aria-hidden="true"
          />
        </div>
      )}
    </div>
  )
}
