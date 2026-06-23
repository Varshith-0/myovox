import type { CSSProperties } from 'react'
import { useStore } from '@/store/useStore'
import styles from './SpeakerControl.module.css'

/**
 * The narration toggle, sitting beside Play in the control bar. Click the
 * speaker to arm narration (also the gesture that unlocks audio — see
 * {@link NarrationLayer}); the voice then plays while the story is playing. When
 * armed, a volume slider reveals on hover/focus. State lives in the store.
 */
export function SpeakerControl() {
  const on = useStore((s) => s.narrationOn)
  const volume = useStore((s) => s.volume)
  const setNarrationOn = useStore((s) => s.setNarrationOn)
  const setVolume = useStore((s) => s.setVolume)

  return (
    <div className={`${styles.group} ${on ? styles.armed : ''}`}>
      <button
        type="button"
        className={styles.btn}
        aria-pressed={on}
        aria-label={on ? 'Turn narration off' : 'Turn narration on'}
        title={on ? 'Narration on — plays during Play' : 'Narration off — click to listen during Play'}
        onClick={() => setNarrationOn(!on)}
      >
        <SpeakerGlyph on={on} />
      </button>

      {on && (
        <div className={styles.vol}>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={(e) => setVolume(Number(e.currentTarget.value))}
            aria-label="Narration volume"
            title={`Volume ${Math.round(volume * 100)}%`}
            style={{ '--v': volume } as CSSProperties}
          />
        </div>
      )}
    </div>
  )
}

/** Speaker glyph: sound waves when on, a mute cross when off. */
function SpeakerGlyph({ on }: { on: boolean }) {
  return (
    <svg
      className={styles.icon}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 9.5v5h3.5L13 19V5L7.5 9.5H4z" fill="currentColor" stroke="none" />
      {on ? (
        <>
          <path d="M16 8.8a4.5 4.5 0 0 1 0 6.4" />
          <path d="M18.7 6a8 8 0 0 1 0 12" />
        </>
      ) : (
        <path d="M16.5 9.5l5 5M21.5 9.5l-5 5" />
      )}
    </svg>
  )
}
