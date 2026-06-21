/**
 * Electrode anchor positions snapped onto the *actual* solid-head surface, in
 * HeadRig-local space (so they rotate with the head). Populated once by FaceHead
 * after the glb loads — see {@link module:three/electrodeSnap} — and read by the
 * Electrodes layer. Kept as a plain module value (like {@link sceneSample}) so it
 * lives outside React's render path; a zustand `electrodesReady` flag signals
 * when it has been filled.
 */
export const electrodeAnchors: {
  positions: Float32Array // 3 per electrode (disc resting on the skin)
  leads: Float32Array // 6 per electrode (line segment: skin → outward)
  phases: Float32Array // pulse phase per electrode
  count: number
} = {
  positions: new Float32Array(0),
  leads: new Float32Array(0),
  phases: new Float32Array(0),
  count: 0,
}
