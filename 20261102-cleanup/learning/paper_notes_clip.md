# 论文笔记：CLIP（Radford et al., ICML 2021）

> 精读完成日期：2026-05-28（Mac Mini M4）
> PDF 路径：`learning/模型详解/papers/33_CLIP_2103.00020.pdf`（arxiv:2103.00020）
> 论文全名：Learning Transferable Visual Models From Natural Language Supervision

---

## 一句话总结

CLIP 通过 4 亿图文对的对比学习，让模型学会将图像和文本映射到同一个向量空间，从而在不使用任何分类头训练的情况下，零样本识别任意类别。对路面抛洒物的意义：不需要每类都标注训练，写个 prompt 模板就能识别未知类别。

---

## 速览记录（Day 5，第一轮）

### Abstract 核心信息
- 训练数据规模：4 亿（400M）图文对，来自互联网爬取（WIT 数据集）
- 训练方式：双塔对比学习——图像编码器 + 文本编码器，最大化正样本对相似度、最小化负样本对
- 核心能力：zero-shot 迁移——无需微调，直接用 prompt 文本匹配图像就能做分类

### Figure 1 理解
论文最核心的图。左边是传统方法：用固定类别标签训练分类器，只能识别训练过的类。右边是 CLIP：用自然语言描述类别（"a photo of a dog"），图文编码到同一空间后计算相似度，能识别任意你"描述得出来"的类别。本质是把分类问题变成了图文匹配问题。

### Conclusion 要点
- 主要贡献：证明大规模自然语言监督可以训练出具有强零样本能力的视觉模型
- 局限性：对抽象任务（计数、空间关系）表现差，对专业领域（卫星图、医学图）泛化差，对 prompt 措辞敏感

---

## 精读记录（Day 6—7，Section 3）

### 3.1 对比预训练

**正样本对**：图像 i 和文本 i（同一条数据的图文对）
**负样本对**：图像 i 和文本 j（i ≠ j），一个 batch 里对角线以外的所有组合

目标：对角线相似度最大，非对角线相似度最小。

**InfoNCE 损失直觉**：每个 batch（32,768 对），让模型区分哪条文本属于哪张图。相当于 32,768 选 1 的多选题——模型不是判断"对/错"，而是在"N 条文本中找出正确的那条"。这个任务比二分类难得多，迫使模型学到更本质的特征。

CLIP 创新：同时做两个方向——从图像找文本 + 从文本找图像，loss 取平均。这避免了单方向训练中某个编码器"偷懒"的问题。

### 3.2 Prompt Engineering

**为什么不能直接用类别名作为文本输入？**

答：预训练数据中的文本是完整的自然语句（"a cute puppy playing in the grass"），不是单个词（"dog"）。直接用单词会造成训练-推理分布不匹配（distribution gap）。加 "a photo of" 等前缀让推理时的输入格式更接近训练数据。CLIP 实验显示，正确的 prompt 模板能将 CIFAR-10 准确率从 63.7% 提升到 79.6%（+16 个百分点）。

**我的研究中 Prompt 模板设计草稿**：
```
已知类别模板：
- "a photo of a {cls} on the road"
- "a {cls} debris on the highway"
- "road surface with {cls} on it"
- "a close-up view of {cls} on asphalt"

异常/未知模板：
- "an unknown object on the road surface"
- "a foreign debris on the highway"
- "background: clean road without debris"

背景模板（负类，排除路面本身）：
- "a clean asphalt road surface"
- "normal highway without debris"
```

**Prompt Ensemble 的含义**：不是用单个模板，而是把多个模板计算的文本特征取平均。相当于"多角度描述同一类别"，比单一措辞更鲁棒。CLIP 论文发现 prompt ensemble 提升约 5 个百分点，效果相当于 4 倍计算量。

### 3.3 Zero-Shot 推理流程

```
Step 1: YOLO 检测框裁剪图像 → 缩放到 CLIP 输入尺寸（224×224 或 336×336）
Step 2: 图像送入 CLIP Image Encoder → L2 归一化 → 图像特征向量
Step 3: N 条 prompt 模板送入 CLIP Text Encoder（可预先计算缓存）→ N 个文本特征向量
Step 4: 图像特征 · 文本特征 = 余弦相似度矩阵 → 乘温度参数 τ → Softmax
Step 5: 最高分对应的模板类别 = 识别结果；分数可作为置信度辅助 OOD 判断
```

**与我的第四章对应关系**：
- 输入：YOLOv8（改进后）输出的检测框，裁剪后送入 CLIP
- 文本库：预定义的路面抛洒物类别模板 + 未知类通用模板
- 输出：类别名 + 相似度分数（高相似度=已知类，低相似度=潜在未知抛洒物 → OOD）

---

## 实验结果记录（Day 7，Section 5 选读）

### Table 1 / Figure 5 关键数据

CLIP ViT-L/14 zero-shot 在 ImageNet 上的精度：**76.2%**（与原始 ResNet-50 监督训练的 76.2% 持平）

在 27 个数据集中，CLIP zero-shot 在 16 个上优于监督 ResNet-50 线性分类器。

**对我的研究的启示**：CLIP 的 zero-shot 能力在通用场景很强，但论文也指出对专业化场景（卫星图 ≈38.5%）效果差。路面抛洒物场景介于两者之间——有明确的视觉特征（比卫星图容易）但比 ImageNet 通用物体更细化。第四章的关键实验是验证 CLIP 在路面场景的 prompt 设计是否有效，可能需要微调或 adapter。

---

## 代码验证记录（Day 8）

运行 `experiments/clip_module/exp003_clip_zeroshot_eval.py` 后，从
`experiments/clip_module/runs/exp_003a_openai-clip-vit-base-patch32/summary.json`
填写：

- 数据划分清单 SHA-256：
- 测试图片 / 真值框：
- GL：正确数 / 总数、top-1、95% CI：
- RU：正确数 / 总数、top-1、95% CI：
- GL+RU 综合 top-1、95% CI：
- 预留类别 OOD AUC：
- 主要混淆方向：
- 结论与局限：

---

## 与我的研究的关系

- **直接用**：
  - 推理阶段的图文相似度计算（第四章核心）
  - Prompt Template 设计方法（论文 Section 3.2）
  - 预训练权重（`ViT-B/32` 或 `ViT-L/14@336px`），不重新训练

- **参考**：
  - 对比学习思想（当前采用的 CLIP 余弦相似度/OOD 代理评分可借鉴——正样本靠近、负样本远离）
  - 温度参数 τ 的作用（控制 softmax 平滑度，影响置信度分布）

- **不用**：
  - 预训练过程（直接加载开源权重）
  - 大规模数据收集（WIT 不可复现，也不需要）

---

## 架构精读补充（2026-05-28 从 PDF 直接读取）

### 模型规格（Figure 3 / Section 2.4/2.5）

**图像编码器**（两种选择）：
- ResNet 系列：RN50、RN101、RN50x4、RN50x16、RN50x64（x 倍宽度缩放）
- Vision Transformer 系列：ViT-B/32、ViT-B/16、**ViT-L/14**（论文最强模型，336px 精调版称 ViT-L/14@336px）

**文本编码器**：
- 63M 参数 Transformer，12 层，512 维，8 头自注意力
- BPE 编码，最大 token 长度 76
- 取 `[EOS]` 位置的最后一层输出作为文本特征，再线性投影到多模态空间

**训练规格**（Section 2.5）：
- 数据集：WIT（WebImageText），4 亿图文对，50 万查询词构建
- Batch size：**32,768**（非常大，这是负样本对来源）
- 训练 32 个 epoch，Adam + 余弦学习率衰减 + decoupled weight decay
- 投影层：**线性投影**（不是非线性）—— 作者发现非线性投影无益于 CLIP

**伪代码核心逻辑（Figure 3）**：
```python
# 提取特征
I_f = image_encoder(I)           # [n, d_i]
T_f = text_encoder(T)            # [n, d_t]
# L2 归一化 + 投影到联合空间
I_e = l2_normalize(I_f @ W_i)   # [n, d_e]
T_e = l2_normalize(T_f @ W_t)   # [n, d_e]
# 缩放余弦相似度矩阵
logits = I_e @ T_e.T * exp(t)   # [n, n], t 是可学习参数
# 对称交叉熵损失
loss = (cross_entropy(logits, labels) + cross_entropy(logits.T, labels)) / 2
```

### 零样本关键结论（Section 3.1 / 3.5）

**Table 1 数据**（直接引用可进论文）：
- CLIP zero-shot vs Visual N-Grams：ImageNet 76.2% vs 11.5%（提升 64.7 个百分点）
- CLIP zero-shot 与有监督 ResNet-50（76.2%）持平，但不使用任何 ImageNet 训练样本

**Figure 5 数据**（27 个数据集对比）：
- CLIP zero-shot 在 16/27 个数据集上优于有监督 ResNet-50 线性分类器
- 明显胜出的：Stanford Cars（+28.9%）、Food101（+22.5%）、Kinetics700（+14.5%）
- 明显劣势的：MNIST（-10.0%）、KITTI Distance（-34%）——抽象任务/特殊领域

**Prompt Engineering（Section 3.1.4）**：
- 默认模板 `"A photo of a {label}."` 是最佳通用起点
- Prompt ensemble（80 个不同描述取平均）在 ImageNet 上额外提升 3.5%，相当于 4 倍计算量的"免费"涨点
- 领域特化模板比通用模板好：`"a {label} on the road"` 适合我们的场景

---

## 读完后还不懂的地方（已解答部分）

1. ViT 的 self-attention 具体怎么在 224×224 图上运作的？patch 切分后位置编码怎么加？
   → 暂未精读 ViT 原文，待补

2. **【已解答】CLIP 的温度参数 τ 是学出来的还是固定的？**
   → **学出来的**。论文 Section 2.3 明确说："the temperature parameter τ is directly optimized during training as a log-parameterized multiplicative scalar"，初始化为 0.07，训练时自动调整，防止超过 100（避免训练不稳定）。

3. 如果需要微调 CLIP 适配路面场景，哪种方式最轻量？
   → 优先级：Prompt Tuning（CoCoOp）> Linear Probe > LoRA/Adapter。路面场景视觉特征足够独特，可能 Prompt Tuning 已够用，待 EXP-003 实验后决定。

---

## 需要进一步查的问题

- [x] ViT 基本结构：图像切分为 14×14 patches → 线性投影 → + 位置编码 → Transformer
- [ ] 余弦相似度和点积相似度的区别？（L2 归一化后等价，CLIP 用归一化后的点积）
- [ ] 路面场景 CLIP prompt 微调方案调研
