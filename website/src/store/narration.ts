/**
 * Hot-path narration playback state, kept out of React/zustand (like
 * {@link module:store/scroll}). The {@link NarrationLayer} writes the active
 * clip's id and current playhead here every frame; the {@link Subtitles}
 * overlay reads it every frame to highlight the spoken word. A plain module
 * value means this 60×/second update never re-renders the tree.
 */
const state = {
  /** Id of the clip currently playing, or null when silent. */
  activeId: null as string | null,
  /** Playhead position in seconds. */
  time: 0,
  /** Clip duration in seconds (0 until known). */
  duration: 0,
  /** Whether audio is actually playing right now. */
  playing: false,
  /** The active clip has played to its end (drives the stage handoff). */
  ended: false,
}

export const narration = state
