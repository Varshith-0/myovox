import { useEffect, useState } from 'react'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './Loader.module.css'

/**
 * Tasteful black-and-white glow splash. The story is Manim clips (nothing to
 * wait on), so it shows a brief brand flash and then unmounts — never trapping
 * focus.
 */
export function Loader() {
  const [unmounted, setUnmounted] = useState(false)

  useEffect(() => {
    const t = window.setTimeout(() => setUnmounted(true), 800)
    return () => window.clearTimeout(t)
  }, [])

  if (unmounted) return null

  return (
    <div className={`${styles.loader} ${styles.done}`} role="status" aria-live="polite">
      <LogoMark size={64} duration={1.4} />
      <span className={styles.text}>Ready</span>
    </div>
  )
}
