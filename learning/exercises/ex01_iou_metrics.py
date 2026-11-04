"""练习 1：IoU、置信度排序、一对一匹配与 Precision/Recall。"""

from __future__ import annotations

from collections.abc import Sequence

Box = tuple[float, float, float, float]
Prediction = tuple[float, float, float, float, float]


def box_iou(box_a: Box, box_b: Box) -> float:
    """计算两个 xyxy 框的 IoU。

    参数:
        box_a, box_b: `(x1, y1, x2, y2)`，要求右下角不小于左上角。
    返回:
        交集面积 / 并集面积；没有交集时为 0。
    """
    # TODO: 分别求交集宽高、交集面积、两个框面积和并集面积。
    raise NotImplementedError("请实现 box_iou")


def match_predictions(
    predictions: Sequence[Prediction],
    ground_truths: Sequence[Box],
    iou_threshold: float = 0.5,
) -> tuple[int, int, int]:
    """按置信度从高到低，将预测框与真值框进行一对一贪心匹配。

    每个预测为 `(confidence, x1, y1, x2, y2)`。同一个真值最多匹配一次；
    重复命中已经匹配的真值应计为 FP。返回 `(TP, FP, FN)`。
    """
    # TODO: 排序预测；为每个预测寻找尚未匹配且 IoU 最大的真值。
    raise NotImplementedError("请实现 match_predictions")


def precision_recall(tp: int, fp: int, fn: int) -> tuple[float, float]:
    """根据计数返回 `(precision, recall)`，分母为 0 时对应结果取 0。"""
    # TODO: precision = TP/(TP+FP)，recall = TP/(TP+FN)。
    raise NotImplementedError("请实现 precision_recall")
