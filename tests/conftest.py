"""pytest fixtures. The myovox package lives in src/ (pyproject package-dir maps
myovox -> src), so run `pip install -e .` before pytest for `import myovox` to resolve."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def have(path) -> bool:
    return (ROOT / path).exists()
