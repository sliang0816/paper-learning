# 学习资料与手写练习

本目录是独立论文学习项目的主要工作区，保存模型笔记、文献精读、答疑与小型练习。返回[项目首页](../README.md)。

- 系统阅读：[模型详解](模型详解/README.md)，原图件与论文 PDF 保留相对层级。
- 课题相关：[YOLOv8/CLIP 精读指南](精读指南_YOLOv8与CLIP.md)、[文献综述整理](文献综述整理.md)。
- 求职、模型拓展和单篇笔记按需阅读，旧学习进度不作为正式实验状态。
- 手写练习按下文操作；原课题制度材料见[历史资料](../archive/road-debris-detection/docs/硕士毕业制度与文件汇总下载2025/README.md)。

这里的练习只用于理解与验证核心概念，不能作为论文实验结果。正式实验的 `experiments/` 和 `results/` 位于独立的 `vlm-rd-detect` 项目中。

## 1. 开始前

使用已安装 PyTorch 的 Python 环境，在本仓库根目录执行。可复用已有环境，不要求名为 `vlm-rd-detect`：

```bash
python learning/check_environment.py --device cpu
# 可选：需要已配置 CUDA 的环境
python learning/check_environment.py --device cuda
```

环境检查只执行一次很小的矩阵前向与反向传播，通常几秒内结束。白天可以运行，
但不要把它改成完整数据集遍历或长时间压力测试。

## 2. 练习与验收

待手写文件位于 `learning/exercises/`：

| 编号 | 文件 | 目标 |
|---|---|---|
| 1 | `ex01_iou_metrics.py` | IoU、预测匹配、Precision/Recall |
| 2 | `ex02_p2_fusion.py` | P2/P3 上采样、拼接和卷积融合 |
| 3 | `ex03_cbam.py` | 通道注意力和空间注意力 |
| 4 | `ex04_clip_ood.py` | CLIP 余弦相似度、OOD 分数和 ROC AUC |
| 5 | `ex05_multiseed_stats.py` | 多 seed 均值、标准差、配对差值和交互项 |

建议按编号完成。每个模板已经给出函数签名、输入输出约定和必要提示，但没有给出
实现。请只替换 `TODO` 和 `raise NotImplementedError`，不要先看正式实现。

随时查看进度：

```bash
# 检查全部练习；未完成时也正常退出，便于查看进度
python learning/check_progress.py

# 只检查第 1 项
python learning/check_progress.py --exercise 1

# 全部写完后的最终验收；任何一项未通过都会返回非零退出码
python learning/check_progress.py --strict
```

验收器只使用构造的小张量和固定数字，不加载数据集、不训练模型，也不使用 GPU。
它验证核心行为，但不能代替你解释公式和 shape。

## 3. 与正式项目对照

一项通过后，再阅读对应资料。指标说明已保存在本仓库；以下 `experiments/` 路径均相对于独立的 `vlm-rd-detect` 仓库根目录，不是本仓库文件，需在该项目当前版本中核对：

- 练习 1：[实验评估指标说明](../archive/road-debris-detection/docs/实验评估指标说明.md)
- 练习 2：`experiments/anomaly_head/yolov8s-p2.yaml`
- 练习 3：`experiments/anomaly_head/cbam.py`
- 练习 4：`experiments/clip_module/exp003_clip_zeroshot_eval.py`
- 练习 5：`experiments/summarize_detection_results.py`

每项最后记录四句话：输入输出、公式对应的代码、最容易出错的口径，以及它与论文
哪一节或哪个实验相关。

## 4. 使用边界

- 可以在这里做随机张量、小批量、单次 forward/backward 和 shape 调试。
- 不要写入或修改 `results/runs/`，不要读取正式 test 来反复调参。
- 长训练、多 seed 和完整数据集评估按当前任务与资源安排执行，不依据旧学习计划自动启动。
- 练习实现可以提交 Git；生成的缓存和临时输出不要提交。
