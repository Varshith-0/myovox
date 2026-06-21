"""EMG feature front-end: per-channel norm + rotation-invariant MLP.

Turns a 31x31 SPD covariance window into a 384-dim frame embedding that the
Conformer (model.py) consumes. Two small modules:
  * featuresNorm           — BatchNorm2d over the covariance grid, per sample.
  * RotationInvariantMLP   — MLP pooled over electrode rotations (offsets -1,0,1).

VENDORED, unmodified, from the upstream emg2speech reference implementation
(Gowda et al., "emg2speech: synthesizing speech from electromyography using
self-supervised speech models"; frontend.py). Kept verbatim so the front-end
stays byte-faithful to the paper. See README "Provenance & license".
"""
import torch
from torch import nn


class featuresNorm(nn.Module):
    """
    Expect input: (T, N, C, C')
    Applies BatchNorm2d over (C', T) for each channel C, independently per sample N.
    """
    def __init__(self, channels: int, eps: float = 1e-5, momentum: float = 0.1, affine: bool = True) -> None:
        super().__init__()
        self.channels = channels
        self.bn2d = nn.BatchNorm2d(channels, eps=eps, momentum=momentum, affine=affine)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.ndim == 4, f"featuresNorm expects (T,N,C,C), got {x.shape}"
        T, N, C, _ = x.shape
        assert C == self.channels, f"BatchNorm2d expects C={self.channels}, got {C}"

        x = x.movedim(0, -1)
        x = self.bn2d(x)
        x = x.movedim(-1, 0).contiguous()
        return x


class RotationInvariantMLP(nn.Module):

    def __init__(self, inFeatures: int, mlpFeatures, pooling: str = "mean", offsets=(-1, 0, 1)) -> None:
        super().__init__()
        assert len(mlpFeatures) > 0
        layers = []
        fin = inFeatures
        for fout in mlpFeatures:
            layers += [nn.Linear(fin, fout), nn.ReLU()]
            fin = fout
        self.mlp = nn.Sequential(*layers)
        assert pooling in {"max", "mean"}
        self.pooling = pooling
        self.offsets = offsets if len(offsets) > 0 else (0,)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.ndim == 4, f"RotationInvariantMLP expects (T,N,C,C), got {x.shape}"
        x = torch.stack([x.roll(off, dims=2) for off in self.offsets], dim=2)
        x = self.mlp(x.flatten(start_dim=3))
        return x.max(dim=2).values if self.pooling == "max" else x.mean(dim=2)
