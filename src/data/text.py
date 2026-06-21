"""Phoneme vocabulary and text→phoneme conversion (g2p), with an on-disk cache.

Faithful to the headline pipeline: classes are ``token_id - 1`` (0..39), blank = 40.
The cache (``phon_arr.npy`` / ``phon_syms.json``) lets evaluation avoid re-running g2p.
"""
import json
import re

import numpy as np

from emg2text import config


def load_phone_def(tokens_path=None):
    """Return {ARPABET symbol -> token id} from tokens.txt (skips <eps> and #-markers)."""
    tokens_path = tokens_path or (config.LANG_DIR / "tokens.txt")
    tok2id = {}
    with open(tokens_path) as f:
        for line in f:
            s, i = line.strip().split()
            i = int(i)
            if s == "<eps>" or s.startswith("#"):
                continue
            tok2id[s] = i
    return tok2id


def phonemize(labels, phone_def):
    """Text -> phoneme-class sequences (class = token_id - 1). Uses the on-disk cache if present."""
    if config.PHON_CACHE.exists() and config.PHON_SYMS_CACHE.exists():
        arr = np.load(config.PHON_CACHE)
        lens = np.load(config.PHON_LEN_CACHE)
        syms = json.load(open(config.PHON_SYMS_CACHE))
        if len(syms) == len(labels):
            return syms, arr, lens
    from g2p_en import G2p
    g2p = G2p()
    syms = []
    for txt in labels:
        ph = [re.sub(r"[0-9]", "", p) for p in g2p(txt)]
        ph = [p for p in ph if re.match(r"[A-Z]+", p)]
        syms.append(ph)
    classes = [[phone_def[p] - 1 for p in s] for s in syms]
    L = max(len(s) for s in classes) if classes else 1
    arr = np.full((len(classes), L), -1, dtype=np.int64)
    lens = np.zeros(len(classes), dtype=np.int64)
    for i, s in enumerate(classes):
        arr[i, : len(s)] = s
        lens[i] = len(s)
    return syms, arr, lens


def pad_units(unit_labels):
    """Pad a list of HuBERT-unit sequences into (N, Lmax) + lengths."""
    mx = max(len(u) for u in unit_labels)
    arr = np.zeros((len(unit_labels), mx), dtype=np.int64)
    lens = np.zeros(len(unit_labels), dtype=np.int64)
    for i, seq in enumerate(unit_labels):
        seq = np.asarray(seq, dtype=np.int64)
        arr[i, : len(seq)] = seq
        lens[i] = len(seq)
    return arr, lens
