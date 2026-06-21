"""Training losses.

Offline headline objective terms:
  - consistency_loss : phoneme-guided unit↔phoneme agreement through P(phone|unit) (build_A).
  - distill_loss     : masked L2 pulling the EMG projection toward frozen WavLM-L9 (term i).
  - crosscon_loss    : frame-synchronous InfoNCE between EMG projection and WavLM (term ii).

The streaming path uses only the plain phoneme CTC loss (torch.nn.CTCLoss) — no audio terms.
"""
import numpy as np
import torch
import torch.nn.functional as F

from emg2text import config


# ----------------------------------------------------------------------------
# Phoneme-guided unit↔phoneme consistency (Gowda et al. emg2speech)
# ----------------------------------------------------------------------------
def build_A(ppgivenu_path=None, phone_blank=config.PHONE_BLANK):
    """Load P(phoneme | HuBERT-unit) from PpGivenU.npy; build the soft-constraint matrix."""
    ppgivenu_path = ppgivenu_path or (config.DATA_ROOT / "PpGivenU.npy")
    Anb = np.load(ppgivenu_path)[:, 1:].astype(np.float64) + 1e-6
    Anb /= Anb.sum(axis=0, keepdims=True)
    P, Un = Anb.shape
    A = np.zeros((P, Un + 1), dtype=np.float32)
    A[:, :Un] = Anb
    A[phone_blank, Un] = 1.0
    return torch.tensor(A, dtype=torch.float32)


def consistency_loss(unit_logp, phone_logp, A, lengths=None, phone_blank=config.PHONE_BLANK,
                     tau=1.0, exclude_blank=True, weight_by_nonblank=True, gamma=1.0,
                     log_floor=-20.0):
    dev = unit_logp.device
    P = phone_logp.size(-1)
    A = A.to(dev, torch.float32).clamp_min(1e-8)
    logA = torch.log(A)
    logPhat = torch.logsumexp(unit_logp.unsqueeze(-2) + logA.unsqueeze(0).unsqueeze(0), dim=-1)
    logpP = phone_logp
    if tau != 1.0:
        logpP = torch.log_softmax(logpP / tau, dim=-1)
    if exclude_blank:
        keep = torch.ones(P, dtype=torch.bool, device=dev); keep[phone_blank] = False
        logpP = logpP[..., keep]; logPhat = logPhat[..., keep]
    logpP = logpP - torch.logsumexp(logpP, dim=-1, keepdim=True)
    logPhat = logPhat - torch.logsumexp(logPhat, dim=-1, keepdim=True)
    pPtarget = logpP.exp().detach()
    if weight_by_nonblank:
        pBlank = phone_logp.exp().detach()[..., phone_blank]
        w = (1.0 - pBlank).pow(gamma)
    else:
        w = None
    per = -(pPtarget * torch.clamp(logPhat, min=log_floor)).sum(dim=-1)
    if lengths is not None:
        Tt, N = per.shape
        L = lengths.to(dev, torch.long)
        mask = (torch.arange(Tt, device=dev).unsqueeze(1) < L.unsqueeze(0)).float()
        if w is not None:
            per = per * w; denom = (mask * w).sum().clamp_min(1.0)
        else:
            denom = mask.sum().clamp_min(1.0)
        return (per * mask).sum() / denom
    return (per * w).mean() if w is not None else per.mean()


# ----------------------------------------------------------------------------
# Cross-modal distillation (offline only)
# ----------------------------------------------------------------------------
def distill_loss(pred, tgt, tgt_len):
    """Masked L2: pred (T_pred,B,D) interpolated to the SSL frame rate (B,T_tgt,D), masked L2."""
    pred = pred.permute(1, 2, 0)                              # (B, D, T_pred)
    B, D, _ = pred.shape
    T_tgt = int(tgt.shape[1])
    pred = F.interpolate(pred, size=T_tgt, mode="linear", align_corners=False).permute(0, 2, 1)
    mask = (torch.arange(T_tgt, device=pred.device).unsqueeze(0)
            < tgt_len.to(pred.device).unsqueeze(1)).float().unsqueeze(-1)
    return (((pred - tgt) ** 2) * mask).sum() / (mask.sum().clamp_min(1.0) * D)


def crosscon_loss(distill_TBD, wavlm_BTD, in_lens, tau: float = 0.1):
    """Symmetric frame-synchronous InfoNCE between the EMG projection and WavLM frames."""
    emg = distill_TBD.permute(1, 0, 2)
    B, T_emg, _ = emg.shape
    if T_emg < 2:
        return torch.zeros((), device=emg.device)
    w_res = F.interpolate(wavlm_BTD.transpose(1, 2), size=T_emg, mode="linear",
                          align_corners=False).transpose(1, 2)
    e_n = F.normalize(emg, dim=-1)
    w_n = F.normalize(w_res, dim=-1)
    losses = []
    for b in range(B):
        Tt = min(int(in_lens[b]), T_emg)
        if Tt < 2:
            continue
        sim = (e_n[b, :Tt] @ w_n[b, :Tt].T) / tau
        lab = torch.arange(Tt, device=sim.device)
        losses.append((F.cross_entropy(sim, lab) + F.cross_entropy(sim.T, lab)) / 2)
    if not losses:
        return torch.zeros((), device=emg.device)
    return torch.stack(losses).mean()
