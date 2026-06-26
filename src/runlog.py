"""Lightweight per-run tracking — no external deps (W&B is unavailable here).

Each training run writes, under outputs/runs/<name>/:
  * config.yaml    — the resolved hyperparameters for the run
  * metrics.jsonl  — one JSON line per epoch (append-only)
  * metrics.json   — the final summary (best epoch, test scores, ...)
"""
import json

from myovox.paths import RUNS


def _jsonable(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    return str(v)


class RunLog:
    """Open with the run name + resolved config; .log(**row) per epoch; .finish(**summary)."""

    def __init__(self, name, config):
        self.dir = RUNS / name
        self.dir.mkdir(parents=True, exist_ok=True)
        import yaml
        cfg = {k: _jsonable(v) for k, v in dict(config).items()}
        (self.dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        self.metrics_path = self.dir / "metrics.jsonl"
        self.metrics_path.write_text("")

    def log(self, **row):
        with open(self.metrics_path, "a") as f:
            f.write(json.dumps({k: _jsonable(v) for k, v in row.items()}) + "\n")

    def finish(self, **summary):
        (self.dir / "metrics.json").write_text(
            json.dumps({k: _jsonable(v) for k, v in summary.items()}, indent=2))
