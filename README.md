# emg2text — surface-EMG → text decoding

Decode open-vocabulary English text from 31-channel surface electromyography (sEMG) of vocalized
speech, on the *emg2speech* General Corpus (one subject, 9,660 sentences). One pipeline:

| Pipeline | Test WER | Test PER | What it is |
|---|---|---|---|
| **emg2text** | **18.53** | 20.90 | Conformer+WavLM-L9 **ensemble** → multi-scale n-best **union** → **LIFT** LLM rerank |

```
EMG (31ch, 5kHz) → SPD covariance → Conformer (×2, distilled from WavLM-L9) → phoneme CTC
                 → WFST (k2 HLG) → multi-scale n-best → union → QLoRA-LIFT rerank → text
```

The acoustic member alone is **26.14 WER / 22.34 PER**. All numbers are **tuned on val, applied once
to test**. PER is the decoder-independent greedy CTC phone error rate.

---

## Run it

```bash
bash scripts/setup.sh          # deps + the icefall WFST decoder (installed outside the repo) + OSF data steps
pip install -e .               # editable install

bash scripts/run.sh --check            # verify cached artifacts reproduce 26.14 + 18.53        (~15 min, GPU)
bash scripts/run.sh                    # full pipeline FROM SCRATCH (trains everything) → 18.53  (~15–25 h, GPU 0)
```

`scripts/run.sh` inlines the environment (GPU 0, editable install, HF cache, CPU decode pool) and runs the
whole chain. **Every step is idempotent** — it is skipped if its output exists, so a crashed run
resumes where it stopped. It requires the `varshith` tmux session for the long run. It ends by printing
the produced numbers next to the paper targets (`python -m emg2text.report`).

### Which file produces which number

| Number | Entry point | Key code |
|---|---|---|
| **26.14 / 22.34** (acoustic) | `python -m emg2text.reproduce` (cached) / `emg2text.train` (from scratch) | `model.py`, `train.py`, `losses.py`, `decode.py` |
| **18.53** (final) | `python -m emg2text.rerank.infer` | `ensemble.py`, `nbest.py`, `union.py`, `rerank/{data,train,tune,infer}.py` |

---

## How the pipeline works (18.53)

1. **Acoustic ensemble.** Mean of phone log-probs from two encoders: the WavLM-L9-distilled Conformer
   (`train.py` → 26.14) and an anti-overfit augmented Conformer (`train_augmented.py`). Ensembling
   alone: 26.14 → ~20 WER.
2. **Multi-scale n-best union** (`nbest.py` + `union.py`). N-best lists are extracted from the HLG
   lattice at acoustic scales {0.5, 0.4, 0.65} and unioned, lowering the oracle WER to **9.30**.
3. **LIFT rerank** (`rerank/`). A QLoRA-fine-tuned Qwen2.5-7B-Instruct maps *(n-best candidates +
   detected phonemes) → reference*. Trained on the TRAIN split only (leakage-safe via 2-fold
   cross-decoding, `crossfold.py`); the variant (free vs constrained) is selected on val. Final **test
   WER 18.53** (excl. the 6 test∩train duplicates: 18.75; verbatim-recall 0).

**Honest finding.** Reranking is exhausted: the binding constraint is the EMG acoustic PER (~20.9%),
not the language model — the correct words are absent from the acoustic posteriors, so no reranker can
close the gap to the 9.30 n-best oracle. `<10%` WER is not reached. (See `docs/technical_report.md`;
its §3 baseline is historical context — this repo reproduces the 26.14 + 18.53 numbers.)

---

## Repository layout

```
emg2text/
├── README.md  pyproject.toml  requirements.txt  LICENSE
├── scripts/                       # run.sh (the ONE command: full pipeline + --check) + setup.sh
├── configs/                       # all hyperparameters (one YAML per stage)
│   ├── conformer.yaml  augmented.yaml  teacher_conv.yaml  teacher_bilstm.yaml
│   └── ssl_features.yaml  nbest.yaml  lift.yaml  offline.yaml
├── docs/technical_report.md       # method, results, limitations
├── src/                           # the `emg2text` package (pyproject maps emg2text -> src/)
│   ├── config.py                  # SINGLE source of truth: paths + ALL constants + YAML loader
│   ├── paths.py  log.py  runlog.py  reproduce.py  report.py
│   ├── data/      data.py  covariance.py  text.py        # corpus, SPD features [vendored], g2p
│   ├── models/    frontend.py [vendored]  model.py  losses.py   # front-end + Conformer + losses
│   ├── decode/    decode.py  evaluate.py  score.py        # WFST decoder, WER/PER harness, scorer
│   ├── audio/    ssl_features.py  teacher_conv.py  teacher_bilstm.py   # WavLM feats + teachers
│   ├── training/  train.py  train_augmented.py  crossfold.py   # acoustic trainers + cross-decode
│   ├── pipeline/  forward.py  ensemble.py  nbest.py  union.py   # logits → ensemble → n-best → union
│   └── rerank/    data.py  train.py  tune.py  infer.py    # LIFT: data, QLoRA train, tune, inference
├── tests/                         # imports, config, reproduce, leakage controls, decode isolation
├── checkpoints/  outputs/         # trained models + cached logits/n-best/LIFT  (NOT in git)
└── data/                          # corpus + WFST graph                          (NOT in git; OSF)
```

## Data & checkpoints (not committed — fetch from OSF; see `scripts/setup.sh`)

```
OSF osf.io/65vbx → data/GeneralCorpusData/   (DATA.pkl, textLABELS.pkl, audio, ...)
OSF osf.io/bgh7t → data/wfst_decoder/ckptsLargeVocb/lang_phone/  (HLG.pt, lexicon, tokens)
checkpoints/baseline/epoch_30.pt   → upstream front-end warm-start SEED (a required input; the
                                     Conformer initialises its front-end + CTC heads from it)
checkpoints/main/ssl_wl_l9.pt      → precomputed WavLM-L9 features (17 GB; run.sh re-extracts if absent)
```

Runtime ~15–25 h on one 12 GB GPU; ~40 GB disk for the WavLM cache + intermediate logits. **What to do
when a step fails:** just re-run `bash scripts/run.sh` — completed steps are skipped (idempotent). Per-run
configs + metrics are written under `outputs/runs/<name>/`.

## Provenance & license

Two files are **vendored** from the upstream emg2speech reference implementation and keep their
attribution: `src/data/covariance.py` (SPD covariance) and `src/models/frontend.py`
(`featuresNorm` / `RotationInvariantMLP`). The rest is MIT. The WFST decoder is k2 / icefall (installed
out-of-repo by `scripts/setup.sh`). Reproduction numbers are nondeterministic to within ±0.5 WER
(cuDNN/CTC; QLoRA on a 7B LLM); greedy PER is the stable anchor.
