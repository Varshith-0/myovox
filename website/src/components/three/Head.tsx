import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useHeadPoints } from '@/hooks/useHeadPoints'
import { useStore } from '@/store/useStore'
import { sceneSample } from '@/store/sceneSample'

/**
 * The glowing head: a point cloud where each point's brightness is a fresnel of
 * its own normal — grazing-angle points glow white (the silhouette/rim), front
 * points sit at a dim fill, back-facing points fade out. Intensities exceed 1.0
 * so the rim (and only the rim) trips the bloom. The `uForm` uniform scatters
 * the cloud into dust (0) or condenses it into the head (1), driven by scroll.
 */

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uForm;
  uniform float uSize;
  uniform float uRimPower;
  uniform float uRimIntensity;
  uniform float uBase;
  uniform float uDiff;
  uniform float uDpr;

  attribute vec3 aNormal;
  attribute float aRand;

  varying float vIntensity;
  varying float vTwinkle;

  void main() {
    // Scatter outward into dust when not formed.
    float scatter = 1.0 - uForm;
    vec3 jitter = normalize(aNormal + 0.7 * vec3(
      sin(aRand * 42.0), cos(aRand * 17.3), sin(aRand * 91.7)));
    vec3 pos = position + jitter * scatter * (0.5 + aRand * 1.3);

    // Gentle breathing once formed.
    pos += aNormal * sin(uTime * 0.7 + aRand * 6.2831) * 0.006 * uForm;

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    vec3 n = normalize(normalMatrix * aNormal);
    vec3 viewDir = normalize(-mvPosition.xyz);
    float facing = dot(n, viewDir);

    // Sharp fresnel rim — the glowing silhouette edge.
    float rim = pow(clamp(1.0 - abs(facing), 0.0, 1.0), uRimPower);
    float vis = smoothstep(-0.2, 0.12, facing); // fade out back-facing points

    // Soft studio light on the normals: reveals the face once formed — nose,
    // brows, lips and cheeks catch the light, eye sockets and under-nose fall
    // into shadow. Gated on uForm so the dispersed intro keeps its bare dust.
    vec3 L = normalize(vec3(-0.35, 0.5, 0.85));
    float diff = max(dot(n, L), 0.0);

    vIntensity = (uBase + rim * uRimIntensity) * vis;
    vIntensity += diff * uDiff * vis * uForm;
    // While dispersed, let the dust read faintly even where not on a rim.
    vIntensity += scatter * (0.04 + 0.06 * aRand);

    vTwinkle = 0.8 + 0.2 * sin(uTime * 2.0 + aRand * 30.0);

    // Density rises as the head forms: the dispersed intro shows a sparse subset
    // (its approved look), points fill in to the full dense face once formed.
    float keep = step(aRand, mix(0.36, 1.0, uForm));
    gl_PointSize = uSize * uDpr * (300.0 / -mvPosition.z) * (0.55 + aRand * 0.9) * keep;
    gl_Position = projectionMatrix * mvPosition;
  }
`

const fragmentShader = /* glsl */ `
  precision mediump float;
  uniform float uFade;
  varying float vIntensity;
  varying float vTwinkle;

  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if (d > 0.5) discard;
    float soft = smoothstep(0.5, 0.0, d);
    float i = vIntensity * vTwinkle * uFade;
    gl_FragColor = vec4(vec3(i), soft * i);
  }
`

export function Head() {
  const data = useHeadPoints()
  const dpr = useStore((s) => s.dpr)
  const pointsRef = useRef<THREE.Points>(null)

  const geometry = useMemo(() => {
    if (!data) return null
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(data.positions, 3))
    g.setAttribute('aNormal', new THREE.BufferAttribute(data.normals, 3))
    g.setAttribute('aRand', new THREE.BufferAttribute(data.seeds, 1))
    g.computeBoundingSphere()
    return g
  }, [data])

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uForm: { value: 0 },
          uSize: { value: 0.02 },
          uRimPower: { value: 4.5 },
          uRimIntensity: { value: 0.08 },
          uBase: { value: 0.09 },
          uDiff: { value: 0.46 },
          uDpr: { value: dpr },
          uFade: { value: 1 },
        },
        vertexShader,
        fragmentShader,
        transparent: true,
        depthTest: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
      }),
    [dpr],
  )

  // Dispose GPU resources on geometry/material swap.
  useEffect(() => () => geometry?.dispose(), [geometry])
  useEffect(() => () => material.dispose(), [material])

  useFrame((_, delta) => {
    const s = sceneSample.current
    // Crossfade out where the solid head fades in (the muscles stage). Once the
    // dust has fully resolved into the solid face (fade ~0), skip drawing the
    // 200k-point cloud entirely — it's invisible for most of the scroll, so this
    // is the single biggest steady-state saving.
    const fade = 1 - s.layers.face
    if (pointsRef.current) pointsRef.current.visible = fade > 0.01
    if (fade <= 0.01) return
    material.uniforms.uTime.value += delta
    material.uniforms.uForm.value = s.form
    // Rim kept minimal — the boundary reads by point density, not a bright edge.
    material.uniforms.uRimIntensity.value = 0.06 + s.rim * 0.04
    material.uniforms.uFade.value = fade
  })

  if (!geometry) return null

  return <points ref={pointsRef} geometry={geometry} material={material} />
}
