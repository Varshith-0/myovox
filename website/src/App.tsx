import { lazy, Suspense, useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { ReactLenis, useLenis } from 'lenis/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

import { Layout } from '@/components/layout/Layout'
import { StoryPage } from '@/routes/StoryPage'
import { useLenisGsapSync } from '@/hooks/useLenis'
import { useResponsive, getInitialReducedMotion } from '@/hooks/useResponsive'
import { scroll } from '@/store/scroll'
import { useStore } from '@/store/useStore'
import { STAGES } from '@/data/stages'

// The reading pages pull in react-markdown + the syntax highlighter; load them
// only when visited so they stay out of the initial (Story) bundle.
const TechnicalPage = lazy(() =>
  import('@/routes/TechnicalPage').then((m) => ({ default: m.TechnicalPage })),
)
const CodePage = lazy(() => import('@/routes/CodePage').then((m) => ({ default: m.CodePage })))

gsap.registerPlugin(ScrollTrigger)

// GitHub Pages serves the site under /<repo>/; the router needs that prefix
// (trailing slash stripped, so "/" still matches the served root) to produce
// clean URLs like /myovox/code. See vite `base` and public/404.html.
const ROUTER_BASENAME = import.meta.env.BASE_URL.replace(/\/$/, '') || '/'

/** Lives inside <ReactLenis> so it can wire Lenis into the GSAP ticker. */
function ScrollSync() {
  useLenisGsapSync()
  return null
}

/**
 * Dev-only handles (exposed on `window` in dev builds only) to drive scroll
 * deterministically from the console: to a raw progress, to a stage's top, or to
 * a precise sub-progress within a stage (to inspect the video scrub).
 */
function DevScrollHooks() {
  const lenis = useLenis()
  useEffect(() => {
    if (!import.meta.env.DEV || !lenis) return
    const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
    const w = window as unknown as Record<string, unknown>
    const sectionEl = (k: string | number) => {
      const id = typeof k === 'number' ? STAGES[k]?.id : k
      return id ? document.getElementById(id) : null
    }
    // Use Lenis's element scrolling (aligns the element top to the viewport top);
    // a positive `offset` scrolls further into a tall section for sub-progress.
    const goEl = (el: HTMLElement, offset: number) => {
      lenis.scrollTo(el, { immediate: true, offset })
      ScrollTrigger.update()
    }
    w.__lenis = lenis
    w.__ScrollTrigger = ScrollTrigger
    w.__scrollToProgress = (p: number) => {
      lenis.scrollTo(clamp01(p) * (document.documentElement.scrollHeight - window.innerHeight), {
        immediate: true,
      })
      ScrollTrigger.update()
    }
    w.__scrollToStage = (k: string | number) => {
      const el = sectionEl(k)
      if (el) goEl(el, 0)
    }
    w.__scrollToStageLocal = (k: string | number, local: number) => {
      const el = sectionEl(k)
      if (el) goEl(el, el.offsetHeight * clamp01(local)) // local = scrolled / section height
    }
  }, [lenis])
  return null
}

/** Per-route document title (client-side routing doesn't change it on its own) — so
 *  shared links and browser tabs read meaningfully instead of all saying the same thing. */
const ROUTE_TITLES: Record<string, string> = {
  '/': 'Myovox — reading speech from the muscles of the face',
  '/technical': 'Technical report — Myovox',
  '/code': 'Code — Myovox',
}
function DocumentTitle() {
  const { pathname } = useLocation()
  useEffect(() => {
    document.title = ROUTE_TITLES[pathname] ?? ROUTE_TITLES['/']
  }, [pathname])
  return null
}

/** Reset scroll + story state on route change (the router keeps the offset). */
function ScrollReset() {
  const { pathname } = useLocation()
  const lenis = useLenis()
  useEffect(() => {
    if (lenis) lenis.scrollTo(0, { immediate: true })
    else window.scrollTo(0, 0)
    scroll.progress = 0
    useStore.getState().setStageIndex(0)
    ScrollTrigger.refresh()
  }, [pathname, lenis])
  return null
}

/**
 * Root: BrowserRouter for clean URLs (no #). On GitHub Pages, public/404.html
 * redirects deep links back through index.html so refreshes/shared links resolve.
 * Wraps the Lenis smooth-scroll provider, the layout shell (fixed nav + footer),
 * and the three routes.
 */
export default function App() {
  useResponsive()
  // Disable smooth scrubbing for motion-sensitive users (instant lerp).
  const [reduceMotion] = useState(getInitialReducedMotion)

  return (
    <BrowserRouter basename={ROUTER_BASENAME}>
      <ReactLenis
        root
        options={{
          autoRaf: false, // GSAP ticker drives the RAF (see useLenisGsapSync)
          lerp: reduceMotion ? 1 : 0.1,
          duration: 1.2,
          smoothWheel: !reduceMotion,
        }}
      >
        <ScrollSync />
        <ScrollReset />
        <DocumentTitle />
        <DevScrollHooks />
        <Layout>
          <Suspense fallback={null}>
            <Routes>
              <Route path="/" element={<StoryPage />} />
              <Route path="/technical" element={<TechnicalPage />} />
              <Route path="/code" element={<CodePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </Layout>
      </ReactLenis>
    </BrowserRouter>
  )
}
