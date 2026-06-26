# Myovox — interactive WebGL explainer

A scroll-driven, cinematic explainer of how speech is decoded from the faint electrical signals of
facial muscles (surface EMG → text). Black-and-white only: a glowing point-cloud human head on black,
transforming through the stages of the pipeline as you scroll. Three pages:

- **Story** (`/`) — the scroll experience.
- **Technical** (`/technical`) — the full technical report (tables, formulas, code).
- **Code** (`/code`) — curated implementation snippets + the repository link.

It accompanies the [myovox](https://github.com/Varshith-0/myovox) pipeline (surface-EMG speech
decoding, **18.53% word error rate**). Every number shown is drawn from `docs/technical_report.md`.

## Stack

Vite + React + TypeScript (strict) · three.js / @react-three/fiber / drei / postprocessing ·
GSAP ScrollTrigger + Lenis (single shared RAF) · Zustand · react-router (HashRouter) ·
react-markdown + remark-gfm · Fonts: Fraunces (display) + JetBrains Mono.

## Develop

```bash
npm install
npm run dev        # http://localhost:5173/myovox/
```

Other scripts: `npm run build` · `npm run preview` · `npm run typecheck` · `npm run lint` ·
`npm run format`.

## The 3D head

The head is a point cloud surface-sampled, **at author time**, from a realistic human-head scan and
shipped as two small binaries in `public/` (`head-points.bin`, `head-mesh.bin`) — no runtime glTF
parsing, no textures. Each point is fresnel-shaded by its own normal so grazing points glow (the rim),
with a black inner mesh occluding the back so the head reads as a luminous shell.

Re-bake (e.g. to swap the model or change point count) with:

```bash
npm run bake:head   # downloads the source scan on first run, writes public/head-*.bin
```

To swap the head: change `SRC_URL` in `scripts/bake-head.mjs` to another permissive head model
(glTF/GLB with a single triangle mesh) and re-run. The procedural fallback in
`src/three/headGeometry.ts` is used automatically if `head-points.bin` is missing.

**Source geometry:** the “Lee Perry-Smith” head (Infinite-Realities), distributed with the three.js
examples under **CC-BY 3.0**. Only sampled geometry is used; attribution is given here and on the Code
page.

## Architecture

```
src/
  App.tsx                 router + Lenis provider + GSAP↔Lenis RAF sync
  routes/                 StoryPage · TechnicalPage · CodePage (the last two lazy-loaded)
  components/
    layout/               Nav · Footer · Layout · Loader
    three/                Scene · HeadRig · Head · HeadOccluder · Electrodes ·
                          SignalField · NeuralNet · CameraRig · SceneDriver · Effects
    story/                StorySections · Caption · ProgressRail
    ui/                   GlowText · CodeBlock
  hooks/                  useLenis (RAF bridge) · useScrollProgress · useResponsive · useHeadPoints
  store/                  useStore (zustand) · scroll (hot progress) · sceneSample (per-frame state)
  data/                   stages.ts (narrative + keyframes) · results.ts · site.ts
  three/                  headGeometry · headMesh · anchors · graph
  content/                technical_report.md · snippets.ts
  styles/                 tokens.css · globals.css
```

**The core rule:** ScrollTrigger writes one normalized `progress` into a hot-path module; the 3D
scene reads it imperatively in `useFrame` and interpolates between per-stage keyframes. The scene is
never coupled to DOM scroll events, and there is one RAF loop (GSAP's ticker drives Lenis).

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

Respects `prefers-reduced-motion` (no scrubbing/idle motion, instant scroll); degrades on mobile/weak
GPUs (fewer points, lighter post-processing — append `?lite` to force it); a WebGL error boundary
falls back to readable content rather than crashing; skip link, semantic headings, and a text
alternative for the canvas. The heavy chunks (three.js, the report renderer) are code-split out of the
initial load.
