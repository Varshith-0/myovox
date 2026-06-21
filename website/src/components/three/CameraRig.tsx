import { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * Applies the eased per-stage camera keyframe (position + look-at) every frame,
 * with a whisper of idle drift so the scene feels alive when still. Reads the
 * shared scene sample — never the DOM.
 */
export function CameraRig() {
  const camera = useThree((s) => s.camera)
  const reduced = useStore((s) => s.reducedMotion)
  const target = useRef(new THREE.Vector3())

  useFrame(() => {
    const s = sceneSample.current
    const drift = reduced ? 0 : 1
    const t = performance.now() * 0.0002
    camera.position.set(
      s.camPos[0] + Math.sin(t) * 0.05 * drift,
      s.camPos[1] + Math.cos(t * 1.3) * 0.04 * drift,
      s.camPos[2],
    )
    target.current.set(s.camTarget[0], s.camTarget[1], s.camTarget[2])
    camera.lookAt(target.current)
  })

  return null
}
