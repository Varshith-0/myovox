import { useEffect, useState } from 'react'
import { useStore } from '@/store/useStore'
import { buildProceduralHead, loadBakedHead, type HeadData } from '@/three/headGeometry'

/**
 * Resolves the head point cloud: tries the baked binary first, falls back to the
 * procedural head, and flips the store `ready` flag (dismisses the loader) once
 * geometry is available. Point count scales down on low-power devices.
 */
export function useHeadPoints(): HeadData | null {
  const setReady = useStore((s) => s.setReady)
  const lowPower = useStore((s) => s.lowPower)
  const [data, setData] = useState<HeadData | null>(null)

  useEffect(() => {
    let alive = true
    const count = lowPower ? 55000 : 200000
    const url = `${import.meta.env.BASE_URL}head-points.bin`

    loadBakedHead(url, count)
      .then((baked) => baked ?? buildProceduralHead(count))
      .then((resolved) => {
        if (!alive) return
        setData(resolved)
        setReady(true)
      })

    return () => {
      alive = false
    }
  }, [lowPower, setReady])

  return data
}
