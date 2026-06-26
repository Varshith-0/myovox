"""decode must be disk-only: importing myovox.decode.decode pulls in NO training or model
code, so the decode pipeline only ever consumes cached logits. Checked in a fresh subprocess
(other tests import the trainers, polluting this process's sys.modules)."""
import subprocess
import sys


def test_decode_imports_no_training_or_model():
    code = (
        "import sys; import myovox.decode.decode;"
        "bad=[m for m in sys.modules if m in ("
        "'myovox.training.train','myovox.training.train_augmented','myovox.training.crossfold',"
        "'myovox.models.model','myovox.data.data','myovox.audio.teacher_conv','myovox.audio.teacher_bilstm')];"
        "print('LEAK:'+','.join(bad) if bad else 'CLEAN')"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert "CLEAN" in out.stdout, f"decode pulled in training/model code: {out.stdout} {out.stderr[-300:]}"
