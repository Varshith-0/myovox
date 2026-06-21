/**
 * Head point-cloud geometry.
 *
 * Two sources, same output shape:
 *  - {@link loadBakedHead} fetches `public/head-points.bin` — a flat
 *    Float32Array of interleaved [px,py,pz, nx,ny,nz] surface samples baked at
 *    author time from a realistic Creative-Commons head scan (see
 *    `scripts/bake-head.mjs`). This is the production head — unmistakably human.
 *  - {@link buildProceduralHead} synthesizes a head-shaped cloud with no asset,
 *    used as a graceful fallback if the binary is missing.
 *
 * Each renders identically: positions + per-point normals (for fresnel rim
 * shading) + a per-point random seed (for scatter direction and twinkle).
 */

export interface HeadData {
  positions: Float32Array // count * 3
  normals: Float32Array // count * 3
  seeds: Float32Array // count
  count: number
}

const FLOATS_PER_POINT = 6 // px,py,pz,nx,ny,nz

function randomSeeds(count: number): Float32Array {
  const seeds = new Float32Array(count)
  for (let i = 0; i < count; i++) seeds[i] = Math.random()
  return seeds
}

/**
 * Load the baked head binary and (optionally) subsample to `targetCount` points.
 * Returns null on any failure so the caller can fall back procedurally.
 */
export async function loadBakedHead(url: string, targetCount: number): Promise<HeadData | null> {
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    const buf = await res.arrayBuffer()
    const raw = new Float32Array(buf)
    const total = Math.floor(raw.length / FLOATS_PER_POINT)
    if (total < 100) return null

    const count = Math.min(targetCount, total)
    const stride = total / count // even subsample across the surface
    const positions = new Float32Array(count * 3)
    const normals = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const src = Math.floor(i * stride) * FLOATS_PER_POINT
      positions[i * 3] = raw[src]
      positions[i * 3 + 1] = raw[src + 1]
      positions[i * 3 + 2] = raw[src + 2]
      normals[i * 3] = raw[src + 3]
      normals[i * 3 + 1] = raw[src + 4]
      normals[i * 3 + 2] = raw[src + 5]
    }
    return { positions, normals, seeds: randomSeeds(count), count }
  } catch {
    return null
  }
}

/**
 * Build a head-shaped point cloud analytically: a vertically elongated spheroid
 * with a tapered jaw/chin. Not a substitute for the scanned head, but reads as a
 * head silhouette for the fallback path.
 */
export function buildProceduralHead(count: number): HeadData {
  const positions = new Float32Array(count * 3)
  const normals = new Float32Array(count * 3)
  const seeds = new Float32Array(count)

  // Semi-axes: width, height (elongated), depth (slightly shallow).
  const A = 1.0
  const B = 1.22
  const C = 0.92

  for (let i = 0; i < count; i++) {
    // Uniform point on a unit sphere.
    const u = Math.random()
    const v = Math.random()
    const theta = Math.acos(2 * u - 1)
    const phi = 2 * Math.PI * v
    const sx = Math.sin(theta) * Math.cos(phi)
    const sy = Math.cos(theta)
    const sz = Math.sin(theta) * Math.sin(phi)

    let x = sx * A
    let y = sy * B
    let z = sz * C

    // Taper the lower-front region into a jaw/chin.
    if (y < 0) {
      const t = Math.min(1, -y / B)
      x *= 1 - 0.34 * t
      z *= 1 - 0.12 * t
      y -= 0.06 * t // drop the chin a touch
    }
    // Flatten the back of the skull slightly.
    if (z < 0) z *= 0.94

    positions[i * 3] = x
    positions[i * 3 + 1] = y
    positions[i * 3 + 2] = z

    // Ellipsoid surface normal (gradient of x²/A² + y²/B² + z²/C²).
    let nx = x / (A * A)
    let ny = y / (B * B)
    let nz = z / (C * C)
    const len = Math.hypot(nx, ny, nz) || 1
    nx /= len
    ny /= len
    nz /= len
    normals[i * 3] = nx
    normals[i * 3 + 1] = ny
    normals[i * 3 + 2] = nz

    seeds[i] = Math.random()
  }

  return { positions, normals, seeds, count }
}
