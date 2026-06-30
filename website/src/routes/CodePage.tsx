import { SITE } from '@/data/site'
import styles from './CodePage.module.css'

/**
 * Not a code tour — a pointer to the source and a note on who built it. The
 * full pipeline, this website, and the technical report are open source; this
 * page leads with the repository and credits the author.
 */
export function CodePage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <span className="label">Open source</span>
        <h1 className={`display ${styles.title}`}>Code</h1>
        <p className={styles.lede}>
          Everything here — the EMG-to-text pipeline, this website, and the technical report — is
          open source under the MIT license, with one idempotent command to reproduce every number.

        </p>
        <a className={styles.repo} href={SITE.repoUrl} target="_blank" rel="noreferrer noopener">
          <span className={styles.repoIcon} aria-hidden="true" />
          <span className={styles.repoText}>
            <span className={styles.repoLabel}>View the repository</span>
            <span className={styles.repoUrl}>{SITE.repoUrl.replace('https://', '')}</span>
          </span>
          <span className={styles.repoArrow} aria-hidden="true">
            →
          </span>
        </a>
      </header>

      <section className={styles.author}>
        <span className="label">The author</span>
        <h2 className={styles.authorName}>{SITE.author}</h2>
        <p className={styles.authorBio}>Built with the help of Claude.</p>
        <a
          className={styles.authorLink}
          href={SITE.authorUrl}
          target="_blank"
          rel="noreferrer noopener"
        >
          {SITE.authorUrl.replace('https://', '')}
          <span className={styles.authorArrow} aria-hidden="true">
            →
          </span>
        </a>
      </section>
    </div>
  )
}
