/**
 * The single small zustand store. It holds only *React-facing* state that
 * changes infrequently: the active stage index, environment flags, and asset
 * readiness. The high-frequency scroll value (updated every frame) lives in
 * {@link module:store/scroll} instead, so per-frame scroll updates never
 * trigger React re-renders. Components subscribe with selectors; the 3D scene
 * reads progress imperatively.
 */
import { create } from 'zustand'

export interface AppState {
  /** Stage nearest the current scroll position (drives the active caption). */
  stageIndex: number
  /** Small viewport (phone / coarse pointer). */
  isMobile: boolean
  /** User prefers reduced motion. */
  reducedMotion: boolean
  /** Simplify the scene: mobile, reduced-motion, or weak hardware. */
  lowPower: boolean
  /** Device pixel ratio to render the canvas at (clamped). */
  dpr: number
  /** The head point cloud has loaded — gate the loader overlay. */
  ready: boolean
  /** Electrodes have been snapped onto the loaded head mesh (see electrodeSnap). */
  electrodesReady: boolean
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
  setElectrodesReady: (ready: boolean) => void
  setSpeechWord: (i: number) => void
  setNarrationOn: (on: boolean) => void
  setSubtitlesOn: (on: boolean) => void
  setVolume: (v: number) => void
  setPlaying: (playing: boolean) => void
  setPlaySpeed: (speed: number) => void
  setEnv: (env: Partial<Pick<AppState, 'isMobile' | 'reducedMotion' | 'lowPower' | 'dpr'>>) => void
}

export const useStore = create<AppState>((set) => ({
  stageIndex: 0,
  isMobile: false,
  reducedMotion: false,
  lowPower: false,
  dpr: 1.5,
  ready: true, // no WebGL scene to wait on — the story is Manim clips
  electrodesReady: false,
  speechWord: 0,
  narrationOn: false,
  subtitlesOn: true,
  volume: 1,
  playing: false,
  playSpeed: 1,

  setStageIndex: (stageIndex) =>
    set((s) => (s.stageIndex === stageIndex ? s : { ...s, stageIndex })),
  setReady: (ready) => set({ ready }),
  setElectrodesReady: (electrodesReady) =>
    set((s) => (s.electrodesReady === electrodesReady ? s : { ...s, electrodesReady })),
  setSpeechWord: (speechWord) =>
    set((s) => (s.speechWord === speechWord ? s : { ...s, speechWord })),
  setNarrationOn: (narrationOn) => set((s) => (s.narrationOn === narrationOn ? s : { ...s, narrationOn })),
  setSubtitlesOn: (subtitlesOn) => set((s) => (s.subtitlesOn === subtitlesOn ? s : { ...s, subtitlesOn })),
  setVolume: (volume) => set((s) => (s.volume === volume ? s : { ...s, volume })),
  setPlaying: (playing) => set((s) => (s.playing === playing ? s : { ...s, playing })),
  setPlaySpeed: (playSpeed) => set((s) => (s.playSpeed === playSpeed ? s : { ...s, playSpeed })),
  setEnv: (env) => set(env),
}))
