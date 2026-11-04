"""练习 3：手写 Convolutional Block Attention Module（CBAM）。"""

from __future__ import annotations

import torch
from torch import nn


class CBAM(nn.Module):
    """依次执行通道注意力和空间注意力，保持输入输出 shape 一致。

    提示:
        通道分支对空间维做 avg/max pooling，并共享同一个两层 MLP；
        空间分支对通道维做 mean/max pooling，拼接后用卷积生成单通道权重。
    """

    def __init__(
        self,
        channels: int,
        reduction: int = 16,
        kernel_size: int = 7,
    ) -> None:
        super().__init__()
        # TODO: 定义共享 MLP、空间卷积和激活函数。
        # 注意 hidden channels 至少为 1，空间卷积需要保持 H、W 不变。
        raise NotImplementedError("请在 __init__ 中定义 CBAM 子模块")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """返回经过通道和空间两级加权的特征。"""
        # TODO: channel 权重应为 [B,C,1,1]；spatial 权重应为 [B,1,H,W]。
        raise NotImplementedError("请实现 CBAM.forward")
