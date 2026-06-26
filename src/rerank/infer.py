"""LIFT step 3 — inference with the fine-tuned reranker. Two variants, selected on VAL:
  (a) FREE: the model generates the corrected sentence (may leave the n-best -> can recover oracle
      misses, but can hallucinate -> leakage-audited).
  (b) CONSTRAINED: pick the n-best candidate the fine-tuned model scores highest (cannot hallucinate
      -> verbatim-recall 0 by construction).
Reports WER with/without LIFT, n-best oracle, incl/excl the 6 test-train dups, and the leakage audit.
Weights/variant chosen on VAL, applied once to TEST.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import torch

from myovox.config import apply_config_and_logging
from myovox.decode.evaluate import split_refs
from myovox.paths import NBEST, OUT, CKPT, quarantine_test_indices
from myovox.rerank.data import SYS, build_user, norm, nb_file
from myovox.rerank.tune import corpus_wer, paired_bootstrap, acoustic_onebest_hyps


def load_model(base, adapter):
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(base)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    m = AutoModelForCausalLM.from_pretrained(base, quantization_config=bnb, device_map={"": 0}).eval()
    if adapter:
        m = PeftModel.from_pretrained(m, adapter)
    return m, tok


def prompt_ids(tok, u, topk, dev):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": build_user(u, topk)}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok(text, return_tensors="pt").input_ids.to(dev), text


@torch.no_grad()
def free_generate(m, tok, utts, topk, dev, max_new=40, batch=8):
    outs = []
    for i in range(0, len(utts), batch):
        chunk = utts[i:i + batch]
        texts = [prompt_ids(tok, u, topk, dev)[1] for u in chunk]
        enc = tok(texts, return_tensors="pt", padding=True, padding_side="left").to(dev)
        gen = m.generate(**enc, max_new_tokens=max_new, do_sample=False, num_beams=1,
                         pad_token_id=tok.pad_token_id)
        for j in range(len(chunk)):
            new = gen[j, enc["input_ids"].shape[1]:]
            outs.append(norm(tok.decode(new, skip_special_tokens=True)))
        if i % 200 == 0:
            print(f"  [free {i}/{len(utts)}]", flush=True)
    return outs


@torch.no_grad()
def constrained_rerank(m, tok, utts, topk, dev, batch=3):
    """For each utt, pick the candidate with the highest fine-tuned-model completion log-prob."""
    best = []
    for u in utts:
        cands = []
        seen = set()
        for c in u["cands"][:topk]:
            t = c["text"].lower()
            if t not in seen:
                seen.add(t); cands.append(t)
        if not cands:
            best.append(""); continue
        msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": build_user(u, topk)}]
        ptxt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        plen = tok(ptxt, return_tensors="pt").input_ids.shape[1]
        full = [ptxt + c for c in cands]
        scores = []
        for i in range(0, len(full), batch):
            ch = full[i:i + batch]
            enc = tok(ch, return_tensors="pt", padding=True).to(dev)
            logits = m(**enc).logits                       # (B,L,V) fp16 — avoid full float log_softmax
            ids, am = enc["input_ids"], enc["attention_mask"]
            shift = logits[:, :-1]
            lse = torch.logsumexp(shift.float(), -1)       # (B,L-1)
            tgt_logit = shift.gather(-1, ids[:, 1:].unsqueeze(-1)).squeeze(-1).float()
            tgt = tgt_logit - lse                          # per-token logprob
            mask = am[:, 1:].clone().float()
            mask[:, :plen - 1] = 0.0                       # score only the completion tokens
            scores.extend(((tgt * mask).sum(-1)).tolist())
        best.append(cands[int(torch.tensor(scores).argmax())])
    return best


def audit_recall(utts, hyps, refs):
    rec = 0
    for u, h, r in zip(utts, hyps, refs):
        cset = {c["text"].lower() for c in u["cands"]}
        if norm(h) == norm(r) and norm(r) not in {norm(x) for x in cset}:
            rec += 1
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nbset", required=True, help="val/test n-best set (e.g. ensA)")
    ap.add_argument("--base", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--adapter", default=str(CKPT / "lift_qwen"))
    ap.add_argument("--topk", type=int, default=10)
    ap.add_argument("--tag", default="lift")
    ap.add_argument("--val_lo", type=int, default=0,
                    help="evaluate/select on val[val_lo:] (the held-out part when LIFT trained on val[:val_lo])")
    args = apply_config_and_logging(ap)
    dev = "cuda:0"
    m, tok = load_model(args.base, args.adapter)
    print(f"[lift_infer] base={args.base} adapter={args.adapter} val_lo={args.val_lo}", flush=True)

    R, hyps = {}, {}
    for split in ("val", "test"):
        blob = torch.load(nb_file(args.nbset, split), map_location="cpu", weights_only=False)
        utts = blob["utts"]
        refs = list(split_refs(split)[0])[:len(utts)]
        if split == "val" and args.val_lo > 0:
            utts, refs = utts[args.val_lo:], refs[args.val_lo:]
        onebest = [u["cands"][0]["text"] if u["cands"] else "" for u in utts]
        free = free_generate(m, tok, utts, args.topk, dev)
        cons = constrained_rerank(m, tok, utts, args.topk, dev)
        hyps[split] = dict(utts=utts, refs=refs, onebest=onebest, free=free, cons=cons)
        R[f"{split}_nolift_wer"] = corpus_wer(refs, onebest)
        R[f"{split}_free_wer"] = corpus_wer(refs, free)
        R[f"{split}_cons_wer"] = corpus_wer(refs, cons)
        R[f"{split}_oracle"] = blob.get("report", {}).get("wer_oracle")
        R[f"{split}_free_recall"] = audit_recall(utts, free, refs)
        print(f"[{split}] no-LIFT={R[f'{split}_nolift_wer']*100:.2f}  free={R[f'{split}_free_wer']*100:.2f}"
              f"  cons={R[f'{split}_cons_wer']*100:.2f}  oracle={(R[f'{split}_oracle'] or 0)*100:.2f}"
              f"  free_recall={R[f'{split}_free_recall']}", flush=True)

    # variant selection on VAL
    variant = "free" if R["val_free_wer"] <= R["val_cons_wer"] else "cons"
    R["selected_variant"] = variant
    test_hyp = hyps["test"][variant]
    refs = hyps["test"]["refs"]
    R["test_lift_wer"] = corpus_wer(refs, test_hyp)
    # leakage / dup reporting
    q = set(quarantine_test_indices()); keep = [i for i in range(len(refs)) if i not in q]
    R["test_lift_wer_excl_dups"] = corpus_wer([refs[i] for i in keep], [test_hyp[i] for i in keep])
    R["test_lift_verbatim_recall"] = audit_recall(hyps["test"]["utts"], test_hyp, refs)
    # bootstrap vs legacy 26.14 and vs prior 20.13 one-best (== ensemble onebest here)
    base26 = acoustic_onebest_hyps("test")[:len(refs)]
    lo, hi, mn = paired_bootstrap(refs, base26, test_hyp)
    R["bootstrap_vs_26_ci"], R["bootstrap_vs_26_mean"] = (lo, hi), mn
    lo2, hi2, mn2 = paired_bootstrap(refs, hyps["test"]["onebest"], test_hyp)
    R["bootstrap_vs_onebest_ci"], R["bootstrap_vs_onebest_mean"] = (lo2, hi2), mn2

    (OUT / "B" / f"lift_report_{args.tag}.json").write_text(json.dumps(R, indent=2, default=float))
    with open(OUT / "B" / f"lift_test_hyps_{args.tag}.txt", "w") as f:
        for i, (r, h) in enumerate(zip(refs, test_hyp)):
            f.write(f"{i}\tREF\t{r}\n{i}\tHYP\t{h}\n")
    print(json.dumps(R, indent=2, default=float), flush=True)
    with open(OUT / "LEADERBOARD.md", "a") as f:
        ci = R["bootstrap_vs_26_ci"]
        f.write(f"| B-LIFT | LIFT {variant} ({args.tag}) on {args.nbset} | {R['test_lift_wer']*100:.2f} | "
                f"{R['test_nolift_wer']*100:.2f} | {(R['test_oracle'] or 0)*100:.2f} | "
                f"{R['val_'+variant+'_wer']*100:.2f} | [{ci[0]*100:+.2f},{ci[1]*100:+.2f}] vs26 | "
                f"excl-dups {R['test_lift_wer_excl_dups']*100:.2f}; recall {R['test_lift_verbatim_recall']} |\n")
    print("LIFT_INFER_DONE", flush=True)


if __name__ == "__main__":
    main()
