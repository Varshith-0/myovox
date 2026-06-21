import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF, useTexture } from '@react-three/drei'
import * as THREE from 'three'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'
import { WORDS, WORD_DURATION } from '@/data/speech'
import { snapElectrodes } from '@/three/electrodeSnap'
import { electrodeAnchors } from '@/store/electrodeAnchors'

/**
 * The solid, realistic head — a Ready Player Me MALE head scan (free, with Oculus
 * viseme morph targets for lip-sync) rendered in the site's monochrome idiom:
 * the real skin/eye textures are kept (so eyebrows, eyeballs and lips read), but
 * desaturated to greyscale and graded dark, lit softly so the sculpted form shows,
 * with a fresnel rim that blooms. The baked-in beard is painted out in a pre-pass
 * (scripts/clean-face.py -> public/face-skin.png) and swapped onto the head mesh.
 * The head is rendered bald (no hair mesh). A world-Y fade dissolves the bust into
 * black below the chest.
 *
 * Gated on the `face` scene layer: invisible where face=0 (the dust intro), it is
 * the persistent head across the rest of the stages. On the Talking stage it
 * drives visemes from the per-word speech schedule so the mouth speaks.
 */

const URL = `${import.meta.env.BASE_URL}face-head.glb`
const SKIN_URL = `${import.meta.env.BASE_URL}face-skin.png` // beardless face
const TOP_URL = `${import.meta.env.BASE_URL}face-top.png` // de-logo'd shirt

// Head + eyes + neck/chest (a bust), rendered bald. Legs/shoes hidden; arms
// collapsed + faded. Wolf3D_Hair is intentionally omitted so the head is bald.
const SHOW = new Set([
  'Wolf3D_Head',
  'Wolf3D_Teeth',
  'EyeLeft',
  'EyeRight',
  'Wolf3D_Body',
  'Wolf3D_Outfit_Top',
])

// Fit: head height in world units (measured bbox) + where its centre sits. Tuned
// to fill the frame (head-and-chest) and roughly match the old point-cloud head.
const FIT_HEIGHT = 1.7
const FIT_CENTER = new THREE.Vector3(0, 0.29, 0)

// World-Y band over which the bust dissolves to black — cut at roughly the first
// shirt button (a tighter bust). Tuned with the eye aligned to ~y 0.5.
const FADE_LO = -0.58
const FADE_HI = -0.28

const BG = new THREE.Color(0x050505)

// Per-material greyscale grade: the face reads bright with a soft fresnel rim.
type Grade = { rimPow: number; rimGain: number; gamma: number; exposure: number }
const FACE_GRADE: Grade = { rimPow: 2.6, rimGain: 0.85, gamma: 1.35, exposure: 0.82 }

// Per-letter → Oculus viseme, for the Talking stage lip-sync.
const V_FOR: Record<string, string> = {
  a: 'viseme_aa', e: 'viseme_E', i: 'viseme_I', o: 'viseme_O', u: 'viseme_U',
  b: 'viseme_PP', p: 'viseme_PP', m: 'viseme_PP', f: 'viseme_FF', v: 'viseme_FF',
  t: 'viseme_DD', d: 'viseme_DD', k: 'viseme_kk', g: 'viseme_kk', c: 'viseme_kk',
  q: 'viseme_kk', x: 'viseme_kk', s: 'viseme_SS', z: 'viseme_SS', n: 'viseme_nn',
  l: 'viseme_nn', r: 'viseme_RR', j: 'viseme_CH', h: 'viseme_sil', w: 'viseme_U',
  y: 'viseme_I',
}
const VISEMES = [
  'viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD', 'viseme_kk',
  'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR', 'viseme_aa', 'viseme_E',
  'viseme_I', 'viseme_O', 'viseme_U',
]
const TALK_TOTAL = WORDS.length * WORD_DURATION

useGLTF.preload(URL)

type VisemeMesh = { infl: number[]; idx: Record<string, number | undefined> }

export function FaceHead() {
  const gltf = useGLTF(URL)
  const tex = useTexture({ skin: SKIN_URL, top: TOP_URL })
  const reduced = useStore((s) => s.reducedMotion)
  const setElectrodesReady = useStore((s) => s.setElectrodesReady)
  const rootRef = useRef<THREE.Group>(null)
  const snapped = useRef(false)
  const snapTries = useRef(0)

  // Live uniforms shared across every material variant, updated once per frame.
  const live = useMemo(() => ({ uFace: { value: 0 }, uRim: { value: 1 } }), [])

  // Inject the greyscale grade + rim + vertical fade into a GLTF material, keeping
  // its textures/skinning/morphs.
  const grade = useMemo(() => {
    const seen = new WeakSet<THREE.Material>()
    return (mat: THREE.MeshStandardMaterial, p: Grade) => {
      if (seen.has(mat)) return
      seen.add(mat)
      mat.onBeforeCompile = (shader) => {
        shader.uniforms.uFace = live.uFace
        shader.uniforms.uRim = live.uRim
        shader.uniforms.uRimPow = { value: p.rimPow }
        shader.uniforms.uRimGain = { value: p.rimGain }
        shader.uniforms.uGamma = { value: p.gamma }
        shader.uniforms.uExposure = { value: p.exposure }
        shader.uniforms.uFadeLo = { value: FADE_LO }
        shader.uniforms.uFadeHi = { value: FADE_HI }
        shader.uniforms.uBg = { value: BG }
        shader.vertexShader =
          'varying float vWorldY;\n' +
          shader.vertexShader.replace(
            '#include <project_vertex>',
            'vWorldY = (modelMatrix * vec4(transformed, 1.0)).y;\n#include <project_vertex>',
          )
        shader.fragmentShader =
          'uniform float uFace;uniform float uRim;uniform float uRimPow;uniform float uRimGain;' +
          'uniform float uGamma;uniform float uExposure;uniform float uFadeLo;uniform float uFadeHi;' +
          'uniform vec3 uBg;varying float vWorldY;\n' +
          shader.fragmentShader.replace(
            '#include <dithering_fragment>',
            /* glsl */ `#include <dithering_fragment>
              float lum = dot(gl_FragColor.rgb, vec3(0.299, 0.587, 0.114));
              lum = pow(clamp(lum, 0.0, 1.0), uGamma) * uExposure;
              vec3 vn = normalize(vNormal);
              vec3 vd = normalize(vViewPosition);
              float fres = pow(clamp(1.0 - abs(dot(vn, vd)), 0.0, 1.0), uRimPow);
              lum += fres * uRimGain;
              lum *= smoothstep(uFadeLo, uFadeHi, vWorldY);
              gl_FragColor.rgb = mix(uBg, vec3(lum), uFace);
              gl_FragColor.a = 1.0;`,
          )
      }
      mat.toneMapped = false
      mat.needsUpdate = true
    }
  }, [live])

  const rig = useMemo(() => {
    const scene = gltf.scene
    for (const t of [tex.skin, tex.top]) {
      t.flipY = false // match the GLB's glTF UV convention
      t.colorSpace = THREE.SRGBColorSpace
      t.needsUpdate = true
    }

    const visemeMeshes: VisemeMesh[] = []
    // Solid surfaces to raycast electrode anchors against (head kept first — its
    // bbox sets the vertical range; body + shirt let the lowest rows reach the neck).
    const faceTargets: THREE.Mesh[] = []
    let headMesh: THREE.SkinnedMesh | null = null

    scene.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!mesh.isMesh) return
      mesh.visible = SHOW.has(mesh.name)
      mesh.frustumCulled = false
      const mat = mesh.material as THREE.MeshStandardMaterial
      if (mesh.name === 'Wolf3D_Head') {
        mat.map = tex.skin // beardless face texture (same UVs)
        headMesh = mesh as THREE.SkinnedMesh
        faceTargets.unshift(mesh)
      } else if (mesh.name === 'Wolf3D_Body') {
        faceTargets.push(mesh)
      } else if (mesh.name === 'Wolf3D_Outfit_Top') {
        mat.map = tex.top // de-logo'd shirt
        faceTargets.push(mesh)
      }
      grade(mat, FACE_GRADE)
      if (
        (mesh.name === 'Wolf3D_Head' || mesh.name === 'Wolf3D_Teeth') &&
        mesh.morphTargetDictionary &&
        mesh.morphTargetInfluences
      ) {
        const idx: Record<string, number | undefined> = {}
        for (const v of VISEMES) idx[v] = mesh.morphTargetDictionary[v]
        visemeMeshes.push({ infl: mesh.morphTargetInfluences, idx })
      }
    })

    const bone = (n: string) => scene.getObjectByName(n) as THREE.Bone | null
    // Collapse the arms (and their sleeves) to the shoulder joint so the bust has
    // no A-pose limbs — far more reliable than guessing tuck rotations.
    for (const n of ['LeftArm', 'RightArm']) {
      const b = bone(n)
      if (b) b.scale.setScalar(0.02)
    }

    let scale = 3.8
    const pos = FIT_CENTER.clone()
    if (headMesh) {
      const g = (headMesh as THREE.SkinnedMesh).geometry
      g.computeBoundingBox()
      const bb = g.boundingBox!
      const size = bb.getSize(new THREE.Vector3())
      const center = bb.getCenter(new THREE.Vector3())
      scale = FIT_HEIGHT / size.y
      pos.copy(FIT_CENTER).sub(center.multiplyScalar(scale))
    }

    return { scene, scale, pos, visemeMeshes, snapMeshes: faceTargets }
  }, [gltf.scene, tex, grade])

  useEffect(() => () => {
    rig.scene.traverse((o) => {
      const m = (o as THREE.Mesh).material as THREE.Material | undefined
      if (m) m.dispose()
    })
  }, [rig])

  // DEV: force the electrode snap on demand (for the Playwright harness) — returns
  // the count or an error string, bypassing the per-frame gate.
  useEffect(() => {
    if (!import.meta.env.DEV) return
    const w = window as unknown as Record<string, unknown>
    w.__snapNow = () => {
      const root = rootRef.current
      if (!root?.parent) return 'no-parent'
      root.parent.updateWorldMatrix(true, true)
      try {
        const snap = snapElectrodes(rig.snapMeshes, root.parent)
        if (!snap) return 'null-or-empty-box'
        Object.assign(electrodeAnchors, snap)
        snapped.current = true
        setElectrodesReady(true)
        return snap.count
      } catch (e) {
        return 'ERR:' + (e as Error).message
      }
    }
  }, [rig, setElectrodesReady])

  const talk = useRef(0)

  useFrame((_, delta) => {
    const s = sceneSample.current
    const face = s.layers.face
    live.uFace.value = face
    live.uRim.value = s.rim
    if (rootRef.current) rootRef.current.visible = face > 0.01

    // Once the head is visible and its matrices have settled, snap the 31
    // electrodes onto the real surface (a few frames in, so worldMatrix is valid).
    if (!snapped.current && face > 0.5 && rootRef.current?.parent) {
      snapTries.current++
      if (snapTries.current >= 2) {
        const headRig = rootRef.current.parent
        headRig.updateWorldMatrix(true, true)
        const snap = snapElectrodes(rig.snapMeshes, headRig)
        if (snap && (snap.count >= 28 || snapTries.current > 40)) {
          Object.assign(electrodeAnchors, snap)
          snapped.current = true
          setElectrodesReady(true)
        }
      }
    }

    if (face < 0.02) return

    const dt = Math.min(delta, 0.05)

    // Talking: drive visemes from the per-word schedule on the Talking stage.
    const talking = s.layers.muscles // 1 on the articulation stage
    let target: string | null = null
    let open = 0
    if (talking > 0.5 && !reduced) {
      talk.current += dt
      const tt = talk.current % TALK_TOTAL
      const wi = Math.min(WORDS.length - 1, Math.floor(tt / WORD_DURATION))
      const fw = (tt / WORD_DURATION) % 1
      const letters = WORDS[wi].toLowerCase().replace(/[^a-z]/g, '')
      if (letters.length) {
        const ch = letters[Math.min(letters.length - 1, Math.floor(fw * letters.length))]
        target = V_FOR[ch] ?? 'viseme_sil'
        // Envelope: open within the word, close at the seams, so it reads as speech.
        open = 0.45 + 0.55 * Math.sin(Math.min(1, fw) * Math.PI)
      }
    } else {
      talk.current = 0
    }
    const lerp = Math.min(1, dt * 14)
    for (const m of rig.visemeMeshes) {
      for (const v of VISEMES) {
        const i = m.idx[v]
        if (i === undefined) continue
        const want = v === target && v !== 'viseme_sil' ? open : 0
        m.infl[i] += (want - m.infl[i]) * lerp
      }
    }
  })

  return (
    <group ref={rootRef}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[2.5, 3, 4]} intensity={0.95} />
      <directionalLight position={[-3, 0.5, 1.5]} intensity={0.3} />
      <group scale={rig.scale} position={rig.pos}>
        <primitive object={rig.scene} />
      </group>
    </group>
  )
}
