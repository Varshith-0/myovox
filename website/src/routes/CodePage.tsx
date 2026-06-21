import { SNIPPETS } from '@/content/snippets'
import { SITE } from '@/data/site'
import { CodeBlock } from '@/components/ui/CodeBlock'
import styles from './CodePage.module.css'

/**
 * The implementation showcase: a prominent repository link, then curated,
 * faithful excerpts of the pipeline (objective, encoder, contrastive term,
 * decode config, reproduce commands), each with a monochrome syntax block.
 */
export function CodePage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <span className="label">The implementation</span>
        <h1 className={`display ${styles.title}`}>Code</h1>
        <p className={styles.lede}>
          The full pipeline — features, the Conformer, the four-term distillation, the WFST decode,
          and the LLM reranker — is open source. Below are the load-bearing pieces; the repository has
          the rest, with one idempotent command to reproduce every number.
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

      <section className={styles.snippets}>
        {SNIPPETS.map((s) => (
          <article key={s.id} className={styles.snippet}>
            <div className={styles.snippetHead}>
              <h2 className={styles.snippetTitle}>{s.title}</h2>
              <code className={styles.snippetSource}>{s.source}</code>
            </div>
            <p className={styles.snippetDesc}>{s.description}</p>
            <div className={styles.codeWrap}>
              <CodeBlock code={s.code} language={s.language} />
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}
