import { useEffect } from 'react'
import { useLenis } from 'lenis/react'
import Snap from 'lenis/snap'
import { STAGES } from '@/data/stages'
import { useStore } from '@/store/useStore'

/**
 * Mandatory scroll-snap for the story spine.
 *
 * Each stage is a full-viewport section; without snapping, Lenis momentum lets a
 * flick settle anywhere — half-way between two stages, or skidding past one. This
 * registers every section as a snap point (`align: 'start'`) with the Lenis snap
 * add-on in `mandatory` mode, so after the wheel settles the scroll always glides
 * to the nearest stage and never rests in the gap between two. The progress-rail
 * jump (a programmatic `lenis.scrollTo`) is unaffected — snap only reacts to real
 * wheel input, so clicking a stage still lands exactly as before.
 *
 * Smoothing is shared with the rest of the app: reduced-motion users get an
 * instant snap (no glide); everyone else gets a soft easeOut settle.
 *
 * Must be called from a component inside `<ReactLenis>` (for the Lenis context)
 * and only where the story sections exist in the DOM (the Story route).
 */
export function useScrollSnap(): void {
  const lenis = useLenis()
  const reduced = useStore((s) => s.reducedMotion)

  useEffect(() => {
    if (!lenis) return

    const snap = new Snap(lenis, {
      type: 'mandatory',
      // Soft, quick settle once the wheel stops; instant for reduced motion.
      duration: reduced ? 0.001 : 0.9,
      easing: (t) => 1 - Math.pow(1 - t, 3), // easeOutCubic
      // Wait briefly after the last wheel tick so a flick can glide before it
      // commits to the nearest stage (too short fights momentum; too long lags).
      debounce: 180,
    })

    const removers = STAGES.map((stage) => document.getElementById(stage.id))
      .filter((el): el is HTMLElement => el !== null)
      .map((el) => snap.addElement(el, { align: 'start' }))

    return () => {
      removers.forEach((remove) => remove())
      snap.destroy()
    }
  }, [lenis, reduced])
}
