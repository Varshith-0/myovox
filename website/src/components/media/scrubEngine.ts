// scrubEngine.ts — image-sequence scrubber. Replaces the <video> seek + drawImage(video)
// path. Draws pre-decoded frames onto the existing shared canvas. A tiny always-loaded
// strip (L0) guarantees a frame is always drawable, so the "rendering…" loader cannot stick.

export type Tier = 'hi' | 'lo';
export type Fit = 'contain' | 'cover';

export interface StripMeta { n: number; cols: number; rows: number; cw: number; ch: number; }
export interface ClipMeta {
  frames: number;
  fps: number;
  tiers: { hi: number; lo: number };
  strip: StripMeta;
}
export type ChapterManifest = Record<string, ClipMeta>;

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
  hiThresholdDevicePx?: number; // display width (device px) above which hi tier is used (default 640)
}

interface ClipState {
  id: string;
  meta: ClipMeta;
  tier: Tier;
  strip?: ImageBitmap;
  stripInflight?: boolean;
  frames: Map<number, ImageBitmap>;
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
  private cfg!: Required<Omit<ScrubConfig, 'version'>> & Pick<ScrubConfig, 'version'>;
  private clips = new Map<string, ClipState>();
  private tier: Tier = 'hi';

  configure(cfg: ScrubConfig) {
    this.cfg = {
      preloadDistance: 2,
      releaseDistance: 3,
      frameWindow: 16,
      leadAhead: 6,
      hiThresholdDevicePx: 640,
      ...cfg,
    };
  }

  setViewport(cssWidth: number, dpr: number) {
    const devicePx = cssWidth * dpr;
    this.tier = devicePx > this.cfg.hiThresholdDevicePx ? 'hi' : 'lo';
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
    const i = clamp(Math.round(local * (n - 1)), 0, n - 1);
    const dir = Math.sign(i - cs.lastIndex) || 1;
    cs.lastIndex = i;

    if (cs.active) {
      this.loadFrame(cs, i);
      for (let k = 1; k <= this.cfg.leadAhead; k++) this.loadFrame(cs, clamp(i + dir * k, 0, n - 1));
      this.loadFrame(cs, clamp(i - dir, 0, n - 1));
    }

    const l1 = cs.frames.get(i);
    if (l1) {
      ctx.clearRect(0, 0, dstW, dstH);
      this.blit(ctx, l1, 0, 0, l1.width, l1.height, dstW, dstH, fit, alignTop);
      return { drawn: true, crisp: true };
    }

    if (cs.strip) {
      const { cols, rows, n: sn } = cs.meta.strip;
      const si = clamp(Math.round(local * (sn - 1)), 0, sn - 1);
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
      id, meta, tier: this.tier,
      frames: new Map(), inflight: new Set(),
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
    if (cs.strip || cs.stripInflight) return;
    cs.stripInflight = true;
    try {
      const url = `${this.cfg.assetBase}/${this.cfg.chapter}/scrub/${cs.id}/strip.webp`;
      const res = await fetch(versioned(url, this.cfg.version), { signal: cs.abort.signal });
      if (!res.ok) return;
      const bmp = await createImageBitmap(await res.blob());
      if (cs.abort.signal.aborted) { bmp.close(); return; }
      cs.strip = bmp;
    } catch { /* leave it; loader is time-bounded */ }
    finally { cs.stripInflight = false; }
  }

  private async loadFrame(cs: ClipState, i: number) {
    if (cs.frames.has(i) || cs.inflight.has(i)) return;
    cs.inflight.add(i);
    try {
      const name = String(i + 1).padStart(4, '0'); // ffmpeg %04d is 1-based
      const url = `${this.cfg.assetBase}/${this.cfg.chapter}/scrub/${cs.id}/${cs.tier}/${name}.webp`;
      const res = await fetch(versioned(url, this.cfg.version), { signal: cs.abort.signal });
      if (!res.ok) throw new Error(String(res.status));
      const bmp = await createImageBitmap(await res.blob());
      if (cs.abort.signal.aborted) { bmp.close(); return; }
      cs.frames.set(i, bmp);
      this.evict(cs);
    } catch { /* leave to L0 */ }
    finally { cs.inflight.delete(i); }
  }

  private evict(cs: ClipState) {
    const w = this.cfg.frameWindow;
    if (cs.frames.size <= w) return;
    const lo = cs.lastIndex - Math.floor(w / 2);
    const hi = cs.lastIndex + Math.ceil(w / 2);
    for (const [idx, bmp] of cs.frames) {
      if (idx < lo || idx > hi) { bmp.close(); cs.frames.delete(idx); }
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
