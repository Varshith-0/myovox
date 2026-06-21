import { useFrame } from '@react-three/fiber'
import { scroll } from '@/store/scroll'
import { advanceScene } from '@/store/sceneSample'
import { useStore } from '@/store/useStore'

/**
 * The single per-frame driver: eases the shared scene sample toward the current
 * scroll progress. Mounted first inside the Canvas so its `useFrame` runs before
 * the layers that read the sample. Reduced motion → instant (no easing).
 */
export function SceneDriver() {
  const reduced = useStore((s) => s.reducedMotion)
  useFrame(() => {
    advanceScene(scroll.progress, reduced ? 1 : 0.09)
  })
  return null
}
