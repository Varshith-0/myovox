# Myovox: Reading Speech from the Muscles of the Face

**Varshith Madishetty** · [madishettyvarshith@gmail.com](mailto:madishettyvarshith@gmail.com) ·
[github.com/Varshith-0/myovox](https://github.com/Varshith-0/myovox) ·
[varshith-0.github.io/myovox](https://varshith-0.github.io/myovox/)

Myovox, from *myo* (muscle) and *vox* (voice), decodes [open-vocabulary](#open-vocabulary) English text from 31-channel [surface electromyography (sEMG)](#semg-surface-electromyography) recorded from the muscles of the face during [vocalized speech](#vocalized-speech). It takes the single-subject *emg2speech* [General Corpus](#general-corpus) from a published 51.17% word error rate to 18.53%, in three separable moves, each measured in isolation. First, I recover the open-vocabulary decode settings missing from the public release and reach a faithful **40.63% [WER](#wer-word-error-rate) / 39.02% [PER](#per-phone-error-rate)** baseline whose phone error rate matches the published one to within 0.8 points, so the [acoustic model](#acoustic-model) is reproduced faithfully. Second, I replace the [causal](#causal-encoder) encoder with a [bidirectional](#bidirectional-full-context-encoder) [Conformer](#conformer) trained by a four-term [cross-modal distillation](#cross-modal-distillation) against the parallel audio's [WavLM-Large](#wavlm-wavlm-large-layer-9) layer-9 features, reaching **26.14% [WER](#wer-word-error-rate) / 22.34% [PER](#per-phone-error-rate)** from the [electromyography](#electromyography-emg) alone. Third, I [ensemble](#ensemble) two acoustic models, union their multi-scale [*n*-best](#n-best-list) lists, and [rerank](#reranking) with a [QLoRA](#qlora)-fine-tuned 7B [language model](#language-model), reaching **18.53% [WER](#wer-word-error-rate)**, the best result reported on this corpus, though not the best reported for sEMG-to-text on other corpora ([Section 2](#2-related-work)). I then report the negative result that bounds the whole approach: reranking is exhausted at 18.5% because the binding constraint is the electromyographic *acoustic* phone error rate (~20.9%), not the language model. The correct words are simply absent from the acoustic posteriors, so no reranker can reach the 9.30% *n*-best [oracle](#oracle-wer-n-best-oracle). All test numbers are on the 400-sentence held-out [test set](#test-set) under the authors' official 8,500 / 760 / 400 [sequential split](#sequential-split-8-500-760-400); every hyperparameter is tuned once on [validation](#validation-set) and applied once to test.

---

## 1. Introduction

When you speak, the decision to say a word reaches the muscles of your face, jaw, and throat long before any sound leaves your mouth. Those muscles fire, and the firing shows up as faint electrical voltages on the skin. Myovox reads that electricity. A grid of 31 sensors records the voltages a few thousand times a second, and a chain of models turns the recording into a line of English text. The name is literal: *myo* for the muscle, *vox* for the voice the muscle was reaching for.

The long-term goal of [electromyographic](#electromyography-emg) speech decoding is to help people who cannot speak because of conditions such as ALS or a laryngectomy. This report does not demonstrate that. Myovox was trained entirely on a healthy speaker who vocalized normally, so I cannot claim that it works for people who have lost their voice. What I can say is that it demonstrates a different use case: allowing a healthy person to communicate without producing audible speech, where the intention to speak is decoded from facial muscle activity instead of sound. I view this as a stepping stone toward true [silent-speech](#silent-speech) systems rather than the destination.

The report is organized around a single discipline: start from a strong published result, and measure the effect of each change in isolation before applying the next. That is what makes the final number decomposable into a decode fix, a modeling gain, and an extraction gain, rather than a single undifferentiated delta. The starting point is the *emg2speech* work of Gowda et al. [[1](#ref-1)], whose Appendix D.4 (“emg2text”) reports 51.17% [WER](#wer-word-error-rate) and 38.19% [PER](#per-phone-error-rate) on the General Corpus. The three sections that follow trace three moves: a decode correction that recovers most of the published gap while matching the original phone error rate ([Section 4](#4-baseline-reproduction-and-a-decode-correction)); a full-context acoustic model trained to imitate the parallel audio ([Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)); and a decode-time stack of ensembling, *n*-best union, and language-model reranking ([Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker)). [Table 1](#table-1-the-whole-report-in-one-table) is the whole story in one place. [Section 7](#7-why-it-stops-at-18-5) carries the report's main finding: why the system stops improving at 18.5%, and where the next gain has to come from. Terms of art are collected in the Glossary ([Section 10](#10-glossary)), and every occurrence of a glossary term in the text links to its entry; the objections the project actually drew are answered in [Section 11](#11-frequently-asked-questions).

Two numbers run through everything. *[Word error rate](#wer-word-error-rate)* ([WER](#wer-word-error-rate)) is what a reader cares about: the fraction of words wrong after substitutions, insertions, and deletions. *[Phone error rate](#per-phone-error-rate)* ([PER](#per-phone-error-rate)) is the honest gauge of the acoustic model: the fraction of [phonemes](#phoneme-phone) wrong, measured by [greedy decoding](#greedy-decoding) with no [lexicon](#lexicon) and no language model. [PER](#per-phone-error-rate) cannot be improved by a better decoder or a better language model. As it turns out, [PER](#per-phone-error-rate) is what limits the entire system.

##### Table 1. The whole report in one table.

All test numbers are on the 400-sentence held-out set under the authors' 8,500 / 760 / 400 sequential split. [PER](#per-phone-error-rate) is the decoder-independent greedy CTC phone error rate. Bold marks each stage's headline word error rate.

| # | System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|---|
| — | Gowda et al., Appendix D.4 (target) [[1](#ref-1)] | n/a | n/a | 51.17 | 38.19 |
| 1 | Causal TDS + dual-CTC, *corrected* decode | 53.12 | 45.31 | **40.63** | 39.02 |
| 2 | Bidirectional Conformer + WavLM-L9 distillation | 35.54 | 27.47 | **26.14** | 22.34 |
| 3 | Ensemble → *n*-best union → LIFT rerank | n/a | n/a | **18.53** | 20.90 † |

> †Phone error rate of the acoustic [ensemble](#ensemble) beneath the pipeline. Reranking operates on words and cannot change [PER](#per-phone-error-rate), which is precisely the point of [Section 7](#7-why-it-stops-at-18-5).

---

## 2. Related work

Two non-invasive routes lead from a person's intention to speak to a line of text, and they differ in where along the motor chain they tap. *Surface electromyography* reads the muscles of the face and neck as they articulate, which is the last link before sound. *Electro- and magnetoencephalography* read cortex, which is many links earlier. Myovox belongs to the first family. [Table 2](#table-2-non-invasive-speech-and-language-decoding-grouped-by-corpus) places it against both. Invasive intracortical decoders are excluded throughout: they are the performance ceiling, but they are not an alternative Myovox competes with.

**Surface EMG to text: the Gaddy line.** The reference corpus for open-vocabulary sEMG speech decoding is the one released by Gaddy and Klein [[2](#ref-2)]: eight facial channels at 1 kHz, roughly nineteen hours from a single English speaker, recorded in both [silent](#silent-speech) and [vocalized](#vocalized-speech) modes with audio available for the vocalized half. Their first system synthesized speech from silent EMG and was scored by transcribing that speech; a Transformer front-end and an auxiliary phoneme loss then cut the open-vocabulary error substantially [[3](#ref-3)]. Gaddy's thesis [[4](#ref-4)] moved from synthesis to direct EMG-to-text and set the prior state of the art at 28.8% [WER](#wer-word-error-rate) on silent EMG and 23.3% on vocalized EMG. MONA LISA [[5](#ref-5)] then combined cross-modal alignment (a contrastive objective binding EMG and audio latents, plus training on audio-only LibriSpeech) with an LLM reranker, and reached **12.2% [WER](#wer-word-error-rate) on silent EMG and 3.7% on vocalized EMG**. Both halves of that system have direct descendants here: the [cross-modal distillation](#cross-modal-distillation) of [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio) and the [LIFT](#lift-dcond-lift-style)-style reranker of [Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker). A recent line asks the harder question of what is achievable from unvoiced EMG with no paired voiced recordings or audio at all [[6](#ref-6)], which is the setting a patient would actually present.

**Myovox is not the best sEMG-to-text system; it is the best one on this corpus.** This distinction matters enough to state before the table rather than after it. MONA LISA's 3.7% on vocalized EMG is 15 points better than the 18.53% reported here, and it was obtained two years earlier. The two numbers are not measured on the same recordings and are not directly comparable: the Gaddy corpus is eight channels and about nineteen hours with both speaking modes from one speaker, while the *emg2speech* [General Corpus](#general-corpus) is 31 channels and 9,660 sentences from a different speaker in one mode; MONA additionally trains against an audio-only corpus that Myovox does not use. What can be said cleanly is narrower: on the *emg2speech* General Corpus, 18.53% is the best result I am aware of, against a published 51.17%. Whether the residual gap to MONA is a property of the corpus, of the [covariance front-end](#shrinkage-covariance-the-vec-e-front-end), or of the model is precisely what a single corpus cannot resolve; [Q3](#q3-mona-lisa-reported-3-7-wer-on-vocalized-emg-in-2024-why-is-your-number-five-times-worse) takes the question up directly.

**Non-invasive brain to text.** The parallel effort decodes cortex rather than muscle. Brain2Qwerty [[7](#ref-7)] decoded typed sentences from 35 volunteers, reaching a 32% [CER](#cer-character-error-rate) from MEG and 67% from EEG. Its successor [[8](#ref-8)] scaled the data to roughly 22,000 sentences across nine subjects and reached 39% [WER](#wer-word-error-rate) from MEG. Two things about it are worth a reader's attention here. The first is architectural convergence: independently of this work, that system also settles on a [Conformer](#conformer) encoder trained with [CTC](#ctc-connectionist-temporal-classification) and a [LoRA](#lora-low-rank-adaptation)-fine-tuned LLM on top: the same two components as Sections [5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio) and [6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker), arrived at from a different signal. The second is that it independently reproduces the finding of [Section 7](#7-why-it-stops-at-18-5). Their encoder alone reaches 55% [WER](#wer-word-error-rate); an *n*-gram [language model](#language-model) takes it to 43%; the fine-tuned LLM takes it to 39%. There, the LLM *worsens* the character-level metric (31% [CER](#cer-character-error-rate) against the encoder's 28%) even as it improves the word-level one, and the authors conclude that final performance is dominated by upstream encoder quality. What transfers to [Section 7](#7-why-it-stops-at-18-5) is that conclusion, not the mechanism, and the difference is worth stating: their LLM generates the sentence autoregressively and is conditioned on MEG-derived word embeddings as well as on the encoder's characters, so it can and does degrade the character metric, whereas the reranker of [Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker) sits downstream of the greedy CTC output and cannot move [PER](#per-phone-error-rate) at all. Their own text-only ablation, which leaves the LLM nothing but the encoder's characters, is the closer analogue, and it is worth about six [WER](#wer-word-error-rate) points over the encoder alone. Either way a language model bolted onto a weak encoder buys a bounded, single-digit number of [WER](#wer-word-error-rate) points. That is the same wall, found on a different signal.

##### Table 2. Non-invasive speech and language decoding, grouped by corpus.

Numbers are as reported by each work and are *not* comparable across groups: corpora, electrode counts, speaking modes, subject counts, and metrics all differ. “Aud.” marks whether parallel or external audio is used as a training signal (never at inference). Invasive intracortical systems are omitted by design.

| System | Mode | Vocab | Aud. | WER ↓ | PER ↓ | CER ↓ |
|---|---|---|---|---|---|---|
| **Facial sEMG → text: Gaddy corpus** (8 ch, 1 kHz, ~19 h, 1 speaker) [[2](#ref-2)] | | | | | | |
| Gaddy & Klein 2020 [[2](#ref-2)] \* | silent | open | ✓ | 68.0 | – | – |
| Gaddy & Klein 2021 [[3](#ref-3)] \* | silent | open | ✓ | 42.2 | – | – |
| Gaddy 2022 [[4](#ref-4)] | silent | open | ✓ | 28.8 | – | – |
| Gaddy 2022 [[4](#ref-4)] | vocalized | open | ✓ | 23.3 | – | – |
| MONA LISA [[5](#ref-5)] | silent | open | ✓ | 12.2 | – | – |
| MONA LISA [[5](#ref-5)] | vocalized | open | ✓ | **3.7** | – | – |
| **Facial sEMG → text: emg2speech General Corpus** (31 ch, 5 kHz, 9,660 sentences, 1 speaker) [[1](#ref-1)] | | | | | | |
| Gowda et al. 2026, App. D.4 [[1](#ref-1)] | vocalized | open | ✓ | 51.17 | 38.19 | – |
| Myovox, corrected decode (§4) | vocalized | open | ✓ | 40.63 | 39.02 | – |
| Myovox, Conformer + distillation (§5) | vocalized | open | ✓ | 26.14 | 22.34 | – |
| Myovox, Conformer, EMG-only (§5) | vocalized | open | – | 26.10 | 23.71 | – |
| **Myovox, full pipeline (§6)** | vocalized | open | ✓ | **18.53** | 20.90 † | – |
| **Non-invasive brain → text** (typed sentences, healthy volunteers) | | | | | | |
| Brain2Qwerty v1, EEG [[7](#ref-7)] | typing | open | – | – | – | 67 |
| Brain2Qwerty v1, MEG [[7](#ref-7)] | typing | open | – | – | – | 32 |
| Brain2Qwerty v2, MEG [[8](#ref-8)] | typing | open | – | 39 | – | 31 |

> \*These two systems *synthesize speech* and are scored by transcribing the synthesized audio, so their [WER](#wer-word-error-rate) is an intelligibility measure rather than a direct text-decoding score. Brain2Qwerty v1 reports only [CER](#cer-character-error-rate); v2 reports both. Brain2Qwerty v1 averages 35 subjects (19% [CER](#cer-character-error-rate) for the best); v2 averages 9 subjects (22% [WER](#wer-word-error-rate) for the best). †The [PER](#per-phone-error-rate) of the acoustic [ensemble](#ensemble) beneath the full pipeline, not of the pipeline: reranking operates on words and cannot change [PER](#per-phone-error-rate).

**What is new here.** Against that background, this report contributes three things, none of which is a new architecture. It supplies the open-vocabulary [decode settings](#blank-symbol-and-blank-penalty) missing from the *emg2speech* release, without which that release decodes at roughly 75% [WER](#wer-word-error-rate) rather than the 40.63% reported here, and shows by a matched [phone error rate](#per-phone-error-rate) that the acoustic model is unchanged ([Section 4](#4-baseline-reproduction-and-a-decode-correction)). It prints a control that undercuts its own favoured component: an encoder trained on [electromyography](#electromyography-emg) alone matches the audio-distilled one at the word level, so the parallel audio is not a hidden crutch beneath the headline number ([Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)). And it locates, with three independent lines of evidence, the point at which decode-time machinery stops paying ([Section 7](#7-why-it-stops-at-18-5)).

---

## 3. The data

The recordings are the healthy-subject *[General Corpus](#general-corpus)* from the *emg2speech* release. Its properties are summarized in [Table 3](#table-3-the-emg2speech-general-corpus). Three facts about it shape the rest of the report.

**It is one person.** The entire system is trained and evaluated on recordings from a single healthy speaker. I therefore do not know how well it generalizes to other people, anatomies, or speaking styles. The results in this report should be read as a demonstration of what is possible for one speaker, not as evidence that the same performance will transfer to others.

**It has parallel audio.** While the subject spoke, a microphone recorded the voice at the same time; per-sentence electromyography and audio durations correlate at 1.000. That audio is the training signal I lean on hardest in [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio). It is also a crutch that will not exist at [silent-speech](#silent-speech) inference, so I treat it as a training-time-only teacher and, at the end, check how much the system depends on it.

**It is open-vocabulary.** The decoder works over a 34,546-word [LibriSpeech](#librispeech)-derived [lexicon](#lexicon) [[9](#ref-9)], roughly five times the corpus vocabulary, so the system can emit words it never saw in training. Twelve of the 2,429 test tokens fall [outside the lexicon](#oov-out-of-vocabulary), a 0.49% [WER](#wer-word-error-rate) floor that no amount of modeling can remove.

##### Table 3. The *emg2speech* General Corpus..

| Property | Value |
|---|---|
| Sentences | 9,660 (9,541 unique) |
| Subject | single, healthy |
| Electromyography | 31-channel surface array, 5 kHz |
| Parallel audio | recorded simultaneously (per-sentence duration correlation = 1.000) |
| Train / val / test | 8,500 / 760 / 400, sequential |

The [split](#sequential-split-8-500-760-400) is the authors' own, taken in recording order. I keep it exactly. Every knob in this report is tuned on the 760 [validation](#validation-set) sentences and then applied, once, to the 400 [test](#test-set) sentences. That discipline is the only thing that makes the final number mean anything.

---

## 4. Baseline: reproduction and a decode correction

**The acoustic model, unchanged.** I keep the authors' [acoustic model](#acoustic-model) as released. The features are a [shrinkage covariance](#shrinkage-covariance-the-vec-e-front-end) of the 31 channels (the vec(E) representation whose geometry Gowda et al. develop in their articulation-decoding work [[10](#ref-10), [11](#ref-11)]), taken over a 25 ms [window with a 20 ms hop](#frame-window-hop), giving 50 frames per second. The encoder is the released `DualHeadTDSCTC`: a [causal](#causal-encoder) [time-depth-separable convolution](#tds-time-depth-separable-convolution) [[12](#ref-12)] with two [CTC](#ctc-connectionist-temporal-classification) heads [[13](#ref-13)], one predicting 100 [HuBERT](#hubert) [units](#hubert-unit) [[14](#ref-14)] and one predicting 40 [phonemes](#phoneme-phone), coupled by a fixed P(phone | unit) [consistency table](#consistency-table). The training loss is `0.8 · CTC_unit + 0.1 · CTC_phone + 0.1 · consistency`, a [dual-CTC](#dual-ctc) objective. Phoneme posteriors are turned into words by an open-vocabulary [weighted finite-state transducer](#wfst-weighted-finite-state-transducer), [HLG](#hlg) = H ∘ L ∘ G, built with [k2 and icefall](#k2-and-icefall) [[15](#ref-15)]. It is the same graph the authors use, which is why my phone error rate can be compared to theirs directly.

**What was missing.** The public notebooks reproduce the model but not the decode. They omit the handful of decode-time settings that separate good posteriors from good words, and without them the released configuration decodes at roughly 75% [WER](#wer-word-error-rate). Four things were missing, in rough order of importance.

1. **[Blank penalty](#blank-symbol-and-blank-penalty).** CTC posteriors are dominated by the blank symbol (peak ≈ 0.92), and the release applies no penalty at all. On the first 200 validation sentences at scale 1.0, sweeping the penalty from 0 to 2 drops [WER](#wer-word-error-rate) from 77.6% to 60.6%. This is the single largest lever in the entire baseline.
2. **[Checkpoint selection](#checkpoint-selection) by validation [PER](#per-phone-error-rate)**, rather than by validation CTC loss, which moves test [PER](#per-phone-error-rate) from 42.9% to 39.0%.
3. **A missing `words.txt`**, which I regenerated from `lexicon.txt`.
4. **[Acoustic scale](#acoustic-scale).** The weight on the acoustic scores relative to the language model is unspecified in the release, which decodes at the default of 1.0. Tuning it on validation returns 1.0 for this baseline, so it buys nothing here. It matters for the Conformer of [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio), where validation selects 0.25. I list it because the right value is not the same for both encoders, so a reader reproducing the decode has to set it deliberately rather than inherit it.

I tuned the (blank, scale) pair jointly on validation and applied (2.0, 1.0) once to test.

**Result.** [Table 4](#table-4-baseline-reproduction) is the outcome. The corrected decode reaches 40.63% [WER](#wer-word-error-rate) / 39.02% [PER](#per-phone-error-rate) on test: 10.5 [WER](#wer-word-error-rate) points below the published number, with the phone error rate matched to within 0.8 points (39.0 against 38.2). That matched [PER](#per-phone-error-rate) is the point of this section. Phone error rate is decoder-independent, so if it lands on the published value then the acoustic model has been reproduced faithfully, and the entire [WER](#wer-word-error-rate) gain is attributable to a correctly specified open-vocabulary decode rather than to any change in the model. Note that the published 51.17% is not itself recoverable from the public release, which decodes at roughly 75%; the comparison rests on the matched phone error rate, not on a reproduced [WER](#wer-word-error-rate). This checkpoint is the [warm start](#warm-start) for the encoder in the next section.

##### Table 4. Baseline reproduction.

The [WER](#wer-word-error-rate) gain over the published number comes entirely from the decode; the phone error rate is matched, not beaten, which is the credibility argument. Bold marks this section's headline number.

| System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|
| Gowda et al., Appendix D.4 [[1](#ref-1)] | n/a | n/a | 51.17 | 38.19 |
| TDS + dual-CTC, corrected decode (this work) | 53.12 | 45.31 | **40.63** | 39.02 |

---

## 5. The acoustic model: a full-context Conformer taught by the audio

Two changes take the baseline from 40.63 / 39.02 to 26.14 / 22.34: giving the encoder full context, and teaching it to imitate the parallel audio.

**Full context.** The released [time-depth-separable](#tds-time-depth-separable-convolution) encoder is [causal](#causal-encoder): it left-pads by kernel − 1 and never looks ahead. That is the right choice for [streaming](#streaming) and the wrong one for offline transcription, where the whole sentence is available at once. I replace it with a [bidirectional](#bidirectional-full-context-encoder) [Conformer](#conformer) [[16](#ref-16)]: four layers of [multi-head self-attention](#multi-head-self-attention) interleaved with [depthwise convolution](#depthwise-convolution) (four heads, feed-forward width 1024, convolution kernel 31). The covariance front-end, the two CTC heads, and the audio projection [warm-start](#warm-start) from the baseline checkpoint of [Section 4](#4-baseline-reproduction-and-a-decode-correction); the Conformer itself trains from scratch.

**A four-term cross-modal objective.** Only a better acoustic model lowers phone error rate, so this is where I spent the effort. I pull the electromyographic encoder toward the parallel audio's [WavLM-Large](#wavlm-wavlm-large-layer-9) layer-9 features [[17](#ref-17)], precomputed once for all 9,660 sentences, through a single linear projection into WavLM's 1024-dimensional space. The construction is inspired by the [cross-modal](#cross-modal-distillation) approach of Benster et al. [[5](#ref-5)]. On top of the three acoustic terms from the baseline, the objective adds three [distillation](#distillation) terms:

```text
L =  0.8·CTC_unit + 0.1·CTC_phone + 0.1·cons.  +  0.5·L_L2 + 0.5·L_InfoNCE + 1.0·L_rec^CTC
     └─────── acoustic (as in the baseline) ───┘  └────── cross-modal distillation ───────┘
```

The three new terms are: (i) a masked, frame-resampled L2 regression of the projection onto WavLM layer-9; (ii) a frame-synchronous [InfoNCE](#infonce) contrast [[18](#ref-18)] (τ = 0.1) that sharpens each frame toward its own audio moment and away from the others; and (iii) a CTC loss through a small, *[frozen](#frozen-model)* WavLM-to-phoneme recognizer (LayerNorm, two 1-D convolutions, a linear layer to 41 classes; trained to ~10% [PER](#per-phone-error-rate) and then frozen).

Term (iii) is the one that earns its place relative to a plain feature-matching setup. The L2 and contrastive terms pull the projection *close* to WavLM, but close is not the same as useful: a projection can be smooth and audio-like and still not be phoneme-decodable. Forcing the projection through a frozen recognizer that already reads phonemes out of real audio makes “close” mean “decodable into the right phonemes.” It guards the regression against smooth-but-empty blur.

**Result, and a control that surprised me.** [Table 5](#table-5-the-acoustic-model) gives the outcome, with validation-tuned [scale](#acoustic-scale) 0.25. The full-context, distilled Conformer reaches 26.14% [WER](#wer-word-error-rate) / 22.34% [PER](#per-phone-error-rate) on test, acoustic-only: a gain of 14.49 [WER](#wer-word-error-rate) and 16.68 [PER](#per-phone-error-rate) points over the baseline, present in the greedy phone error rate with no language model involved, and significant under a [paired bootstrap](#paired-bootstrap). The control is the interesting part. An otherwise identical Conformer trained on electromyography alone, with no audio distillation at all, reaches 26.10% [WER](#wer-word-error-rate), indistinguishable from 26.14%. At the word level the audio teacher buys essentially nothing. The distillation does help phone error rate (22.34 against 23.71), but it is the full-context encoder, not the audio crutch, that moves [WER](#wer-word-error-rate). That is good news for the silent-speech setting, where the parallel audio will not be available.

##### Table 5. The acoustic model.

The full-context encoder is what moves [WER](#wer-word-error-rate). The audio distillation helps [PER](#per-phone-error-rate), but at the word level an encoder trained on electromyography alone matches it. Bold marks this section's headline number.

| System | val WER | val PER | **TEST WER** | **TEST PER** |
|---|---|---|---|---|
| Baseline (causal TDS, Section 4) | 53.12 | 45.31 | 40.63 | 39.02 |
| Bidirectional Conformer + WavLM-L9 distillation | 35.54 | 27.47 | **26.14** | 22.34 |
| Conformer, electromyography-only (no audio) | n/a | n/a | 26.10 | 23.71 |

---

## 6. The final pipeline: ensemble, union, and a language-model reranker

The last stretch is all decode-time. The acoustic model does not change; what changes is how much is squeezed out of it.

**An acoustic ensemble.** I [average the per-frame phone log-probabilities](#ensemble) of two encoders: the distilled Conformer of [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio), and a second Conformer trained with heavier anti-overfitting defenses (stronger jitter and dropout, plus a [BiLSTM](#bilstm) audio-teacher frame-level KL). Averaging the two alone takes test [WER](#wer-word-error-rate) from 26.14 to 23.47 at the best of the [acoustic scales](#acoustic-scale) swept, the ensemble decoding between 23.5% and 25.1% across them. Worth noting for later: the augmented member's phone error rate is no better than the distilled member's, and averaging the two lowers greedy [PER](#per-phone-error-rate) to 20.9%, 1.4 points below either member. The gain is modest either way: 2.7 [WER](#wer-word-error-rate) points at best, against the 14.49 that full context bought in [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio). How much of it follows from the improved argmax and how much from decode-level diversity is taken up in [Q13](#q13-distillation-bought-1-4-points-of-per-and-no-wer-at-all-the-ensemble-bought-1-4-points-of-per-and-2-7-wer-why-the-difference).

**Multi-scale *n*-best union.** From the ensemble's [lattice](#lattice) I extract [*n*-best lists](#n-best-list) at several [acoustic scales](#acoustic-scale) and take their union. The union lowers the [*n*-best oracle [WER](#wer-word-error-rate)](#oracle-wer-n-best-oracle), the score a perfect judge would obtain by always picking the best candidate in the pool, from 11.94% for the best single-scale list to 9.30%, while the union's single-best candidate sits at 23.26%. The gap between 23.26 and 9.30 is the headroom a [reranker](#reranking) can, in principle, recover: the reranker below takes 4.7 points of it, and [Section 7](#7-why-it-stops-at-18-5) explains why the remaining nine are out of reach.

**The LIFT reranker.** I [fine-tune](#fine-tuning) [Qwen2.5-7B-Instruct](#qwen2-5-7b-instruct) [[19](#ref-19)] with [QLoRA](#qlora) [[20](#ref-20)] (4-bit NF4 plus a rank-16 [LoRA](#lora-low-rank-adaptation) adapter [[21](#ref-21)]) to map *(candidate list + detected phonemes)* to the reference, in the [DCoND-LIFT](#lift-dcond-lift-style) style [[22](#ref-22), [5](#ref-5)]. Two variants are chosen on validation. The *free* variant writes its own correction, which lets it recover a candidate that is close but wrong, at the cost of being able to hallucinate. The *constrained* variant must pick an existing candidate, so it cannot hallucinate, but neither can it rescue an answer that was never proposed.

[Leakage](#leakage) is the obvious risk with a language model on a single-subject corpus, so I built three controls before trusting the number. The reranker is trained only on the training split, and its training candidates are produced by two-fold [cross-decoding](#cross-decoding-two-fold): each half of the training data is decoded by a model that did not train on it, so the candidates look like realistic errors rather than the memorized ~1% [WER](#wer-word-error-rate) the model achieves on its own training set. Six of the 400 test sentences are exact-text duplicates of training phrases, so I report the score both with and without them (18.53 against 18.75). And a [verbatim-recall audit](#verbatim-recall-audit) measures how often free generation produces a reference that was *absent* from the candidate set: the count is zero, so no training text is leaking through the language model.

##### Table 6. The final pipeline.

Both bootstrap confidence intervals exclude zero, so the rerank gain is significant. The nine-point gap between the oracle and the achieved [WER](#wer-word-error-rate) is the subject of [Section 7](#7-why-it-stops-at-18-5).

| Metric | Value |
|---|---|
| **Test WER (LIFT)** | **18.53** |
| Test WER, excluding 6 duplicates | 18.75 |
| Union 1-best WER (no rerank) | 23.26 |
| *n*-best oracle WER | 9.30 |
| Greedy PER (acoustic ensemble) | 20.90 |
| Verbatim-recall (leakage audit) | 0 |
| Paired bootstrap vs. 26.14 acoustic | ΔWER −7.6, 95% CI [−9.40, −5.90] |
| Paired bootstrap vs. union 1-best (23.26) | ΔWER −4.7, 95% CI [−6.22, −3.29] |

[Table 6](#table-6-the-final-pipeline) collects the result: 18.53% [WER](#wer-word-error-rate), with the reranker worth −4.7 [WER](#wer-word-error-rate) points over the union's single-best output of 23.26%, and both bootstrap intervals well clear of zero.

---

## 7. Why it stops at 18.5%

This is the report's central finding. It is a negative one, and it tells the next person where to spend effort. Reranking is exhausted at 18.5%, and the limit is acoustic, not linguistic. Three pieces of evidence point the same way.

First, phone error rate responds to the interventions that moved word error rate only in small increments, and expensively. The anti-overfitting augmentation of the second ensemble member leaves it untouched. A ~10%-[PER](#per-phone-error-rate) audio teacher buys 1.4 points (23.71 to 22.34, [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)), which the decoder then fails to convert into words at all. A second full model, averaged in, buys 1.4 more (22.34 to 20.90, [Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker)). Everything downstream of the full-context encoder moves [PER](#per-phone-error-rate) by 1.44 points in total, against the 16.68 that full context bought on its own.

Second, the audio teacher cannot transfer its own quality. The electromyography-only Conformer matches the distilled one at the word level (26.10 against 26.14, [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)). A teacher that is itself only a ~10% [PER](#per-phone-error-rate) recognizer does not hand its phonetics to the muscle encoder.

Third, and most concretely, there is a nine-point [oracle](#oracle-wer-n-best-oracle) gap that no reranker closes. The union oracle is 9.30%; the reranker reaches 18.53%. The residual is not a language problem. For those utterances the reference words are *absent from the [acoustic posteriors](#acoustic-posterior)*: there is no candidate to select, and nothing for the constrained reranker to move toward. Free generation that “fixed” them would be hallucination, and the audit shows it does not happen (recall zero).

The conclusion is that ~20.9% acoustic phone error rate is the binding constraint. Getting below roughly 10% [WER](#wer-word-error-rate) on this task requires a better electromyographic acoustic model (more data, multiple subjects, or a stronger front-end that reads phonemes out of the raw signal), not a bigger or smarter language model. The entire decode-time stack in [Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker) is, in effect, a careful way of extracting the most words possible from a fixed amount of phonetic information. The same conclusion is reached independently, on an entirely different non-invasive signal, by Brain2Qwerty v2 [[8](#ref-8)], whose fine-tuned LLM improves [WER](#wer-word-error-rate) while *worsening* [CER](#cer-character-error-rate) and whose authors identify upstream encoder quality as the dominant term ([Section 2](#2-related-work)).

---

## 8. Limitations

- **One subject.** Every number comes from a single healthy speaker. The encoder memorizes the 8,500 training sentences (training [PER](#per-phone-error-rate) is far below the ~27% validation [PER](#per-phone-error-rate)), so cross-subject robustness is untested.
- **Not the best sEMG-to-text system.** 18.53% is the best result on the *emg2speech* General Corpus, but MONA LISA [[5](#ref-5)] reports 3.7% on vocalized EMG on the Gaddy corpus. The two are not measured on the same recordings ([Section 2](#2-related-work)), and I have not run Myovox on the Gaddy corpus, so I cannot say whether the gap is the corpus or the model.
- **Validation is harder than test.** Both systems score better on test than on validation, which is a roughly nine-point property of this fixed [sequential split](#sequential-split-8-500-760-400) rather than evidence of test-set overfitting. It also means the headline number is measured on the easier segment of the corpus. I report both columns rather than the flattering one.
- **The audio is a training-time crutch.** WavLM [distillation](#distillation) uses the parallel audio, which does not exist at silent-speech inference. At the word level the electromyography-only encoder matches it ([Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)), which is reassuring for the eventual application.
- **The ensemble's two contributions are not separated.** Averaging the two encoders improves [PER](#per-phone-error-rate) by 1.4 points and [WER](#wer-word-error-rate) by 2.7. How much of the word-level gain follows from the sharpened argmax and how much from the reshaped posterior is not measured here ([Q13](#q13-distillation-bought-1-4-points-of-per-and-no-wer-at-all-the-ensemble-bought-1-4-points-of-per-and-2-7-wer-why-the-difference)). The question does not bear on [Section 7](#7-why-it-stops-at-18-5), which holds under either answer, but the report should not be read as having settled it.
- **Test duplicates.** Six of the 400 test sentences duplicate training text, so the score is reported with and without them (18.53 against 18.75).
- **Reranking saturates.** The headline 18.53% is bounded by acoustic phone error rate, not by the language model. This is a negative result about language-model reranking for electromyography, not a claim that reranking is useless: it is worth −4.7 [WER](#wer-word-error-rate).
- **Vocalized, not silent.** The subject spoke aloud, so this validates the pipeline on the easier case. It is a stepping stone toward [silent speech](#silent-speech), not a demonstration of it.

---

## 9. The project website

Myovox is documented in two ways: this report, which is terse and aimed at readers who already know the field, and a website, which is aimed at a curious reader who is new to speech decoding and to electromyography. The site is a cinematic, scroll-driven explainer of surface-EMG speech decoding, showing how the electrical signals of the facial muscles are turned into text at an 18.53% word error rate. It walks each stage of the pipeline with animation rather than equations, which is why this report carries no architecture diagrams: the moving explanation lives at [`varshith-0.github.io/myovox`](https://varshith-0.github.io/myovox/). The project is open-sourced under the MIT license, and the site is paired with this technical report and a reproducible pipeline so that every claim on it is auditable.

---

## 10. Glossary

Every term below is a jump target: clicking any occurrence of the term in the body of the report brings the reader here. Definitions are given as the term is used in this report, not in full generality.

### Metrics

#### WER (word error rate)

The fraction of reference words that are wrong after the best alignment of hypothesis to reference, counting substitutions, insertions, and deletions: (S + I + D) / N. It is the reader-facing number, and it depends on the acoustic model, the decoder, and the language model together. Lower is better; 18.53% is the headline result here.

#### PER (phone error rate)

The same edit-distance quantity computed over [phonemes](#phoneme-phone) rather than words, measured by [greedy decoding](#greedy-decoding) of the CTC posteriors with no [lexicon](#lexicon) and no [language model](#language-model). Because nothing downstream of the encoder is involved, [PER](#per-phone-error-rate) is *decoder-independent*: it isolates the quality of the [acoustic model](#acoustic-model). In this report it serves as both the credibility check ([Section 4](#4-baseline-reproduction-and-a-decode-correction)) and the binding constraint ([Section 7](#7-why-it-stops-at-18-5)).

#### CER (character error rate)

The same edit distance computed over characters. Not used for any Myovox result, since [PER](#per-phone-error-rate) is the sharper instrument for an acoustic model that emits phonemes. It appears only in [Section 2](#2-related-work), because the non-invasive brain-to-text literature reports it: those systems decode keystrokes, for which the character is the natural unit. The usual ladder of granularity runs character, phone, word.

#### Oracle WER (*n*-best oracle)

The [WER](#wer-word-error-rate) that would be obtained if a perfect judge always selected the single best candidate from the *n*-best pool. It is a lower bound on what any [reranker](#reranking) over that pool can achieve, and therefore a measure of how much information the pool contains. Here the union pool has a 9.30% oracle against an 18.53% achieved [WER](#wer-word-error-rate), and the remaining nine points are words the acoustics never proposed at all.

#### Acoustic posterior

The per-frame probability distribution over output symbols (phonemes, units, or blank) emitted by the encoder. If the correct word's phonemes never receive appreciable probability mass, no decoder or reranker can recover it. That is the failure mode diagnosed in [Section 7](#7-why-it-stops-at-18-5).

### Models and architectures

#### Acoustic model

The neural network that maps the input signal, here [sEMG](#semg-surface-electromyography) features, to per-frame symbol posteriors. It is the only component whose quality [PER](#per-phone-error-rate) measures.

#### Language model

A model of which word sequences are plausible in English, used either inside the decoding graph (the *G* of [HLG](#hlg)) or after decoding, as a [reranker](#reranking). It supplies word-level priors, not phonetic evidence.

#### TDS (time-depth separable convolution)

The convolutional encoder used in the released baseline. It factorizes a convolution into a time-only and a channel-only (depthwise and pointwise) part, giving cheap large receptive fields. The released variant is [causal](#causal-encoder).

#### Conformer

An encoder block that interleaves [multi-head self-attention](#multi-head-self-attention) with [depthwise convolution](#depthwise-convolution), so it can model both long-range and local structure. The [bidirectional](#bidirectional-full-context-encoder) Conformer replaces the causal TDS encoder in [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio), and is responsible for most of the [WER](#wer-word-error-rate) gain.

#### Multi-head self-attention

The mechanism by which every frame in a sentence attends to every other frame, with several independent “heads” attending to different things. It is what gives the Conformer full-sentence context.

#### Depthwise convolution

A convolution applied independently per channel. It is cheap in parameters, and is used inside the Conformer block to capture local, short-time structure.

#### Causal encoder

An encoder that at each frame sees only past and present frames, never the future (implemented here by left-padding). Required for [streaming](#streaming), but a handicap for offline transcription.

#### Bidirectional (full-context) encoder

An encoder that may look at the entire utterance, future frames included. Legitimate whenever the whole sentence is recorded before decoding begins, as it is here.

#### Streaming

Producing output as the signal arrives, in real time, without waiting for the sentence to finish. Not required by this report, which decodes offline.

#### HuBERT

A self-supervised speech model whose discretized representations give the 100 [units](#hubert-unit) that the first CTC head predicts.

#### HuBERT unit

One of 100 discrete, self-supervised speech tokens obtained by clustering HuBERT features. Units are a finer-grained, learned alternative to phonemes, and they carry the dominant (0.8-weighted) CTC loss.

#### WavLM (WavLM-Large, layer 9)

A large self-supervised speech representation model. Its layer-9 features, extracted from the parallel audio, are the teacher signal for the [cross-modal distillation](#cross-modal-distillation). Layer 9 is used because the mid-stack layers of such models carry the most phonetic information.

#### Qwen2.5-7B-Instruct

The 7-billion-parameter open-weight instruction-tuned language model used as the [LIFT](#lift-dcond-lift-style) [reranker](#reranking).

#### LoRA (low-rank adaptation)

A fine-tuning method that freezes the base model and trains only a small pair of low-rank matrices injected into each weight (here, rank 16). It makes adapting a 7B model cheap, and makes its changes easy to isolate.

#### QLoRA

LoRA applied on top of a base model quantized to 4 bits (NF4), so that a 7B model can be fine-tuned on a single consumer GPU. Used for the reranker.

#### BiLSTM

A bidirectional long short-term memory recurrent network. Used here as the audio teacher for the frame-level KL term of the second ensemble member.

#### Frozen model

A model whose weights are held fixed while it participates in another model's training. The small WavLM-to-phoneme recognizer is frozen so that it acts as a fixed judge of whether the projected features are phoneme-decodable.

### Speech and electromyography

#### Electromyography (EMG)

The measurement of the electrical activity produced by muscle fibres when they contract.

#### sEMG (surface electromyography)

EMG measured non-invasively, by electrodes placed on the skin rather than by needles inserted into muscle. Here: a 31-channel array on the face, sampled at 5 kHz.

#### Non-invasive BCI (EEG, MEG)

The other non-invasive route to text, tapping cortex rather than muscle. EEG measures electrical fields at the scalp and is cheap and portable; MEG measures the magnetic fields of neuronal activity and is far cleaner but requires a room-sized, cryogenically cooled instrument. Both are far upstream of articulation, and both currently trail sEMG on error rate ([Section 2](#2-related-work)). Not used in this report; included only for comparison.

#### Vocalized speech

Speech produced aloud, with the vocal folds active and audible sound emitted. All Myovox recordings are vocalized, which is why the parallel audio exists at all.

#### Silent speech

Articulating without producing sound, and in the strictest case without moving air, so that only muscle activity is available. The eventual target application, and *not* what this report evaluates.

#### Phoneme (phone)

The smallest sound unit that distinguishes words in a language. The model predicts a 40-phoneme inventory (41 classes once blank is included), and [PER](#per-phone-error-rate) is measured over it.

#### Shrinkage covariance, the vec(E) front-end

The input representation. Rather than raw waveforms, each analysis window is summarized by the regularized (“shrunk”) covariance matrix across the 31 channels, vectorized. It captures how the channels co-activate, which is the form in which the geometry of facial articulation shows up.

#### Frame, window, hop

The signal is chopped into 25 ms *windows* advanced by a 20 ms *hop*, yielding one feature *frame* every 20 ms, that is, 50 frames per second.

### Training

#### CTC (connectionist temporal classification)

A loss that trains a frame-level classifier against an unaligned target sequence by summing over all alignments, using a special [blank](#blank-symbol-and-blank-penalty) symbol to mean “no output here.” It removes the need for frame-by-frame labels, which do not exist for EMG.

#### Dual-CTC

The baseline objective: two CTC heads on one encoder, one predicting HuBERT [units](#hubert-unit) and one predicting phonemes, tied together by a [consistency](#consistency-table) term.

#### Consistency table

A fixed conditional table P(phone | unit) used to penalize disagreement between the two CTC heads, so that the unit head's richer signal informs the phone head.

#### Distillation

Training one model (the student) to imitate the internal representations or outputs of another (the teacher), rather than only to fit the labels.

#### Cross-modal distillation

Distillation in which teacher and student read *different* signals of the same event: here the teacher reads audio (WavLM) and the student reads muscle activity (sEMG). The teacher exists only at training time; at inference the student runs on EMG alone. The idea is adapted from MONA [[5](#ref-5)].

#### InfoNCE

A contrastive loss that pulls a representation toward its matching partner, the same moment in the parallel audio, and pushes it away from all the non-matching ones in the batch, sharpened by a temperature τ (0.1 here).

#### Warm start

Initializing part of a new model from the weights of a previously trained one, rather than from random. The covariance front-end, the CTC heads, and the audio projection all warm-start from the baseline checkpoint.

#### Checkpoint selection

Choosing which training snapshot to keep, by a criterion evaluated on validation. Selecting by validation [PER](#per-phone-error-rate) rather than by validation CTC loss is worth roughly 4 [PER](#per-phone-error-rate) points here.

#### Fine-tuning

Continuing to train an already-trained model on a new, usually narrower task. Here: adapting Qwen2.5 to the reranking task with QLoRA.

#### Paired bootstrap

A significance test. Resample the test utterances with replacement many times, recompute the *difference* between two systems on the same resampled set each time, and read off a confidence interval. If the interval excludes zero, the improvement is unlikely to be sampling noise.

#### Cross-decoding (two-fold)

Generating the reranker's training candidates by splitting the training data in half and decoding each half with a model trained only on the other half. Without it, the candidates would reflect the model's memorized ~1% training [WER](#wer-word-error-rate), and the reranker would learn to correct errors it will never see at test time.

#### Leakage

Any path by which information about the evaluation data reaches the model during training, inflating the score. On a single-subject corpus the main risk is a language model that has memorized training sentences which recur at test.

#### Verbatim-recall audit

The control that counts how often the free reranker emits a reference sentence that was *not* present anywhere in its candidate list, that is, produced from memory rather than from evidence. The count here is zero.

### Decoding

#### Greedy decoding

Taking the highest-probability symbol at each frame independently, then collapsing repeats and blanks. No lexicon, no language model, no search. This is how [PER](#per-phone-error-rate) is measured, which is why [PER](#per-phone-error-rate) reflects the acoustic model and nothing else.

#### WFST (weighted finite-state transducer)

A finite-state machine whose transitions carry input symbols, output symbols, and weights. Composing several of them gives a single graph that maps frame-level posteriors to word sequences while accumulating scores.

#### HLG

The composed decoding graph H ∘ L ∘ G. *H* maps CTC frames to phonemes, *L* is the [lexicon](#lexicon) mapping phoneme strings to words, and *G* is the [language model](#language-model) over word sequences. Decoding is a search through this graph.

#### Lexicon

The pronunciation dictionary: for each word, its phoneme sequence or sequences. It defines exactly which words the decoder is capable of producing.

#### k2 and icefall

The open-source finite-state and speech-recognition toolkits used to construct and search the HLG graph, matching the original authors' setup.

#### LibriSpeech

A large public read-speech corpus. Its pronunciation lexicon, 34,546 words here, is what makes the decode [open-vocabulary](#open-vocabulary).

#### Open vocabulary

Decoding over a lexicon far larger than the corpus vocabulary (roughly five times larger here), so that the system can output words it never saw in training. The alternative would be a closed-set classifier over a fixed sentence or word list. Word error rates are not comparable across this boundary: a closed-vocabulary system with a small phrase list can post a much lower [WER](#wer-word-error-rate) while solving a much easier problem.

#### OOV (out of vocabulary)

A reference word absent from the lexicon, and hence impossible to emit. Twelve of the 2,429 test tokens are OOV, a hard 0.49% [WER](#wer-word-error-rate) floor.

#### Acoustic scale

The weight given to the acoustic scores relative to the language-model scores during graph search. Set it too low and the language model overwhelms the evidence; set it too high and the language model stops helping. Tuned on validation: 1.0 for the baseline, which is also the released default, so tuning changes nothing there; 0.25 for the Conformer, where it matters.

#### Blank symbol, and blank penalty

CTC's “emit nothing here” symbol, which dominates the posteriors (peak ≈ 0.92). The blank *penalty* subtracts a constant from its score at decode time so that real symbols can compete. It is the single largest lever in the baseline decode.

#### Lattice

The compact graph of high-scoring alternative paths retained during decoding, from which *n*-best lists are extracted.

#### *n*-best list

The top *n* complete hypotheses from the lattice, ranked by score. Extracting *n*-best lists at several acoustic scales and taking their *union* widens the pool a reranker can choose from, lowering the [oracle](#oracle-wer-n-best-oracle) [WER](#wer-word-error-rate) without changing the acoustic model.

#### Ensemble

Averaging the per-frame phone log-probabilities of two independently trained encoders before decoding. Worth 2.7 [WER](#wer-word-error-rate) points here at best (26.14 to 23.47), alongside a 1.4-point [PER](#per-phone-error-rate) improvement (22.34 to 20.90). How much of the word-level gain follows from the sharpened argmax and how much from the reshaped posterior is not separated in this report; see [Q13](#q13-distillation-bought-1-4-points-of-per-and-no-wer-at-all-the-ensemble-bought-1-4-points-of-per-and-2-7-wer-why-the-difference).

#### Reranking

Rescoring or rewriting the *n*-best candidates with a stronger model, usually a language model, so as to pick a better one than the acoustic score alone would. Bounded from below by the oracle [WER](#wer-word-error-rate).

#### LIFT (DCoND-LIFT style)

The reranking recipe adopted here: prompt a fine-tuned LLM with the candidate list *and* the detected phoneme sequence, and have it produce the final transcript. The *constrained* variant must return one of the candidates; the *free* variant may write its own correction.

### Data

#### General Corpus

The single-subject, healthy-speaker portion of the *emg2speech* release, used throughout: 9,660 sentences of 31-channel sEMG with simultaneously recorded audio.

#### Gaddy corpus

The reference open-vocabulary sEMG corpus of Gaddy and Klein [[2](#ref-2)]: eight facial channels at 1 kHz, roughly nineteen hours from a single English speaker, recorded in both silent and vocalized modes. It is the benchmark on which MONA LISA and most other sEMG-to-text systems report, and it is *not* the corpus used here.

#### Sequential split (8,500 / 760 / 400)

The authors' own division of the corpus, taken in recording order rather than at random, and kept unchanged here. Because it is sequential, validation and test are not statistically interchangeable: validation is systematically harder, by roughly nine points.

#### Validation set

The 760 sentences on which every hyperparameter is tuned: blank penalty, acoustic scale, checkpoint, and reranker variant. Nothing is ever tuned on test.

#### Test set

The 400 held-out sentences on which every reported test number is computed, once, with the settings already fixed on validation. Six of them duplicate training text, so results are reported both with and without them.

---

## 11. Frequently asked questions

These are the questions the project actually drew, in roughly the order they were asked. I have tried to answer the sharp form of each rather than the polite one, and where the honest answer is “I do not know,” it says so.

### Reproduction and the headline result

#### Q1. You report a 32-point improvement over the published number. Did you improve their model, or only their decoder?

Both, in separable amounts, and [Section 4](#4-baseline-reproduction-and-a-decode-correction) exists to keep them separable. The first 10.5 points are a decoder fix and nothing else. The evidence is the phone error rate: my baseline lands at 39.02% against the published 38.19%, a gap of 0.8 points ([Table 4](#table-4-baseline-reproduction)). Because [PER](#per-phone-error-rate) is measured by [greedy decoding](#greedy-decoding) with no [lexicon](#lexicon) and no [language model](#language-model), a matched [PER](#per-phone-error-rate) establishes that the [acoustic model](#acoustic-model) is the same acoustic model, so the entire [WER](#wer-word-error-rate) gain must come from supplying the decode settings the public release omits, of which the [blank penalty](#blank-symbol-and-blank-penalty) is much the largest. The remaining 22 points split into a genuinely better acoustic model ([Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio), [PER](#per-phone-error-rate) 39.02 → 22.34, worth 14.5 [WER](#wer-word-error-rate) points) and a decode-time stack worth 7.6 [WER](#wer-word-error-rate) points that takes [PER](#per-phone-error-rate) only 1.4 further, from 22.34 to 20.90, and whose largest single component, the reranker, cannot move [PER](#per-phone-error-rate) at all ([Section 6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker)). So: roughly a third of the total from decoding, a little under half from modeling, and the balance from extraction. I would rather publish that breakdown than a single undifferentiated delta. One caveat worth stating plainly: I never reproduce 51.17% itself, because the released configuration decodes at roughly 75%. The claim to have reproduced their *model* rests on the matched phone error rate, not on a matched word error rate.

#### Q2. Is 18.53% WER good? What does a sentence at that error rate look like?

Approximately one word in five is wrong, whether substituted, inserted, or dropped. The errors are not distributed evenly: most sentences read cleanly and a minority are badly mangled. For calibration, a modern recognizer on clean audio sits near 5%, and the published starting point for this task was 51.17%. The practical reading is that 18.53% is useful to a human who can tolerate correcting it, and not yet trustworthy unattended.

#### Q3. MONA LISA reported 3.7% WER on vocalized EMG in 2024. Why is your number five times worse?

Because it is a different corpus, and I do not know how much of the gap that explains. MONA LISA [[5](#ref-5)] evaluates on the [Gaddy corpus](#gaddy-corpus): eight channels, about nineteen hours, one speaker, recorded in both silent and vocalized modes. Myovox evaluates on the *emg2speech* [General Corpus](#general-corpus): 31 channels, 9,660 sentences, a different speaker, one mode. MONA additionally trains against audio-only LibriSpeech, which I do not. So the honest claim is the narrow one: 18.53% is the best number on *this* corpus, against a published 51.17%, and Myovox is not the state of the art for sEMG-to-text in general. There is a real scientific question hiding in the gap, and it is the sharpest one the project raises. MONA reaches 3.7% with a cross-modal audio objective; my control shows my cross-modal audio objective buying nothing at the word level (26.10 against 26.14). Either their contrastive formulation carries phonetic information that mine does not, or the [covariance front-end](#shrinkage-covariance-the-vec-e-front-end) discards what their raw-signal front-end keeps, or this corpus is simply harder. Running Myovox on the Gaddy corpus would separate those, and I have not done it.

#### Q4. Your test score is *better* than your validation score. That usually indicates a problem.

It usually does, so it deserves a direct answer rather than a footnote. The [split](#sequential-split-8-500-760-400) is *sequential*: the corpus is cut in recording order, not at random, so validation and test are not exchangeable samples of one distribution. Test is the easier segment, by roughly nine points, and the gap is stable across every system I trained, including the baseline, on which no tuning was performed. Overfitting to test would have *widened* the gap as I tuned; it did not. The protection here is procedural rather than statistical: every hyperparameter is selected on the 760 validation sentences and applied once to the 400 test sentences. Both columns are reported throughout, rather than only the flattering one. The corollary, which I would rather state than have pointed out to me, is that 18.53% is the error rate on the easier half of this corpus, not on a random sentence drawn from it.

### Scope: vocalized versus silent speech

#### Q5. Does this read thoughts?

No. It reads muscles. Myovox decodes the electrical activity of facial muscles as they contract to articulate, which is the terminal link of the motor chain, long after intention has become movement. Absent articulation, there is nothing at the electrodes to decode. The systems that do read cortex, non-invasively, are the [EEG and MEG](#non-invasive-bci-eeg-meg) decoders of [Section 2](#2-related-work), and they are currently far behind.

#### Q6. The subject spoke aloud. Doesn't the presence of parallel audio make the result vacuous?

It makes the claim weaker than a silent-speech demonstration would be, which is why the limitation is stated plainly rather than buried. It does not make it vacuous. The audio exists in the *recording*; it does not exist in the *model's input*. Every reported number, 40.63, 26.14, and 18.53, is produced by a system whose inference-time input is 31 channels of [sEMG](#semg-surface-electromyography) and nothing else. Audio enters only as a training-time teacher ([Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio)), and [Q9](#q9-your-own-control-shows-the-emg-only-encoder-matching-the-distilled-one-on-wer-was-the-wavlm-distillation-therefore-wasted) below shows that even this proves dispensable at the word level. What [vocalization](#vocalized-speech) buys is a stronger, more consistent signal than silent articulation produces, which is precisely why this is a stepping stone rather than the destination.

#### Q7. Would this work for someone who cannot speak, an ALS patient, say?

I do not know, and I would rather say so than gesture at the application and let the reader supply the optimism. The model is trained on one healthy speaker articulating normally. A patient with ALS presents different muscle recruitment, different signal amplitude, frequently altered anatomy, and no parallel audio from which to distil. Nothing in this report constitutes evidence that a model trained under my conditions transfers to theirs. Closing that gap requires data from the affected population, not extrapolation from mine.

#### Q8. Audio and EMG were recorded simultaneously. How do you know the model is not exploiting acoustic leakage into the electrode array?

The suspicion is well placed. The structural answer is that the input is a [shrinkage covariance across the 31 channels](#shrinkage-covariance-the-vec-e-front-end), a representation of how muscle groups co-activate over a 25 ms window rather than a waveform, so there is no spectral path by which speech could survive into the model's input in decodable form. For leakage to explain the result, it would have to carry enough phonetic detail to sustain a 22.34% [PER](#per-phone-error-rate) through a skin-surface array band-limited to muscle frequencies, and then survive the covariance summary. I did not run a dedicated acoustic-shielding ablation, so I offer this as a design argument, not as a measured control.

### Modeling choices

#### Q9. Your own control shows the EMG-only encoder matching the distilled one on WER. Was the WavLM distillation therefore wasted?

At the word level, effectively yes: 26.10 against 26.14 is a coin flip, and I chose to print that control in the same table as the result rather than relegate it to a footnote. Two things survive. The distillation does improve [PER](#per-phone-error-rate) (22.34 against 23.71), so the encoder is phonetically better even though the decoder cannot convert the improvement into words, which is itself a preview of the ceiling diagnosed in [Section 7](#7-why-it-stops-at-18-5). More importantly, the negative result is load-bearing: it demonstrates that the parallel audio is not a hidden crutch supporting the headline number, which is exactly what one needs to know before extending any of this to silent speech, where audio will not exist. A control that invalidates a favored component is worth more than the component was.

#### Q10. Why retain the frozen WavLM-to-phoneme recognizer? Are L2 and InfoNCE not sufficient to match the teacher's features?

L2 and InfoNCE make the projection *close* to WavLM. Close is not the same as useful. A projection can be smooth, correctly scaled, and well correlated frame-by-frame with the teacher, and still be phonetically empty: regression toward a high-dimensional target will happily settle on a blurred average that satisfies the loss while discarding the distinctions that separate one phoneme from the next. The [frozen](#frozen-model) recognizer changes what “close” is permitted to mean. It is a small network that already reads phonemes out of real audio, and its weights never move, so pushing the EMG projection through it and demanding a low CTC loss forces the projection to be *decodable into the correct phonemes* rather than merely audio-shaped. It is a guard against smooth-but-empty blur.

### The language-model reranker

#### Q11. A 7B language model on a single-subject corpus invites memorization. How do you exclude it?

By assuming it would occur, and building three controls before trusting the number. First, the reranker sees only the training split, and its training candidates are produced by two-fold [cross-decoding](#cross-decoding-two-fold), each half decoded by a model that never trained on it, so it learns to repair realistic errors rather than the memorized ~1% [WER](#wer-word-error-rate) the acoustic model achieves on its own training data. Second, six of the 400 test sentences duplicate training text exactly, so the score is reported both with and without them (18.53 against 18.75) and the reader may take whichever they find credible. Third, the [verbatim-recall audit](#verbatim-recall-audit) counts how often free generation emits a reference sentence *absent* from the candidate list, that is, recalled from memory rather than selected from evidence. The count is zero.

#### Q12. The free reranker may write anything it likes. Is 18.53% simply fluent hallucination?

That is the failure mode the verbatim-recall audit was constructed to detect, and it returns zero: the free variant never produces a correct reference that the acoustics did not propose. Its gains come from repairing candidates that were close but wrong, not from inventing candidates that were absent. The structural argument is the one that also bounds the system ([Section 7](#7-why-it-stops-at-18-5)). A model hallucinating its way to the answer would be closing the nine-point gap to the [oracle](#oracle-wer-n-best-oracle). It is not. It halts precisely where the acoustic evidence halts, which is what a well-behaved reranker does and what a hallucinating one would not.

### The acoustic ceiling

#### Q13. Distillation bought 1.4 points of PER and no WER at all. The ensemble bought 1.4 points of PER and 2.7 WER. Why the difference?

Because [PER](#per-phone-error-rate) and [WER](#wer-word-error-rate) interrogate different objects, and the ensemble moves both. [PER](#per-phone-error-rate) is a [greedy](#greedy-decoding) argmax over frames: it asks only whether the top symbol is correct. The [WFST](#wfst-weighted-finite-state-transducer) decoder never takes the top symbol; it searches over *paths*, weighing whole sequences against the [lexicon](#lexicon) and the [language model](#language-model). Averaging two encoders' log-probabilities sharpens the argmax, which is the 1.4 points of [PER](#per-phone-error-rate), but it also reshapes the tails of the distribution, and the tails are where the search actually operates. Paths on which the two models disagree get suppressed; correct paths that were never top-ranked survive to be found.

I did not separate the two contributions, and this report should not claim to have. The distillation control offers a rough calibration: there, 1.37 points of [PER](#per-phone-error-rate) (23.71 to 22.34) bought −0.04 [WER](#wer-word-error-rate). If that exchange rate held at 21–22% [PER](#per-phone-error-rate), the ensemble's 1.44 points would likewise buy nothing and the 2.67 [WER](#wer-word-error-rate) points would be the reshaped posterior alone. But that assumes the marginal [WER](#wer-word-error-rate) value of a [PER](#per-phone-error-rate) point is constant across the range, which it probably is not: a word needs all of its phonemes, so the curve is likely convex and the lower-[PER](#per-phone-error-rate) points worth more. Some of the 2.67 may be phonetic after all.

Either answer leaves [Section 7](#7-why-it-stops-at-18-5) standing, which is why the question can be left open here. If the gain is phonetic, it is direct evidence that [PER](#per-phone-error-rate) is the quantity that binds. If it is diversity, the ensemble redistributes information rather than adding any. It cannot rescue the system either way: 2.7 [WER](#wer-word-error-rate) points against the 14.49 that full context bought, and a phone error rate still at 20.9%.

#### Q14. Is 20.9% PER a ceiling for EMG, or only for *your* EMG model?

Only for mine. A single-subject study cannot support the stronger claim. What the report does establish is narrower and, I think, more useful: for this acoustic model on this corpus, 20.9% [PER](#per-phone-error-rate) is the binding constraint, and no amount of decoder or language-model sophistication passes it. [Section 7](#7-why-it-stops-at-18-5) gives three independent lines of evidence that the ceiling is acoustic. [PER](#per-phone-error-rate) moves only in small, expensive increments under interventions that move [WER](#wer-word-error-rate); the audio teacher cannot transfer its own phonetic quality; and the nine-point oracle gap consists of words the posteriors never proposed. Whether the ceiling is a property of surface EMG itself, of the covariance front-end, or of possessing 8,500 sentences from one person, this study cannot distinguish. That is the next experiment. MONA LISA's 3.7% on a different corpus ([Q3](#q3-mona-lisa-reported-3-7-wer-on-vocalized-emg-in-2024-why-is-your-number-five-times-worse)) is direct evidence that it is not a property of surface EMG itself.

#### Q15. Is there any independent support for the claim that the reranker, not the encoder, is the exhausted component?

Yes, and it arrives from a different signal entirely, which is the best kind of corroboration. Brain2Qwerty v2 [[8](#ref-8)] decodes typed sentences from non-invasive MEG with a [Conformer](#conformer) [CTC](#ctc-connectionist-temporal-classification) encoder and a [LoRA](#lora-low-rank-adaptation)-fine-tuned LLM above it, which is structurally the same stack as Sections [5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio) and [6](#6-the-final-pipeline-ensemble-union-and-a-language-model-reranker). Their encoder alone reaches 55% [WER](#wer-word-error-rate); an *n*-gram language model takes it to 43%; the fine-tuned 4B LLM takes it to 39%. The LLM is worth four points over the *n*-gram, and it buys them while *worsening* the character error rate: it trades local accuracy for fluency. The analogy is in the conclusion rather than the mechanism, and the difference matters. Their LLM rewrites the sentence autoregressively and reads MEG-derived word embeddings directly, so it can degrade [CER](#cer-character-error-rate); my reranker operates on words downstream of the greedy CTC output and cannot move [PER](#per-phone-error-rate) at all, which is why [PER](#per-phone-error-rate) here stays pinned at 20.9% rather than worsening. Their own text-only ablation, which leaves the LLM nothing but the encoder's characters, is the closer analogue to what I built, and it is worth about six [WER](#wer-word-error-rate) points. Their conclusion is nonetheless mine: final performance is dominated by upstream encoder quality, and improving the encoder is the priority. Two systems, two signals, one wall.

#### Q16. What is the single highest-value next step toward sub-10% WER?

Not the decoder. Everything downstream of the encoder is exhausted, which is the finding, and the reason [Section 7](#7-why-it-stops-at-18-5) was written. The gain has to come from the acoustic model: more data, multiple subjects, or a front-end that recovers phonemes from the raw 31-channel signal rather than from a 25 ms covariance summary. If forced to choose one, I would choose additional speakers, because it attacks the ceiling and the generalization limitation at the same time, and because a single-subject corpus is not a constraint one can model around.

### Reproducibility and deployment

#### Q17. What did this cost to train, and can it be reproduced?

The code, the configurations, and, critically, the decode settings are open-sourced under the MIT license at [`github.com/Varshith-0/myovox`](https://github.com/Varshith-0/myovox). That includes the [blank penalty](#blank-symbol-and-blank-penalty), the [checkpoint-selection criterion](#checkpoint-selection), the regenerated `words.txt`, and the [acoustic scale](#acoustic-scale): the settings whose combined absence is why the released configuration decodes at roughly 75% [WER](#wer-word-error-rate) rather than the 40.63% this baseline reaches. The blank penalty is much the largest of the four; I did not separate them further. The data is the *emg2speech* General Corpus, and must be obtained from its authors. Training ran on a single NVIDIA RTX 3080 Ti with 12 GB of VRAM, and took roughly 15 to 25 hours end to end depending on the experiment (baseline reproduction, Conformer training, or reranker fine-tuning). The [QLoRA](#qlora) configuration was chosen precisely so that the 7B reranker fits on that same 12 GB consumer card.

#### Q18. Does it run in real time?

No, and this is a deliberate trade rather than an oversight. The central architectural decision of [Section 5](#5-the-acoustic-model-a-full-context-conformer-taught-by-the-audio), replacing the [causal](#causal-encoder) encoder with a [bidirectional](#bidirectional-full-context-encoder) Conformer, lets the model attend to the entire utterance, future frames included, so no word can be emitted until the sentence ends. The [ensemble](#ensemble), the multi-scale [*n*-best union](#n-best-list), and the 7B [reranker](#reranking) above it are all offline by construction. A [streaming](#streaming) variant is certainly buildable, and the released causal TDS encoder is one, but it would surrender most of the 14.49 [WER](#wer-word-error-rate) points that full context purchased. The objective of this report was to locate the ceiling, not to ship an interface.

---

## Acknowledgments

Throughout the project I made heavy use of Anthropic's Claude: for working through the decode-time failures, structuring the distillation objective and the leakage controls, sifting the literature, and drafting this report. The design decisions, the experiments, and any errors that remain are mine.

---

## References

1. [](#ref-1)Harshavardhana T. Gowda, Daniel C. Comstock, and Lee M. Miller. *emg2speech: Synthesizing speech
   from electromyography using self-supervised speech models.* ACL 2026.
   [arXiv:2510.23969](https://arxiv.org/abs/2510.23969). Baseline reproduced here (Appendix D.4,
   "emg2text").
2. [](#ref-2)David Gaddy and Dan Klein. *Digital voicing of silent speech.* EMNLP 2020, pages 5521–5530.
   Introduces the 8-channel, single-speaker silent/vocalized facial EMG corpus.
3. [](#ref-3)David Gaddy and Dan Klein. *An improved model for voicing silent speech.* ACL-IJCNLP 2021
   (Volume 2: Short Papers).
4. [](#ref-4)David Gaddy. *Voicing Silent Speech.* PhD thesis, University of California, Berkeley, 2022.
5. [](#ref-5)Tyler Benster, Guy Wilson, Reshef Elisha, Francis R. Willett, and Shaul Druckmann. *A cross-modal
   approach to silent speech with LLM-enhanced recognition.* 2024.
   [arXiv:2403.05583](https://arxiv.org/abs/2403.05583). MONA LISA.
6. [](#ref-6)Payal Mohapatra, Akash Pandey, Xiaoyan Zhang, and Qi Zhu. *Can LLMs understand unvoiced speech?
   Exploring EMG-to-text conversion with LLMs.* ACL 2025 (Volume 2: Short Papers), pages 703–712,
   Vienna, Austria.
7. [](#ref-7)Jarod Lévy, Mingfang Zhang, Svetlana Pinet, Jérémy Rapin, Hubert Banville, Stéphane d'Ascoli, and
   Jean-Rémi King. *Brain-to-text decoding: A non-invasive approach via typing.* Nature Neuroscience,
   2025. Brain2Qwerty v1. [arXiv:2502.17480](https://arxiv.org/abs/2502.17480).
8. [](#ref-8)Mingfang Zhang, Jarod Lévy, Cedric Rommel, Jérémy Rapin, Corentin Bel, Julie Bonnaire, Daniel
   Nieto, Pierre Bourdillon, Svetlana Pinet, Stéphane d'Ascoli, Thomas Moreau, and Jean-Rémi King.
   *Accurate decoding of natural sentences from non-invasive brain recordings.* Meta AI technical
   report, 2026. Brain2Qwerty v2, 29 June 2026.
   [github.com/facebookresearch/brain2qwerty](https://github.com/facebookresearch/brain2qwerty).
9. [](#ref-9)Vassil Panayotov, Guoguo Chen, Daniel Povey, and Sanjeev Khudanpur. *LibriSpeech: An ASR corpus
   based on public domain audio books.* ICASSP 2015, pages 5206–5210.
10. [](#ref-10)Harshavardhana T. Gowda, Zachary D. McNaughton, and Lee M. Miller. *Geometry of orofacial
    neuromuscular signals: Speech articulation decoding using surface electromyography.* Journal of
    Neural Engineering, 2024.
11. [](#ref-11)Harshavardhana T. Gowda and Lee M. Miller. *Non-invasive electromyographic speech neuroprosthesis:
    A geometric perspective.* 2025. [arXiv:2502.05762](https://arxiv.org/abs/2502.05762).
12. [](#ref-12)Awni Hannun, Ann Lee, Qiantong Xu, and Ronan Collobert. *Sequence-to-sequence speech recognition
    with time-depth separable convolutions.* Interspeech 2019.
    [arXiv:1904.02619](https://arxiv.org/abs/1904.02619).
13. [](#ref-13)Alex Graves, Santiago Fernández, Faustino Gomez, and Jürgen Schmidhuber. *Connectionist temporal
    classification: Labelling unsegmented sequence data with recurrent neural networks.* ICML 2006,
    pages 369–376.
14. [](#ref-14)Wei-Ning Hsu, Benjamin Bolte, Yao-Hung Hubert Tsai, Kushal Lakhotia, Ruslan Salakhutdinov, and
    Abdelrahman Mohamed. *HuBERT: Self-supervised speech representation learning by masked prediction
    of hidden units.* IEEE/ACM TASLP, 29:3451–3460, 2021.
    [arXiv:2106.07447](https://arxiv.org/abs/2106.07447).
15. [](#ref-15)Daniel Povey et al. *k2 and icefall: FSA/FST algorithms and ASR recipes.* 2023.
    [github.com/k2-fsa/k2](https://github.com/k2-fsa/k2) ·
    [github.com/k2-fsa/icefall](https://github.com/k2-fsa/icefall).
16. [](#ref-16)Anmol Gulati, James Qin, Chung-Cheng Chiu, Niki Parmar, Yu Zhang, Jiahui Yu, Wei Han, Shibo Wang,
    Zhengdong Zhang, Yonghui Wu, and Ruoming Pang. *Conformer: Convolution-augmented transformer for
    speech recognition.* Interspeech 2020. [arXiv:2005.08100](https://arxiv.org/abs/2005.08100).
17. [](#ref-17)Sanyuan Chen, Chengyi Wang, Zhengyang Chen, Yu Wu, Shujie Liu, Zhuo Chen, Jinyu Li, Naoyuki Kanda,
    Takuya Yoshioka, Xiong Xiao, Jian Wu, Long Zhou, Shuo Ren, Yanmin Qian, Yao Qian, Michael Zeng,
    Xiangzhan Yu, and Furu Wei. *WavLM: Large-scale self-supervised pre-training for full stack speech
    processing.* IEEE JSTSP, 16(6):1505–1518, 2022.
    [arXiv:2110.13900](https://arxiv.org/abs/2110.13900).
18. [](#ref-18)Aaron van den Oord, Yazhe Li, and Oriol Vinyals. *Representation learning with contrastive
    predictive coding.* 2018. [arXiv:1807.03748](https://arxiv.org/abs/1807.03748).
19. [](#ref-19)Qwen Team. *Qwen2.5 technical report.* 2024. [arXiv:2412.15115](https://arxiv.org/abs/2412.15115).
20. [](#ref-20)Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, and Luke Zettlemoyer. *QLoRA: Efficient finetuning of
    quantized LLMs.* NeurIPS 2023. [arXiv:2305.14314](https://arxiv.org/abs/2305.14314).
21. [](#ref-21)Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and
    Weizhu Chen. *LoRA: Low-rank adaptation of large language models.* ICLR 2022.
    [arXiv:2106.09685](https://arxiv.org/abs/2106.09685).
22. [](#ref-22)Jingyuan Li, Trung Le, Chaofei Fan, Mingfei Chen, and Eli Shlizerman. *Brain-to-text decoding with
    context-aware neural representations and large language models.* 2024. DCoND-LIFT. Journal of
    Neural Engineering, 2025. [arXiv:2411.10657](https://arxiv.org/abs/2411.10657).
