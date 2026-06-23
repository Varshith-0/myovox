import { useCallback, useEffect, useRef } from 'react'
import { useLenis } from 'lenis/react'
import { STAGES, STAGE_COUNT } from '@/data/stages'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'
import { SpeakerControl } from './SpeakerControl'
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
const SPEEDS = [1, 1.5, 2, 3] as const

const PAUSE_KEYS = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' ']
const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
// If the scroll hasn't budged this long while playing (a clip that never loaded,
// a boundary that didn't tick over), step to the next section so we never hang.
const STALL_MS = 2500

export function PlayButton() {
  const lenis = useLenis()
  const playing = useStore((s) => s.playing)
  const speed = useStore((s) => s.playSpeed)
  const setPlaying = useStore((s) => s.setPlaying)
  const setPlaySpeed = useStore((s) => s.setPlaySpeed)
  const setNarrationOn = useStore((s) => s.setNarrationOn)

  const rafRef = useRef(0)
  const lastT = useRef(0)
  const lastScroll = useRef(0)
  const stallSince = useRef(0)
  // Holds the latest `frame` so the rAF loop can recurse without referencing the
  // memoized callback inside its own initializer (which trips react-hooks rules).
  const frameRef = useRef<(t: number) => void>(() => {})

  const maxScroll = () => Math.max(0, document.documentElement.scrollHeight - window.innerHeight)

  const stop = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = 0
    setPlaying(false)
  }, [setPlaying])

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
      const max = maxScroll()
      const onLast = st.stageIndex >= STAGE_COUNT - 1
      const activeId = STAGES[st.stageIndex]?.id

      if (st.narrationOn && !onLast && activeId) {
        const rect = sectionRect(activeId)
        const matched = narration.activeId === activeId && narration.duration > 0
        const done = matched && (narration.ended || narration.time >= narration.duration - 0.04)
        if (rect) {
          if (done) {
            lenis.scrollTo(rect.top + rect.height + 6, { immediate: true, force: true }) // step into next
          } else if (matched) {
            const p = clamp01(narration.time / narration.duration)
            lenis.scrollTo(rect.top + p * rect.height, { immediate: true, force: true })
          }
          // else: clip not ready yet → hold (the stall guard below covers a hang)
        }
        // Stall guard: if scroll is frozen too long, step to the next section.
        if (Math.abs(lenis.scroll - lastScroll.current) > 0.5) {
          lastScroll.current = lenis.scroll
          stallSince.current = t
        } else if (t - stallSince.current > STALL_MS && rect) {
          lenis.scrollTo(rect.top + rect.height + 6, { immediate: true, force: true })
          stallSince.current = t
        }
        if (lenis.scroll >= max - 1) {
          stop()
          return
        }
      } else {
        // Voice off (any stage) or the cinematic finale: gentle constant scroll.
        const next = lenis.scroll + SPEED * st.playSpeed * dt
        lenis.scrollTo(Math.min(max, next), { immediate: true, force: true })
        if (next >= max - 1) {
          stop()
          return
        }
      }
      rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
    },
    [lenis, stop],
  )

  useEffect(() => {
    frameRef.current = frame
  }, [frame])

  const start = useCallback(() => {
    if (!lenis) return
    // Only reset to the top when already parked at the very end; otherwise play
    // from exactly where you are (the voice picks up at the matching moment).
    if (maxScroll() - lenis.scroll < 8) lenis.scrollTo(0, { immediate: true, force: true })
    lastT.current = 0
    lastScroll.current = lenis.scroll
    stallSince.current = 0
    // Voice is on by default when you press Play (the click is also the gesture
    // that unlocks audio); mute it any time with the speaker.
    setNarrationOn(true)
    setPlaying(true)
    rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
  }, [lenis, setPlaying, setNarrationOn])

  // Any real user scroll input pauses auto-play. (Programmatic scrolls above do
  // not fire wheel/touch/key events, so they never self-pause; nor does clicking
  // the speed control, which only changes the rate.)
  useEffect(() => {
    const onUser = () => {
      if (useStore.getState().playing) stop()
    }
    const onKey = (e: KeyboardEvent) => {
      if (useStore.getState().playing && PAUSE_KEYS.includes(e.key)) stop()
    }
    window.addEventListener('wheel', onUser, { passive: true })
    window.addEventListener('touchstart', onUser, { passive: true })
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('wheel', onUser)
      window.removeEventListener('touchstart', onUser)
      window.removeEventListener('keydown', onKey)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [stop])

  const cycleSpeed = () =>
    setPlaySpeed(SPEEDS[(SPEEDS.indexOf(speed as (typeof SPEEDS)[number]) + 1) % SPEEDS.length])

  return (
    <div className={styles.bar}>
      {playing && <SpeakerControl />}

      <button
        type="button"
        className={styles.btn}
        onClick={() => (playing ? stop() : start())}
        aria-label={playing ? 'Pause auto-play' : 'Play the story hands-free'}
      >
        <span className={playing ? styles.pause : styles.play} aria-hidden="true" />
        <span className={styles.label}>{playing ? 'Pause' : 'Play'}</span>
      </button>

      {playing && (
        <button
          type="button"
          className={styles.speed}
          onClick={cycleSpeed}
          aria-label={`Playback speed ${speed}×. Click to change.`}
          title={`Playback speed: ${speed}× — click to change`}
        >
          <span className={styles.ff} aria-hidden="true" />
          <span className={styles.speedVal}>{speed}×</span>
        </button>
      )}
    </div>
  )
}
