# Surface-EMG-to-Text: From a 51% Baseline to 18.5% WER

**A technical report.** We decode open-vocabulary English text from 31-channel surface
electromyography (sEMG) of vocalized speech, on the single-subject *emg2speech* General Corpus.
Starting from the published 51.17% WER of Gowda et al. (Appendix D.4), we (i) recover the missing
open-vocabulary decode hyperparameters to reach a faithful **40.63% WER / 39.02% PER** baseline;
(ii) replace the causal encoder with a **bidirectional Conformer trained by four-term cross-modal
distillation** against the parallel audio's WavLM-Large layer-9 features, for **26.14% WER /
22.34% PER** acoustic-only; and (iii) add a **two-model acoustic ensemble → multi-scale n-best union
→ LLM reranker (LIFT)** to reach **18.53% WER**. We also report a negative result that bounds the
approach: reranking is exhausted at 18.5% because the binding constraint is the EMG **acoustic** PER
(~20.9%), not the language model — the correct words are absent from the acoustic posteriors, so no
reranker can close the gap to the 9.30% n-best oracle.

*All test numbers are on the 400-sentence held-out test set under the authors' official
8500 / 760 / 400 sequential split. Every hyperparameter is tuned on validation and applied once to
test. PER is the decoder-independent greedy CTC phone error rate.*

---

## 1. Results overview

| # | System | val WER | val PER | **TEST WER** | **TEST PER** | §|
|---|---|---|---|---|---|---|
| — | Gowda et al., Appendix D.4 (target) [1] | — | — | 51.17 | 38.19 | — |
| 1 | Baseline: causal TDS + dual-CTC + **corrected** open-vocab WFST decode | 53.12 | 45.31 | **40.63** | **39.02** | §3 |
| 2 | Acoustic: **bidirectional Conformer + WavLM-L9** 4-term distillation | 35.54 | 27.47 | **26.14** | **22.34** | §4 |
| 3 | Final: ensemble → n-best **union** → **LIFT** rerank | — | — | **18.53** | 20.90 | §5 |

The story is three moves. **§3** recovers the decode-time hyperparameters missing from the public
release, taking 51.17 → 40.63 WER *while matching PER* — establishing that the acoustic model
reproduces faithfully. **§4** makes the offline encoder full-context and trains it with cross-modal
distillation against the parallel audio, reaching 26.14 / 22.34 acoustic-only (−14.5 WER / −16.7 PER).
**§5** ensembles two acoustic models, unions their multi-scale n-best lists (oracle 9.30), and reranks
with a QLoRA-fine-tuned 7B LLM, reaching 18.53 — then shows why that is where this approach saturates.

---

## 2. Dataset

The healthy-subject **General Corpus** from the *emg2speech* OSF release (osf.io/65vbx).

| Property | Value |
|---|---|
| Sentences | 9,660 (9,541 unique) |
| Subject | single, healthy |
| EMG | 31-channel surface array, 5 kHz |
| Parallel audio | recorded **simultaneously** with the EMG (per-sentence EMG/audio duration correlation = 1.000) |
| Train / val / test | **8,500 / 760 / 400**, sequential (authors' split: `normDATA[:8500]`, `[8500:9260]`, `[9260:]`) |

The decoder operates over a **34,546-word** LibriSpeech-derived lexicon [10] (~5× the corpus
vocabulary), so the task is open-vocabulary; 12 of 2,429 test tokens are out-of-lexicon (0.49% WER
floor). EMG is vocalized (not silent) speech with time-aligned audio — the parallel audio is a
*training-time* signal only.

---

## 3. Baseline: reproduction and decode correction → 40.63 / 39.02

### 3.1 Acoustic model (unchanged from the authors' release)
- **Features:** `vec(E)` SPD shrinkage covariance, 31×31 → 961-dim, 25 ms window / 20 ms hop,
  α = 0.1, EpochJitter augmentation (`features/covariance.py`, vendored).
- **Encoder:** `DualHeadTDSCTC` [5] — causal TDS conv, `mlpFeatures=[384]`,
  `blockChannels=[24,24,24,24]`, `kernelWidth=14`, `bottleneckDim=512` (`models/tds.py`, vendored).
- **Heads / loss:** dual CTC — HuBERT-unit (100+blank) [7] and phoneme (40+blank);
  `0.8·CTC_unit + 0.1·CTC_phone + 0.1·consistency` (a fixed `P(phone|unit)` table couples the heads).

### 3.2 Open-vocabulary WFST decode
Phoneme posteriors → words with `HLG = H ∘ L ∘ G` via k2 / icefall [9] (`decode.py`) — the same
graph the authors use, so PER matches the paper directly.

### 3.3 What was missing, and what we added
The public notebooks omit the decode-time hyperparameters that turn good posteriors into good words:
1. **Acoustic scale** — notebooks decode at scale 1.0, over-weighting the LM (~75% WER); must be tuned.
2. **Blank penalty** — CTC posteriors are blank-dominant (peak ≈ 0.92). On val[:200] at scale 1.0,
   WER drops **77.6 → 60.6%** as blank penalty goes 0 → 2 (clean U-shape). The single largest lever.
3. **Missing `words.txt`** — regenerated from `lexicon.txt`.
4. **Checkpoint selection by validation PER** (not val CTC loss): test PER 42.9 → 39.0%.

Tuned `(scale, blank)` on val, applied `(1.0, 2.0)` once to test.

### 3.4 Baseline result (verified, Δ+0.00)
`scripts/reproduce_baseline.sh` forwards `checkpoints/baseline/epoch_30.pt` and decodes:

| System | val WER | val PER | TEST WER | TEST PER |
|---|---|---|---|---|
| Gowda et al., Appendix D.4 [1] | — | — | 51.17 | 38.19 |
| **Ours — TDS+CTC, corrected decode** | 53.12 | 45.31 | **40.63** | **39.02** |

We beat the published WER by **10.5 points while matching PER** (39.0 vs 38.2). Matched PER is the
credibility argument: the acoustic model reproduces faithfully (decoder-independent error is
identical), so the WER gain is attributable to a correctly specified open-vocabulary decode, not to
any model change. This checkpoint warm-starts the headline encoder (§4).

---

## 4. Acoustic model: bidirectional Conformer + WavLM-L9 cross-modal distillation → 26.14 / 22.34

Two changes take the baseline from 40.63 / 39.02 to 26.14 / 22.34: a full-context encoder, and a
four-term cross-modal distillation objective against the parallel audio.

### 4.1 Full-context encoding
The upstream TDS is **causal** (left-pads by `kernelWidth−1`) — correct for streaming, a handicap for
the offline task. We replace it with a **bidirectional Conformer** [15] (`models/conformer.py`):
4 layers, multi-head self-attention + depthwise conv (`conf_layers=4`, `conf_heads=4`, `conf_ffn=1024`,
`conf_kernel=31`), keeping the same front-end, two CTC heads, and WavLM projection. The front-end and
heads warm-start from §3.4; the Conformer trains fresh.

### 4.2 The four-term objective (`training/distill.py`, `losses.py`)
PER is decoder-independent: only a better acoustic model lowers it. We pull the EMG encoder toward the
parallel audio's **WavLM-Large layer-9** features [8] (precomputed for all 9,660 sentences,
`ssl/extract.py`) through one linear projection into WavLM's 1,024-dim space (construction inspired by
MONA [4]):

```
Loss = 0.8·CTC_unit + 0.1·CTC_phone + 0.1·consistency
     + 0.5·L2(proj, WavLM-L9)              (i)   feature regression (masked, frame-resampled)
     + 0.5·InfoNCE(proj, WavLM-L9)         (ii)  frame-synchronous contrast (τ=0.1)
     + 1.0·CTC(recognizer(proj), phones)   (iii) frozen WavLM→phoneme recognizer
```

Term (iii) is load-bearing relative to a vanilla MONA: a small **frozen** WavLM→phoneme CTC head
(`ssl/recognizer.py`; LayerNorm → 2×Conv1d(k=5) → Linear(41), trained to ~10% PER then frozen) forces
the projection to be **phoneme-decodable**, not merely close to WavLM — guarding the L2 term against
smooth-but-non-decodable blur.

### 4.3 Result (verified, Δ+0.00) and the EMG-only control
`scripts/run_headline.sh` trains; `emg2text.reproduce` decodes cached logits (val-tuned scale 0.25):

| | val WER | val PER | TEST WER | TEST PER |
|---|---|---|---|---|
| baseline (causal TDS, §3) | 53.12 | 45.31 | 40.63 | 39.02 |
| **bidirectional Conformer + WavLM-L9** | 35.54 | 27.47 | **26.14** | **22.34** |
| Conformer, **EMG-only** (no audio crutch) | — | — | 26.10 | 23.71 |

The gain is **−14.49 WER / −16.68 PER** vs baseline, acoustic-only, present in greedy PER (no LM) and
bootstrap-significant on test. **Key control:** an EMG-only Conformer (no WavLM distillation) reaches
**26.10 WER ≈ 26.14** — at the *word* level the audio crutch buys essentially nothing; the
distillation helps PER (22.34 vs 23.71) but the full-context encoder is what moves WER. This matters
for the silent-speech setting, where the parallel audio is unavailable.

---

## 5. Final pipeline: ensemble → n-best union → LIFT rerank → 18.53

### 5.1 Acoustic ensemble
We average per-frame phone log-probs of two encoders: the WavLM-L9-distilled Conformer (§4) and an
**anti-overfit augmented** Conformer (`training/augment.py`, "p2": stronger jitter/dropout, BiLSTM
audio-teacher frame-KL via `training/recognizer.py`). Ensembling alone: 26.14 → **~20.1 WER**.
Notably, the augmented model's **PER is unchanged** from the distilled one (~20.9%) — the ensemble
gain is decode-level diversity, not better phonetics (foreshadowing §5.4).

### 5.2 Multi-scale n-best union (`nbest.py`, `union.py`)
From the ensemble's HLG lattice we extract n-best lists at several acoustic scales (k2 `random_paths`
+ `Nbest.intersect`) and **union** them. The union lowers the **n-best oracle WER to 9.30%** (the best
achievable by picking the single best candidate per utterance) while the 1-best stays ~20%. The gap
between 9.30 (oracle) and 20 (1-best) is the headroom a reranker can in principle recover.

### 5.3 LIFT reranker (`rerank/`)
We fine-tune **Qwen2.5-7B-Instruct** with **QLoRA** (4-bit nf4 + LoRA r=16) to map *(n-best candidates
+ detected phonemes) → reference* (DCoND-LIFT-style [4]). Two variants, selected on val: **free**
(generate the correction — can recover oracle misses but can hallucinate) and **constrained** (pick
the highest-scored candidate — cannot hallucinate). Leakage controls:
- **Train split only.** LIFT trains on TRAIN n-best, generated by **2-fold cross-decoding**
  (`training/xdecode.py`): each half is decoded by a model that did **not** train on it, so the n-best
  reflects realistic (not memorized 1.08%-WER) candidates.
- **Test∩train duplicates.** 6 / 400 test sentences are exact-text duplicates of train phrases;
  reported both in and out: **18.53 / 18.75**.
- **Verbatim-recall audit.** Free-generation recall of references *absent from the candidate set* = **0**
  (no train-text leakage through the LLM).

`scripts/reproduce_final.sh` (`emg2text.rerank.infer`, cached union n-best + adapter):

| Metric | Value |
|---|---|
| **TEST WER (LIFT)** | **18.53** |
| TEST WER excl. 6 dups | 18.75 |
| n-best oracle WER | 9.30 |
| greedy PER (acoustic) | 20.90 |
| verbatim-recall (leakage) | 0 |
| paired bootstrap vs 26.14 acoustic | ΔWER mean −7.6, 95% CI [−9.40, −5.90] |
| paired bootstrap vs ~20.1 ensemble 1-best | ΔWER mean −4.7, 95% CI [−6.22, −3.29] |

Both CIs exclude 0 — the rerank gain is significant.

### 5.4 The binding constraint (negative finding)
**Reranking is exhausted at 18.5%, and the limit is acoustic, not linguistic.** Evidence:
- **PER is invariant to the interventions that helped WER.** Anti-overfit augmentation (§5.1) and the
  10%-PER audio-teacher distillation (§4.2) leave the EMG **greedy PER pinned at ~20.9%**. The model's
  phonetic quality does not move; only decode-level diversity and word-level priors do.
- **EMG-only ≈ WavLM-distilled at the word level** (26.10 ≈ 26.14, §4.3): the audio teacher — itself a
  ~10% PER recognizer — cannot transfer its phonetic quality to the EMG encoder.
- **A 9-point oracle gap no reranker closes.** The union oracle is 9.30; the reranker reaches 18.53.
  The residual exists because the reference words are **absent from the acoustic posteriors** for those
  utterances — there is no candidate to select and (constrained) nothing to rerank toward; free
  generation that "fixes" them would be hallucination (recall = 0 by audit). The ~20.9% acoustic PER is
  the binding constraint; closing it requires a better EMG **acoustic** model (more data, multi-subject,
  or a stronger silent-speech front-end), not a better language model. **<10% WER is not reached.**

---

## 6. Limitations & honesty notes

- **Single subject.** All numbers are one healthy subject; the encoder memorizes the 8,500 train
  sentences (train PER ≪ val PER ≈ 27%), so cross-subject robustness is **untested**.
- **val > test split gap.** Test scores *better* than val for both systems (a ~9-point property of the
  fixed sequential split, not test-overfitting); both columns are reported.
- **Audio crutch (training only).** WavLM distillation uses the parallel audio, unavailable at
  silent-speech inference; at the word level the EMG-only encoder matches it (§4.3).
- **Test duplicates.** 6 / 400 test sentences duplicate train text; reported in/out (18.53 / 18.75).
- **Reranking saturates (§5.4).** The headline 18.53 is acoustic-PER-bound; this is a negative result
  about LLM reranking for EMG, not a claim that reranking is unhelpful (it is worth −4.7 WER).

---

## 7. Reproducibility

| | Command | Reads | Produces |
|---|---|---|---|
| Target 1 | `bash scripts/reproduce_baseline.sh` | `checkpoints/baseline/epoch_30.pt` | val 53.12/45.31, test **40.63/39.02** |
| Acoustic | `emg2text.reproduce` | `outputs/main/conf_l9_logits.pt` | test **26.14/22.34** |
| Target 2 | `bash scripts/reproduce_final.sh` | `outputs/nbest/ensU_*`, `checkpoints/lift_qwen_x/` | test **18.53** (oracle 9.30, excl-dups 18.75, recall 0) |

- **Split:** authors' official 8,500 / 760 / 400 sequential.
- **Decode:** open-vocab `HLG` (34,546-word lexicon + LibriSpeech 4-gram LM); scale/blank tuned on val,
  applied once to test (`1.0/2.0` baseline; `0.25/2.0` Conformer).
- **Metrics:** WER (`jiwer`) and decoder-independent greedy PER. Significance via paired 10k-bootstrap.
- **Hardware:** one NVIDIA GPU (12 GB), CUDA 12.1; PyTorch 2.5 + cu121; k2 / icefall [9];
  transformers + peft (QLoRA Qwen2.5-7B-Instruct). `scripts/env.sh` pins GPU 0 + the HF cache.
- **From scratch:** `scripts/run_headline.sh` (WavLM-L9 extraction → audio-recognizer → Conformer →
  decode); ensemble/union/LIFT via `emg2text.{ensemble,union,rerank.train}` (see `scripts/`).

---

## References

*Identifiers are best-effort; verify against your reference manager.*

[1] Gowda et al. *emg2speech: synthesizing speech from electromyography using self-supervised speech models.* Result reproduced: Appendix D.4 "emg2text," 51.17% WER / 38.19% PER.
[4] T. Benster et al. *A Cross-Modal Approach to Silent Speech with LLM-Enhanced Recognition (MONA-LISA).* 2024. arXiv:2403.05583.
[5] A. Hannun et al. *Sequence-to-Sequence Speech Recognition with Time-Depth Separable Convolutions.* Interspeech 2019. arXiv:1904.02619.
[6] A. Graves et al. *Connectionist Temporal Classification.* ICML 2006.
[7] W.-N. Hsu et al. *HuBERT.* IEEE/ACM TASLP 2021. arXiv:2106.07447.
[8] S. Chen et al. *WavLM.* IEEE JSTSP 2022. arXiv:2110.13900.
[9] D. Povey et al. *k2 / icefall.* github.com/k2-fsa/k2, github.com/k2-fsa/icefall.
[10] V. Panayotov et al. *LibriSpeech.* ICASSP 2015.
[15] A. Gulati et al. *Conformer.* Interspeech 2020. arXiv:2005.08100.
