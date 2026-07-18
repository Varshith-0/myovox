import { useEffect, useMemo, useState, isValidElement, type ReactNode } from 'react'
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

/** Distance from the viewport top that counts as "at the top" — clears the nav. */
const SCROLL_OFFSET = 96

interface TocItem {
  text: string
  slug: string
}

export function TechnicalPage() {
  const lenis = useLenis()
  const [activeSlug, setActiveSlug] = useState('')

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
    // Scroll to an absolute position rather than passing the element: `.page` is
    // a positioned ancestor, so Lenis's element path measures offsetTop against
    // it and lands the heading ~80px below the nav line — which would also put it
    // past the line the scroll-spy below uses to decide the active section.
    const y = el.getBoundingClientRect().top + window.scrollY - SCROLL_OFFSET
    if (lenis) lenis.scrollTo(y)
    else window.scrollTo({ top: y, behavior: 'smooth' })
  }

  // The active section is the last one whose heading has crossed the nav line —
  // deterministic where an IntersectionObserver would be ambiguous for sections
  // shorter than the viewport, or when several are on screen at once.
  useEffect(() => {
    const read = () => {
      let current = ''
      for (const { slug } of toc) {
        const el = document.getElementById(slug)
        if (!el) continue
        if (el.getBoundingClientRect().top <= SCROLL_OFFSET + 8) current = slug
        else break
      }
      // Before the first heading scrolls up, keep the first entry lit.
      setActiveSlug(current || toc[0]?.slug || '')
    }
    read()
    window.addEventListener('scroll', read, { passive: true })
    window.addEventListener('resize', read)
    return () => {
      window.removeEventListener('scroll', read)
      window.removeEventListener('resize', read)
    }
  }, [toc])

  // Heading renderers share one shape: every heading is a jump target, because the
  // report's glossary and FAQ cross-link into them by slug (see tex2md).
  const markdownComponents = useMemo<Components>(
    () => ({
      h1: ({ children }) => <h1 className={`display ${styles.h1}`}>{children}</h1>,
      h2: ({ children }) => (
        <h2 id={slugify(toText(children))} className={styles.h2}>
          {children}
        </h2>
      ),
      h3: ({ children }) => (
        <h3 id={slugify(toText(children))} className={styles.h3}>
          {children}
        </h3>
      ),
      h4: ({ children }) => (
        <h4 id={slugify(toText(children))} className={styles.h4}>
          {children}
        </h4>
      ),
      h5: ({ children }) => (
        <h5 id={slugify(toText(children))} className={styles.h5}>
          {children}
        </h5>
      ),
      p: ({ children }) => <p className={styles.p}>{children}</p>,
      ul: ({ children }) => <ul className={styles.ul}>{children}</ul>,
      ol: ({ children }) => <ol className={styles.ol}>{children}</ol>,
      li: ({ children }) => <li className={styles.li}>{children}</li>,
      blockquote: ({ children }) => <blockquote className={styles.quote}>{children}</blockquote>,
      hr: () => <hr className={styles.hr} />,
      a: ({ href, children }) => {
        // In-page jumps (glossary terms, citations, section/table/question
        // cross-references) scroll through Lenis; anything else is external.
        if (href?.startsWith('#')) {
          const slug = href.slice(1)
          // `[](#ref-3)` — a link with no text is not a link, it is the jump
          // target itself. It is how the generated markdown puts an id on a
          // reference list item, which markdown alone cannot express.
          if (!toText(children)) return <span id={slug} className={styles.anchor} />
          return (
            <a
              href={href}
              className={styles.jump}
              onClick={(e) => {
                e.preventDefault()
                goto(slug)
                history.replaceState(null, '', `#${slug}`)
              }}
            >
              {children}
            </a>
          )
        }
        return (
          <a href={href} target="_blank" rel="noreferrer noopener" className={styles.link}>
            {children}
          </a>
        )
      },
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
    }),
    // `goto` closes over lenis; rebuild the renderers when it arrives.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [lenis],
  )

  // A deep link (/technical#hlg) lands before the article has rendered, and the
  // syntax highlighter keeps shifting layout for a while after — so a single scroll
  // aims at a stale position, missing targets low in the report (e.g. an FAQ answer).
  // Re-scroll until the target's absolute position stops moving, then stop.
  useEffect(() => {
    if (!window.location.hash) return
    const id = window.location.hash.slice(1)
    let lastY = -1
    let tries = 0
    let t = 0
    const settle = () => {
      const el = document.getElementById(id)
      if (el) {
        const y = el.getBoundingClientRect().top + window.scrollY - SCROLL_OFFSET
        goto(id)
        if (Math.abs(y - lastY) <= 2 || tries >= 12) return // layout settled
        lastY = y
      }
      tries += 1
      t = window.setTimeout(settle, 120)
    }
    t = window.setTimeout(settle, 100)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lenis])

  return (
    <div className={styles.page}>
      <nav className={styles.toc} aria-label="Report contents">
        <span className="label">Contents</span>
        <ol className={styles.tocList}>
          {toc.map((item) => (
            <li key={item.slug}>
              <button
                type="button"
                className={`${styles.tocLink} ${item.slug === activeSlug ? styles.tocLinkActive : ''}`}
                aria-current={item.slug === activeSlug ? 'true' : undefined}
                onClick={() => goto(item.slug)}
              >
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
