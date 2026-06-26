#!/bin/bash
# One-time setup for the myovox pipeline (Conformer+WavLM-L9 ensemble -> n-best union ->
# LIFT rerank -> 18.53 % WER). Installs deps + the icefall WFST decoder, and lists the OSF
# data + checkpoint artifacts to download. After this, the whole pipeline runs with: bash scripts/run.sh
set -eu
REPO_ROOT="${MYOVOX_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO_ROOT"

echo "==> 1/3  Python dependencies + editable install (myovox-* console scripts)"
pip install -e . --config-settings editable_mode=strict
echo "    NOTE: install k2 manually for your CUDA/torch: https://k2-fsa.github.io/k2/"

echo "==> 2/3  icefall WFST decoder (get_lattice / one_best_decoding / get_texts / Nbest)"
# icefall is a source install kept OUTSIDE the repo. Clone once, then editable-install it.
ICEFALL_DIR="${ICEFALL_DIR:-$HOME/icefall}"
if python -c "import icefall" 2>/dev/null; then
    echo "    icefall already importable ($(python -c 'import icefall,os;print(os.path.dirname(icefall.__file__))'))"
else
    [ -d "$ICEFALL_DIR" ] || git clone https://github.com/k2-fsa/icefall.git "$ICEFALL_DIR"
    pip install -e "$ICEFALL_DIR"
fi

echo "==> 3/3  Data + checkpoints (download from OSF — not redistributed in this repo)"
cat <<'EOF'
    Place under  data/  and  checkpoints/  (see README "Data & checkpoints"):
      OSF osf.io/65vbx -> data/GeneralCorpusData/   (DATA.pkl, textLABELS.pkl,
                          HuBERTLABELS.pkl, PpGivenU.npy, groundTruthAudioFiles.pkl)
      OSF osf.io/bgh7t -> data/wfst_decoder/ckptsLargeVocb/lang_phone/  (HLG.pt, lexicon.txt, tokens.txt; words.txt)
      checkpoints/baseline/epoch_30.pt   -> the upstream front-end warm-start SEED (required input)
      checkpoints/main/ssl_wl_l9.pt      -> precomputed WavLM-L9 features (optional; run.sh re-extracts if absent)

    Then:  bash scripts/run.sh            # full pipeline from scratch -> 18.53
           bash scripts/run.sh --check    # verify the cached artifacts reproduce 26.14 + 18.53
EOF
