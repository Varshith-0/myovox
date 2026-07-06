# How the website renders its animations

A file-by-file walkthrough of the Myovox website and its animation pipeline —
from a Python scene file on your laptop to a frame glued to your scroll wheel
in the browser.

---

## Part 1 — The website in one page

The site (in [`website/`](../website/)) is a **React 19 + TypeScript + Vite**
single-page app deployed to GitHub Pages. It has four routes, wired in
[`src/App.tsx`](../website/src/App.tsx):

| Route | Component | What it is |
|---|---|---|
| `/` | `src/routes/ChooserPage.tsx` | Landing page: pick a story |
| `/story/one-breath` | `src/routes/StoryPage.tsx` (`StoryExperience`) | 10-scene short story |
| `/story/under-the-hood` | same component, different stage list | 50-scene deep dive |
| `/technical`, `/code` | `TechnicalPage.tsx`, `CodePage.tsx` | Markdown reading pages (lazy-loaded) |

The core idea of the whole site: **the story pages are a scroll-driven video
scrubber.** There is no live WebGL animation and no JS animation engine drawing
the diagrams. Every animation you see is a **pre-rendered MP4**, rendered ahead
of time with [Manim](https://www.manim.community/) (the math-animation library),
and the browser's only job is: *map scroll position → video timestamp → draw
that frame*.

Key libraries and why each exists:

- **Lenis** — smooth (inertial) scrolling. The raw wheel input is jumpy; Lenis
  lerps it, which is what makes the video scrub feel like silk.
- **GSAP ScrollTrigger** — measures scroll progress through the story container.
  Not used for tweening anything; it's used as a well-tested scroll observer.
- **Zustand** (`src/store/useStore.ts`) — slow-changing UI state: active stage
  index, play/pause, volume, captions on/off, reduced motion.
- **react-markdown + react-syntax-highlighter** — only for the `/technical` and
  `/code` reading pages.

### The one architectural rule

Stated at the top of [`src/data/stages.ts`](../website/src/data/stages.ts):
overlays react to the **active stage index in the store**, never to DOM scroll
events directly. Per-frame consumers read a plain module variable, never React
state. Concretely there are two "speeds" of state:

- **Hot path (60×/s):** `scroll.progress` in
  [`src/store/scroll.ts`](../website/src/store/scroll.ts) — a plain module-level
  number. Writing it every frame costs nothing and never re-renders React.
- **Cold path (a few times/min):** `stageIndex` in the Zustand store — updates
  only when you cross into a new section, which re-renders the caption and
  progress rail.

This split is why the site can scrub video at 60fps without React churn.

---

## Part 2 — The offline pipeline: Python → MP4

Nothing animates "live". Every clip is produced ahead of time by this chain:

```
anim/under-the-hood/NN-name.py   (a Manim Scene class)
        │  ./render.sh <id>          manim -qh → 1080p30 raw render
        ▼
anim/encode.sh                       ffmpeg re-encode for scrubbing
        │
        ├── public/anim/<chapter>/video/1080/<id>.mp4   (retina tier)
        ├── public/anim/<chapter>/video/540/<id>.mp4    (phone tier)
        └── public/anim/<chapter>/posters/<id>.webp     (final frame, fallback)

scripts/narrate.py                   edge-tts (neural TTS)
        │
        ├── public/anim/<chapter>/audio/<id>.mp3        (narration voice)
        └── public/anim/<chapter>/captions/<id>.json    (subtitle cues)
```

### 2.1 Scene files — `website/anim/`

Each animation is one Python file containing one Manim `Scene` class. There are
two chapters: [`anim/under-the-hood/`](../website/anim/under-the-hood/) (50
scenes, `01-hero.py` … `50-end.py`) and [`anim/one-breath/`](../website/anim/one-breath/)
(10 scenes). A scene is ordinary Manim code — build mobjects, `self.play(...)`
transitions, `self.wait(...)` holds. See
[`anim/under-the-hood/01-hero.py`](../website/anim/under-the-hood/01-hero.py)
for a representative one: it draws an audio waveform, flattens it ("sound —
off"), raises 31 EMG traces, collapses them into one, and ends on the title.

Scenes are written in "beats" — one visual beat per narration sentence — so the
video and the spoken script stay in step.

### 2.2 Shared style — `anim/style.py`

[`style.py`](../website/anim/style.py) is imported by every scene
(`from style import *`). It pins:

- **Palette**: strict monochrome on `#050505`, with the exact hex values from
  the site's [`src/styles/tokens.css`](../website/src/styles/tokens.css) — this
  is why the videos blend invisibly into the page background.
- **Fonts**: JetBrains Mono + Fraunces, again matching the site.
- **`config.frame_rate = 30`** — every clip is 30fps; the frontend hardcodes
  the same number (`MEDIA_CONFIG.fps`) for its seek math.
- **`seed()`** — fixed RNG seeds so re-renders are pixel-deterministic
  (important when a re-rendered clip must splice invisibly next to old ones).
- Helpers: `mono()/serif()/num()` text builders (Pango text, never LaTeX),
  `glow()`, `dim()`, a `counter()` for live number readouts.

### 2.3 The render map — `anim/render.manifest.json`

[`render.manifest.json`](../website/anim/render.manifest.json) is the
authoritative list of scenes: `{seq, file, class, id}` per clip. The `id`
(e.g. `ctc`, `wfst`) is the key that names every derived asset **and** matches
the stage id in the frontend's `src/data/stages.ts`. Story order (`seq`)
mirrors the stage order there too.

### 2.4 Rendering — `anim/render.sh`

[`render.sh`](../website/anim/render.sh) loops over the manifest (or one id)
and for each scene runs:

1. `manim -qh <file> <Class>` → a raw 1080p30 MP4 in a scratch media dir
   (`/tmp/emg_media` by default).
2. Hands off to `encode.sh` (below).

It also has an `og` target that renders a single still and flattens it onto the
site background to produce the social-share card `public/og.png`.

### 2.5 Encoding for scrubbing — `anim/encode.sh`

This is the step that makes scroll-scrubbing possible.
[`encode.sh`](../website/anim/encode.sh) re-encodes the raw render with:

```
ffmpeg -an -c:v libx264 -g 12 -keyint_min 12 -sc_threshold 0 -crf 24 -movflags +faststart
```

The important flags:

- **`-g 12 -keyint_min 12 -sc_threshold 0`** — a keyframe every 12 frames
  (~0.4s), no scene-cut detection. When the browser seeks to an arbitrary
  `currentTime`, the decoder must decode from the previous keyframe forward; a
  12-frame GOP caps that at ≤11 frames of work (sub-millisecond on hardware
  decoders), while still letting P-frames compress these B&W clips ~2–3× smaller
  than all-keyframe encoding. This is the trade that makes seeks cheap *and*
  files small.
- **`-an`** — no audio track; narration is a separate MP3.
- **`-movflags +faststart`** — the MP4 index (moov atom) goes at the front of
  the file so the browser can start seeking before the download finishes.

It also extracts the clip's **final frame** as `posters/<id>.webp` — used as
the reduced-motion static image and as a blurred fallback while a video loads.

The 540p phone tier in `video/540/` is produced by
[`encode-videos.sh`](../website/anim/encode-videos.sh).

### 2.6 Narration — `scripts/narrate.py`

[`narrate.py`](../website/scripts/narrate.py) reads the spoken script from
[`src/data/narration.json`](../website/src/data/narration.json) (stage id →
text) and renders one MP3 per stage with **edge-tts** (Microsoft neural voices,
currently `en-US-AndrewMultilingualNeural` — the recent "female to male voice"
commit changed this default). It also writes per-sentence cue JSON to
`captions/<id>.json`, which the subtitle overlay consumes via
[`src/lib/cues.ts`](../website/src/lib/cues.ts). Everything is static files —
the browser never calls a TTS service.

---

## Part 3 — The runtime pipeline: scroll → frame

This is where "rendering" happens in the browser. The flow, top to bottom:

```
wheel/touch input
   → Lenis (smooth lerp)                     src/hooks/useLenis.ts, App.tsx
   → ScrollTrigger onUpdate                  src/hooks/useScrollProgress.ts
       → scroll.progress (hot module var)    src/store/scroll.ts
       → stageIndex (zustand, on change)     src/store/useStore.ts
   → RAF loop (every frame)                  src/components/media/useMediaScrubber.ts
       → local progress of active section    core.ts: localProgressFor()
       → video.currentTime = progress × dur  mediaLifecycle.ts: scrubVideo()
       → ctx.drawImage(video) onto canvas    mediaLifecycle.ts: drawFrame()
       → opacity/transform side-effects      mediaDomFx.ts
```

### 3.1 The scroll spine — `StorySections.tsx` + `useScrollProgress.ts`

[`StorySections.tsx`](../website/src/components/story/StorySections.tsx)
renders one `<section id={stage.id}>` per stage — *empty* except for a
screen-reader heading. Its only job is to be **tall**: each video stage
declares `scrollVh` (~165vh in the deep dive), and that height is the scrub
runway — the distance you scroll through a section is the timeline of its clip.
A trailing 100svh spacer lets the last clip scrub to its end.

[`useScrollProgress.ts`](../website/src/hooks/useScrollProgress.ts) creates the
**single ScrollTrigger** in the app. On every update it computes a fractional
stage index from live DOM rects (`stageFloatFromDom` — robust to sections of
different heights), writes normalized progress into `scroll.progress`, and
pushes `floor(f)` into the store as the active `stageIndex`.

[`useLenis.ts`](../website/src/hooks/useLenis.ts) wires Lenis and GSAP into
**one clock**: Lenis does not self-drive (`autoRaf: false` in `App.tsx`);
GSAP's ticker advances Lenis, and each Lenis scroll event pokes
`ScrollTrigger.update()`. One RAF loop, no competing clocks.

### 3.2 Stage data — `src/data/stages.ts` / `oneBreathStages.ts`

Each `Stage` bundles: `id` (== manifest clip id == section DOM id), rail label,
caption, `media` (`src` MP4 path + `poster` webp + fit + alt text), `scrollVh`,
and optional narration tokens. The `act2()` factory builds one from just the id
and text. This file is the join point between the offline pipeline (asset
paths) and the runtime (sections, captions, scrub targets).

### 3.3 The scrubber — `MediaLayer.tsx` + `useMediaScrubber.ts`

[`MediaLayer.tsx`](../website/src/components/media/MediaLayer.tsx) is a fixed,
full-viewport layer that renders:

- one `<img>` **poster per stage** (final frame; static content under reduced
  motion, blurred loading-fallback otherwise), and
- **one shared `<canvas>`** — the actual animation surface for every clip.

Note what it does *not* render: any `<video>` elements. Videos are created
off-DOM (`document.createElement('video')`), muted, and used purely as
**decoders**.

[`useMediaScrubber.ts`](../website/src/components/media/useMediaScrubber.ts)
runs the hot RAF loop. Per frame, for the active stage
(`runClipStageFrame`):

1. **Local progress** — `localProgressFor(section)` reads the section's
   bounding rect: 0 when its top hits the viewport top, 1 when scrolled out.
2. **Seek** — `scrubVideo(video, local)` sets
   `video.currentTime = local × (duration − oneFrame)`.
3. **Draw** — if the video has a decoded frame (`videoDrawable`),
   `drawFrame()` copies it onto the shared canvas with contain/cover math.
   `drawImage` from a video element is a GPU-side copy of the frame the
   hardware decoder already produced — nothing decodes on the main thread. A
   `lastDraw` key (`id:time`) skips redundant redraws when the scroll is idle.
4. **Envelope** — the canvas opacity is
   `presence × smooth(local, HOLD=0.04, REVEAL=0.16) × frameReveal`:
   - *presence* lerps 0↔1 as stages hand off (no hard cuts at boundaries),
   - the *HOLD→REVEAL* ramp keeps the clip hidden during the first ~4% of the
     section — that's the centred **title-card beat** — then fades it in,
   - *frameReveal* latches upward once real frames draw, so a momentarily
     un-decoded frame can't flash back to black mid-scrub.

### 3.4 Why seeking is smooth — `mediaLifecycle.ts`

[`mediaLifecycle.ts`](../website/src/components/media/mediaLifecycle.ts) holds
the three tricks:

- **Coalesced seeks.** `scrubVideo` issues nothing while `video.seeking` is
  true. However fast the RAF loop runs, seeks land at the decoder's own pace
  and always jump to the *latest* target — never a queue of stale frames. It
  also skips seeks smaller than half a frame (30fps grid), so idle scroll
  doesn't thrash the decoder.
- **Sliding window of decoders.** Distances are measured in stages from the
  active one: within `preloadDistance: 2` a clip's video is created and fetched
  (`preload='auto'` — one small file, one request); beyond
  `releaseDistance: 3` it is released (`src` removed, cache dropped) so the
  browser reclaims decoder + buffer memory. At most ~5 decoders exist at once,
  even on the 50-scene page. Failed loads self-retry after a 3s backoff.
- **Resolution tiers.** `pickTier()` in
  [`core.ts`](../website/src/components/media/core.ts) computes the device-pixel
  width the 16:9 clip will actually span: over 960 device pixels → 1080p file,
  otherwise the 540p file is pixel-for-pixel identical on that screen and
  half the bytes. `tierSrc()` just rewrites `video/1080/` → `video/540/`.

All tuning knobs live in one place: `MEDIA_CONFIG` in `core.ts` (fps, lerp
speeds, preload/release distances, hold/reveal points, DPR cap).

### 3.5 Title-card choreography — `mediaDomFx.ts`

[`mediaDomFx.ts`](../website/src/components/media/mediaDomFx.ts) applies the
per-frame DOM side effects, all driven by the same `local` value: the caption
starts low/centred and rises `22vh` as the clip fades in (`applyCaptionLift`),
the sub-line fades out (`applySubFade`), the hero title scales
(`applyHeroScale`), and the scroll cue disappears (`applyScrollCue`). All
direct `style` writes — never React state — because they run every frame.

### 3.6 Loading state — `MediaLoader.tsx`

If you jump deep into the page and the active clip is past its title card but
still has no decodable frame, the scrubber counts "not ready" frames; after 12
consecutive RAF frames (~200ms — real stall, not a blink) it flips
`mediaLoading` in the store and
[`MediaLoader.tsx`](../website/src/components/media/MediaLoader.tsx) shows the
"rendering…" overlay. The clips deliberately **start from black**, so the
loading state is just… the animation's beginning — and the *final*-frame poster
never spoils the ending.

### 3.7 Hands-free Play — narration + auto-scroll

Two more layers ride on the same machinery:

- [`NarrationLayer.tsx`](../website/src/components/story/NarrationLayer.tsx)
  plays the active stage's MP3 straight through at natural rate (never
  scrubbed, so the voice stays clean) and publishes its playhead into a hot
  state module ([`src/store/narration.ts`](../website/src/store/narration.ts)).
- [`PlayButton.tsx`](../website/src/components/story/PlayButton.tsx) inverts the
  relationship: while Play is on, it **drives the scroll** to follow the
  audio's playhead — so the same scroll→frame pipeline renders the animation,
  just with the narration as the driver instead of your finger. Any manual
  scroll stops Play. [`Subtitles.tsx`](../website/src/components/story/Subtitles.tsx)
  shows the current sentence using the cue JSON via
  [`src/lib/cues.ts`](../website/src/lib/cues.ts).

### 3.8 Accessibility fallback

With `prefers-reduced-motion` (read in
[`useResponsive.ts`](../website/src/hooks/useResponsive.ts)), the scrubber's
`runReducedStageFrame` path shows only the static final-frame poster per stage
— no seeking, no canvas — and Lenis switches to instant scroll (`lerp: 1`).

---

## Part 4 — Cheat sheet: which file does what

| Task | File |
|---|---|
| Draw an animation (offline) | `website/anim/<chapter>/NN-<name>.py` |
| Shared look (palette/fonts/fps/helpers) | `website/anim/style.py` |
| List of all scenes → ids | `website/anim/render.manifest.json` |
| Run Manim renders | `website/anim/render.sh` |
| Scrub-friendly ffmpeg encode + poster | `website/anim/encode.sh` (540p: `encode-videos.sh`) |
| Narration MP3s + subtitle cues | `website/scripts/narrate.py` ← `src/data/narration.json` |
| Served assets | `website/public/anim/<chapter>/{video/1080,video/540,posters,audio,captions}/` |
| Routes, Lenis provider, GSAP setup | `src/App.tsx` |
| Story page composition | `src/routes/StoryPage.tsx` |
| Stage definitions (id, caption, clip, height) | `src/data/stages.ts`, `src/data/oneBreathStages.ts` |
| Scroll spine (tall empty sections) | `src/components/story/StorySections.tsx` |
| Scroll → progress + active stage | `src/hooks/useScrollProgress.ts` |
| Lenis ↔ GSAP single clock | `src/hooks/useLenis.ts` |
| Hot-path scroll value | `src/store/scroll.ts` |
| UI state (stage index, play, volume…) | `src/store/useStore.ts` |
| Posters + shared canvas DOM | `src/components/media/MediaLayer.tsx` |
| The RAF scrub loop | `src/components/media/useMediaScrubber.ts` |
| Video create/seek/draw/release | `src/components/media/mediaLifecycle.ts` |
| Config knobs, tier pick, progress math | `src/components/media/core.ts` |
| Title-card fades/lifts per frame | `src/components/media/mediaDomFx.ts` |
| "rendering…" overlay | `src/components/media/MediaLoader.tsx` |
| Voice playback | `src/components/story/NarrationLayer.tsx` |
| Hands-free auto-scroll | `src/components/story/PlayButton.tsx` |
| Subtitles + cue parsing | `src/components/story/Subtitles.tsx`, `src/lib/cues.ts` |

---

## The mental model to keep

**The animation is a film strip glued to the scrollbar.** Python/Manim prints
the film ahead of time; ffmpeg perforates it every 12 frames so any spot is
cheap to jump to; the browser holds a handful of hardware decoders open, and on
every animation frame it asks "how far into this section am I?", seeks the film
to that spot, and blits the decoded frame onto one canvas. Everything else —
captions rising, posters fading, the play button — is choreography around that
one loop.
