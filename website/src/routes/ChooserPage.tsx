import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SITE } from '@/data/site'
import styles from './ChooserPage.module.css'

/**
 * The landing chooser (route `/`). Two ways into the same science: the ten-scene
 * One Breath ("In One Breath") or the fifty-scene deep dive ("Under the Hood"). Picking
 * One Breath is itself the user gesture browsers require to auto-play its audio, so
 * that card routes straight into One Breath already playing.
 *
 * Clicking a card runs a short shared-element handoff — the chosen card lifts and
 * the frame dissolves to black — before navigating, so the black start of the
 * story reads as a continuation rather than a hard cut. Reduced-motion skips it.
 */

const ONE_BREATH_PATH = '/story/one-breath'
const DEEP_PATH = '/story/under-the-hood'
const LEAVE_MS = 460

export function ChooserPage() {
  const navigate = useNavigate()
  const [leaving, setLeaving] = useState<null | 'one-breath' | 'deep'>(null)

  const go = (which: 'one-breath' | 'deep', path: string) => {
    if (leaving) return
    // Reduced motion: skip the handoff, navigate straight away.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      navigate(path)
      return
    }
    setLeaving(which)
    window.setTimeout(() => navigate(path), LEAVE_MS)
  }

  return (
    <main className={`${styles.page} ${leaving ? styles.leaving : ''}`}>
      <header className={styles.head}>
        <p className={styles.tagline}>{SITE.tagline}</p>
        <p className={styles.prompt}>Two ways in. Pick your depth.</p>
      </header>

      <div className={styles.cards}>
        <span className={styles.spine} aria-hidden="true" />

        <button
          type="button"
          className={`${styles.card} ${leaving === 'one-breath' ? styles.chosen : ''}`}
          onClick={() => go('one-breath', ONE_BREATH_PATH)}
        >
          <span className={styles.badge}>10 chapters · a short watch</span>
          <span className={styles.cardTitle}>In One Breath</span>
          <span className={styles.cardDesc}>
            The whole story, in one breath. A short, jargon-free watch: what happens, why it
            works, and why it matters. The complete picture, in under two minutes.
          </span>
          <span className={styles.cta}>Watch in one breath →</span>
        </button>

        <button
          type="button"
          className={`${styles.card} ${leaving === 'deep' ? styles.chosen : ''}`}
          onClick={() => go('deep', DEEP_PATH)}
        >
          <span className={styles.badge}>50 chapters · go deep</span>
          <span className={styles.cardTitle}>Under the Hood</span>
          <span className={styles.cardDesc}>
            The full deep dive. Fifty short chapters, from the first muscle spark to the final
            sentence. One concept at a time. Understand what's happening under the hood.
          </span>
          <span className={styles.cta}>Take the deep dive →</span>
        </button>
      </div>

      <p className={styles.note}>
        Either one narrates itself, hands-free, or just scroll to move through it at your own
        pace. Your scroll is the remote.
      </p>

      {/* Dissolve-to-black veil for the shared-element handoff into the story. */}
      <div className={`${styles.veil} ${leaving ? styles.veilShow : ''}`} aria-hidden="true" />
    </main>
  )
}
