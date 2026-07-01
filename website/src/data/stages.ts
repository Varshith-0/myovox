/**
 * The narrative spine of the Story page.
 *
 * One entry = one full-viewport scroll section. Every stage renders a scrubbed
 * Manim clip via the MediaLayer, driven by the section's local scroll. The
 * caption and progress-rail overlays react to the active stage index (published
 * by useScrollProgress into the store) — never to DOM scroll events directly,
 * the single most important architectural rule of this app.
 */

/**
 * What renders behind a stage's caption: a Manim clip scrubbed by the stage's
 * local scroll. `src` and `poster` are paths *relative to BASE_URL* (e.g.
 * `anim/ctc.mp4`); the MediaLayer resolves them via {@link assetUrl}. `poster` is
 * shown for reduced-motion / while loading; `alt` is a one-sentence description of
 * the animation for assistive tech.
 */
export interface StageMedia {
  readonly src: string
  readonly poster: string
  readonly fit?: 'contain' | 'cover'
  readonly alt?: string
}

export interface Stage {
  /** Stable id, also used as the section's DOM id / anchor. */
  readonly id: string
  /** Tiny label for the progress rail (small caps). */
  readonly rail: string
  /** Headline caption (1–2 lines), rendered with a soft white glow. */
  readonly caption: string
  /** Optional sub-line under the caption. */
  readonly sub?: string
  /** The scrubbed Manim clip that renders behind the caption. */
  readonly media: StageMedia
  /** Section height in vh (scroll length). Defaults to 100; video stages want
   *  ~140–245 so the clip has comfortable scrub range. */
  readonly scrollVh?: number
  /** Phoneme/word/sentence content surfaced by the Tokens layer. */
  readonly tokens?: {
    readonly phonemes?: readonly string[]
    readonly words?: readonly string[]
    readonly sentence?: string
  }
  /** Where the caption sits (default bottom). 'top' frees the frame for labels. */
  readonly captionPosition?: 'top' | 'bottom'
}

/** Section scroll length in vh (defaults to a full viewport). */
export const stageScrollVh = (s: Stage): number => s.scrollVh ?? 100

/** A Manim video stage scrubbed by its section's local scroll. */
function act2(id: string, rail: string, caption: string, alt: string, sub?: string, scrollVh = 165): Stage {
  return {
    id,
    rail,
    caption,
    sub,
    media: {
      src: `anim/${id}.mp4`,
      poster: `anim/${id}.poster.webp`,
      fit: 'contain',
      alt,
    },
    scrollVh,
    captionPosition: 'top',
  }
}

export const STAGES: readonly Stage[] = [
  // ---- Intro: the "why" prologue + the body/data (all Manim clips) ----
  act2(
    'hero', 'Intro',
    'We can read speech from the muscles of your face.',
    'A bundle of 31 EMG traces scrolls in and collapses into one glowing line that resolves into the words "read speech from muscles"; the title MYOVOX settles in.',
    'No microphone, no sound — just the faint electricity of moving muscles, read back into text. By the end, four words in five come back right.',
  ),
  act2(
    'why', 'Why',
    'Why this exists.',
    'Three research-paper cards fan in and collapse onto a UC Davis name plate (Gowda, Miller, with Comstock and McNaughton); a "what I changed" block stacks onto a "their foundation" block; a fifty-tick timeline labelled "the same science — made to watch" lights up.',
    'Research papers are a wall of math almost nobody reads. This is that same science — made to watch: about fifty short scenes, built on one UC Davis lab’s work, then pushed further.',
  ),
  act2(
    'landscape', 'Why this way',
    'Three ways to read speech from the body.',
    'Three doors — a brain implant, a scalp cap, and skin sensors — each scored on four rows: needs surgery?, signal strength, needs movement?, and safety. Skin sensors are surgery-free, strong-signal, and safe.',
    'A brain implant works even without movement, but it takes surgery. Scalp sensors need no surgery, but the signal is faint and smeared. Muscle sensors on the skin are strong and surgery-free — the practical sweet spot, as long as you can still move your face.',
  ),
  act2(
    'roadmap', 'The map',
    'What you’re about to learn.',
    'A left-to-right map lights up stop by stop: the body, fingerprints, the reader, sounds, the word map, the chooser, and the final score — about fifty short scenes.',
    'Here is the whole journey: the body and its signal, tidy fingerprints, the reader that learns, sounds instead of spelling, words on a map of English, and a chooser that picks the best sentence — ending at the score. About fifty short scenes, each one idea.',
  ),
  act2(
    'muscles', 'Muscles',
    'Speech starts as movement.',
    'A 2D face; a "brain" dot fires electrical pulses down nerves to named muscle markers — orbicularis oris, zygomaticus, masseter, genioglossus, sternohyoid — lighting each in turn.',
    'To shape one word your brain fires dozens of muscles — lips, cheeks, jaw, tongue and throat — each on its own rhythm. And every contraction leaks a faint flicker of electricity onto the skin.',
  ),
  act2(
    'signal', 'The signal',
    'Listening, five thousand times a second.',
    'A one-millivolt pulse rises on a voltage axis; a grid of 31 skin sensors traces overlapping wiggly lines; a microphone marked "training only" fades in; the view zooms out to the corpus counts.',
    'Each faint pulse is read by a grid of 31 skin sensors, five thousand times a second, with the real voice recorded alongside — across 9,660 sentences from one speaker. Hidden inside that noise is every word; the rest of the story is pulling it back out.',
    245,
  ),

  // ---- Act 2: the machine (scrubbed Manim clips) ----
  act2(
    'features-window', 'Slicing the signal',
    'First we chop each wiggly line into tiny overlapping snapshots — one every 20 milliseconds.',
    'A 25 ms window slides along a stack of sample signal traces, dropping a tick every 20 ms onto a timeline that counts up to 50 snapshots per second.',
    'Those 31 wiggly lines are far too much to use raw. So we slide a tiny 25-millisecond window along them and take a snapshot every 20 ms — turning the stream into a steady 50 snapshots a second.',
  ),
  act2(
    'two-sensors-dancing', 'Two dancers',
    'What does "move together" actually mean? Watch just two sensors.',
    'Two stacked traces wiggle while a vertical scan line sweeps them and dots accumulate into a scatter cloud, plotting B against A; in-sync motion builds a tilted diagonal cloud, opposed motion tilts the other way, and unrelated motion fills a round blob.',
    'Forget 31. Take two sensors and ask one question: do they rise and fall on the same beat, or not? That agreement — not loudness — is the whole idea.',
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
    'A single covariance value becomes one bright cell, then a scan-head fills a full 31 by 31 grid that is mirror-symmetric across a bright diagonal; the off-diagonal cells flash to show which sensors moved together.',
    'Thirty-one sensors, each checked against all the others. Each cell holds one "do these two agree?" value. The whole 31-by-31 grid is a portrait of how the face moved together, this instant.',
  ),
  act2(
    'features-embed', 'Fingerprint',
    'We steady each matrix, then squeeze it down to 384 numbers — one fingerprint per snapshot.',
    'A speckled matrix blends 90% measured with 10% a plain pattern, then funnels into a row of 384 bars; the sentence becomes a filmstrip of fingerprints.',
    'That grid is noisy and huge. We steady it, then squeeze it down to just 384 numbers — one compact fingerprint per snapshot. This filmstrip of fingerprints is what the reader actually reads.',
  ),
  act2(
    'what-is-a-net', 'What "the model" is',
    'We keep saying "the network reads it." So what is a network, really?',
    'A fingerprint flows left to right through several layers of a dial-filled box and out as a short vector; the dials sit at random angles and the first guess is shown garbled and dim.',
    "It's a function: a deep stack of millions of tiny dials that turns numbers into a guess. Nothing is programmed by hand — everything it knows lives in how the dials are set.",
  ),
  act2(
    'how-training-works', 'Rolling downhill',
    'Training is just this: guess, measure the error, step downhill, repeat.',
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
    "We also use 100 finer sound-shapes a model discovered on its own — plus a marker for 'nothing new yet.'",
    'About forty phonemes sit beside 100 finer self-discovered units; a blank symbol marks no new sound.',
    "Phonemes are coarse, so we add a finer target: 100 sound-shapes a model discovered on its own from nearly a thousand hours of audio — plus a 'blank' marker for 'nothing new yet'. Two views teach it more.",
  ),
  act2(
    'where-units-from', 'Sounds nobody named',
    'Those hundred finer sounds — nobody handed the machine a list. Where from?',
    'A scrolling waveform has a snapshot masked out; a model predicts the hidden piece, and over many clips the recurring snippets settle into a handful of representative bins tagged as one of a hundred.',
    'Self-supervised learning: play a model nearly a thousand hours of audio, hide a chunk, make it predict the missing piece. To do that well, it has to invent its own catalog of sound-shapes.',
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
    'A filmstrip of many blank frames sits above the three-sound word K-AE-T (cat); dotted lines try to pair frames to sounds and dangle with question marks, the words known but every timestamp struck out.',
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
    'To name a blurry snapshot, the reader "pays attention" to other snapshots. What does that mean?',
    'From one highlighted snapshot, faint query lines fan out to all other snapshots; a few relevant lines thicken while the rest fade, and the weighted information from the strong ones flows back to update the asking snapshot.',
    'Each snapshot asks every other snapshot "how relevant are you to me?", gets a weight back, and pulls hardest on the few that matter — near or far. That reaching-and-weighting is attention.',
  ),
  act2(
    'what-is-convolution', 'The other lens',
    'Attention is the wide lens. You also need a magnifier.',
    'Beside faint long-range attention lines, a small bracket window slides across a few adjacent frames, lighting only its local neighbours and emitting a sharpened local feature that the wide view missed.',
    'Attention reaches far but blurs the fine grain. A small sliding window — a convolution — reads only a handful of neighbours, but closely, catching the local texture attention misses.',
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
    "The reader gives three answers per snapshot — and one of them isn't for reading text at all.",
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
    'Here the teacher is the real voice, captured only while training — read by a model that already learned to hear.',
    "Two time-aligned lanes of one sentence: a clean audio waveform feeds a tall layer stack whose highlighted middle layer pours a rich representation down into the noisy EMG lane's projection, stamped training only, with the microphone struck out at use time.",
    'While the data was collected, a microphone ran alongside the sensors. An audio model turns that voice into a rich middle-layer picture; the muscle model copies it. At real use, the mic is gone.',
  ),
  act2(
    'distillation', 'A teacher voice',
    'While training, the muscle model copies a model that listens to the real voice recorded at the same time.',
    'Face-to-face teacher and student vector columns; dashed ties pull the student to match as a gap readout falls from 1.00 to 0.04; a flatten-to-gray detour warns against a dull average; then a contrastive step pulls each moment toward its partner and pushes rivals away, under a fork labelled 0.5 L2 (copy the numbers) and 0.5 InfoNCE (keep each moment distinct).',
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
    "Weights copy from an old model's front-end and heads into a new one; a tougher twin trains under stronger jitter, heavier dropout, and a different audio teacher; the two make different mistakes.",
    'We give the new reader a head start from the old model, then train a tougher twin differently — stronger jitter, heavier dropout, and a different audio teacher. The two fail differently, which is exactly why averaging them helps.',
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
    'A noisy stream of per-frame sounds feeds a branching node-and-edge map with small toll values; candidate sentences flicker faintly above the stream, then one continuous lowest-cost route lights up start to end, spelling a sentence.',
    'Lay every legal route from sounds to real words on one map, give each step a toll — cheap when sound and grammar agree, steep when they fight — and the best sentence is the lowest-toll route end to end.',
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
    'Now we combine: average the two readers for a steadier signal (26% to ~20% wrong), keep dozens of candidate sentences, and pool them across dial settings. A perfect chooser would be only 9.30% wrong — that gap is the prize.',
  ),
  act2(
    'what-is-wer', 'Counting the misses',
    "We keep quoting \"percent wrong.\" Here's exactly how that's measured.",
    'A reference sentence and a guess align word by word; one substitution, one insertion, and one deletion are marked and summed, then divided by the reference word count and read out as a percentage.',
    "Line your guess against the truth and count every word you'd swap, add, or delete to fix it; divide by the number of true words. Two edits in an eight-word sentence is a quarter wrong. Lower is better.",
  ),
  act2(
    'rerank', 'The chooser',
    'A language model reads the guesses and the raw sounds together — and chooses the sentence that makes the most sense.',
    'A 7-billion-parameter model squeezed to 4-bit with small trained adapters reads about ten candidates plus the detected sounds and picks one final sentence; an audit confirms it only ever chooses from the pool, never beyond it.',
    'A language model reads every candidate and the detected sounds together, then picks the sentence that makes most sense — using the sounds to break ties between look-alikes. We audited it: it never invents words the evidence does not support.',
  ),
  act2(
    'binding-constraint', 'The honest ceiling',
    'Why it stops at eighteen and a half — and what would actually break through.',
    'The chooser scans an n-best list and settles at 18.53, then on a hard sentence finds the correct word absent from every candidate; a sound-error gauge holds near 20.9 while the word-error gauge refuses to drop below 18.5.',
    "The chooser can only pick from the list it's handed. For the hardest errors the right word was never in the sounds at all — so no language model can conjure it. The ceiling is the ears, not the chooser.",
  ),
  act2(
    'journey', 'The whole journey',
    'One sentence, from muscle to text.',
    'A left-to-right montage: speak, 31 sensors, fingerprint filmstrip, the reader, per-frame sounds, the word map, candidate sentences, the chooser, and the final sentence.',
    'One sentence, end to end — speak, 31 sensors, fingerprints, the reader, sounds, the word-map, a pool of guesses, the chooser, text. Everything you have just learned, in order.',
  ),
  act2(
    'arc', 'The climb',
    'From 51% wrong to 18.5% — in three moves.',
    'Four descending markers 51.17, 40.63, 26.14, 18.53 percent word-error, with a phoneme-error track that drops then barely moves on the last move.',
    'Three moves: fix the decode, look both ways while copying the teacher voice, then combine readers and add the chooser. The sound-error fell on move two — it truly heard better — but barely moved on move three.',
  ),
  // ---- Closing: what I changed, who I built on, and thanks ----
  act2(
    'approach', 'What I changed',
    'What I changed — and how I trained.',
    "A 'what I changed' ledger: three before→after rows — scale-1.0 decode → tuned open-vocab decode, causal TDS → bidirectional Conformer + distillation, single 1-best → ensemble/n-best/7B rerank — while a word-error readout ticks 51.17 down to 18.53 and a training recipe runs along the bottom.",
    'On top of a published 51% baseline I made three changes: a tuned open-vocabulary decode, a full-context bidirectional Conformer distilled from the parallel voice (training only), and a two-model ensemble pooled into n-best lists that a QLoRA-tuned 7B language model reranks — 51% → 18.5% word error.',
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
    "Two foundation stones — the 'geometric perspective' paper and the 'emg2speech' corpus — bear a small 'my pipeline' block; a glowing name plate reads Harshavardhana T. Gowda, with Zachary D. McNaughton, Daniel C. Comstock and Lee M. Miller, UC Davis.",
    'The corpus, the 31-channel sensor array, the SPD geometric features, and the EMG-to-text decoder all came out of UC Davis — Harshavardhana T. Gowda, with Zachary D. McNaughton, Daniel C. Comstock and Lee M. Miller. My pipeline is a small block resting on that foundation; I only built upward.',
  ),
  act2(
    'credits', 'Credits',
    'Every method here was borrowed — and credited.',
    'A two-column credit ledger pairing each method with the work it came from — Conformer (Gulati), WavLM (Chen), HuBERT (Hsu), CTC (Graves), TDS (Hannun), cross-modal distillation + LLM rerank (Benster / MONA), WFST decode (Povey, k2/icefall), LibriSpeech (Panayotov), Qwen2.5, and QLoRA (Dettmers) — closing on "composition, not invention".',
    'I invented none of the building blocks. The Conformer, WavLM, HuBERT units, CTC, the TDS front-end, the MONA-style cross-modal distillation and LLM reranking, the k2/icefall decode, the LibriSpeech lexicon, Qwen2.5 and QLoRA — each came from someone else’s work. This is composition, not invention.',
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
    'A cinematic finale: one last EMG signal traces across the dark, shatters into a cloud of particles, and they stream together to spell THE END — which ignites with a light-sweep and a halo, then holds steady as faint motes hang in the dark.',
  ),
] as const

export const STAGE_COUNT = STAGES.length
