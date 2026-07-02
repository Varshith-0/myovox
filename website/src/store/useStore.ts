/**
 * The single small zustand store. It holds only *React-facing* state that
 * changes infrequently: the active stage index, the reduced-motion flag, and
 * narration / playback state. The high-frequency scroll value (updated every
 * frame) lives in {@link module:store/scroll} instead, so per-frame scroll
 * updates never trigger React re-renders. Components subscribe with selectors.
 */
import { create } from 'zustand'

export interface AppState {
  /** Stage nearest the current scroll position (drives the active caption). */
  stageIndex: number
  /** User prefers reduced motion. */
  reducedMotion: boolean
  /** Narration ("Voice") armed — off until the user opts in (also the audio
   *  unlock gesture browsers require). Narration is only audible during Play. */
  narrationOn: boolean
  /** Word-synced caption subtitles shown — ON by default (WCAG 1.2.2/1.2.4).
   *  Driven by the scroll position while reading, by the audio playhead in Play. */
  subtitlesOn: boolean
  /** Narration volume, 0..1 (only audible while {@link narrationOn}). */
  volume: number
  /** Hands-free playback is running (auto-advancing the story). */
  playing: boolean
  /** Playback speed multiplier (1×–5×) — scales both scroll and the voice. */
  playSpeed: number
  /** The active clip's frames aren't ready to draw yet (fast-scrolled past the
   *  preload window) — drives the "rendering…" overlay and gates Play. */
  mediaLoading: boolean
  /** Bumped to ask the PlayButton to (re)start hands-free playback — the seam the
   *  reel's end-card "Replay" uses without reaching into PlayButton internals. */
  playNonce: number
  /** The reel's end-card is showing — subtitles hide so the CTA reads cleanly. */
  endCardShown: boolean

  setStageIndex: (i: number) => void
  setReducedMotion: (reduced: boolean) => void
  setNarrationOn: (on: boolean) => void
  setSubtitlesOn: (on: boolean) => void
  setVolume: (v: number) => void
  setPlaying: (playing: boolean) => void
  setPlaySpeed: (speed: number) => void
  setMediaLoading: (loading: boolean) => void
  requestPlay: () => void
  setEndCardShown: (shown: boolean) => void
}

export const useStore = create<AppState>((set) => ({
  stageIndex: 0,
  reducedMotion: false,
  narrationOn: false,
  subtitlesOn: true,
  volume: 1,
  playing: false,
  playSpeed: 1,
  mediaLoading: false,
  playNonce: 0,
  endCardShown: false,

  setStageIndex: (stageIndex) =>
    set((s) => (s.stageIndex === stageIndex ? s : { ...s, stageIndex })),
  setReducedMotion: (reducedMotion) =>
    set((s) => (s.reducedMotion === reducedMotion ? s : { ...s, reducedMotion })),
  setNarrationOn: (narrationOn) => set((s) => (s.narrationOn === narrationOn ? s : { ...s, narrationOn })),
  setSubtitlesOn: (subtitlesOn) => set((s) => (s.subtitlesOn === subtitlesOn ? s : { ...s, subtitlesOn })),
  setVolume: (volume) => set((s) => (s.volume === volume ? s : { ...s, volume })),
  setPlaying: (playing) => set((s) => (s.playing === playing ? s : { ...s, playing })),
  setPlaySpeed: (playSpeed) => set((s) => (s.playSpeed === playSpeed ? s : { ...s, playSpeed })),
  setMediaLoading: (mediaLoading) =>
    set((s) => (s.mediaLoading === mediaLoading ? s : { ...s, mediaLoading })),
  requestPlay: () => set((s) => ({ ...s, playNonce: s.playNonce + 1 })),
  setEndCardShown: (endCardShown) =>
    set((s) => (s.endCardShown === endCardShown ? s : { ...s, endCardShown })),
}))
