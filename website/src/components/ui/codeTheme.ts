import type { CSSProperties } from 'react'

/**
 * A strictly monochrome Prism theme — token "colours" are shades of grey/white
 * only (comments dim, keywords bright), honoring the no-hue brand. Passed to
 * react-syntax-highlighter as its `style`.
 */
const base: CSSProperties = {
  color: '#d7d7d3',
  background: 'none',
  fontFamily: 'var(--font-mono)',
  fontSize: '0.82rem',
  lineHeight: 1.7,
  textShadow: 'none',
}

const tok = (color: string, extra: CSSProperties = {}): CSSProperties => ({ color, ...extra })

export const monoCodeStyle: Record<string, CSSProperties> = {
  'code[class*="language-"]': base,
  'pre[class*="language-"]': { ...base, margin: 0, padding: 0, overflow: 'auto' },
  comment: tok('#67676a', { fontStyle: 'italic' }),
  prolog: tok('#67676a'),
  doctype: tok('#67676a'),
  cdata: tok('#67676a'),
  punctuation: tok('#8c8c89'),
  property: tok('#cfcfcb'),
  tag: tok('#f1f0ed'),
  boolean: tok('#f5f4f1'),
  number: tok('#cfcfcb'),
  constant: tok('#e8e7e4'),
  symbol: tok('#cfcfcb'),
  selector: tok('#cfcfcb'),
  'attr-name': tok('#cfcfcb'),
  string: tok('#a9a9a5'),
  char: tok('#a9a9a5'),
  builtin: tok('#f1f0ed'),
  inserted: tok('#f1f0ed'),
  operator: tok('#9a9a97'),
  entity: tok('#d7d7d3'),
  url: tok('#a9a9a5'),
  'attr-value': tok('#a9a9a5'),
  keyword: tok('#f5f4f1', { fontWeight: 600 }),
  function: tok('#ecebe8'),
  'class-name': tok('#f1f0ed'),
  regex: tok('#a9a9a5'),
  important: tok('#ffffff', { fontWeight: 700 }),
  variable: tok('#d7d7d3'),
}
