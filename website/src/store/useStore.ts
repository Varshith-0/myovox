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

  setStageIndex: (i: number) => void
  setReady: (ready: boolean) => void
  setElectrodesReady: (ready: boolean) => void
  setSpeechWord: (i: number) => void
  setEnv: (env: Partial<Pick<AppState, 'isMobile' | 'reducedMotion' | 'lowPower' | 'dpr'>>) => void
}

export const useStore = create<AppState>((set) => ({
  stageIndex: 0,
  isMobile: false,
  reducedMotion: false,
  lowPower: false,
  dpr: 1.5,
  ready: false,
  electrodesReady: false,
  speechWord: 0,

  setStageIndex: (stageIndex) =>
    set((s) => (s.stageIndex === stageIndex ? s : { ...s, stageIndex })),
  setReady: (ready) => set({ ready }),
  setElectrodesReady: (electrodesReady) =>
    set((s) => (s.electrodesReady === electrodesReady ? s : { ...s, electrodesReady })),
  setSpeechWord: (speechWord) =>
    set((s) => (s.speechWord === speechWord ? s : { ...s, speechWord })),
  setEnv: (env) => set(env),
}))
