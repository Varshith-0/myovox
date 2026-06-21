"""Open-vocabulary WFST decoder (disk-only: phone log-probs in, word strings out).

WFSTDecoder loads the HLG graph + token/word symbol tables once, then maps a list of
(T, 41) phone log-probabilities to one-best word strings via k2 / icefall. greedy_per is
the decoder-independent greedy-CTC phone error rate. This module imports NO training or
model code — decoding only ever reads cached logits from disk (see tests/test_decode_isolation.py).
"""
import torch
import Levenshtein

from emg2text import config as C

import k2
from icefall.decode import get_lattice, one_best_decoding
from icefall.utils import get_texts


def read_symtable(path):
    s2i, i2s, mx = {}, {}, -1
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        s, i = line.split(); i = int(i); s2i[s] = i; i2s[i] = s; mx = max(mx, i)
    return s2i, i2s, mx + 1


def acoustic_token_ids(tok2id, n_phones=40):
    """The token ids for the 40 real phones (drop blank / noise / disambig symbols)."""
    EX = {"<eps>", "<blk>", "SPN", "NSN", "<SPOKEN_NOISE>", "<UNK>", "<NOISE>", "<SIL>", "<NOISE_SIG>"}
    items = sorted([(s, t) for s, t in tok2id.items()
                    if s not in EX and not s.startswith("#") and s != "<eps>"], key=lambda x: x[1])
    return [t for _, t in items[:n_phones]]


class WFSTDecoder:
    """Open-vocabulary HLG decoder. Construct once (loads the 1.2 GB graph), reuse."""

    def __init__(self, device="cpu"):
        self.tok2id, self.id2tok, self.n_tok = read_symtable(C.LANG_DIR / "tokens.txt")
        self.w2id, self.id2word, self.n_word = read_symtable(C.LANG_DIR / "words.txt")
        self.HLG = k2.arc_sort(k2.Fsa.from_dict(
            torch.load(C.LANG_DIR / "HLG.pt", map_location="cpu", weights_only=False)
        )).to(device).requires_grad_(False)
        self.phone_token_ids = acoustic_token_ids(self.tok2id, 40)
        self.dev = torch.device(device)
        self.NEG = -1e30

    def decode(self, logps, scale, sb=50.0, ob=50.0, blank_pen=2.0):
        words = []
        for lp in logps:
            lp = lp.float() * scale
            T = lp.shape[0]
            token_logits = torch.full((1, T, self.n_tok), self.NEG, dtype=torch.float32, device=self.dev)
            token_logits[..., 0] = lp[:, C.PHONE_BLANK].to(self.dev) - blank_pen
            for col, tok in enumerate(self.phone_token_ids):
                token_logits[..., tok] = lp[:, col].to(self.dev)
            sup = torch.tensor([[0, 0, T]], dtype=torch.int32)
            try:
                lat = get_lattice(nnet_output=token_logits, decoding_graph=self.HLG, supervision_segments=sup,
                                  search_beam=sb, output_beam=ob, min_active_states=30, max_active_states=10000)
                ids = get_texts(one_best_decoding(lat, use_double_scores=True))
                words.append(" ".join(self.id2word[w] for w in ids[0] if w in self.id2word))
            except Exception:
                words.append("")
        return words


def greedy_per(logps, syms, phone_def):
    """Decoder-independent greedy CTC phone error rate over a list of (T,41) log-probs."""
    tot_dist = tot_len = 0
    for lp, sym in zip(logps, syms):
        g = lp.argmax(-1).numpy()
        hyp, prev = [], -1
        for t in g:
            if t != C.PHONE_BLANK and t != prev:
                hyp.append(int(t))
            prev = int(t)
        ref = [phone_def[p] - 1 for p in sym]
        tot_dist += Levenshtein.distance(hyp, ref)
        tot_len += len(ref)
    return tot_dist / max(1, tot_len)
