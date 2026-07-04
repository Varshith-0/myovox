import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLenis } from 'lenis/react'
import { useStages } from '@/story/StagesContext'
import { useStore } from '@/store/useStore'
import styles from './EndCard.module.css'

/**
 * The reel's closing call-to-action, shown only on "In One Breath". It fades in
 * once the final scene (MYOVOX) has settled — over the lower third the end clip
 * leaves clear — offering the deep dive and a replay. Mounted only for the reel,
 * so the deep dive never shows it.
 *
 * @param deepDivePath route to the fifty-scene deep dive.
 */
export function EndCard({ deepDivePath }: { deepDivePath: string }) {
  const stages = useStages()
  const lastId = stages[stages.length - 1]?.id
  const navigate = useNavigate()
  const lenis = useLenis()
  const requestPlay = useStore((s) => s.requestPlay)
  const lastIndex = stages.length - 1
  const [shown, setShown] = useState(false)

  // Reveal once the final stage's local scroll passes ~60% (MYOVOX has formed and
  // ignited); hide again if the reader scrolls back up. A single rAF reads the
  // store's stage index + the last section's rect and toggles only on change.
  useEffect(() => {
    if (!lastId) return
    let raf = 0
    const tick = () => {
      const onLast = useStore.getState().stageIndex >= lastIndex
      const el = document.getElementById(lastId)
      let next = false
      if (onLast && el) {
        const r = el.getBoundingClientRect()
        next = (0 - r.top) / (r.height || 1) > 0.6
      }
      setShown((prev) => (prev === next ? prev : next))
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [lastId, lastIndex])

  // Tell the rest of the story the card is up, so the Subtitles hide behind it.
  const setEndCardShown = useStore((s) => s.setEndCardShown)
  useEffect(() => {
    setEndCardShown(shown)
    return () => setEndCardShown(false)
  }, [shown, setEndCardShown])

  const replay = () => {
    useStore.getState().setPlaying(false)
    if (lenis) lenis.scrollTo(0, { immediate: true, force: true })
    else window.scrollTo(0, 0)
    // Next frame, after the scroll lands, ask the PlayButton to start again.
    requestAnimationFrame(() => requestPlay())
  }

  return (
    <div className={`${styles.wrap} ${shown ? styles.shown : ''}`} aria-hidden={!shown}>
      <div className={styles.card}>
        <p className={styles.kicker}>That was the trailer.</p>
        <p className={styles.line}>The full story goes fifty chapters deep.</p>
        <div className={styles.actions}>
          <button
            type="button"
            className={styles.primary}
            onClick={() => navigate(deepDivePath)}
            tabIndex={shown ? 0 : -1}
          >
            Go under the hood →
          </button>
          <button
            type="button"
            className={styles.ghost}
            onClick={replay}
            tabIndex={shown ? 0 : -1}
          >
            ↻ Replay
          </button>
        </div>
      </div>
    </div>
  )
}
