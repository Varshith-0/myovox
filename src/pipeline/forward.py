"""Forward a list of Conformer checkpoints -> save each one's {val,test} phone logits under outputs/.
Enables snapshot ensembling (cheap decorrelated members from late epochs of a run)."""
import argparse
import torch
from myovox import config as C
from myovox.data import data as DATA
from myovox.models.model import EMGConformer
from myovox.training.train_augmented import forward_split
from myovox.paths import OUT as NEWOUT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", nargs="+", required=True, help="checkpoint .pt paths")
    ap.add_argument("--tags", nargs="+", required=True, help="output tag per ckpt (logits -> NEWOUT/{tag}_logits.pt)")
    ap.add_argument("--ssl_dim", type=int, default=1024)
    ap.add_argument("--conf_dropout", type=float, default=0.15)
    ap.add_argument("--splits", default="val,test")
    args = ap.parse_args()
    assert len(args.ckpts) == len(args.tags)
    splits = args.splits.split(",")
    dev = "cuda:0"
    d = DATA.load_all(verbose=False)
    model = EMGConformer(ssl_dim=args.ssl_dim, conf_dropout=args.conf_dropout, **C.MODEL_CFG).to(dev)
    for ck, tag in zip(args.ckpts, args.tags):
        sd = torch.load(ck, map_location=dev, weights_only=True)
        model.load_state_dict(sd)
        blob = {s: forward_split(model, s, dev, d) for s in splits}
        out = NEWOUT / f"{tag}_logits.pt"
        torch.save(blob, out)
        print(f"forwarded {ck} splits={splits} -> {out}", flush=True)
    print("FWD_DONE", flush=True)


if __name__ == "__main__":
    main()
