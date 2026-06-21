"""Headline trainer: bidirectional Conformer + WavLM-L9 cross-modal distillation.

Trains the EMG -> phoneme Conformer with the multitask CTC objective plus three cross-modal
distillation terms (six terms total, below), selects the checkpoint by validation PER, then
decodes it through the WFST (acoustic scale tuned on val, applied once to test).  Reproduces
the headline: 26.14 % test WER / 22.34 % test PER.

  Loss = LAM_UNIT*CTC_unit + LAM_PHONE*CTC_phone + LAM_CONS*consistency        (multitask CTC)
       + lam_distill*L2(proj, WavLM-L9)                                        (cross-modal i)
       + lam_crosscon*InfoNCE(proj, WavLM-L9)                                  (cross-modal ii)
       + lam_recog*CTC(frozen WavLM-L9->phone recognizer(proj), phones)        (cross-modal iv)

Inputs (all under checkpoints/main by default — see scripts/run_headline.sh to build them):
  --ssl_pt       WavLM-Large layer-9 features        (emg2text.ssl_features)
  --recog_ckpt   frozen WavLM-L9 -> phone recognizer (emg2text.teacher_conv)
  --warm_start   small DualHead baseline ckpt (checkpoints/baseline/epoch_30.pt) that warm-starts
                 the feature front-end + CTC heads; '' trains everything from scratch

CAVEAT (single subject, ~8,500 sentences): the Conformer memorises the train set hard
(train PER ~4 % vs val ~27 %); the val-PER-selected checkpoint still generalises (the test
win is bootstrap-significant), but cross-subject robustness is untested.
"""
import argparse, time, sys
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from emg2text import config as C
from emg2text.data import data as DATA
from emg2text.models import losses as L
from emg2text.decode import evaluate as V
from emg2text.models.losses import distill_loss, crosscon_loss
from emg2text.audio.teacher_conv import AudioRecognizer
from emg2text.models.model import EMGConformer
from emg2text.runlog import RunLog
from emg2text.paths import artifact_name

LABEL = "Conformer + WavLM-L9 (headline, acoustic-only)"


def _link_provenance(name, ep, val_per):
    """Create a provenance-named symlink to the stable {name}_logits.pt (run.sh reads the stable name)."""
    src = V.RESULTS_DIR / f"{name}_logits.pt"
    link = V.RESULTS_DIR / artifact_name("logits", arch="conformer", tag=name, ep=ep, val_per=val_per)
    try:
        if src.exists() and not link.exists():
            link.symlink_to(src.name)
    except OSError:
        pass


@torch.no_grad()
def greedy_per(model, loader, device, syms, phone_def):
    import Levenshtein
    model.eval(); td = tl = idx = 0
    for inputs, phT, unT, in_lens, pl, ul, fe, fl in loader:
        o = model(inputs.to(device), in_lens.to(device))["phoneLogprobs"]
        for b in range(o.shape[1]):
            g = o[: int(in_lens[b]), b].argmax(-1).cpu().numpy()
            hyp, prev = [], -1
            for t in g:
                if t != C.PHONE_BLANK and t != prev: hyp.append(int(t))
                prev = int(t)
            ref = [phone_def[p] - 1 for p in syms[idx]]
            td += Levenshtein.distance(hyp, ref); tl += len(ref); idx += 1
    return td / max(1, tl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="conf_l9")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lam_distill", type=float, default=0.5)
    ap.add_argument("--lam_crosscon", type=float, default=0.5)
    ap.add_argument("--lam_recog", type=float, default=1.0)
    ap.add_argument("--tau", type=float, default=0.1)
    ap.add_argument("--conf_layers", type=int, default=4)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--ssl_pt", default=str(V.CKPT_DIR / "ssl_wl_l9.pt"))
    ap.add_argument("--recog_ckpt", default=str(V.CKPT_DIR / "recog_wl_l9" / "best.pt"))
    ap.add_argument("--warm_start", default=str(C.CKPT_ROOT / "baseline" / "epoch_30.pt"),
                    help="DualHead ckpt to warm-start featNorm/riMlp/heads ('' = from scratch)")
    ap.add_argument("--decode_only", default="", help="ckpt path: skip training, just decode+score")
    args = C.apply_config_and_logging(ap)

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    ckpt_dir = V.CKPT_DIR / args.name; ckpt_dir.mkdir(parents=True, exist_ok=True)
    tracker = RunLog(args.name, vars(args))   # NB: distinct name — `run` is the inner train/eval fn
    device = torch.device(args.device)

    d = DATA.load_all()
    feats = torch.load(args.ssl_pt, map_location="cpu", weights_only=False)["feats"]
    Dssl = int(feats[0].shape[-1])
    print(f"[{args.name}] ssl={args.ssl_pt} (dim {Dssl})", flush=True)

    coll = DATA.make_collate()
    tl = DataLoader(DATA.make_train_ds(d, 0, C.TRAIN_END, True, feats), batch_size=args.batch,
                    shuffle=True, num_workers=args.workers, pin_memory=True, collate_fn=coll)
    vl = DataLoader(DATA.make_train_ds(d, C.TRAIN_END, C.VAL_END, False, feats), batch_size=args.batch,
                    shuffle=False, num_workers=args.workers, pin_memory=True, collate_fn=coll)
    val_syms = d["syms"][C.TRAIN_END:C.VAL_END]

    model = EMGConformer(ssl_dim=Dssl, conf_layers=args.conf_layers, **C.MODEL_CFG).to(device)
    if args.warm_start and not args.decode_only and Path(args.warm_start).exists():
        model.warm_start_heads(args.warm_start, device)
    elif not args.warm_start:
        print(f"[{args.name}] training from scratch (no warm start)", flush=True)
    print(f"[{args.name}] params={sum(p.numel() for p in model.parameters() if p.requires_grad):,}", flush=True)

    if args.decode_only:
        model.load_state_dict(torch.load(args.decode_only, map_location=device, weights_only=True))
        decode_and_score(model, device, args.name, args.decode_only, args.seed, d)
        return

    recog = AudioRecognizer(in_dim=Dssl, num_classes=C.PHONE_BLANK + 1).to(device)
    recog.load_state_dict(torch.load(args.recog_ckpt, map_location=device, weights_only=True))
    recog.eval()
    for p in recog.parameters(): p.requires_grad_(False)
    print(f"[{args.name}] loaded frozen audio recognizer {args.recog_ckpt}", flush=True)

    A = L.build_A()
    ctc_u = nn.CTCLoss(blank=C.UNIT_BLANK, zero_infinity=True)
    ctc_p = nn.CTCLoss(blank=C.PHONE_BLANK, zero_infinity=True)
    opt = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4, betas=(0.9, 0.98))
    sched = torch.optim.lr_scheduler.SequentialLR(
        opt, schedulers=[
            torch.optim.lr_scheduler.LinearLR(opt, start_factor=0.1, total_iters=args.warmup),
            torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs - args.warmup, eta_min=1e-6)],
        milestones=[args.warmup])

    def run(loader, train):
        model.train() if train else model.eval()
        tot = 0.0
        ctx = torch.enable_grad() if train else torch.no_grad()
        with ctx:
            for inputs, phT, unT, in_lens, pl, ul, fe, fl in loader:
                inputs = inputs.to(device); phT = phT.to(device); unT = unT.to(device)
                in_lens = in_lens.to(device, torch.long); pl = pl.to(device, torch.long); ul = ul.to(device, torch.long)
                fe = fe.to(device); fl = fl.to(device, torch.long)
                ph1d = DATA.cat_targets(phT, pl); un1d = DATA.cat_targets(unT, ul)
                if train: opt.zero_grad(set_to_none=True)
                out = model(inputs, in_lens)
                lu = ctc_u(out["unitLogprobs"], un1d, in_lens, ul)
                lp = ctc_p(out["phoneLogprobs"], ph1d, in_lens, pl)
                lc = L.consistency_loss(out["unitLogprobs"], out["phoneLogprobs"], A, lengths=in_lens)
                ld = distill_loss(out["distill"], fe, fl)
                lcc = crosscon_loss(out["distill"], fe, in_lens, tau=args.tau)
                recog_lp = recog(out["distill"].permute(1, 0, 2)).transpose(0, 1)
                rec_lens = torch.clamp(in_lens, max=recog_lp.shape[0])
                lrec = ctc_p(recog_lp, ph1d, rec_lens, pl)
                loss = (C.LAM_UNIT * lu + C.LAM_PHONE * lp + C.LAM_CONS * lc
                        + args.lam_distill * ld + args.lam_crosscon * lcc + args.lam_recog * lrec)
                if train:
                    loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
                tot += float(loss)
        return tot / max(1, len(loader))

    hist = []
    for ep in range(1, args.epochs + 1):
        tl.dataset.emg.resampleJitter(seed=None)
        t0 = time.time()
        tr = run(tl, True); va = run(vl, False)
        vper = greedy_per(model, vl, device, val_syms, d["phone_def"])
        sched.step()
        torch.save(model.state_dict(), ckpt_dir / f"epoch_{ep:02d}.pt")
        hist.append(dict(ep=ep, train=tr, val=va, val_PER=vper))
        np.save(ckpt_dir / "history.npy", np.array(hist, dtype=object), allow_pickle=True)
        print(f"[{args.name} ep {ep:02d}/{args.epochs}] {time.time()-t0:.0f}s "
              f"train={tr:.3f} val={va:.3f} valPER={vper*100:.2f}%", flush=True)
        tracker.log(epoch=ep, train=tr, val=va, val_PER=vper)

    best = min(hist, key=lambda h: h["val_PER"])
    (ckpt_dir / "best.txt").write_text(f"best_by_val_PER={best['ep']}\nbest_val_PER={best['val_PER']:.4f}\n")
    print(f"[{args.name}] best-by-valPER ep{best['ep']} (PER {best['val_PER']*100:.2f}%)", flush=True)
    best_ckpt = ckpt_dir / f"epoch_{best['ep']:02d}.pt"
    model.load_state_dict(torch.load(best_ckpt, map_location=device, weights_only=True))
    tracker.finish(best_epoch=best["ep"], best_val_PER=best["val_PER"])
    decode_and_score(model, device, args.name, str(best_ckpt), args.seed, d)
    _link_provenance(args.name, best["ep"], best["val_PER"])


def decode_and_score(model, device, name, ckpt, seed, d):
    """Forward val+test -> save logits -> decode+score in a fresh subprocess (val-tune scale)."""
    print(f"[{name}] forwarding val+test for WFST decode ...", flush=True)
    val_lp = _forward(model, "val", device, d)
    test_lp = _forward(model, "test", device, d)
    out = V.RESULTS_DIR / f"{name}_logits.pt"
    torch.save({"val": val_lp, "test": test_lp}, out)
    del model
    torch.cuda.empty_cache()
    V.subprocess_eval(out, LABEL, track="acoustic-only", ckpt=ckpt, seed=seed)


@torch.no_grad()
def _forward(model, split, device, d):
    lo, hi = V.split_slice(split)
    dl = DataLoader(DATA.make_dataset(d, lo, hi, False), batch_size=1, shuffle=False,
                    num_workers=4, collate_fn=DATA.make_eval_collate())
    model.eval(); out = []
    for inputs, phT, unT, in_lens, pl, ul in dl:
        o = model(inputs.to(device), in_lens.to(device))["phoneLogprobs"]
        for b in range(o.shape[1]):
            out.append(o[: int(in_lens[b]), b].cpu())
    return out


if __name__ == "__main__":
    main()
