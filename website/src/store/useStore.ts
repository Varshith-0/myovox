/**
 * The single small zustand store. It holds only *React-facing* state that
 * changes infrequently: the active stage index, environment flags, narration /
 * playback state, and the loader gate. The high-frequency scroll value (updated
 * every frame) lives in {@link module:store/scroll} instead, so per-frame scroll
 * updates never trigger React re-renders. Components subscribe with selectors.
 */
import { create } from 'zustand'

export interface AppState {
  /** Stage nearest the current scroll position (drives the active caption). */
  stageIndex: number
  /** Small viewport (phone / coarse pointer). */
  isMobile: boolean
  /** User prefers reduced motion. */
  reducedMotion: boolean
  /** Initial load gate for the loader overlay. */
  ready: boolean
  /** Index of the word currently being "spoken" on the Talking stage. */
  speechWord: number
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

  setStageIndex: (i: number) => void
  setReady: (ready: boolean) => void
  setSpeechWord: (i: number) => void
  setNarrationOn: (on: boolean) => void
  setSubtitlesOn: (on: boolean) => void
  setVolume: (v: number) => void
  setPlaying: (playing: boolean) => void
  setPlaySpeed: (speed: number) => void
  setEnv: (env: Partial<Pick<AppState, 'isMobile' | 'reducedMotion'>>) => void
}

export const useStore = create<AppState>((set) => ({
  stageIndex: 0,
  isMobile: false,
  reducedMotion: false,
  ready: true, // no WebGL scene to wait on — the story is Manim clips
  speechWord: 0,
  narrationOn: false,
  subtitlesOn: true,
  volume: 1,
  playing: false,
  playSpeed: 1,

  setStageIndex: (stageIndex) =>
    set((s) => (s.stageIndex === stageIndex ? s : { ...s, stageIndex })),
  setReady: (ready) => set({ ready }),
  setSpeechWord: (speechWord) =>
    set((s) => (s.speechWord === speechWord ? s : { ...s, speechWord })),
  setNarrationOn: (narrationOn) => set((s) => (s.narrationOn === narrationOn ? s : { ...s, narrationOn })),
  setSubtitlesOn: (subtitlesOn) => set((s) => (s.subtitlesOn === subtitlesOn ? s : { ...s, subtitlesOn })),
  setVolume: (volume) => set((s) => (s.volume === volume ? s : { ...s, volume })),
  setPlaying: (playing) => set((s) => (s.playing === playing ? s : { ...s, playing })),
  setPlaySpeed: (playSpeed) => set((s) => (s.playSpeed === playSpeed ? s : { ...s, playSpeed })),
  setEnv: (env) => set(env),
}))
