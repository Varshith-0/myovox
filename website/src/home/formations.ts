/**
 * Particle formation targets for the homepage experience. Each builder returns
 * one xyz triple per particle; the vertex shader morphs between them as the
 * visitor scrolls. World frame: camera flies down -z, eye height y ≈ 2.
 *
 * The story anchor (`FOCUS`) is where everything converges and the logo forms:
 * directly ahead of where the camera comes to rest.
 */

export const FOCUS = { x: 0, y: 2, z: -262 } as const

/** Formation indices — must match the `formation()` switch in the vertex shader. */
export const DUST = 0
export const STREAMS = 1
export const CATHEDRAL = 2
export const WAVE = 3
export const POINT = 4
export const LOGO = 5

const rand = Math.random

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t
}

/** Sparse motes drifting around the camera's starting position. */
export function buildDust(n: number): Float32Array {
  const out = new Float32Array(n * 3)
  for (let i = 0; i < n; i++) {
    out[i * 3] = (rand() - 0.5) * 90
    out[i * 3 + 1] = 2 + (rand() - 0.5) * 52
    out[i * 3 + 2] = lerp(-50, 70, rand())
  }
  return out
}

/**
 * Bundles of sinuous currents sweeping across the visitor's view — the camera
 * looks down -z, so the filaments run along x to read as flowing lines.
 */
export function buildStreams(n: number): Float32Array {
  const LANES = 26
  const lanes = Array.from({ length: LANES }, () => ({
    y: 2 + (rand() - 0.5) * 36,
    z: lerp(-45, 8, rand()),
    phase: rand() * Math.PI * 2,
    amp: 1 + rand() * 2.5,
    tilt: (rand() - 0.5) * 0.12,
  }))
  const out = new Float32Array(n * 3)
  for (let i = 0; i < n; i++) {
    const lane = lanes[(rand() * LANES) | 0]
    const x = (rand() - 0.5) * 110
    const helixRadius = 0.12 + rand() * 0.4
    const angle = x * 0.4 + lane.phase + rand() * 0.2
    out[i * 3] = x
    out[i * 3 + 1] =
      lane.y +
      x * lane.tilt +
      Math.sin(x * 0.12 + lane.phase) * lane.amp +
      Math.sin(angle) * helixRadius
    out[i * 3 + 2] = lane.z + Math.cos(x * 0.1 + lane.phase) * 2 + Math.cos(angle) * helixRadius
  }
  return out
}

/**
 * The electric cathedral: fluted pillar rows, transverse arches, longitudinal
 * ribs, a gridded floor, and ambient volume dust. Nave runs z ∈ [12, -228].
 */
export function buildCathedral(n: number): Float32Array {
  const NAVE_HALF = 14
  const SPRING_Y = 15 // where arches leave the pillars
  const FLOOR_Y = -10
  const BAY_STEP = 16
  const Z_NEAR = 12
  const Z_FAR = -228
  const bays: number[] = []
  for (let z = Z_NEAR; z >= Z_FAR; z -= BAY_STEP) bays.push(z)

  const out = new Float32Array(n * 3)
  for (let i = 0; i < n; i++) {
    const pick = rand()
    let x: number, y: number, z: number

    if (pick < 0.4) {
      // Fluted pillars: inner nave rows, plus a sparser outer aisle.
      const outer = rand() < 0.3
      const side = rand() < 0.5 ? -1 : 1
      const cx = side * (outer ? 26 : NAVE_HALF)
      const bay = bays[(rand() * bays.length) | 0]
      y = lerp(FLOOR_Y, SPRING_Y, rand())
      const theta = rand() * Math.PI * 2
      const capital = Math.max(0, (y - SPRING_Y + 3) / 3) // flare near the top
      const radius = 1.5 + 0.25 * Math.sin(6 * theta + y * 0.9) + capital * 0.8
      x = cx + Math.cos(theta) * radius
      z = bay + Math.sin(theta) * radius
    } else if (pick < 0.72) {
      // Transverse arches spanning the nave at each bay.
      const bay = bays[(rand() * bays.length) | 0]
      const theta = rand() * Math.PI
      x = Math.cos(theta) * NAVE_HALF + (rand() - 0.5) * 0.35
      y = SPRING_Y + Math.sin(theta) * 9 + (rand() - 0.5) * 0.35
      z = bay + (rand() - 0.5) * 0.5
    } else if (pick < 0.84) {
      // Longitudinal ribs: springline rails and the apex ridge, full length.
      const which = rand()
      if (which < 0.4) {
        x = (rand() < 0.5 ? -1 : 1) * NAVE_HALF
        y = SPRING_Y
      } else if (which < 0.7) {
        x = 0
        y = SPRING_Y + 9
      } else {
        x = (rand() < 0.5 ? -1 : 1) * 7
        y = SPRING_Y + 7.2
      }
      x += (rand() - 0.5) * 0.5
      y += (rand() - 0.5) * 0.5
      z = lerp(Z_FAR, Z_NEAR, rand())
    } else if (pick < 0.94) {
      // Floor: scattered points pulled toward grid lines.
      const rawX = (rand() - 0.5) * 60
      const rawZ = lerp(Z_FAR, Z_NEAR, rand())
      x = lerp(rawX, Math.round(rawX / 7) * 7, 0.88)
      y = FLOOR_Y + rand() * 0.3
      z = lerp(rawZ, Math.round(rawZ / 8) * 8, 0.88)
    } else {
      // Ambient dust filling the volume.
      x = (rand() - 0.5) * 56
      y = lerp(FLOOR_Y, SPRING_Y + 12, rand())
      z = lerp(Z_FAR, Z_NEAR, rand())
    }

    out[i * 3] = x
    out[i * 3 + 1] = y
    out[i * 3 + 2] = z
  }
  return out
}

/** Stacked synchronized waves — muscle-signal traces, centered on the focus. */
export function buildWave(n: number): Float32Array {
  const ROWS = 28
  const rows = Array.from({ length: ROWS }, (_, r) => ({
    phase: r * 0.7 + rand() * 0.4,
    burstCenter: -0.3 + (r / ROWS) * 0.6 + (rand() - 0.5) * 0.2,
  }))
  const out = new Float32Array(n * 3)
  for (let i = 0; i < n; i++) {
    const r = (rand() * ROWS) | 0
    const row = rows[r]
    const u = rand() - 0.5 // -0.5..0.5 along the trace
    const x = u * 84
    const burst = Math.exp(-((u - row.burstCenter) ** 2) * 28)
    const signal =
      burst * (Math.sin(u * 55 + row.phase * 5) * 1.7 + Math.sin(u * 23 + row.phase) * 1.1) +
      Math.sin(u * 9 + row.phase) * 0.4
    out[i * 3] = x + (rand() - 0.5) * 0.2
    out[i * 3 + 1] = FOCUS.y + (r - ROWS / 2) * 1.7 + signal + (rand() - 0.5) * 0.08
    out[i * 3 + 2] = FOCUS.z + (r - ROWS / 2) * 0.4 + (rand() - 0.5) * 0.3
  }
  return out
}

/**
 * The MYOVOX logotype, sampled from rasterized Fraunces text. Returned in a
 * unit frame (width 1, centered on origin); the shader scales it to fit the
 * viewport and re-centers it on the focus point.
 */
export async function buildLogo(n: number): Promise<{ points: Float32Array; aspect: number }> {
  const W = 1400
  const H = 400
  try {
    await document.fonts.load('500 220px "Fraunces Variable"')
  } catch {
    /* fallback serif still samples fine */
  }
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return { points: new Float32Array(n * 3), aspect: 0.25 }
  ctx.fillStyle = '#fff'
  ctx.font = '500 220px "Fraunces Variable", Georgia, serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('MYOVOX', W / 2, H / 2)

  const data = ctx.getImageData(0, 0, W, H).data
  const candidates: number[] = []
  let minX = W
  let maxX = 0
  for (let py = 0; py < H; py += 1) {
    for (let px = 0; px < W; px += 1) {
      if (data[(py * W + px) * 4 + 3] > 120) {
        candidates.push(px, py)
        if (px < minX) minX = px
        if (px > maxX) maxX = px
      }
    }
  }
  const textWidth = Math.max(1, maxX - minX)
  const points = new Float32Array(n * 3)
  const count = candidates.length / 2
  for (let i = 0; i < n; i++) {
    const c = (rand() * count) | 0
    const px = candidates[c * 2] + rand()
    const py = candidates[c * 2 + 1] + rand()
    points[i * 3] = (px - W / 2) / textWidth
    points[i * 3 + 1] = -(py - H / 2) / textWidth
    points[i * 3 + 2] = (rand() - 0.5) * 0.012
  }
  return { points, aspect: H / textWidth }
}
