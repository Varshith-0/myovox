import type { CSSProperties } from 'react'
import { STAGES, STAGE_COUNT } from '@/data/stages'
import { useStore } from '@/store/useStore'
import styles from './Caption.module.css'

/** Tokens emitted by the model stages — glowing DOM chips, staggered in. */
function TokenStream({
  phonemes,
  words,
  sentence,
}: {
  phonemes?: readonly string[]
  words?: readonly string[]
  sentence?: string
}) {
  if (!phonemes && !words && !sentence) return null
  return (
    <div className={styles.tokens}>
      {phonemes?.map((p, k) => (
        <span key={`p${k}`} className={styles.phon} style={{ '--k': k } as CSSProperties}>
          {p}
        </span>
      ))}
      {words?.map((w, k) => (
        <span key={`w${k}`} className={styles.word} style={{ '--k': k } as CSSProperties}>
          {w}
        </span>
      ))}
      {sentence && <span className={styles.sentence}>{sentence}</span>}
    </div>
  )
}

/**
 * Fixed caption overlay. Renders the active stage's label, headline, sub-line,
 * and any emitted tokens. The closing stages carry their numeric results inside
 * the Manim clip itself, so no DOM readout is overlaid here. The `key={index}`
 * remounts the block on stage change to replay the entrance.
 */
export function Caption() {
  const index = useStore((s) => s.stageIndex)
  const narrationOn = useStore((s) => s.narrationOn)
  const playing = useStore((s) => s.playing)
  const stage = STAGES[index]
  const isHero = index === 0
  const atTop = stage.captionPosition === 'top'
  // Only while actually narrating (armed *and* playing) do the word-synced
  // subtitles take over: hide the on-screen sub (no duplicate text) and lift
  // bottom captions clear of the subtitle band.
  const captionsMode = narrationOn && playing
  const lifted = captionsMode && !atTop

  return (
    <>
      <div
        data-caption-wrap
        className={`${styles.wrap} ${atTop ? styles.wrapTop : ''} ${lifted ? styles.lifted : ''}`}
        aria-live="polite"
      >
        <div key={index} className={`${styles.block} ${isHero ? styles.hero : ''}`}>
          <span className={styles.rail}>
            {String(index + 1).padStart(2, '0')} / {String(STAGE_COUNT).padStart(2, '0')} ·{' '}
            {stage.rail}
          </span>
          <h2 data-hero-title={isHero ? '' : undefined} className={`${styles.caption} display`}>
            {stage.caption}
          </h2>
          {stage.sub && !captionsMode && (
            <p data-caption-sub className={styles.sub}>
              {stage.sub}
            </p>
          )}
          <TokenStream
            phonemes={stage.tokens?.phonemes}
            words={stage.tokens?.words}
            sentence={stage.tokens?.sentence}
          />
        </div>
      </div>

      {/* The scroll cue lives OUTSIDE the caption wrap so the wrap's title-card
          transform can't drag it off-screen; MediaLayer fades it as you scroll. */}
      {isHero && !playing && (
        <div data-scroll-cue className={styles.scrollCue} aria-hidden="true">
          <span className={styles.scrollLine} />
          scroll or press play
        </div>
      )}
    </>
  )
}
