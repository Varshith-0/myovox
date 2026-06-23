/**
 * The narrative spine of the Story page.
 *
 * One entry = one full-viewport scroll section. Act 1 stages render the live 3D
 * scene (reading the normalized scroll `progress` from the store and interpolating
 * between adjacent stages' `scene` params — see {@link sampleScene}); Act 2 stages
 * render a scrubbed Manim clip via the MediaLayer (their `scene.layers` are all 0
 * so the canvas fades out). This keeps the scene decoupled from the DOM — the
 * single most important architectural rule of this app.
 */

export type Vec3 = readonly [number, number, number]

/**
 * Interpolatable scene state. Every field is numeric (or a vector of numbers)
 * so the renderer can lerp between two stages cleanly.
 */
export interface SceneParams {
  /** Camera world position. */
  readonly camPos: Vec3
  /** Camera look-at target. */
  readonly camTarget: Vec3
  /** Target head yaw in radians (the scene eases toward this). */
  readonly headYaw: number
  /** Head formation: 0 = dispersed point cloud, 1 = fully formed surface. */
  readonly form: number
  /** Fresnel rim-light intensity on the head (the core glow). */
  readonly rim: number
  /** Post-processing bloom strength for this stage. */
  readonly bloom: number
  /** Layer opacities/intensities, each 0..1, faded per stage. */
  readonly layers: {
    /** Solid realistic head (crossfades with the point cloud on the muscles stage). */
    readonly face: number
    readonly muscles: number
    readonly electrodes: number
    readonly signal: number
    readonly neural: number
    readonly tokens: number
  }
}

/**
 * What renders behind a stage's caption.
 *  - `scene`: the live 3D canvas (Act 1, the default).
 *  - `video`: a Manim clip scrubbed by the stage's local scroll (Act 2). `src`
 *     and `poster` are paths *relative to BASE_URL* (e.g. `anim/ctc.mp4`); the
 *     MediaLayer prefixes `import.meta.env.BASE_URL` so they resolve under
 *     `/emg2text/`. `poster` is shown for reduced-motion / while loading; `alt`
 *     is a one-sentence description of the animation for assistive tech.
 *  - `svg`: an optional live React/SVG stage (named component).
 */
export type StageMedia =
  | { readonly kind: 'scene' }
  | {
      readonly kind: 'video'
      readonly src: string
      readonly poster: string
      readonly fit?: 'contain' | 'cover'
      readonly alt?: string
    }
  | { readonly kind: 'svg'; readonly component: string }

export interface Stage {
  /** Stable id, also used as the section's DOM id / anchor. */
  readonly id: string
  /** Tiny label for the progress rail (small caps). */
  readonly rail: string
  /** Headline caption (1–2 lines), rendered with a soft white glow. */
  readonly caption: string
  /** Optional sub-line under the caption. */
  readonly sub?: string
  /** Which act: 1 = live 3D body, 2 = Manim machine. Defaults to 1. */
  readonly act?: 1 | 2
  /** What renders behind the caption. Defaults to `{ kind: 'scene' }`. */
  readonly media?: StageMedia
  /** Section height in vh (scroll length). Defaults to 100; Act-2 video stages
   *  want ~140–180 so the clip has comfortable scrub range. */
  readonly scrollVh?: number
  /** Phoneme/word/sentence content surfaced by the Tokens layer. */
  readonly tokens?: {
    readonly phonemes?: readonly string[]
    readonly words?: readonly string[]
    readonly sentence?: string
  }
  /** Where the caption sits (default bottom). 'top' frees the frame for labels. */
  readonly captionPosition?: 'top' | 'bottom'
  /** The scene state this stage holds. Act-2 stages set all layers ~0. */
  readonly scene: SceneParams
}

/** Layers fully off — Act-2 (Manim) stages fade the 3D scene out entirely. */
export const OFF = { face: 0, muscles: 0, electrodes: 0, signal: 0, neural: 0, tokens: 0 } as const

/** Accessors that apply the schema defaults (act 1, scene media, 100vh). */
export const stageAct = (s: Stage): 1 | 2 => s.act ?? 1
export const stageMedia = (s: Stage): StageMedia => s.media ?? { kind: 'scene' }
export const stageScrollVh = (s: Stage): number => s.scrollVh ?? 100

// The solid head is the default everywhere (face: 1); only the hero stage opts
// out (face: 0) to keep the dispersed point-cloud "dust" intro that forms into it.
const NONE = { face: 1, muscles: 0, electrodes: 0, signal: 0, neural: 0, tokens: 0 } as const

// Shared Act-2 scene: the 3D canvas is fully faded (the MediaLayer covers it),
// the head a faint dispersed hint behind the crossfade.
const A2: SceneParams = {
  camPos: [0, 0.12, 5.0],
  camTarget: [0, 0, 0],
  headYaw: 0,
  form: 0.15,
  rim: 0.15,
  bloom: 0.3,
  layers: { ...OFF },
}

/** An Act-2 (Manim video) stage. */
function act2(id: string, rail: string, caption: string, alt: string, sub?: string): Stage {
  return {
    id,
    rail,
    caption,
    sub,
    act: 2,
    media: {
      kind: 'video',
      src: `anim/${id}.mp4`,
      poster: `anim/${id}.poster.webp`,
      fit: 'contain',
      alt,
    },
    scrollVh: 165,
    captionPosition: 'top',
    scene: A2,
  }
}

export const STAGES: readonly Stage[] = [
  // ---- Act 1: the body (live 3D head) ----
  {
    id: 'hero',
    rail: 'Intro',
    caption: 'We can read speech from the muscles of your face.',
    sub: 'No microphone, no sound — just the faint electricity of moving muscles, read back into text. Scroll to see how it gets to four words in five.',
    scene: {
      camPos: [0, 0.15, 4.4],
      camTarget: [0, 0, 0],
      headYaw: 0,
      form: 0.06,
      rim: 0.7,
      bloom: 0.9,
      layers: { ...NONE, face: 0 },
    },
  },
  {
    id: 'muscles',
    rail: 'Muscles',
    caption: 'Speech starts as movement.',
    sub: 'Your brain fires nerves that drive dozens of muscles in the face and throat — even the faintest motion makes electricity.',
    scene: {
      camPos: [0.7, 0.12, 3.6],
      camTarget: [0, -0.02, 0],
      headYaw: 0.18,
      form: 1,
      rim: 1.0,
      bloom: 1.0,
      layers: { ...NONE, face: 1 },
    },
  },
  {
    id: 'articulation',
    rail: 'Talking',
    caption: 'Talking is dozens of muscles firing in sequence.',
    sub: 'Lips, jaw, tongue and throat — every sound is a different pattern.',
    captionPosition: 'top',
    scene: {
      camPos: [0.1, 0.05, 5.3],
      camTarget: [0, 0.66, 0],
      headYaw: 0.04,
      form: 1,
      rim: 0.9,
      bloom: 1.05,
      layers: { ...NONE, muscles: 1 },
    },
  },
  {
    id: 'electricity',
    rail: 'Electricity',
    caption: 'Every time a muscle moves, it makes a little electricity on the skin.',
    sub: 'Far too faint to feel — but a sensor can.',
    captionPosition: 'top',
    scene: {
      camPos: [0.8, 0.05, 4.0],
      camTarget: [0.05, 0.1, 0],
      headYaw: 0.3,
      form: 1,
      rim: 1.0,
      bloom: 1.15,
      layers: { ...NONE, muscles: 0.55, electrodes: 0.22 },
    },
  },
  {
    id: 'sensors',
    rail: 'Sensors',
    caption: 'A grid of 31 sensors rests on the skin and listens.',
    sub: 'Each one feels the electricity from the muscles beneath it — five thousand times a second.',
    scene: {
      camPos: [2.1, 0.0, 2.7],
      camTarget: [0.25, -0.12, 0],
      headYaw: 0.62,
      form: 1,
      rim: 1.05,
      bloom: 1.1,
      layers: { ...NONE, electrodes: 1 },
    },
  },
  {
    id: 'recording',
    rail: 'Recording',
    caption: 'Each sensor traces a wiggly line, five thousand times a second.',
    sub: 'Thirty-one lines, thousands of points each — a noisy mess we now have to make sense of.',
    captionPosition: 'top',
    scene: {
      camPos: [1.4, -0.05, 2.6],
      camTarget: [0.2, -0.15, 0],
      headYaw: 0.45,
      form: 1,
      rim: 1.0,
      bloom: 1.2,
      layers: { ...NONE, electrodes: 0.65, signal: 1 },
    },
  },

  // ---- Act 2: the machine (scrubbed Manim clips) ----
  act2(
    'features-window', 'Slicing the signal',
    'First we chop each wiggly line into tiny overlapping slices — one every 20 milliseconds.',
    'A 25 ms window slides along 31 stacked signal traces, dropping a tick every 20 ms onto a frame timeline that counts up to 50 frames per second.',
    'Those 31 wiggly lines are far too much to use raw. So we slide a tiny 25-millisecond window along them and take a snapshot every 20 ms — turning the stream into a steady 50 snapshots a second.',
  ),
  act2(
    'two-sensors-dancing', 'Two dancers',
    'What does "move together" actually mean? Watch just two sensors.',
    'Two stacked traces wiggle while a moving dot plots one against the other; in-sync motion builds a tilted diagonal cloud, opposed motion tilts the other way, and unrelated motion fills a round blob.',
    'Forget thirty-one. Take two sensors and ask one question: do they rise and fall on the same beat, or not? That agreement — not loudness — is the whole idea.',
  ),
  act2(
    'features-cov', 'Moving together',
    "What tells sounds apart isn't how strong each sensor is — it's which sensors move together.",
    'Pairs of sensor snippets fill a 31×31 grid by how together they move; two different gestures make two different bright patterns.',
    "A snapshot's loudness barely matters. What separates one sound from another is which sensors rise and fall together — so for each snapshot we measure how every pair of sensors moves in sync.",
  ),
  act2(
    'every-pair-grid', 'Everyone with everyone',
    'Now ask that for every pair — and lay the answers in a grid.',
    'A single covariance value becomes one bright cell, then a scan-head fills a full 31 by 31 grid that is mirror-symmetric across a bright diagonal, and two different gestures light two clearly different patterns.',
    'Thirty-one sensors, each checked against all the others. Each cell holds one "do these two agree?" value. The whole 31-by-31 grid is a portrait of how the face moved together, this instant.',
  ),
  act2(
    'features-embed', 'Fingerprint',
    'We steady each matrix, then squeeze it down to 384 numbers — one fingerprint per slice.',
    'A speckled matrix blends 90% measured with 10% a plain pattern, then funnels into a row of 384 bars; the sentence becomes a filmstrip of fingerprints.',
    'That grid is noisy and huge. We steady it, then squeeze it down to just 384 numbers — one compact fingerprint per snapshot. This filmstrip of fingerprints is what the network actually reads.',
  ),
  act2(
    'what-is-a-net', 'What "the model" is',
    'We keep saying "the network reads it." So what is a network, really?',
    'A fingerprint flows left to right through several layers of a dial-filled box and out as a short vector; the dials sit at random angles and the first guess is shown garbled and dim.',
    "It's a function: a deep stack of millions of tiny dials that turns numbers in into a guess out. Nothing is programmed by hand — everything it knows lives in how the dials are set.",
  ),
  act2(
    'how-training-works', 'Rolling downhill',
    'Training is just this: guess, measure the miss, step downhill, repeat.',
    'An example flows through the dial-box to a guess; the error appears as height on a one-dimensional curve and a ball rolls downhill while the guessed letter sharpens toward the true one over repeated passes.',
    'Show it an example with a known answer. Measure how wrong the guess is. Nudge every dial a hair in the direction that shrinks the error — like a ball rolling down a hill — and do it millions of times.',
  ),
  act2(
    'targets-phon', 'Sounds, not spelling',
    "The model guesses sounds, not spelling — so it can handle words it's never seen.",
    'The words though, tough, through are struck out; the word cat morphs into the sounds K AE T; a palette of about forty sound symbols appears.',
    'What should it predict? Not letters — English spelling lies (though, tough, through). We predict the ~40 actual sounds, the building blocks linguists call phonemes, so it can spell words it has never seen.',
  ),
  act2(
    'targets-units', 'Finer sounds',
    "We also use 100 finer sound-shapes a machine discovered on its own — plus a marker for 'nothing new yet.'",
    'About forty phonemes sit beside 100 finer self-discovered units; a blank symbol marks no new sound.',
    "Phonemes are coarse, so we add a finer target: 100 sound-shapes a model discovered on its own from thousands of hours of audio — plus a 'blank' marker for 'nothing new yet'. Two views teach it more.",
  ),
  act2(
    'where-units-from', 'Sounds nobody named',
    'Those hundred finer sounds — nobody handed the machine a list. Where from?',
    'A scrolling waveform has a slice masked out; a model predicts the hidden piece, and over many clips the recurring snippets settle into a handful of representative bins tagged as one of a hundred.',
    'Self-supervised learning: play a model thousands of hours of audio, hide a chunk, make it predict the missing piece. To do that well, it has to invent its own catalog of sound-shapes.',
  ),
  act2(
    'two-answer-keys', 'Two answer keys',
    'So now there are two answer keys at once. Why bother with both?',
    'One stream of frames forks into two parallel target rows, about forty phonemes and one hundred units; a shortcut that satisfies the coarse row but fails the fine row is struck out, and the shared core glows where both agree.',
    'The ~40 human phonemes are clean but coarse; the 100 machine units are fine but strange. Being right on both is much harder to fake than being right on one — so it learns sound more deeply.',
  ),
  act2(
    'alignment-problem', 'Subtitles, no clock',
    'The real puzzle before any of this can train: you have the words, but no timestamps.',
    'A filmstrip of many blank frames sits above the three-symbol word K A E T; dotted lines try to pair frames to sounds and dangle with question marks, the words known but every timestamp struck out.',
    "Each second is fifty snapshots, but a word is only a handful of sounds — and nobody ever wrote down which snapshot is which. It's like a movie's subtitles with every timestamp erased.",
  ),
  act2(
    'ctc', 'Aligning the sounds',
    'Nobody marks where each sound starts. The model learns the order, and figures out the timing itself.',
    'Per-frame labels blank K K blank AE AE AE T blank collapse by merging repeats and dropping blanks to K AE T, and several different timings all collapse to the same answer.',
    'The catch: nobody labelled which snapshot is which sound. The model guesses a sound or blank per frame; collapsing repeats and blanks, many different timings give the same word — so it learns the order without being told the timing.',
  ),
  act2(
    'ctc-many-timings', 'Reward every right timing',
    'How the unlabeled puzzle becomes a training signal.',
    'Several different valid alignment rows for one word stack up, each with a small probability bar; the bars gather into one total that an upward force pushes higher, while a wrong-order row gets no push.',
    "Instead of betting on one timing, training adds up every timing that spells the right word — and pushes the whole total up at once. Get the order right and you're rewarded, however you stretched it.",
  ),
  act2(
    'encoder-bidir', 'Looking both ways',
    'To name the sound at one moment, look at what came before — and after — like replaying a tricky bit.',
    'Arrows reach a highlighted frame from only the left (causal), then from both sides (bidirectional).',
    'To name the sound at one instant, it helps to see what came just before and just after. The original model only looked backward (good for live captioning); for a finished recording, looking both ways is strictly better.',
  ),
  act2(
    'what-is-attention', 'A spotlight that reaches',
    'To name a blurry moment, the reader "pays attention" to other moments. What does that mean?',
    'From one highlighted frame, faint query lines fan out to all other frames; a few relevant lines thicken while the rest fade, and the weighted information from the strong ones flows back to update the asking frame.',
    'Each moment asks every other moment "how relevant are you to me?", gets a weight back, and pulls hardest on the few that matter — near or far. That reaching-and-weighting is attention.',
  ),
  act2(
    'what-is-convolution', 'The other lens',
    'Attention is the telescope. You also need a magnifier.',
    'Beside faint long-range attention lines, a small bracket window slides across a few adjacent frames, lighting only its local neighbors and emitting a sharpened local feature that the wide view missed.',
    'Attention reaches far but blurs the fine grain. A small sliding window — a convolution — reads only a handful of neighbors, but closely, catching the local texture attention misses.',
  ),
  act2(
    'memorize-trap', 'The memorizing trap',
    "You'd expect a bigger reader to be better. Here it's the opposite.",
    'A scatter of training dots; a huge model threads a wild curve through every dot but misses a new test dot badly, while a small four-layer model draws a smooth curve that lands near the new dot.',
    "With only one person's data, a giant model just memorizes the exact examples and falls apart on anything new — like cramming the answer key. So we deliberately keep the reader tiny.",
  ),
  act2(
    'conformer', 'The reader',
    'The reader uses two lenses at once: the whole sentence, and the fine local detail.',
    'From one frame, attention lines reach every other frame; a small convolution bracket slides over neighbours; a compact 4-layer stack beats a crossed-out giant one.',
    'The reader uses two lenses at once — attention, which pulls context from anywhere in the sentence, and convolution, which reads fine local texture. We keep it small on purpose: with one person’s data, a big model would just memorize.',
  ),
  act2(
    'heads', 'Three outputs',
    "The reader gives three answers per slice — and one of them isn't for reading text at all.",
    'The encoder fans into three heads: units, phonemes (highlighted), and a projection of 1024 numbers that glows toward the next stage.',
    "It outputs three things per snapshot: the 100 fine units, the ~40 phonemes (what everything downstream uses), and a third 1024-number 'projection' that isn't for reading text at all — it exists to imitate a real voice.",
  ),
  act2(
    'copy-the-teacher', 'Tracing the master',
    "That third output exists for a trick called distillation: a student traces a master's strokes.",
    "A faint confident master curve is drawn; a student pen first scrawls a crude attempt graded only by its endpoint, then traces the master's whole shape point by point until its line matches.",
    "Instead of grading only right-or-wrong, let a student copy a stronger model's rich internal picture — not the final label, the whole detailed representation it forms. Like tracing over a master's brushstroke.",
  ),
  act2(
    'voice-as-teacher', 'The recording in the room',
    'Here the teacher is the real voice — a model that already learned to hear, recorded only while training.',
    "Two time-aligned lanes of one sentence: a clean audio waveform feeds a tall layer stack whose highlighted middle layer pours a rich representation down into the noisy EMG lane's projection, stamped training only, with the microphone struck out at use time.",
    'While the data was collected, a microphone ran alongside the sensors. An audio model turns that voice into a rich middle-layer picture; the muscle model copies it. At real use, the mic is gone.',
  ),
  act2(
    'distillation', 'A teacher voice',
    'While training, the muscle model copies a model that listens to the real voice recorded at the same time.',
    'A top audio lane (waveform into WavLM into a layer-9 representation) pours knowledge into the bottom EMG lane projection; a stamp reads training only.',
    "During training only, we also recorded the real voice. A powerful audio model listens to it, and we pull the muscle model's projection to match what it hears — a teacher to copy. At real use there is no microphone.",
  ),
  act2(
    'frozen-recognizer', 'The honesty lock',
    "Being 'close' to the real voice isn't enough. A locked reader forces the copy to actually spell out sounds.",
    'Two different sounds collapse into one blurry vector, then a padlocked phoneme reader forces them apart into crisp separable ones.',
    "But 'sounding close' can cheat — two different sounds can blur into one vague average. So a locked phoneme-reader forces the copied features to actually spell out the right sounds, not merely resemble the voice.",
  ),
  act2(
    'blurry-average-cheat', 'The lazy shortcut',
    'Why lock a reader onto the copy? Because "just be close" has a cheat.',
    'Two distinct target points for two sounds; a student point told only to minimize distance drifts to the blurry midpoint, scoring close on average while the two sounds become indistinguishable inside the smudge.',
    'The student copies one long string of numbers. To look close to two similar sounds on average, the laziest move is to aim for one mushy point between them — scoring well while erasing the very difference that matters.',
  ),
  act2(
    'frozen-lock-how', "A reader it can't change",
    "The fix: a locked sound-reader that the model isn't allowed to touch.",
    "A padlocked recognizer reads the student's blurry smudge and outputs garbled ambiguous sounds with a rejection mark, then a force splits the smudge into two crisp points that the frozen reader can name cleanly.",
    "Bolt a frozen sound-reader onto the copied features and demand real, distinct sounds come out. Because its dials are locked, the blur can't soften it — to pass, the student must pull the two sounds back apart.",
  ),
  act2(
    'twin-warmstart', 'Two readers',
    'We give the reader a head start, then train a tougher twin that fails differently.',
    "Weights copy from an old model's front-end and heads into a new one; a tougher twin adds masking, sensor dropout, noise and rotation; the two make different mistakes.",
    'We give the new reader a head start from the old model, then train a tougher twin with heavier defences — masking moments, dropping sensors, adding noise. The two fail differently, which is exactly why averaging them helps.',
  ),
  act2(
    'second-opinion', 'Ask twice',
    "Two readers that fail differently beat one that's slightly better. Here's the intuition.",
    'Two guess curves wobble around a hidden true line with errors in different spots; their point-by-point average hugs the true line tightly, and a word-error readout falls from 26 to about 20.',
    "Average two doctors who make different mistakes and the errors partly cancel. Two identical experts add nothing. That's why the twin was trained to be different — different mistakes are the asset.",
  ),
  act2(
    'wfst', 'The map of words',
    'Sounds become words by finding the cheapest path through a giant map of how English is spelled and spoken.',
    'A path lights up across a toll-road map; three smaller maps H, L (a 34,546-word dictionary) and G compose into one graph.',
    'Sounds are not words yet. We find the cheapest legal path through one giant map of how 34,546 words are pronounced and how English words follow each other — five times more words than we trained on, so it can output unseen ones.',
  ),
  act2(
    'sounds-to-words-search', 'Cheapest road',
    'Turning loose sounds into words is a search: find the cheapest road through a giant map.',
    'A noisy stream of per-frame sounds feeds a branching node-and-edge map with small toll values; many candidate paths flicker faintly and one continuous lowest-cost route lights up from start to end, spelling a sentence.',
    'Lay every legal route from sounds to real words on one map, give each step a toll — cheap when sound and grammar agree, dear when they fight — and the best sentence is the lowest-toll route end to end.',
  ),
  act2(
    'knobs', 'Two dials',
    "Same sounds can be 'ice cream' or 'I scream.' Two dials decide which words come out.",
    'Homophone pairs ice cream / I scream resolve as an acoustic-scale dial lands near 0.25 and a blank-penalty dial lands at 2.0.',
    "The same sounds can be 'ice cream' or 'I scream'. One dial balances the muscle reading against plain English (~0.25); another curbs the model's habit of guessing 'blank' (~2.0). Set wrong, most words come out wrong.",
  ),
  act2(
    'what-is-lm', 'What English expects',
    'Part of every toll comes from a "language model." What does it actually know?',
    'After the phrase the peanut, a fan of candidate next words appears sized by likelihood, butter tall and bicycle tiny; the tall ones become cheap edges and the short ones expensive edges on the map.',
    "A language model has read mountains of text and learned one thing: which word likely follows the words so far. After \"peanut,\" \"butter\" lights up; \"bicycle\" stays dim. It can't hear — it only knows how English flows.",
  ),
  act2(
    'ensemble-nbest', 'Many guesses',
    'Average two readers, keep dozens of guesses each, and pool them — until the right answer is almost always in there.',
    'Two readers average to about 20% wrong; a ranked n-best list and a multi-scale union pool guesses; a perfect oracle would be 9.30% wrong.',
    'Now we combine: average the two readers for a steadier signal (26% to ~20% wrong), keep dozens of candidate sentences, and pool them across dial settings. A perfect chooser would be only 9.3% wrong — that gap is the prize.',
  ),
  act2(
    'what-is-wer', 'Counting the misses',
    "We keep quoting \"percent wrong.\" Here's exactly how that's measured.",
    'A reference sentence and a guess align word by word; one substitution, one insertion, and one deletion are marked and summed, then divided by the reference word count into an abstract fraction.',
    "Line your guess against the truth and count every word you'd swap, add, or delete to fix it; divide by the number of true words. Two edits in an eight-word sentence is a quarter wrong. Lower is better.",
  ),
  act2(
    'rerank', 'The chooser',
    'A language model reads the guesses and the raw sounds together — and chooses the sentence that makes the most sense.',
    'A 7-billion-parameter model squeezed to 4-bit with small locked adapters reads about ten candidates plus the detected sounds and picks one final sentence; an audit reads 0.',
    'A language model reads every candidate and the detected sounds together, then picks the sentence that makes most sense — using the sounds to break ties between look-alikes. We audited it: it never invents words the evidence does not support.',
  ),
  act2(
    'binding-constraint', 'The honest ceiling',
    'Why it stops at eighteen and a half — and what would actually break through.',
    'The reranker scans an n-best list and settles at 18.53, then on a hard sentence finds the correct word absent from every candidate; a sound-error gauge holds near 20.9 while the word-error gauge refuses to drop below 18.5.',
    "The chooser can only pick from the list it's handed. For the hardest errors the right word was never in the sounds at all — so no language model can conjure it. The ceiling is the ears, not the chooser.",
  ),
  act2(
    'journey', 'The whole journey',
    'One sentence, from muscle to text.',
    'A left-to-right montage: speak, 31 sensors, fingerprint filmstrip, the reader, per-frame sounds, the word map, candidate sentences, the chooser, and the final sentence.',
    'One sentence, end to end — speak, 31 sensors, fingerprints, the reader, sounds, the word-map, a pool of guesses, the chooser, text. Everything you have just seen, in order.',
  ),
  act2(
    'arc', 'The climb',
    'From 51% wrong to 18.5% — in three moves.',
    'Four descending markers 51.17, 40.63, 26.14, 18.53 percent word-error, with a phoneme-error track that drops then barely moves on the last move.',
    'Three moves: fix the decode, look both ways while copying the teacher voice, then combine readers and add the chooser. The sound-error fell on move two — it truly heard better — but barely moved on move three.',
  ),
  // ---- Closing: what we changed, who we built on, and thanks ----
  act2(
    'approach', 'What we changed',
    'What we changed — and how we trained.',
    "A 'what we changed' ledger: three before→after rows — scale-1.0 decode → tuned open-vocab decode, causal TDS → bidirectional Conformer + distillation, single 1-best → ensemble/n-best/7B rerank — while a word-error readout ticks 51.17 down to 18.53 and a training recipe runs along the bottom.",
    'On top of a published 51% baseline we made three changes: a tuned open-vocabulary decode, a full-context bidirectional Conformer distilled from the parallel voice (training only), and a two-model ensemble pooled into n-best lists that a QLoRA-tuned 7B language model reranks — 51% → 18.5% word error.',
  ),
  act2(
    'silent', 'Silent speech',
    'What it’s for: silent speech.',
    'A silent-speech flow — mouth the words → a muted speaker → typed text — over four use-case cards (quiet room, private, noisy place, hands-free) and an honesty note: one healthy speaker, cross-subject is future work, not a medical device.',
    'Trained on one healthy speaker, this is a silent interface — a silent keyboard, not a clinical device. You mouth the words and it types them: dictate in a quiet room, speak privately in public, get through where a microphone can’t, or go hands-free. Cross-subject use is future work.',
  ),
  act2(
    'foundation', 'Foundation',
    'None of this starts without the team at UC Davis.',
    "Two foundation stones — the 'geometric perspective' paper and the 'emg2speech' corpus — bear a small 'our pipeline' block; a glowing name plate reads Harshavardhana T. Gowda, with Daniel C. Comstock and Lee M. Miller, UC Davis.",
    'The corpus, the 31-channel sensor array, the SPD geometric features, and the first EMG-to-text decoder all came out of UC Davis — Harshavardhana T. Gowda, with Daniel C. Comstock and Lee M. Miller. Our pipeline is a small block resting on that foundation; we only built upward.',
  ),
  act2(
    'credits', 'Credits',
    'Every method here was borrowed — and credited.',
    'A two-column credit ledger pairing each method with the work it came from — Conformer (Gulati), WavLM (Chen), HuBERT (Hsu), CTC (Graves), TDS (Hannun), cross-modal distillation + LLM rerank (Benster / MONA), WFST decode (Povey, k2/icefall), LibriSpeech (Panayotov), Qwen2.5, and QLoRA (Dettmers) — closing on "composition, not invention".',
    'We invented none of the building blocks. The Conformer, WavLM, HuBERT units, CTC, the TDS front-end, the MONA-style cross-modal distillation and LLM reranking, the k2/icefall decode, the LibriSpeech lexicon, Qwen2.5 and QLoRA — each came from someone else’s work. This is composition, not invention.',
  ),
  act2(
    'thanks', 'Thank you',
    'Thank you.',
    'A closing card: “Thank you” for making it to the end, the maker — Varshith Madishetty — and a credit “built with the help of Claude”, shown with the Claude mark.',
    'Thank you for making it all the way to the end. Made by Varshith Madishetty, built with the help of Claude.',
  ),
  act2(
    'end', 'The end',
    'The end.',
    'A cinematic finale: one last EMG signal traces across the dark, shatters into a cloud of particles, and they stream together to spell THE END — which ignites with a light-sweep and a halo before settling as embers drift away.',
  ),
] as const

export const STAGE_COUNT = STAGES.length

/* ------------------------------------------------------------------ */
/* Interpolation: map global scroll progress -> a blended SceneParams  */
/* ------------------------------------------------------------------ */

const lerp = (a: number, b: number, t: number) => a + (b - a) * t

const lerpVec3 = (a: Vec3, b: Vec3, t: number): Vec3 => [
  lerp(a[0], b[0], t),
  lerp(a[1], b[1], t),
  lerp(a[2], b[2], t),
]

/** Smoothstep easing for buttery transitions between stage keyframes. */
const ease = (t: number) => t * t * (3 - 2 * t)

/**
 * Sample the scene at a normalized global progress `p` in [0, 1].
 * `p = 0` is the first stage, `p = 1` the last; intermediate values blend the
 * two surrounding stages with smoothstep easing.
 */
export function sampleScene(p: number): SceneParams {
  const clamped = Math.min(1, Math.max(0, p))
  const f = clamped * (STAGE_COUNT - 1)
  const i = Math.min(STAGE_COUNT - 2, Math.floor(f))
  const t = ease(f - i)
  const a = STAGES[i].scene
  const b = STAGES[i + 1].scene
  return {
    camPos: lerpVec3(a.camPos, b.camPos, t),
    camTarget: lerpVec3(a.camTarget, b.camTarget, t),
    headYaw: lerp(a.headYaw, b.headYaw, t),
    form: lerp(a.form, b.form, t),
    rim: lerp(a.rim, b.rim, t),
    bloom: lerp(a.bloom, b.bloom, t),
    layers: {
      face: lerp(a.layers.face, b.layers.face, t),
      muscles: lerp(a.layers.muscles, b.layers.muscles, t),
      electrodes: lerp(a.layers.electrodes, b.layers.electrodes, t),
      signal: lerp(a.layers.signal, b.layers.signal, t),
      neural: lerp(a.layers.neural, b.layers.neural, t),
      tokens: lerp(a.layers.tokens, b.layers.tokens, t),
    },
  }
}

/** The stage index nearest a given global progress — drives the active caption. */
export function stageIndexFor(p: number): number {
  const clamped = Math.min(1, Math.max(0, p))
  return Math.round(clamped * (STAGE_COUNT - 1))
}
