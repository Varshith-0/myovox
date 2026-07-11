import { useCallback, useEffect, useRef, useState } from 'react'
import { useLenis } from 'lenis/react'
import { useStages } from '@/story/StagesContext'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'
import { clamp01 } from '@/lib/num'
import { SpeakerControl } from './SpeakerControl'
import { CaptionsToggle } from './CaptionsToggle'
import { QualityControl } from './QualityControl'
import styles from './PlayButton.module.css'

/**
 * Hands-free playback. Click Play to auto-advance the story from wherever you
 * are; any real scroll input — wheel, touch, arrow/space keys — or a second
 * click pauses instantly. While playing, a speaker (narration) and a speed
 * control appear beside it.
 *
 * Two pacing modes, chosen by whether Voice is armed:
 *  - **Voice off** (and the finale): scroll advances at a constant px/s × speed.
 *  - **Voice on:** the *narration is the clock*. Each frame the scroll is set so
 *    the active section's progress equals its clip's playhead, so voice,
 *    animation, and subtitles stay locked and a long line is never cut off. When
 *    a clip ends, we step firmly into the next section so the story can't stall.
 *
 * Play state lives in the store so the engine and subtitles can react to it.
 */
const SPEED = 95 // base px per second at 1× (voice-off mode); the speed control scales it
const SPEEDS = [1, 1.25, 1.5, 2, 3] as const

const PAUSE_KEYS = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' ']
// If the scroll hasn't budged this long while playing (a clip that never loaded,
// a boundary that didn't tick over), step to the next section so we never hang.
const STALL_MS = 2500

export function PlayButton({ autoPlay = false }: { autoPlay?: boolean }) {
  const stages = useStages()
  const stageCount = stages.length
  const lenis = useLenis()
  const playing = useStore((s) => s.playing)
  const speed = useStore((s) => s.playSpeed)
  const setPlaying = useStore((s) => s.setPlaying)
  const setPlaySpeed = useStore((s) => s.setPlaySpeed)
  const setNarrationOn = useStore((s) => s.setNarrationOn)
  // Don't let Play start into a clip that hasn't rendered yet (blank auto-scroll).
  const mediaLoading = useStore((s) => s.mediaLoading)
  const reducedMotion = useStore((s) => s.reducedMotion)

  const rafRef = useRef(0)
  const lastT = useRef(0)
  const lastScroll = useRef(0)
  const stallSince = useRef(0)
  // Holds the latest `frame` so the rAF loop can recurse without referencing the
  // memoized callback inside its own initializer (which trips react-hooks rules).
  const frameRef = useRef<(t: number) => void>(() => {})

  const maxScroll = () => Math.max(0, document.documentElement.scrollHeight - window.innerHeight)

  // Stopping is just flipping the flag; the loop-lifecycle effect below owns the
  // rAF, so it cancels when `playing` goes false and re-kicks when it goes true.
  const stop = useCallback(() => setPlaying(false), [setPlaying])

  // Document-space top of a section and its scroll span.
  const sectionRect = (id: string) => {
    const el = document.getElementById(id)
    if (!el) return null
    const r = el.getBoundingClientRect()
    return { top: r.top + window.scrollY, height: r.height }
  }

  const frame = useCallback(
    (t: number) => {
      const st = useStore.getState()
      if (!st.playing || !lenis) return
      const dt = lastT.current ? Math.min(0.05, (t - lastT.current) / 1000) : 0
      lastT.current = t
      if (!stallSince.current) stallSince.current = t
      // Buffering: the clip's frames aren't drawable, so hold the whole player —
      // narration pauses itself on the same flag, and resetting the stall timer
      // keeps the skip-ahead from firing while the animation loads.
      if (st.mediaLoading) {
        stallSince.current = t
        rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
        return
      }
      const max = maxScroll()
      const onLast = st.stageIndex >= stageCount - 1
      const activeId = stages[st.stageIndex]?.id
      const useNarrationClock = st.narrationOn && !onLast && !!activeId

      const stepNarrationSynced = () => {
        if (!activeId) return false
        const rect = sectionRect(activeId)
        const matched = narration.activeId === activeId && narration.duration > 0
        const done = matched && (narration.ended || narration.time >= narration.duration - 0.04)

        if (rect) {
          if (done) {
            lenis.scrollTo(rect.top + rect.height + 6, { immediate: true, force: true })
          } else if (matched) {
            const p = clamp01(narration.time / narration.duration)
            lenis.scrollTo(rect.top + p * rect.height, { immediate: true, force: true })
          }
        }

        if (Math.abs(lenis.scroll - lastScroll.current) > 0.5) {
          lastScroll.current = lenis.scroll
          stallSince.current = t
        } else if (t - stallSince.current > STALL_MS && rect) {
          lenis.scrollTo(rect.top + rect.height + 6, { immediate: true, force: true })
          stallSince.current = t
        }
        return lenis.scroll >= max - 1
      }

      const stepConstantVelocity = () => {
        const next = lenis.scroll + SPEED * st.playSpeed * dt
        lenis.scrollTo(Math.min(max, next), { immediate: true, force: true })
        return next >= max - 1
      }

      if (useNarrationClock ? stepNarrationSynced() : stepConstantVelocity()) {
        stop()
        return
      }

      rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
    },
    [lenis, stop, stages, stageCount],
  )

  useEffect(() => {
    frameRef.current = frame
  }, [frame])

  const start = useCallback(() => {
    if (!lenis) return
    // Only reset to the top when already parked at the very end; otherwise play
    // from exactly where you are (the voice picks up at the matching moment).
    if (maxScroll() - lenis.scroll < 8) lenis.scrollTo(0, { immediate: true, force: true })
    // Voice is on by default when you press Play (the click is also the gesture
    // that unlocks audio); mute it any time with the speaker. Setting `playing`
    // starts the loop via the lifecycle effect below — never kick rAF here, or a
    // StrictMode/remount teardown could cancel it with nothing to restart it.
    setNarrationOn(true)
    setPlaying(true)
  }, [lenis, setPlaying, setNarrationOn])

  // The rAF loop lifecycle, driven by `playing`. This is the single owner of the
  // loop: it (re)starts whenever we're playing (including after a StrictMode
  // double-mount or any remount that leaves `playing` true — the bug where the
  // voice played but nothing scrolled) and cancels the moment we pause.
  useEffect(() => {
    if (!playing || !lenis) return
    lastT.current = 0
    lastScroll.current = lenis.scroll
    stallSince.current = 0
    rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = 0
    }
  }, [playing, lenis])

  // One Breath auto-start: entering via the chooser card is itself the user gesture that
  // unlocks audio, so One Breath plays the moment it can. Fire exactly once, and only
  // after the first clip's frames are ready (mediaLoading false) so it never
  // auto-scrolls into black. Any real scroll/tap before that pauses as usual.
  const didAutoStart = useRef(false)
  useEffect(() => {
    if (!autoPlay || didAutoStart.current || !lenis || mediaLoading) return
    didAutoStart.current = true
    start()
  }, [autoPlay, lenis, mediaLoading, start])

  // The end-card "Replay" bumps playNonce; start playback when it changes (but not
  // on the initial value, which would auto-play every mount).
  const playNonce = useStore((s) => s.playNonce)
  const lastNonce = useRef(playNonce)
  useEffect(() => {
    if (playNonce === lastNonce.current) return
    lastNonce.current = playNonce
    if (lenis) start()
  }, [playNonce, lenis, start])

  // Any real user SCROLL input pauses auto-play: wheel, touch DRAG, or nav keys.
  // A bare tap is not scroll intent — touchmove (not touchstart) is what pauses,
  // so tapping the pause/speaker/speed buttons on mobile doesn't race a global
  // pause against the button's own click (the "pause restarts playback" bug).
  // Touches that start on a control keep working even if the finger wobbles.
  useEffect(() => {
    const onUser = (e: Event) => {
      if (e.target instanceof Element && e.target.closest('button, input')) return
      if (useStore.getState().playing) stop()
    }
    const onKey = (e: KeyboardEvent) => {
      if (useStore.getState().playing && PAUSE_KEYS.includes(e.key)) stop()
    }
    window.addEventListener('wheel', onUser, { passive: true })
    window.addEventListener('touchmove', onUser, { passive: true })
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('wheel', onUser)
      window.removeEventListener('touchmove', onUser)
      window.removeEventListener('keydown', onKey)
    }
  }, [stop])

  // YouTube-style speed menu: the pill toggles a list of selectable speeds.
  const [speedOpen, setSpeedOpen] = useState(false)
  const speedRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!speedOpen) return
    const onDown = (e: PointerEvent) => {
      if (!(e.target instanceof Node) || !speedRef.current?.contains(e.target)) {
        setSpeedOpen(false)
      }
    }
    window.addEventListener('pointerdown', onDown)
    return () => window.removeEventListener('pointerdown', onDown)
  }, [speedOpen])

  return (
    <div className={styles.bar}>
      <CaptionsToggle />
      {/* Reduced motion shows static posters — quality has nothing to change. */}
      {!reducedMotion && <QualityControl />}
      {playing && <SpeakerControl />}

      <button
        type="button"
        className={styles.btn}
        onClick={() => (playing ? stop() : start())}
        disabled={!playing && mediaLoading}
        aria-label={
          playing
            ? 'Pause auto-play'
            : mediaLoading
              ? 'Play (waiting for the animation to finish rendering)'
              : 'Play the story hands-free'
        }
      >
        <span className={playing ? styles.pause : styles.play} aria-hidden="true" />
        <span className={styles.label}>{playing ? 'Pause' : 'Play'}</span>
      </button>

      {playing && (
        <div className={styles.speedGroup} ref={speedRef}>
          {speedOpen && (
            <div className={styles.speedMenu} role="menu" aria-label="Playback speed">
              {SPEEDS.map((s) => (
                <button
                  key={s}
                  type="button"
                  role="menuitemradio"
                  aria-checked={s === speed}
                  className={`${styles.speedItem} ${s === speed ? styles.speedItemActive : ''}`}
                  onClick={() => {
                    setPlaySpeed(s)
                    setSpeedOpen(false)
                  }}
                >
                  <span>{s}×</span>
                  {s === 1 && <span className={styles.speedNote}>normal</span>}
                </button>
              ))}
            </div>
          )}
          <button
            type="button"
            className={styles.speed}
            onClick={() => setSpeedOpen((o) => !o)}
            aria-haspopup="menu"
            aria-expanded={speedOpen}
            aria-label={`Playback speed ${speed}×. Click to choose a speed.`}
            title={`Playback speed: ${speed}×`}
          >
            <span className={styles.ff} aria-hidden="true" />
            <span className={styles.speedVal}>{speed}×</span>
          </button>
        </div>
      )}
    </div>
  )
}
