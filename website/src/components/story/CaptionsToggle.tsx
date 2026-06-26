import { useStore } from '@/store/useStore'
import styles from './SpeakerControl.module.css'

/**
 * Subtitle (captions) toggle. Captions are ON by default (WCAG 1.2.2/1.2.4) and
 * follow the scroll position while reading; this lets a viewer turn them off.
 * Always visible in the control bar (captions show during scroll, not just Play).
 * Reuses the SpeakerControl pill styling for a consistent control row.
 */
export function CaptionsToggle() {
  const on = useStore((s) => s.subtitlesOn)
  const setSubtitlesOn = useStore((s) => s.setSubtitlesOn)

  return (
    <div className={`${styles.group} ${on ? styles.armed : ''}`}>
      <button
        type="button"
        className={styles.btn}
        aria-pressed={on}
        aria-label={on ? 'Turn subtitles off' : 'Turn subtitles on'}
        title={on ? 'Subtitles on — click to hide' : 'Subtitles off — click to show'}
        onClick={() => setSubtitlesOn(!on)}
      >
        <CcGlyph on={on} />
      </button>
    </div>
  )
}

/** A captions box with two "c" marks; struck through when off. */
function CcGlyph({ on }: { on: boolean }) {
  return (
    <svg
      className={styles.icon}
      width="18"
      height="14"
      viewBox="0 0 24 18"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="1.5" y="1.5" width="21" height="15" rx="3" />
      <path d="M10 7.4a2.3 2.3 0 1 0 0 3.2" />
      <path d="M17 7.4a2.3 2.3 0 1 0 0 3.2" />
      {!on && <path d="M3.5 15.5 20.5 2.5" />}
    </svg>
  )
}
