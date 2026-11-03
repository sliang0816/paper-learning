#!/usr/bin/env python3
"""根据正式结果文件生成带勾选框的论文核心实验状态清单。"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
OUTPUT_MD = RESULTS / "core_experiment_status.md"
OUTPUT_JSON = RESULTS / "core_experiment_status.json"


def detector_task(variant: str, seed: int, label: str) -> dict:
    run_dir = RESULTS / "runs" / f"{variant}_seed{seed}"
    complete = (run_dir / "metrics.json").is_file()
    incomplete = run_dir.is_dir() and not complete
    command = (
        f"conda run --no-capture-output -n vlm-rd-detect python "
        f"experiments/run_experiment.py {variant} --epochs 100 --batch 16 "
        f"--patience 30 --workers 8 --seed {seed}"
    )
    return {
        "id": f"{variant}_seed{seed}",
        "label": label,
        "complete": complete,
        "resumable": False,
        "incomplete": incomplete,
        "artifact": str(run_dir / "metrics.json"),
        "command": command,
    }


def artifact_task(task_id: str, label: str, artifact: str, command: str) -> dict:
    path = PROJECT / artifact
    return {
        "id": task_id,
        "label": label,
        "complete": path.is_file(),
        "resumable": False,
        "artifact": str(path),
        "command": command,
    }


def build_tasks() -> list[dict]:
    original_runs = [
        RESULTS / "runs" / f"{variant}_seed{seed}" / "metrics.json"
        for variant in ("baseline", "p2_cbam", "p2_only", "cbam_only")
        for seed in (0, 1, 2)
    ]
    original_complete = all(path.is_file() for path in original_runs)
    tasks = [
        {
            "id": "original_12_detector_runs",
            "label": "原始 4 变体 × 3 seed 检测实验",
            "complete": original_complete,
            "resumable": False,
            "artifact": str(RESULTS / "runs/summary.json"),
            "command": "无需重跑；缺失时按 EXPERIMENTS.md 逐项补齐",
        },
        artifact_task(
            "prompt_val",
            "固定 11 组 prompt 的 val 重选",
            "results/prompt_engineering_val_summary.json",
            "conda run -n vlm-rd-detect python experiments/clip_module/exp003_prompt_engineering.py --split val",
        ),
        artifact_task(
            "size_original",
            "原始四变体修正后尺寸分层分析",
            "results/size_stratified_analysis.json",
            "conda run -n vlm-rd-detect python experiments/size_stratified_analysis.py",
        ),
    ]
    for variant, label in (
        ("p2_head128", "P2 + 固定 128 宽分类头"),
        ("p2_cbam_head128", "P2+CBAM + 固定 128 宽分类头"),
    ):
        for seed in (0, 1, 2):
            tasks.append(detector_task(variant, seed, f"{label}，seed {seed}"))
    tasks.extend(
        [
            artifact_task(
                "head_width_summary",
                "EXP-005 固定头宽 2×2 汇总",
                "results/head_width_control_summary.json",
                "conda run -n vlm-rd-detect python experiments/summarize_head_width_controls.py",
            ),
            artifact_task(
                "size_head128",
                "EXP-005 全模型尺寸分层汇总",
                "results/size_stratified_head128_controls.json",
                "conda run -n vlm-rd-detect python experiments/size_stratified_analysis.py --variants baseline,cbam_only,p2_only,p2_cbam,p2_head128,p2_cbam_head128 --seeds 0,1,2 --output results/size_stratified_head128_controls.json",
            ),
            artifact_task(
                "clip_upper_val",
                "EXP-003a 冻结 prompt 的 val 真值框上界",
                "experiments/clip_module/runs/exp_003a_openai-clip-vit-base-patch32_val/summary.json",
                "conda run -n vlm-rd-detect python experiments/clip_module/exp003_clip_zeroshot_eval.py --split val --run-name exp_003a_openai-clip-vit-base-patch32_val",
            ),
            artifact_task(
                "clip_end2end_val",
                "EXP-003b val 低阈值端到端记录",
                "experiments/clip_module/runs/exp_003b_p2_cbam_seed0_val_conf001/summary.json",
                "conda run -n vlm-rd-detect python experiments/clip_module/exp003b_clip_end2end_eval.py --weights results/runs/p2_cbam_seed0/weights/best.pt --split val --conf 0.01 --run-name exp_003b_p2_cbam_seed0_val_conf001",
            ),
            artifact_task(
                "rejection_calibration",
                "EXP-003e val 选阈值、历史 test 冻结拒识校准",
                "results/rejection_calibration.json",
                "conda run -n vlm-rd-detect python experiments/clip_module/exp003e_rejection_calibration.py --val-run experiments/clip_module/runs/exp_003b_p2_cbam_seed0_val_conf001 --test-run experiments/clip_module/runs/conf_scan_0_01",
            ),
            artifact_task(
                "vit_l14_corrected",
                "EXP-003c ViT-L/14 归一化修正重跑",
                "experiments/clip_module/runs/exp_003c_vitl14_corrected/summary.json",
                "conda run -n vlm-rd-detect python experiments/clip_module/exp003c_vitl14_compare.py --run-name exp_003c_vitl14_corrected",
            ),
            artifact_task(
                "yoloworld",
                "EXP-006 YOLO-World 独立开放词汇基线",
                "results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16/summary.json",
                "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True conda run -n vlm-rd-detect python experiments/open_vocab_baselines/yoloworld_eval.py --weights weights/yolov8s-worldv2.pt --imgsz 320 --batch 1 --half --output results/open_vocab/yoloworld_v2s_gl_ru_imgsz320_fp16",
            ),
        ]
    )
    return tasks


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.tmp")
    staging.write_text(text, encoding="utf-8")
    staging.replace(path)


def main() -> None:
    tasks = build_tasks()
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    complete_count = sum(task["complete"] for task in tasks)
    lines = [
        "# 论文核心实验自动完成清单",
        "",
        f"> 自动生成：{generated_at}；完成 {complete_count}/{len(tasks)}。",
        "> `[x]` 只由正式 `metrics.json` 或 `summary.json` 是否存在决定，不靠人工猜测。",
        "",
    ]
    for task in tasks:
        mark = "x" if task["complete"] else " "
        state = (
            "已完成"
            if task["complete"]
            else ("不完整；队列将归档后干净重跑" if task.get("incomplete") else "待运行")
        )
        lines.extend(
            [
                f"- [{mark}] **{task['label']}** — {state}",
                f"  - 结果：`{Path(task['artifact']).relative_to(PROJECT)}`",
                f"  - 命令：`{task['command']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## 一键入口",
            "",
            "- 夜间温控窗口：`bash scripts/nightly_experiment_window.sh`",
            "- 任意时间手动队列：`bash scripts/run_thesis_core_queue.sh`",
            "- 手动归档不完整检测：`bash scripts/archive_incomplete_detector_run.sh 变体 seed`",
            "- 刷新本清单：`python scripts/update_core_experiment_status.py`",
            "- 查看温控日志：`tail -f results/nightly_experiment.log`",
            "",
        ]
    )
    write_atomic(OUTPUT_MD, "\n".join(lines))
    write_atomic(
        OUTPUT_JSON,
        json.dumps(
            {
                "generated_at": generated_at,
                "complete": complete_count,
                "total": len(tasks),
                "tasks": tasks,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    print(f"核心实验完成 {complete_count}/{len(tasks)}：{OUTPUT_MD}")


if __name__ == "__main__":
    main()
