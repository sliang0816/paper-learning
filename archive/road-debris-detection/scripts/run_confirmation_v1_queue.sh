#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

RESULT_ROOT="results/confirmation"
RUN_ROOT="experiments/clip_module/runs"
LOG_PATH="$RESULT_ROOT/confirmation_v1_queue.log"
CONDA_BIN="${CONDA_EXE:-}"
if [[ -z "$CONDA_BIN" || ! -x "$CONDA_BIN" ]]; then
    for candidate in \
        /home/bornshine/miniconda3/bin/conda \
        /home/bornshine/miniconda3/condabin/conda; do
        if [[ -x "$candidate" ]]; then
            CONDA_BIN="$candidate"
            break
        fi
    done
fi
if [[ -z "$CONDA_BIN" || ! -x "$CONDA_BIN" ]]; then
    echo "找不到可执行的 conda；请通过 CONDA_EXE 指定绝对路径" >&2
    exit 127
fi
mkdir -p "$RESULT_ROOT"
exec > >(tee -a "$LOG_PATH") 2>&1

echo "[$(date -Is)] confirmation_v1 queue started"
while pgrep -f '[r]un_raod_external_queue.sh' >/dev/null; do
    echo "[$(date -Is)] RAOD queue is active; confirmation GPU jobs are waiting"
    sleep 30
done

echo "[$(date -Is)] RAOD queue finished; validating frozen protocol"
sha256sum -c <(printf '%s  %s\n' \
  '8df469e624b7ce1b28a9c3073668dd5b3a6107395c7ad3f00fc46ea72295ae1d' \
  'results/runs/p2_head128_seed0/weights/best.pt')
sha256sum -c <(printf '%s  %s\n' \
  '64e913b7fd4ac3aec20b5ac86631f4328dee840703d01b2dfa75645cfb9fbd0f' \
  'results/runs/baseline_seed0/weights/best.pt')

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python -m unittest discover -s tests -p 'test_*.py'

# 先在开发 val 上生成主检测器候选记录并冻结阈值。
"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/clip_module/exp003b_clip_end2end_eval.py \
  --weights results/runs/p2_head128_seed0/weights/best.pt \
  --split val --conf 0.01 --imgsz 640 --nms-iou 0.7 --iou-match 0.5 \
  --upper-summary "$RUN_ROOT/exp_003f_frozen_prompt_val_p015/summary.json" \
  --crop-padding 0.15 --batch-size 64 \
  --run-name exp_003b_p2_head128_seed0_val_p015_conf001_v1

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/confirmation/frozen_rejection.py freeze \
  --val-run "$RUN_ROOT/exp_003b_p2_head128_seed0_val_p015_conf001_v1" \
  --output "$RESULT_ROOT/rejection_thresholds_v1.json"

# 阈值已落盘后，才允许生成一次性确认预测。
"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/clip_module/exp003_clip_zeroshot_eval.py \
  --split confirm \
  --data-root data/roadSpill/confirmation_internal_v1 \
  --manifest "$RESULT_ROOT/internal_confirmation_v1.json" \
  --crop-padding 0.15 --batch-size 64 \
  --run-name exp_003a_clip_b32_internal_confirm_v1

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/clip_module/exp003b_clip_end2end_eval.py \
  --weights results/runs/p2_head128_seed0/weights/best.pt \
  --split confirm \
  --data-root data/roadSpill/confirmation_internal_v1 \
  --manifest "$RESULT_ROOT/internal_confirmation_v1.json" \
  --upper-summary "$RUN_ROOT/exp_003a_clip_b32_internal_confirm_v1/summary.json" \
  --conf 0.01 --imgsz 640 --nms-iou 0.7 --iou-match 0.5 \
  --crop-padding 0.15 --batch-size 64 \
  --run-name exp_003b_p2_head128_seed0_internal_confirm_v1

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/confirmation/frozen_rejection.py evaluate \
  --confirmation-run "$RUN_ROOT/exp_003b_p2_head128_seed0_internal_confirm_v1" \
  --frozen "$RESULT_ROOT/rejection_thresholds_v1.json" \
  --data-root data/roadSpill/confirmation_internal_v1 \
  --split confirm \
  --output "$RESULT_ROOT/rejection_confirmation_v1.json"

# 预注册的 baseline 诊断和公开语义代理只在主确认结束后顺序运行。
"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/clip_module/exp003b_clip_end2end_eval.py \
  --weights results/runs/baseline_seed0/weights/best.pt \
  --split confirm \
  --data-root data/roadSpill/confirmation_internal_v1 \
  --manifest "$RESULT_ROOT/internal_confirmation_v1.json" \
  --upper-summary "$RUN_ROOT/exp_003a_clip_b32_internal_confirm_v1/summary.json" \
  --conf 0.01 --imgsz 640 --nms-iou 0.7 --iou-match 0.5 \
  --crop-padding 0.15 --batch-size 64 \
  --run-name exp_003b_baseline_seed0_internal_confirm_v1

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/clip_module/exp003_clip_zeroshot_eval.py \
  --split confirm \
  --data-root data/external/semantic_proxy_v1 \
  --manifest "$RESULT_ROOT/public_semantic_proxy_v1.json" \
  --crop-padding 0.15 --batch-size 64 \
  --run-name exp_003a_clip_b32_public_proxy_v1

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/open_vocab_baselines/yoloworld_eval.py \
  --weights weights/yolov8s-worldv2.pt \
  --output results/open_vocab/yoloworld_v2s_gl_ru_internal_confirm_v1 \
  --evaluation-data-root data/roadSpill/confirmation_internal_v1 \
  --evaluation-split confirm \
  --evaluation-manifest "$RESULT_ROOT/internal_confirmation_v1.json" \
  --imgsz 640 --batch 1 --collection-conf 0.001 \
  --nms-iou 0.7 --match-iou 0.5 --max-det 300 --half

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
  python experiments/open_vocab_baselines/grounding_dino_eval.py \
  --output results/open_vocab/grounding_dino_tiny_gl_ru_internal_confirm_v1 \
  --evaluation-data-root data/roadSpill/confirmation_internal_v1 \
  --evaluation-split confirm \
  --evaluation-manifest "$RESULT_ROOT/internal_confirmation_v1.json" \
  --imgsz 640 --collection-conf 0.001 --text-threshold 0.25 \
  --match-iou 0.5 --half

echo "[$(date -Is)] confirmation_v1 queue completed"
