import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import gsap from 'gsap'
import { useStore } from '@/store/useStore'
import { clamp01 } from '@/lib/num'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './HomePage.module.css'

/**
 * The homepage (route `/`): one still, centered lockup — mark, wordmark,
 * tagline, facts, one button — with a single living detail: the underline
 * beneath MYOVOX is a muscle-signal trace. It breathes on its own, ripples
 * when the pointer moves across it, and calms when left alone.
 *
 * Reduced motion gets the same lockup with the trace drawn once, frozen.
 */

const STORY_PATH = '/story'

/**
 * A travelling activation on the trace. Every burst swells in over `attack`
 * seconds and decays away after — nothing ever pops into existence, which is
 * what keeps the line perfectly smooth in time as well as in space.
 */
interface Burst {
  center: number // 0..1 along the line
  amp: number // the peak it swells toward
  width: number
  drift: number
  phase: number
  attack: number // seconds to reach full strength
  decay: number // fade rate once past the attack
  age: number
}

function ambientBurst(): Burst {
  return {
    center: 0.12 + Math.random() * 0.76,
    amp: 0.3 + Math.random() * 0.35,
    width: 0.05 + Math.random() * 0.05,
    drift: (Math.random() - 0.5) * 0.04,
    phase: Math.random() * Math.PI * 2,
    attack: 0.6 + Math.random() * 0.5,
    decay: 0.5 + Math.random() * 0.35,
    age: 0,
  }
}

/** Attack-then-decay strength, C1-smooth at every point in a burst's life. */
function burstStrength(b: Burst): number {
  const a = clamp01(b.age / b.attack)
  const swell = a * a * (3 - 2 * a)
  const fade = Math.exp(-b.decay * Math.max(0, b.age - b.attack))
  return b.amp * swell * fade
}

/** The pointer's presence on the line: one follower, smoothed, never respawned. */
interface Follower {
  center: number
  amp: number
  targetCenter: number
  targetAmp: number
}

/** Signal height at x (0..1): burst envelopes over a faint resting hum. */
function signalAt(x: number, t: number, bursts: Burst[], follower: Follower | null): number {
  let y = 0.03 * Math.sin(x * 14 + t * 1.1) + 0.02 * Math.sin(x * 31 - t * 0.7)
  for (const b of bursts) {
    const envelope = burstStrength(b) * Math.exp(-(((x - b.center) / b.width) ** 2))
    y += envelope * Math.sin(x * 90 + t * 6 + b.phase)
  }
  if (follower && follower.amp > 0.004) {
    const envelope = follower.amp * Math.exp(-(((x - follower.center) / 0.06) ** 2))
    y += envelope * Math.sin(x * 70 + t * 7)
  }
  // Soft limiter: overlapping bursts compress gracefully instead of clipping
  // against the canvas edge.
  return Math.tanh(y)
}

function drawTrace(
  canvas: HTMLCanvasElement,
  t: number,
  bursts: Burst[],
  follower: Follower | null,
  entrance: number,
): void {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const { width, height } = canvas
  const midY = height / 2
  const ampScale = (height / 2) * 0.82 * entrance

  ctx.clearRect(0, 0, width, height)
  ctx.beginPath()
  const step = Math.max(1.25, width / 900)
  for (let px = 0; px <= width; px += step) {
    const x = px / width
    // The trace fades in from the center outward on entrance.
    const reveal = clamp01(entrance * 2.2 - Math.abs(x - 0.5) * 2)
    const y = midY - signalAt(x, t, bursts, follower) * ampScale * reveal
    if (px === 0) ctx.moveTo(px, y)
    else ctx.lineTo(px, y)
  }
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  ctx.strokeStyle = 'rgba(245, 244, 241, 0.92)'
  ctx.lineWidth = 1.3 * dpr
  ctx.lineJoin = 'round'
  ctx.lineCap = 'round'
  ctx.shadowColor = 'rgba(245, 244, 241, 0.6)'
  ctx.shadowBlur = 7 * dpr
  ctx.stroke()
}

export function HomePage() {
  const navigate = useNavigate()
  const reducedMotion = useStore((s) => s.reducedMotion)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const fit = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      const rect = canvas.getBoundingClientRect()
      canvas.width = Math.max(1, Math.round(rect.width * dpr))
      canvas.height = Math.max(1, Math.round(rect.height * dpr))
    }
    fit()

    // Reduced motion: one calm, frozen breath of signal.
    if (reducedMotion) {
      const frozen = [ambientBurst(), ambientBurst()]
      for (const b of frozen) b.age = b.attack // fully swollen, not yet fading
      drawTrace(canvas, 1.6, frozen, null, 1)
      return
    }

    const bursts: Burst[] = [ambientBurst()]
    const follower: Follower = { center: 0.5, amp: 0, targetCenter: 0.5, targetAmp: 0 }
    let time = 0
    let entrance = 0
    let nextAmbient = 1.6
    const pointer = { lastX: 0, lastT: 0 }

    const onResize = () => fit()
    const onPointer = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect()
      const x = (e.clientX - rect.left) / Math.max(1, rect.width)
      const now = performance.now()
      const speed = Math.abs(e.clientX - pointer.lastX) / Math.max(16, now - pointer.lastT)
      pointer.lastX = e.clientX
      pointer.lastT = now
      if (x < -0.1 || x > 1.1) return
      // The reader's motion feeds one smoothed follower — energy rises with
      // speed, capped so the line never gets frantic.
      follower.targetCenter = clamp01(x)
      follower.targetAmp = Math.min(0.45, follower.targetAmp + speed * 0.12)
    }

    const tick = (_t: number, deltaMs: number) => {
      const dt = Math.min(deltaMs / 1000, 0.05)
      time += dt
      entrance = clamp01(entrance + dt / 1.4)

      nextAmbient -= dt
      if (nextAmbient <= 0) {
        bursts.push(ambientBurst())
        nextAmbient = 2.2 + Math.random() * 2.4
        if (bursts.length > 8) bursts.shift()
      }
      for (let i = bursts.length - 1; i >= 0; i--) {
        const b = bursts[i]
        b.age += dt
        b.center += b.drift * dt
        if (b.age > b.attack && burstStrength(b) < 0.008) bursts.splice(i, 1)
      }

      // The follower glides toward the pointer; its energy bleeds away.
      follower.center += (follower.targetCenter - follower.center) * Math.min(1, dt * 7)
      follower.amp += (follower.targetAmp - follower.amp) * Math.min(1, dt * 5)
      follower.targetAmp *= Math.exp(-2.2 * dt)

      drawTrace(canvas, time, bursts, follower, entrance)
    }

    window.addEventListener('resize', onResize)
    window.addEventListener('pointermove', onPointer, { passive: true })
    gsap.ticker.add(tick)
    return () => {
      gsap.ticker.remove(tick)
      window.removeEventListener('resize', onResize)
      window.removeEventListener('pointermove', onPointer)
    }
  }, [reducedMotion])

  return (
    <div className={styles.hero}>
      <h1 className={`${styles.lockup} ${styles.rise}`}>
        <span className={styles.mark}>
          <LogoMark size={40} duration={9} />
        </span>
        <span className={`${styles.wordmark} display glow`}>MYOVOX</span>
      </h1>

      <div className={`${styles.traceWrap} ${styles.rise}`} aria-hidden="true">
        <canvas ref={canvasRef} className={styles.trace} />
      </div>

      <p className={`${styles.tagline} ${styles.rise} label`}>Reading Speech From Facial Muscles</p>

      <p className={`${styles.abstract} ${styles.rise}`}>
        Say a sentence in perfect silence, and it still comes back as text. Thirty-one
        sensors read the electricity of your facial muscles, no microphone anywhere, and
        decode open, unscripted vocabulary at <em>18.5% word error</em>, down from a
        published baseline of 51%.
      </p>

      <button
        type="button"
        className={`${styles.cta} ${styles.rise}`}
        onClick={() => navigate(STORY_PATH)}
      >
        Learn How It Works <span aria-hidden="true">→</span>
      </button>
    </div>
  )
}
