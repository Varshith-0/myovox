"""Myovox — surface-EMG → text decoding.

One pipeline: a bidirectional Conformer distilled from WavLM-L9, ensembled (two members),
its multi-scale n-best unioned, and reranked by a QLoRA LLM (LIFT) → 18.53 % test WER.

Package layout (subpackages under src/, imported as myovox via package-dir):
    config  paths  log  runlog  reproduce  report      (top level)
    data/   models/  decode/  ssl/  training/  pipeline/  rerank/

Entry points (after `pip install -e .`):
    from myovox.config import load_config, Config
    from myovox.decode import evaluate     # WER / PER + paired bootstrap
    python -m myovox.reproduce             # fast acoustic check (26.14 / 22.34) from cached logits
    bash run.sh                              # full pipeline from scratch → 18.53
"""
__version__ = "2.0.0"
