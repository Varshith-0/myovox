import { useEffect } from 'react'
import { useStore } from '@/store/useStore'

/**
 * Detects the runtime environment (small screen, reduced-motion preference,
 * weak hardware) and writes the flags into the store. Mount once near the root.
 * The 3D scene and animations read these flags to degrade gracefully — never
 * crash on mobile, never animate for motion-sensitive users.
 */
export function useResponsive(): void {
  const setEnv = useStore((s) => s.setEnv)

  useEffect(() => {
    const mqMobile = window.matchMedia('(max-width: 820px), (pointer: coarse)')
    const mqMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

    // `?lite` forces the low-power path (also a manual escape hatch for weak GPUs).
    const lite = new URLSearchParams(window.location.search).has('lite')

    const compute = () => {
      const isMobile = mqMobile.matches
      const reducedMotion = mqMotion.matches
      const cores = navigator.hardwareConcurrency ?? 8
      const lowPower = lite || isMobile || reducedMotion || cores <= 4
      // Cap the canvas resolution: the full-screen bloom/vignette/grain composite
      // is fill-rate bound, so rendering a HiDPI (2×) display at native pixels is
      // the dominant cost. 1.5× keeps the soft, bloom-heavy look crisp while
      // cutting ~40% of the pixels a 2× cap would push every frame.
      const dpr = lite ? 1 : Math.min(window.devicePixelRatio || 1, 1.5)
      setEnv({ isMobile, reducedMotion, lowPower, dpr })
    }

    compute()
    mqMobile.addEventListener('change', compute)
    mqMotion.addEventListener('change', compute)
    window.addEventListener('resize', compute, { passive: true })
    return () => {
      mqMobile.removeEventListener('change', compute)
      mqMotion.removeEventListener('change', compute)
      window.removeEventListener('resize', compute)
    }
  }, [setEnv])
}

/** Read the reduced-motion preference synchronously (for first-render config). */
export function getInitialReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
