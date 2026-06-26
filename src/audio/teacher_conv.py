"""Cross-modal loss term iv prereq: small CTC phoneme recognizer on WavLM features.

Trains a frozen "audio recognizer" that decodes WavLM-L9 features (downsampled to
50 Hz to match the EMG frame rate) into phoneme CTC logits. The headline trainer then
forces the EMG projection through this frozen recognizer with a CTC loss vs the same
phoneme targets — so the projection must be phoneme-DECODABLE, not merely close
to WavLM (guards against L2-regression-blur).
"""
import argparse, sys, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import Levenshtein

from myovox import config as C
from myovox.data import data as DATA


class AudioRecognizer(nn.Module):
    """LayerNorm + 2 Conv1d blocks (k=5) + Linear -> phoneme CTC logits."""
    def __init__(self, in_dim=1024, hid=512, num_classes=41):
        super().__init__()
        self.ln = nn.LayerNorm(in_dim)
        self.c1 = nn.Conv1d(in_dim, hid, kernel_size=5, padding=2)
        self.c2 = nn.Conv1d(hid, hid, kernel_size=5, padding=2)
        self.fc = nn.Linear(hid, num_classes)

    def forward(self, x):
        # x: (B, T, D)
        x = self.ln(x).transpose(1, 2)
        x = F.gelu(self.c1(x))
        x = F.gelu(self.c2(x))
        x = x.transpose(1, 2)
        return F.log_softmax(self.fc(x), dim=-1)         # (B, T, num_classes)


WAVLM_HZ = 137.7
TARGET_HZ = 50.0


def downsample(f, target_hz=TARGET_HZ, wavlm_hz=WAVLM_HZ):
    """f: (T, D) at WAVLM_HZ -> (T', D) at target_hz."""
    T_new = max(1, int(round(f.shape[0] * target_hz / wavlm_hz)))
    return F.interpolate(f.unsqueeze(0).transpose(1, 2), size=T_new,
                         mode="linear", align_corners=False).transpose(1, 2).squeeze(0)


class WavLMPhonemeDS(Dataset):
    def __init__(self, feats, syms, phone_def, lo, hi):
        self.feats = feats[lo:hi]
        self.syms = syms[lo:hi]
        self.phone_def = phone_def

    def __len__(self): return len(self.feats)

    def __getitem__(self, i):
        f_d = downsample(self.feats[i])
        ph = [self.phone_def[p] - 1 for p in self.syms[i]]
        return f_d, torch.tensor(ph, dtype=torch.long)


def collate(batch):
    feats, labs = zip(*batch)
    Tm = max(int(f.shape[0]) for f in feats); D = int(feats[0].shape[-1])
    Lm = max(int(l.shape[0]) for l in labs)
    Ft = torch.zeros((len(batch), Tm, D), dtype=torch.float32)
    Lt = torch.zeros((len(batch), Lm), dtype=torch.long)
    Fl = torch.zeros(len(batch), dtype=torch.long)
    Ll = torch.zeros(len(batch), dtype=torch.long)
    for i, (f, l) in enumerate(zip(feats, labs)):
        Ft[i, :f.shape[0]] = f; Lt[i, :l.shape[0]] = l
        Fl[i] = int(f.shape[0]); Ll[i] = int(l.shape[0])
    return Ft, Lt, Fl, Ll


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ssl_pt", default=str(C.CKPT_ROOT / "main" / "ssl_wl_l9.pt"))
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--out", default=str(C.CKPT_ROOT / "main" / "recog_wl_l9"))
    args = C.apply_config_and_logging(ap)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    d = DATA.load_all()
    feats = torch.load(args.ssl_pt, map_location="cpu", weights_only=False)["feats"]
    print(f"loaded {len(feats)} WavLM features  (downsampled {WAVLM_HZ:.1f} -> {TARGET_HZ} Hz)", flush=True)

    train_ds = WavLMPhonemeDS(feats, d["syms"], d["phone_def"], 0, C.TRAIN_END)
    val_ds = WavLMPhonemeDS(feats, d["syms"], d["phone_def"], C.TRAIN_END, C.VAL_END)
    tl = DataLoader(train_ds, batch_size=args.batch, shuffle=True, num_workers=2, collate_fn=collate)
    vl = DataLoader(val_ds, batch_size=args.batch, shuffle=False, num_workers=2, collate_fn=collate)

    device = torch.device("cuda:0")
    model = AudioRecognizer().to(device)
    print(f"recognizer params: {sum(p.numel() for p in model.parameters()):,}", flush=True)
    ctc = nn.CTCLoss(blank=C.PHONE_BLANK, zero_infinity=True)
    opt = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

    best = 1.0; t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train(); tot, n = 0.0, 0
        for Ft, Lt, Fl, Ll in tl:
            Ft, Lt, Fl, Ll = Ft.to(device), Lt.to(device), Fl.to(device), Ll.to(device)
            lp = model(Ft).transpose(0, 1)                        # (T, B, C)
            L_ = torch.cat([Lt[i, :int(Ll[i])] for i in range(Lt.shape[0])])
            loss = ctc(lp, L_, Fl, Ll)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            tot += float(loss); n += 1
        sched.step()
        # val PER
        model.eval(); td = tl_ = 0
        with torch.no_grad():
            for Ft, Lt, Fl, Ll in vl:
                Ft = Ft.to(device)
                lp = model(Ft).cpu()
                for b in range(lp.shape[0]):
                    g = lp[b, :int(Fl[b])].argmax(-1).numpy(); hyp, prev = [], -1
                    for t in g:
                        if t != C.PHONE_BLANK and t != prev: hyp.append(int(t))
                        prev = int(t)
                    ref = [int(Lt[b, j]) for j in range(int(Ll[b]))]
                    td += Levenshtein.distance(hyp, ref); tl_ += len(ref)
        per = td / max(1, tl_)
        print(f"[recog ep {ep:02d}/{args.epochs}] {time.time()-t0:.0f}s "
              f"train={tot/max(1,n):.3f} val_PER={per*100:.2f}%", flush=True)
        if per < best:
            best = per
            torch.save(model.state_dict(), out / "best.pt")
            print(f"  -> new best @ val_PER={per*100:.2f}%", flush=True)

    print(f"AUDIO_RECOG_DONE  best_val_PER={best*100:.2f}%", flush=True)


if __name__ == "__main__":
    main()
