"""练习 4：手写 CLIP 相似度、OOD 分数和无依赖的二分类 ROC AUC。"""

from __future__ import annotations

from collections.abc import Sequence

import torch


def l2_normalize(features: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """沿最后一维做 L2 归一化，并用 eps 避免除以 0。"""
    # TODO: 求最后一维范数并归一化。
    raise NotImplementedError("请实现 l2_normalize")


def cosine_logits(
    image_features: torch.Tensor,
    text_features: torch.Tensor,
    temperature: float = 1.0,
) -> torch.Tensor:
    """返回 `[N_image, N_text]` 的余弦相似度 logits。

    两侧特征需要先 L2 归一化；按 CLIP 常用定义，logits 除以 temperature。
    """
    # TODO: 检查 temperature > 0，归一化后做矩阵乘法。
    raise NotImplementedError("请实现 cosine_logits")


def ood_scores(known_similarities: torch.Tensor) -> torch.Tensor:
    """根据已知类别相似度返回每个样本的 OOD 分数：`1 - max_similarity`。"""
    # TODO: 对类别维取最大值。
    raise NotImplementedError("请实现 ood_scores")


def binary_roc_auc(labels: Sequence[int], scores: Sequence[float]) -> float:
    """用正负样本两两排序的定义计算二分类 ROC AUC。

    `label=1` 表示正类/OOD。正负分数相等时计 0.5；两类任一为空应报错。
    """
    # TODO: 枚举所有正负样本对，统计正样本得分更高和并列的比例。
    raise NotImplementedError("请实现 binary_roc_auc")
