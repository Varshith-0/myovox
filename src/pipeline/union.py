"""Union n-best candidate lists across multiple runs (models x acoustic scales) to LOWER THE ORACLE.

For each utterance, take the union (dedup by lowercased text) of candidates from several n-best
files, keep the greedy phoneme string from the primary run, and recompute the n-best oracle WER.
`am` is kept as the max seen (not comparable across scales) — downstream rescoring recomputes a
consistent acoustic score via add_ctc; LIFT conditions on the candidate texts + phonemes.
"""
import argparse
import torch
from emg2text.pipeline.nbest import report
from emg2text.paths import NBEST


def nb_file(nbset, split):
    return NBEST / (f"{split}_nbest.pt" if nbset in ("", "base") else f"{nbset}_{split}_nbest.pt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="nbset names to union (primary first)")
    ap.add_argument("--out", required=True, help="output nbset name")
    ap.add_argument("--splits", default="val,test")
    args = ap.parse_args()
    for split in args.splits.split(","):
        blobs = [torch.load(nb_file(nb, split), map_location="cpu", weights_only=False) for nb in args.inputs]
        n = len(blobs[0]["utts"])
        utts = []
        for i in range(n):
            primary = blobs[0]["utts"][i]
            seen = {}
            for bl in blobs:
                if i >= len(bl["utts"]):
                    continue
                for c in bl["utts"][i]["cands"]:
                    k = c["text"].lower()
                    if k not in seen or c.get("am", -1e30) > seen[k]["am"]:
                        seen[k] = {"text": c["text"], "am": c.get("am", 0.0), "lm": 0.0}
            cands = sorted(seen.values(), key=lambda d: d["am"], reverse=True)
            utts.append({"greedy_phones": primary.get("greedy_phones", ""),
                         "cands": cands, "n_unique": len(cands)})
        rep = report(split, utts)
        meta = {**blobs[0].get("meta", {}), "unioned_from": args.inputs}
        out = nb_file(args.out, split)
        torch.save({"meta": meta, "split": split, "utts": utts, "report": rep}, out)
        print(f"  union {args.inputs} -> {out}  (n={n}, mean#cand={rep['mean_cand']:.1f})", flush=True)
    print("UNION_DONE", flush=True)


if __name__ == "__main__":
    main()
