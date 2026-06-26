"""Config: constants single-source + offline WFST-decode runtime config."""
from myovox import config


def test_default_decode():
    cfg = config.Config()
    assert cfg.decode.acoustic_scale == config.OFFLINE_SCALE
    assert cfg.decode.blank_penalty == config.DEFAULT_BLANK_PEN


def test_split_single_source():
    # the 8500/760/400 split lives only in config.SPLITS
    assert config.SPLITS["train"] == (0, 8500)
    assert config.SPLITS["val"] == (8500, 9260)
    assert config.SPLITS["test"] == (9260, 9660)
    # evaluate.split_slice must read from config (no duplicate magic numbers)
    from myovox.decode import evaluate
    assert evaluate.split_slice("test") == config.SPLITS["test"]


def test_load_default_and_yaml():
    assert config.load_config(None).decode.acoustic_scale > 0
    cfg = config.load_config("configs/offline.yaml")
    assert cfg.decode.acoustic_scale > 0 and cfg.decode.blank_penalty >= 0


def test_load_yaml_cfg_overrides_defaults():
    merged = config.load_yaml_cfg(None, {"epochs": 50, "lr": 3e-4})
    assert merged["epochs"] == 50


def test_ms_to_frames():
    assert config.ms_to_frames(500) == 25
    assert config.ms_to_frames(100) == 5
    assert config.ms_to_frames(200) == 10
