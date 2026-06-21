"""Print the produced numbers next to the paper targets (docs/technical_report.md), with
PASS/FAIL per row. Run at the end of run.sh.

  python -m emg2text.report --tag liftx

Acoustic row is recomputed from the cached headline logits (scale 0.25); the final row is
read from the LIFT report JSON produced by emg2text.rerank.infer.
"""
import argparse
import json
from pathlib import Path

from emg2text import config as C
from emg2text.paths import OUT
from emg2text.decode.evaluate import RESULTS_DIR

# (label, produced WER, produced PER, target WER, target PER, WER tol, PER tol)
WER_TOL, PER_TOL = 0.5, 0.7


def _acoustic_row(logits_path):
    import torch
    from emg2text.decode import evaluate as ev
    if not logits_path.exists():
        return None
    blob = torch.load(logits_path, map_location="cpu", weights_only=False)
    wer, per = ev.evaluate(blob["test"], "test", scale=C.OFFLINE_SCALE)
    return wer * 100, per * 100


def _final_row(tag):
    p = OUT / "B" / f"lift_report_{tag}.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    return r.get("test_lift_wer", 0) * 100, None, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="liftx")
    ap.add_argument("--acoustic-logits", default=str(RESULTS_DIR / "conf_l9_logits.pt"))
    args = ap.parse_args()

    print("\n================ emg2text — produced vs paper (docs/technical_report.md) ================")
    print(f"{'system':40s} {'WER':>8} {'target':>8} {'PER':>8} {'target':>8}  status")
    all_pass = True

    ac = _acoustic_row(Path(args.acoustic_logits))
    if ac:
        w, p = ac
        ok = abs(w - 26.14) <= WER_TOL and abs(p - 22.34) <= PER_TOL
        all_pass &= ok
        print(f"{'Conformer + WavLM-L9 (acoustic)':40s} {w:8.2f} {26.14:8.2f} {p:8.2f} {22.34:8.2f}  "
              f"{'PASS' if ok else 'FAIL'}")
    else:
        print(f"{'Conformer + WavLM-L9 (acoustic)':40s} {'—':>8} {26.14:8.2f} {'—':>8} {22.34:8.2f}  MISSING")
        all_pass = False

    fr = _final_row(args.tag)
    if fr:
        w, _, r = fr
        ok = abs(w - 18.53) <= WER_TOL
        all_pass &= ok
        extra = (f"  [excl-dups {r.get('test_lift_wer_excl_dups', 0)*100:.2f} (18.75), "
                 f"oracle {r.get('test_oracle', 0)*100:.2f} (9.30), "
                 f"recall {r.get('test_lift_verbatim_recall')} (0), variant {r.get('selected_variant')}]")
        print(f"{'Final ensemble -> union -> LIFT':40s} {w:8.2f} {18.53:8.2f} {'—':>8} {'—':>8}  "
              f"{'PASS' if ok else 'FAIL'}{extra}")
    else:
        print(f"{'Final ensemble -> union -> LIFT':40s} {'—':>8} {18.53:8.2f} {'—':>8} {'—':>8}  MISSING")
        all_pass = False

    print("=" * 90)
    print(f"OVERALL: {'ALL PASS' if all_pass else 'NOT ALL PASS'} (WER tol ±{WER_TOL}, PER tol ±{PER_TOL})\n")
    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
