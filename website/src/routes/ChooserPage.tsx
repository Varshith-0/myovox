import { useNavigate } from 'react-router-dom'
import { SITE } from '@/data/site'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './ChooserPage.module.css'

/**
 * The landing chooser (route `/`). Two ways into the same science: the ten-scene
 * reel ("In One Breath") or the fifty-scene deep dive ("Under the Hood"). Picking
 * the reel is itself the user gesture browsers require to auto-play its audio, so
 * that card routes straight into a playing reel.
 */

const REEL_PATH = '/story/one-breath'
const DEEP_PATH = '/story/under-the-hood'

/** A faint, non-interactive EMG trace motif behind a card. */
function TraceMotif() {
  return (
    <svg className={styles.motif} viewBox="0 0 320 120" aria-hidden="true" preserveAspectRatio="none">
      <path
        d="M0 60 H60 l6 -34 l7 66 l7 -52 l6 40 l6 -14 H150 l6 -44 l7 78 l6 -40 l6 20 H320"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
      />
    </svg>
  )
}

/** A faint grid-of-dials motif behind the deep-dive card. */
function GridMotif() {
  const cells = Array.from({ length: 36 }, (_, i) => i)
  return (
    <svg className={styles.motif} viewBox="0 0 120 120" aria-hidden="true">
      {cells.map((i) => {
        const x = 10 + (i % 6) * 20
        const y = 10 + Math.floor(i / 6) * 20
        return <circle key={i} cx={x} cy={y} r="4.5" fill="none" stroke="currentColor" strokeWidth="1" />
      })}
    </svg>
  )
}

export function ChooserPage() {
  const navigate = useNavigate()

  return (
    <main className={styles.page}>
      <header className={styles.head}>
        <LogoMark className={styles.mark} size={40} duration={14} />
        <h1 className={styles.title}>{SITE.brand}</h1>
        <p className={styles.tagline}>{SITE.tagline}</p>
        <p className={styles.prompt}>Two ways in. Pick your depth.</p>
      </header>

      <div className={styles.cards}>
        <button
          type="button"
          className={`${styles.card} ${styles.reel}`}
          onClick={() => navigate(REEL_PATH)}
        >
          <TraceMotif />
          <span className={styles.badge}>10 scenes · a short watch</span>
          <span className={styles.cardTitle}>In One Breath</span>
          <span className={styles.cardDesc}>
            The whole story, in one breath. A short, jargon-free watch — what happens, why it
            works, and why it matters. The complete picture, in under two minutes.
          </span>
          <span className={styles.cta}>Watch the reel →</span>
        </button>

        <button
          type="button"
          className={`${styles.card} ${styles.deep}`}
          onClick={() => navigate(DEEP_PATH)}
        >
          <GridMotif />
          <span className={styles.badge}>50 scenes · go deep</span>
          <span className={styles.cardTitle}>Under the Hood</span>
          <span className={styles.cardDesc}>
            The full deep dive. Fifty short scenes, from the first muscle spark to
            the final sentence. One concept at a time. Understand what's happening under the hood.
          </span>
          <span className={styles.cta}>Take the deep dive →</span>
        </button>
      </div>
    </main>
  )
}
