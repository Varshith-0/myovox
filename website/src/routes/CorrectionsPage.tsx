import { Link } from 'react-router-dom'
import styles from './CorrectionsPage.module.css'

const EMG2SPEECH = 'https://arxiv.org/abs/2510.23969'
const EMG2TEXT = 'https://harshavardhanatg.github.io/emg2text.github.io/'
const FAQ = '/technical#q18-does-it-run-in-real-time'

/** External citation link — opens in a new tab, matches the report's link style. */
function Cite({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noreferrer noopener" className={styles.link}>
      {children}
    </a>
  )
}

/**
 * Corrections & Errata — a standalone letter documenting mistakes in the released
 * report, caught by Harshavardhana Gowda (author of the emg2speech work this builds
 * on). Rendered as a note in the middle of the page, in the site's serif. Papers are
 * cited inline and clickable; there is no separate references list.
 */
export function CorrectionsPage() {
  return (
    <div className={styles.page}>
      <article className={styles.letter}>
        <header className={styles.head}>
          <h1 className={`display ${styles.title}`}>Corrections &amp; Errata</h1>
        </header>

        <p className={styles.p}>
          After releasing this report, Harshavardhana Gowda, the author of the{' '}
          <Cite href={EMG2SPEECH}>emg2speech</Cite> work this project builds on, pointed out several
          mistakes. They&apos;re real, and I&apos;m documenting them here rather than quietly
          revising, because the record should be accurate. I&apos;m no longer developing this
          project, so these are corrections to the claims, not fixes to the numbers.
        </p>

        <p className={styles.p}>
          All of them trace to one root cause: I built on the{' '}
          <Cite href={EMG2SPEECH}>emg2speech paper</Cite> and its appendix (D.4) without finding the
          dedicated <Cite href={EMG2TEXT}>emg2text benchmark and its repository</Cite>, which
          already contained the correct baseline, the decoding graph, and the causal framing.
        </p>

        <ol className={styles.list}>
          <li className={styles.item}>
            <strong>The baseline I compared against is the wrong split.</strong> I anchored
            everything to 51.17% WER / 38.19% PER (<Cite href={EMG2SPEECH}>emg2speech</Cite>{' '}
            Table 6). That number is averaged over the General Corpus and the ALS data. The correct
            large-vocabulary-only reference is Table 2 (32.78% PER on the General Corpus). Two
            consequences follow: my headline &ldquo;51.17 to 18.53&rdquo; compares against a blended
            baseline rather than a General-only one, and my Section 4 credibility argument, matching
            PER to within 0.8 points, matched my General-only PER against the blended figure.
            &ldquo;Reproduced faithfully&rdquo; does not hold as I stated it.
          </li>
          <li className={styles.item}>
            <strong>The HLG decoding files were not missing.</strong> I described the decode graph
            (HLG = H∘L∘G), the lexicon, <code className={styles.code}>words.txt</code>, and the
            grammar as absent from the release and something I had to regenerate. They were
            published in the sister <Cite href={EMG2TEXT}>emg2text repository</Cite>. My
            blank-penalty and acoustic-scale tuning may be a small genuine addition, but the
            &ldquo;recovered the missing decode settings&rdquo; contribution overstates what was
            actually missing.
          </li>
          <li className={styles.item}>
            <strong>The bidirectional Conformer isn&apos;t a fair comparison.</strong> My single
            largest gain (14.49 WER points) comes from replacing the released causal encoder with a
            bidirectional, full-context one. That breaks streaming and is not a like-for-like
            comparison against the causal, streaming-capable models in{' '}
            <Cite href={EMG2SPEECH}>emg2speech</Cite>. The causal constraint is the entire point of
            that line of work. I noted this in the{' '}
            <Link to={FAQ} className={styles.link}>
              FAQ
            </Link>{' '}
            and limitations, but I led with the number anyway, which is misleading.
          </li>
        </ol>

        <p className={styles.p}>
          My thanks to Harsha for taking the time to catch these, and for being generous about it.
        </p>

        <footer className={styles.sign}>
          <p className={styles.p}>Regards,</p>
          <p className={styles.name}>Varshith Madishetty</p>
        </footer>
      </article>
    </div>
  )
}
