import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import gsap from 'gsap'
import { useStore } from '@/store/useStore'
import { clamp01 } from '@/lib/num'
import { HomeScene, type Quality } from '@/home/scene'
import styles from './HomePage.module.css'

/**
 * The cinematic homepage (route `/`): one uninterrupted shot through a particle
 * cathedral, scrubbed by scroll. Statements surface and dissolve along the way;
 * everything converges into the MYOVOX logotype and the single call to action.
 *
 * Reduced motion (or no WebGL) skips the theater and shows the final screen.
 */

const STORY_PATH = '/story'

/** Each statement owns a slice of scroll progress; it fades in, holds, dissolves. */
const STATEMENTS = [
  { p0: 0.045, p1: 0.13, text: 'Nothing has been spoken.' },
  { p0: 0.155, p1: 0.25, text: 'Yet something already exists.' },
  { p0: 0.3, p1: 0.395, text: 'Speech begins before sound.' },
  { p0: 0.435, p1: 0.55, text: 'Invisible. Electrical. Human.' },
  { p0: 0.575, p1: 0.665, text: 'Language lives inside motion.' },
  { p0: 0.75, p1: 0.85, text: 'MYOVOX reads what the world cannot hear.' },
] as const

const END_CARD_AT = 0.95

/** ponytail: static device buckets; add live FPS-adaptive degradation only if reports demand it. */
function pickQuality(): Quality {
  const coarse = window.matchMedia('(pointer: coarse)').matches
  const count = !coarse ? 140_000 : window.innerWidth < 600 ? 26_000 : 60_000
  return { count, dpr: Math.min(window.devicePixelRatio || 1, coarse ? 1.5 : 2) }
}

function statementOpacity(p: number, p0: number, p1: number): number {
  const local = (p - p0) / (p1 - p0)
  if (local <= 0 || local >= 1) return 0
  const inK = clamp01(local / 0.3)
  const outK = clamp01((1 - local) / 0.3)
  return inK * inK * (3 - 2 * inK) * outK * outK * (3 - 2 * outK)
}

export function HomePage() {
  const navigate = useNavigate()
  const reducedMotion = useStore((s) => s.reducedMotion)
  const [fallback, setFallback] = useState(false)
  const still = reducedMotion || fallback

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const statementRefs = useRef<(HTMLParagraphElement | null)[]>([])
  const endCardRef = useRef<HTMLDivElement>(null)
  const hintRef = useRef<HTMLParagraphElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (still || !canvas) return

    let scene: HomeScene | null = null
    let disposed = false
    const pointer = { x: 0, y: 0, tx: 0, ty: 0 }
    const start = performance.now()

    const onPointer = (e: PointerEvent) => {
      pointer.tx = (e.clientX / window.innerWidth - 0.5) * 2
      pointer.ty = -(e.clientY / window.innerHeight - 0.5) * 2
    }
    const onResize = () => scene?.resize(window.innerWidth, window.innerHeight)

    const tick = (_t: number, deltaMs: number) => {
      if (!scene) return
      const dt = Math.min(deltaMs / 1000, 0.05)
      const doc = document.documentElement
      const range = doc.scrollHeight - window.innerHeight
      const p = range > 0 ? clamp01(doc.scrollTop / range) : 0

      pointer.x += (pointer.tx - pointer.x) * Math.min(1, dt * 3)
      pointer.y += (pointer.ty - pointer.y) * Math.min(1, dt * 3)
      scene.setParallax(pointer.x, pointer.y)
      scene.frame(p, dt)

      STATEMENTS.forEach((s, i) => {
        const el = statementRefs.current[i]
        if (!el) return
        const o = statementOpacity(p, s.p0, s.p1)
        el.style.opacity = o.toFixed(3)
        el.style.visibility = o > 0.001 ? 'visible' : 'hidden'
        const local = clamp01((p - s.p0) / (s.p1 - s.p0))
        el.style.transform = `translateY(${(0.5 - local) * 34}px)`
      })

      const end = endCardRef.current
      if (end) {
        const o = clamp01((p - END_CARD_AT) / 0.04)
        end.style.opacity = o.toFixed(3)
        end.style.pointerEvents = o > 0.6 ? 'auto' : 'none'
      }

      const hint = hintRef.current
      if (hint) {
        const settled = clamp01((performance.now() - start - 5500) / 1500)
        hint.style.opacity = (settled * clamp01((0.02 - p) / 0.01)).toFixed(3)
      }
    }

    HomeScene.create(canvas, pickQuality())
      .then((s) => {
        if (disposed) {
          s.dispose()
          return
        }
        scene = s
        s.resize(window.innerWidth, window.innerHeight)
        window.addEventListener('resize', onResize)
        window.addEventListener('pointermove', onPointer, { passive: true })
        gsap.ticker.add(tick)
      })
      .catch(() => setFallback(true))

    return () => {
      disposed = true
      gsap.ticker.remove(tick)
      window.removeEventListener('resize', onResize)
      window.removeEventListener('pointermove', onPointer)
      scene?.dispose()
      scene = null
    }
  }, [still])

  return (
    <div className={still ? styles.still : styles.journey}>
      {!still && <canvas ref={canvasRef} className={styles.canvas} aria-hidden="true" />}
      <div className={styles.vignette} aria-hidden="true" />

      {/* The narrative, readable by assistive tech as plain prose. */}
      <p className="sr-only">
        Nothing has been spoken — yet something already exists. Speech begins before sound:
        invisible, electrical, human. Language lives inside motion. MYOVOX reads what the world
        cannot hear.
      </p>

      {!still && (
        <>
          <div className={styles.statements} aria-hidden="true">
            {STATEMENTS.map((s, i) => (
              <p
                key={s.text}
                ref={(el) => {
                  statementRefs.current[i] = el
                }}
                className={`${styles.statement} display glow`}
              >
                {s.text}
              </p>
            ))}
          </div>
          <p ref={hintRef} className={`${styles.hint} label`} aria-hidden="true">
            Scroll
          </p>
        </>
      )}

      <div
        ref={endCardRef}
        className={still ? `${styles.endCard} ${styles.endCardStill}` : styles.endCard}
      >
        <h1 className={`${styles.logo} display glow-strong`}>MYOVOX</h1>
        <div className={styles.meta}>
          <p className={`${styles.subline} label`}>Reading Speech From Facial Muscles</p>
          <p className={styles.stats}>
            <span>18.53% Word Error Rate</span>
            <span className={styles.dot} aria-hidden="true" />
            <span>Open Vocabulary</span>
            <span className={styles.dot} aria-hidden="true" />
            <span>No Microphone Required</span>
          </p>
          <button type="button" className={styles.cta} onClick={() => navigate(STORY_PATH)}>
            Learn How It Works <span aria-hidden="true">→</span>
          </button>
        </div>
      </div>
    </div>
  )
}
