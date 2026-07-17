// scrubEngine.ts — image-sequence scrubber. Replaces the <video> seek + drawImage(video)
// path. Draws pre-decoded frames onto the existing shared canvas. A tiny always-loaded
// strip (L0) guarantees a frame is always drawable, so the "rendering…" loader cannot stick.
//
// Frames exist in a YouTube-style quality ladder (240p…1080p, one directory per
// tier). The engine fetches from whichever tier `setTier` selects; on a switch the
// old tier's decoded frames are kept as a stale fallback so the picture never
// drops to the strip while the new tier streams in.

/** The quality ladder, best first. Labels are the height names the UI shows (…p). */
export const TIERS = ['1080', '720', '540', '360', '240'] as const
export type Tier = (typeof TIERS)[number]

/** Tier widths (px) — mirrors encode-scrub.sh; the manifest carries the real values. */
export const TIER_WIDTHS: Record<Tier, number> = {
  '1080': 1920,
  '720': 1280,
  '540': 960,
  '360': 640,
  '240': 426,
}

export type Fit = 'contain' | 'cover';

export interface StripMeta { n: number; cols: number; rows: number; cw: number; ch: number; }
export interface ClipMeta {
  frames: number;
  fps: number;
  tiers: Record<string, number>;
  strip: StripMeta;
}
export type ChapterManifest = Record<string, ClipMeta>;

/** One successful frame fetch: how many bytes, how long it took. */
export type FetchSample = (bytes: number, ms: number) => void;

export interface ScrubConfig {
  assetBase: string;        // e.g. `${import.meta.env.BASE_URL}anim`
  chapter: string;          // 'under-the-hood' | 'one-breath'
  manifest: ChapterManifest;
  /** Cache-bust suffix (?v=…) — the media SW prunes unversioned /anim/ URLs per load. */
  version?: string;
  preloadDistance?: number; // clips from active to start fetching (default 2)
  releaseDistance?: number; // clips from active to free memory       (default 3)
  frameWindow?: number;     // decoded L1 frames kept around active index (memory bound; default 16)
  leadAhead?: number;       // frames prefetched in scroll direction (default 6)
  /** Reports each successful frame fetch — feeds the network quality meter. */
  onSample?: FetchSample;
}

interface ClipState {
  id: string;
  meta: ClipMeta;
  strip?: ImageBitmap;
  stripInflight?: boolean;
  /** The strip came back as an HTTP error — permanent for this build, never re-asked. */
  stripFailed?: boolean;
  frames: Map<number, ImageBitmap>;
  /** Previous-tier frames kept as fallback across a tier switch. */
  stale: Map<number, ImageBitmap>;
  /** Frame indices that came back as HTTP errors — never re-requested (the draw
   *  loop would otherwise refetch a missing frame every RAF). */
  failed: Set<number>;
  inflight: Set<number>;
  lastIndex: number;
  active: boolean;
  abort: AbortController;
}

const clamp = (v: number, lo: number, hi: number) => (v < lo ? lo : v > hi ? hi : v);

const versioned = (url: string, version?: string) => (version ? `${url}?v=${version}` : url);

export async function loadChapterManifest(
  assetBase: string,
  chapter: string,
  version?: string,
): Promise<ChapterManifest> {
  const res = await fetch(versioned(`${assetBase}/${chapter}/scrub.manifest.json`, version));
  if (!res.ok) throw new Error(`scrub.manifest.json ${res.status} for ${chapter}`);
  return res.json();
}

export class ScrubEngine {
  private cfg!: Required<Omit<ScrubConfig, 'version' | 'onSample'>> &
    Pick<ScrubConfig, 'version' | 'onSample'>;
  private clips = new Map<string, ClipState>();
  private tier: Tier = '540';
  private cap: Tier = '1080';

  configure(cfg: ScrubConfig) {
    this.cfg = {
      preloadDistance: 2,
      releaseDistance: 3,
      frameWindow: 16,
      leadAhead: 6,
      ...cfg,
    };
  }

  /** Highest tier worth fetching for this display (no point exceeding device px). */
  setViewport(cssWidth: number, dpr: number) {
    const devicePx = cssWidth * dpr;
    let cap: Tier = TIERS[0];
    for (const t of TIERS) {
      if (TIER_WIDTHS[t] >= devicePx) cap = t; // TIERS is best-first; keep tightening
    }
    this.cap = cap;
  }

  viewportCap(): Tier {
    return this.cap;
  }

  currentTier(): Tier {
    return this.tier;
  }

  /**
   * Switch quality. Decoded frames of the old tier become the stale fallback
   * (still drawable, replaced index-by-index as the new tier decodes), so a
   * switch never flashes down to the strip.
   */
  setTier(t: Tier) {
    if (t === this.tier) return;
    this.tier = t;
    for (const cs of this.clips.values()) {
      for (const [i, bmp] of cs.frames) {
        cs.stale.get(i)?.close();
        cs.stale.set(i, bmp);
      }
      cs.frames.clear();
      cs.inflight.clear();
      cs.failed.clear(); // failures are per-tier URLs — the new tier gets a clean slate
    }
  }

  setWindow(activeIndex: number, orderedIds: string[]) {
    for (let idx = 0; idx < orderedIds.length; idx++) {
      const id = orderedIds[idx];
      const dist = Math.abs(idx - activeIndex);
      if (dist <= this.cfg.preloadDistance) {
        const cs = this.ensure(id);
        if (cs) {
          cs.active = idx === activeIndex;
          this.loadStrip(cs);
          if (cs.active) this.warmAround(cs, cs.lastIndex);
        }
      } else if (dist > this.cfg.releaseDistance) {
        this.release(id);
      }
    }
  }

  drawFrame(
    ctx: CanvasRenderingContext2D,
    id: string,
    local: number,
    dstW: number,
    dstH: number,
    fit: Fit = 'contain',
    alignTop = false,
  ): { drawn: boolean; crisp: boolean } {
    const cs = this.clips.get(id) ?? this.ensure(id);
    if (!cs) return { drawn: false, crisp: false };

    const n = cs.meta.frames;
    const pos = clamp(local, 0, 1) * (n - 1);
    const i = clamp(Math.round(pos), 0, n - 1);
    const dir = Math.sign(i - cs.lastIndex) || 1;
    cs.lastIndex = i;

    if (cs.active) {
      this.loadFrame(cs, i);
      for (let k = 1; k <= this.cfg.leadAhead; k++) this.loadFrame(cs, clamp(i + dir * k, 0, n - 1));
      this.loadFrame(cs, clamp(i - dir, 0, n - 1));
    }

    // Cross-dissolve the two frames bracketing the scroll position, so the 12fps
    // frame sampling reads as continuous motion instead of visible 12fps steps.
    const i0 = clamp(Math.floor(pos), 0, n - 1);
    const i1 = clamp(i0 + 1, 0, n - 1);
    const a = cs.frames.get(i0) ?? cs.stale.get(i0) ?? null;
    const b = i1 !== i0 ? (cs.frames.get(i1) ?? cs.stale.get(i1) ?? null) : null;
    const base = a ?? b;
    if (base) {
      // Quantized so a parked scroll position yields a stable key — an unchanged
      // frame is never re-blitted, so an idle page does zero canvas work.
      const alpha = a && b ? Math.round((pos - i0) * 32) / 32 : 0;
      const over = a && b ? b : null;
      if (this.sameDraw(id, base, over, alpha, dstW, dstH, fit, alignTop))
        return { drawn: true, crisp: true };
      ctx.clearRect(0, 0, dstW, dstH);
      this.blit(ctx, base, 0, 0, base.width, base.height, dstW, dstH, fit, alignTop);
      if (over && alpha > 0) {
        ctx.globalAlpha = alpha;
        this.blit(ctx, over, 0, 0, over.width, over.height, dstW, dstH, fit, alignTop);
        ctx.globalAlpha = 1;
      }
      return { drawn: true, crisp: true };
    }

    if (cs.strip) {
      const { cols, rows, n: sn } = cs.meta.strip;
      const si = clamp(Math.round(local * (sn - 1)), 0, sn - 1);
      if (this.sameDraw(id, cs.strip, null, si, dstW, dstH, fit, alignTop))
        return { drawn: true, crisp: false };
      const cw = cs.strip.width / cols;
      const chh = cs.strip.height / rows;
      const sx = (si % cols) * cw;
      const sy = Math.floor(si / cols) * chh;
      ctx.clearRect(0, 0, dstW, dstH);
      this.blit(ctx, cs.strip, sx, sy, cw, chh, dstW, dstH, fit, alignTop);
      return { drawn: true, crisp: false };
    }

    return { drawn: false, crisp: false };
  }

  /** The last blit's identity — bitmaps compared by reference, so a newly decoded
   *  (sharper) frame for the same index changes the key and forces a redraw. */
  private lastDraw: {
    id: string; a: ImageBitmap; b: ImageBitmap | null; alpha: number;
    w: number; h: number; fit: Fit; top: boolean;
  } | null = null;

  private sameDraw(
    id: string, a: ImageBitmap, b: ImageBitmap | null, alpha: number,
    w: number, h: number, fit: Fit, top: boolean,
  ): boolean {
    const d = this.lastDraw;
    const same = !!d && d.id === id && d.a === a && d.b === b && d.alpha === alpha &&
      d.w === w && d.h === h && d.fit === fit && d.top === top;
    if (!same) this.lastDraw = { id, a, b, alpha, w, h, fit, top };
    return same;
  }

  prefetchAllStrips(ids: string[]) {
    for (const id of ids) {
      const cs = this.ensure(id);
      if (cs) this.loadStrip(cs);
    }
  }

  release(id: string) {
    const cs = this.clips.get(id);
    if (!cs) return;
    cs.abort.abort();
    cs.strip?.close();
    for (const b of cs.frames.values()) b.close();
    for (const b of cs.stale.values()) b.close();
    this.clips.delete(id);
  }

  destroy() {
    for (const id of [...this.clips.keys()]) this.release(id);
  }

  private ensure(id: string): ClipState | null {
    const existing = this.clips.get(id);
    if (existing) return existing;
    const meta = this.cfg.manifest[id];
    if (!meta) return null;
    const cs: ClipState = {
      id, meta,
      frames: new Map(), stale: new Map(), failed: new Set(), inflight: new Set(),
      lastIndex: 0, active: false, abort: new AbortController(),
    };
    this.clips.set(id, cs);
    return cs;
  }

  private warmAround(cs: ClipState, center: number) {
    const n = cs.meta.frames;
    for (let k = 0; k <= this.cfg.leadAhead; k++) {
      this.loadFrame(cs, clamp(center + k, 0, n - 1));
      if (k) this.loadFrame(cs, clamp(center - k, 0, n - 1));
    }
  }

  private async loadStrip(cs: ClipState) {
    if (cs.strip || cs.stripInflight || cs.stripFailed) return;
    cs.stripInflight = true;
    try {
      const url = `${this.cfg.assetBase}/${this.cfg.chapter}/scrub/${cs.id}/strip.webp`;
      const res = await fetch(versioned(url, this.cfg.version), { signal: cs.abort.signal });
      if (!res.ok) { cs.stripFailed = true; return; } // missing render — don't re-ask every stage change
      const bmp = await createImageBitmap(await res.blob());
      if (cs.abort.signal.aborted) { bmp.close(); return; }
      cs.strip = bmp;
    } catch { /* transient network error — retried on the next window move */ }
    finally { cs.stripInflight = false; }
  }

  private async loadFrame(cs: ClipState, i: number) {
    if (cs.frames.has(i) || cs.inflight.has(i) || cs.failed.has(i)) return;
    cs.inflight.add(i);
    const tier = this.tier; // captured: a switch mid-flight lands in stale-safe territory
    try {
      const name = String(i + 1).padStart(4, '0'); // ffmpeg %04d is 1-based
      const url = `${this.cfg.assetBase}/${this.cfg.chapter}/scrub/${cs.id}/${tier}/${name}.webp`;
      const t0 = performance.now();
      const res = await fetch(versioned(url, this.cfg.version), { signal: cs.abort.signal });
      if (!res.ok) { cs.failed.add(i); return; } // missing frame — stale/strip covers it
      const blob = await res.blob();
      this.cfg.onSample?.(blob.size, Math.max(1, performance.now() - t0));
      const bmp = await createImageBitmap(blob);
      if (cs.abort.signal.aborted || tier !== this.tier) { bmp.close(); return; }
      cs.frames.set(i, bmp);
      cs.stale.get(i)?.close();
      cs.stale.delete(i);
      this.evict(cs);
    } catch { /* transient network error — leave to stale/strip, retried on a later draw */ }
    finally { cs.inflight.delete(i); }
  }

  private evict(cs: ClipState) {
    const w = this.cfg.frameWindow;
    const lo = cs.lastIndex - Math.floor(w / 2);
    const hi = cs.lastIndex + Math.ceil(w / 2);
    if (cs.frames.size > w) {
      for (const [idx, bmp] of cs.frames) {
        if (idx < lo || idx > hi) { bmp.close(); cs.frames.delete(idx); }
      }
    }
    for (const [idx, bmp] of cs.stale) {
      if (idx < lo || idx > hi) { bmp.close(); cs.stale.delete(idx); }
    }
  }

  private blit(
    ctx: CanvasRenderingContext2D, bmp: ImageBitmap,
    sx: number, sy: number, sw: number, sh: number,
    dw: number, dh: number, fit: Fit, alignTop: boolean,
  ) {
    const scale = fit === 'cover' ? Math.max(dw / sw, dh / sh) : Math.min(dw / sw, dh / sh);
    const w = sw * scale, h = sh * scale;
    const dx = (dw - w) / 2;
    // Mobile CSS anchors a contained clip to the top of its band; mirror it here.
    const dy = fit !== 'cover' && alignTop ? 0 : (dh - h) / 2;
    ctx.drawImage(bmp, sx, sy, sw, sh, dx, dy, w, h);
  }
}
