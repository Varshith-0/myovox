import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'
import { MUSCLE_LABELS, buildMuscleCloud, groupIndex } from '@/data/muscles'
import { WORDS, WORD_PROFILES, WORD_DURATION } from '@/data/speech'
import { STAGES } from '@/data/stages'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'
import styles from './Muscles.module.css'

const TALKING_INDEX = STAGES.findIndex((s) => s.id === 'articulation')

// The muscle map (data/muscles.ts) is authored in the old head's coordinate
// space; the solid head's face is smaller and higher, so compress + lift the
// whole group onto it (kept in sync with FaceHead's fit / the electrode scale).
const FIT_SCALE = 0.72
const FIT_POS: [number, number, number] = [0, 0.18, 0]

const vertex = /* glsl */ `
  uniform float uTime;
  uniform float uSize;
  uniform float uIntensity;
  uniform float uDpr;
  attribute float aIntensity;
  attribute float aRand;
  varying float vI;
  void main() {
    float tw = 0.8 + 0.2 * sin(uTime * 6.0 + aRand * 30.0);
    vI = aIntensity * uIntensity * tw;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = uSize * uDpr * (300.0 / -mv.z) * (0.7 + aRand * 0.7);
    gl_Position = projectionMatrix * mv;
  }
`

const fragment = /* glsl */ `
  precision mediump float;
  varying float vI;
  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if (d > 0.5) discard;
    float core = smoothstep(0.5, 0.0, d);
    gl_FragColor = vec4(vec3(vI), core * vI);
  }
`

/**
 * The speech muscles, as glowing patches on the face that pulse in a talking
 * rhythm (lips/jaw/tongue/throat groups firing on their own cadences — see
 * {@link groupActivation}). Named callouts label the key muscles. Child of the
 * head rig, gated on the `muscles` layer intensity; labels appear on the
 * talking stage. The whole thing teaches which muscles fire while speaking.
 */
export function Muscles() {
  const dpr = useStore((s) => s.dpr)
  // The callouts extend horizontally off a fixed 3D anchor, so on narrow screens
  // they overflow the viewport — drop them there (the glowing patches + the spoken
  // sentence still carry the "which muscles fire" idea).
  const labelsActive = useStore((s) => s.stageIndex === TALKING_INDEX && !s.isMobile)
  const setSpeechWord = useStore((s) => s.setSpeechWord)
  const groupRef = useRef<THREE.Group>(null)
  const elapsed = useRef(0) // seconds of "speech" accumulated on this stage
  const act = useRef(new Float32Array(6)) // smoothed per-group activation
  const lastWord = useRef(-1)
  const labelRefs = useRef<(HTMLDivElement | null)[]>([])
  const labelGroups = useMemo(() => MUSCLE_LABELS.map((l) => groupIndex(l.group)), [])

  const cloud = useMemo(() => buildMuscleCloud(), [])

  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(cloud.positions, 3))
    g.setAttribute('aIntensity', new THREE.BufferAttribute(new Float32Array(cloud.count), 1))
    g.setAttribute('aRand', new THREE.BufferAttribute(cloud.rand, 1))
    return g
  }, [cloud])

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uSize: { value: 0.011 },
          uIntensity: { value: 0 },
          uDpr: { value: dpr },
        },
        vertexShader: vertex,
        fragmentShader: fragment,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
      }),
    [dpr],
  )

  useEffect(() => {
    return () => {
      geometry.dispose()
      material.dispose()
    }
  }, [geometry, material])

  useFrame((_, delta) => {
    const intensity = sceneSample.current.layers.muscles
    material.uniforms.uTime.value += delta
    material.uniforms.uIntensity.value = intensity
    if (groupRef.current) groupRef.current.visible = intensity > 0.01
    if (intensity <= 0.05) return

    // Advance the spoken sentence and pick the current word.
    elapsed.current += delta
    const total = WORDS.length * WORD_DURATION
    const tt = elapsed.current % total
    const idx = Math.min(WORDS.length - 1, Math.floor(tt / WORD_DURATION))
    if (idx !== lastWord.current) {
      lastWord.current = idx
      setSpeechWord(idx)
    }
    // Per-word pulse: muscles for the current word swell then settle.
    const f = (tt / WORD_DURATION) % 1
    const env = 0.4 + 0.6 * Math.sin(f * Math.PI)
    const profile = WORD_PROFILES[idx]
    const a = act.current
    const lerp = Math.min(1, delta * 12)
    for (let g = 0; g < 6; g++) a[g] += (profile[g] * env - a[g]) * lerp

    const attr = geometry.getAttribute('aIntensity') as THREE.BufferAttribute
    const arr = attr.array as Float32Array
    for (let i = 0; i < cloud.count; i++) {
      arr[i] = a[cloud.groupIdx[i]] * cloud.weights[i]
    }
    attr.needsUpdate = true

    // Brighten each callout as its muscle group fires — so the viewer sees which
    // muscle drives the current sound.
    for (let i = 0; i < labelRefs.current.length; i++) {
      const el = labelRefs.current[i]
      if (el) el.style.opacity = String(0.28 + 0.72 * a[labelGroups[i]])
    }
  })

  return (
    <group ref={groupRef} scale={FIT_SCALE} position={FIT_POS}>
      <points geometry={geometry} material={material} />
      {labelsActive &&
        MUSCLE_LABELS.map((label, i) => (
          <Html
            key={label.id}
            position={label.pos as [number, number, number]}
            zIndexRange={[8, 0]}
            style={{ pointerEvents: 'none' }}
          >
            <div
              ref={(el) => {
                labelRefs.current[i] = el
              }}
              className={`${styles.label} ${label.side === 'left' ? styles.left : styles.right}`}
            >
              <span className={styles.dot} />
              <span className={styles.tag}>
                <b className={styles.name}>{label.text}</b>
                <i className={styles.sub}>{label.sub}</i>
              </span>
            </div>
          </Html>
        ))}
    </group>
  )
}
