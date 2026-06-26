# How a Muscle Signal Becomes a Word — The Complete Explanation

*A from-the-ground-up walkthrough of the Myovox system. No code, no equations — just a
careful explanation of how every part works and why. If you read this end to end, you will
understand exactly how a faint electrical signal from the muscles of the face is turned into
readable English text.*

This document is the long, plain-language companion to [`technical_report.md`](technical_report.md).
The technical report is terse and aimed at experts who already know the field; it states
*what* the numbers are. This document is aimed at a curious, technically-literate reader who is
**new to speech decoding and to electromyography**, and it explains *how and why* everything
works, building each idea up from scratch.

---

## Table of contents

1. [The one-paragraph picture](#1-the-one-paragraph-picture)
2. [What problem are we even solving?](#2-what-problem-are-we-even-solving)
3. [The raw material: electricity from muscles](#3-the-raw-material-electricity-from-muscles)
4. [Step 1 — Turning the wiggly signal into features](#4-step-1--turning-the-wiggly-signal-into-features)
5. [Step 2 — Deciding what the answer looks like: phonemes and units](#5-step-2--deciding-what-the-answer-looks-like-phonemes-and-units)
6. [Step 3 — The acoustic model: reading sound from muscle](#6-step-3--the-acoustic-model-reading-sound-from-muscle)
7. [Step 4 — Learning from a real voice: cross-modal distillation](#7-step-4--learning-from-a-real-voice-cross-modal-distillation)
8. [Step 5 — From a stream of sounds to actual words: the decoder](#8-step-5--from-a-stream-of-sounds-to-actual-words-the-decoder)
9. [Step 6 — Squeezing out more: ensembles, n-best lists, and union](#9-step-6--squeezing-out-more-ensembles-n-best-lists-and-union)
10. [Step 7 — The language brain: LLM reranking (LIFT)](#10-step-7--the-language-brain-llm-reranking-lift)
11. [The complete journey of one sentence](#11-the-complete-journey-of-one-sentence)
12. [The historical arc: how we went from 51% to 18.5% wrong](#12-the-historical-arc-how-we-went-from-51-to-185-wrong)
13. [The honest limit: why it stops at 18.5%](#13-the-honest-limit-why-it-stops-at-185)
14. [Glossary — every term in one place](#14-glossary--every-term-in-one-place)

---

## 1. The one-paragraph picture

When you speak, your brain fires nerves that drive dozens of small muscles in your face,
jaw, and throat. Those muscles produce tiny electrical voltages on the surface of the skin.
A grid of 31 sensors on the face records those voltages thousands of times per second. The
system in this repository takes that raw electrical recording and, through a chain of stages,
turns it into a sentence of English text. The chain is:

> **muscle electricity → sensor recording → compact "fingerprint" features → a neural network
> that predicts speech sounds → a decoder that assembles sounds into real words → a panel of
> models that proposes many candidate sentences → a language model that picks the best one →
> final text.**

The best version of this system gets about **18.5% of words wrong** (we call this an 18.53%
*word error rate*). That sounds high until you remember the input is not sound at all — it is
muscle electricity, a far murkier signal than a microphone recording. The rest of this document
explains each link in that chain in detail.

---

## 2. What problem are we even solving?

### 2.1 Speech without (necessarily) sound

Most speech recognition you've used — phone dictation, voice assistants — listens to **audio**
from a microphone. This project does something different: it reads **surface electromyography**,
abbreviated **sEMG** or just **EMG**. EMG is the electrical activity of muscles, measured with
sensors (electrodes) placed on the skin.

The promise is large. If you can decode speech from the *muscle movements* of speaking rather
than from the *sound*, then you can eventually decode speech that makes **no sound at all** —
"silent speech," where a person mouths or sub-vocalizes words. That would help people who have
lost their voice (for example after a laryngectomy or due to ALS), and it would enable silent,
private communication with devices.

### 2.2 What this dataset actually contains

The data used here is the healthy-subject **"General Corpus"** from a public research release
called *emg2speech*. Its key properties:

- **One person.** All recordings are from a single healthy subject. This matters a lot later —
  it makes the task easier in one way (the model only has to learn one person's muscles) and
  harder to trust in another (we don't know if it generalizes to other people).
- **9,660 sentences** spoken in total (about 9,541 of them unique).
- **31 EMG channels**, each sampled at **5,000 times per second** (5 kHz). "Channel" just means
  one sensor; 31 sensors means 31 simultaneous streams of voltage readings.
- **Parallel audio.** Crucially, while the subject spoke, a microphone recorded the actual voice
  **at the same time**. So for every sentence we have *both* the muscle signal *and* the matching
  audio, perfectly time-aligned (their durations match to three decimal places).

That parallel audio is the system's secret weapon during **training** — it is a "teacher" the
EMG model can imitate. But the audio is a *training-time-only* crutch: at the end we also check
how well the system does *without* it, because in the real silent-speech application there is no
voice to record.

### 2.3 Important framing: this is "vocalized" EMG

The subject actually spoke out loud (vocalized), so the muscles were fully engaged. This is
easier than true silent speech, where muscle activity is fainter. The project is honest about
this throughout: it is a stepping stone toward silent speech, validated on the easier vocalized
case.

### 2.4 How we score success

Two numbers run through this entire project:

- **Word Error Rate (WER):** of all the words in the reference sentence, what fraction did the
  system get wrong (counting substitutions, insertions, and deletions)? Lower is better. This is
  the headline metric — it's what an end user cares about.
- **Phone Error Rate (PER):** the same idea but at the level of individual *speech sounds*
  (phonemes) instead of words, and measured **before** any dictionary or language model gets
  involved. PER is the honest, stripped-down measure of how well the neural network actually
  "hears" the sounds in the muscle signal. As you'll see, PER turns out to be the thing that
  ultimately limits the whole system.

The data is split into three fixed, non-overlapping parts, in recording order:
**8,500 sentences for training**, **760 for validation** (tuning knobs), and **400 for the final
held-out test**. Every adjustable setting is tuned on validation and then applied **once** to the
test set — this discipline is what makes the final numbers trustworthy rather than cherry-picked.

---

## 3. The raw material: electricity from muscles

### 3.1 Where the signal comes from, physically

A muscle contracts because nerve cells send it electrical commands. Those commands create small
voltage changes that spread through tissue and reach the skin, where electrodes can pick them up.
When you speak, the muscles around the mouth, jaw, cheeks, and throat perform an intricate,
fast-changing dance — and each spoken sound corresponds to a particular pattern of muscle
activity. EMG captures the electrical shadow of that dance.

The signal is **weak, noisy, and indirect**. Unlike a microphone, which captures the actual
pressure wave of your voice, EMG captures a side effect of the movements that *produce* the
voice. Many different muscles overlap; the electrodes pick up blends; and electrical noise from
the body and environment intrudes. Reading speech out of this is genuinely hard, and that
difficulty is the central theme of the whole project.

### 3.2 The shape of the raw data

For one spoken sentence, the raw recording is a block of numbers: **31 rows** (one per sensor)
and a very large number of columns — 5,000 columns for every second of speech. A three-second
sentence is therefore 31 × 15,000 numbers. This raw block is far too fine-grained and noisy to
feed directly to a model, so the first real job is to compress it into something compact and
meaningful. That is the next section.

---

## 4. Step 1 — Turning the wiggly signal into features

A neural network does not want 5,000 raw voltage readings per second per channel. It wants a
shorter sequence of compact, informative summaries. Converting raw signal into such summaries is
called **feature extraction**, and the choice of features is one of the most important design
decisions in the whole system.

### 4.1 First, tidy each channel

Before anything else, each of the 31 channels is **normalized** independently: the system
measures that channel's average level and its typical spread (standard deviation) across the
whole sentence, and rescales the channel so it has a neutral, comparable range. This stops a
sensor that happens to sit on a stronger muscle, or that has a different baseline, from
dominating just because its raw numbers are bigger. Now all 31 channels speak in the same units.

### 4.2 Chop time into overlapping windows

The continuous signal is sliced into short, overlapping **windows**:

- Each window is **25 milliseconds** long (125 raw samples at 5 kHz).
- A new window starts every **20 milliseconds** (a "hop" of 100 samples).

Because windows are 25 ms long but start every 20 ms, neighboring windows overlap by 5 ms, which
keeps the summary smooth from one moment to the next. The result is a steady drumbeat of one
window every 20 ms — that is **50 windows per second**, or "50 frames per second." From here on,
the unit of time in the system is the **frame** (20 ms), not the raw sample. A three-second
sentence becomes roughly 150 frames. This is the timeline the rest of the system runs on.

### 4.3 The key idea: describe each window by how the channels move *together*

Here is the clever part, and it is worth dwelling on. You might expect each window to be
summarized by *how strong* each channel is. Instead, the system summarizes each window by **how
the 31 channels relate to one another** — specifically, their **covariance**.

Covariance is a measure of co-movement. For any two channels, it asks: when one goes up, does the
other tend to go up too, go down, or move independently? For 31 channels there are 31 × 31 such
relationships (every channel paired with every other channel, including with itself). Arranged in
a grid, these relationships form a **31 × 31 covariance matrix** — one such matrix per 20 ms
frame.

Why covariance instead of raw strength? Because *which muscles activate together* is exactly what
distinguishes one speech gesture from another. A particular sound is produced by a particular
coordinated pattern of muscles, and covariance captures that coordination directly. It is also
naturally robust: it cares about the *pattern* of joint activity, not the absolute voltage, which
drifts and varies. This covariance representation comes from the original *emg2speech* research
and is reused here unchanged so that results are faithful to the source.

### 4.4 A stabilizing nudge: shrinkage

Covariance matrices estimated from a short 25 ms window can be statistically shaky — with only a
little data, the estimate is noisy and can be numerically ill-behaved. To fix this, the system
applies **shrinkage**: it blends the measured covariance (weighted 90%) with a simple, stable
"plain" pattern (weighted 10%) that assumes the channels are independent and equally strong. This
gentle pull toward a sensible default makes every frame's matrix well-behaved without erasing the
real structure. The 10% blend factor is a tuned constant.

### 4.5 A learned front-end that reads the matrices

Each 31 × 31 covariance matrix still has nearly a thousand entries — more than the model needs,
and in a raw form the model can't use directly. So a small **learned front-end** sits at the very
start of the neural network and converts each matrix into a compact **384-number summary vector**
(an "embedding") for that frame. This front-end does two thoughtful things:

- **Per-sensor normalization.** It normalizes the statistics of each sensor's contribution so the
  learning is stable.
- **Rotation invariance.** The electrodes are arranged in a ring/grid on the face, and exactly
  which physical sensor is "number 1" is somewhat arbitrary — shift the array slightly and the
  numbering rotates. The front-end is deliberately built so that nudging the sensor ordering by
  one position barely changes its output. It does this by looking at the matrix, a slightly
  shifted version, and another shifted version, processing all of them, and keeping the strongest
  response. This makes the features robust to small differences in how the electrodes sit — a real
  concern for EMG.

So the front-end converts the stream of covariance matrices into a stream of 384-number frame
embeddings. (This front-end is also reused from the original research, unchanged.)

### 4.6 Two small but important housekeeping details

- **Padding with "neutral" frames.** Sentences have different lengths, but the computer processes
  them in batches of equal-length blocks. Short sentences are padded out to the batch length using
  a "do nothing" pattern (the plain identity matrix), which the model learns to ignore. The model
  is always told each sentence's true length so the padding never corrupts the result.
- **EpochJitter augmentation.** Every time the model sees a sentence during training, the window
  grid is nudged by a small random time offset (somewhere between 0 and one hop). This means the
  exact frame boundaries land in slightly different places each pass, so the model sees many
  slightly-shifted versions of the same sentence over training. This discourages it from
  memorizing one rigid alignment and is a cheap, effective form of regularization.

**At the end of Step 1**, one spoken sentence has become a tidy sequence of frames at 50 frames
per second, each frame a 384-number embedding describing the coordinated muscle activity in that
20 ms slice. This is what the recognition model actually reads.

---

## 5. Step 2 — Deciding what the answer looks like: phonemes and units

Before we can build a model that predicts speech, we have to decide *what* it predicts. The
system does not jump straight to words. It predicts **speech sounds** first, for good reasons.

### 5.1 Why sounds, not letters or words

English spelling is a mess ("though," "tough," "through" rhyme with nothing and each other). The
muscle signal reflects how the mouth *moves*, which corresponds to how words *sound*, not how
they are *spelled*. And predicting whole words directly would force the model to know a fixed
vocabulary in advance, which breaks the moment a new word appears. Predicting sounds keeps the
model flexible: any word, even an unusual one, is just a new sequence of familiar sounds.

### 5.2 Phonemes

A **phoneme** is a basic unit of speech sound — the "k" sound, the "ee" sound, and so on. This
project uses the standard **ARPABET** set, which has about 40 distinct English phonemes. Every
reference sentence is converted from its written text into a sequence of phonemes by a
**grapheme-to-phoneme** ("g2p") tool, which is essentially a pronunciation dictionary with rules
for unknown words. Stress marks (which syllable is emphasized) are stripped, leaving a clean
sequence of around 40 possible sound symbols. This phoneme sequence is the model's primary
"answer key" during training.

### 5.3 HuBERT units — a second, richer answer key

The system also trains the model to predict a second kind of target: **HuBERT units**. These need
a little explanation. HuBERT is a well-known speech model that, by listening to enormous amounts
of audio with no labels, learned to cluster speech into **100 automatically-discovered sound
categories**. These 100 "units" are finer-grained and more acoustically detailed than the 40
phonemes — they capture nuances of sound that phonemes lump together. Pre-computed HuBERT unit
labels for every sentence ship with the corpus.

Why predict both? Predicting the 100 units gives the model a richer, more detailed target to
learn from (more signal to absorb), while predicting the 40 phonemes keeps it anchored to the
clean linguistic units the later stages need. The model has separate output "heads" for each, and
a gentle **consistency** rule links them: a fixed table encodes which phonemes correspond to which
units, and the model is nudged so that its unit predictions and phoneme predictions tell the same
story. The unit target is the heaviest-weighted of the recognition goals; the phoneme and
consistency goals are lighter supporting roles.

### 5.4 The "blank" symbol

Both answer sets get one extra symbol called **blank**. Blank means "no new sound is being emitted
right now." It is the linchpin of how the model handles timing, explained next.

---

## 6. Step 3 — The acoustic model: reading sound from muscle

This is the heart of the system: the neural network that takes the 50-frames-per-second muscle
features and predicts, for every frame, what speech sound is being made. It is called the
**acoustic model** (by analogy to speech recognition, even though our "acoustics" are muscles).

### 6.1 The alignment problem, and how CTC solves it

There is a deep difficulty here. We have ~150 frames of muscle features, and a reference of maybe
~30 phonemes. We do **not** know which frames correspond to which phoneme — nobody hand-marked
"the K sound runs from frame 12 to frame 18." Sounds also stretch and compress: the same word said
slowly or quickly produces different numbers of frames. So how do you train a model when you know
the *sequence* of correct sounds but not their *timing*?

The answer is a technique called **Connectionist Temporal Classification (CTC)**. The intuition:

- The model labels **every frame** with either a phoneme or the special **blank**.
- To read out the prediction, you collapse repeats and drop blanks. So if the model emits
  "blank, K, K, blank, AE, AE, AE, T, blank," you merge the repeated K's and AE's and remove the
  blanks to get "K AE T" — the word "cat."
- The clever bit: there are *many* frame-by-frame labelings that collapse to the same final
  sequence (the K could last three frames or five frames; the blanks could fall anywhere). CTC's
  training procedure efficiently sums over **all** of those valid alignments at once, so the model
  is rewarded for producing *any* timing that yields the right sequence. It never needs to be told
  the exact timing — it discovers it.

This is why "blank" exists: it lets the model say "I'm between sounds" or "I'm still holding the
previous sound," which is what makes flexible, alignment-free training possible. CTC is used for
both the phoneme target and the HuBERT-unit target.

### 6.2 The encoder: from causal to bidirectional

The part of the network that actually processes the sequence of frame embeddings and builds up an
understanding of context is the **encoder**. The project went through two encoder designs, and the
upgrade is one of the two biggest wins in the whole project.

- **The original (baseline) encoder** was a **causal** convolutional network (a "Time-Depth
  Separable" stack). "Causal" means each frame is understood using only the **past** — it never
  looks ahead. That is the right choice for *streaming* (real-time) systems that must emit words
  as you speak, but it is a handicap when you have the whole recorded sentence available and just
  want the most accurate transcription.

- **The improved encoder is a bidirectional Conformer.** Two ideas in that name:
  - **Bidirectional** means each frame is understood using **both past and future** context. To
    decide what sound is happening at frame 50, the model is allowed to look at frames before *and*
    after it — exactly what a human transcriber does when they replay a tricky moment. For offline
    transcription this is strictly better.
  - **Conformer** is a specific, powerful encoder design that combines two complementary mechanisms.
    **Self-attention** lets every frame directly compare itself to every other frame in the
    sentence and pull in whatever distant context is relevant (useful for long-range structure).
    **Convolution** captures fine local detail — how a frame relates to its immediate neighbors.
    By interleaving both, a Conformer models speech at every scale, from the texture of a single
    sound to the shape of the whole utterance.

The Conformer here is deliberately **small** — 4 layers, 4 attention "heads," a modest internal
size, and a local convolution that spans 31 frames. Why small? Because there is only one subject
and only 8,500 training sentences. A bigger network would simply memorize the training data and
fail on new sentences. Keeping it small, plus careful regularization, is the defense against that.

### 6.3 The output heads

After the encoder builds its frame-by-frame understanding, the signal passes through a small
compression block and then fans out into three **heads** (small output layers), each producing a
prediction for every frame:

- A **unit head** that scores the 100 HuBERT units (plus blank) at each frame.
- A **phoneme head** that scores the ~40 phonemes (plus blank) at each frame. This is the head the
  rest of the pipeline ultimately uses.
- A **projection head** that maps each frame into a 1,024-number space. This one isn't for
  recognition at all — it exists purely to imitate the audio teacher, which is the subject of the
  next section.

The phoneme head's output — a probability over phonemes for every 20 ms frame — is the central
product of the acoustic model. Everything downstream consumes it.

---

## 7. Step 4 — Learning from a real voice: cross-modal distillation

The single biggest reason this system works as well as it does is that during training the EMG
model gets to **imitate a model that listens to the real voice**. This is called **cross-modal
distillation** — "cross-modal" because it bridges two different signals (muscle and audio), and
"distillation" because knowledge is poured from a strong teacher into a student.

### 7.1 The teacher: a self-supervised audio model (WavLM)

Recall that every sentence has a parallel audio recording. The system runs that audio through
**WavLM-Large**, a large, pre-trained speech model. WavLM was trained on a huge amount of audio in
a **self-supervised** way — meaning it learned the structure of speech on its own, by predicting
hidden parts of audio, without anyone labeling it. As a result, its internal representations are
an extraordinarily rich description of "what speech sounds like."

A model like WavLM has many internal layers, and different layers capture different things — early
layers capture raw acoustic texture, late layers capture abstract meaning. The system uses
**layer 9** (a middle-upper layer) because it strikes the best balance: rich in *phonetic* content
(which sounds are present) without being so abstract that it drifts away from the signal. For every
one of the 9,660 sentences, the layer-9 representation of the audio is computed once and cached as
a sequence of 1,024-number vectors. This cached set is the **teacher signal**.

The goal: make the EMG model's projection head produce, frame by frame, something that matches the
audio teacher's layer-9 representation. If the muscle model can be pulled toward "what the real
voice's rich representation looks like," it inherits a great deal of the audio model's knowledge of
speech — for free, at training time.

### 7.2 The training objective, term by term

The model is trained by minimizing a combined objective made of several terms working together.
Three of them are the **recognition** terms carried over from the baseline; the others are the
**cross-modal** terms that pull the EMG model toward the audio teacher. In plain language:

1. **Predict the HuBERT units (the main recognition goal).** The heaviest term. The model's unit
   head must produce the right sequence of the 100 fine-grained sound units, judged by CTC.

2. **Predict the phonemes (a lighter recognition goal).** The model's phoneme head must produce the
   right phoneme sequence, also judged by CTC.

3. **Stay consistent (a lighter recognition goal).** Using the fixed phoneme-to-unit table, the
   model is nudged so its unit predictions and phoneme predictions agree with each other,
   emphasizing frames where it is confident an actual sound (not blank) is present.

4. **Match the audio teacher's representation directly (feature regression).** The projection
   head's output is pulled to be numerically close, frame for frame, to the audio teacher's
   layer-9 vectors. (Because the audio and EMG run at slightly different frame rates, the EMG side
   is stretched/compressed to line up in time before comparing.)

5. **Match it in a sharper, relative way (contrastive matching).** Being "close on average" is a
   weak goal — two very different patterns can still be numerically near each other. So a second
   term uses **contrastive learning**: for each EMG frame, the *correct* audio frame (the one at the
   same moment) must be pulled in as the clear best match, while all other frames are pushed away.
   This forces each EMG frame to be specifically, distinctively aligned to its own audio moment,
   not just vaguely similar to audio in general.

6. **Be phoneme-decodable, not just similar (the frozen-recognizer term — the load-bearing one).**
   This is the most important cross-modal term, and it deserves its own explanation, below.

### 7.3 Why the frozen-recognizer term is the crucial one

Imagine the EMG model learns to produce projection vectors that are *numerically close* to the
audio teacher's, but in a smooth, blurry way that has lost the crisp distinctions between similar
sounds. It could score well on "closeness" while being useless for actually telling sounds apart.
This is a real failure mode of naive imitation.

The fix is elegant. **Before** training the EMG model, the project trains a small, separate
recognizer that takes the audio teacher's layer-9 representation and predicts phonemes from it —
and trains it well, to roughly **10% phone error rate**. Then that recognizer is **frozen** (its
weights locked) and bolted onto the EMG model: the EMG projection is fed through this frozen
recognizer, and the EMG model is required to make the frozen recognizer output the correct
phonemes.

The effect: the EMG projection can no longer get away with being merely "close" to the audio
representation. It must carry enough genuine phonetic information that an *independent, fixed*
phoneme reader — one that was tuned for real audio — can correctly read phonemes out of it. In
other words, the EMG features must be **phoneme-decodable**, not just superficially similar. This
single constraint is what keeps the imitation honest and is highlighted in the report as the term
that distinguishes this approach from a plain imitation recipe.

### 7.4 Warm-starting

The new Conformer model does not start from nothing. Its front-end (the covariance-reading part)
and its output heads are **warm-started** — copied — from the trained baseline model, so they begin
already knowing how to read muscle features and produce sound predictions. Only the Conformer
encoder itself starts fresh and learns the new bidirectional contextual processing. This gives a
strong head start while still forcing the model to learn the genuinely new part.

### 7.5 The second model: an "anti-overfit augmented" variant

The system actually trains **two** acoustic models, which later get combined (Section 9). The
second is the same Conformer design but trained with heavier defenses against memorization — useful
precisely because there is only one subject and overfitting is a constant danger. Its extra
ingredients:

- **Stronger data augmentation on the covariance features.** During training it randomly: blanks
  out short stretches of time (forcing the model to cope with missing moments); drops a few sensors
  entirely (forcing it not to depend on any single electrode); adds small structure-preserving
  noise; and occasionally rotates the whole sensor frame of reference (mimicking the array sitting
  slightly differently). Each makes the model more robust and less able to memorize.
- **A second, stronger audio teacher.** Alongside the frozen phoneme recognizer, this variant also
  learns from a more powerful audio recognizer (a bidirectional recurrent network, a "BiLSTM,"
  reaching an even lower phone error rate). It provides **dense, frame-by-frame guidance**: for each
  frame, the EMG model is shown the teacher's full opinion over phonemes and nudged to match it,
  especially on frames where the teacher is confident a real sound is present.
- **Heavier dropout and early stopping** to further curb overfitting.

The two models — the cleanly-distilled one and the heavily-augmented one — make *different*
mistakes, and that diversity is exactly what makes combining them pay off later.

**At the end of Step 4**, we have one (or two) trained acoustic models that, for any new sentence,
output a frame-by-frame probability distribution over phonemes. The quality of *this* output —
measured by phone error rate — is the true ceiling on everything that follows.

---

## 8. Step 5 — From a stream of sounds to actual words: the decoder

The acoustic model gives us, for each 20 ms frame, a probability spread over the ~40 phonemes (and
blank). That is a *phonetic* description, not text. Turning it into real English words is the job
of the **decoder**, and doing it for an open vocabulary is genuinely intricate.

### 8.1 The problem the decoder solves

Three things have to happen at once:

1. **Collapse the frame stream into a phoneme sequence** (the CTC merge-repeats-and-drop-blanks
   idea), but accounting for *uncertainty* — the model isn't sure, so we shouldn't commit too early.
2. **Group phonemes into valid words.** "K AE T" should become "cat." This needs a pronunciation
   dictionary.
3. **Prefer plausible sentences.** "I scream" and "ice cream" sound identical; "recognize speech"
   and "wreck a nice beach" are close. Choosing between them needs knowledge of how English words
   usually follow one another.

### 8.2 What a WFST is, intuitively

The decoder does all three at once using a single large structure called a **weighted finite-state
transducer (WFST)**. You can picture a WFST as a giant map of roads. Each road (arc) you travel
consumes a bit of input (a phoneme) and may emit a bit of output (a word), and each road has a toll
(a weight, i.e., a cost or score). To decode a sentence is to find the cheapest legal route through
the map that is consistent with what the acoustic model heard. Because the map encodes *all* the
rules of pronunciation and word-sequencing, any route through it is guaranteed to be a real,
spellable, grammatical-ish sequence of words.

The specific map used here is built by composing three smaller maps into one, known as **HLG**:

- **H — the CTC topology.** Encodes the merge-repeats-and-drop-blanks bookkeeping, so the decoder
  correctly translates the frame-level predictions into phoneme sequences.
- **L — the lexicon.** The pronunciation dictionary: which sequences of phonemes spell which words.
  Here it is a large **34,546-word** dictionary derived from LibriSpeech (a standard speech corpus)
  — about five times the corpus's own vocabulary. Because the dictionary is so much larger than what
  appears in the data, the system is genuinely **open-vocabulary**: it can produce words it never
  saw during training. (A tiny fraction of test words — 12 out of ~2,400 — aren't even in this big
  dictionary, setting a small unavoidable error floor.)
- **G — the language model.** An **n-gram** model: a statistical table of how likely each word is to
  follow the previous few words in English (learned from large text). This is what lets the decoder
  prefer "ice cream" over "I scream" in the right context.

Composed together, HLG is one big graph that takes the acoustic model's phoneme probabilities in
and produces the most plausible **word sequence** out, simultaneously respecting CTC bookkeeping,
real pronunciations, and English word statistics. (Building and searching such a graph efficiently
is done with a specialized toolkit, k2/icefall.)

### 8.3 The two knobs that make or break the decode

A subtle but vital finding of this project is that good phoneme probabilities are *not enough* —
how you *configure the decode* matters enormously. Two settings dominate:

- **Acoustic scale — balancing the muscle evidence against the language model.** When searching the
  map, the decoder must weigh two sources: what the acoustic model heard, and what the language
  model thinks is plausible English. The acoustic scale is the dial that sets their relative trust.
  Turn it down and the language model dominates (the decoder leans on "what sounds like normal
  English"); turn it up and the acoustic evidence dominates (the decoder trusts the muscle reading
  even when it's unusual). Get this wrong and accuracy collapses — for instance, an untuned setting
  can push word errors above 75%. The right value is found on the validation set (around 0.25 for
  the Conformer) and then applied once to the test set.

- **Blank penalty — counteracting the model's overuse of silence.** CTC models are notoriously
  "blank-happy": they label most frames as blank with very high confidence (often above 90%),
  emitting actual sounds only in brief bursts. Left alone, the decoder over-trusts all that blank
  and skips real sounds. The blank penalty simply makes blank a little more "expensive" to choose,
  encouraging the decoder to commit to genuine phonemes. This is described in the report as the
  single largest lever on word accuracy — adjusting it alone moved word error from roughly 78% down
  to 61% in one early test.

### 8.4 The honest measuring stick: greedy phone error rate

Alongside the full decode, the system computes a deliberately dumb, decoder-free measure of the
acoustic model's quality: **greedy PER**. For each frame, just take the single most likely phoneme,
collapse repeats, drop blanks, and compare the result to the true phoneme sequence. No dictionary,
no language model, no tuning. Because it strips away everything except the model's raw phonetic
ability, greedy PER is the **cleanest, most trustworthy gauge of how well the muscle signal was
actually read** — and the project leans on it heavily as the un-foolable anchor. (As Section 13
explains, it is also the wall the whole system eventually hits.)

**At the end of Step 5**, the acoustic model + WFST decode already produces real transcriptions —
this is the **26.14% word error** single-model system. The remaining steps push it further.

---

## 9. Step 6 — Squeezing out more: ensembles, n-best lists, and union

The single decoded sentence is good, but two well-known techniques extract more accuracy from the
same acoustic models without retraining anything.

### 9.1 Ensembling two models

Recall the two acoustic models (the cleanly-distilled one and the heavily-augmented one), which
make different mistakes. For each frame, the system simply **averages their phoneme probabilities**
(in log form, which is the principled way to average probabilities). Where both models agree, the
average is confident; where they disagree, the average hedges. Because their errors are partly
independent, the combination is more reliable than either alone. Ensembling by itself drops word
error from about 26% to about 20% — a large gain for essentially free.

A telling detail: the ensemble's *phone* error rate barely changes from a single model's. The gain
comes from smoothing out decode-level disagreements, **not** from the models suddenly hearing the
sounds better. This is the first hint of the binding constraint discussed in Section 13.

### 9.2 N-best lists: keep several guesses, not just one

Until now the decoder produced the single best sentence. But the single best is often *almost*
right — the correct word might be the decoder's second or third choice. So instead of taking just
the top route through the WFST map, the system extracts the **top several dozen routes** per
sentence — a ranked list of candidate transcriptions called an **n-best list**. The correct
sentence is far more likely to appear *somewhere* in a list of 50–100 candidates than to be the
exact top one.

### 9.3 Multi-scale extraction and union

Here the project adds a twist. Remember the acoustic scale knob from Section 8.3 — the balance
between muscle evidence and language model. Different settings of that knob surface different good
candidates: a more language-model-leaning setting catches common, fluent phrasings, while a more
acoustic-leaning setting catches unusual words the language model would otherwise suppress. So the
system extracts n-best lists at **three different scale settings** and **unions** them — pools all
the candidates together, removing duplicates and keeping the best-scoring copy of each.

How good is this pooled list? We measure it with the **oracle word error rate** — a hypothetical:
*if a perfect genie always picked the single best candidate in the list for each sentence, how low
could the error go?* For the unioned, multi-scale list, the oracle is **9.30%**. That is the
crucial number: it means the right (or nearly-right) answer is *present in the candidate pool* for
the vast majority of sentences. The gap between that 9.30% oracle and the ~20% you get by always
taking the top candidate is the **headroom** — the prize available to a smart final chooser. That
chooser is the next step.

**At the end of Step 6**, for each sentence we have a pool of candidate transcriptions in which a
near-perfect answer almost always exists. We just need something clever enough to pick it.

---

## 10. Step 7 — The language brain: LLM reranking (LIFT)

The final stage uses a **large language model (LLM)** as the smart chooser. The technique is called
**LIFT** (LLM-improved recognition). The idea: a powerful language model has deep knowledge of how
English sentences are *supposed* to read, so it is well-suited to look at the candidate pool plus
the phonetic evidence and decide the most sensible final sentence.

### 10.1 Adapting a 7-billion-parameter model with QLoRA

The base model is **Qwen2.5-7B-Instruct**, a 7-billion-parameter instruction-following LLM. Such a
model is normally far too big to fine-tune on a 12 GB GPU. The project uses **QLoRA** to make it
feasible:

- **Quantization (the "Q").** The giant model's weights are compressed to a 4-bit format, shrinking
  its memory footprint enough to fit on a single modest GPU. These compressed weights are **frozen**
  — never changed.
- **Low-Rank Adaptation (the "LoRA").** Instead of retraining all 7 billion weights, LoRA inserts
  tiny, trainable "adapter" layers into the model and trains only those — a small fraction of the
  parameters. This is enough to teach the model the new task while leaving the vast frozen base
  intact. Training runs for a few passes over the data with standard settings.

The result is a specialized version of the LLM that has learned the specific job of cleaning up
this EMG recognizer's output.

### 10.2 What the LLM is actually asked to do

For each sentence, the fine-tuned model is given a prompt that contains:

- a short instruction explaining it is correcting the output of a silent-speech EMG recognizer;
- the **list of candidate transcriptions** (the top ~10 from the unioned n-best pool); and
- the **detected phoneme sequence** (the raw sounds the acoustic model read out).

It is asked to reply with the single most likely sentence. Crucially, it sees **both** kinds of
evidence: the word-level guesses *and* the underlying phonetic reading. Combining them is what lets
it sometimes do better than any single candidate — it can use the phonemes to adjudicate between
similar-sounding candidates.

### 10.3 Two ways to use it: free vs. constrained

The system supports two modes and picks the better one on the validation set:

- **Free generation.** The model *writes* its answer from scratch. This is powerful — it can in
  principle produce a correct sentence even if no candidate was exactly right — but it carries a
  risk: it could **hallucinate**, inventing a fluent sentence that drifts from what the muscles
  actually said.
- **Constrained selection.** The model is restricted to *picking* one of the existing candidates
  (it scores each candidate and chooses the one it finds most likely). This cannot hallucinate by
  construction — the output is always something the acoustic models genuinely proposed — but it can
  never recover a correct answer that simply isn't in the pool.

The choice between them is made by whichever scores better on validation, then applied once to test.

### 10.4 Why leakage control is taken so seriously

An LLM that has, in any way, *seen the test answers* would cheat — and there are several sneaky
ways that could happen. The project goes to unusual lengths to prevent it, and audits the result.
This rigor is a big part of why the final number is believable.

- **Train-only fine-tuning.** The LLM is fine-tuned exclusively on the training split. Validation
  and test sentences are never used to teach it.

- **Cross-decoding, to avoid "too-good" training candidates.** This is the subtle one. To fine-tune
  the LLM, you need example candidate-lists for training sentences. But if those lists were produced
  by an acoustic model that *trained on those very sentences*, the model would recognize them almost
  perfectly (near-1% error), and the candidate lists would be unrealistically clean. The LLM would
  then learn the wrong lesson — "the answer is always sitting right there at the top" — and fall
  apart on real, messier test candidates. The fix is **2-fold cross-decoding**: split the training
  data in half, train a model on each half, and use each model to generate candidates only for the
  half it did **not** see. Every training candidate-list then reflects realistic, never-memorized
  performance — exactly the kind of messy input the LLM will face at test time.

- **Quarantining test/train duplicates.** Six of the 400 test sentences happen to be exact text
  duplicates of training sentences. The results are reported both *with* and *without* those six
  (18.53% and 18.75%). Tellingly, removing them makes the score slightly *worse*, not better —
  proof the system isn't secretly leaning on memorized duplicates; they were simply easy sentences.

- **A hallucination audit.** For the free-generation mode, the project specifically checks how often
  the model produced a correct sentence that was **not** anywhere in its candidate pool — i.e., how
  often it "magically" conjured the right answer (which would indicate it had memorized text rather
  than reasoned from evidence). That count is **zero**. The model is genuinely reranking from the
  evidence it's given, not reciting.

**At the end of Step 7**, the system emits its final transcription, achieving **18.53% word error**
on the held-out test set — the headline result.

---

## 11. The complete journey of one sentence

Let's trace a single spoken sentence all the way through, to make the chain concrete.

1. **Speaking.** The subject says a sentence aloud. Muscles in the face and throat fire.

2. **Recording.** 31 skin electrodes capture the muscle voltages 5,000 times a second. A
   microphone simultaneously records the voice (used only later, for training the model — not at
   this point for this already-trained system).

3. **Tidying.** Each of the 31 channels is normalized to a common scale.

4. **Framing.** The continuous recording is chopped into overlapping 25 ms windows, one every
   20 ms — yielding 50 frames per second.

5. **Fingerprinting.** Each window is summarized not by raw strength but by the **covariance** —
   how the 31 channels move together — producing one 31×31 matrix per frame, gently stabilized by
   shrinkage.

6. **Embedding.** A learned, rotation-robust front-end turns each matrix into a compact 384-number
   summary. The sentence is now a tidy sequence of frame embeddings.

7. **Hearing.** The bidirectional Conformer acoustic model reads the whole sequence — looking both
   forward and backward — and outputs, for every frame, a probability spread over the ~40 phonemes
   (plus blank). (In the final system, two such models run and their outputs are averaged.)

8. **Assembling.** The WFST decoder takes those frame-level phoneme probabilities and finds the
   most plausible routes through its giant map of pronunciations (34,546-word dictionary) and
   English word-sequence statistics — balancing muscle evidence against language plausibility
   (acoustic scale) and resisting the model's overuse of blank (blank penalty). It returns not one
   but a **pool of ~dozens of candidate sentences**, gathered across several balance settings.

9. **Choosing.** A QLoRA-fine-tuned 7-billion-parameter language model reads the candidate pool plus
   the raw detected phonemes and outputs the single most sensible sentence.

10. **Result.** That sentence is the system's transcription. Across the 400-sentence test set,
    about 18.5% of words differ from the reference.

Every arrow in that chain is a deliberate design decision, and every one was validated against the
honest, decoder-free phone error rate so that gains are real and not artifacts of tuning.

---

## 12. The historical arc: how we went from 51% to 18.5% wrong

The project did not appear fully formed. It is a sequence of four clearly-attributed improvements,
each measured against the last. Understanding the arc explains *why* each piece exists.

### 12.1 Starting point — the published baseline (51.17% word error)

The original *emg2speech* research reported about **51% word error** on this EMG-to-text task. That
is the bar to beat, and the credibility benchmark.

### 12.2 Move 1 — fix the decode, faithfully (→ 40.63%)

The public release of the original work was missing the *decode-time* settings — the acoustic scale,
the blank penalty, a needed word-list file, and the rule for choosing which training checkpoint to
keep. Without them, even a perfectly good acoustic model produces poor words. The project recovered
these settings (tuning them honestly on validation) and reached **40.63% word error**.

The important part is *how* this gain was earned: the **phone error rate barely moved** and in fact
matched the original paper's (about 39% either way). Matching phone error rate is the proof of
faithfulness — it shows the acoustic model is reproduced exactly, and the entire 10-point word-error
improvement came purely from configuring the *decode* correctly, not from changing the model or
slipping in any advantage. This faithful baseline then serves as the warm-start for the next model.

### 12.3 Move 2 — a better acoustic model (→ 26.14%)

This is the largest single jump, and it has two parts working together (Sections 6 and 7):

- replacing the **causal** encoder with a **bidirectional Conformer** that can look both forward and
  backward; and
- training it with **cross-modal distillation** from the parallel audio (WavLM layer 9), including
  the crucial frozen-recognizer constraint that forces the EMG features to be genuinely
  phoneme-decodable.

Together these cut word error from 40.63% to **26.14%**, and — importantly — they also cut the
*phone* error rate (from ~39% to ~22%). This time the model really did learn to *hear* better, not
just decode better. A revealing control experiment: an EMG-only Conformer trained **without** the
audio teacher reaches almost the same word error (~26.1%). At the *word* level, the bidirectional
context is what mattered most; the audio teacher mainly sharpened the *phonetics*. That distinction
matters for the eventual silent-speech goal, where no audio teacher will be available.

### 12.4 Move 3 — ensemble, n-best union, and LLM reranking (→ 18.53%)

The final stage (Sections 9 and 10) stacks three ideas: average two diverse acoustic models
(~20%), pool their candidate sentences across multiple decode settings until a near-perfect answer
almost always sits in the pool (oracle 9.30%), and let a fine-tuned LLM pick the best candidate
using both word and phoneme evidence. The result is **18.53% word error** — the headline.

So the full arc is: **51.17 → 40.63 → 26.14 → 18.53**, with every step independently measured and
the trustworthy phone-error-rate anchor checked at each stage.

---

## 13. The honest limit: why it stops at 18.5%

A distinctive feature of this project is that it does not just report a good number — it carefully
diagnoses **why it can't do better**, and reaches a clear, somewhat sobering conclusion. This is
the project's most important scientific finding.

**The bottleneck is the acoustic phone error rate (~20.9%), not the language model.** The evidence:

- **The phone error rate refuses to move.** The anti-overfit augmentation, the stronger audio
  teacher, the ensembling — all of them improve *word* error, yet the model's raw phone error rate
  stays pinned near 20.9%. The interventions improve how candidates are *decoded and chosen*; they
  do **not** improve how well the muscle signal is actually *heard*.

- **The audio teacher can't transfer its quality.** Even though the audio teacher itself reads
  phonemes at ~10% error, the EMG model it teaches plateaus at ~21%. There is only so much phonetic
  precision that can be pulled from muscle signal into the EMG model; the gap to the audio teacher
  does not close.

- **A 9-point oracle gap that no reranker can close.** The candidate pool has a 9.30% oracle — a
  near-perfect answer is *usually* available. But for the sentences where the system still errs,
  the correct words are simply **absent** from the acoustic model's phoneme reading in the first
  place. There is nothing in the pool to select, and nothing to rerank toward. A free-generation
  LLM that "fixed" those would be hallucinating — and the audit confirms it does **not** (it never
  conjures answers that weren't supported by the evidence). The reranker is worth a real ~4–5 word-
  error points, but past 18.5% it is **exhausted**, because the limitation is upstream.

The conclusion: to push below ~10% word error, you must build a **better acoustic model** — one
that reads phonemes out of the muscle signal more accurately. That means more data, multiple
subjects, or a fundamentally stronger front-end that learns from the raw signal — **not** a bigger
or smarter language model. This is a negative result, but a valuable one: it tells future work
exactly where to spend effort.

(For context: the EMG-to-text task is intrinsically harder than reading audio. A ~21% phone error
rate on *muscle* signal corresponds to information that is simply blurrier than a clean microphone
recording. The whole downstream stack — decode tuning, ensembling, union, LLM reranking — is, in
effect, a very sophisticated way of getting the most words possible out of that fixed amount of
phonetic information.)

---

## 14. Glossary — every term in one place

- **sEMG / EMG (surface electromyography).** The electrical activity of muscles, recorded by
  electrodes on the skin. Here, the signal from speaking.
- **Channel.** One sensor/electrode's stream of readings. This system has 31.
- **Sampling rate (5 kHz).** How many times per second each channel is measured — 5,000 here.
- **Vocalized vs. silent speech.** This data is *vocalized* (spoken aloud, strong muscle activity).
  The long-term goal is *silent* speech (mouthed, fainter), which is harder.
- **Parallel audio.** A microphone recording made at the same time as the EMG; used only during
  training as a teacher signal.
- **Frame.** One 20 ms time slice of the signal. The system runs at 50 frames per second.
- **Window (25 ms) / hop (20 ms).** Each frame summarizes a 25 ms window; a new window starts every
  20 ms, so windows overlap slightly.
- **Covariance feature.** A 31×31 grid summarizing how the 31 channels move *together* within a
  window — the system's chosen "fingerprint" of muscle coordination.
- **Shrinkage.** Blending a noisy estimate toward a stable default; used to make each frame's
  covariance well-behaved.
- **Front-end.** The first learned layers that turn each covariance matrix into a compact 384-number
  embedding, with built-in robustness to electrode placement (rotation invariance).
- **EpochJitter.** Training-time augmentation that randomly shifts the window grid so the model
  sees many slightly different alignments of each sentence.
- **Phoneme.** A basic unit of speech sound (~40 in English, ARPABET set). The system's primary
  prediction target.
- **Grapheme-to-phoneme (g2p).** Converting written text into its phoneme sequence.
- **HuBERT unit.** One of 100 automatically-discovered, fine-grained sound categories learned by a
  self-supervised audio model; used as a richer secondary prediction target.
- **Blank.** A special "no new sound now" symbol that lets the model handle timing flexibly.
- **CTC (Connectionist Temporal Classification).** The training method that lets the model learn
  the sequence of sounds without being told their exact timing, by summing over all valid
  alignments. Reading it out means collapsing repeats and dropping blanks.
- **Acoustic model.** The neural network that turns muscle features into per-frame phoneme
  probabilities.
- **Encoder.** The core of the acoustic model that processes the frame sequence and builds context.
- **Causal vs. bidirectional.** Causal uses only past context (good for real-time); bidirectional
  uses past *and* future (better for offline transcription). The upgrade to bidirectional was a
  major win.
- **Conformer.** A strong encoder design combining self-attention (global context) with convolution
  (local detail).
- **Self-attention.** A mechanism letting every frame directly compare itself with every other frame
  and pull in relevant context from anywhere in the sentence.
- **Head.** A small output layer. This model has three: HuBERT units, phonemes, and the audio
  projection.
- **WavLM.** A large, self-supervised audio model whose internal layer-9 representation is used as
  the teacher signal.
- **Self-supervised learning.** Learning structure from unlabeled data by predicting hidden parts of
  the input; how WavLM and HuBERT were trained.
- **Cross-modal distillation.** Training the EMG (muscle) model to imitate a model that reads the
  parallel audio, transferring the audio model's knowledge of speech into the muscle model.
- **Feature regression / contrastive matching.** Two ways the EMG features are pulled toward the
  audio teacher: directly matching the numbers, and sharply matching each frame to its own audio
  moment while pushing others away.
- **Frozen recognizer (the load-bearing term).** A pre-trained, locked phoneme reader that the EMG
  features must satisfy, forcing them to be genuinely *phoneme-decodable*, not just superficially
  similar to the audio.
- **Warm-start.** Initializing parts of a new model by copying trained weights from a previous model.
- **Augmented model.** A second acoustic model trained with heavier anti-memorization defenses; its
  diverse errors make ensembling pay off.
- **Decoder.** The component that turns per-frame phoneme probabilities into actual words.
- **WFST (weighted finite-state transducer).** A graph ("map of roads with tolls") that encodes
  rules and costs; decoding is finding the cheapest legal route consistent with the acoustics.
- **HLG.** The composed decoding graph: **H** (CTC bookkeeping) ∘ **L** (pronunciation lexicon) ∘
  **G** (language model).
- **Lexicon (34,546 words).** The pronunciation dictionary; far larger than the corpus vocabulary,
  making the system open-vocabulary.
- **n-gram language model.** A statistical model of how likely each word is to follow the previous
  few; supplies English plausibility.
- **Open-vocabulary.** Able to output words never seen during training.
- **Acoustic scale.** The dial balancing trust in the muscle evidence vs. the language model during
  decoding. Must be tuned; getting it wrong wrecks accuracy.
- **Blank penalty.** A cost that discourages the decoder from over-using the model's many
  high-confidence blank predictions; described as the single biggest lever on word accuracy.
- **WER (word error rate).** Fraction of words wrong — the headline metric. Final system: 18.53%.
- **PER (phone error rate).** Fraction of phonemes wrong, measured without any decoder — the honest
  gauge of the acoustic model's quality, and the system's binding constraint (~20.9%).
- **Greedy decode.** Taking the single most likely option at each frame, with no graph or language
  model; how PER is measured.
- **Ensemble.** Averaging the per-frame phoneme probabilities of two diverse models for a more
  reliable result.
- **n-best list.** The top several dozen candidate transcriptions for a sentence, rather than just
  one.
- **Multi-scale union.** Pooling n-best lists produced at several acoustic-scale settings, removing
  duplicates, to widen the candidate pool.
- **Oracle WER (9.30%).** The error you'd get if a perfect genie always picked the best candidate in
  the pool — a measure of how often the right answer is *available* to be chosen.
- **LLM (large language model).** A model with deep knowledge of language; here used to choose the
  final sentence.
- **LIFT.** The technique of using an LLM to improve recognition output by reranking/correcting
  candidates.
- **QLoRA.** A memory-efficient fine-tuning method: compress the big model to 4 bits and freeze it
  (the "Q"), then train only small inserted adapter layers (the "LoRA"). Lets a 7-billion-parameter
  model be specialized on a single modest GPU.
- **Free vs. constrained reranking.** Free = the LLM writes its own answer (powerful, can
  hallucinate); constrained = the LLM must pick an existing candidate (safe, can't recover missing
  answers). The better of the two is chosen on validation.
- **Cross-decoding.** Generating the LLM's training candidates by having each half of the data
  decoded by a model that never trained on it — so the candidates are realistically imperfect, not
  memorized.
- **Leakage / verbatim-recall audit.** Checks that the system isn't secretly using test answers;
  the audit found the LLM never conjures correct answers absent from its evidence (count: zero).
- **Binding constraint.** The true bottleneck. Here it's the acoustic phone error rate (~20.9%):
  past a point, only a better-hearing acoustic model can improve results — not a better decoder or
  language model.

---

*Companion documents: [`technical_report.md`](technical_report.md) (the expert-facing results
report) and the project [`README.md`](../README.md) (how to run and reproduce everything).*
