import type { SceneParams } from '@/data/stages'
import { sampleScene } from '@/data/stages'

/**
 * The live, eased scene state for the current frame. A single driver component
 * advances it once per frame (lerping toward the raw scroll progress for
 * inertia); every 3D layer reads `sceneSample.current` in its own `useFrame`.
 * Sharing one sample avoids each layer lerping independently (which would drift)
 * and keeps the per-stage interpolation in exactly one place.
 */
export const sceneSample: { current: SceneParams; eased: number; energy: number } = {
  current: sampleScene(0),
  eased: 0,
  // How far the eased scene is trailing the raw scroll — a cheap, smoothed proxy
  // for "scroll speed" (0 at rest). Read by the post FX to swell the bloom as you
  // move and settle it when you stop. Stays 0 for reduced motion (eased == target).
  energy: 0,
}

/**
 * Advance the eased progress toward `target` and recompute the sample.
 * @param target raw scroll progress 0→1
 * @param lerp   smoothing factor per frame (1 = instant, for reduced motion)
 */
export function advanceScene(target: number, lerp: number): void {
  const gap = Math.abs(target - sceneSample.eased)
  sceneSample.energy += (gap - sceneSample.energy) * 0.18 // smooth so it glides, not flickers
  sceneSample.eased += (target - sceneSample.eased) * lerp
  sceneSample.current = sampleScene(sceneSample.eased)
}
