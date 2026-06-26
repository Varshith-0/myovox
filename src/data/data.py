"""Corpus loading, SPD-covariance dataset construction, and batch collation.

Each 31x31 shrinkage-covariance window is padded with IDENTITY matrices (the no-info
covariance). load_all reads the General Corpus (EMG + HuBERT units + text), runs the
cached g2p, and normalises each EMG sample. EMGWithSSLFeatures pairs each EMG window
with its frozen WavLM-L9 feature row for the distillation trainer.
"""
import pickle
import time

import numpy as np
import torch
from torch.utils.data import Dataset

from myovox import config
from myovox.data.covariance import EpochJitterEMGDataset
from myovox.data import text as T
from myovox.log import get_logger

log = get_logger(__name__)


# ----------------------------------------------------------------------------
# Corpus loading
# ----------------------------------------------------------------------------
def load_all(verbose=True):
    """Returns dict(norm, phon, phon_len, units, unit_len, text, syms, phone_def)."""
    t0 = time.time()
    emg = pickle.load(open(config.DATA_ROOT / "DATA.pkl", "rb"))
    units_raw = np.load(config.DATA_ROOT / "HuBERTLABELS.pkl", allow_pickle=True)
    text = pickle.load(open(config.DATA_ROOT / "textLABELS.pkl", "rb"))
    if verbose:
        log.info("loaded %d EMG, %d text (%.0fs)", len(emg), len(text), time.time() - t0)
    phone_def = T.load_phone_def()
    syms, phon, phon_len = T.phonemize(text, phone_def)
    units, unit_len = T.pad_units(list(units_raw))
    norm = []
    for x in emg:
        m = np.mean(x, axis=-1, keepdims=True)
        s = np.std(x, axis=-1, keepdims=True)
        norm.append((x - m) / (s + 1e-9))
    return dict(norm=norm, phon=phon, phon_len=phon_len, units=units,
                unit_len=unit_len, text=text, syms=syms, phone_def=phone_def)


def make_dataset(d, lo, hi, jitter):
    """EpochJitterEMGDataset for the [lo, hi) slice (exposes .resampleJitter())."""
    return EpochJitterEMGDataset(
        d["norm"][lo:hi], d["phon"][lo:hi], d["phon_len"][lo:hi],
        d["units"][lo:hi], d["unit_len"][lo:hi],
        fs=config.FS, winMs=config.WIN_MS, hopMs=config.HOP_MS, shrinkAlpha=config.SHRINK,
        jitter=jitter)


def cat_targets(padded, lengths):
    """Flatten a padded (B,L) target tensor to the 1-D CTC target by lengths."""
    return torch.cat([padded[b, :int(L)] for b, L in enumerate(lengths.tolist())],
                     dim=0).to(torch.long)


# ----------------------------------------------------------------------------
# Distillation training plumbing (EMG window paired with its WavLM-L9 row)
# ----------------------------------------------------------------------------
class EMGWithSSLFeatures(Dataset):
    """Wraps an EpochJitterEMGDataset and returns the matching frozen WavLM-L9 feature row."""

    def __init__(self, emg_ds, feats):
        self.emg = emg_ds
        self.feats = feats

    def __len__(self):
        return len(self.emg)

    def __getitem__(self, i):
        cov, ph, pl, un, ul = self.emg[i]
        return cov, ph, pl, un, ul, self.feats[i]


def make_train_ds(d, lo, hi, jitter, feats):
    """Train/val dataset: EMG covariance paired with the matching WavLM-L9 feature rows."""
    return EMGWithSSLFeatures(make_dataset(d, lo, hi, jitter), feats[lo:hi])


# ----------------------------------------------------------------------------
# Collation
# ----------------------------------------------------------------------------
def _pad_emg(cov, batch_size, max_frames, n_elec):
    """Stack variable-length covariance windows, identity-padding short ones."""
    inputs = cov[0].new_zeros((batch_size, max_frames, n_elec, n_elec))
    eye = torch.eye(n_elec, dtype=inputs.dtype)
    for b, x in enumerate(cov):
        t = int(x.shape[0])
        inputs[b, :t] = x
        if t < max_frames:
            inputs[b, t:max_frames] = eye           # identity pad = no-info covariance
    return inputs


def _pad_targets(seqs, lengths, batch_size, pad):
    max_len = max(int(L) for L in lengths)
    out = torch.full((batch_size, max_len), pad, dtype=torch.long)
    for b, (s, L) in enumerate(zip(seqs, lengths)):
        out[b, :int(L)] = torch.as_tensor(s).view(-1)[:int(L)]
    return out


def make_collate(n_elec=31, pad=-1):
    """Training collate (EMG + SSL) -> (inputs, phone_tgt, unit_tgt, in_lens, pl, ul, feats, feat_lens)."""
    def _collate(batch):
        cov, ph, pl, un, ul, feat_rows = zip(*batch)
        batch_size = len(batch)
        max_frames = max(int(x.shape[0]) for x in cov)
        max_feat_frames = max(int(f.shape[0]) for f in feat_rows)
        inputs = _pad_emg(cov, batch_size, max_frames, n_elec)
        phone_tgt = _pad_targets(ph, pl, batch_size, pad)
        unit_tgt = _pad_targets(un, ul, batch_size, pad)
        feat_dim = int(feat_rows[0].shape[-1])
        feats = torch.zeros((batch_size, max_feat_frames, feat_dim), dtype=torch.float32)
        for b, f in enumerate(feat_rows):
            feats[b, :int(f.shape[0])] = f
        in_lens = torch.as_tensor([int(t.shape[0]) for t in cov], dtype=torch.int32)
        return (inputs, phone_tgt, unit_tgt, in_lens,
                torch.as_tensor(pl, dtype=torch.int32), torch.as_tensor(ul, dtype=torch.int32),
                feats, torch.as_tensor([int(f.shape[0]) for f in feat_rows], dtype=torch.int32))
    return _collate


def make_eval_collate(n_elec=31, pad=-1):
    """Forward/decode collate (EMG only) -> (inputs, phone_tgt, unit_tgt, in_lens, pl, ul)."""
    def _collate(batch):
        cov, ph, pl, un, ul = zip(*batch)
        batch_size = len(batch)
        max_frames = max(int(x.shape[0]) for x in cov)
        inputs = _pad_emg(cov, batch_size, max_frames, n_elec)
        phone_tgt = _pad_targets(ph, pl, batch_size, pad)
        unit_tgt = _pad_targets(un, ul, batch_size, pad)
        in_lens = torch.as_tensor([int(t.shape[0]) for t in cov], dtype=torch.int32)
        return (inputs, phone_tgt, unit_tgt, in_lens,
                torch.as_tensor(pl, dtype=torch.int32), torch.as_tensor(ul, dtype=torch.int32))
    return _collate
