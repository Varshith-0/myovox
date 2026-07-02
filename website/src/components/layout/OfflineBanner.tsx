import { useSyncExternalStore } from 'react'
import styles from './ErrorScreen.module.css'

const subscribe = (onChange: () => void) => {
  window.addEventListener('online', onChange)
  window.addEventListener('offline', onChange)
  return () => {
    window.removeEventListener('online', onChange)
    window.removeEventListener('offline', onChange)
  }
}

/**
 * Non-blocking bar shown when the connection drops after the page has loaded —
 * the honest "internet down" signal for a static site (a first-load failure
 * happens before any of our JS runs, so the browser owns that case).
 */
export function OfflineBanner() {
  const online = useSyncExternalStore(
    subscribe,
    () => navigator.onLine,
    () => true, // assume online for the first paint
  )
  if (online) return null
  return (
    <div className={styles.banner} role="status" aria-live="polite">
      <span className={styles.dot} />
      You’re offline — some clips may not load.
    </div>
  )
}
