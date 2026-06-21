import type { CSSProperties } from 'react'
import styles from './LogoMark.module.css'

interface LogoMarkProps {
  /** Rendered square size in px. */
  size?: number
  /** Seconds for the satellite dot to complete one clockwise revolution. */
  duration?: number
  className?: string
}

/**
 * The brand mark: a fixed central dot ringed by an orbit, with a small dot on
 * a pendant line that rolls clockwise a full round. Shared by the loader and
 * the nav so the loading state and the wordmark read as the same object.
 */
export function LogoMark({ size = 32, duration = 7, className }: LogoMarkProps) {
  return (
    <svg
      className={`${styles.logo} ${className ?? ''}`}
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      style={{ '--spin': `${duration}s` } as CSSProperties}
    >
      <circle className={styles.ring} cx="16" cy="16" r="9" />
      <g className={styles.orbiter}>
        <line className={styles.thread} x1="16" y1="16" x2="29.5" y2="16" />
        <circle className={styles.satellite} cx="29.5" cy="16" r="2" />
      </g>
      <circle className={styles.core} cx="16" cy="16" r="3.1" />
    </svg>
  )
}
