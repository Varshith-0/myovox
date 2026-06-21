import { useLenis } from 'lenis/react'
import { STAGES } from '@/data/stages'
import { useStore } from '@/store/useStore'
import styles from './ProgressRail.module.css'

/**
 * Vertical stage indicator. Highlights the active stage and lets the user jump
 * to any stage (Lenis smooth-scroll to the section anchor). Hidden on small
 * screens where it would crowd the caption.
 */
export function ProgressRail() {
  const active = useStore((s) => s.stageIndex)
  const lenis = useLenis()

  const goto = (id: string) => {
    const el = document.getElementById(id)
    if (!el) return
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
