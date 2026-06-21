import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { electrodeAnchors } from '@/store/electrodeAnchors'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * The 31-channel sensor grid: glowing dots that pulse on the cheek/jaw/throat,
 * each with a short outward lead line. Positions are snapped onto the real head
 * surface (see electrodeSnap.ts) and published via {@link electrodeAnchors}; this
 * is a child of the head rig (identity transform — anchors are already in its
 * space), so it rotates with the face. Fades with the `electrodes` layer.
 */

const dotVertex = /* glsl */ `
  uniform float uTime;
  uniform float uSize;
  uniform float uIntensity;
  uniform float uDpr;
  attribute float aPhase;
  varying float vI;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float pulse = 0.55 + 0.45 * sin(uTime * 3.2 + aPhase * 6.2831);
    vI = uIntensity * (0.5 + 0.7 * pulse);
    gl_PointSize = uSize * uDpr * (300.0 / -mv.z) * (0.9 + 0.5 * pulse);
    gl_Position = projectionMatrix * mv;
  }
`

const dotFragment = /* glsl */ `
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

export function Electrodes() {
  const dpr = useStore((s) => s.dpr)
  const electrodesReady = useStore((s) => s.electrodesReady)
  const groupRef = useRef<THREE.Group>(null)
  const leadMatRef = useRef<THREE.LineBasicMaterial>(null)

  // Rebuilds once the snap fills electrodeAnchors (electrodesReady flips true).
  const dotGeometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    if (electrodesReady && electrodeAnchors.count > 0) {
      g.setAttribute('position', new THREE.BufferAttribute(electrodeAnchors.positions, 3))
      g.setAttribute('aPhase', new THREE.BufferAttribute(electrodeAnchors.phases, 1))
    }
    return g
  }, [electrodesReady])

  const leadGeometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    if (electrodesReady && electrodeAnchors.count > 0) {
      g.setAttribute('position', new THREE.BufferAttribute(electrodeAnchors.leads, 3))
    }
    return g
  }, [electrodesReady])

  const dotMaterial = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uSize: { value: 0.12 },
          uIntensity: { value: 0 },
          uDpr: { value: dpr },
        },
        vertexShader: dotVertex,
        fragmentShader: dotFragment,
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
      dotGeometry.dispose()
      leadGeometry.dispose()
      dotMaterial.dispose()
    }
  }, [dotGeometry, leadGeometry, dotMaterial])

  useFrame((_, delta) => {
    const intensity = sceneSample.current.layers.electrodes
    dotMaterial.uniforms.uTime.value += delta
    dotMaterial.uniforms.uIntensity.value = intensity
    if (leadMatRef.current) leadMatRef.current.opacity = intensity * 0.4
    if (groupRef.current) groupRef.current.visible = intensity > 0.01 && electrodeAnchors.count > 0
  })

  return (
    // Identity transform — electrodeAnchors are already in HeadRig-local space,
    // snapped onto the real surface.
    <group ref={groupRef}>
      <points geometry={dotGeometry} material={dotMaterial} />
      <lineSegments geometry={leadGeometry}>
        <lineBasicMaterial
          ref={leadMatRef}
          color="#ffffff"
          transparent
          opacity={0}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          toneMapped={false}
        />
      </lineSegments>
    </group>
  )
}
