"""Smoke: the whole package imports and public entry points exist (new src/ subpackage layout)."""


def test_top_level_import():
    import myovox
    assert myovox.__version__


def test_core_imports():
    from myovox import config, paths, log, runlog, reproduce, report   # noqa: F401  (top level)
    from myovox.data import data, covariance, text                     # noqa: F401
    from myovox.decode import decode, evaluate, score                  # noqa: F401
    assert hasattr(evaluate, "evaluate")
    assert hasattr(decode, "greedy_per") and hasattr(decode, "WFSTDecoder")


def test_model():
    from myovox.models.model import EMGConformer, build_model           # noqa: F401
    from myovox.models import frontend, losses                          # noqa: F401
    assert callable(build_model)
    assert hasattr(frontend, "featuresNorm") and hasattr(frontend, "RotationInvariantMLP")


def test_pipeline_imports():
    from myovox.audio import ssl_features, teacher_conv, teacher_bilstm   # noqa: F401
    from myovox.training import train, train_augmented, crossfold       # noqa: F401
    from myovox.pipeline import forward, ensemble, nbest, union         # noqa: F401
    from myovox.rerank import data, infer, tune, train as lift_train    # noqa: F401
