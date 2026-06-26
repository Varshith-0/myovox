import { useEffect, useRef } from 'react'
import { STAGES, stageMedia, stageScrollVh, type Stage, type StageMedia } from '@/data/stages'
import { useStore } from '@/store/useStore'
import styles from './MediaLayer.module.css'

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
const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
const smooth = (x: number, a: number, b: number) => {
  const t = clamp01((x - a) / (b - a))
  return t * t * (3 - 2 * t)
}

type VideoStage = { stage: Stage; index: number; media: Extract<StageMedia, { kind: 'video' }>; vh: number }

const VIDEO_STAGES: VideoStage[] = STAGES.flatMap((stage, index) => {
  const m = stageMedia(stage)
  return m.kind === 'video' ? [{ stage, index, media: m, vh: stageScrollVh(stage) }] : []
})

const ACT2_INDICES = new Set(VIDEO_STAGES.map((v) => v.index))

/** Local scroll progress through a section: 0 when its top hits the viewport top,
 *  1 when it has fully scrolled out (its bottom reaches the viewport top). Matches
 *  the fractional stage index, so the clip scrubs across the whole section with no
 *  dead tail. (A trailing spacer lets the last section reach 1.) */
function localProgressFor(el: HTMLElement): number {
  const r = el.getBoundingClientRect()
  return clamp01((0 - r.top) / (r.height || 1))
}

const setOpacity = (el: HTMLElement, v: number) => {
  el.style.opacity = v > 0.985 ? '1' : v < 0.01 ? '0' : String(v)
}

// Title-card hold: below this local progress the clip is hidden and the caption
// is centred; across this band the caption rises and the clip fades in.
const HOLD = 0.04
const REVEAL = 0.16
const RISE_VH = 22

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

  useEffect(() => {
    if (VIDEO_STAGES.length === 0) return
    let raf = 0
    const tick = () => {
      const active = useStore.getState().stageIndex
      let activeLocal = -1 // local progress of the active Act-2 stage (-1 if Act 1)
      for (const vs of VIDEO_STAGES) {
        const id = vs.stage.id
        const section = document.getElementById(id)
        const el = reduced ? posters.current.get(id) : videos.current.get(id)
        if (!section || !el) continue
        const isActive = vs.index === active

        // Far stages: hide so the compositor skips them.
        if (Math.abs(vs.index - active) > 2) {
          if (el.style.display !== 'none') el.style.display = 'none'
          continue
        }
        if (el.style.display === 'none') el.style.display = ''

        const local = localProgressFor(section)
        if (isActive) activeLocal = local

        // Per-stage presence (1 when active) — drives this element's opacity.
        const bTarget = isActive ? 1 : 0
        const bp = baseOp.current.get(id) ?? 0
        const bn = reduced ? bTarget : bp + (bTarget - bp) * 0.2
        baseOp.current.set(id, bn)

        if (reduced) {
          const purl = mediaUrl(vs.media.poster)
          if (el.getAttribute('src') !== purl) el.setAttribute('src', purl)
          setOpacity(el, bn)
          continue
        }

        // Normal motion: scrub the live video; it holds its current frame at rest.
        const video = el as HTMLVideoElement
        const vurl = mediaUrl(vs.media.src)
        if (video.getAttribute('src') !== vurl) {
          video.setAttribute('src', vurl)
          video.load()
        }
        // Scrub by seeking — but never queue a new seek while the previous one is
        // still in flight. Hammering currentTime every frame outruns the decoder,
        // which leaves the <video> half-decoded; waiting for `seeking` to clear
        // self-paces to the decode rate and keeps every frame painted.
        if (
          video.readyState >= 1 &&
          Number.isFinite(video.duration) &&
          video.duration > 0 &&
          !video.seeking
        ) {
          const t = local * video.duration
          if (Math.abs(video.currentTime - t) > 1 / 30) video.currentTime = t
        }
        // Latch "has decoded a frame". Once true we never drop opacity back to 0,
        // because readyState briefly dips below 2 on *every* seek — multiplying it
        // in made the clip dim one frame in two (a 30 Hz flicker). The title-card
        // hold (smooth() below) still keeps it hidden on landing; this only stops
        // the first frame flashing black before any frame has loaded.
        if (video.readyState >= 2) shownOnce.current.set(id, true)
        const vis = shownOnce.current.get(id) ? 1 : 0
        setOpacity(video, bn * smooth(local, HOLD, REVEAL) * vis)
      }

      // Fade the 3D canvas out whenever an Act-2 stage is active (robust — keyed
      // to the active index, so the point-cloud head can't ghost through the clip
      // or the title card).
      const target = ACT2_INDICES.has(active) ? 0 : 1
      canvasFade.current += (target - canvasFade.current) * (reduced ? 1 : 0.26)
      if (!sceneRoot.current) sceneRoot.current = document.querySelector('[data-scene-root]')
      if (sceneRoot.current) {
        sceneRoot.current.style.transition = 'none'
        sceneRoot.current.style.opacity = canvasFade.current > 0.99 ? '1' : canvasFade.current < 0.01 ? '0' : String(canvasFade.current)
      }

      // Title-card reveal: on landing the caption sits low/centred, then rises to
      // the top as the story begins.
      if (!captionWrap.current) captionWrap.current = document.querySelector('[data-caption-wrap]')
      if (captionWrap.current) {
        const rise = activeLocal >= 0 && !reduced ? (1 - smooth(activeLocal, 0, 0.12)) * RISE_VH : 0
        captionWrap.current.style.transform = rise > 0.05 ? `translateY(${rise}vh)` : ''
      }
      // The in-depth description is read on the title card, then fades as the clip
      // plays so it doesn't crowd the animation. (Re-queried each frame because the
      // caption block remounts per stage.) Act-1 stages keep their sub fully shown.
      const sub = document.querySelector('[data-caption-sub]') as HTMLElement | null
      if (sub) sub.style.opacity = activeLocal >= 0 && !reduced ? String(1 - smooth(activeLocal, 0.06, 0.24)) : ''

      // Hero title: shrink from display size (landing) to the normal top-caption
      // size as the story begins, so it stops overlapping the clip behind it.
      const heroTitle = document.querySelector('[data-hero-title]') as HTMLElement | null
      if (heroTitle) {
        const p = reduced ? 0 : activeLocal >= 0 ? 1 - smooth(activeLocal, 0.0, 0.18) : 1
        heroTitle.style.setProperty('--hero-p', String(p))
      }
      // Scroll cue: full on the landing frame, fading out as you scroll in.
      const cue = document.querySelector('[data-scroll-cue]') as HTMLElement | null
      if (cue) cue.style.opacity = reduced ? '1' : String(1 - smooth(Math.max(activeLocal, 0), 0.0, 0.12))

      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      if (sceneRoot.current) {
        sceneRoot.current.style.opacity = ''
        sceneRoot.current.style.transition = ''
      }
      if (captionWrap.current) captionWrap.current.style.transform = ''
    }
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
