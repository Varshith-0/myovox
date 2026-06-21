import { lazy, Suspense, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Nav } from './Nav'
import { Footer } from './Footer'
import { Loader } from './Loader'
import { SceneBoundary } from '@/components/three/SceneBoundary'
import styles from './Layout.module.css'

// The WebGL scene pulls in three.js + postprocessing — by far the largest
// dependency. Load it as its own chunk so the document and nav paint instantly;
// the Loader overlay covers the brief gap until the head is ready.
const Scene = lazy(() => import('@/components/three/Scene').then((m) => ({ default: m.Scene })))

/**
 * App shell: the fixed full-viewport 3D scene sits behind everything; the fixed
 * nav floats on top; routed page content scrolls between them. The scene is
 * mounted once here (not per-route) so it persists across navigation. The footer
 * is shown only on the reading pages — the Story ends, immersively, on its final
 * stage (no footer to overlap the fixed caption).
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
      <SceneBoundary>
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </SceneBoundary>
      <Nav />
      <main id="main" tabIndex={-1} className={styles.main}>
        {children}
      </main>
      {!isStory && <Footer />}
      <Loader />
    </>
  )
}
