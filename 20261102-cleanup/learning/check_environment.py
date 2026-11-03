"""检查当前机器的 Python、PyTorch 和短时计算环境。

该脚本只执行一个很小的矩阵前向/反向传播，不加载数据集或模型权重。
"""

from __future__ import annotations

import argparse
import platform
import time

import torch


def resolve_device(requested: str) -> torch.device:
    """按命令行选择设备；明确请求 CUDA 时不静默退回 CPU。"""
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("请求了 CUDA，但 torch.cuda.is_available() 为 False")
        return torch.device("cuda")
    if requested == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def run_tiny_check(device: torch.device) -> tuple[float, float]:
    """运行一次小矩阵前向和反向，返回损失与耗时。"""
    if device.type == "cuda":
        torch.cuda.synchronize(device)

    started = time.perf_counter()
    x = torch.randn(256, 256, device=device, requires_grad=True)
    weight = torch.randn(256, 128, device=device, requires_grad=True)
    loss = (x @ weight).square().mean()
    loss.backward()

    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return float(loss.detach().cpu()), elapsed_ms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="auto 优先使用 CUDA；显式 cuda 在不可用时直接报错",
    )
    args = parser.parse_args()

    device = resolve_device(args.device)
    print(f"Python: {platform.python_version()}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA runtime: {torch.version.cuda or '不可用'}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Selected device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(device)}")

    loss, elapsed_ms = run_tiny_check(device)
    print(f"Tiny forward/backward: OK (loss={loss:.4f}, {elapsed_ms:.1f} ms)")
    if device.type == "cuda":
        allocated_mb = torch.cuda.memory_allocated(device) / 1024**2
        print(f"CUDA tensor memory after check: {allocated_mb:.1f} MiB")


if __name__ == "__main__":
    main()
