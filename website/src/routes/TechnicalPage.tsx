import { useMemo, isValidElement, type ReactNode } from 'react'
import Markdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useLenis } from 'lenis/react'
import report from '@/content/technical_report.md?raw'
import { CodeBlock } from '@/components/ui/CodeBlock'
import styles from './TechnicalPage.module.css'

/** Flatten a React child tree to its text content (for heading slugs). */
function toText(node: ReactNode): string {
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(toText).join('')
  if (isValidElement(node)) return toText((node.props as { children?: ReactNode }).children)
  return ''
}

const slugify = (s: string) =>
  s
    .toLowerCase()
    .replace(/[^\w]+/g, '-')
    .replace(/^-+|-+$/g, '')

interface TocItem {
  text: string
  slug: string
}

const markdownComponents: Components = {
  h1: ({ children }) => <h1 className={`display ${styles.h1}`}>{children}</h1>,
  h2: ({ children }) => (
    <h2 id={slugify(toText(children))} className={styles.h2}>
      {children}
    </h2>
  ),
  h3: ({ children }) => <h3 className={styles.h3}>{children}</h3>,
  p: ({ children }) => <p className={styles.p}>{children}</p>,
  ul: ({ children }) => <ul className={styles.ul}>{children}</ul>,
  ol: ({ children }) => <ol className={styles.ol}>{children}</ol>,
  li: ({ children }) => <li className={styles.li}>{children}</li>,
  blockquote: ({ children }) => <blockquote className={styles.quote}>{children}</blockquote>,
  hr: () => <hr className={styles.hr} />,
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer noopener" className={styles.link}>
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className={styles.tableWrap}>
      <table className={styles.table}>{children}</table>
    </div>
  ),
  // react-markdown wraps block code in <pre><code>; flatten the <pre> and let the
  // <code> handler decide inline vs block, rendering our monochrome highlighter.
  pre: ({ children }) => <>{children}</>,
  code: ({ className, children }) => {
    const match = /language-(\w+)/.exec(className ?? '')
    const text = toText(children)
    const isBlock = Boolean(match) || text.includes('\n')
    if (!isBlock) return <code className={styles.inlineCode}>{children}</code>
    return (
      <div className={styles.codeBlock}>
        <CodeBlock code={text.replace(/\n$/, '')} language={match?.[1] ?? 'text'} />
      </div>
    )
  },
}

export function TechnicalPage() {
  const lenis = useLenis()

  const toc = useMemo<TocItem[]>(() => {
    const items: TocItem[] = []
    const re = /^##\s+(.+)$/gm
    let m: RegExpExecArray | null
    while ((m = re.exec(report)) !== null) {
      const text = m[1].trim()
      items.push({ text, slug: slugify(text) })
    }
    return items
  }, [])

  const goto = (slug: string) => {
    const el = document.getElementById(slug)
    if (!el) return
    if (lenis) lenis.scrollTo(el, { offset: -96 })
    else el.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className={styles.page}>
      <nav className={styles.toc} aria-label="Report contents">
        <span className="label">Contents</span>
        <ol className={styles.tocList}>
          {toc.map((item) => (
            <li key={item.slug}>
              <button type="button" className={styles.tocLink} onClick={() => goto(item.slug)}>
                {item.text}
              </button>
            </li>
          ))}
        </ol>
      </nav>

      <article className={styles.article}>
        <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
          {report}
        </Markdown>
      </article>
    </div>
  )
}
