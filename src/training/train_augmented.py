"""Phase 2 — acoustic PER reduction by attacking the generalization gap.

Legacy diagnosis: the Conformer memorizes (train PER ~4% vs val ~27%) on 8500 single-subject
sentences with essentially no augmentation; val PER plateaus ~27% from epoch ~19. We keep the
legacy 6-term cross-modal objective and ADD:

  (1) SPD-covariance augmentation (train only): time masking, electrode-subset dropout,
      symmetric covariance noise, and random change-of-basis C -> R C R^T (cross-subject shift
      is a change of basis; the vec() front-end is NOT basis-invariant, so this is real aug).
  (2) frame-level phone distillation: the frozen audio recognizer on the TIME-ALIGNED WavLM
      features gives dense per-frame phone posteriors (a forced-alignment-equivalent); KL-pull
      the EMG phone head toward them (lam_framekl).
  (3) heavier dropout + early stopping by val PER.

Writes all checkpoints/logits under the repo-root checkpoints/ and outputs/.
"""
import argparse, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

from myovox import config as C
from myovox.data import data as DATA
from myovox.models import losses as L
from myovox.decode import evaluate as V
from myovox.models.losses import distill_loss, crosscon_loss
from myovox.audio.teacher_conv import AudioRecognizer
from myovox.models.model import EMGConformer
from myovox.audio.teacher_bilstm import BiLSTMRecognizer
from myovox.paths import CKPT as NEWCKPT, OUT as NEWOUT
from myovox.runlog import RunLog

LABEL = "Phase2 Conformer + WavLM-L9 + aug + frameKL"


def augment_cov(inputs, in_lens, time_masks=2, time_frac=0.12, elec_drop=4,
                noise_std=0.01, rot_prob=0.5, rot_std=0.15):
    """Augment (B,T,31,31) covariance frames within each valid length (train only)."""
    B, T, Cc, _ = inputs.shape
    dev, dt = inputs.device, inputs.dtype
    eye = torch.eye(Cc, device=dev, dtype=dt)
    out = inputs.clone()
    for b in range(B):
        Lb = int(in_lens[b])
        if Lb < 4:
            continue
        for _ in range(time_masks):                       # time masking -> identity frames
            w = max(1, int(time_frac * Lb * float(torch.rand(1))))
            s = int(torch.randint(0, max(1, Lb - w), (1,)))
            out[b, s:s + w] = eye
        if elec_drop > 0:                                 # electrode-subset dropout
            k = int(torch.randint(0, elec_drop + 1, (1,)))
            if k > 0:
                idx = torch.randperm(Cc, device=dev)[:k]
                out[b, :Lb, idx, :] = 0.0
                out[b, :Lb, :, idx] = 0.0
                out[b, :Lb, idx, idx] = 1.0
        if noise_std > 0:                                 # symmetric covariance noise
            n = torch.randn(Lb, Cc, Cc, device=dev, dtype=dt) * noise_std
            out[b, :Lb] = out[b, :Lb] + 0.5 * (n + n.transpose(-1, -2))
        if rot_prob > 0 and float(torch.rand(1)) < rot_prob:   # change of basis C -> R C R^T
            Askew = torch.randn(Cc, Cc, device=dev, dtype=dt) * rot_std
            Askew = Askew - Askew.T
            R = torch.matrix_exp(Askew)
            out[b, :Lb] = R @ out[b, :Lb] @ R.T
    return out


def frame_kl_loss(emg_phone_TBP, audio_logp_BTfP, in_lens, phone_blank=C.PHONE_BLANK):
    """KL( audio-teacher || EMG-student ) per frame over the 40 NON-blank phones only.

    CTC teacher posteriors are blank-dominated; matching the full distribution (incl. blank)
    collapses the student to blank and destroys greedy-PER. So we drop blank, renormalize both
    sides over the 40 phones, and weight each frame by the teacher's non-blank mass (1 - p_blank)
    so silent frames contribute ~0 — this gives dense supervision only where a phone is present.
    """
    T_emg, B, P = emg_phone_TBP.shape
    emg = emg_phone_TBP.permute(1, 0, 2)                            # (B,T_emg,P) log-probs
    aud = F.interpolate(audio_logp_BTfP.permute(0, 2, 1), size=T_emg,
                        mode="linear", align_corners=False).permute(0, 2, 1)
    aud = aud - torch.logsumexp(aud, -1, keepdim=True)
    w = (1.0 - aud[..., phone_blank].exp()).detach()               # (B,T_emg) phone-frame weight
    keep = [c for c in range(P) if c != phone_blank]
    e = emg[..., keep]; a = aud[..., keep]
    e = e - torch.logsumexp(e, -1, keepdim=True)
    a = (a - torch.logsumexp(a, -1, keepdim=True)).detach()
    kl = (a.exp() * (a - e)).sum(-1)                               # (B,T_emg)
    mask = (torch.arange(T_emg, device=emg.device).unsqueeze(0) < in_lens.to(emg.device).unsqueeze(1)).float()
    wm = w * mask
    return (kl * wm).sum() / wm.sum().clamp_min(1.0)


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


@torch.no_grad()
def forward_split(model, split, device, d):
    lo, hi = V.split_slice(split)
    dl = DataLoader(DATA.make_dataset(d, lo, hi, False), batch_size=1, shuffle=False,
                    num_workers=4, collate_fn=DATA.make_eval_collate())
    model.eval(); out = []
    for inputs, phT, unT, in_lens, pl, ul in dl:
        o = model(inputs.to(device), in_lens.to(device))["phoneLogprobs"]
        for b in range(o.shape[1]):
            out.append(o[: int(in_lens[b]), b].cpu())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="p2_aug")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lam_distill", type=float, default=0.5)
    ap.add_argument("--lam_crosscon", type=float, default=0.5)
    ap.add_argument("--lam_recog", type=float, default=1.0)
    ap.add_argument("--lam_framekl", type=float, default=0.3)
    ap.add_argument("--tau", type=float, default=0.1)
    ap.add_argument("--conf_layers", type=int, default=4)
    ap.add_argument("--conf_dropout", type=float, default=0.2)
    ap.add_argument("--wd", type=float, default=3e-4)
    ap.add_argument("--patience", type=int, default=12)
    ap.add_argument("--device", default="cuda:0")
    # augmentation knobs
    ap.add_argument("--time_masks", type=int, default=2)
    ap.add_argument("--elec_drop", type=int, default=4)
    ap.add_argument("--noise_std", type=float, default=0.01)
    ap.add_argument("--rot_prob", type=float, default=0.5)
    ap.add_argument("--rot_std", type=float, default=0.15)
    ap.add_argument("--ssl_pt", default=str(C.CKPT_ROOT / "main" / "ssl_wl_l9.pt"))
    ap.add_argument("--recog_ckpt", default=str(C.CKPT_ROOT / "main" / "recog_wl_l9" / "best.pt"))
    ap.add_argument("--teacher_ckpt", default=str(NEWCKPT / "recog2_bilstm" / "best.pt"),
                    help="strong BiLSTM audio teacher for frame-KL (training.recognizer)")
    ap.add_argument("--warm_start", default=str(C.CKPT_ROOT / "baseline" / "epoch_30.pt"))
    ap.add_argument("--init_from", default="",
                    help="full EMGConformer ckpt to initialise the WHOLE model from (e.g. conf_l9 best); "
                         "overrides the warm_start head-copy. Use to continue-train an augmented member.")
    ap.add_argument("--max_epoch_batches", type=int, default=0, help=">0: smoke test")
    ap.add_argument("--train_lo", type=int, default=0)
    ap.add_argument("--train_hi", type=int, default=C.TRAIN_END)
    ap.add_argument("--xdecode_lo", type=int, default=-1, help=">=0: forward [xdecode_lo:xdecode_hi) after train (cross-decode)")
    ap.add_argument("--xdecode_hi", type=int, default=-1)
    args = C.apply_config_and_logging(ap)

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    ckpt_dir = NEWCKPT / args.name; ckpt_dir.mkdir(parents=True, exist_ok=True)
    tracker = RunLog(args.name, vars(args))   # NB: distinct name — `run` is the inner train/eval fn
    device = torch.device(args.device)

    d = DATA.load_all()
    feats = torch.load(args.ssl_pt, map_location="cpu", weights_only=False)["feats"]
    Dssl = int(feats[0].shape[-1])
    print(f"[{args.name}] ssl dim {Dssl}; aug(time={args.time_masks},elec={args.elec_drop},"
          f"noise={args.noise_std},rot={args.rot_prob}/{args.rot_std}) framekl={args.lam_framekl} "
          f"dropout={args.conf_dropout} wd={args.wd}", flush=True)

    coll = DATA.make_collate()
    tl = DataLoader(DATA.make_train_ds(d, args.train_lo, args.train_hi, True, feats), batch_size=args.batch,
                    shuffle=True, num_workers=args.workers, pin_memory=True, collate_fn=coll)
    vl = DataLoader(DATA.make_train_ds(d, C.TRAIN_END, C.VAL_END, False, feats), batch_size=args.batch,
                    shuffle=False, num_workers=args.workers, pin_memory=True, collate_fn=coll)
    val_syms = d["syms"][C.TRAIN_END:C.VAL_END]

    model = EMGConformer(ssl_dim=Dssl, conf_layers=args.conf_layers,
                                          conf_dropout=args.conf_dropout, **C.MODEL_CFG).to(device)
    if args.init_from and Path(args.init_from).exists():
        model.load_state_dict(torch.load(args.init_from, map_location=device, weights_only=True))
        print(f"[{args.name}] FULL init from {args.init_from}", flush=True)
    elif args.warm_start and Path(args.warm_start).exists():
        model.warm_start_heads(args.warm_start, device)
    print(f"[{args.name}] params={sum(p.numel() for p in model.parameters() if p.requires_grad):,}", flush=True)

    recog = AudioRecognizer(in_dim=Dssl, num_classes=C.PHONE_BLANK + 1).to(device)
    recog.load_state_dict(torch.load(args.recog_ckpt, map_location=device, weights_only=True))
    recog.eval()
    for p in recog.parameters(): p.requires_grad_(False)

    teacher = None
    if args.lam_framekl > 0:
        teacher = BiLSTMRecognizer(in_dim=Dssl, num_classes=C.PHONE_BLANK + 1).to(device)
        teacher.load_state_dict(torch.load(args.teacher_ckpt, map_location=device, weights_only=True))
        teacher.eval()
        for p in teacher.parameters(): p.requires_grad_(False)
        print(f"[{args.name}] frame-KL teacher: {args.teacher_ckpt}", flush=True)

    A = L.build_A()
    ctc_u = nn.CTCLoss(blank=C.UNIT_BLANK, zero_infinity=True)
    ctc_p = nn.CTCLoss(blank=C.PHONE_BLANK, zero_infinity=True)
    opt = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd, betas=(0.9, 0.98))
    sched = torch.optim.lr_scheduler.SequentialLR(
        opt, schedulers=[
            torch.optim.lr_scheduler.LinearLR(opt, start_factor=0.1, total_iters=args.warmup),
            torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(1, args.epochs - args.warmup), eta_min=1e-6)],
        milestones=[args.warmup])

    def run(loader, train):
        model.train() if train else model.eval()
        tot = 0.0; nb = 0
        ctx = torch.enable_grad() if train else torch.no_grad()
        with ctx:
            for bi, (inputs, phT, unT, in_lens, pl, ul, fe, fl) in enumerate(loader):
                if train and args.max_epoch_batches and bi >= args.max_epoch_batches:
                    break
                inputs = inputs.to(device); phT = phT.to(device); unT = unT.to(device)
                in_lens = in_lens.to(device, torch.long); pl = pl.to(device, torch.long); ul = ul.to(device, torch.long)
                fe = fe.to(device); fl = fl.to(device, torch.long)
                if train:
                    inputs = augment_cov(inputs, in_lens, args.time_masks, 0.12, args.elec_drop,
                                         args.noise_std, args.rot_prob, args.rot_std)
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
                if args.lam_framekl > 0:
                    T_emg = out["phoneLogprobs"].shape[0]            # align audio teacher to EMG 50Hz grid
                    fe_ds = F.interpolate(fe.transpose(1, 2), size=T_emg, mode="linear",
                                          align_corners=False).transpose(1, 2)
                    aud = teacher(fe_ds)                             # (B,T_emg,P) audio phone log-probs
                    lfk = frame_kl_loss(out["phoneLogprobs"], aud, in_lens)
                else:
                    lfk = torch.zeros((), device=device)
                loss = (C.LAM_UNIT * lu + C.LAM_PHONE * lp + C.LAM_CONS * lc
                        + args.lam_distill * ld + args.lam_crosscon * lcc + args.lam_recog * lrec
                        + args.lam_framekl * lfk)
                if train:
                    loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
                tot += float(loss); nb += 1
        return tot / max(1, nb)

    hist = []; best_per = 1e9; best_ep = 0; bad = 0
    for ep in range(1, args.epochs + 1):
        tl.dataset.emg.resampleJitter(seed=None)
        t0 = time.time()
        tr = run(tl, True); va = run(vl, False)
        vper = greedy_per(model, vl, device, val_syms, d["phone_def"])
        sched.step()
        torch.save(model.state_dict(), ckpt_dir / f"epoch_{ep:02d}.pt")
        hist.append(dict(ep=ep, train=tr, val=va, val_PER=vper))
        np.save(ckpt_dir / "history.npy", np.array(hist, dtype=object), allow_pickle=True)
        flag = ""
        if vper < best_per - 1e-4:
            best_per, best_ep, bad = vper, ep, 0; flag = " *best*"
            torch.save(model.state_dict(), ckpt_dir / "best.pt")
        else:
            bad += 1
        print(f"[{args.name} ep {ep:02d}/{args.epochs}] {time.time()-t0:.0f}s "
              f"train={tr:.3f} val={va:.3f} valPER={vper*100:.2f}%{flag} (best {best_per*100:.2f}@{best_ep})", flush=True)
        tracker.log(epoch=ep, train=tr, val=va, val_PER=vper, best_val_PER=best_per)
        if args.max_epoch_batches:
            break
        if bad >= args.patience:
            print(f"[{args.name}] early stop at ep{ep} (no val-PER improvement for {bad})", flush=True)
            break

    (ckpt_dir / "best.txt").write_text(f"best_by_val_PER={best_ep}\nbest_val_PER={best_per:.4f}\n")
    tracker.finish(best_epoch=best_ep, best_val_PER=best_per)
    print(f"[{args.name}] best-by-valPER ep{best_ep} (PER {best_per*100:.2f}%)", flush=True)
    if args.max_epoch_batches:
        return
    model.load_state_dict(torch.load(ckpt_dir / "best.pt", map_location=device, weights_only=True))
    # cross-decode: forward the held-out range (utts this model did NOT train on) -> realistic logits
    if args.xdecode_lo >= 0:
        ds = DATA.make_dataset(d, args.xdecode_lo, args.xdecode_hi, False)
        dl = DataLoader(ds, batch_size=1, shuffle=False, num_workers=4, collate_fn=DATA.make_eval_collate())
        model.eval(); xo = []
        with torch.no_grad():
            for inputs, phT, unT, in_lens, pl, ul in dl:
                o = model(inputs.to(device), in_lens.to(device))["phoneLogprobs"]
                xo.append(o[: int(in_lens[0]), 0].cpu())
        torch.save({"xdecode": xo, "lo": args.xdecode_lo, "hi": args.xdecode_hi},
                   NEWOUT / f"{args.name}_xdecode_logits.pt")
        print(f"[{args.name}] saved xdecode logits [{args.xdecode_lo}:{args.xdecode_hi}] (n={len(xo)})", flush=True)
        print("XDECODE_DONE", flush=True)
        return
    # decode best through the legacy WFST (val-tuned scale), save logits to outputs/
    val_lp = forward_split(model, "val", device, d)
    test_lp = forward_split(model, "test", device, d)
    out = NEWOUT / f"{args.name}_logits.pt"
    torch.save({"val": val_lp, "test": test_lp}, out)
    print(f"[{args.name}] saved logits -> {out}", flush=True)
    res = V.tune_scale_then_test(val_lp, test_lp)
    print(f"[{args.name}] ACOUSTIC-STACK: val WER={res['val_wer']*100:.2f} "
          f"test WER={res['test_wer']*100:.2f} test PER={res['test_per']*100:.2f} (scale {res['scale']})", flush=True)
    (NEWOUT / f"{args.name}_acoustic_result.txt").write_text(str(res))


if __name__ == "__main__":
    main()
