/**
 * Snap a 31-channel speech-EMG grid onto the real head surface by raycasting.
 *
 * For each grid point we cast a ray from in *front* of the face straight back
 * (−Z) and take the first hit — the front skin surface — so every channel lands
 * on the actual geometry (front faces, not the culled back faces an inside-out
 * ray would hit). Points are returned in the space of `toLocal` (the HeadRig
 * group) so they rotate with the head. The grid covers the region a face array
 * sits on: cheeks → jaw → chin → upper neck.
 */
import * as THREE from 'three'

export interface SnappedElectrodes {
  positions: Float32Array
  leads: Float32Array
  phases: Float32Array
  count: number
}

// Rows over the lower face. yFrac is a fraction of the head's height measured up
// from its bbox bottom; xspread is the fraction of the head's half-width the row
// covers (t sweeps −1..1). 5+6+6+6+5+3 = 31.
const ROWS: { yFrac: number; n: number; xspread: number }[] = [
  { yFrac: 0.58, n: 5, xspread: 0.82 }, // upper cheek (below the eyes)
  { yFrac: 0.46, n: 6, xspread: 0.92 }, // mid cheek
  { yFrac: 0.34, n: 6, xspread: 0.86 }, // mouth line
  { yFrac: 0.22, n: 6, xspread: 0.7 }, // jawline
  { yFrac: 0.12, n: 5, xspread: 0.46 }, // chin / under-jaw
  { yFrac: -0.04, n: 3, xspread: 0.28 }, // upper neck (throat)
]

const SKIN_OFFSET = 0.012 // lift the disc just off the surface so it reads as "on" the skin
const LEAD_LEN = 0.14 // outward lead-line length

/** Deterministic 0..1 phase from an index — avoids Math.random so renders match. */
function phaseFor(i: number): number {
  const v = (Math.sin(i * 12.9898) * 43758.5453) % 1
  return v < 0 ? v + 1 : v
}

export function snapElectrodes(
  meshes: THREE.Object3D[],
  toLocal: THREE.Object3D,
): SnappedElectrodes | null {
  const targets = meshes.filter(Boolean)
  if (targets.length === 0) return null

  const headBox = new THREE.Box3().setFromObject(targets[0])
  if (headBox.isEmpty()) return null
  const H = headBox.max.y - headBox.min.y
  const W = headBox.max.x - headBox.min.x
  const y0 = headBox.min.y
  const center = headBox.getCenter(new THREE.Vector3())
  const frontZ = headBox.max.z + 0.6

  const ray = new THREE.Raycaster()
  ray.far = 4
  const back = new THREE.Vector3(0, 0, -1)
  const origin = new THREE.Vector3()
  const skin = new THREE.Vector3()
  const tip = new THREE.Vector3()
  const nrm = new THREE.Vector3()
  const nm = new THREE.Matrix3()

  const positions: number[] = []
  const leads: number[] = []
  const phases: number[] = []
  let idx = 0

  for (const row of ROWS) {
    const yW = y0 + row.yFrac * H
    for (let i = 0; i < row.n; i++) {
      const t = row.n === 1 ? 0 : (i / (row.n - 1)) * 2 - 1
      // Cast straight back; if it misses (the row is wider than the head here),
      // pull the ray toward the centerline until it catches the silhouette.
      let hit: THREE.Intersection | undefined
      for (const scl of [1, 0.85, 0.7, 0.55, 0.4]) {
        const x = center.x + t * (W * 0.5) * row.xspread * scl
        origin.set(x, yW, frontZ)
        ray.set(origin, back)
        const hits = ray.intersectObjects(targets, true)
        if (hits.length > 0) {
          hit = hits[0]
          break
        }
      }
      if (!hit) {
        idx++
        continue
      }
      if (hit.face) {
        nrm.copy(hit.face.normal).applyNormalMatrix(nm.getNormalMatrix(hit.object.matrixWorld))
        if (nrm.z < 0) nrm.negate() // outward = toward the viewer
      } else {
        nrm.set(0, 0, 1)
      }
      skin.copy(hit.point).addScaledVector(nrm, SKIN_OFFSET)
      tip.copy(hit.point).addScaledVector(nrm, LEAD_LEN)
      const p = toLocal.worldToLocal(skin.clone())
      const l = toLocal.worldToLocal(tip.clone())
      positions.push(p.x, p.y, p.z)
      leads.push(p.x, p.y, p.z, l.x, l.y, l.z)
      phases.push(phaseFor(idx))
      idx++
    }
  }

  return {
    positions: new Float32Array(positions),
    leads: new Float32Array(leads),
    phases: new Float32Array(phases),
    count: phases.length,
  }
}
