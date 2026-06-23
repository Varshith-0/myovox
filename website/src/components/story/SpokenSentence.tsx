import { WORDS } from '@/data/speech'
import { STAGES } from '@/data/stages'
import { useStore } from '@/store/useStore'
import styles from './SpokenSentence.module.css'

const TALKING_INDEX = STAGES.findIndex((s) => s.id === 'articulation')

/**
 * The sentence the head is "speaking" on the Talking stage, shown as a running
 * subtitle with the current word lit. It advances in lock-step with the muscle
 * activation (both read the same word index), so the viewer sees the word and
 * the muscles that produce it at the same moment.
 */
export function SpokenSentence() {
  const active = useStore((s) => s.stageIndex === TALKING_INDEX)
  const current = useStore((s) => s.speechWord)
  // While narration is on, the word-synced subtitles own the bottom band — don't
  // stack this demo subtitle under them.
  const narrationOn = useStore((s) => s.narrationOn)
  if (!active || narrationOn) return null

  return (
    <div className={styles.wrap} aria-hidden="true">
      <span className={styles.cue}>speaking</span>
      <p className={styles.line}>
        {WORDS.map((word, i) => (
          <span key={i} className={i === current ? styles.active : styles.word}>
            {word}{' '}
          </span>
        ))}
      </p>
    </div>
  )
}
