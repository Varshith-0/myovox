import { useEffect, useRef } from 'react'
import { STAGES } from '@/data/stages'
import { NARRATED_IDS, hasNarration } from '@/data/narration'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'

/**
 * The narration engine. One hidden `<audio>` per stage; it plays the active
 * stage's clip straight through at natural rate — never scrubbed, so the voice
 * stays clean.
 *
 * Narration is bound to hands-free **Play**: it sounds only while `playing` and
 * `narrationOn`. Stopping Play (or any manual scroll, which stops Play) pauses
 * it. While playing, {@link PlayButton} paces the scroll to this clip's playhead
 * so the animation and voice stay locked together; the play speed scales the
 * voice via `playbackRate`, so 2×/3× speeds both in step.
 *
 * Each frame it publishes the playhead to the {@link narration} hot-state for
 * the {@link Subtitles} overlay.
 */

const BASE = import.meta.env.BASE_URL
const ASSET_VER = import.meta.env.DEV ? String(Date.now()) : __BUILD_ID__
const audioUrl = (id: string) => `${BASE}anim/${id}.mp3?v=${ASSET_VER}`
const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

// Stage id → index, so the "load only near the active stage" check is O(1).
const INDEX = new Map(STAGES.map((s, i) => [s.id, i]))

/** Local scroll progress through a section: 0 at its top, 1 once scrolled out. */
function localProgressFor(id: string): number {
  const el = document.getElementById(id)
  if (!el) return 0
  const r = el.getBoundingClientRect()
  return clamp01((0 - r.top) / (r.height || 1))
}

export function NarrationLayer() {
  const audios = useRef(new Map<string, HTMLAudioElement>())
  // The clip currently playing — switched only when the active stage changes.
  const voiced = useRef<string | null>(null)

  useEffect(() => {
    const audioMap = audios.current
    let raf = 0
    const tick = () => {
      const { stageIndex, narrationOn, playing, volume, playSpeed } = useStore.getState()
      const activeId = STAGES[stageIndex]?.id ?? null
      // Voice is part of Play: only sound while both are on.
      const shouldPlay = narrationOn && playing
      const target = shouldPlay && activeId && hasNarration(activeId) ? activeId : null

      // Fetch the active clip and its immediate neighbours only.
      for (const [id, audio] of audioMap) {
        if (Math.abs((INDEX.get(id) ?? -1) - stageIndex) <= 1) {
          const url = audioUrl(id)
          if (audio.getAttribute('src') !== url) audio.setAttribute('src', url)
        }
      }

      // Switch clips only on a real change — then play through cleanly. Start at
      // the point that matches the current scroll, so pressing Play mid-stage (or
      // arming Voice mid-play) picks the voice up from that moment, like a video.
      if (target !== voiced.current) {
        const prev = voiced.current ? audioMap.get(voiced.current) : undefined
        if (prev) {
          prev.pause()
          prev.currentTime = 0
        }
        voiced.current = target
        const next = target ? audioMap.get(target) : undefined
        if (next) {
          const dur = next.duration
          next.currentTime =
            target && Number.isFinite(dur) && dur > 0 ? clamp01(localProgressFor(target)) * dur : 0
          next.volume = clamp01(volume)
          next.playbackRate = playSpeed
          next.play().catch(() => {})
        }
      }

      // Publish the playhead for the subtitles. In Play the audio is the clock;
      // while reading (no audio), subtitles follow the SCROLL position mapped
      // onto the active section's caption track, so captions are on by default.
      if (shouldPlay && voiced.current) {
        const cur = audioMap.get(voiced.current)
        if (cur) {
          cur.volume = clamp01(volume)
          cur.playbackRate = playSpeed
        }
        narration.activeId = voiced.current
        narration.time = cur ? cur.currentTime : 0
        narration.duration = cur && Number.isFinite(cur.duration) ? cur.duration : 0
        narration.playing = !!cur && !cur.paused && !cur.ended
        narration.ended = !!cur && cur.ended
      } else {
        const sid = activeId && hasNarration(activeId) ? activeId : null
        const audio = sid ? audioMap.get(sid) : undefined
        const dur = audio && Number.isFinite(audio.duration) ? audio.duration : 0
        narration.activeId = sid
        narration.time = sid && dur > 0 ? clamp01(localProgressFor(sid)) * dur : 0
        narration.duration = dur
        narration.playing = false
        narration.ended = false
      }

      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      for (const a of audioMap.values()) a.pause()
    }
  }, [])

  return (
    <div aria-hidden="true" style={{ display: 'none' }}>
      {NARRATED_IDS.map((id) => (
        <audio
          key={id}
          ref={(el) => {
            if (el) audios.current.set(id, el)
            else audios.current.delete(id)
          }}
          preload="auto"
        />
      ))}
    </div>
  )
}
