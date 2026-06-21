"""Canonical evaluation harness: WFST decode + jiwer WER + greedy CTC PER.

One evaluate() is used everywhere (train.py, reproduce.py, score.py) so every number is
byte-identical. Also provides: tune_scale_then_test (pick acoustic scale on val, apply
once to test), a parallel WFST decode pool (DECODE_NPROC=1 forces serial), subprocess_eval
(decode a saved logits file in a clean process), and a Leaderboard helper.
"""
import os
import sys
import pickle
import multiprocessing as mp

from emg2text import config as C
from emg2text.decode import decode as D
from emg2text.data import text as _text
from emg2text.log import get_logger

log = get_logger(__name__)

# Artifact directories for the headline acoustic member.
CKPT_DIR = C.CKPT_ROOT / "main"        # trained features / teacher / Conformer ckpts
RESULTS_DIR = C.RESULTS_ROOT / "main"  # cached logits, leaderboard, repro.md
CKPT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LEADERBOARD = RESULTS_DIR / "leaderboard.md"

# Decode hyperparameters that define the comparison (single source: config.py).
DEFAULT_BLANK_PEN = C.DEFAULT_BLANK_PEN
DEFAULT_SCALES = C.DECODE_SCALES
DECODE_NPROC = int(os.environ.get("DECODE_NPROC", "12"))


# ----------------------------------------------------------------------------
# Reference loader (text + phoneme syms only; never loads the 18 GB EMG pickle).
# ----------------------------------------------------------------------------
_REFS = None


def load_refs():
    """dict(text, syms, phone_def) for the full corpus, via the on-disk g2p cache."""
    global _REFS
    if _REFS is not None:
        return _REFS
    text = pickle.load(open(C.DATA_ROOT / "textLABELS.pkl", "rb"))
    phone_def = _text.load_phone_def()
    syms, _, _ = _text.phonemize(text, phone_def)
    _REFS = dict(text=text, syms=syms, phone_def=phone_def)
    return _REFS


def split_slice(split):
    """(lo, hi) index range for a named split (the one definition in config.SPLITS)."""
    return C.SPLITS[split]


def split_refs(split):
    r = load_refs()
    lo, hi = split_slice(split)
    return r["text"][lo:hi], r["syms"][lo:hi], r["phone_def"]


# ----------------------------------------------------------------------------
# Shared WFST decoder (reuse decode.WFSTDecoder + greedy_per)
# ----------------------------------------------------------------------------
_DECODER = None


def get_decoder(device="cpu"):
    global _DECODER
    if _DECODER is None:
        _DECODER = D.WFSTDecoder(device=device)
    return _DECODER


def greedy_per_logits(logps, syms, phone_def):
    """Decoder-independent greedy CTC PER (reuses decode.greedy_per)."""
    return D.greedy_per(logps, syms, phone_def)


# ---- parallel decode (the WFST loop is single-threaded; fan it across cores) ----
_WORKER_DEC = None
_POOL = None


def _worker_init():
    global _WORKER_DEC
    from emg2text.decode import decode as _D
    _WORKER_DEC = _D.WFSTDecoder(device="cpu")


def _worker_decode(arg):
    lp, scale, blank_pen, sb, ob = arg
    return _WORKER_DEC.decode([lp], scale, sb=sb, ob=ob, blank_pen=blank_pen)[0]


def _get_pool():
    global _POOL
    if _POOL is None:
        _POOL = mp.get_context("spawn").Pool(DECODE_NPROC, initializer=_worker_init)
    return _POOL


def decode_words(logps, scale, blank_pen=DEFAULT_BLANK_PEN, sb=50.0, ob=50.0, device="cpu"):
    """WFST one-best word strings for a list of (T,41) phone log-probs.

    Fans the per-sentence decode across DECODE_NPROC processes (each its own WFSTDecoder);
    byte-identical to serial. DECODE_NPROC=1 forces serial; any pool error falls back to serial.
    """
    if DECODE_NPROC <= 1 or len(logps) < 8:
        return get_decoder(device).decode(logps, scale, sb=sb, ob=ob, blank_pen=blank_pen)
    try:
        pool = _get_pool()
        args = [(lp, scale, blank_pen, sb, ob) for lp in logps]
        chunk = max(1, len(args) // (DECODE_NPROC * 4))
        return pool.map(_worker_decode, args, chunksize=chunk)
    except Exception as e:
        log.warning("parallel decode pool failed (%s); serial fallback", e)
        return get_decoder(device).decode(logps, scale, sb=sb, ob=ob, blank_pen=blank_pen)


def wer_of(refs, hyps):
    import jiwer
    return jiwer.wer([t.lower() for t in refs], [h.lower() for h in hyps])


# ----------------------------------------------------------------------------
# Canonical evaluate()
# ----------------------------------------------------------------------------
def evaluate(logits_or_text, split, scale=None, blank_pen=DEFAULT_BLANK_PEN,
             sb=50.0, ob=50.0, device="cpu"):
    """Single canonical scorer used throughout the pipeline.

    logits_or_text:
        - list[Tensor (T,41)] of phone log-posteriors -> decode + WER + greedy PER
        - list[str] of decoded hypotheses             -> WER only (PER is None)
    Returns (wer, per).
    """
    text, syms, phone_def = split_refs(split)
    if len(logits_or_text) and isinstance(logits_or_text[0], str):
        hyps = logits_or_text
        n = min(len(hyps), len(text))
        return wer_of(text[:n], hyps[:n]), None
    logps = logits_or_text
    assert scale is not None, "scale required when evaluating logits"
    n = min(len(logps), len(text))
    logps = logps[:n]
    per = greedy_per_logits(logps, syms[:n], phone_def)
    hyps = decode_words(logps, scale, blank_pen=blank_pen, sb=sb, ob=ob, device=device)
    wer = wer_of(text[:n], hyps)
    return wer, per


def tune_scale_then_test(val_logps, test_logps, scales=None, blank_pen=DEFAULT_BLANK_PEN,
                         sb=50.0, ob=50.0, device="cpu"):
    """Pick the acoustic scale by VAL WER, apply once to TEST. No test-set tuning.

    Returns dict(scale, val_wer, val_per, test_wer, test_per).
    """
    scales = scales or DEFAULT_SCALES
    best_scale, best_vwer, best_vper = None, 1e9, None
    for s in scales:
        vwer, vper = evaluate(val_logps, "val", scale=s, blank_pen=blank_pen, sb=sb, ob=ob, device=device)
        log.info("tune scale=%-5s val WER=%.2f%% PER=%.2f%%", s, vwer * 100, vper * 100)
        if vwer < best_vwer:
            best_vwer, best_vper, best_scale = vwer, vper, s
    twer, tper = evaluate(test_logps, "test", scale=best_scale, blank_pen=blank_pen, sb=sb, ob=ob, device=device)
    log.info("tune -> scale=%s  TEST WER=%.2f%% PER=%.2f%%", best_scale, twer * 100, tper * 100)
    return dict(scale=best_scale, val_wer=best_vwer, val_per=best_vper, test_wer=twer, test_per=tper)


# ----------------------------------------------------------------------------
# Leaderboard (append-only; one row per experiment)
# ----------------------------------------------------------------------------
_LB_HEADER = ("| system | track | val WER | val PER | test WER | test PER | "
              "ckpt / source | decode hyperparams | seed |\n"
              "|---|---|---|---|---|---|---|---|---|\n")


def _fmt(x):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x * 100:.2f}"
    return str(x)


class Leaderboard:
    @staticmethod
    def append(system, track="acoustic-only", val_wer=None, val_per=None,
               test_wer=None, test_per=None, ckpt="", hparams="", seed=0):
        if not LEADERBOARD.exists():
            LEADERBOARD.write_text("# leaderboard\n\n" + _LB_HEADER)
        row = (f"| {system} | {track} | {_fmt(val_wer)} | {_fmt(val_per)} | "
               f"{_fmt(test_wer)} | {_fmt(test_per)} | {ckpt} | {hparams} | {seed} |\n")
        with open(LEADERBOARD, "a") as f:
            f.write(row)
        log.info("leaderboard + %s: val WER=%s test WER=%s test PER=%s",
                 system, _fmt(val_wer), _fmt(test_wer), _fmt(test_per))
        return row


# ----------------------------------------------------------------------------
# Decode a saved {val,test} logits file in a fresh process (used by the trainer)
# ----------------------------------------------------------------------------
def subprocess_eval(logits_path, system, track="acoustic-only", ckpt="", seed=0,
                    blank_pen=DEFAULT_BLANK_PEN):
    """Decode a saved {val,test} logits file by invoking score.py in a FRESH process.

    The 'spawn' decode pool is unreliable when created inside a CUDA-initialised training
    process holding the 18 GB SSL tensor; a clean subprocess sidesteps that (byte-identical).
    """
    import subprocess
    cmd = [sys.executable, "-u", "-m", "emg2text.decode.score",
           "--logits", str(logits_path), "--system", system, "--track", track,
           "--ckpt", str(ckpt), "--seed", str(seed), "--blank_pen", str(blank_pen)]
    log.info("subprocess_eval: %s", " ".join(cmd))
    subprocess.run(cmd, check=False)
