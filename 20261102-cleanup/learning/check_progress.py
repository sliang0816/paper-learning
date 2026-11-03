"""自动验收 learning/exercises 下的五项手写练习。"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import torch

# 同时支持 `python learning/check_progress.py` 和模块方式运行。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass(frozen=True)
class CheckResult:
    number: int
    name: str
    status: str
    detail: str


def check_01() -> None:
    from learning.exercises.ex01_iou_metrics import (
        box_iou,
        match_predictions,
        precision_recall,
    )

    iou = box_iou((0, 0, 2, 2), (1, 1, 3, 3))
    assert math.isclose(iou, 1 / 7, rel_tol=1e-6), f"IoU 应为 1/7，实际为 {iou}"

    predictions = [
        (0.95, 0.0, 0.0, 2.0, 2.0),
        (0.90, 4.0, 4.0, 6.0, 6.0),
        (0.80, 0.0, 0.0, 2.0, 2.0),
    ]
    ground_truths = [(0.0, 0.0, 2.0, 2.0), (4.0, 4.0, 6.0, 6.0)]
    counts = match_predictions(predictions, ground_truths, iou_threshold=0.5)
    assert tuple(counts) == (2, 1, 0), f"(TP, FP, FN) 应为 (2, 1, 0)，实际为 {counts}"

    precision, recall = precision_recall(*counts)
    assert math.isclose(precision, 2 / 3, rel_tol=1e-6)
    assert math.isclose(recall, 1.0, rel_tol=1e-6)


def check_02() -> None:
    from learning.exercises.ex02_p2_fusion import MiniP2Fusion

    module = MiniP2Fusion(c2_channels=32, c3_channels=64, out_channels=48).eval()
    p2 = torch.randn(1, 32, 40, 40)
    p3 = torch.randn(1, 64, 20, 20)
    with torch.no_grad():
        output = module(p2, p3)
    assert tuple(output.shape) == (1, 48, 40, 40), f"输出 shape 错误：{tuple(output.shape)}"
    assert torch.isfinite(output).all(), "输出中出现 NaN 或 Inf"
    assert sum(parameter.numel() for parameter in module.parameters()) > 0, "模块没有可学习参数"


def check_03() -> None:
    from learning.exercises.ex03_cbam import CBAM

    module = CBAM(channels=32, reduction=8, kernel_size=7).eval()
    inputs = torch.randn(2, 32, 16, 16)
    with torch.no_grad():
        output = module(inputs)
    assert output.shape == inputs.shape, "CBAM 必须保持输入输出 shape 一致"
    assert torch.isfinite(output).all(), "输出中出现 NaN 或 Inf"
    assert sum(parameter.numel() for parameter in module.parameters()) > 0, "模块没有可学习参数"


def check_04() -> None:
    from learning.exercises.ex04_clip_ood import (
        binary_roc_auc,
        cosine_logits,
        l2_normalize,
        ood_scores,
    )

    features = torch.tensor([[3.0, 4.0], [0.0, 2.0]])
    normalized = l2_normalize(features)
    assert torch.allclose(normalized.norm(dim=-1), torch.ones(2), atol=1e-6)

    images = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    texts = torch.tensor([[1.0, 0.0], [1.0, 1.0]])
    logits = cosine_logits(images, texts, temperature=0.5)
    expected = torch.tensor([[2.0, math.sqrt(2)], [0.0, math.sqrt(2)]])
    assert torch.allclose(logits, expected, atol=1e-5), f"余弦 logits 错误：{logits}"

    similarities = torch.tensor([[0.8, 0.2], [0.3, 0.4]])
    scores = ood_scores(similarities)
    assert torch.allclose(scores, torch.tensor([0.2, 0.6]), atol=1e-6)

    auc = binary_roc_auc(labels=[0, 0, 1, 1], scores=[0.1, 0.2, 0.8, 0.9])
    assert math.isclose(auc, 1.0, rel_tol=1e-6), f"完全正确排序的 AUC 应为 1，实际为 {auc}"


def check_05() -> None:
    from learning.exercises.ex05_multiseed_stats import (
        interaction_effect,
        mean_std,
        paired_delta,
    )

    mean, std = mean_std([1.0, 2.0, 3.0])
    assert math.isclose(mean, 2.0, rel_tol=1e-6)
    assert math.isclose(std, 1.0, rel_tol=1e-6), "应计算样本标准差（分母 n-1）"

    deltas = paired_delta([0.40, 0.50], [0.30, 0.45])
    assert len(deltas) == 2
    assert all(
        math.isclose(actual, expected, abs_tol=1e-9)
        for actual, expected in zip(deltas, [0.10, 0.05])
    )

    effects = interaction_effect(
        joint=[0.4469],
        p2_only=[0.4224],
        cbam_only=[0.4317],
        baseline=[0.4275],
    )
    assert len(effects) == 1
    assert math.isclose(effects[0], 0.0203, abs_tol=1e-9), (
        f"seed 0 的 mAP50 交互项应为 0.0203，实际为 {effects[0]}"
    )


CHECKS: dict[int, tuple[str, Callable[[], None]]] = {
    1: ("IoU 与检测指标", check_01),
    2: ("mini P2 特征融合", check_02),
    3: ("mini CBAM", check_03),
    4: ("CLIP 相似度与 OOD", check_04),
    5: ("多随机种子统计", check_05),
}


def run_check(number: int, name: str, check: Callable[[], None]) -> CheckResult:
    try:
        check()
    except NotImplementedError as error:
        return CheckResult(number, name, "未完成", str(error) or "仍有 TODO")
    except Exception as error:  # 练习验收需要把具体错误继续展示给学习者。
        return CheckResult(number, name, "失败", f"{type(error).__name__}: {error}")
    return CheckResult(number, name, "通过", "核心行为符合验收样例")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exercise",
        type=int,
        choices=CHECKS,
        help="只检查指定编号；默认检查全部",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="存在未完成或失败项时返回非零退出码",
    )
    args = parser.parse_args()

    selected = [args.exercise] if args.exercise else list(CHECKS)
    results = [
        run_check(number, CHECKS[number][0], CHECKS[number][1])
        for number in selected
    ]
    for result in results:
        print(f"[{result.status}] {result.number}. {result.name} — {result.detail}")

    passed = sum(result.status == "通过" for result in results)
    print(f"\n进度：{passed}/{len(results)} 项通过")
    if args.strict and passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
