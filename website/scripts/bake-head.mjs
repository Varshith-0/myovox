/**
 * bake-head.mjs — author-time head baker.
 *
 * Surface-samples a realistic human-head scan into a flat point cloud and writes
 * `public/head-points.bin`: an interleaved Float32Array of [px,py,pz, nx,ny,nz]
 * per point. The web app loads that binary directly (no runtime glTF parsing,
 * no shipped mesh/textures) and renders it as a fresnel-shaded `THREE.Points`.
 *
 * Source geometry: the "Lee Perry-Smith" head (Infinite-Realities), distributed
 * with three.js examples under CC-BY 3.0. We use only sampled geometry; credit
 * is given in the README and the on-site Code page. The source GLB is fetched on
 * demand and NOT committed — only the derived binary is.
 *
 * Run: `npm run bake:head`  (pure Node, no dependencies).
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

const SRC_URL =
  'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/models/gltf/LeePerrySmith/LeePerrySmith.glb'
const SRC_PATH = resolve(ROOT, 'scripts/_assets/head.glb')
const OUT_PATH = resolve(ROOT, 'public/head-points.bin')
const MESH_PATH = resolve(ROOT, 'public/head-mesh.bin')

const SAMPLE_COUNT = 240_000
const TARGET_HEIGHT = 2.4 // world units for the head's Y extent

// glTF component types → typed-array constructors.
const COMPONENT = {
  5120: Int8Array,
  5121: Uint8Array,
  5122: Int16Array,
  5123: Uint16Array,
  5125: Uint32Array,
  5126: Float32Array,
}
const NUM_COMPONENTS = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }

async function ensureSource() {
  if (existsSync(SRC_PATH)) return
  mkdirSync(dirname(SRC_PATH), { recursive: true })
  process.stdout.write(`Fetching source head GLB…\n`)
  const res = await fetch(SRC_URL)
  if (!res.ok) throw new Error(`Failed to download head GLB: ${res.status} ${res.statusText}`)
  const buf = Buffer.from(await res.arrayBuffer())
  writeFileSync(SRC_PATH, buf)
  process.stdout.write(`Saved ${SRC_PATH} (${buf.length} bytes)\n`)
}

/** Parse a binary GLB into { json, bin } where bin is a Buffer. */
function parseGlb(buffer) {
  const dv = new DataView(buffer.buffer, buffer.byteOffset, buffer.byteLength)
  const magic = dv.getUint32(0, true)
  if (magic !== 0x46546c67) throw new Error('Not a GLB file')
  const length = dv.getUint32(8, true)
  let off = 12
  let json = null
  let bin = null
  while (off < length) {
    const chunkLen = dv.getUint32(off, true)
    const chunkType = dv.getUint32(off + 4, true)
    const start = off + 8
    if (chunkType === 0x4e4f534a) {
      json = JSON.parse(buffer.subarray(start, start + chunkLen).toString('utf8'))
    } else if (chunkType === 0x004e4942) {
      bin = buffer.subarray(start, start + chunkLen)
    }
    off = start + chunkLen
  }
  if (!json || !bin) throw new Error('GLB missing JSON or BIN chunk')
  return { json, bin }
}

/** Read an accessor into a flat JS array of numbers (handles byteStride). */
function readAccessor(json, bin, accessorIndex) {
  const acc = json.accessors[accessorIndex]
  const view = json.bufferViews[acc.bufferView]
  const TypedArray = COMPONENT[acc.componentType]
  const comps = NUM_COMPONENTS[acc.type]
  const baseOffset = (view.byteOffset ?? 0) + (acc.byteOffset ?? 0)
  const elementBytes = TypedArray.BYTES_PER_ELEMENT
  const stride = view.byteStride ?? comps * elementBytes
  const out = new Array(acc.count * comps)
  const dv = new DataView(bin.buffer, bin.byteOffset, bin.byteLength)
  const reader = {
    5121: (o) => dv.getUint8(o),
    5123: (o) => dv.getUint16(o, true),
    5125: (o) => dv.getUint32(o, true),
    5126: (o) => dv.getFloat32(o, true),
  }[acc.componentType]
  if (!reader) throw new Error(`Unsupported componentType ${acc.componentType}`)
  for (let i = 0; i < acc.count; i++) {
    const elementOffset = baseOffset + i * stride
    for (let c = 0; c < comps; c++) out[i * comps + c] = reader(elementOffset + c * elementBytes)
  }
  return out
}

function cross(ax, ay, az, bx, by, bz) {
  return [ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx]
}

function main() {
  const buffer = readFileSync(SRC_PATH)
  const { json, bin } = parseGlb(buffer)

  const prim = json.meshes[0].primitives[0]
  const positions = readAccessor(json, bin, prim.attributes.POSITION)
  const normals = readAccessor(json, bin, prim.attributes.NORMAL)
  const indices = readAccessor(json, bin, prim.indices)
  const triCount = indices.length / 3
  process.stdout.write(`Mesh: ${positions.length / 3} verts, ${triCount} triangles\n`)

  // Cumulative triangle areas for area-weighted sampling.
  const cumulative = new Float64Array(triCount)
  let total = 0
  for (let t = 0; t < triCount; t++) {
    const i0 = indices[t * 3] * 3
    const i1 = indices[t * 3 + 1] * 3
    const i2 = indices[t * 3 + 2] * 3
    const e1x = positions[i1] - positions[i0]
    const e1y = positions[i1 + 1] - positions[i0 + 1]
    const e1z = positions[i1 + 2] - positions[i0 + 2]
    const e2x = positions[i2] - positions[i0]
    const e2y = positions[i2 + 1] - positions[i0 + 1]
    const e2z = positions[i2 + 2] - positions[i0 + 2]
    const [cx, cy, cz] = cross(e1x, e1y, e1z, e2x, e2y, e2z)
    total += 0.5 * Math.hypot(cx, cy, cz)
    cumulative[t] = total
  }

  const pickTriangle = (r) => {
    // binary search the cumulative areas
    let lo = 0
    let hi = triCount - 1
    const target = r * total
    while (lo < hi) {
      const mid = (lo + hi) >> 1
      if (cumulative[mid] < target) lo = mid + 1
      else hi = mid
    }
    return lo
  }

  // One transform derived from the mesh vertices, applied to BOTH the sampled
  // points and the occluder mesh so they align exactly: recenter to origin and
  // scale so the head's Y extent equals TARGET_HEIGHT.
  let minX = Infinity,
    minY = Infinity,
    minZ = Infinity,
    maxX = -Infinity,
    maxY = -Infinity,
    maxZ = -Infinity
  for (let i = 0; i < positions.length; i += 3) {
    if (positions[i] < minX) minX = positions[i]
    if (positions[i + 1] < minY) minY = positions[i + 1]
    if (positions[i + 2] < minZ) minZ = positions[i + 2]
    if (positions[i] > maxX) maxX = positions[i]
    if (positions[i + 1] > maxY) maxY = positions[i + 1]
    if (positions[i + 2] > maxZ) maxZ = positions[i + 2]
  }
  const cX = (minX + maxX) / 2
  const cY = (minY + maxY) / 2
  const cZ = (minZ + maxZ) / 2
  const scale = TARGET_HEIGHT / (maxY - minY)

  // --- sample the surface into the point cloud ---
  const out = new Float32Array(SAMPLE_COUNT * 6)
  for (let s = 0; s < SAMPLE_COUNT; s++) {
    const t = pickTriangle(Math.random())
    const i0 = indices[t * 3] * 3
    const i1 = indices[t * 3 + 1] * 3
    const i2 = indices[t * 3 + 2] * 3
    let u = Math.random()
    let v = Math.random()
    if (u + v > 1) {
      u = 1 - u
      v = 1 - v
    }
    const w = 1 - u - v
    const px = w * positions[i0] + u * positions[i1] + v * positions[i2]
    const py = w * positions[i0 + 1] + u * positions[i1 + 1] + v * positions[i2 + 1]
    const pz = w * positions[i0 + 2] + u * positions[i1 + 2] + v * positions[i2 + 2]
    let nx = w * normals[i0] + u * normals[i1] + v * normals[i2]
    let ny = w * normals[i0 + 1] + u * normals[i1 + 1] + v * normals[i2 + 1]
    let nz = w * normals[i0 + 2] + u * normals[i1 + 2] + v * normals[i2 + 2]
    const nl = Math.hypot(nx, ny, nz) || 1
    out[s * 6] = (px - cX) * scale
    out[s * 6 + 1] = (py - cY) * scale
    out[s * 6 + 2] = (pz - cZ) * scale
    out[s * 6 + 3] = nx / nl
    out[s * 6 + 4] = ny / nl
    out[s * 6 + 5] = nz / nl
  }
  mkdirSync(dirname(OUT_PATH), { recursive: true })
  writeFileSync(OUT_PATH, Buffer.from(out.buffer))

  // --- write the occluder mesh: [u32 vertCount][u32 indexCount][f32 pos…][u32 idx…] ---
  const vertCount = positions.length / 3
  const indexCount = indices.length
  const header = new Uint32Array([vertCount, indexCount])
  const meshPos = new Float32Array(vertCount * 3)
  for (let i = 0; i < vertCount; i++) {
    meshPos[i * 3] = (positions[i * 3] - cX) * scale
    meshPos[i * 3 + 1] = (positions[i * 3 + 1] - cY) * scale
    meshPos[i * 3 + 2] = (positions[i * 3 + 2] - cZ) * scale
  }
  const meshIdx = Uint32Array.from(indices)
  const meshBuf = Buffer.concat([
    Buffer.from(header.buffer),
    Buffer.from(meshPos.buffer),
    Buffer.from(meshIdx.buffer),
  ])
  writeFileSync(MESH_PATH, meshBuf)

  process.stdout.write(
    `Bounds (raw): X[${minX.toFixed(2)},${maxX.toFixed(2)}] ` +
      `Y[${minY.toFixed(2)},${maxY.toFixed(2)}] Z[${minZ.toFixed(2)},${maxZ.toFixed(2)}]\n`,
  )
  process.stdout.write(
    `Wrote ${OUT_PATH} (${SAMPLE_COUNT} pts, ${(out.byteLength / 1024).toFixed(0)} KB) and ` +
      `${MESH_PATH} (${vertCount} verts / ${indexCount / 3} tris, ${(meshBuf.length / 1024).toFixed(0)} KB)\n`,
  )
}

await ensureSource()
main()
