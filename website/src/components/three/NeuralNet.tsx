import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { buildGraph } from '@/three/graph'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * The model as a glowing node-graph in front of the head: nodes twinkle, faint
 * edges connect them, and pulses travel along the edges (the signal flowing
 * through the network). World-space — it does not rotate with the head. Fades
 * with the `neural` layer intensity.
 */

const nodeVertex = /* glsl */ `
  uniform float uTime; uniform float uSize; uniform float uIntensity; uniform float uDpr;
  attribute float aPhase;
  varying float vI;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float tw = 0.65 + 0.35 * sin(uTime * 1.6 + aPhase * 6.2831);
    vI = uIntensity * tw;
    gl_PointSize = uSize * uDpr * (300.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
  }
`

const pulseVertex = /* glsl */ `
  uniform float uTime; uniform float uSize; uniform float uIntensity; uniform float uDpr;
  attribute vec3 aEnd; attribute float aOffset;
  varying float vI;
  void main() {
    float life = fract(uTime * 0.55 + aOffset);
    vec3 pos = mix(position, aEnd, life);
    vI = uIntensity * sin(life * 3.14159);
    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = uSize * uDpr * (300.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
  }
`

const discFragment = /* glsl */ `
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

export function NeuralNet() {
  const dpr = useStore((s) => s.dpr)
  const lowPower = useStore((s) => s.lowPower)
  const groupRef = useRef<THREE.Group>(null)
  const edgeMatRef = useRef<THREE.LineBasicMaterial>(null)

  const built = useMemo(() => {
    const graph = buildGraph(lowPower ? 26 : 46, 2, 1)

    const nodeGeo = new THREE.BufferGeometry()
    nodeGeo.setAttribute('position', new THREE.BufferAttribute(graph.nodes, 3))
    nodeGeo.setAttribute('aPhase', new THREE.BufferAttribute(graph.nodePhase, 1))

    const edgeGeo = new THREE.BufferGeometry()
    edgeGeo.setAttribute('position', new THREE.BufferAttribute(graph.edgeLines, 3))

    const pulseGeo = new THREE.BufferGeometry()
    pulseGeo.setAttribute('position', new THREE.BufferAttribute(graph.pulseStart, 3))
    pulseGeo.setAttribute('aEnd', new THREE.BufferAttribute(graph.pulseEnd, 3))
    pulseGeo.setAttribute('aOffset', new THREE.BufferAttribute(graph.pulseOffset, 1))

    const mkMat = (vertexShader: string, size: number) =>
      new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uSize: { value: size },
          uIntensity: { value: 0 },
          uDpr: { value: dpr },
        },
        vertexShader,
        fragmentShader: discFragment,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
      })

    return {
      nodeGeo,
      edgeGeo,
      pulseGeo,
      nodeMat: mkMat(nodeVertex, 0.07),
      pulseMat: mkMat(pulseVertex, 0.05),
    }
  }, [dpr, lowPower])

  useEffect(() => {
    return () => {
      built.nodeGeo.dispose()
      built.edgeGeo.dispose()
      built.pulseGeo.dispose()
      built.nodeMat.dispose()
      built.pulseMat.dispose()
    }
  }, [built])

  useFrame((_, delta) => {
    const intensity = sceneSample.current.layers.neural
    built.nodeMat.uniforms.uTime.value += delta
    built.nodeMat.uniforms.uIntensity.value = intensity
    built.pulseMat.uniforms.uTime.value += delta
    built.pulseMat.uniforms.uIntensity.value = intensity
    if (edgeMatRef.current) edgeMatRef.current.opacity = intensity * 0.16
    if (groupRef.current) groupRef.current.visible = intensity > 0.01
  })

  return (
    <group ref={groupRef}>
      <points geometry={built.nodeGeo} material={built.nodeMat} />
      <points geometry={built.pulseGeo} material={built.pulseMat} />
      <lineSegments geometry={built.edgeGeo}>
        <lineBasicMaterial
          ref={edgeMatRef}
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
