"""Reproduction: the cached acoustic headline test logits still give greedy PER 22.34
(decoder-independent, fast — no k2/HLG needed). Full WFST numbers: `bash run.sh --check`.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOGITS = ROOT / "outputs" / "main" / "conf_l9_logits.pt"


def test_entrypoints_exist():
    import myovox.reproduce as r
    import myovox.report as rep
    assert hasattr(r, "main") and hasattr(rep, "main")


@pytest.mark.skipif(not LOGITS.exists(), reason="cached headline logits not present")
def test_headline_greedy_per_matches():
    import torch
    from myovox.decode import evaluate as V
    from myovox.decode import decode as D
    blob = torch.load(LOGITS, map_location="cpu", weights_only=False)
    _, syms, phone_def = V.split_refs("test")
    n = min(len(blob["test"]), len(syms))
    per = D.greedy_per(blob["test"][:n], syms[:n], phone_def)
    # acoustic headline test PER is 22.34%; greedy PER is decoder-independent.
    assert abs(per * 100 - 22.34) < 0.7, f"greedy PER drifted: {per*100:.2f}% (expected 22.34%)"
