import { useEffect, useMemo, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { loadHeadMesh, type HeadMesh } from '@/three/headMesh'
import { sceneSample } from '@/store/sceneSample'

/**
 * A black solid of the head, sitting just inside the point cloud. It writes
 * depth (and renders black on the black scene, so it's invisible), which hides
 * the back-facing points so the head reads as a luminous rim-lit shell rather
 * than a translucent ball of dots. Absent gracefully if the binary is missing.
 */
export function HeadOccluder() {
  const [mesh, setMesh] = useState<HeadMesh | null>(null)
  const ref = useRef<THREE.Mesh>(null)

  // The occluder is sized to the point cloud; once the solid head takes over on
  // the muscles stage it would clip the new mesh, so retire it there.
  useFrame(() => {
    if (ref.current) ref.current.visible = sceneSample.current.layers.face < 0.4
  })

  useEffect(() => {
    let alive = true
    loadHeadMesh(`${import.meta.env.BASE_URL}head-mesh.bin`).then((m) => {
      if (alive) setMesh(m)
    })
    return () => {
      alive = false
    }
  }, [])

  const geometry = useMemo(() => {
    if (!mesh) return null
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(mesh.positions, 3))
    g.setIndex(new THREE.BufferAttribute(mesh.indices, 1))
    g.computeBoundingSphere()
    return g
  }, [mesh])

  useEffect(() => () => geometry?.dispose(), [geometry])

  if (!geometry) return null

  return (
    <mesh ref={ref} geometry={geometry} scale={0.985}>
      <meshBasicMaterial color="#000000" toneMapped={false} />
    </mesh>
  )
}
