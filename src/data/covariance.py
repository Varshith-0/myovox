"""EpochJitterEMGDataset + computeConvSeq: SPD covariance feature pipeline.

VENDORED, unmodified, from the upstream emg2speech reference implementation
(Gowda et al.; emgJitter.py).  Builds the (F, C, C) shrinkage-covariance feature
sequence from raw EMG with epoch jitter.  Kept verbatim for byte-faithful
reproduction; see README "Provenance & license" and the upstream repo licence.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import torch
from torch.utils.data import Dataset

@torch.no_grad()
def computeConvSeq(
    X: torch.Tensor,
    *,
    fs: int,
    winMs: float,
    hopMs: float,
    phase: int = 0,
    shrinkAlpha: float = 0.1,
    diag: bool = False,
    diagOnly: bool = False,
    logDiag: bool = True,                       
    eps: float = 1e-12,                         
    eigenvectors: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, int]:
    C, T = X.shape
    win = int(round(winMs * fs / 1000.0))
    hop = int(round(hopMs * fs / 1000.0))
    if win <= 0 or hop <= 0:
        raise ValueError("winMs and hopMs must produce positive sample sizes")

    if T <= 0:
        covSeq = torch.eye(C, dtype = torch.float32).unsqueeze(0)  
        diagSeq = covSeq.diagonal(dim1 = 1, dim2 = 2)             
        if diag and diagOnly:
            if logDiag:
                diagSeq = torch.log(diagSeq.clamp_min(eps))
            return diagSeq, 1
        return covSeq, 1

    if T < win:
        W = X.unsqueeze(1)
        eff = float(T)
    else:
        maxPhase = max(0, T - win)
        phase = min(max(phase, 0), maxPhase)
        Xs = X[:, phase:]
        if Xs.shape[1] < win:
            W = X.unsqueeze(1)
            eff = float(T)
        else:
            W = Xs.unfold(dimension = 1, size = win, step = hop)
            eff = float(win - 1) if win > 1 else float(win)

    S = torch.einsum("cfl,dfl->fdc", W, W) / eff

    tr = S.diagonal(dim1 = 1, dim2 = 2).sum(-1)
    target = (tr / C).view(-1, 1, 1)
    I = torch.eye(C, dtype = S.dtype, device=  S.device).unsqueeze(0)
    covSeq = (1.0 - shrinkAlpha) * S + shrinkAlpha * target * I  

    if diag and (eigenvectors is not None):
        E = eigenvectors.to(dtype = covSeq.dtype, device = covSeq.device)
        covSeq = torch.einsum("ij,fjk,kl->fil", E.t(), covSeq, E)

    if diagOnly:
        diagSeq = covSeq.diagonal(dim1 = 1, dim2 = 2).contiguous()
        if logDiag:
            diagSeq = diagSeq
        return diagSeq, diagSeq.shape[0]

    return covSeq.contiguous(), covSeq.shape[0]


class EpochJitterEMGDataset(Dataset):
    """
    Returns (covSeq, phoneSeq, phoneLen, unitSeq, unitLen)
      covSeq   : (F, C, C) float32  — SPD feature sequence
      phoneSeq : (Lp,)     int64    — phoneme ids (0..39, 40 = blank)
      phoneLen : int
      unitSeq  : (Lu,)     int64    — HuBERT unit ids (0..99, 100 = blank)
      unitLen  : int
    """
    def __init__(
        self,
        inputsList: List[torch.Tensor] | List,      
        phoneLabelsList: List,                      
        phoneLabelLengths: List[int],
        unitLabelsList: List,                    
        unitLabelLengths: List[int],
        *,
        fs: int = 5000,
        winMs: float = 25.0,
        hopMs: float = 20.0,
        shrinkAlpha: float = 0.1,
        diag: bool = False,
        diagOnly: bool = False,
        eigenvectors: Optional[torch.Tensor] = None,
        jitter: bool = True,
    ):
        nItems = len(inputsList)
        assert nItems == len(phoneLabelsList) == len(phoneLabelLengths) \
               == len(unitLabelsList) == len(unitLabelLengths), \
               "Inputs/labels/lengths must have the same length."
        
        self.inputs: List[torch.Tensor] = []
        for X in inputsList:
            Xt = torch.as_tensor(X, dtype=torch.float32, device = "cpu")
            assert Xt.ndim == 2, "Each EMG sample must be (C, T)"
            self.inputs.append(Xt.contiguous())

        self.phoneLabels       = phoneLabelsList
        self.phoneLabelLengths = phoneLabelLengths
        self.unitLabels        = unitLabelsList
        self.unitLabelLengths  = unitLabelLengths

        self.C = int(self.inputs[0].shape[0])
        self.fs = int(fs)
        self.winMs = float(winMs)
        self.hopMs = float(hopMs)
        self.shrinkAlpha = float(shrinkAlpha)
        self.diag = bool(diag)
        self.diagOnly = bool(diagOnly)

        self.E = None
        if eigenvectors is not None:
            self.E = torch.as_tensor(eigenvectors, dtype = torch.float32, device = "cpu").contiguous()
            assert self.E.shape == (self.C, self.C), f"eigenvectors must be ({self.C},{self.C})"

        self.jitterEnabled = bool(jitter)
        self.phases: List[int] = []
        self.resampleJitter(seed = None)

    def resampleJitter(self, seed: Optional[int] = None) -> None:
        g = torch.Generator()
        if seed is not None:
            g.manual_seed(int(seed))
        self.phases = []

        hop = int(round(self.hopMs * self.fs / 1000.0))
        hop = max(hop, 1)

        for X in self.inputs:
            T = int(X.shape[1])
            win = int(round(self.winMs * self.fs / 1000.0))
            if T < win:
                self.phases.append(0)
                continue
            maxPhase = min(hop - 1, T - win)
            if self.jitterEnabled and maxPhase > 0:
                p = int(torch.randint(0, maxPhase + 1, (1,), generator = g))
            else:
                p = 0
            self.phases.append(p)

    def __len__(self) -> int:
        return len(self.inputs)

    def __getitem__(self, idx: int):
        X = self.inputs[idx]                    
        phase = self.phases[idx]

        covSeq, nFrames = computeConvSeq(
            X,
            fs = self.fs,
            winMs = self.winMs,
            hopMs = self.hopMs,
            phase = phase,
            shrinkAlpha = self.shrinkAlpha,
            diag = self.diag,
            diagOnly = self.diagOnly,
            eigenvectors = self.E
        )

        phoneSeq = torch.as_tensor(self.phoneLabels[idx], dtype = torch.long) 
        unitSeq  = torch.as_tensor(self.unitLabels[idx],  dtype = torch.long)   
        phoneLen = int(self.phoneLabelLengths[idx])
        unitLen  = int(self.unitLabelLengths[idx])

        if phoneSeq.numel() < phoneLen:
            raise ValueError(f"Phone target shorter than phoneLen: {phoneSeq.numel()} < {phoneLen}")
        if unitSeq.numel() < unitLen:
            raise ValueError(f"Unit target shorter than unitLen: {unitSeq.numel()} < {unitLen}")

        return covSeq.contiguous(), phoneSeq, phoneLen, unitSeq, unitLen
