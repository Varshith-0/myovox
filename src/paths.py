"""Artifact paths + provenance naming + the leakage-control index set.

Everything the pipeline writes goes under outputs/ (config.RESULTS_ROOT); trained
models go under checkpoints/ (config.CKPT_ROOT). Output filenames encode the config
and metric that produced them via artifact_name().
"""
from __future__ import annotations
import pickle

from myovox import config as C

OUT = C.RESULTS_ROOT                               # repo-root outputs/
CKPT = C.CKPT_ROOT                                 # repo-root checkpoints/
LOGS = OUT / "logs"
NBEST = OUT / "nbest"
RUNS = OUT / "runs"                                # per-run config + metrics (runlog.py)
for _p in (OUT, CKPT, LOGS, NBEST, RUNS, OUT / "B"):
    _p.mkdir(parents=True, exist_ok=True)

# Cached headline phone log-probs (the acoustic member that reproduces 26.14/22.34).
LEGACY_LOGITS = OUT / "main" / "conf_l9_logits.pt"


def artifact_name(stem, *, arch=None, tag=None, ep=None, val_per=None, val_wer=None, ext="pt"):
    """Provenance-encoding filename: arch/tag + epoch + metric + stem.

    e.g. artifact_name("logits", arch="conformer", tag="l9", ep=31, val_per=0.2747)
         -> "conformer_l9_ep31_valPER27.47_logits.pt"
    """
    parts = [p for p in (arch, tag) if p]
    if ep is not None:
        parts.append(f"ep{ep}")
    if val_per is not None:
        parts.append(f"valPER{val_per * 100:.2f}")
    if val_wer is not None:
        parts.append(f"valWER{val_wer * 100:.2f}")
    parts.append(stem)
    return "_".join(parts) + "." + ext


def _texts():
    return pickle.load(open(C.DATA_ROOT / "textLABELS.pkl", "rb"))


def quarantine_test_indices():
    """0-based indices within the 400-sentence test split whose sentence is an exact
    duplicate of a TRAIN sentence (leakage-control #3). Reported both in and out."""
    t = _texts()
    train_lo, train_hi = C.SPLITS["train"]
    test_lo, test_hi = C.SPLITS["test"]
    train = set(s.strip().lower() for s in t[train_lo:train_hi])
    test = t[test_lo:test_hi]
    return [i for i, s in enumerate(test) if s.strip().lower() in train]


if __name__ == "__main__":
    q = quarantine_test_indices()
    print("quarantine test indices (test also in train):", q, "count", len(q))
