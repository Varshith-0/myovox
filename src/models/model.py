"""Bidirectional Conformer encoder (depthwise conv + self-attention) — the headline
temporal model for EMG -> phoneme decoding.

Uses the feature front-end (featuresNorm + RotationInvariantMLP) with two CTC heads
(unit + phoneme) and a WavLM distill projection, so the four cross-modal losses plus the
consistency loss all apply.  A torchaudio Conformer stack (self-attention is inherently
full-context; the depthwise conv supplies local context) is the temporal model.

forward(inputs, in_lens) -> dict {"unitLogprobs", "phoneLogprobs", "distill", "bottleneck"}.

Single-subject overfitting risk is real -> keep it small (4 layers) and select the
checkpoint by val PER.
"""
import torch
from torch import nn
import torch.nn.functional as F
from torchaudio.models import Conformer

from emg2text.models import frontend  # vendored: featuresNorm, RotationInvariantMLP
from emg2text import config
from emg2text.log import get_logger

log = get_logger(__name__)


class EMGConformer(nn.Module):
    def __init__(self, *, inFeatures, mlpFeatures,
                 numUnits=101, numPhones=41, unitBlank=100, phoneBlank=40,
                 electrodeChannels=31, bottleneckDim=512, ssl_dim=1024,
                 conf_layers=4, conf_heads=4, conf_ffn=1024, conf_kernel=31,
                 conf_dropout=0.1, **_ignore):
        super().__init__()
        self.C = electrodeChannels
        self.unitBlank = unitBlank
        self.phoneBlank = phoneBlank

        self.featNorm = frontend.featuresNorm(channels=self.C)
        self.riMlp = frontend.RotationInvariantMLP(
            inFeatures=inFeatures, mlpFeatures=mlpFeatures, pooling="mean", offsets=(-1, 0, 1))
        H = mlpFeatures[-1]
        self.conformer = Conformer(
            input_dim=H, num_heads=conf_heads, ffn_dim=conf_ffn,
            num_layers=conf_layers, depthwise_conv_kernel_size=conf_kernel,
            dropout=conf_dropout, use_group_norm=False, convolution_first=False)
        self.enc_norm = nn.LayerNorm(H)

        self.post = nn.Sequential(
            nn.LayerNorm(H), nn.GELU(), nn.Linear(H, bottleneckDim), nn.GELU(), nn.Dropout(0.5))
        self.unitHead = nn.Linear(bottleneckDim, numUnits)
        self.phoneHead = nn.Linear(bottleneckDim, numPhones)
        self.distill = nn.Linear(bottleneckDim, ssl_dim)

    def forward(self, inputs: torch.Tensor, in_lens=None):
        assert inputs.ndim == 4 and inputs.shape[2] == self.C and inputs.shape[3] == self.C, \
            f"Expected (N,T,{self.C},{self.C}), got {inputs.shape}"
        x = inputs.permute(1, 0, 2, 3).contiguous()   # (T,N,C,C)
        y = self.featNorm(x)
        y = self.riMlp(y)                              # (T,N,H)
        T, N, H = y.shape
        ycb = y.permute(1, 0, 2).contiguous()          # (N,T,H) for torchaudio Conformer
        if in_lens is not None:
            lengths = in_lens.detach().to(ycb.device, torch.int64).clamp(min=1, max=T)
        else:
            lengths = torch.full((N,), T, dtype=torch.int64, device=ycb.device)
        g, _ = self.conformer(ycb, lengths)            # (N,T,H), full-context
        g = g.permute(1, 0, 2).contiguous()            # (T,N,H)
        y = self.enc_norm(y + g)                        # residual + norm
        z = self.post(y)                                # (T,N,bottleneck)
        return {
            "unitLogprobs": F.log_softmax(self.unitHead(z), dim=-1),
            "phoneLogprobs": F.log_softmax(self.phoneHead(z), dim=-1),
            "distill": self.distill(z),
            "bottleneck": z,
        }

    @torch.no_grad()
    def warm_start_heads(self, seed_ckpt_path, device):
        """Warm-start from the upstream front-end seed (config.WARMSTART_SEED): copy the
        feature front-end (featNorm, riMlp) and output heads (post, unitHead, phoneHead)
        where shapes match; the Conformer temporal stack itself trains fresh."""
        sd = torch.load(seed_ckpt_path, map_location=device, weights_only=True)
        if any(k.startswith("base.") for k in sd):
            sd = {k[5:]: v for k, v in sd.items() if k.startswith("base.")}
        own = self.state_dict()
        prefixes = ("featNorm", "riMlp", "post", "unitHead", "phoneHead")
        copied = []
        for k in own:
            if k.startswith(prefixes) and k in sd and own[k].shape == sd[k].shape:
                own[k].copy_(sd[k]); copied.append(k)
        self.load_state_dict(own)
        log.info("warm-start: copied %d front-end/head tensors from %s", len(copied), seed_ckpt_path)


def build_model(device, **overrides):
    """Build the EMGConformer from config.MODEL_CFG, overridable per-call."""
    cfg = {**config.MODEL_CFG, **overrides}
    return EMGConformer(**cfg).to(device)
