#!/usr/bin/env bash
# 串行完成论文核心补充实验。完整结果跳过；不完整检测运行归档后干净重跑。
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
CONDA_BIN="${CONDA_BIN:-/home/bornshine/miniconda3/bin/conda}"
if [[ ! -x "$CONDA_BIN" ]]; then
    echo "找不到可执行 Conda：$CONDA_BIN" >&2
    exit 127
fi

update_status() {
    "$CONDA_BIN" run -n vlm-rd-detect \
        python scripts/update_core_experiment_status.py || true
}
trap update_status EXIT
update_status

archive_incomplete_directory() {
    local source_dir="$1"
    local label="$2"
    if [[ ! -d "$source_dir" ]] \
        || [[ -z "$(find "$source_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        return
    fi
    local archive_root="results/interrupted_archive"
    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    local target="$archive_root/${label}_$timestamp"
    mkdir -p "$archive_root"
    mv "$source_dir" "$target"
    echo "已将不完整运行可恢复地归档到：$target"
}

WAIT_PID="${1:-}"
if [[ -n "$WAIT_PID" ]]; then
    if [[ ! "$WAIT_PID" =~ ^[0-9]+$ ]]; then
        echo "wait PID 必须是整数，实际为：$WAIT_PID" >&2
        exit 2
    fi
    echo "等待当前正式实验 PID=$WAIT_PID ..."
    while kill -0 "$WAIT_PID" 2>/dev/null; do
        sleep 30
    done
    if [[ ! -f results/runs/p2_head128_seed0/metrics.json ]]; then
        echo "当前实验进程已结束，但缺少 p2_head128_seed0/metrics.json，停止队列。" >&2
        exit 1
    fi
fi

run_detector() {
    local variant="$1"
    local seed="$2"
    local run_dir="results/runs/${variant}_seed${seed}"
    if [[ -f "$run_dir/metrics.json" ]]; then
        echo "跳过完整实验：${variant}_seed${seed}"
        return
    fi
    if [[ -d "$run_dir" ]]; then
        echo "发现不完整运行；为保证论文数据有效，将先归档再干净重跑：$run_dir"
        bash scripts/archive_incomplete_detector_run.sh "$variant" "$seed"
    fi
    echo "运行：${variant}_seed${seed}"
    "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/run_experiment.py "$variant" \
        --epochs 100 --batch 16 --patience 30 --workers 8 --seed "$seed"
    update_status
}

run_clip() {
    local summary_path="$1"
    shift
    if [[ -f "$summary_path" ]]; then
        echo "跳过完整 CLIP 实验：$summary_path"
        return
    fi
    archive_incomplete_directory \
        "${summary_path%/summary.json}" \
        "$(basename "${summary_path%/summary.json}")"
    "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect "$@"
    update_status
}

run_detector p2_head128 0
run_detector p2_cbam_head128 0
run_detector p2_head128 1
run_detector p2_cbam_head128 1
run_detector p2_head128 2
run_detector p2_cbam_head128 2

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
    python experiments/summarize_head_width_controls.py

"$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
    python experiments/size_stratified_analysis.py \
    --variants baseline,cbam_only,p2_only,p2_cbam,p2_head128,p2_cbam_head128 \
    --seeds 0,1,2 \
    --output results/size_stratified_head128_controls.json

run_clip \
    experiments/clip_module/runs/exp_003a_openai-clip-vit-base-patch32_val/summary.json \
    python experiments/clip_module/exp003_clip_zeroshot_eval.py \
    --split val --run-name exp_003a_openai-clip-vit-base-patch32_val

run_clip \
    experiments/clip_module/runs/exp_003b_p2_cbam_seed0_val_conf001/summary.json \
    python experiments/clip_module/exp003b_clip_end2end_eval.py \
    --weights results/runs/p2_cbam_seed0/weights/best.pt \
    --split val --conf 0.01 --run-name exp_003b_p2_cbam_seed0_val_conf001

if [[ ! -f results/rejection_calibration.json ]]; then
    "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/clip_module/exp003e_rejection_calibration.py \
        --val-run experiments/clip_module/runs/exp_003b_p2_cbam_seed0_val_conf001 \
        --test-run experiments/clip_module/runs/conf_scan_0_01
else
    echo "跳过完整拒识校准：results/rejection_calibration.json"
fi

run_clip \
    experiments/clip_module/runs/exp_003c_vitl14_corrected/summary.json \
    python experiments/clip_module/exp003c_vitl14_compare.py \
    --run-name exp_003c_vitl14_corrected

if [[ ! -f results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16/summary.json ]]; then
    archive_incomplete_directory \
        results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16 \
        yoloworld_v2s_gl_ru_imgsz320_fp16
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/open_vocab_baselines/yoloworld_eval.py \
        --weights weights/yolov8s-worldv2.pt --imgsz 320 --batch 1 --half \
        --output results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16
else
    echo "跳过完整 YOLO-World：results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16/summary.json"
fi

echo "论文核心实验队列全部完成。"
