import { useEffect, useRef, useState } from 'react'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'
import styles from './Subtitles.module.css'

/**
 * YouTube-style subtitles: one punctuated sentence at a time, with the spoken
 * word lit in step. Shown only while narration is actually playing. It follows
 * the {@link NarrationLayer}'s active clip + playhead (via the {@link narration}
 * hot-state) and reads the sentence cues baked beside each clip
 * (`<id>.captions.json`, from `scripts/narrate.py`).
 */

const BASE = import.meta.env.BASE_URL
const ASSET_VER = import.meta.env.DEV ? String(Date.now()) : __BUILD_ID__
const capsUrl = (id: string) => `${BASE}anim/${id}.captions.json?v=${ASSET_VER}`

interface CueWord {
  w: string
  t: number
}
interface Cue {
  t: number
  end: number | null
  words: CueWord[]
}

/** Index of the last item whose start time has passed `time` (or -1). */
function lastBefore<T extends { t: number }>(items: T[], time: number): number {
  let lo = 0
  let hi = items.length - 1
  let found = -1
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    if (items[mid].t <= time) {
      found = mid
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  return found
}

/** No leading space before a word that begins with closing punctuation. */
const NO_LEAD = /^[.,!?;:’'")\]…—-]/

export function Subtitles() {
  const on = useStore((s) => s.narrationOn)
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
        const res = await fetch(capsUrl(clipId))
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

  return (
    <div className={styles.wrap} aria-hidden="true">
      <p className={styles.line}>
        {cue.words.map((word, i) => {
          const cls = i === wordIdx ? styles.now : i < wordIdx ? styles.spoken : styles.ahead
          const lead = i > 0 && !NO_LEAD.test(word.w) ? ' ' : ''
          return (
            <span key={i} className={cls}>
              {lead}
              {word.w}
            </span>
          )
        })}
      </p>
    </div>
  )
}
