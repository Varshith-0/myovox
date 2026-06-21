/**
 * Anchor geometry for the face-mounted scene elements (electrodes, signal
 * origins). Positions are generated on a spheroid approximating the baked head's
 * normalized bounds (≈ ±1.29 × ±1.2 × ±0.82), so they sit on the front of the
 * face/jaw/throat region and rotate with the head rig.
 */

// Head half-extents in normalized world units (matches scripts/bake-head.mjs).
const AX = 1.27
const AY = 1.2
const AZ = 0.82

/** A point on the front-face spheroid at height `y` and azimuth `theta` (0 = forward). */
function frontPoint(y: number, theta: number): [number, number, number] {
  const k2 = Math.max(0, 1 - (y / AY) ** 2)
  const k = Math.sqrt(k2)
  const x = AX * k * Math.sin(theta)
  const z = AZ * k * Math.cos(theta)
  return [x, y, z]
}

export interface Electrodes {
  positions: Float32Array // 3 per electrode
  phases: Float32Array // pulse phase per electrode
  leads: Float32Array // 6 per electrode (line segment: anchor → outward)
  count: number
}

/** The 31-channel grid, laid out in rows over cheek, jaw, and throat. */
export function generateElectrodes(): Electrodes {
  const rows: { y: number; n: number; spread: number }[] = [
    { y: 0.45, n: 5, spread: 0.95 },
    { y: 0.16, n: 6, spread: 1.05 },
    { y: -0.13, n: 6, spread: 1.05 },
    { y: -0.42, n: 6, spread: 0.98 },
    { y: -0.72, n: 5, spread: 0.85 },
    { y: -1.0, n: 3, spread: 0.55 },
  ]
  const pts: number[] = []
  const leads: number[] = []
  const phases: number[] = []
  for (const row of rows) {
    for (let i = 0; i < row.n; i++) {
      const t = row.n === 1 ? 0 : (i / (row.n - 1)) * 2 - 1 // -1..1
      const theta = t * row.spread
      const [x, y, z] = frontPoint(row.y, theta)
      pts.push(x, y, z)
      // lead line: from the anchor outward along the radial direction
      const len = Math.hypot(x, y, z) || 1
      const ox = (x / len) * 0.16
      const oy = (y / len) * 0.16
      const oz = (z / len) * 0.16
      leads.push(x, y, z, x + ox, y + oy, z + oz)
      phases.push(Math.random())
    }
  }
  return {
    positions: new Float32Array(pts),
    phases: new Float32Array(phases),
    leads: new Float32Array(leads),
    count: phases.length,
  }
}

/**
 * Random points across the front face — origins for the signal stream. Returns
 * positions, an outward/forward direction for each (toward the viewer), and a
 * per-particle phase offset for the streaming animation.
 */
export function sampleFaceOrigins(n: number): {
  positions: Float32Array
  dirs: Float32Array
  offsets: Float32Array
} {
  const positions = new Float32Array(n * 3)
  const dirs = new Float32Array(n * 3)
  const offsets = new Float32Array(n)
  for (let i = 0; i < n; i++) {
    offsets[i] = Math.random()
    const y = -1.0 + Math.random() * 1.5
    const theta = (Math.random() * 2 - 1) * 1.15
    const [x, py, z] = frontPoint(y, theta)
    positions[i * 3] = x
    positions[i * 3 + 1] = py
    positions[i * 3 + 2] = z
    // Stream mostly forward (+Z) with a little radial spread.
    const len = Math.hypot(x, py, z) || 1
    dirs[i * 3] = (x / len) * 0.4
    dirs[i * 3 + 1] = (py / len) * 0.4
    dirs[i * 3 + 2] = 0.9
  }
  return { positions, dirs, offsets }
}
