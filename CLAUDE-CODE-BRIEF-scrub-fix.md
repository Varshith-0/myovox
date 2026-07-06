# TASK FOR CLAUDE CODE — fix Myovox scroll-scrubbing (mobile stutter + infinite "rendering…")

You are editing the Myovox website (`website/`, React 19 + TS + Vite, GitHub Pages).

## Why
The story pages scrub animation by seeking an off-DOM `<video>` (`video.currentTime = t`,
then `drawImage(video)` onto a shared canvas) on every scroll frame. Video *seeking* is
unreliable on phones (stuck `seeked` events, iOS decoder caps, preload refusals), which
causes mid-scroll stutter and a "rendering…" overlay that never dismisses.

The fix: **stop seeking video. Scrub by drawing pre-decoded image frames** (Apple-style
image-sequence scrubbing). A tiny always-loaded "strip" guarantees a frame is always
drawable, so the loader can never get stuck.

## Current state — ALREADY DONE (verify, don't redo)
Frame assets have been generated and committed under `website/public/`:
```
public/anim/<chapter>/scrub.manifest.json          # { "<id>": {frames, fps, tiers:{hi,lo}, strip:{n,cols,rows,cw,ch}} }
public/anim/<chapter>/scrub/<id>/hi/0001.webp …    # crisp scrub frames, retina tier
public/anim/<chapter>/scrub/<id>/lo/0001.webp …    # crisp scrub frames, phone tier
public/anim/<chapter>/scrub/<id>/strip.webp         # ONE 12-frame sheet (the fallback baseline)
```
for both chapters: `under-the-hood` (50 clips) and `one-breath` (10 clips).
Verify with `ls website/public/anim/under-the-hood/scrub | head` and
`cat website/public/anim/one-breath/scrub.manifest.json`. If any are missing, regenerate
with `bash website/anim/encode-scrub.sh` (idempotent) — but they should already exist.

Do NOT delete the existing MP4s or posters. Posters stay as the reduced-motion image and
final fallback. MP4s can stay for a future Play mode (played linearly, never seeked).

---

## STEP 1 — Add the scrub engine
Create `website/src/components/media/scrubEngine.ts` with exactly this content:

```ts
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

export async function loadChapterManifest(assetBase: string, chapter: string): Promise<ChapterManifest> {
  const res = await fetch(`${assetBase}/${chapter}/scrub.manifest.json`);
  if (!res.ok) throw new Error(`scrub.manifest.json ${res.status} for ${chapter}`);
  return res.json();
}

export class ScrubEngine {
  private cfg!: Required<ScrubConfig>;
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
      this.blit(ctx, l1, 0, 0, l1.width, l1.height, dstW, dstH, fit);
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
      this.blit(ctx, cs.strip, sx, sy, cw, chh, dstW, dstH, fit);
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
      const res = await fetch(url, { signal: cs.abort.signal });
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
      const res = await fetch(url, { signal: cs.abort.signal });
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
    dw: number, dh: number, fit: Fit,
  ) {
    const scale = fit === 'cover' ? Math.max(dw / sw, dh / sh) : Math.min(dw / sw, dh / sh);
    const w = sw * scale, h = sh * scale;
    const dx = (dw - w) / 2, dy = (dh - h) / 2;
    ctx.drawImage(bmp, sx, sy, sw, sh, dx, dy, w, h);
  }
}
```

---

## STEP 2 — Wire the engine into the runtime
Read these existing files first to learn their exact shapes:
`src/components/media/MediaLayer.tsx`, `useMediaScrubber.ts`, `mediaLifecycle.ts`,
`core.ts`, `MediaLoader.tsx`, and `src/data/stages.ts` / `oneBreathStages.ts`.

Then make these edits:

**(a) Instantiate + configure once per story** (in `MediaLayer.tsx`, or wherever the
story mounts and already knows the chapter + ordered stage list). Pseudo-outline:
```ts
import { ScrubEngine, loadChapterManifest } from './scrubEngine';

const engineRef = useRef<ScrubEngine | null>(null);
useEffect(() => {
  let alive = true;
  (async () => {
    const assetBase = `${import.meta.env.BASE_URL}anim`;
    const manifest = await loadChapterManifest(assetBase, chapter); // 'under-the-hood' | 'one-breath'
    if (!alive) return;
    const engine = new ScrubEngine();
    engine.configure({
      assetBase, chapter, manifest,
      preloadDistance: MEDIA_CONFIG.preloadDistance, // reuse existing knobs from core.ts
      releaseDistance: MEDIA_CONFIG.releaseDistance,
    });
    const canvasCssWidth = /* the media canvas CSS width, e.g. window.innerWidth */;
    engine.setViewport(canvasCssWidth, Math.min(window.devicePixelRatio, MEDIA_CONFIG.dprCap));
    engine.prefetchAllStrips(orderedStageIds); // all strips are ~3–4 MB total; whole story instantly scrubbable
    engineRef.current = engine;
  })();
  return () => { alive = false; engineRef.current?.destroy(); engineRef.current = null; };
}, [chapter]);
```
Recompute `engine.setViewport(...)` on resize (there is already a resize path in
`useResponsive.ts` / `MediaLayer`).

**(b) Cold path — on active stage change.** Wherever `stageIndex` in the Zustand store is
read/subscribed, call:
```ts
engineRef.current?.setWindow(activeIndex, orderedStageIds);
```
`orderedStageIds` = the stage ids in story order (from the stage list used to render sections).

**(c) Hot path — in `useMediaScrubber.ts`, inside `runClipStageFrame`.** Replace the
`scrubVideo(video, local)` + `drawFrame(...)` calls with a single engine draw. Keep the
existing `local = localProgressFor(section)` computation and the existing opacity/envelope
math (presence × HOLD→REVEAL × frameReveal). The canvas backing-store size is `bw`/`bh`
(width/height in device px — use whatever the code already uses for the canvas dimensions):
```ts
const { drawn, crisp } = engineRef.current!.drawFrame(
  ctx, stage.id, local, bw, bh, stage.media.fit ?? 'contain',
);
// frameReveal should latch upward on `drawn` (L0 is NOT black, so content appears immediately).
// `crisp` is available if you want to distinguish "showing HD frame" from "showing baseline".
```
`runReducedStageFrame` (reduced-motion path) is unchanged — it still shows the poster only.

---

## STEP 3 — Delete the old video-seek path
In `mediaLifecycle.ts` (and any callers), remove the video-decoder machinery now that the
engine owns drawing:
- the off-DOM `document.createElement('video')` creation + `preload='auto'` fetch,
- `scrubVideo` (the `video.currentTime = …` seek + `video.seeking` coalescing),
- `drawFrame` that copied from a `<video>`,
- the sliding-window of *video decoders* (create within preloadDistance / release beyond
  releaseDistance) and the 3s failed-load retry.

`MediaLayer.tsx` should no longer create or hold any `<video>` for scrubbing. (If you want to
keep a Play mode later, that's a single `<video>` played linearly — not part of this task.)

---

## STEP 4 — Make the loader impossible to get stuck (`MediaLoader.tsx` + stall block)
Currently the stall counter increments when the newest seek target isn't ready, and after
~12 frames flips `mediaLoading`. Change it to:
- **increment the stall counter only when `!drawn`** (i.e. not even the L0 strip is available).
  With the engine, that's true only for the sub-second before the tiny strip decodes.
- **add a hard timeout**: once `mediaLoading` is true, auto-dismiss after ≤1000ms regardless,
  falling back to whatever is drawable (poster → solid `#050505`). The spinner must be
  strictly time-bounded — there must be no code path that leaves it up indefinitely.

---

## Keep unchanged
Lenis + GSAP single-clock setup, `scroll.progress` hot module var, the Zustand cold state,
the title-card choreography in `mediaDomFx.ts`, posters, captions, narration, and the
reduced-motion path. This task only swaps the drawing primitive.

## Acceptance checks
1. Open a story page and scrub. In DevTools → Elements, **no `<video>` elements are created**
   during scrubbing; in Network you see `.webp` frame requests, not MP4 range requests.
2. In DevTools device mode, throttle to "Slow 4G" + a mobile profile, then jump the scrollbar
   deep into the page: **a frame appears within a second and the "rendering…" overlay never
   persists** (at worst a brief chunky baseline, then it sharpens).
3. Fast scrubbing tracks the scrollbar smoothly with no repeated overlay flashes.
4. Memory stays bounded while scrolling the 50-scene page (only the active clip holds a window
   of decoded frames; neighbors hold just a strip).
5. `prefers-reduced-motion` still shows the static poster per stage.

If any referenced symbol name differs in the actual code, adapt to the real names — the file
and function names above come from the project's own architecture doc but verify against source.
