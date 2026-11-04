"""练习 5：多随机种子统计与 P2×CBAM 交互效应。"""

from __future__ import annotations

from collections.abc import Sequence


def mean_std(values: Sequence[float]) -> tuple[float, float]:
    """返回算术均值与样本标准差（分母 n-1）。

    本练习要求至少两个 seed；不足两个时应抛出 ValueError，避免报告没有意义的
    单 seed 标准差。
    """
    # TODO: 不调用 numpy，按定义实现均值和样本标准差。
    raise NotImplementedError("请实现 mean_std")


def paired_delta(
    model_values: Sequence[float],
    baseline_values: Sequence[float],
) -> list[float]:
    """按相同 seed 配对，返回 `model - baseline`。

    两组长度不相等时应抛出 ValueError。
    """
    # TODO: 逐 seed 相减，而不是用两个均值相减代替配对结果。
    raise NotImplementedError("请实现 paired_delta")


def interaction_effect(
    joint: Sequence[float],
    p2_only: Sequence[float],
    cbam_only: Sequence[float],
    baseline: Sequence[float],
) -> list[float]:
    """逐 seed 计算 `joint - p2_only - cbam_only + baseline`。

    四组长度必须相等；正值表示联合效果超过两个单模块增益的简单相加。
    """
    # TODO: 校验长度并按 seed 计算交互项。
    raise NotImplementedError("请实现 interaction_effect")
