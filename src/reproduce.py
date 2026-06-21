"""Fast reproduction of the headline: decode the trained Conformer's cached test logits
through the WFST and confirm 26.14 % WER / 22.34 % PER (within +-0.7), in seconds.

Run:    python -m emg2text.reproduce     (or the console script: emg2text-reproduce)
Writes: outputs/main/repro.md            (prints REPRO_PASS / REPRO_FAIL)

To reproduce from scratch instead (train the model, then decode), run: scripts/run_headline.sh
"""
import sys

from emg2text.decode import evaluate as V

LOGITS = V.RESULTS_DIR / "conf_l9_logits.pt"   # saved by train.py (val+test phone log-probs)
SCALE = 0.25                                   # acoustic scale selected on val (argmin val WER)
EXP_WER, EXP_PER = 26.14, 22.34
TOL = 0.7
OUT = V.RESULTS_DIR                            # outputs/main


def main():
    import torch
    OUT.mkdir(parents=True, exist_ok=True)
    blob = torch.load(LOGITS, map_location="cpu", weights_only=False)
    wer, per = V.evaluate(blob["test"], "test", scale=SCALE)
    wer, per = wer * 100, per * 100
    dW, dP = wer - EXP_WER, per - EXP_PER
    ok = abs(dW) <= TOL and abs(dP) <= TOL
    print(f"[{'PASS' if ok else 'FAIL'}] Conformer + WavLM-L9 (headline): "
          f"test WER {wer:.2f}% (exp {EXP_WER}, d{dW:+.2f})  PER {per:.2f}% (exp {EXP_PER}, d{dP:+.2f})",
          flush=True)
    lines = [
        "# Headline reproduction — bidirectional Conformer + WavLM-L9\n",
        f"Decoded the trained Conformer's cached **test** logits through the self-contained "
        f"`emg2text` package (val-tuned acoustic scale {SCALE}, applied once to test). "
        f"Tolerance: +-{TOL} WER/PER.\n",
        "| system | scale | exp WER | got WER | dWER | exp PER | got PER | dPER | status |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| Conformer + WavLM-L9 | {SCALE} | {EXP_WER} | {wer:.2f} | {dW:+.2f} | "
        f"{EXP_PER} | {per:.2f} | {dP:+.2f} | {'PASS' if ok else 'FAIL'} |",
        f"\n**Overall: {'PASS — standalone main/ reproduces 26.14 / 22.34.' if ok else 'FAIL — drift detected.'}**",
    ]
    (OUT / "repro.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT / 'repro.md'}", flush=True)
    print("REPRO_PASS" if ok else "REPRO_FAIL", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
