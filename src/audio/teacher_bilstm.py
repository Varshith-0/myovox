"""Strong audio->phone teacher (the base recognizer is ~54% PER; the audio is good,
Whisper transcribes it ~correctly). A 3-layer BiLSTM over WavLM-L9 features gives long context
+ much lower PER, suitable for dense distillation into the EMG model. Writes to checkpoints/.
"""
import argparse, time
import torch, torch.nn as nn, torch.nn.functional as F, torch.optim as optim
from torch.utils.data import DataLoader
import Levenshtein

from emg2text import config as C
from emg2text.data import data as DATA
from emg2text.audio.teacher_conv import WavLMPhonemeDS, collate
from emg2text.paths import CKPT as NEWCKPT


class BiLSTMRecognizer(nn.Module):
    def __init__(self, in_dim=1024, hid=512, layers=3, num_classes=41, dropout=0.3):
        super().__init__()
        self.ln = nn.LayerNorm(in_dim)
        self.drop = nn.Dropout(dropout)
        self.rnn = nn.LSTM(in_dim, hid, num_layers=layers, batch_first=True,
                           bidirectional=True, dropout=dropout)
        self.fc = nn.Linear(2 * hid, num_classes)

    def forward(self, x):
        x = self.drop(self.ln(x))
        x, _ = self.rnn(x)
        return F.log_softmax(self.fc(x), dim=-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ssl_pt", default=str(C.CKPT_ROOT / "main" / "ssl_wl_l9.pt"))
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--name", default="recog2_bilstm")
    args = C.apply_config_and_logging(ap)
    out = NEWCKPT / args.name; out.mkdir(parents=True, exist_ok=True)
    dev = "cuda:0"

    d = DATA.load_all()
    feats = torch.load(args.ssl_pt, map_location="cpu", weights_only=False)["feats"]
    tl = DataLoader(WavLMPhonemeDS(feats, d["syms"], d["phone_def"], 0, C.TRAIN_END),
                    batch_size=args.batch, shuffle=True, num_workers=3, collate_fn=collate)
    vl = DataLoader(WavLMPhonemeDS(feats, d["syms"], d["phone_def"], C.TRAIN_END, C.VAL_END),
                    batch_size=args.batch, shuffle=False, num_workers=3, collate_fn=collate)
    model = BiLSTMRecognizer().to(dev)
    print(f"[{args.name}] params={sum(p.numel() for p in model.parameters()):,}", flush=True)
    ctc = nn.CTCLoss(blank=C.PHONE_BLANK, zero_infinity=True)
    opt = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)
    best = 1.0; t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train(); tot = n = 0
        for Ft, Lt, Fl, Ll in tl:
            Ft, Lt, Fl, Ll = Ft.to(dev), Lt.to(dev), Fl.to(dev), Ll.to(dev)
            lp = model(Ft).transpose(0, 1)
            L_ = torch.cat([Lt[i, :int(Ll[i])] for i in range(Lt.shape[0])])
            loss = ctc(lp, L_, Fl, Ll)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            tot += float(loss); n += 1
        sched.step()
        model.eval(); td = tll = 0
        with torch.no_grad():
            for Ft, Lt, Fl, Ll in vl:
                lp = model(Ft.to(dev)).cpu()
                for b in range(lp.shape[0]):
                    g = lp[b, :int(Fl[b])].argmax(-1).numpy(); hyp, prev = [], -1
                    for t in g:
                        if t != C.PHONE_BLANK and t != prev: hyp.append(int(t))
                        prev = int(t)
                    ref = [int(Lt[b, j]) for j in range(int(Ll[b]))]
                    td += Levenshtein.distance(hyp, ref); tll += len(ref)
        per = td / max(1, tll)
        flag = ""
        if per < best:
            best = per; torch.save(model.state_dict(), out / "best.pt"); flag = " *best*"
        print(f"[{args.name} ep {ep:02d}/{args.epochs}] {time.time()-t0:.0f}s train={tot/max(1,n):.3f} val_PER={per*100:.2f}%{flag}", flush=True)
    print(f"RECOG2_DONE best_val_PER={best*100:.2f}%", flush=True)


if __name__ == "__main__":
    main()
