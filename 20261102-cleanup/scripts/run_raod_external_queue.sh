#!/usr/bin/env bash
# 串行训练 RAOD baseline/P2 三个配对 seeds；测试阶段由独立脚本统一执行。
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
CONDA_BIN="${CONDA_BIN:-/home/bornshine/miniconda3/bin/conda}"
DATA_YAML="data/external/raod/adapted/raod.yaml"
RESULTS_ROOT="results/external_validation/raod"

if [[ ! -f "$DATA_YAML" ]]; then
    echo "缺少已适配 RAOD 数据：$DATA_YAML" >&2
    exit 2
fi

run_one() {
    local variant="$1"
    local seed="$2"
    local run_dir="$RESULTS_ROOT/${variant}_seed${seed}"
    if [[ -f "$run_dir/train_summary.json" ]]; then
        echo "跳过已有 RAOD 训练：${variant}_seed${seed}"
        return
    fi
    if [[ -d "$run_dir" ]] && [[ -n "$(find "$run_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        local timestamp
        timestamp="$(date '+%Y%m%d_%H%M%S')"
        local archive="results/interrupted_archive/raod_${variant}_seed${seed}_${timestamp}"
        mkdir -p "$(dirname "$archive")"
        mv "$run_dir" "$archive"
        echo "已归档不完整 RAOD 运行：$archive"
    fi
    echo "开始 RAOD：${variant}_seed${seed}"
    "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/external_validation/run_raod_experiment.py "$variant" \
        --seed "$seed" --data "$DATA_YAML" --results "$RESULTS_ROOT" \
        --epochs 100 --batch 16 --imgsz 640 --patience 30 --workers 8
}

for seed in 0 1 2; do
    run_one baseline "$seed"
    run_one p2_head128 "$seed"
done

echo "RAOD 六次训练与验证全部完成；可进入冻结 test 评估。"
