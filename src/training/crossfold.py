"""Combine the two cross-decode fold outputs (each forwards the held-out half it did NOT train on)
into ordered realistic TRAIN logits (key 'train'), for the LIFT train n-best."""
import argparse, torch


def combine(inputs, out):
    parts = []
    for p in inputs:
        d = torch.load(p, map_location="cpu", weights_only=False)
        parts.append((int(d["lo"]), int(d["hi"]), d["xdecode"]))
    parts.sort(key=lambda x: x[0])
    train, exp = [], 0
    for lo, hi, xo in parts:
        assert lo == exp, f"gap/overlap: expected {exp} got {lo}"
        train.extend(xo); exp = hi
    torch.save({"train": train}, out)
    print(f"combined {len(parts)} folds -> {out}  (n={len(train)})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="*_xdecode_logits.pt files")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    combine(a.inputs, a.out)


if __name__ == "__main__":
    main()
