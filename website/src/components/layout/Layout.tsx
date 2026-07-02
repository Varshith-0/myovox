import { type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Nav } from './Nav'
import { Footer } from './Footer'
import { Loader } from './Loader'
import { OfflineBanner } from './OfflineBanner'
import styles from './Layout.module.css'

/**
 * App shell: the fixed nav floats on top; routed page content scrolls beneath.
 * The story is now entirely Manim clips (the MediaLayer), so there is no WebGL
 * scene behind it — just the black backdrop. The footer is shown only on the
 * reading pages — the Story ends immersively on its final stage.
 */
export function Layout({ children }: { children: ReactNode }) {
  const isStory = useLocation().pathname === '/'
  return (
    <>
      <a
        href="#main"
        className={styles.skip}
        onClick={(e) => {
          e.preventDefault()
          const el = document.getElementById('main')
          el?.focus()
          el?.scrollIntoView()
        }}
      >
        Skip to content
      </a>
      <OfflineBanner />
      <Nav />
      <main id="main" tabIndex={-1} className={styles.main}>
        {children}
      </main>
      {!isStory && <Footer />}
      <Loader />
    </>
  )
}
