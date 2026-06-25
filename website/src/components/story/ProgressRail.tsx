import { useEffect, useState } from 'react'
import { useLenis } from 'lenis/react'
import { useStore } from '@/store/useStore'
import { STAGES } from '@/data/stages'
import styles from './ProgressRail.module.css'

/**
 * Vertical stage indicator. Highlights the active stage and lets the user jump
 * to any stage (Lenis smooth-scroll to the section anchor). Hidden on small
 * screens where it would crowd the caption.
 */
export function ProgressRail() {
  const setPlaying = useStore((s) => s.setPlaying)
  const lenis = useLenis()

  // The live active stage flips for a frame at section boundaries (sub-pixel
  // scroll jitter), which made the rail's animated tick/glow flicker. Debounce
  // ONLY the rail's highlight — settle for ~90ms before moving it — without
  // touching the global stageIndex that Play, captions and narration rely on.
  const rawActive = useStore((s) => s.stageIndex)
  const [active, setActive] = useState(rawActive)
  useEffect(() => {
    const id = window.setTimeout(() => setActive(rawActive), 90)
    return () => window.clearTimeout(id)
  }, [rawActive])

  const goto = (id: string) => {
    const el = document.getElementById(id)
    if (!el) return
    // Stop hands-free Play first — otherwise its per-frame scroll loop overrides
    // the jump and the click "doesn't go directly" to the chosen stage.
    setPlaying(false)
    if (lenis) lenis.scrollTo(el)
    else el.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <nav className={styles.rail} aria-label="Story stages">
      <ol className={styles.list}>
        {STAGES.map((stage, i) => (
          <li key={stage.id}>
            <button
              type="button"
              className={`${styles.item} ${i === active ? styles.active : ''}`}
              onClick={() => goto(stage.id)}
              aria-current={i === active ? 'step' : undefined}
              aria-label={`Stage ${i + 1}: ${stage.rail}`}
            >
              <span className={styles.tick} aria-hidden="true" />
              <span className={styles.name}>{stage.rail}</span>
            </button>
          </li>
        ))}
      </ol>
    </nav>
  )
}
