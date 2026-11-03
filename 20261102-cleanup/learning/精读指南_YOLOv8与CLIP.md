# 精读指南：YOLOv8 与 CLIP

> 适用于基础一般的研究生，按顺序执行，预计 8 天完成。
> 读完每篇后填写对应的笔记模板（`learning/paper_notes_*.md`）。

---

## 一、YOLOv8 精读路线（第 1—4 天）

YOLOv8 没有正式论文，资料分散，按以下顺序读。

### 第 1 天：看懂结构图

**资料**：`https://docs.ultralytics.com/models/yolov8/`

看图时只问三个问题：

| 模块 | 做什么 |
|------|--------|
| Backbone | 提取特征，输出三个尺度的特征图 |
| Neck（PAN-FPN） | 融合不同尺度特征（小目标用浅层，大目标用深层） |
| Head | 对每个位置预测框的位置 + 类别 |

**任务**：在纸上手画一遍这个流程图，画完即掌握。

**在 Linux 实验机上跑通 demo**：
```bash
pip install ultralytics
yolo predict model=yolov8n.pt source='https://ultralytics.com/images/bus.jpg'
```

---

### 第 2—3 天：理解三个关键设计

**（1）C2f 模块**（YOLOv8 特征提取核心，替代 CSP）

查看源码位置：`ultralytics/nn/modules/block.py`，搜索 `class C2f`

理解要点：多分支梯度流，保留更多浅层纹理信息，对小目标有利。

**（2）Anchor-free 检测头**

不再预定义锚框，直接预测目标中心点偏移和宽高。
参考资料：知乎搜索"anchor free 检测头 FCOS"，看任意一篇讲解。

**（3）解耦头（Decoupled Head）**

分类分支和回归分支独立计算，避免相互干扰。
对比 YOLOv5 的耦合头（同一个卷积层同时预测类别和位置）理解差异。

**任务**：打开源码，对照结构图，找到每个模块对应的代码文件。

---

### 第 4 天：读 FPN 原论文（选读，直接影响第三章）

**论文**：Lin T Y, et al. Feature Pyramid Networks for Object Detection. CVPR 2017.

**只读**：Abstract + Figure 1 + Section 3（多尺度特征融合方法）

**核心思想**：自上而下的特征融合路径，让深层语义特征增强浅层位置特征，提升小目标检测能力。这是你第三章改进工作的直接理论基础。

---

## 二、CLIP 精读路线（第 5—8 天）

**论文**：Radford A, et al. Learning Transferable Visual Models From Natural Language Supervision. ICML 2021.

论文共 48 页，**不要从头读到尾**，按以下三轮进行。

---

### 第 5 天：第一轮速览（建立整体感，约 20 分钟）

按顺序只看以下部分：

1. **Abstract**（2 分钟）：记住核心——4亿图文对对比学习，实现 zero-shot 迁移
2. **Figure 1**（5 分钟）：这张图是整篇论文的核心，反复看懂
3. **Introduction 最后两段**（3 分钟）：作者自述贡献
4. **Conclusion**（5 分钟）：总结与局限性
5. **Figure 5**（5 分钟）：zero-shot ImageNet 结果，建立对效果的直觉

---

### 第 6—7 天：第二轮精读核心机制（重点）

**精读 Section 3**，分三部分理解：

#### 3.1 对比预训练（Contrastive Pre-training）

核心思想一句话：
> 让图像和对应文本的特征向量尽量相似，与不对应的文本特征向量尽量不相似。

在纸上画出这个矩阵：
```
        文本1  文本2  文本3
图像1  [  高    低    低  ]   ← 对角线上的值应该最大
图像2  [  低    高    低  ]
图像3  [  低    低    高  ]
```
对角线是正样本对，其余是负样本对，这是 InfoNCE 损失的直觉。

#### 3.2 Prompt Engineering（重点，直接影响你的代码）

这节讲如何设计文本模板。你的第四章直接用到：
```python
# 你的 Prompt Templates 来自此处设计思路
texts = [
    "a photo of a tire debris on the road",
    "a photo of a metal piece on the road",
    "a photo of a broken bucket on the road",
]
```
读完后你就知道为什么要加 "a photo of"，而不是直接写类别名。

#### 3.3 Zero-Shot 推理流程（必须完全理解）

```
输入图像 → Image Encoder → 图像特征向量（归一化）
文本模板 → Text Encoder  → N 个文本特征向量（归一化）
                ↓
          计算余弦相似度
                ↓
             Softmax
                ↓
          最高分 = 预测类别
```
这个流程就是你第四章的核心方法。

---

### 第 8 天：代码验证（最重要的一步）

在 Linux 实验机上运行
`experiments/clip_module/exp003_clip_zeroshot_eval.py`。该入口会在正式独立
测试集的全部 8 类真值框上输出 top-1、混淆矩阵、Wilson 置信区间和 OOD AUC，
比早期单图 demo 更适合直接支撑第四章。

实验结果记录到 `learning/paper_notes_clip.md`。

**读 Section 5（选读）**：只看 Table 1 和 Figure 5，了解 CLIP zero-shot 与有监督方法的精度差距，写相关工作时作为对比数据。

跳过：Section 4（训练基础设施细节）、Section 6（偏差分析）、Appendix 大部分。

---

## 三、笔记规范

每读完一篇，填写对应模板：
- YOLOv8：`learning/paper_notes_yolov8.md`
- CLIP：`learning/paper_notes_clip.md`

**笔记格式要求**：
- 用自己的话写，不抄原文
- 重点记录与你研究的关联
- 记录读完后仍不懂的地方（下次问 Claude 或查资料）

---

## 四、8 天时间安排

| 天 | 任务 | 预计时长 |
|----|------|----------|
| Day 1 | YOLOv8 文档 + 手画结构图 + 跑 demo | 3—4 小时 |
| Day 2 | C2f 模块 + Anchor-free 头理解 | 3 小时 |
| Day 3 | 解耦头 + 源码对照阅读 | 3 小时 |
| Day 4 | FPN 论文 Section 3 + 笔记 | 2 小时 |
| Day 5 | CLIP 第一轮速览 + Figure 1 反复看 | 2 小时 |
| Day 6 | CLIP Section 3.1 + 3.2 精读 | 3—4 小时 |
| Day 7 | CLIP Section 3.3 + Section 5 选读 | 3 小时 |
| Day 8 | 跑通 EXP-003a 正式评估 + 填写笔记 | 3 小时 |
