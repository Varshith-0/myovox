"""Single source of truth for Myovox: paths, constants, and the decode config.

Every other module imports its constants from here — there are no magic numbers
elsewhere. Paths derive from the repo root (this file is src/myovox/config.py →
parents[1]), overridable with the MYOVOX_ROOT environment variable.

The repo has ONE pipeline: a bidirectional Conformer distilled from WavLM-L9, two
of which are ensembled, their n-best unioned, and reranked by a QLoRA LLM → 18.53 WER.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
REPO_ROOT = Path(os.environ.get("MYOVOX_ROOT", Path(__file__).resolve().parents[1]))
DATA_ROOT = REPO_ROOT / "data" / "GeneralCorpusData"
LANG_DIR = REPO_ROOT / "data" / "wfst_decoder" / "ckptsLargeVocb" / "lang_phone"
CKPT_ROOT = REPO_ROOT / "checkpoints"
RESULTS_ROOT = REPO_ROOT / "outputs"
PHON_CACHE = CKPT_ROOT / "phon_arr.npy"            # cached g2p (survives env drift)
PHON_LEN_CACHE = CKPT_ROOT / "phon_len.npy"
PHON_SYMS_CACHE = CKPT_ROOT / "phon_syms.json"

# Front-end warm-start seed: a small upstream emg2speech acoustic checkpoint whose
# feature front-end (featNorm + riMlp) and CTC heads initialise the Conformer. It is a
# fixed INPUT (not trained here); the report's numbers were produced with this warm-start.
WARMSTART_SEED = CKPT_ROOT / "baseline" / "epoch_30.pt"

# ----------------------------------------------------------------------------
# Data split — authors' official sequential split over the 9660-sentence corpus.
# One definition, imported everywhere; never repeat 8500/9260/9660 as a literal.
# ----------------------------------------------------------------------------
TRAIN_END, VAL_END, N_TOTAL = 8500, 9260, 9660
SPLITS = {"train": (0, TRAIN_END), "val": (TRAIN_END, VAL_END), "test": (VAL_END, N_TOTAL)}

# ----------------------------------------------------------------------------
# Model architecture (the Conformer front-end + CTC heads)
# ----------------------------------------------------------------------------
MODEL_CFG = dict(
    inFeatures=31 * 31, mlpFeatures=[384],
    numUnits=101, numPhones=41, unitBlank=100, phoneBlank=40,
    electrodeChannels=31, bottleneckDim=512,
)
# NOTE: ssl_dim is NOT in MODEL_CFG — the trainers pass it explicitly (ssl_dim=Dssl) from the
# loaded WavLM features, and EMGConformer defaults it to SSL_DIM (1024). Keeping it out of
# MODEL_CFG avoids a duplicate-keyword error at EMGConformer(ssl_dim=..., **MODEL_CFG).
NUM_PHONES = 41
PHONE_BLANK, UNIT_BLANK = 40, 100

# ----------------------------------------------------------------------------
# Loss weights (one place; YAML configs reference these as defaults)
# ----------------------------------------------------------------------------
LAM_UNIT, LAM_PHONE, LAM_CONS = 0.8, 0.1, 0.1     # multitask CTC mix
LAM_DISTILL, LAM_CROSSCON, LAM_RECOG = 0.5, 0.5, 1.0   # cross-modal terms i / ii / iv
LAM_FRAMEKL = 0.3                                  # frame-level KL teacher (augmented run)
TAU = 0.1                                          # InfoNCE temperature

# ----------------------------------------------------------------------------
# Audio / feature front-end
# ----------------------------------------------------------------------------
FS, WIN_MS, HOP_MS, SHRINK = 5000, 25.0, 20.0, 0.1
FRAME_HZ = 1000.0 / HOP_MS                         # ≈ 50 Hz feature frame rate

# ----------------------------------------------------------------------------
# WFST decode operating point (tuned on val, applied once to test)
# ----------------------------------------------------------------------------
OFFLINE_SCALE = 0.25                               # acoustic scale (headline Conformer)
SCALE = OFFLINE_SCALE                              # readable alias
DEFAULT_BLANK_PEN = 2.0                            # blank-emission penalty
SEARCH_BEAM, OUTPUT_BEAM = 50.0, 50.0
DECODE_SCALES = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]   # val tuning grid

# ----------------------------------------------------------------------------
# Self-supervised audio teacher (WavLM-Large layer 9)
# ----------------------------------------------------------------------------
SSL_MODEL, SSL_LAYER, SSL_DIM = "microsoft/wavlm-large", 9, 1024

# ----------------------------------------------------------------------------
# LIFT LLM reranker (QLoRA)
# ----------------------------------------------------------------------------
LIFT_BASE = "Qwen/Qwen2.5-7B-Instruct"
LIFT_LORA_R, LIFT_TOPK, LIFT_MAX_LEN = 16, 10, 320
LIFT_LR, LIFT_EPOCHS = 2e-4, 3.0


# ----------------------------------------------------------------------------
# Decode runtime config (used by configs/decode.yaml + load_config)
# ----------------------------------------------------------------------------
@dataclass
class DecodeConfig:
    acoustic_scale: float = OFFLINE_SCALE
    blank_penalty: float = DEFAULT_BLANK_PEN
    search_beam: float = SEARCH_BEAM
    output_beam: float = OUTPUT_BEAM


@dataclass
class Config:
    """Top-level runtime config (offline decode)."""
    decode: DecodeConfig = field(default_factory=DecodeConfig)
    root: str | None = None                        # overrides MYOVOX_ROOT if set

    def __post_init__(self):
        if self.root:
            os.environ["MYOVOX_ROOT"] = str(self.root)

    def to_dict(self):
        return asdict(self)


def load_config(path: str | os.PathLike | None = None) -> Config:
    """Load a decode Config from a YAML file (or return the default offline Config)."""
    if path is None:
        return Config()
    import yaml
    with open(path) as f:
        raw = yaml.safe_load(f) or {}
    dc = raw.get("decode", {}) or {}
    root = (raw.get("paths", {}) or {}).get("root")
    keys = ("acoustic_scale", "blank_penalty", "search_beam", "output_beam")
    return Config(decode=DecodeConfig(**{k: dc[k] for k in keys if k in dc}), root=root)


def load_yaml_cfg(path, defaults: dict) -> dict:
    """Merge a flat YAML file of hyperparameters over a dict of defaults.

    Used by every training entry point: defaults (from this file) < YAML < --flag.
    Returns a plain dict the caller feeds to argparse via ap.set_defaults(**cfg).
    """
    cfg = dict(defaults)
    if path:
        import yaml
        with open(path) as f:
            cfg.update({k: v for k, v in (yaml.safe_load(f) or {}).items() if v is not None})
    return cfg


def apply_config_and_logging(ap):
    """Add --config / --log-level to an argparse parser, apply the YAML as defaults
    (config.py default < YAML < explicit --flag), set up logging, and return parsed args.
    Call this in place of `args = ap.parse_args()` at the end of an entry point's main()."""
    ap.add_argument("--config", default=None, help="YAML of hyperparameters (overrides code defaults)")
    ap.add_argument("--log-level", default="INFO")
    pre, _ = ap.parse_known_args()
    if pre.config:
        ap.set_defaults(**load_yaml_cfg(pre.config, {}))
    args = ap.parse_args()
    from myovox.log import setup_logging
    setup_logging(args.log_level)
    return args


def ms_to_frames(ms: float) -> int:
    """Duration in ms → integer feature frames (20 ms hop)."""
    return max(1, int(round(ms / HOP_MS)))
