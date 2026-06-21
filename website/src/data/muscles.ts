/**
 * Speech-articulation muscle map for the "Talking" stage.
 *
 * Positions and muscle attributions are derived from the emg2speech papers
 * (Gowda, Comstock & Miller; the 31-channel General Corpus rig over neck, chin,
 * jaw, cheek and lips) — see the papers/ folder. Coordinates are on the
 * front-facing normalized head: +x = viewer's right, +y = up (eyeline ≈ 0.25,
 * mouth ≈ −0.35, jaw ≈ −0.7, throat ≈ −1.0), z = depth out of the face.
 *
 * Each muscle belongs to a functional GROUP; the groups activate on different
 * rhythms during speech ({@link groupActivation}) so the face reads as talking.
 */

export const GROUPS = ['lip', 'cheek', 'jawClose', 'jawOpen', 'tongue', 'throat'] as const
export type MuscleGroup = (typeof GROUPS)[number]
export const groupIndex = (g: MuscleGroup): number => GROUPS.indexOf(g)

export interface Muscle {
  readonly id: string
  readonly group: MuscleGroup
  readonly pos: readonly [number, number, number]
  /** Relative activation weight during continuous speech (0..1). */
  readonly weight: number
  /** Cluster radius on the face surface. */
  readonly radius: number
}

/** A named callout shown on the talking stage (subset of muscles, to stay legible). */
export interface MuscleLabel {
  readonly id: string
  readonly text: string
  readonly sub: string
  readonly pos: readonly [number, number, number]
  readonly side: 'left' | 'right'
  /** The functional group this callout names — its label brightens as that group fires. */
  readonly group: MuscleGroup
}

// NOTE: anchors are in normalized head space (+x = viewer's right, +y = up,
// +z = out of the face) and are then fit-scaled 0.72 and lifted [0,0.18,0] onto
// the SOLID talking head in Muscles.tsx. Empirically (verified in screenshots)
// the +0.18 lift means nominal y reads higher than it looks: on the solid head
// nose ≈ y+0.13, eyes ≈ y+0.30, lips ≈ y−0.10, chin ≈ y−0.25, submental ≈ y−0.40,
// larynx ≈ y−0.55, low neck ≈ y−0.70. Positions below place each muscle on the
// correct anatomy for the solid head; the five callouts in MUSCLE_LABELS share
// these anchors.
export const MUSCLES: readonly Muscle[] = [
  // Lips — orbicularis oris ring + depressors (fastest, per-syllable transients).
  { id: 'oo-upper', group: 'lip', pos: [0.0, 0.01, 0.72], weight: 1.0, radius: 0.08 },
  { id: 'oo-lower', group: 'lip', pos: [0.0, -0.12, 0.7], weight: 1.0, radius: 0.08 },
  { id: 'dli-l', group: 'lip', pos: [0.13, -0.2, 0.62], weight: 0.7, radius: 0.07 },
  { id: 'dli-r', group: 'lip', pos: [-0.13, -0.2, 0.62], weight: 0.7, radius: 0.07 },
  { id: 'dao-l', group: 'lip', pos: [0.26, -0.14, 0.56], weight: 0.5, radius: 0.07 },
  { id: 'dao-r', group: 'lip', pos: [-0.26, -0.14, 0.56], weight: 0.5, radius: 0.07 },
  { id: 'mentalis', group: 'lip', pos: [0.0, -0.28, 0.58], weight: 0.5, radius: 0.07 },
  // Cheeks — zygomaticus major (cheekbone → mouth corner) / risorius.
  { id: 'zyg-l', group: 'cheek', pos: [0.42, 0.06, 0.52], weight: 0.8, radius: 0.1 },
  { id: 'zyg-r', group: 'cheek', pos: [-0.42, 0.06, 0.52], weight: 0.8, radius: 0.1 },
  { id: 'ris-l', group: 'cheek', pos: [0.52, -0.06, 0.46], weight: 0.5, radius: 0.08 },
  { id: 'ris-r', group: 'cheek', pos: [-0.52, -0.06, 0.46], weight: 0.5, radius: 0.08 },
  // Jaw closers — masseter (over the jaw angle, lateral + low) / temporalis (temple).
  { id: 'mas-l', group: 'jawClose', pos: [0.64, -0.28, 0.34], weight: 0.9, radius: 0.1 },
  { id: 'mas-r', group: 'jawClose', pos: [-0.64, -0.28, 0.34], weight: 0.9, radius: 0.1 },
  { id: 'tem-l', group: 'jawClose', pos: [0.7, 0.4, 0.26], weight: 0.5, radius: 0.1 },
  { id: 'tem-r', group: 'jawClose', pos: [-0.7, 0.4, 0.26], weight: 0.5, radius: 0.1 },
  // Tongue (via submental, under the chin) — near-continuous high baseline.
  { id: 'gen-l', group: 'tongue', pos: [0.1, -0.34, 0.46], weight: 1.0, radius: 0.08 },
  { id: 'gen-r', group: 'tongue', pos: [-0.1, -0.34, 0.46], weight: 1.0, radius: 0.08 },
  { id: 'hyo-l', group: 'tongue', pos: [0.24, -0.36, 0.42], weight: 0.85, radius: 0.08 },
  { id: 'hyo-r', group: 'tongue', pos: [-0.24, -0.36, 0.42], weight: 0.85, radius: 0.08 },
  // Jaw openers — digastric / suprahyoid (antiphase to closers).
  { id: 'dig-l', group: 'jawOpen', pos: [0.16, -0.54, 0.42], weight: 0.8, radius: 0.08 },
  { id: 'dig-r', group: 'jawOpen', pos: [-0.16, -0.54, 0.42], weight: 0.8, radius: 0.08 },
  // Throat / larynx — sternohyoid (front of neck, low) / platysma (slow prosody).
  { id: 'sth-l', group: 'throat', pos: [0.1, -0.66, 0.34], weight: 0.6, radius: 0.09 },
  { id: 'sth-r', group: 'throat', pos: [-0.1, -0.66, 0.34], weight: 0.6, radius: 0.09 },
  { id: 'pla-l', group: 'throat', pos: [0.3, -0.78, 0.3], weight: 0.45, radius: 0.1 },
  { id: 'pla-r', group: 'throat', pos: [-0.3, -0.78, 0.3], weight: 0.45, radius: 0.1 },
] as const

export const MUSCLE_LABELS: readonly MuscleLabel[] = [
  {
    id: 'l-oo',
    text: 'Orbicularis oris',
    sub: 'lips · rounding & closure',
    pos: [0.0, -0.06, 0.72],
    side: 'right',
    group: 'lip',
  },
  {
    id: 'l-zyg',
    text: 'Zygomaticus',
    sub: 'cheek · lip spreading',
    pos: [0.42, 0.06, 0.52],
    side: 'right',
    group: 'cheek',
  },
  { id: 'l-mas', text: 'Masseter', sub: 'jaw · closing', pos: [-0.64, -0.28, 0.34], side: 'left', group: 'jawClose' },
  {
    id: 'l-gen',
    text: 'Genioglossus',
    sub: 'tongue · protrusion',
    pos: [0.0, -0.34, 0.46],
    side: 'left',
    group: 'tongue',
  },
  {
    id: 'l-sth',
    text: 'Sternohyoid',
    sub: 'larynx · pitch',
    pos: [0.0, -0.66, 0.34],
    side: 'right',
    group: 'throat',
  },
] as const

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

/**
 * Per-group activation (0..1) at time `t` seconds — the "talking" rhythm.
 * Jaw open/close oscillate in antiphase (the syllable beat); lips and cheeks
 * fire as faster transients; the tongue holds a high flickering baseline; the
 * throat modulates slowly (prosody). Layering follows the papers' description.
 */
export function groupActivation(t: number): number[] {
  const TAU = Math.PI * 2
  const syllable = Math.sin(TAU * 2.1 * t) // ~2 syllables/sec
  const lip = 0.32 + 0.68 * Math.abs(Math.sin(TAU * 3.1 * t + 0.6))
  const cheek = 0.28 + 0.52 * Math.abs(Math.sin(TAU * 1.9 * t + 1.7))
  const jawClose = clamp01(Math.max(0, syllable) * 1.1)
  const jawOpen = clamp01(Math.max(0, -syllable) * 1.1)
  const tongue = 0.55 + 0.45 * Math.abs(Math.sin(TAU * 2.6 * t))
  const throat = 0.3 + 0.35 * (0.5 + 0.5 * Math.sin(TAU * 0.5 * t))
  // index order must match GROUPS
  return [clamp01(lip), clamp01(cheek), jawClose, jawOpen, clamp01(tongue), clamp01(throat)]
}

export interface MuscleCloud {
  positions: Float32Array
  groupIdx: Float32Array
  weights: Float32Array
  rand: Float32Array
  count: number
}

/** Expand each muscle into a small jittered cluster of points (a glowing patch). */
export function buildMuscleCloud(perMuscle = 102): MuscleCloud {
  const count = MUSCLES.length * perMuscle
  const positions = new Float32Array(count * 3)
  const groupIdx = new Float32Array(count)
  const weights = new Float32Array(count)
  const rand = new Float32Array(count)
  let k = 0
  for (const m of MUSCLES) {
    const gi = groupIndex(m.group)
    for (let i = 0; i < perMuscle; i++) {
      // Disc jitter within the muscle radius, hugging the face surface.
      const a = Math.random() * Math.PI * 2
      const r = Math.sqrt(Math.random()) * m.radius
      positions[k * 3] = m.pos[0] + Math.cos(a) * r
      positions[k * 3 + 1] = m.pos[1] + Math.sin(a) * r
      positions[k * 3 + 2] = m.pos[2] + (Math.random() - 0.5) * 0.05
      groupIdx[k] = gi
      weights[k] = m.weight
      rand[k] = Math.random()
      k++
    }
  }
  return { positions, groupIdx, weights, rand, count }
}
