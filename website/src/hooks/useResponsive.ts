import { useEffect } from 'react'
import { useStore } from '@/store/useStore'

/**
 * Detects the runtime environment (small screen, reduced-motion preference) and
 * writes the flags into the store. Mount once near the root. Reduced motion
 * swaps clip scrubbing / idle motion for static posters for motion-sensitive users.
 */
export function useResponsive(): void {
  const setEnv = useStore((s) => s.setEnv)

  useEffect(() => {
    const mqMobile = window.matchMedia('(max-width: 820px), (pointer: coarse)')
    const mqMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

    const compute = () => setEnv({ isMobile: mqMobile.matches, reducedMotion: mqMotion.matches })

    compute()
    mqMobile.addEventListener('change', compute)
    mqMotion.addEventListener('change', compute)
    return () => {
      mqMobile.removeEventListener('change', compute)
      mqMotion.removeEventListener('change', compute)
    }
  }, [setEnv])
}

/** Read the reduced-motion preference synchronously (for first-render config). */
export function getInitialReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
