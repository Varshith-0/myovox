import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'
import { assetUrl } from '@/lib/asset'
import { lastBefore, needsLeadingSpace, joinWords, type Cue } from '@/lib/cues'
import styles from './Subtitles.module.css'

/**
 * YouTube-style subtitles: one punctuated sentence at a time, with the spoken
 * word lit in step. Shown only while narration is actually playing. It follows
 * the {@link NarrationLayer}'s active clip + playhead (via the {@link narration}
 * hot-state) and reads the sentence cues baked beside each clip
 * (`<id>.captions.json`, from `scripts/narrate.py`).
 */

export function Subtitles() {
  const on = useStore((s) => s.subtitlesOn)
  const [cues, setCues] = useState<Cue[]>([])
  const [cueIdx, setCueIdx] = useState(-1)
  const [wordIdx, setWordIdx] = useState(-1)

  const cache = useRef(new Map<string, Cue[]>())
  const idRef = useRef<string | null>(null)
  const cuesRef = useRef<Cue[]>([])

  useEffect(() => {
    if (!on) return
    let raf = 0
    let cancelled = false

    const load = async (clipId: string) => {
      const cached = cache.current.get(clipId)
      if (cached) {
        cuesRef.current = cached
        setCues(cached)
        return
      }
      try {
        const res = await fetch(assetUrl(`anim/${clipId}.captions.json`))
        const data = res.ok ? ((await res.json()).cues as Cue[]) : []
        cache.current.set(clipId, data)
        if (!cancelled && idRef.current === clipId) {
          cuesRef.current = data
          setCues(data)
        }
      } catch {
        /* no caption track — leave empty */
      }
    }

    const tick = () => {
      const clip = narration.activeId
      if (clip !== idRef.current) {
        idRef.current = clip
        cuesRef.current = []
        setCues([])
        setCueIdx(-1)
        setWordIdx(-1)
        if (clip) load(clip)
      }
      const cs = cuesRef.current
      if (cs.length) {
        const t = narration.time
        const ci = lastBefore(cs, t)
        setCueIdx((prev) => (prev === ci ? prev : ci))
        const wi = ci >= 0 ? lastBefore(cs[ci].words, t) : -1
        setWordIdx((prev) => (prev === wi ? prev : wi))
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelled = true
      cancelAnimationFrame(raf)
    }
  }, [on])

  if (!on || cueIdx < 0 || cueIdx >= cues.length) return null
  const cue = cues[cueIdx]
  // The whole sentence as one string — announced once per cue by the live region
  // below (the visible word-by-word line is decorative, so AT isn't spammed).
  const sentence = joinWords(cue.words)

  return (
    <>
      <div className={styles.wrap} data-subtitles aria-hidden="true">
        <p className={styles.line}>
          {cue.words.map((word, i) => {
            const cls = i === wordIdx ? styles.now : i < wordIdx ? styles.spoken : styles.ahead
            const lead = needsLeadingSpace(word.w, i) ? ' ' : ''
            return (
              <span key={i} className={cls}>
                {lead}
                {word.w}
              </span>
            )
          })}
        </p>
      </div>
      <p aria-live="polite" style={SR_ONLY}>
        {sentence}
      </p>
    </>
  )
}

/** Visually hidden, but present in the accessibility tree (a polite live region). */
const SR_ONLY: CSSProperties = {
  position: 'absolute',
  width: 1,
  height: 1,
  margin: -1,
  padding: 0,
  border: 0,
  overflow: 'hidden',
  clip: 'rect(0 0 0 0)',
  whiteSpace: 'nowrap',
}
