import { SITE } from '@/data/site'
import styles from './Footer.module.css'

/** Quiet footer: credit, repo link, and the source attribution. */
export function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.row}>
        <span className={styles.label}>{SITE.brand}</span>
        <a className={styles.link} href={SITE.repoUrl} target="_blank" rel="noreferrer noopener">
          {SITE.repoUrl.replace('https://', '')}
        </a>
      </div>
      <p className={styles.fine}>
        Myovox is a cinematic, scroll-driven explainer of surface-EMG speech decoding: how
        facial-muscle electrical signals are transformed into text with an 18.53% word error
        rate. Built by Varshith Madishetty, open-sourced under MIT, and paired with a full
        technical report and reproducible pipeline so every claim on this site is auditable.
      </p>
    </footer>
  )
}
