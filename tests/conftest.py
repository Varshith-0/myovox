"""pytest fixtures. The emg2text package lives in src/ (pyproject package-dir maps
emg2text -> src), so run `pip install -e .` before pytest for `import emg2text` to resolve."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def have(path) -> bool:
    return (ROOT / path).exists()
