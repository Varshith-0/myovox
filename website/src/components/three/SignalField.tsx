import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { sampleFaceOrigins } from '@/three/anchors'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * EMG-style signal: motes that stream forward off the face in waving lines,
 * fading in and out over their travel — the "raw signal" emanating from the
 * sensors. Animated entirely in-shader (a looping per-particle life). Fades with
 * the `signal` layer intensity.
 */

const vertex = /* glsl */ `
  uniform float uTime;
  uniform float uSize;
  uniform float uIntensity;
  uniform float uDpr;
  attribute vec3 aDir;
  attribute float aOffset;
  varying float vI;
  void main() {
    float life = fract(uTime * 0.32 + aOffset);
    vec3 pos = position + aDir * life * 2.6;
    pos.x += sin(life * 11.0 + aOffset * 6.2831) * 0.09;
    pos.y += cos(life * 8.0 + aOffset * 6.2831) * 0.07;
    float fade = sin(life * 3.14159);          // fade in then out across the path
    vI = uIntensity * fade;
    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = uSize * uDpr * (300.0 / -mv.z);
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

export function SignalField() {
  const dpr = useStore((s) => s.dpr)
  const lowPower = useStore((s) => s.lowPower)
  const groupRef = useRef<THREE.Group>(null)

  const { geometry, material } = useMemo(() => {
    const count = lowPower ? 900 : 2600
    const { positions, dirs, offsets } = sampleFaceOrigins(count)
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    g.setAttribute('aDir', new THREE.BufferAttribute(dirs, 3))
    g.setAttribute('aOffset', new THREE.BufferAttribute(offsets, 1))
    const m = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uSize: { value: 0.024 },
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
    })
    return { geometry: g, material: m }
  }, [dpr, lowPower])

  useEffect(() => {
    return () => {
      geometry.dispose()
      material.dispose()
    }
  }, [geometry, material])

  useFrame((_, delta) => {
    const intensity = sceneSample.current.layers.signal
    material.uniforms.uTime.value += delta
    material.uniforms.uIntensity.value = intensity
    if (groupRef.current) groupRef.current.visible = intensity > 0.01
  })

  return (
    // Sized to the old head; scale + lift the origins onto the solid head's face.
    <group ref={groupRef} scale={0.62} position={[0, 0.12, 0.03]}>
      <points geometry={geometry} material={material} />
    </group>
  )
}
