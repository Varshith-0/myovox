import { LogoMark } from '@/components/ui/LogoMark'
import styles from './ErrorScreen.module.css'

export type ErrorVariant = 'crashed' | 'offline' | 'update'

const COPY: Record<ErrorVariant, { title: string; body: string; action: string }> = {
  offline: {
    title: "You're offline",
    body: 'This page needs a connection to load. Check your network and try again.',
    action: 'Retry',
  },
  update: {
    title: 'A new version is available',
    body: 'This page was updated since you opened it. Reload to get the latest.',
    action: 'Reload',
  },
  crashed: {
    title: 'Something broke',
    body: 'An unexpected error interrupted the page.',
    action: 'Reload',
  },
}

/**
 * Full-screen, brand-matched error state (reuses the loader's LogoMark so the
 * error reads as the same object as the splash). A full reload is the recovery
 * for every variant: it re-fetches a fresh index.html — new chunk hashes after a
 * deploy — and simply retries once the connection is back.
 */
export function ErrorScreen({ variant }: { variant: ErrorVariant }) {
  const { title, body, action } = COPY[variant]
  return (
    <div className={styles.screen} role="alert">
      <LogoMark size={64} duration={1.4} />
      <div className={styles.copy}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.body}>{body}</p>
      </div>
      <button type="button" className={styles.action} onClick={() => window.location.reload()}>
        {action}
      </button>
    </div>
  )
}
