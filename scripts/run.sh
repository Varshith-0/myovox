#!/usr/bin/env bash
# =============================================================================
# emg2text — ONE command to reproduce the 18.53 % WER pipeline end to end.
#
#   bash scripts/run.sh            full pipeline FROM SCRATCH (trains everything) -> 18.53   (~15-25 h, GPU 0)
#   bash scripts/run.sh --check    fast verification from cached artifacts (26.14 + 18.53)   (~15 min)
#
# Every step is idempotent: it is skipped if its output already exists, so a crashed run
# resumes where it stopped. All hyperparameters live in configs/*.yaml (passed via --config);
# this script only orchestrates. Run inside a tmux/screen session so it survives logout.
# =============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."          # repo root (this script lives in scripts/)

# ---- environment (GPU 0 only; editable install; HF cache; CPU decode pool) --------
export EMG2TEXT_ROOT="$(pwd)"
# the emg2text package lives in src/ (pyproject package-dir maps emg2text -> src). Install it
# editable in STRICT mode so only emg2text.* is exposed (a lenient install would put src/ on the
# path and shadow stdlib modules like `ssl`). Idempotent; overwrites any prior lenient install.
pip install -e . --config-settings editable_mode=strict -q 2>/dev/null || pip install -e . -q
export CUDA_VISIBLE_DEVICES=0
export TOKENIZERS_PARALLELISM=false
export DECODE_NPROC=${DECODE_NPROC:-12}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HOME=${HF_HOME:-$HOME/.cache/huggingface}
export HF_HUB_CACHE=${HF_HUB_CACHE:-$HF_HOME/hub}
export PYTHONUNBUFFERED=1

CK=checkpoints; OUT=outputs; CFG=configs
LOGTAG="liftx"
have(){ [ -s "$1" ]; }                                   # idempotency guard (non-empty file)
say(){ echo -e "\n=== $* ===" ; }
[ -n "${TMUX:-}" ] || echo "WARNING: not inside tmux — long runs should use a tmux/screen session."

# ---- read the n-best operating points from configs/nbest.yaml ---------------
yget(){ python -c "import yaml;print(yaml.safe_load(open('$1')).get('$2',''))"; }
NB_BLANK=$(yget $CFG/nbest.yaml blank_pen)
NB_SBEAM=$(yget $CFG/nbest.yaml search_beam)
NB_SCALES=$(yget $CFG/nbest.yaml nbest_scales)
NPARTS=$(yget $CFG/nbest.yaml nproc)

# sharded n-best (independent OS processes — k2 + multiprocessing.Pool deadlocks otherwise)
nbest_run(){  # nbset scale num_paths output_beam splits logits
  local nbset=$1 scale=$2 np=$3 ob=$4 splits=$5 logits=$6
  local marker
  case "$splits" in *test*) marker="$OUT/nbest/${nbset}_test_nbest.pt";; *) marker="$OUT/nbest/${nbset}_train_nbest.pt";; esac
  if have "$marker"; then echo "[skip] n-best $nbset ($marker exists)"; return; fi
  say "n-best $nbset  scale=$scale paths=$np ob=$ob splits=$splits"
  mkdir -p "$OUT/logs"; local pids=()
  for k in $(seq 0 $((NPARTS-1))); do
    OMP_NUM_THREADS=4 python -u -m emg2text.pipeline.nbest --splits "$splits" --part "$k" --nparts "$NPARTS" \
        --num_paths "$np" --nbest_scales "$NB_SCALES" --output_beam "$ob" --search_beam "$NB_SBEAM" \
        --blank_pen "$NB_BLANK" --scale "$scale" --logits "$logits" --nbset "$nbset" \
        > "$OUT/logs/nbest_${nbset}_p${k}.log" 2>&1 &
    pids+=($!)
  done
  local fail=0; for p in "${pids[@]}"; do wait "$p" || fail=$((fail+1)); done
  python -u -m emg2text.pipeline.nbest --splits "$splits" --merge --nparts "$NPARTS" --nbset "$nbset"
  [ "$fail" -eq 0 ] || echo "WARNING: $fail n-best shards failed for $nbset"
}

# =============================================================================
# FAST PATH: verify the cached artifacts reproduce the paper numbers.
# =============================================================================
if [ "${1:-}" = "--check" ]; then
  say "CHECK 1/2  acoustic member (cached logits) -> expect 26.14 / 22.34"
  python -m emg2text.reproduce || true
  say "CHECK 2/2  final LIFT rerank (cached ensU + adapter) -> expect 18.53"
  python -m emg2text.rerank.infer --nbset ensU --adapter "$CK/lift_qwen_x" --val_lo 0 --tag "$LOGTAG"
  python -m emg2text.report --tag "$LOGTAG"
  exit 0
fi

# =============================================================================
# FULL PIPELINE FROM SCRATCH
# =============================================================================
[ -s "$CK/baseline/epoch_30.pt" ] || { echo "ERROR: missing front-end warm-start seed $CK/baseline/epoch_30.pt (fetch via scripts/setup.sh)"; exit 1; }

# 1. WavLM-Large layer-9 features (deterministic; the 17 GB cache — never re-extract if present)
have "$CK/main/ssl_wl_l9.pt" || python -m emg2text.audio.ssl_features --config $CFG/ssl_features.yaml

# 2. frozen WavLM->phone conv teacher (distillation term iv)
have "$CK/main/recog_wl_l9/best.pt" || python -m emg2text.audio.teacher_conv --config $CFG/teacher_conv.yaml \
    --out "$CK/main/recog_wl_l9"

# 3. strong BiLSTM audio teacher (frame-KL for the augmented member)
have "$CK/recog2_bilstm/best.pt" || python -m emg2text.audio.teacher_bilstm --config $CFG/teacher_bilstm.yaml --name recog2_bilstm

# 4. headline Conformer (member 1) -> outputs/main/conf_l9_logits.pt + scores 26.14/22.34
have "$OUT/main/conf_l9_logits.pt" || python -m emg2text.training.train --config $CFG/conformer.yaml --name conf_l9

# 5. anti-overfit augmented Conformer (member 2) -> outputs/p2_aug2_logits.pt
have "$OUT/p2_aug2_logits.pt" || python -m emg2text.training.train_augmented --config $CFG/augmented.yaml --name p2_aug2

# 6. ensemble the two members' phone log-probs (val+test)
have "$OUT/ens_logits.pt" || python -m emg2text.pipeline.ensemble \
    --inputs "$OUT/main/conf_l9_logits.pt" "$OUT/p2_aug2_logits.pt" --splits val,test --out "$OUT/ens_logits.pt"

# 7. multi-scale n-best on the ensemble logits (val+test)
while read nbset scale np ob; do
  nbest_run "$nbset" "$scale" "$np" "$ob" val,test "$OUT/ens_logits.pt"
done < <(python -c "import yaml;[print(v['nbset'],v['scale'],v['num_paths'],v['output_beam']) for v in yaml.safe_load(open('$CFG/nbest.yaml'))['variants']]")

# 8. union the n-best sets -> ensU (oracle ~9.30)
UNION_OUT=$(yget $CFG/nbest.yaml union_out)
have "$OUT/nbest/${UNION_OUT}_test_nbest.pt" || python -m emg2text.pipeline.union \
    --inputs $(python -c "import yaml;print(' '.join(v['nbset'] for v in yaml.safe_load(open('$CFG/nbest.yaml'))['variants']))") \
    --out "$UNION_OUT" --splits val,test

# 9. leak-free TRAIN n-best via 2-fold cross-decode (each half decoded by the other fold's model)
have "$OUT/xfoldA_xdecode_logits.pt" || python -m emg2text.training.train_augmented --config $CFG/augmented.yaml \
    --name xfoldA --train_lo 0 --train_hi 4250 --xdecode_lo 4250 --xdecode_hi 8500
have "$OUT/xfoldB_xdecode_logits.pt" || python -m emg2text.training.train_augmented --config $CFG/augmented.yaml \
    --name xfoldB --train_lo 4250 --train_hi 8500 --xdecode_lo 0 --xdecode_hi 4250
have "$OUT/ens_xdecode_train.pt" || python -m emg2text.training.crossfold \
    --inputs "$OUT/xfoldA_xdecode_logits.pt" "$OUT/xfoldB_xdecode_logits.pt" --out "$OUT/ens_xdecode_train.pt"

# 10. n-best on the cross-decoded TRAIN logits
TRN_NBSET=$(python -c "import yaml;print(yaml.safe_load(open('$CFG/nbest.yaml'))['train_nbest']['nbset'])")
TRN_SCALE=$(python -c "import yaml;print(yaml.safe_load(open('$CFG/nbest.yaml'))['train_nbest']['scale'])")
TRN_NP=$(python -c "import yaml;print(yaml.safe_load(open('$CFG/nbest.yaml'))['train_nbest']['num_paths'])")
TRN_OB=$(python -c "import yaml;print(yaml.safe_load(open('$CFG/nbest.yaml'))['train_nbest']['output_beam'])")
nbest_run "$TRN_NBSET" "$TRN_SCALE" "$TRN_NP" "$TRN_OB" train "$OUT/ens_xdecode_train.pt"

# 11. assemble LIFT training data (TRAIN split only -> leakage-safe)
TOPK=$(yget $CFG/lift.yaml topk)
have "$OUT/B/lift_x.jsonl" || python -m emg2text.rerank.data \
    --nbset "$TRN_NBSET" --split train --out "$OUT/B/lift_x.jsonl" --topk "$TOPK"

# 12. QLoRA fine-tune the reranker
have "$CK/lift_qwen_x/adapter_model.safetensors" || python -m emg2text.rerank.train \
    --config $CFG/lift.yaml --train_jsonl "$OUT/B/lift_x.jsonl" --name lift_qwen_x

# 13. final inference: variant selected on val, applied once to test -> 18.53
python -m emg2text.rerank.infer --nbset "$UNION_OUT" --adapter "$CK/lift_qwen_x" --val_lo 0 --tag "$LOGTAG"

# ---- report produced vs paper -----------------------------------------------
python -m emg2text.report --tag "$LOGTAG"
echo "RUN_DONE"
