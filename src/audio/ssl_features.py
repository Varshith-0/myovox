"""Extract the WavLM distillation target for the headline.

Feeds raw audio at native rate through a HuggingFace SSL model and saves a chosen
hidden layer (~137.7 Hz features) as {layer, model, feats} to ckpts/main/ssl_<tag>.pt.
The headline uses microsoft/wavlm-large layer 9:

  python3 -m emg2text.ssl_features --model microsoft/wavlm-large --layer 9 --tag wl_l9
"""
import argparse, sys, time, pickle
from pathlib import Path
import numpy as np
import torch

from emg2text import config as C
from emg2text.decode import evaluate as V


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="microsoft/wavlm-large")
    ap.add_argument("--layer", type=int, default=9)
    ap.add_argument("--tag", required=True, help="output tag -> ckpts/main/ssl_<tag>.pt")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--norm", action="store_true", help="zero-mean/unit-var per utterance (feature-extractor style)")
    args = C.apply_config_and_logging(ap)
    out = V.CKPT_DIR / f"ssl_{args.tag}.pt"
    if out.exists():
        print(f"[extract_ssl] {out} exists; skip", flush=True); return

    from transformers import AutoModel
    device = torch.device(args.device)
    # force safetensors: transformers>=4.5 + torch<2.6 refuses to torch.load .bin checkpoints
    # (CVE-2025-32434); both wavlm-large and hubert-large have model.safetensors cached.
    model = AutoModel.from_pretrained(args.model, output_hidden_states=True,
                                      use_safetensors=True).to(device).eval()
    print(f"[extract_ssl] {args.model} layer {args.layer} -> {out}", flush=True)

    audio = pickle.load(open(C.DATA_ROOT / "groundTruthAudioFiles.pkl", "rb"))
    feats = []
    t0 = time.time()
    for i, wav in enumerate(audio):
        x = torch.tensor(np.asarray(wav), dtype=torch.float32, device=device) / 32768.0  # int16 -> [-1,1]
        if args.norm:
            x = (x - x.mean()) / (x.std() + 1e-7)
        hs = model(x.unsqueeze(0), output_hidden_states=True).hidden_states  # tuple (L+1) of (1,T,D)
        f = hs[args.layer][0].float().cpu()                                  # (T,D)
        feats.append(f)
        if i % 1000 == 0:
            print(f"  [{i}/{len(audio)}] T={f.shape[0]} D={f.shape[1]} ({time.time()-t0:.0f}s)", flush=True)
    torch.save({"layer": args.layer, "model": args.model, "feats": feats}, out)
    print(f"[extract_ssl] wrote {len(feats)} -> {out}  ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
