# Myovox — interactive explainer

A scroll-driven, cinematic explainer of how speech is decoded from the faint electrical signals of
facial muscles (surface EMG → text). Black-and-white only: each stage of the pipeline plays as a
short, scroll-scrubbed animation on black. Three pages:

- **Story** (`/`) — the scroll experience: ~50 short animated scenes, one idea each.
- **Technical** (`/technical`) — the full technical report (tables, formulas, code).
- **Code** (`/code`) — curated implementation snippets + the repository link.

It accompanies the [myovox](https://github.com/Varshith-0/myovox) pipeline (surface-EMG speech
decoding, **18.53% word error rate**). Every number shown is drawn from `docs/technical_report.md`.

## Stack

Vite + React + TypeScript (strict) · GSAP ScrollTrigger + Lenis (single shared RAF) · Zustand ·
react-router (HashRouter) · react-markdown + remark-gfm · react-syntax-highlighter ·
Fonts: Fraunces (display) + JetBrains Mono.

## Develop

```bash
npm install
npm run dev        # http://localhost:5173/myovox/
```

Other scripts: `npm run build` · `npm run preview` · `npm run typecheck` · `npm run lint` ·
`npm run format`.

## The animations

The Story is a sequence of pre-rendered [Manim](https://www.manim.community/) clips. Each scene is a
Python file in [`anim/`](anim/) (`01-hero.py … 50-end.py`, in story order, plus the shared
`style.py`); it renders to `public/anim/<id>.mp4` + `<id>.poster.webp`, where `<id>` is the kebab-case
clip id referenced from `src/data/stages.ts`. At runtime the `MediaLayer` plays the active stage's
clip and **scrubs it with the local scroll** — the animation literally plays as you scroll. Reduced
motion shows the static poster instead.

The author-time pipeline lives entirely in `anim/`:

```bash
cd anim
./render.sh            # render all 50 scenes -> public/anim/<id>.{mp4,poster.webp}
./render.sh hero       # render one scene by clip id
./render.sh og         # render the social card -> public/og.png
```

[`anim/render.manifest.json`](anim/render.manifest.json) is the authoritative
`file → scene class → clip id` map (story order matches `src/data/stages.ts`); `render.sh` reads it,
runs `manim -qh` then `encode.sh` (re-encodes every frame as a keyframe for smooth scrubbing and
emits the poster). Narration is generated separately:

```bash
python scripts/narrate.py            # all stages, from src/data/narration.json (the spoken-script source)
python scripts/narrate.py hero why   # specific stages -> public/anim/<id>.mp3 + <id>.captions.json
```

`render.sh` defaults to a base anaconda install (`MENV=/opt/anaconda3`) that provides `manim` +
`ffmpeg`; override `MENV` / `MEDIA_DIR` for another environment.

## Architecture

```
src/
  main.tsx                entry
  App.tsx                 router + Lenis provider + GSAP↔Lenis RAF sync
  routes/                 StoryPage · TechnicalPage · CodePage (the last two lazy-loaded)
  components/
    layout/               Nav · Footer · Layout · Loader
    media/                MediaLayer (the scroll-scrubbed Manim-clip player)
    story/                StorySections · Caption · ProgressRail · SpokenSentence ·
                          NarrationLayer · Subtitles · PlayButton · SpeakerControl · CaptionsToggle
    ui/                   CodeBlock · LogoMark · codeTheme
  hooks/                  useLenis (RAF bridge) · useScrollProgress · useResponsive
  store/                  useStore (zustand UI state) · scroll (hot-path progress) · narration (audio playhead)
  data/                   stages.ts (the narrative spine) · site.ts · speech.ts · muscles.ts ·
                          narration.ts (+ narration.json — the spoken-script source for narrate.py)
  content/                technical_report.md · snippets.ts
  styles/                 tokens.css · globals.css
```

**The core rule:** a single ScrollTrigger turns the story container's scroll into one fractional
stage index — it writes a normalized `progress` into a hot-path module and pushes the active stage
into the store. The captions/rail react to that index, and the MediaLayer scrubs the active clip
imperatively in its own RAF loop. Nothing downstream reads DOM scroll events directly.

## Deploy (GitHub Pages)

`vite.config.ts` sets `base: '/myovox/'`. Pushing to `main` runs `.github/workflows/deploy.yml`,
which builds `website/` and publishes `dist/` → `https://<user>.github.io/myovox/`.

- For a `username.github.io` user-site or a custom domain, build with `VITE_BASE=/ npm run build`.
- Routing uses **HashRouter** (URLs like `/#/technical`) — zero-config and refresh-proof on Pages.
  `public/.nojekyll` is included so hashed asset paths serve correctly.

Verify a production bundle locally before deploying:

```bash
npm run build && npm run preview
```

## Accessibility & performance

Respects `prefers-reduced-motion` (no scrubbing — static posters, instant scroll); word-synced
subtitles are on by default; semantic headings, a skip link, and a text alternative for each clip.
The reading pages (react-markdown + the syntax highlighter) are code-split out of the initial Story
bundle, and only clips near the active stage are loaded/decoded.
