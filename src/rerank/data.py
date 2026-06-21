"""LIFT (LLM-Informed Fine-Tuning) — shared prompt + data assembly for the generative reranker.

We QLoRA-fine-tune a local instruct LLM to map (n-best candidates + detected phoneme sequence) ->
the reference sentence, on the TRAIN split only. This teaches the in-domain sentence distribution
and the phoneme/n-best -> text mapping (the DCoND-LIFT mechanism that yields WER << PER), unlike the
prior run's frozen perplexity rescoring. Inference reuses build_user() so train/test prompts match.
"""
from __future__ import annotations
import argparse, json, re
import torch

from emg2text.config import apply_config_and_logging
from emg2text.decode.evaluate import split_refs
from emg2text.paths import NBEST, OUT

SYS = ("You correct the output of a silent-speech EMG recognizer. You are given several candidate "
       "transcriptions of one short spoken sentence and the recognizer's detected phoneme sequence "
       "(ARPABET). Reply with ONLY the single most likely sentence, in lowercase, with no "
       "punctuation. Use the candidates and phonemes as evidence.")


def norm(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def nb_file(nbset, split):
    return NBEST / (f"{split}_nbest.pt" if nbset in ("", "base") else f"{nbset}_{split}_nbest.pt")


def build_user(u, topk=10):
    cands = []
    seen = set()
    for c in u["cands"][:topk]:
        t = c["text"].lower()
        if t not in seen:
            seen.add(t); cands.append(t)
    lines = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(cands)) or "(none)"
    gp = u.get("greedy_phones", "")
    return f"Candidates:\n{lines}\nDetected phonemes: {gp}\nCorrect sentence:"


def main():
    import random
    ap = argparse.ArgumentParser()
    ap.add_argument("--nbset", required=True, help="n-best set name (e.g. enstrain)")
    ap.add_argument("--split", required=True)
    ap.add_argument("--out", required=True, help="output jsonl path")
    ap.add_argument("--topk", type=int, default=10)
    ap.add_argument("--aug_drop", type=float, default=0.0,
                    help="prob of dropping the target-matching candidate (forces generation; for clean train n-best)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--append", action="store_true")
    args = apply_config_and_logging(ap)
    random.seed(0)
    text = list(split_refs(args.split)[0])
    blob = torch.load(nb_file(args.nbset, args.split), map_location="cpu", weights_only=False)
    utts = blob["utts"]
    n = min(len(utts), len(text))
    if args.limit:
        n = min(n, args.limit)
    with open(args.out, "a" if args.append else "w") as f:
        for u, ref in zip(utts[:n], text[:n]):
            uu = u
            if args.aug_drop > 0 and random.random() < args.aug_drop:
                tnorm = norm(ref)
                uu = {**u, "cands": [c for c in u["cands"] if norm(c["text"]) != tnorm]}
            f.write(json.dumps({"system": SYS, "user": build_user(uu, args.topk),
                                "target": norm(ref)}) + "\n")
    print(f"[lift_data] wrote {n} examples (aug_drop={args.aug_drop}) -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
