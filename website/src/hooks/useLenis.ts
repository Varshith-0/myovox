import { useGSAP } from '@gsap/react'
import { useLenis } from 'lenis/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

/**
 * Bridges Lenis smooth scroll and GSAP into a single requestAnimationFrame loop.
 *
 * The rule (see build notes): Lenis must NOT self-drive (`autoRaf: false` on the
 * provider). GSAP's ticker is the one clock — it advances Lenis each tick, and
 * every Lenis scroll event pokes ScrollTrigger so triggers read the smoothed
 * offset. R3F keeps its own render loop and only *reads* the resulting scroll
 * value; it is never wired in here. `lagSmoothing(0)` stops a scroll jump when
 * the tab regains focus.
 *
 * Must be called from a component rendered *inside* `<ReactLenis>` so the
 * `useLenis()` context is available.
 */
export function useLenisGsapSync(): void {
  const lenis = useLenis()

  useGSAP(
    () => {
      if (!lenis) return
      const onScroll = () => ScrollTrigger.update()
      lenis.on('scroll', onScroll)

      const advance = (time: number) => lenis.raf(time * 1000) // GSAP sec → Lenis ms
      gsap.ticker.add(advance)
      gsap.ticker.lagSmoothing(0)

      ScrollTrigger.refresh()
      return () => {
        lenis.off('scroll', onScroll)
        gsap.ticker.remove(advance)
      }
    },
    { dependencies: [lenis] },
  )
}
