"""Phase 1d — tune the n-best score combination on VAL, apply once to TEST, report.

Score per candidate i of an utterance:
    s_i = am_i + b * llm_i + g * n_words_i        (+ a * kenlm_i  when present)
LISA generative hypothesis competes with an inherited acoustic score (am of the most
word-similar n-best candidate) plus a tunable bonus d.

Reports, on TEST (weights fixed from VAL):
  - acoustic-only greedy PER (modality-honest; LM/LLM-independent)
  - WER no-LLM  (am only, and am+kenlm if available)   -> n-gram-only operating point
  - WER LLM rescore           (b,g tuned, no LISA)
  - WER LLM rescore + LISA     (b,g,d tuned)            -> headline
  - oracle WER (ceiling of the n-best list)
  - paired-bootstrap 95% CI of (headline - baseline 26.14)
  - leakage audit: quarantine the 6 test∩train dups (WER in/out); LISA verbatim-recall flag

Writes outputs/LEADERBOARD.md rows + a JSON report. Never writes into legacy.
"""
from __future__ import annotations
import argparse, json, itertools
from pathlib import Path

import numpy as np
import torch
import Levenshtein

from emg2text.decode.evaluate import split_refs
from emg2text.paths import NBEST, OUT, quarantine_test_indices, LEGACY_LOGITS


def norm(s):
    return " ".join(s.lower().split())


def word_edits(ref, hyp):
    """Word-level edit distance + ref length (global sum == jiwer.wer).
    python-Levenshtein.distance accepts lists of ints (as legacy greedy_per uses it)."""
    r, h = ref.split(), hyp.split()
    vocab = {}
    ri = [vocab.setdefault(w, len(vocab)) for w in r]
    hi = [vocab.setdefault(w, len(vocab)) for w in h]
    return Levenshtein.distance(ri, hi), len(r)


def corpus_wer(refs, hyps):
    e = l = 0
    for r, h in zip(refs, hyps):
        de, dl = word_edits(norm(r), norm(h))
        e += de; l += dl
    return e / max(1, l)


def lisa_am(u):
    """Inherit acoustic score for the LISA hypothesis from the most word-similar candidate."""
    if not u["cands"]:
        return None
    lt = set(u.get("lisa_text", "").split())
    if not lt:
        return max(c["am"] for c in u["cands"])
    best, bj = u["cands"][0], -1.0
    for c in u["cands"]:
        ct = set(c["text"].lower().split())
        j = len(lt & ct) / max(1, len(lt | ct))
        if j > bj:
            bj, best = j, c
    return best["am"]


def hyps_for(utts, b, g, d, use_lisa, use_kenlm=False, a=0.0):
    out = []
    for u in utts:
        best_txt, best_s = "", -1e30
        for c in u["cands"]:
            nw = c.get("n_words", len(c["text"].split()))
            s = c["am"] + b * c.get("llm_logprob", 0.0) + g * nw
            if use_kenlm:
                s += a * c.get("kenlm", 0.0)
            if s > best_s:
                best_s, best_txt = s, c["text"]
        if use_lisa and u.get("lisa_text"):
            am_l = lisa_am(u)
            if am_l is not None:
                s = am_l + b * u.get("lisa_llm_logprob", 0.0) + g * u.get("lisa_n_words", 0) + d
                if use_kenlm:
                    s += a * u.get("lisa_kenlm", 0.0)
                if s > best_s:
                    best_s, best_txt = s, u["lisa_text"]
        out.append(best_txt)
    return out


def tune(val_utts, val_refs, betas, gammas, deltas, use_lisa, use_kenlm=False, alphas=(0.0,)):
    best = (1e9, 0.0, 0.0, 0.0, 0.0)
    for a in (alphas if use_kenlm else (0.0,)):
        for b in betas:
            for g in gammas:
                dlist = deltas if use_lisa else (0.0,)
                for d in dlist:
                    h = hyps_for(val_utts, b, g, d, use_lisa, use_kenlm, a)
                    w = corpus_wer(val_refs, h)
                    if w < best[0]:
                        best = (w, b, g, d, a)
    return best  # (val_wer, b, g, d, a)


def acoustic_onebest_hyps(split):
    """Exact legacy one-best hyps (scale 0.25, blank_pen 2.0, ob 50) — the 26.14 system.
    Cached to outputs/ so the paired bootstrap compares against the true legacy headline."""
    import json
    cache = OUT / f"legacy_{split}_onebest.json"
    if cache.exists():
        return json.loads(cache.read_text())
    from emg2text.decode.evaluate import decode_words
    blob = torch.load(LEGACY_LOGITS, map_location="cpu", weights_only=False)
    hyps = decode_words(blob[split], 0.25, blank_pen=2.0, sb=50.0, ob=50.0)
    cache.write_text(json.dumps(hyps))
    return hyps


def paired_bootstrap(refs, hyp_a, hyp_b, n=10000, seed=0):
    """95% CI of WER(b) - WER(a) by resampling sentences. Negative => b better than a."""
    rng = np.random.default_rng(seed)
    ea = np.array([word_edits(norm(r), norm(h)) for r, h in zip(refs, hyp_a)], float)
    eb = np.array([word_edits(norm(r), norm(h)) for r, h in zip(refs, hyp_b)], float)
    N = len(refs)
    diffs = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, N, N)
        wa = ea[idx, 0].sum() / ea[idx, 1].sum()
        wb = eb[idx, 0].sum() / eb[idx, 1].sum()
        diffs[i] = wb - wa
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi), float(diffs.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="qwen7b")
    ap.add_argument("--has_kenlm", action="store_true")
    args = ap.parse_args()

    feats = {s: torch.load(NBEST / f"{s}_llm_{args.tag}.pt", map_location="cpu", weights_only=False)
             for s in ("val", "test")}
    val_refs = list(split_refs("val")[0]); test_refs = list(split_refs("test")[0])
    val_utts = feats["val"]["utts"]; test_utts = feats["test"]["utts"]
    val_refs = val_refs[:len(val_utts)]; test_refs = test_refs[:len(test_utts)]

    betas = [0.0, 0.25, 0.5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48]
    gammas = [-6, -4, -2, -1, 0, 1, 2, 4]
    deltas = [-40, -20, -10, -5, 0, 5, 10, 20, 40]
    alphas = [0.0, 0.5, 1, 2, 4, 8] if args.has_kenlm else [0.0]

    R = {}
    # am-only sanity (b=g=d=0)
    R["am_only_test_wer"] = corpus_wer(test_refs, hyps_for(test_utts, 0, 0, 0, False))
    # no-LLM (am + kenlm) — only meaningful if kenlm present; else == am-only
    if args.has_kenlm:
        vw, b, g, d, a = tune(val_utts, val_refs, [0.0], gammas, [0.0], False, True, alphas)
        R["noLLM_val_wer"], R["noLLM_w"] = vw, (b, g, d, a)
        R["noLLM_test_wer"] = corpus_wer(test_refs, hyps_for(test_utts, b, g, d, False, True, a))
    else:
        R["noLLM_test_wer"] = R["am_only_test_wer"]
    # LLM rescore (no LISA)
    vw, b, g, d, a = tune(val_utts, val_refs, betas, gammas, [0.0], False, args.has_kenlm, alphas)
    R["llm_val_wer"], R["llm_w"] = vw, (b, g, d, a)
    test_hyp_llm = hyps_for(test_utts, b, g, d, False, args.has_kenlm, a)
    R["llm_test_wer"] = corpus_wer(test_refs, test_hyp_llm)
    # LLM rescore + LISA (headline)
    vw, b, g, d, a = tune(val_utts, val_refs, betas, gammas, deltas, True, args.has_kenlm, alphas)
    R["lisa_val_wer"], R["lisa_w"] = vw, (b, g, d, a)
    test_hyp_lisa = hyps_for(test_utts, b, g, d, True, args.has_kenlm, a)
    R["lisa_test_wer"] = corpus_wer(test_refs, test_hyp_lisa)
    headline_hyp = test_hyp_lisa if R["lisa_test_wer"] <= R["llm_test_wer"] else test_hyp_llm
    R["headline_test_wer"] = min(R["lisa_test_wer"], R["llm_test_wer"])

    # oracle ceiling (from the original n-best file's report)
    try:
        nb_test = torch.load(NBEST / "test_nbest.pt", map_location="cpu", weights_only=False)
        R["oracle_test_wer"] = nb_test.get("report", {}).get("wer_oracle")
    except Exception:
        R["oracle_test_wer"] = None

    # acoustic-only greedy PER (modality-honest, unchanged by LM/LLM)
    from emg2text.decode.evaluate import greedy_per_logits
    blob = torch.load(LEGACY_LOGITS, map_location="cpu", weights_only=False)
    _, syms, pdf = split_refs("test")
    R["test_greedy_PER"] = greedy_per_logits(blob["test"], syms[:len(test_utts)], pdf)

    # baseline = EXACT legacy one-best (the 26.14 system) for the paired bootstrap
    base_hyp = acoustic_onebest_hyps("test")[:len(test_refs)]
    R["baseline_test_wer"] = corpus_wer(test_refs, base_hyp)
    lo, hi, mean = paired_bootstrap(test_refs, base_hyp, headline_hyp)
    R["bootstrap_delta_mean"], R["bootstrap_ci95"] = mean, (lo, hi)

    # leakage: quarantine the test∩train duplicates
    q = set(quarantine_test_indices())
    keep = [i for i in range(len(test_refs)) if i not in q]
    R["n_quarantine"] = len(q)
    R["headline_test_wer_excl_dups"] = corpus_wer([test_refs[i] for i in keep],
                                                  [headline_hyp[i] for i in keep])
    # LISA verbatim-recall audit: LISA output == ref but NOT present among its candidates
    recalled = 0
    for u, r in zip(test_utts, test_refs):
        lt = norm(u.get("lisa_text", ""))
        if lt and lt == norm(r) and norm(r) not in {norm(c["text"]) for c in u["cands"]}:
            recalled += 1
    R["lisa_verbatim_recall_count"] = recalled

    (OUT / f"phase1_report_{args.tag}.json").write_text(json.dumps(R, indent=2, default=float))
    print(json.dumps(R, indent=2, default=float), flush=True)
    # save headline hyps for inspection
    with open(OUT / f"phase1_headline_hyps_{args.tag}.txt", "w") as f:
        for i, (r, h) in enumerate(zip(test_refs, headline_hyp)):
            f.write(f"{i}\tREF\t{r}\n{i}\tHYP\t{h}\n")

    # append to outputs/ leaderboard
    lb = OUT / "LEADERBOARD.md"
    with open(lb, "a") as f:
        ci = R["bootstrap_ci95"]
        f.write(f"| 1c | Qwen-rescore+LISA ({args.tag}) | {R['headline_test_wer']*100:.2f} | "
                f"{R['noLLM_test_wer']*100:.2f} | {R['test_greedy_PER']*100:.2f} | "
                f"{R['lisa_val_wer']*100:.2f} | [{ci[0]*100:+.2f},{ci[1]*100:+.2f}] WER pts vs base | "
                f"oracle {R['oracle_test_wer']*100:.1f}; excl-dups {R['headline_test_wer_excl_dups']*100:.2f} |\n")
    print(f"[leaderboard] appended; report -> {OUT}/phase1_report_{args.tag}.json", flush=True)


if __name__ == "__main__":
    main()
