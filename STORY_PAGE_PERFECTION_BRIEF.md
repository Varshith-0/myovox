# Story Page — Perfection Pass · Handoff Brief for the Next Session

> Paste-and-go brief. Read this top to bottom **first**, then follow §6 (Process).
> Scope is the **Story page only**. Technical & Code pages are out of scope for
> editing (but `src/content/technical_report.md` is a *source of truth* you must read).

---

## 0. Your operating contract (read this twice)

You are perfecting a public, educational, scroll-driven explainer. Treat it as if
it **will go viral and be picked apart by domain experts, CS people, and pedants.**
The bar: **a neuroscientist, a CS grad, an ML researcher, and a careful layperson
should each finish it without spotting a single error — scientific, narrative,
visual, factual, grammatical, or interaction.** Not one silly mistake.

Hard rules:
1. **Do not assume — ask.** The previous session repeatedly assumed what the reader
   knows (e.g. assumed "EMG" needs no definition). That was wrong. Whenever a
   content/scope/taste decision is genuinely the user's, **stop and ask** (see the
   question bank in §7). Default to asking when unsure.
2. **Science = Narration = Animation, exactly.** Every spoken sentence must match
   what is on screen at that moment, and every on-screen claim must be true per the
   papers / technical report. If any of the three disagree, it's a bug.
3. **Define every term before it's used,** at the audience's level (§1).
4. **Cite your evidence.** For every scientific claim you write or verify, note the
   paper + section (or `technical_report.md` line) it comes from, in the task notes.
   If a claim can't be sourced, flag it to the user — do not ship it.
5. **Audit first, fix second.** Produce `STORY_TASKS.md` (exhaustive, ranked), get
   the user's sign-off, then fix one task at a time, verifying each.
6. **Use ultracode workflows** for the audit (fan out over dimensions/stages) and
   for batched fixes + adversarial verification. Give maximum effort.
7. **Verify visually.** After any clip change, render it and *read the frames*
   (extract PNGs with ffmpeg) and check the live page. Never call a clip "done"
   from code alone.
8. **Ethics & honesty are non-negotiable** (single subject, not a medical device,
   credit others, no over-claiming, respect licenses).

---

## 1. The audience (DECIDED — do not re-litigate, but confirm edge cases)

- **Baseline reader: a CS graduate who knows *a little* ML, but not deep learning.**
  - You MAY assume: programming, basic math, the rough idea of "a model learns from
    data."
  - You must NOT assume: any neuroscience, physiology, physics, anatomy, signal
    processing, phonetics/linguistics, or speech tech. **Explain all of it.**
  - You must NOT assume deep-learning fluency: explain neural nets, training,
    embeddings, attention, convolution, CTC, distillation, language models, beam
    search/WFST, reranking — **from first principles**, gently.
- **Reach goal:** a curious non-CS person should still follow the gist. Favor plain
  language + analogy; introduce jargon only after defining it.
- **Litmus test for every page:** "Could our baseline reader watch this clip and its
  narration and *never need to open Google*?" If no → it's a task.

## 1a. Other decisions (DECIDED)

- **Story length: exactly 50 stages.** You have **full freedom** to add / remove /
  reorder / merge / split stages **as long as the total stays 50.** Propose the new
  structure in `STORY_TASKS.md` and get sign-off before executing.
- **Clarity over length (within the 50):** individual clips may get longer/richer if
  it removes confusion. A confused viewer is the worst outcome. Don't pad.

---

## 2. What the site is (context)

A black-and-white, scroll-driven explainer of **decoding speech from facial-muscle
electrical signals (surface EMG → text)**. The Story page is **50 stages**, each a
scrubbed **Manim** video clip with a fixed caption overlay and optional voice
narration + word-synced subtitles. **There is no longer any 3D/WebGL** — the whole
story is Manim clips now (the previous 3D head was removed).

The headline result: a published **51.17% word-error baseline → 18.53% WER**, by
three changes on top of the UC Davis work.

### File map (Story page)
- `website/src/data/stages.ts` — **the spine.** 50 `STAGES`; each: `id, rail,
  caption, sub, act, media{kind:'video', src, poster, alt}, scrollVh,
  captionPosition, scene`. Helper `act2(id, rail, caption, alt, sub?, scrollVh)`.
  ⚠️ `scene`/`SceneParams`/`sampleScene`/`stageIndexFor` are **vestigial** (3D gone)
  — inert data; cleaning the type is optional and low-priority.
- `website/src/data/narration.json` — **single source of truth for spoken text**
  (`id → sentence string`). `scripts/narrate.py` turns it into `.mp3` + `.captions.json`.
- `website/src/data/narration.ts` — derives `NARRATED_IDS` from `STAGES`.
- `website/src/data/muscles.ts` — speech-muscle map (names, groups, positions).
- `website/anim/*.py` — Manim scenes. Intro: `i1_hero … i6_signal`
  (hero, why, landscape, roadmap, muscles, signal). Bridges: `b01…b20`.
  Mid/late: `s7…s30`. Shared style: `emg_style.py`. Social card: `s_og.py`.
- `website/public/anim/<id>.mp4` + `<id>.poster.webp` + `<id>.mp3` + `<id>.captions.json`
  — built artifacts (committed).
- `website/src/components/story/` — `Caption`, `Subtitles`, `NarrationLayer`,
  `PlayButton`, `ProgressRail`, `SpokenSentence`, `SpeakerControl`, `StorySections`.
- `website/src/components/three/MediaLayer.tsx` — the **video scrubber** (the only
  remaining file under `three/`; it composites clip + poster, fades, lifts for
  subtitles, drives hero-title shrink + scroll-cue). Its CSS: `MediaLayer.module.css`.
- `website/src/hooks/` — `useScrollProgress`, `useLenis`, `useResponsive`.
- `website/src/store/` — `useStore` (zustand), `scroll`, `narration` (hot-state).
- `website/src/routes/StoryPage.tsx`, `App.tsx`, `components/layout/{Layout,Loader,Nav}`.

### Sources of truth (science) — READ THESE
- `papers/` (3 PDFs, all **UC Davis**):
  1. **Geometry of orofacial neuromuscular signals: speech articulation decoding
     using surface EMG** — Gowda, **McNaughton**, Miller (J. Neural Eng). SPD/geometric
     features; open 16-subject dataset.
  2. **Non-invasive electromyographic speech neuroprosthesis: a geometric
     perspective** — Gowda, Miller. EMG→text; explicit invasive-vs-non-invasive BCI
     framing; SPD matrices.
  3. **emg2speech: synthesizing speech from EMG using self-supervised speech
     models** — Gowda, **Comstock**, Miller. EMG→audio; corpus; ALS participant.
- `website/src/content/technical_report.md` — the numbers, dataset, pipeline.
- (Read the PDFs page-by-page with the file reader's `pages` arg.)

### Build / verify pipeline (this machine)
- Render a clip: `cd website/anim && PYTHONPATH=$PWD /opt/anaconda3/bin/manim -qh
  --media_dir /tmp/emg_media <file>.py <Class>`
- Encode for scrubbing + poster: `MENV=/opt/anaconda3 MEDIA_DIR=/tmp/emg_media
  ./encode.sh <file>.py <Class> <id>` (every frame a keyframe; `-g 1`).
- Poster gotcha: anaconda ffmpeg may lack webp — make poster with
  `/opt/homebrew/bin/cwebp` from a PNG grabbed via `/opt/homebrew/bin/ffmpeg -sseof
  -0.1 -i <id>.mp4 -frames:v 1 x.png`.
- Narration: `/opt/anaconda3/bin/python scripts/narrate.py <ids...>`
  (edge-tts, voice `en-US-AvaMultilingualNeural`, rate `+10%`). Needs network.
  Re-run for any id whose `narration.json` text changed; it rewrites `.mp3` + `.captions.json`.
- Inspect a clip: extract frames with `ffmpeg -ss <t> -i <id>.mp4 -frames:v 1 f.png`
  then **read the PNG**.
- In-page checks (dev): `window.__scrollToStage(id)`, `__scrollToStageLocal(id,
  local)`, `__scrollToProgress(p)`. ⚠️ The old `scripts/shoot.mjs` waits for a
  `<canvas>` that no longer exists — write a canvas-free Playwright screenshot
  helper (wait for content instead). Run Playwright scripts from inside
  `website/` (or `website/scripts/`) so `playwright` resolves.
- Manim conventions: monochrome palette + helpers in `emg_style.py`
  (`mono/serif/num/counter/glow/dim`); 1080p30; **no LaTeX — Pango `Text` only**;
  one `self.next_section(...)` **per spoken sentence** (this is how a scrubbed clip
  stays aligned to narration — keep narration sentence-count == beat-count).
- Manim 0.20 gotchas: `LaggedStartMap(lambda m: FadeIn(m,...), ...)` breaks — use
  `LaggedStart(*[FadeIn(m,...) for m in grp])`; `VGroup.set_opacity(1)` clobbers
  children's own `fill_opacity` — fade with `FadeIn(grp, shift=...)` instead.

---

## 3. The numbers & facts that MUST stay consistent everywhere

Verify every occurrence across all 50 clips + captions + narration against these
(and re-verify these against `technical_report.md` / the papers — don't trust this
list blindly, it's a convenience copy):

- **WER ladder:** 51.17 → 40.63 → 26.14 → **18.53**. **PER:** 38.19 / 39.02 /
  22.34 / 20.90. **Oracle (n-best union):** 9.30.
- **Dataset:** 9,660 sentences (9,541 unique); **single healthy subject**;
  **31-channel** surface EMG @ **5 kHz**; parallel audio recorded simultaneously
  (training-time signal only); split **8,500 / 760 / 400**; lexicon **34,546 words**
  (~5× corpus vocab). EMG is **vocalized** (not silent) with time-aligned audio.
- **Features:** SPD shrinkage covariance 31×31 → 961-dim; **25 ms window / 20 ms hop**
  (→ 50 frames/s); α = 0.1; squeezed to **384-dim**.
- **Pipeline:** dual-CTC (100 HuBERT units + ~40 phonemes); bidirectional Conformer;
  **WavLM-L9** cross-modal distillation (training only); 2-model ensemble; multi-scale
  n-best **union**; **QLoRA-fine-tuned 7B** reranker; **WFST (HLG, k2/icefall)** decode.
- **Authorship/credit:** UC Davis — **Gowda** (all 3 papers), **Miller** (all),
  **McNaughton** (paper 1), **Comstock** (paper 3). Borrowed methods credited:
  Conformer (Gulati), WavLM (Chen), HuBERT (Hsu), CTC (Graves), TDS (Hannun),
  MONA-style distillation/rerank (Benster), k2/icefall (Povey), LibriSpeech
  (Panayotov), Qwen2.5, QLoRA (Dettmers). Animation style: homage to 3Blue1Brown.
- **Honesty caveats (must remain visible/true):** one speaker; cross-subject is
  future work; **not a medical device**; it's a *silent-speech interface*, you must be
  able to move your face (so not for the fully paralyzed — invasive BCI serves them).

---

## 4. Audit dimensions — fan a workflow over each (with adversarial verification)

For **every one of the 50 stages**, and for the page as a whole, check:

- **A. Scientific accuracy** — every claim true & sourced to a paper/report line.
  Watch for over-claiming, wrong numbers, sloppy mechanism ("muscles make
  electricity" must be explained correctly: motor-neuron command → muscle-fiber
  action potentials → summed voltage at skin).
- **B. Narration ↔ visual sync** — does the spoken sentence match what's on screen
  *at that scrub position*? Beat count == sentence count? Any clip where the voice
  describes something not yet (or no longer) visible?
- **C. Narration quality** — clarity for the §1 audience; define-before-use; tone;
  no undefined jargon; grammar; pronunciation traps for TTS (numbers, acronyms,
  symbols → spell out, e.g. "5 kHz" → "five kilohertz").
- **D. Animation quality & legibility** — text overlaps, off-screen elements, text
  vs clip-edge clipping, readability at 1080p AND when letterboxed on the page;
  timing/pacing; visual polish; consistent motion language across all clips.
- **E. Pedagogy & completeness** — Is the logical chain unbroken? What's **missing**
  (a concept used before it's taught)? What's **redundant**? Is the ordering optimal?
  What single additions would most help understanding (within the 50-cap)?
- **F. Code / UX / interaction bugs** — scroll-scrub, Play/pacing, subtitles+scrim,
  caption rise/shrink, progress rail, reduced-motion, **mobile/portrait**, keyboard
  & focus, console errors, performance (50 videos), asset caching/versioning.
- **G. Consistency** — terminology, capitalization, number formatting, units,
  acronyms, and naming identical across all stages and matching the report.
- **H. Manim craft / "most out of Manim"** — are we using its strengths (smooth
  morphs, value-tracked counters, lagged reveals, camera/zoom, graphs) or just
  fading text? Where would a better visual metaphor teach more? Shared visual
  vocabulary across the 50 (same glyph = same meaning everywhere)?
- **I. Accessibility & ethics** — `alt`/text alternatives, captions correctness,
  reduced-motion path, contrast, honest framing, credits, licensing of any asset,
  no PII, no medical/clinical claims.
- **J. Polish** — grammar/typos in captions & subs, punctuation, the em-dash/quote
  characters, poster frames (is the poster a good representative frame?), social card.

---

## 5. Known issues & context carried from the previous session (don't rediscover)

These were observed but **not** all fixed — verify and add to tasks:

1. **Play scroll-pacing may jump forward.** Pressing **Play** on a mid-story stage
   appeared to jump the view forward several stages. Investigate `PlayButton`'s
   scroll-pacing (it paces scroll to the audio playhead). May be a real bug. HIGH.
2. **Narration↔scrub drift.** Narration audio is decoupled from the video scrub
   except via PlayButton pacing; pacing maps audio-time→scroll linearly while clip
   beats have uneven durations → the visible beat can lag the spoken sentence.
   Audit sync on every clip; consider mapping pacing to `next_section` boundaries.
3. **Subtitle scrim** was strengthened to an opaque vertical band (`Subtitles.module.css`)
   and the clip lifts when narrating (`MediaLayer.module.css .withCaptions`). Verify
   across all clips, 1–5 line subtitles, and mobile — no clip bottom-text bleed-through.
4. **Hero** title now interpolates display→h3 size over scroll and holds **2 lines**
   (em-based max-width); scroll-cue moved OUTSIDE the caption wrap and fades on
   scroll. Verify across many viewport widths/heights & mobile.
5. The **6 intro clips were just rewritten** for the CS audience (EMG defined via
   electro+myo+graphy; brain labeled + brain→nerve→muscle pulse; 3 papers + UC Davis
   authors; BCI comparison incl. a **safety** row). They still must pass the full bar.
6. `stages.ts` vestigial `scene`/`SceneParams` (3D removed). Inert; optional cleanup.
7. **Orphaned artifacts:** old caption/mp3 for retired ids (`articulation`,
   `electricity`, `sensors`, `recording`) still in `public/anim`. Clean up.
8. The narration generator splits text into sentences for cues — keep sentences
   short enough that subtitles stay ≤ ~3 lines; spell out numbers/acronyms for TTS.

---

## 6. Process the next session MUST follow

1. **Read everything** (Story scope): all `website/anim/*.py` + `emg_style.py`;
   `stages.ts`, `narration.json`, `narration.ts`, `muscles.ts`; every component in
   `src/components/story/` + `MediaLayer.tsx` + their CSS; `StoryPage.tsx`, `App.tsx`,
   `Layout`, `Loader`; the **3 PDFs**; `technical_report.md`; `tokens.css`/`globals.css`.
   Also actually **watch** representative clips (extract frames) — don't audit from code alone.
2. **Confirm open questions with the user** (§7) before deciding anything subjective.
3. **Run the audit** as an ultracode workflow: fan out over §4 dimensions × the 50
   stages; each finding adversarially verified (is it really wrong? cite proof).
   Dedup and rank by severity (blocker / major / minor / polish).
4. **Write `STORY_TASKS.md`** — exhaustive, categorized, severity-ranked. Each task:
   atomic, with **file(s)**, **what's wrong**, **the fix**, **acceptance criteria**,
   and **source/citation** for any scientific change. Include a proposed 50-stage
   structure if you're reshaping. Hundreds of tasks is fine and expected.
5. **Get the user's sign-off** on `STORY_TASKS.md` (and the structure) before fixing.
6. **Fix one-by-one** (or batched by workflow), **rendering + reading frames** and
   checking the live page after each. Re-run `narrate.py` for changed narration.
   Re-verify any changed science against the papers.
7. Keep a running **CHANGELOG** in `STORY_TASKS.md` (check off + note verification).
8. Final gate: run the §8 definition-of-done checklist as a last adversarial sweep.

---

## 7. Question bank — ASK the user before deciding (don't assume)

Already decided (see §1/§1a): audience = CS + light ML; 50-stage cap with full
reshape freedom; clarity over length. Still confirm/ask:

- **Tone:** how playful vs. serious/academic? Any humor allowed?
- **Voice:** keep the current TTS voice (`en-US-AvaMultilingualNeural`, +10%) or change?
  Human-recorded later?
- **Maker credit:** keep "made by Varshith Madishetty, with Claude"? Name UC Davis
  authors in full on screen, or just the lab?
- **Claims policy:** how strong may the "promising vs BCI" framing be? Any words to
  avoid (e.g. anything sounding medical/clinical)?
- **Devices:** is mobile/portrait a first-class target or desktop-first? (affects layout tasks)
- **Accessibility bar:** target a specific standard (e.g. WCAG AA)? Captions on by default?
- **Restructure:** if reshaping the 50, do you want to approve the new outline before any clip work?
- **Visual style:** strictly keep monochrome + Fraunces/JetBrains Mono, or open to
  subtle additions (one accent, motion style changes)?
- **Scientific depth ceiling:** for the deep-dive (CTC, WFST, distillation), how deep
  before it's "too much"? Where do we draw the line for a light-ML reader?
- Anything that reads as uncertain in the audit → **ask, attach the options, recommend one.**

---

## 8. Definition of done (final adversarial checklist)

- [ ] Every scientific claim is **true and sourced** (paper/section or report line in notes).
- [ ] Every clip: **narration matches the on-screen beat**, sentence-count == beat-count,
      and a §1 reader needs no external lookup.
- [ ] No undefined jargon; every term defined before first use.
- [ ] No text overlap / off-screen / clipped / illegible elements at target viewports
      (incl. letterboxed-on-page and mobile); reduced-motion path works.
- [ ] Subtitles never collide with clip text; scrim masks cleanly at all line counts.
- [ ] No console errors; scroll, Play/pacing, subtitles, progress rail correct on
      desktop **and** mobile; Play doesn't jump stages.
- [ ] All numbers, terms, units, acronyms **consistent** across 50 stages + report.
- [ ] Captions/subs: no typos, correct punctuation/characters; TTS pronounces numbers/acronyms right.
- [ ] Posters are representative frames; social card correct.
- [ ] Honest framing intact (one subject, not medical, credits, licenses).
- [ ] A neuroscientist, an ML researcher, a CS grad, and a layperson each find **zero**
      mistakes.

---

### Kickoff line for the next chat
> "Read `STORY_PAGE_PERFECTION_BRIEF.md`, then read the whole Story page + the 3
> papers + technical_report.md. Ask me the §7 questions. Then run an ultracode audit
> over §4 and write `STORY_TASKS.md` for my sign-off before fixing anything. Attention
> to detail — assume it goes viral; no silly mistakes."
