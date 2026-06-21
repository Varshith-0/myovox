/**
 * The hot-path scroll value, deliberately kept out of React/zustand.
 *
 * ScrollTrigger writes `progress` here every frame (see {@link useScrollProgress});
 * the WebGL scene reads it imperatively inside `useFrame`. Because it is a plain
 * module-level value, updating it 60×/second costs nothing and never re-renders
 * the React tree — the core decoupling the architecture depends on.
 */

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

const state = { progress: 0 }

/** Normalized scroll progress across the whole story, 0 (top) → 1 (bottom). */
export const scroll = {
  get progress(): number {
    return state.progress
  },
  set progress(v: number) {
    state.progress = clamp01(v)
  },
}
