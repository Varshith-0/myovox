import { useCallback, useState } from 'react'
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/esm/languages/prism/python'
import bash from 'react-syntax-highlighter/dist/esm/languages/prism/bash'
import json from 'react-syntax-highlighter/dist/esm/languages/prism/json'
import { monoCodeStyle } from './codeTheme'
import styles from './CodeBlock.module.css'

SyntaxHighlighter.registerLanguage('python', python)
SyntaxHighlighter.registerLanguage('bash', bash)
SyntaxHighlighter.registerLanguage('json', json)

/** Monochrome syntax-highlighted code block (lazy Prism, only the langs we use),
 *  with a copy-to-clipboard control so readers can lift a snippet in one click. */
export function CodeBlock({ code, language = 'text' }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false)

  const copy = useCallback(() => {
    void navigator.clipboard?.writeText(code).then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1600)
    })
  }, [code])

  return (
    <div className={styles.wrap}>
      <button
        type="button"
        className={styles.copy}
        onClick={copy}
        aria-label={copied ? 'Copied to clipboard' : 'Copy code to clipboard'}
      >
        {copied ? 'copied' : 'copy'}
      </button>
      <SyntaxHighlighter
        language={language}
        style={monoCodeStyle}
        customStyle={{ background: 'transparent', margin: 0, padding: 0 }}
        codeTagProps={{ style: { fontFamily: 'var(--font-mono)' } }}
        wrapLongLines
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}
