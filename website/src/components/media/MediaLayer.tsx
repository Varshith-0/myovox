import { useEffect, useRef } from 'react'
import { STAGES } from '@/data/stages'
import { useStore } from '@/store/useStore'
import { assetUrl } from '@/lib/asset'
import styles from './MediaLayer.module.css'
import { useMediaScrubber } from './useMediaScrubber'
import {
  MEDIA_CONFIG,
  pickTier,
  setOpacity,
  type ClipStage,
  type FrameClip,
  type FrameManifest,
  type FrameTier,
} from './core'

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
 * Rendering is frame-perfect: every clip is a preloaded WebP frame sequence, and
 * the active clip's current frame is drawn to one shared <canvas> each RAF — a
 * synchronous drawImage with no video decoder on the hot path, so the picture is
 * glued to the scroll however fast it moves. The per-stage poster is the base
 * layer: shown instantly on a cold jump while that clip's frames preload, then the
 * canvas crossfades over it. Far stages are display:none and their frames released.
 */

const CLIP_STAGES: ClipStage[] = STAGES.map((stage, index) => ({ stage, index, media: stage.media }))

const ACT2_INDICES = new Set(CLIP_STAGES.map((v) => v.index))

/** Matches the mobile CSS that anchors a contained clip to the top of its band. */
const TOP_ANCHOR_QUERY = '(max-width: 820px), (max-height: 600px), (max-aspect-ratio: 7/5)'

export function MediaLayer() {
  const reduced = useStore((s) => s.reducedMotion)
  // While narrating → lift the clip to free a band for the subtitles.
  const captionsMode = useStore((s) => s.subtitlesOn)
  const posters = useRef(new Map<string, HTMLImageElement>())
  const canvas = useRef<HTMLCanvasElement | null>(null)
  const frames = useRef(new Map<string, FrameClip>())
  const manifest = useRef<FrameManifest | null>(null)
  const tier = useRef<FrameTier>('1x')
  const alignTop = useRef(false)
  const baseOp = useRef(new Map<string, number>())
  const frameReveal = useRef(new Map<string, number>())
  const sceneRoot = useRef<HTMLElement | null>(null)
  const captionWrap = useRef<HTMLElement | null>(null)
  const canvasFade = useRef(1) // 1 = canvas visible (Act 1), 0 = hidden (Act 2)

  useMediaScrubber({
    reduced,
    clipStages: CLIP_STAGES,
    act2Indices: ACT2_INDICES,
    refs: {
      posters,
      canvas,
      frames,
      manifest,
      tier,
      alignTop,
      baseOp,
      frameReveal,
      sceneRoot,
      captionWrap,
      canvasFade,
    },
  })

  // Frame counts drive preloading and scroll→index mapping. Absent manifest just
  // falls back to posters, so a missing/failed fetch degrades gracefully.
  useEffect(() => {
    let alive = true
    fetch(assetUrl('anim/frames/manifest.json'))
      .then((r) => (r.ok ? (r.json() as Promise<FrameManifest>) : null))
      .then((m) => {
        if (alive && m) {
          manifest.current = m
          tier.current = pickTier(m)
        }
      })
      .catch(() => {})
    return () => {
      alive = false
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

  if (CLIP_STAGES.length === 0) return null

  return (
    <div className={`${styles.layer} ${captionsMode ? styles.withCaptions : ''}`}>
      {CLIP_STAGES.map((vs) => {
        const fitClass = vs.media.fit === 'cover' ? styles.cover : styles.contain
        return (
          <div key={vs.stage.id} className={styles.stage}>
            {/* Poster base: the final frame, shown instantly on a cold jump while
                this clip's frames preload; the canvas crossfades over it. Meaningful
                alt in reduced motion; decorative (caption carries text) otherwise. */}
            <img
              ref={(el) => {
                if (el) posters.current.set(vs.stage.id, el)
                else posters.current.delete(vs.stage.id)
              }}
              src={assetUrl(vs.media.poster)}
              className={`${styles.media} ${fitClass}`}
              alt={vs.media.alt ?? vs.stage.caption}
              aria-hidden={reduced ? undefined : true}
              decoding="async"
            />
          </div>
        )
      })}
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
