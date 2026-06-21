import { useEffect, useState } from 'react'
import { useStore } from '@/store/useStore'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './Loader.module.css'

/**
 * Tasteful black-and-white glow loading screen, shown until the head point
 * cloud reports ready (Suspense-adjacent — gated on the store flag). Fades out,
 * then unmounts so it never traps focus.
 */
export function Loader() {
  const ready = useStore((s) => s.ready)
  const [unmounted, setUnmounted] = useState(false)

  useEffect(() => {
    if (!ready) return
    const t = window.setTimeout(() => setUnmounted(true), 800)
    return () => window.clearTimeout(t)
  }, [ready])

  if (unmounted) return null

  return (
    <div className={`${styles.loader} ${ready ? styles.done : ''}`} role="status" aria-live="polite">
      <LogoMark size={64} duration={ready ? 1.4 : 6} />
      <span className={styles.text}>{ready ? 'Ready' : 'Materializing'}</span>
    </div>
  )
}
