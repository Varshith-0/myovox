import { useCallback, useEffect, useRef, useState } from 'react'
import { useLenis } from 'lenis/react'
import styles from './PlayButton.module.css'

/**
 * Hands-free playback. Click Play to auto-scroll the story at a gentle, steady
 * reading pace (so the Act-2 clips scrub themselves); any real scroll input —
 * wheel, touch, arrow/space keys — or a second click pauses it instantly. A speed
 * control beside it (enabled only while playing) cycles 1× → 5×, multiplying the
 * scroll rate so the whole thing plays back like a video at the chosen speed
 * (takes effect immediately, even mid-play).
 *
 * We advance the scroll a little every animation frame via Lenis, rather than
 * firing one long `scrollTo(end, duration)` tween: pausing is then simply "stop
 * the loop" (cancelAnimationFrame), which a long tween could not be relied on to
 * cancel. The pace is constant px/s, so the speed is the same wherever you start.
 */
const SPEED = 95 // base px per second at 1× — gentle; the speed control scales it
const SPEEDS = [1, 2, 3, 4, 5] as const

const PAUSE_KEYS = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' ']

export function PlayButton() {
  const lenis = useLenis()
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState<number>(1)
  const playingRef = useRef(false)
  const rafRef = useRef(0)
  const lastT = useRef(0)
  // Holds the latest `frame` so the rAF loop can recurse without referencing the
  // memoized callback inside its own initializer (which trips react-hooks rules).
  const frameRef = useRef<(t: number) => void>(() => {})
  // The loop reads the live speed each frame, so changing it never restarts playback.
  const speedRef = useRef(1)
  useEffect(() => {
    speedRef.current = speed
  }, [speed])

  const maxScroll = () =>
    Math.max(0, document.documentElement.scrollHeight - window.innerHeight)

  const stop = useCallback(() => {
    if (!playingRef.current) return
    playingRef.current = false
    setPlaying(false)
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = 0
  }, [])

  const frame = useCallback(
    (t: number) => {
      if (!playingRef.current || !lenis) return
      // dt in seconds, clamped so a long frame (tab refocus) can't lurch.
      const dt = lastT.current ? Math.min(0.05, (t - lastT.current) / 1000) : 0
      lastT.current = t
      const max = maxScroll()
      const next = lenis.scroll + SPEED * speedRef.current * dt
      lenis.scrollTo(Math.min(max, next), { immediate: true, force: true })
      if (next >= max - 1) {
        stop()
        return
      }
      rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
    },
    [lenis, stop],
  )

  // Keep the ref pointing at the latest frame so the loop always runs current logic.
  useEffect(() => {
    frameRef.current = frame
  }, [frame])

  const start = useCallback(() => {
    if (!lenis) return
    // At the very end → restart from the top.
    if (maxScroll() - lenis.scroll < 8) lenis.scrollTo(0, { immediate: true, force: true })
    playingRef.current = true
    setPlaying(true)
    lastT.current = 0
    rafRef.current = requestAnimationFrame((ts) => frameRef.current(ts))
  }, [lenis])

  // Any real user scroll input pauses auto-play. (Programmatic scrolls above do
  // not fire wheel/touch/key events, so they never self-pause; nor does clicking
  // the speed control, which only changes the rate.)
  useEffect(() => {
    const onUser = () => {
      if (playingRef.current) stop()
    }
    const onKey = (e: KeyboardEvent) => {
      if (playingRef.current && PAUSE_KEYS.includes(e.key)) stop()
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
    setSpeed((s) => SPEEDS[(SPEEDS.indexOf(s as (typeof SPEEDS)[number]) + 1) % SPEEDS.length])

  return (
    <div className={styles.bar}>
      <button
        type="button"
        className={styles.btn}
        onClick={() => (playing ? stop() : start())}
        aria-label={playing ? 'Pause auto-play' : 'Play the story hands-free'}
      >
        <span className={playing ? styles.pause : styles.play} aria-hidden="true" />
        <span className={styles.label}>{playing ? 'Pause' : 'Play'}</span>
      </button>

      <button
        type="button"
        className={styles.speed}
        onClick={cycleSpeed}
        disabled={!playing}
        aria-label={`Playback speed ${speed}×. Click to change (1×–5×).`}
        title={playing ? `Playback speed: ${speed}× — click to change` : 'Speed (available while playing)'}
      >
        <span className={styles.ff} aria-hidden="true" />
        <span className={styles.speedVal}>{speed}×</span>
      </button>
    </div>
  )
}
