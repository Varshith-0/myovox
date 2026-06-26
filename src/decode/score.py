"""Canonical scorer: decode phone log-posteriors through the WFST and report WER/PER.

Run:  python -m myovox.score --logits LOGITS.pt [--scale S | --split test]
The trainer and `myovox.reproduce` both score through this harness so numbers are comparable.
"""
import argparse
from pathlib import Path

import torch

from myovox.decode import evaluate as V


def read_text_file(path, split):
    lines = Path(path).read_text().splitlines()
    if any("\tHYP\t" in ln for ln in lines):
        hyps = {}
        for ln in lines:
            parts = ln.split("\t")
            if len(parts) >= 3 and parts[1] == "HYP":
                hyps[int(parts[0])] = parts[2]
        return [hyps[i] for i in sorted(hyps)]
    return [ln for ln in lines]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logits", default="")
    ap.add_argument("--text", default="")
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--scale", type=float, default=None,
                    help="fixed acoustic scale; if omitted and logits has val+test, tune on val")
    ap.add_argument("--blank_pen", type=float, default=V.DEFAULT_BLANK_PEN)
    ap.add_argument("--scales", default="", help="comma list to override default tuning grid")
    ap.add_argument("--system", default="eval")
    ap.add_argument("--track", default="acoustic-only")
    ap.add_argument("--ckpt", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--no_row", action="store_true")
    args = ap.parse_args()

    if args.text:
        hyps = read_text_file(args.text, args.split)
        wer, per = V.evaluate(hyps, args.split)
        print(f"\n==== {args.system} [{args.split}] WER={wer*100:.2f}%  (text input) ====", flush=True)
        if not args.no_row:
            kw = {f"{args.split}_wer": wer}
            V.Leaderboard.append(args.system, track=args.track, ckpt=args.ckpt or args.text,
                                 hparams="text", seed=args.seed, **kw)
        return

    blob = torch.load(args.logits, map_location="cpu", weights_only=False)
    scales = [float(s) for s in args.scales.split(",")] if args.scales else V.DEFAULT_SCALES

    if args.scale is not None:
        logps = blob[args.split] if isinstance(blob, dict) else blob
        wer, per = V.evaluate(logps, args.split, scale=args.scale,
                              blank_pen=args.blank_pen, device=args.device)
        print(f"\n==== {args.system} [{args.split}] scale={args.scale} "
              f"WER={wer*100:.2f}%  PER={per*100:.2f}% ====", flush=True)
        if not args.no_row:
            kw = {f"{args.split}_wer": wer, f"{args.split}_per": per}
            V.Leaderboard.append(args.system, track=args.track, ckpt=args.ckpt or args.logits,
                                 hparams=f"scale={args.scale},bp={args.blank_pen}", seed=args.seed, **kw)
        return

    assert isinstance(blob, dict) and "val" in blob and "test" in blob, \
        "tuning mode needs a {'val':...,'test':...} logits file (or pass --scale)"
    res = V.tune_scale_then_test(blob["val"], blob["test"], scales=scales,
                                 blank_pen=args.blank_pen, device=args.device)
    print(f"\n==== {args.system}  val WER={res['val_wer']*100:.2f}% PER={res['val_per']*100:.2f}%  "
          f"|  TEST WER={res['test_wer']*100:.2f}% PER={res['test_per']*100:.2f}%  "
          f"(scale={res['scale']}, bp={args.blank_pen}) ====", flush=True)
    if not args.no_row:
        V.Leaderboard.append(args.system, track=args.track,
                             val_wer=res["val_wer"], val_per=res["val_per"],
                             test_wer=res["test_wer"], test_per=res["test_per"],
                             ckpt=args.ckpt or args.logits,
                             hparams=f"scale={res['scale']},bp={args.blank_pen}", seed=args.seed)


if __name__ == "__main__":
    main()
