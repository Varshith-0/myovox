import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Bloom, EffectComposer, Noise, Vignette } from '@react-three/postprocessing'
import { useStore } from '@/store/useStore'
import { sceneSample } from '@/store/sceneSample'

/**
 * Post-processing for the look: soft white Bloom (the glow), a restrained
 * Vignette to sink the edges into black, and a faint film grain. No chromatic
 * aberration, no color — monochrome only. Simplified on low-power devices.
 *
 * The bloom is driven every frame rather than held constant: each stage carries
 * its own `bloom` keyframe (the cinematography), and a smoothed scroll-energy
 * term swells the glow while you move and lets it settle when you stop — a quiet
 * sense of momentum that costs nothing extra (the bloom pass already runs).
 */
export function Effects() {
  const lowPower = useStore((s) => s.lowPower)
  // The effect instance forwards an `intensity` accessor; type it structurally so
  // we don't depend on the postprocessing package directly.
  const bloomRef = useRef<{ intensity: number } | null>(null)
  // Chosen so base × the typical per-stage keyframe (~1.05) lands on the original
  // at-rest bloom (0.7 desktop / 0.55 low-power); the swell rides on top.
  const base = lowPower ? 0.52 : 0.66

  useFrame(() => {
    const b = bloomRef.current
    if (!b) return
    const stageBloom = sceneSample.current.bloom // ~0.9–1.2 per stage
    const swell = Math.min(sceneSample.energy * 4, 0.4) // capped scroll-energy boost
    b.intensity = base * stageBloom + swell
  })

  return (
    <EffectComposer multisampling={lowPower ? 0 : 2} enableNormalPass={false}>
      <Bloom
        ref={bloomRef}
        intensity={base}
        luminanceThreshold={0.35}
        luminanceSmoothing={0.2}
        radius={0.6}
        mipmapBlur
      />
      <Vignette offset={0.28} darkness={0.92} eskil={false} />
      <Noise opacity={lowPower ? 0 : 0.025} premultiply />
    </EffectComposer>
  )
}
