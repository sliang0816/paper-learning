#!/usr/bin/env bash
# 将固定头宽 2x2 因子实验从 3 seeds 扩展到 5 seeds（新增 seed 3、4）。
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
CONDA_BIN="${CONDA_BIN:-/home/bornshine/miniconda3/bin/conda}"

if [[ ! -x "$CONDA_BIN" ]]; then
    echo "找不到可执行 Conda：$CONDA_BIN" >&2
    exit 127
fi

run_detector() {
    local variant="$1"
    local seed="$2"
    local run_dir="results/runs/${variant}_seed${seed}"
    local resume_args=()

    if [[ -f "$run_dir/metrics.json" ]]; then
        echo "跳过完整实验：${variant}_seed${seed}"
        return
    fi
    if [[ -d "$run_dir" ]] && [[ -n "$(find "$run_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        echo "从已验证的有限 checkpoint 恢复：${variant}_seed${seed}"
        resume_args=(--resume)
    fi

    "$CONDA_BIN" run --no-capture-output -n vlm-rd-detect \
        python experiments/run_experiment.py "$variant" \
        --epochs 100 --batch 16 --patience 30 --workers 8 --seed "$seed" \
        "${resume_args[@]}"
}

for seed in 3 4; do
    run_detector baseline "$seed"
    run_detector cbam_only "$seed"
    run_detector p2_head128 "$seed"
    run_detector p2_cbam_head128 "$seed"
done
echo "固定头宽 2x2 扩展实验 seed 3、4 全部完成。"
