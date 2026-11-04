"""练习 2：用随机特征图手写一个最小 P2/P3 融合模块。"""

from __future__ import annotations

import torch
from torch import nn


class MiniP2Fusion(nn.Module):
    """将低分辨率 P3 上采样，与高分辨率 P2 拼接后卷积融合。

    输入:
        p2: `[B, c2_channels, H, W]`
        p3: `[B, c3_channels, H/2, W/2]`
    输出:
        `[B, out_channels, H, W]`
    """

    def __init__(
        self,
        c2_channels: int = 32,
        c3_channels: int = 64,
        out_channels: int = 48,
    ) -> None:
        super().__init__()
        # TODO: 定义一个处理 concat 后通道的卷积融合层。
        raise NotImplementedError("请在 __init__ 中定义 P2 融合层")

    def forward(self, p2: torch.Tensor, p3: torch.Tensor) -> torch.Tensor:
        """上采样 P3 到 P2 尺寸，沿通道维拼接并卷积融合。"""
        # TODO: 建议用 torch.nn.functional.interpolate，尺寸直接取 p2.shape[-2:]。
        raise NotImplementedError("请实现 MiniP2Fusion.forward")
