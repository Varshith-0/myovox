"""Phase 1a — N-best extraction from the legacy k2 HLG lattice.

For each utterance we sample an N-best list of *word* hypotheses from the HLG decode
lattice (icefall `Nbest`), decompose each path into:
  - am  : acoustic score along the path (nnet_output sum, with acoustic_scale applied)
  - lm  : HLG graph (n-gram LM + lexicon) score along the path
and attach the utterance's greedy-CTC phoneme string (what the acoustic model "heard",
lexicon-independent) for downstream LISA-style LLM rescoring.

To raise the oracle ceiling we union samples taken at several `nbest_scale` values
(smaller -> more unique paths) and optionally several acoustic scales.

We reuse the legacy `emg2text.decode.WFSTDecoder` verbatim (its loaded HLG, token maps,
acoustic-token mapping, and blank-penalty convention) — nothing in legacy is modified.

Output (cached, deterministic downstream): outputs/nbest/{split}_nbest.pt
  {meta, utts: [ {greedy_phones, cands: [{text, am, lm}], n_unique} ]}

On merge this file maps to emg2text/decode_nbest.py.
"""
from __future__ import annotations
import argparse, time
from pathlib import Path

import torch
import k2
from icefall.decode import get_lattice, Nbest, one_best_decoding
from icefall.utils import get_texts

from emg2text import config as C
from emg2text.decode import decode as D
from emg2text.decode.evaluate import wer_of, split_refs
from emg2text.paths import NBEST, LEGACY_LOGITS


def greedy_phone_string(lp: torch.Tensor, id2tok, a_ids) -> str:
    """Greedy CTC collapse of (T,41) phone logprobs -> ARPABET string (blank=40 dropped)."""
    g = lp.argmax(-1).tolist()
    out, prev = [], -1
    for t in g:
        if t != C.PHONE_BLANK and t != prev:
            out.append(id2tok[a_ids[t]])
        prev = t
    return " ".join(out)


class NbestDecoder:
    def __init__(self, device="cuda:0"):
        self.dec = D.WFSTDecoder(device=device)   # loads HLG (arc-sorted) on device
        self.dev = torch.device(device)
        self.has_lm = hasattr(self.dec.HLG, "lm_scores") and self.dec.HLG.lm_scores is not None
        self._nerr = 0
        print(f"[nbest] HLG on {device}; HLG has lm_scores = {self.has_lm}", flush=True)

    def _token_logits(self, lp: torch.Tensor, scale: float, blank_pen: float) -> torch.Tensor:
        lp = lp.float().to(self.dev) * scale
        T = lp.shape[0]
        tl = torch.full((1, T, self.dec.n_tok), self.dec.NEG, dtype=torch.float32, device=self.dev)
        tl[..., 0] = lp[:, C.PHONE_BLANK] - blank_pen
        for c, t in enumerate(self.dec.phone_token_ids):
            tl[..., t] = lp[:, c]
        return tl

    def nbest_one(self, lp, scale, blank_pen, num_paths, nbest_scales, sb=20.0, ob=8.0):
        """Return list of {text, am, lm} candidates (unioned over nbest_scales, deduped).

        We sample paths with k2.random_paths and read each path's total lattice score
        (= acoustic + HLG-LM, summed over its arcs) and word-ids DIRECTLY from the lattice
        tensors — avoiding icefall Nbest.intersect, which costs ~10 s/utt on these dense EMG
        lattices (k2.intersect_device over ~400k arcs). The best path survives any output_beam,
        so a small ob just prunes the lattice cheaply without changing the 1-best.

        `am` here holds the combined lattice total (HLG has no separate lm_scores); the LM
        contribution is re-added externally via the n-gram / LLM rescorer.
        """
        tl = self._token_logits(lp, scale, blank_pen)
        T = tl.shape[1]
        sup = torch.tensor([[0, 0, T]], dtype=torch.int32)
        try:
            lattice = get_lattice(nnet_output=tl, decoding_graph=self.dec.HLG,
                                  supervision_segments=sup, search_beam=sb, output_beam=ob,
                                  min_active_states=30, max_active_states=10000)
        except Exception as e:
            if self._nerr < 3:
                print(f"  [warn] get_lattice failed: {type(e).__name__}: {str(e)[:80]}", flush=True)
                self._nerr += 1
            return []
        seen = {}
        # exact one-best (the legacy 26.14 path) — guaranteed present in the candidate set
        try:
            ob_fsa = one_best_decoding(lattice, use_double_scores=True)
            ob_words = get_texts(ob_fsa)[0]
            ob_txt = " ".join(self.dec.id2word[w] for w in ob_words if w in self.dec.id2word).strip()
            if ob_txt:
                seen[ob_txt] = float(ob_fsa.scores.sum())
        except Exception:
            pass
        for ns in nbest_scales:
            try:
                nb = Nbest.from_lattice(lattice=lattice, num_paths=num_paths,
                                        use_double_scores=True, nbest_scale=ns)
                nb = nb.intersect(lattice)        # re-scores each word seq by its best alignment
                tot = nb.tot_scores().values.tolist()
                texts = get_texts(nb.fsa)
            except Exception as e:
                if self._nerr < 3:
                    print(f"  [warn] nbest(ns={ns}) failed: {type(e).__name__}: {str(e)[:80]}", flush=True)
                    self._nerr += 1
                continue
            for wid, sc in zip(texts, tot):
                txt = " ".join(self.dec.id2word[w] for w in wid if w in self.dec.id2word).strip()
                if not txt:
                    continue
                if txt not in seen or sc > seen[txt]:
                    seen[txt] = float(sc)
        cands = [{"text": t, "am": s, "lm": 0.0} for t, s in seen.items()]
        cands.sort(key=lambda d: d["am"], reverse=True)
        return cands

    def run_split(self, logps, scale, blank_pen, num_paths, nbest_scales, sb=20.0, ob=8.0):
        id2tok, a_ids = self.dec.id2tok, self.dec.phone_token_ids
        utts = []
        t0 = time.time()
        for i, lp in enumerate(logps):
            cands = self.nbest_one(lp, scale, blank_pen, num_paths, nbest_scales, sb=sb, ob=ob)
            utts.append({"greedy_phones": greedy_phone_string(lp, id2tok, a_ids),
                         "cands": cands, "n_unique": len(cands)})
            if (i + 1) % 25 == 0:
                torch.cuda.empty_cache()
            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(logps)}] mean#cand={sum(u['n_unique'] for u in utts)/len(utts):.1f} "
                      f"({time.time()-t0:.0f}s)", flush=True)
        return utts


# ---- parallel CPU runner (k2 GPU decode is unstable here; mirror legacy CPU pool) ----
import multiprocessing as _mp
_W = None


def _winit(device):
    global _W
    _W = NbestDecoder(device=device)


def _wdecode(arg):
    i, lp, scale, blank_pen, num_paths, nbest_scales, sb, ob = arg
    cands = _W.nbest_one(lp, scale, blank_pen, num_paths, nbest_scales, sb=sb, ob=ob)
    gp = greedy_phone_string(lp, _W.dec.id2tok, _W.dec.phone_token_ids)
    return i, {"greedy_phones": gp, "cands": cands, "n_unique": len(cands)}


def run_split_parallel(logps, scale, blank_pen, num_paths, nbest_scales, sb, ob, nproc, device="cpu"):
    ctx = _mp.get_context("spawn")
    args = [(i, lp, scale, blank_pen, num_paths, nbest_scales, sb, ob) for i, lp in enumerate(logps)]
    t0 = time.time()
    with ctx.Pool(nproc, initializer=_winit, initargs=(device,)) as pool:
        res = []
        for r in pool.imap_unordered(_wdecode, args, chunksize=max(1, len(args) // (nproc * 4))):
            res.append(r)
            if len(res) % 100 == 0:
                print(f"  [{len(res)}/{len(args)}] ({time.time()-t0:.0f}s)", flush=True)
    res.sort(key=lambda x: x[0])
    return [u for _, u in res]


def report(split, utts):
    """1-best (HLG total) WER + oracle WER + candidate stats."""
    import jiwer
    text, _, _ = split_refs(split)
    n = min(len(utts), len(text))
    onebest = [u["cands"][0]["text"] if u["cands"] else "" for u in utts[:n]]
    wer1 = wer_of(text[:n], onebest)
    # oracle: per-utt candidate with lowest single-sentence WER
    oracle = []
    for ref, u in zip(text[:n], utts[:n]):
        if not u["cands"]:
            oracle.append("")
            continue
        best = min(u["cands"], key=lambda c: jiwer.wer(ref.lower().strip() or " ", c["text"].lower().strip() or " "))
        oracle.append(best["text"])
    wero = wer_of(text[:n], oracle)
    mc = sum(u["n_unique"] for u in utts[:n]) / max(1, n)
    print(f"\n==== {split}: n-best 1-best WER={wer1*100:.2f}%  ORACLE WER={wero*100:.2f}%  "
          f"mean#cand={mc:.1f} ====", flush=True)
    return dict(wer_1best=wer1, wer_oracle=wero, mean_cand=mc, n=n)


def nb_path(nbset, split):
    """Canonical merged n-best file for a given n-best set + split."""
    return NBEST / (f"{split}_nbest.pt" if nbset in ("", "base") else f"{nbset}_{split}_nbest.pt")


def shard_path(nbset, split, k, nparts):
    pre = "" if nbset in ("", "base") else f"{nbset}_"
    return NBEST / f"{pre}{split}_nbest_part{k}of{nparts}.pt"


def merge_parts(split, nparts, nbset="base"):
    """Concatenate shard files (independent shard processes) in order, compute the report,
    and write the canonical merged n-best file."""
    parts = []
    for k in range(nparts):
        d = torch.load(shard_path(nbset, split, k, nparts), map_location="cpu", weights_only=False)
        parts.append((d["lo"], d["utts"], d["meta"]))
    parts.sort(key=lambda x: x[0])
    utts = [u for _, us, _ in parts for u in us]
    meta = parts[0][2]
    rep = report(split, utts)
    out = nb_path(nbset, split)
    torch.save({"meta": meta, "split": split, "utts": utts, "report": rep}, out)
    print(f"  merged {nparts} parts -> {out}  (n={len(utts)}, {out.stat().st_size/1e6:.1f} MB)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", default="test,val")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--blank_pen", type=float, default=2.0)
    ap.add_argument("--num_paths", type=int, default=100)
    ap.add_argument("--nbest_scales", default="0.5")
    ap.add_argument("--search_beam", type=float, default=20.0)
    ap.add_argument("--output_beam", type=float, default=8.0)
    ap.add_argument("--device", default="cpu", help="cpu only (k2 GPU decode asserts)")
    ap.add_argument("--part", type=int, default=-1, help="shard index (independent process)")
    ap.add_argument("--nparts", type=int, default=1, help="total shards")
    ap.add_argument("--merge", action="store_true", help="merge shard files into the merged n-best")
    ap.add_argument("--logits", default=str(LEGACY_LOGITS), help="input {val,test} logits .pt")
    ap.add_argument("--nbset", default="base", help="n-best set name (output file prefix)")
    ap.add_argument("--limit", type=int, default=0, help=">0: smoke-test first N utts, do not save")
    args = C.apply_config_and_logging(ap)
    nbest_scales = [float(x) for x in args.nbest_scales.split(",")]
    meta = dict(scale=args.scale, blank_pen=args.blank_pen, num_paths=args.num_paths,
                nbest_scales=nbest_scales, search_beam=args.search_beam, output_beam=args.output_beam)

    if args.merge:
        for split in args.splits.split(","):
            merge_parts(split, args.nparts, args.nbset)
        return

    blob = torch.load(args.logits, map_location="cpu", weights_only=False)
    dec = NbestDecoder(device=args.device)
    for split in args.splits.split(","):
        full = blob[split]
        n = len(full)
        if args.part >= 0:                       # contiguous shard
            per = (n + args.nparts - 1) // args.nparts
            lo, hi = args.part * per, min(n, (args.part + 1) * per)
        elif args.limit:
            lo, hi = 0, args.limit
        else:
            lo, hi = 0, n
        print(f"\n########## {split} [{lo}:{hi}] ##########", flush=True)
        utts = dec.run_split(full[lo:hi], args.scale, args.blank_pen, args.num_paths, nbest_scales,
                             sb=args.search_beam, ob=args.output_beam)
        if args.limit:
            report(split, utts)
            for u in utts[:3]:
                print("  greedy:", u["greedy_phones"][:70])
                print("  top3 :", [c["text"] for c in u["cands"][:3]], "n=", u["n_unique"])
            continue
        if args.part >= 0:
            out = shard_path(args.nbset, split, args.part, args.nparts)
            torch.save({"meta": meta, "split": split, "lo": lo, "hi": hi, "utts": utts}, out)
            print(f"  saved shard {args.part} -> {out}  (n={len(utts)})", flush=True)
        else:
            rep = report(split, utts)
            out = nb_path(args.nbset, split)
            torch.save({"meta": meta, "split": split, "utts": utts, "report": rep}, out)
            print(f"  saved {out}  ({out.stat().st_size/1e6:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
