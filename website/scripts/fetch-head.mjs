// Fetch a free Ready Player Me head GLB with ARKit + Oculus visemes baked in,
// save it to public/face-head.glb, then inspect it (morph target names, bones,
// meshes, bbox) by parsing the GLB JSON chunk directly — no GLTFLoader / DOM
// needed. Run with Node 18+ (global fetch). See claude-code-brief context.

import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const PUB = join(__dirname, '..', 'public')

// models.readyplayer.me is DNS-blocked on this host, so we pull free RPM-export
// avatars (with Oculus visemes for lip-sync) committed to public MIT repos and
// served over GitHub raw, which is reachable. We download a couple of
// candidates + a body-animation clip set, inspect each, and keep the best.
const CANDIDATES = [
  {
    name: 'face-a.glb',
    url: 'https://raw.githubusercontent.com/wass08/r3f-lipsync-tutorial/main/public/models/646d9dcdc8a5f5bddbfac913.glb',
  },
  {
    name: 'face-b.glb',
    url: 'https://raw.githubusercontent.com/wass08/wawa-lipsync/main/examples/lipsync-demo/public/models/64f1a714fe61576b46f27ca2.glb',
  },
  {
    name: 'face-anims.glb',
    url: 'https://raw.githubusercontent.com/wass08/wawa-lipsync/main/examples/lipsync-demo/public/models/animations.glb',
  },
]

async function tryFetch(url) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': 'curl/8' }, redirect: 'follow' })
    if (!res.ok) return null
    const buf = Buffer.from(await res.arrayBuffer())
    // GLB magic = 'glTF'
    if (buf.length < 12 || buf.readUInt32LE(0) !== 0x46546c67) return null
    return buf
  } catch {
    return null
  }
}

function parseGlb(buf) {
  const length = buf.readUInt32LE(8)
  let off = 12
  let json = null
  while (off < length) {
    const chunkLen = buf.readUInt32LE(off)
    const chunkType = buf.readUInt32LE(off + 4)
    const data = buf.subarray(off + 8, off + 8 + chunkLen)
    if (chunkType === 0x4e4f534a) json = JSON.parse(data.toString('utf8')) // 'JSON'
    off += 8 + chunkLen
  }
  return json
}

function summarize(g) {
  const lines = []
  lines.push(`generator: ${g.asset?.generator ?? '?'}`)
  lines.push(`meshes: ${g.meshes?.length}, nodes: ${g.nodes?.length}, anims: ${g.animations?.length ?? 0}, images: ${g.images?.length ?? 0}, skins: ${g.skins?.length ?? 0}`)

  // Morph targets per mesh
  for (const m of g.meshes ?? []) {
    const names = m.extras?.targetNames ?? []
    const prim = m.primitives?.[0]
    const tcount = prim?.targets?.length ?? 0
    lines.push(`\n=== mesh "${m.name}" — ${tcount} morph targets ===`)
    if (names.length) lines.push('  ' + names.join(', '))
    // bbox from POSITION accessor min/max
    const posAcc = prim?.attributes?.POSITION
    if (posAcc != null) {
      const a = g.accessors[posAcc]
      if (a?.min && a?.max)
        lines.push(`  bbox min=[${a.min.map((v) => v.toFixed(3))}] max=[${a.max.map((v) => v.toFixed(3))}]`)
    }
  }

  // Bone / node names (for breathing rig)
  const boneNames = (g.nodes ?? []).map((n) => n.name).filter(Boolean)
  const rigHits = boneNames.filter((n) => /spine|chest|neck|head|shoulder|hips|clavicle/i.test(n))
  lines.push(`\n=== rig nodes of interest ===`)
  lines.push('  ' + (rigHits.join(', ') || '(none found)'))
  lines.push(`\n=== all node names (${boneNames.length}) ===`)
  lines.push('  ' + boneNames.join(', '))

  if (g.animations?.length) {
    lines.push(`\n=== animations ===`)
    lines.push('  ' + g.animations.map((a) => a.name).join(', '))
  }
  return lines.join('\n')
}

let got = 0
for (const c of CANDIDATES) {
  process.stdout.write(`fetching ${c.name} ... `)
  const buf = await tryFetch(c.url)
  if (!buf) {
    console.log('FAIL')
    continue
  }
  got++
  const out = join(PUB, c.name)
  writeFileSync(out, buf)
  console.log(`OK (${(buf.length / 1024 / 1024).toFixed(2)} MB) -> ${out}`)
  console.log('\n--- SUMMARY: ' + c.name + ' ---')
  console.log(summarize(parseGlb(buf)))
  console.log('\n========================================\n')
}

if (!got) {
  console.error('FAILED: no candidate returned a valid GLB.')
  process.exit(1)
}
