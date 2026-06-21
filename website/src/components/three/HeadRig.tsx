import { Suspense, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { Head } from './Head'
import { HeadOccluder } from './HeadOccluder'
import { FaceHead } from './FaceHead'
import { Muscles } from './Muscles'
import { Electrodes } from './Electrodes'
import { SignalField } from './SignalField'
import { sceneSample } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * Groups the head and everything mounted to it (electrodes, signal stream) under
 * one transform so they rotate together. The per-stage head yaw plus a whisper
 * of idle rotation is applied once here.
 */
export function HeadRig() {
  const ref = useRef<THREE.Group>(null)
  const reduced = useStore((s) => s.reducedMotion)

  useFrame(() => {
    if (!ref.current) return
    const idle = reduced ? 0 : Math.sin(performance.now() * 0.0001) * 0.05
    ref.current.rotation.y = sceneSample.current.headYaw + idle
  })

  return (
    <group ref={ref}>
      <HeadOccluder />
      <Head />
      <Suspense fallback={null}>
        <FaceHead />
      </Suspense>
      <Muscles />
      <Electrodes />
      <SignalField />
    </group>
  )
}
