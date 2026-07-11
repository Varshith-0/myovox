// quality.ts — YouTube-style adaptive quality for the scrub frames.
//
// The scrubber is constantly fetching frames, so the connection measures itself:
// every successful fetch feeds an EWMA of throughput and of per-frame bytes.
// Auto picks the highest tier the measured throughput can sustain at scrub fps,
// capped at what the viewport can display. A user pick pins the tier absolutely
// (slow networks just show the loader more — their call); tapping the pinned
// quality again returns to auto.

import { useStore } from '@/store/useStore'
import { TIERS, TIER_WIDTHS, type Tier, type ScrubEngine } from './scrubEngine'

/** How the loader should explain a stall: the pipe, or simply outrunning it. */
export type LoadReason = 'network' | 'preparing'

const SCRUB_FPS = 12
/** Throughput must exceed need by this much to hold a tier. */
const SAFETY = 1.4
/** …and the next tier up by this much before promoting (hysteresis). */
const PROMOTE_HEADROOM = 1.9
/** Minimum ms between automatic switches, so it never oscillates. */
const SWITCH_COOLDOWN_MS = 4000

/**
 * Rough per-frame bytes per tier before any measurement lands (from the
 * encode dry-run medians). Refined live by scaling the measured frame size.
 */
const PRIOR_FRAME_BYTES: Record<Tier, number> = {
  '1080': 15_000,
  '720': 9_000,
  '540': 6_500,
  '360': 4_000,
  '240': 2_400,
}

/** Hot-path meter (module-level, like store/scroll): no React churn. */
export const netMeter = {
  /** Smoothed throughput, bytes per ms (≈ kB/s). 0 = no sample yet. */
  bps: 0,
  /** Smoothed observed frame size at `measuredTier`. */
  frameBytes: 0,
  measuredTier: '540' as Tier,

  sample(bytes: number, ms: number, tier: Tier) {
    const inst = bytes / ms
    this.bps = this.bps ? this.bps * 0.8 + inst * 0.2 : inst
    if (tier === this.measuredTier && this.frameBytes) {
      this.frameBytes = this.frameBytes * 0.8 + bytes * 0.2
    } else {
      this.frameBytes = bytes
      this.measuredTier = tier
    }
  },

  /** Expected frame bytes at `tier`, scaled from what we've actually seen. */
  frameBytesAt(tier: Tier): number {
    if (!this.frameBytes) return PRIOR_FRAME_BYTES[tier]
    const ratio = TIER_WIDTHS[tier] / TIER_WIDTHS[this.measuredTier]
    return this.frameBytes * ratio ** 1.6
  },

  /** Bytes/ms needed to stream `tier` at scrub speed, with safety margin. */
  needFor(tier: Tier): number {
    return (this.frameBytesAt(tier) * SCRUB_FPS * SAFETY) / 1000
  },

  /** Is a stall better explained by the pipe than by a fast scroll? */
  networkBound(tier: Tier): boolean {
    return this.bps > 0 && this.bps < this.needFor(tier)
  },
}

/** First guess before any fetch lands: the Network Information API if present. */
function initialTier(cap: Tier): Tier {
  const conn = (navigator as { connection?: { downlink?: number } }).connection
  const downlinkBpms = conn?.downlink ? (conn.downlink * 125_000) / 1000 : 0
  if (!downlinkBpms) {
    // ponytail: no signal → start one below the cap and let measurement promote.
    const i = TIERS.indexOf(cap)
    return TIERS[Math.min(i + 1, TIERS.length - 1)]
  }
  for (const t of TIERS.slice(TIERS.indexOf(cap))) {
    if (downlinkBpms >= netMeter.needFor(t)) return t
  }
  return TIERS[TIERS.length - 1]
}

/**
 * Owns the engine's tier. Auto mode follows the meter; a pinned quality (store)
 * always wins. Call `sample` from the engine's onSample; `dispose` on unmount.
 */
export class QualityController {
  private engine: ScrubEngine
  private lastSwitch = 0
  private unsubscribe: () => void

  constructor(engine: ScrubEngine) {
    this.engine = engine
    const cap = engine.viewportCap()
    const auto = initialTier(cap)
    useStore.getState().setAutoQuality(auto)
    this.apply(useStore.getState().qualityPinned ?? auto)

    // React to pin/unpin from the menu immediately.
    this.unsubscribe = useStore.subscribe((s, prev) => {
      if (s.qualityPinned !== prev.qualityPinned) {
        this.lastSwitch = performance.now()
        this.apply(s.qualityPinned ?? s.autoQuality)
      }
    })
  }

  sample(bytes: number, ms: number) {
    netMeter.sample(bytes, ms, this.engine.currentTier())
    const now = performance.now()
    if (now - this.lastSwitch < SWITCH_COOLDOWN_MS) return
    const next = this.autoTier()
    // Auto's pick is tracked even while pinned — the menu's Auto row shows it.
    useStore.getState().setAutoQuality(next)
    if (useStore.getState().qualityPinned) return
    if (next !== this.engine.currentTier()) {
      this.lastSwitch = now
      this.apply(next)
    }
  }

  /** A confirmed stall (loader showing): demote one step right away in auto. */
  onStall() {
    if (useStore.getState().qualityPinned) return
    const cur = this.engine.currentTier()
    const i = TIERS.indexOf(cur)
    if (i < TIERS.length - 1 && netMeter.networkBound(cur)) {
      this.lastSwitch = performance.now()
      this.apply(TIERS[i + 1])
    }
  }

  dispose() {
    this.unsubscribe()
  }

  /** Highest sustainable tier ≤ viewport cap; promotion needs extra headroom. */
  private autoTier(): Tier {
    const cap = this.engine.viewportCap()
    const cur = this.engine.currentTier()
    if (!netMeter.bps) return cur
    const candidates = TIERS.slice(TIERS.indexOf(cap)) // best-first from the cap down
    for (const t of candidates) {
      const isPromotion = TIERS.indexOf(t) < TIERS.indexOf(cur)
      const need = netMeter.needFor(t) * (isPromotion ? PROMOTE_HEADROOM / SAFETY : 1)
      if (netMeter.bps >= need) return t
    }
    return TIERS[TIERS.length - 1]
  }

  private apply(t: Tier) {
    this.engine.setTier(t)
    useStore.getState().setActiveQuality(t)
  }
}
