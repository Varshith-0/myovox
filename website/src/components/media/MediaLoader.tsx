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
  const reduced = useStore((s) => s.reducedMotion)
  if (reduced || !loading) return null

  return (
    <div className={styles.loader} role="status" aria-live="polite">
      <LogoMark size={44} duration={1.4} />
      <span className={styles.text}>Animation is loading, one moment</span>
    </div>
  )
}
