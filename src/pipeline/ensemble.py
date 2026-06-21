"""Average several models' per-frame phone log-probs into ensemble logits.

Reads each member's {split: [logits]} file, averages per frame (truncating to the
shortest member), and writes one {split: [logits]} file covering all requested splits.
"""
import argparse

import torch

from emg2text.log import setup_logging, get_logger

log = get_logger(__name__)


def mean_logits(inputs, splits, out):
    blobs = [torch.load(p, map_location="cpu", weights_only=False) for p in inputs]
    result = {}
    for split in splits:
        members = [b[split] for b in blobs]
        n = len(members[0])
        merged = []
        for i in range(n):
            ls = [m[i].float() for m in members]
            T = min(x.shape[0] for x in ls)
            merged.append(sum(x[:T] for x in ls) / len(ls))
        result[split] = merged
        log.info("ensembled %d members, split=%s (n=%d)", len(inputs), split, n)
    torch.save(result, out)
    log.info("saved ensemble logits -> %s", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="member {split:logits} .pt files")
    ap.add_argument("--splits", default="val,test")
    ap.add_argument("--out", required=True)
    ap.add_argument("--log-level", default="INFO")
    a = ap.parse_args()
    setup_logging(a.log_level)
    mean_logits(a.inputs, a.splits.split(","), a.out)
    print("ENSEMBLE_DONE", flush=True)


if __name__ == "__main__":
    main()
