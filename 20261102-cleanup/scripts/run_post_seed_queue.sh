#!/usr/bin/env bash
# 新增 seeds 完成后的汇总、尺寸分析和统一开放词汇基线。
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
CONDA_BIN="${CONDA_BIN:-/home/bornshine/miniconda3/bin/conda}"
failures=0

run_step() {
    local label="$1"
    shift
    echo "开始：$label"
    if "$@"; then
        echo "完成：$label"
    else
        status=$?
        echo "失败：$label（退出码 $status）；继续后续独立任务。" >&2
        failures=$((failures + 1))
    fi
}

if [[ ! -f results/head_width_control_summary_5seed.json ]]; then
    run_step "5-seed 固定头宽 2x2 汇总" \
        "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/summarize_head_width_controls.py \
        --seeds 0,1,2,3,4 \
        --output results/head_width_control_summary_5seed.json
else
    echo "跳过已有 5-seed 固定头宽完整汇总。"
fi

if [[ ! -f results/size_stratified_head128_controls_5seed.json ]]; then
    run_step "5-seed 尺寸分层分析" \
        "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/size_stratified_analysis.py \
        --variants baseline,cbam_only,p2_head128,p2_cbam_head128 \
        --seeds 0,1,2,3,4 \
        --output results/size_stratified_head128_controls_5seed.json
else
    echo "跳过已有 5-seed 尺寸分层完整结果。"
fi

if [[ ! -f results/open_vocab/grounding_dino_tiny_gl_ru_imgsz640_fp16/summary.json ]]; then
    grounding_overwrite=()
    if [[ -d results/open_vocab/grounding_dino_tiny_gl_ru_imgsz640_fp16 ]] \
        && [[ -n "$(find results/open_vocab/grounding_dino_tiny_gl_ru_imgsz640_fp16 -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        grounding_overwrite=(--overwrite)
    fi
    run_step "Grounding DINO tiny 640 FP16" \
        "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/open_vocab_baselines/grounding_dino_eval.py \
        --imgsz 640 --half --allow-download \
        --output results/open_vocab/grounding_dino_tiny_gl_ru_imgsz640_fp16 \
        "${grounding_overwrite[@]}"
else
    echo "跳过已有 Grounding DINO 完整结果。"
fi

if [[ ! -f results/open_vocab/yoloworld_v2s_gl_ru_imgsz640_fp16/summary.json ]]; then
    yoloworld_overwrite=()
    if [[ -d results/open_vocab/yoloworld_v2s_gl_ru_imgsz640_fp16 ]] \
        && [[ -n "$(find results/open_vocab/yoloworld_v2s_gl_ru_imgsz640_fp16 -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        yoloworld_overwrite=(--overwrite)
    fi
    run_step "YOLO-World 640 FP16" \
        "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/open_vocab_baselines/yoloworld_eval.py \
        --weights weights/yolov8s-worldv2.pt --imgsz 640 --batch 1 --half \
        --output results/open_vocab/yoloworld_v2s_gl_ru_imgsz640_fp16 \
        "${yoloworld_overwrite[@]}"
else
    echo "跳过已有 YOLO-World 640 完整结果。"
fi

if (( failures > 0 )); then
    echo "后处理队列完成，但有 $failures 项失败。" >&2
    exit 1
fi
echo "后处理队列全部完成。"
