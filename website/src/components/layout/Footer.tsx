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
        A surface-EMG speech-decoding pipeline — 18.53% word error rate, reported honestly. Built by
        Varshith Madishetty, MIT-licensed. The 3D head is a point cloud sampled from the
        &ldquo;Lee Perry-Smith&rdquo; head scan (Infinite-Realities), used under CC-BY 3.0. All
        numbers are drawn from the project&rsquo;s technical report.
      </p>
    </footer>
  )
}
