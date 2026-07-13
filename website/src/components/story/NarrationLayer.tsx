import { useEffect, useMemo, useRef } from 'react'
import { useStages } from '@/story/StagesContext'
import { useStore } from '@/store/useStore'
import { narration } from '@/store/narration'
import { clamp01 } from '@/lib/num'
import { animDir, assetUrl } from '@/lib/asset'

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

/** Local scroll progress through a section: 0 at its top, 1 once scrolled out. */
function localProgressFor(id: string): number {
  const el = document.getElementById(id)
  if (!el) return 0
  const r = el.getBoundingClientRect()
  return clamp01((0 - r.top) / (r.height || 1))
}

export function NarrationLayer() {
  const stages = useStages()
  // Stage ids in order + an id→index map (O(1) "near the active stage" check).
  // Every stage carries a narration clip, so membership == has-narration.
  const narratedIds = useMemo(() => stages.map((s) => s.id), [stages])
  const index = useMemo(() => new Map(narratedIds.map((id, i) => [id, i])), [narratedIds])
  const hasNarration = useMemo(() => {
    const set = new Set(narratedIds)
    return (id: string) => set.has(id)
  }, [narratedIds])

  const audios = useRef(new Map<string, HTMLAudioElement>())
  // The clip currently playing — switched only when the active stage changes.
  const voiced = useRef<string | null>(null)

  useEffect(() => {
    const audioMap = audios.current
    let raf = 0
    // The clip switched before its metadata arrived — align to the scroll once
    // the duration is known, so a cold Play never rewinds to the sentence start.
    let alignNeeded = false
    // play()'s outcome is the autoplay-block / broken-clip signal. While blocked,
    // {@link PlayButton} paces by constant velocity instead of this playhead.
    const tryPlay = (audio: HTMLAudioElement) => {
      audio.play().then(
        () => {
          narration.blocked = false
        },
        () => {
          narration.blocked = true
        },
      )
    }
    const scrollMatchedTime = (id: string, duration: number) =>
      clamp01(localProgressFor(id)) * duration
    const tick = () => {
      const { stageIndex, narrationOn, playing, volume, playSpeed, mediaLoading } =
        useStore.getState()
      const activeId = stages[stageIndex]?.id ?? null
      // Voice is part of Play: only sound while both are on.
      const shouldPlay = narrationOn && playing
      const target = shouldPlay && activeId && hasNarration(activeId) ? activeId : null

      // Fetch the active clip and its immediate neighbours only.
      for (const [id, audio] of audioMap) {
        if (Math.abs((index.get(id) ?? -1) - stageIndex) <= 1) {
          const url = assetUrl(`${animDir(id)}/audio/${id}.mp3`)
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
        if (next && target) {
          const dur = next.duration
          alignNeeded = !(Number.isFinite(dur) && dur > 0)
          next.currentTime = alignNeeded ? 0 : scrollMatchedTime(target, dur)
          next.volume = clamp01(volume)
          next.playbackRate = playSpeed
          tryPlay(next)
        } else {
          alignNeeded = false
          narration.blocked = false
        }
      }

      const cur = voiced.current ? audioMap.get(voiced.current) : undefined
      if (shouldPlay && voiced.current && cur) {
        cur.volume = clamp01(volume)
        cur.playbackRate = playSpeed
        const dur = Number.isFinite(cur.duration) ? cur.duration : 0
        if (alignNeeded && dur > 0) {
          cur.currentTime = scrollMatchedTime(voiced.current, dur)
          alignNeeded = false
        }
        // Video-player behavior: when the animation's frames aren't ready
        // (mediaLoading), the sound pauses with the picture and resumes when
        // it's back — the voice never talks over a black canvas.
        if (mediaLoading) {
          if (!cur.paused) cur.pause()
        } else if (cur.paused && !cur.ended) {
          // A blocked clip re-aligns to the scroll before each retry, so the
          // moment a user gesture unlocks audio the voice joins mid-sentence
          // instead of yanking the story back to where the block began.
          if (narration.blocked && dur > 0) {
            const t = scrollMatchedTime(voiced.current, dur)
            if (Math.abs(cur.currentTime - t) > 0.25) cur.currentTime = t
          }
          tryPlay(cur)
        }
      }

      // Publish the playhead for the subtitles. In Play the audio is the clock;
      // while reading — or while audio is blocked — subtitles follow the SCROLL
      // position mapped onto the active section's caption track, so captions
      // stay live (and on by default) even when the voice can't sound.
      if (shouldPlay && voiced.current && cur && !narration.blocked) {
        narration.activeId = voiced.current
        narration.time = cur.currentTime
        narration.duration = Number.isFinite(cur.duration) ? cur.duration : 0
        narration.playing = !cur.paused && !cur.ended
        narration.ended = cur.ended
      } else {
        const sid = activeId && hasNarration(activeId) ? activeId : null
        const audio = sid ? audioMap.get(sid) : undefined
        const dur = audio && Number.isFinite(audio.duration) ? audio.duration : 0
        narration.activeId = sid
        narration.time = sid && dur > 0 ? scrollMatchedTime(sid, dur) : 0
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
      narration.blocked = false
    }
  }, [stages, index, hasNarration])

  return (
    <div aria-hidden="true" style={{ display: 'none' }}>
      {narratedIds.map((id) => (
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
