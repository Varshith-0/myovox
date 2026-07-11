import { useStore } from '@/store/useStore'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './MediaLoader.module.css'

/**
 * "Rendering…" overlay shown in the clip band while the active clip's frames are
 * still loading — e.g. after a fast scroll outran the preload window. Driven by
 * `store.mediaLoading`, which the scrubber sets (debounced) whenever the current
 * frame stays un-drawable. It replaces the bare black canvas so the reader knows
 * the animation is coming, not broken. Its own component so toggling it never
 * re-renders the MediaLayer scrubber. Hidden in reduced motion (posters are static).
 */
export function MediaLoader() {
  const loading = useStore((s) => s.mediaLoading)
  const reason = useStore((s) => s.mediaLoadReason)
  const quality = useStore((s) => s.activeQuality)
  const reduced = useStore((s) => s.reducedMotion)
  if (reduced || !loading) return null

  // Honest reasons: either the pipe is the bottleneck (especially with a pinned
  // high tier) or the reader simply outran the preloader.
  const text =
    reason === 'network'
      ? `Weak connection — loading the ${quality}p animation…`
      : 'Preparing animation — one moment'

  return (
    <div className={styles.loader} role="status" aria-live="polite">
      <LogoMark size={44} duration={1.4} />
      <span className={styles.text}>{text}</span>
    </div>
  )
}
