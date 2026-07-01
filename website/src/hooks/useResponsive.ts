import { useEffect } from 'react'
import { useStore } from '@/store/useStore'

/**
 * Tracks the reduced-motion preference and writes it into the store. Mount once
 * near the root. Reduced motion swaps clip scrubbing / idle motion for static
 * posters for motion-sensitive users.
 */
export function useResponsive(): void {
  const setReducedMotion = useStore((s) => s.setReducedMotion)

  useEffect(() => {
    const mqMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const compute = () => setReducedMotion(mqMotion.matches)

    compute()
    mqMotion.addEventListener('change', compute)
    return () => mqMotion.removeEventListener('change', compute)
  }, [setReducedMotion])
}

/** Read the reduced-motion preference synchronously (for first-render config). */
export function getInitialReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
