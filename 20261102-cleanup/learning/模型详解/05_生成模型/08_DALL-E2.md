# 47a. DALL-E 2

> **定位**：CLIP 先验 + 级联 DDPM 解码器，2022 年文生图质量标杆
> **论文**：*Hierarchical Text-Conditional Image Generation with CLIP Latents*（OpenAI，Ramesh et al.，2022）
> **必读前置**：33 CLIP · 46 DDPM 与 DDIM · 47 Latent / Stable Diffusion
> **配套图**：[figures/m47a_dalle2.svg](../figures/m47a_dalle2.svg)

---

## 1. 提出背景

DALL-E 1（2021）用离散 VAE（dVAE）将图像量化为 token，再训练 12B 参数自回归 Transformer 对文本+图像 token 建模——质量有限，分辨率仅 256×256。

2021 年 CLIP 的出现提供了一个关键工具：**CLIP 图像嵌入空间捕获图像的语义内容，同一语义的不同图像在该空间中聚集在一起**。DALL-E 2 的核心洞察：

> 将"文本→像素"拆成两步：
> 1. **Prior**：文本嵌入 $y_c$ → CLIP 图像嵌入 $z_i$（语义推理，DDPM 先验）
> 2. **Decoder**：CLIP 图像嵌入 $z_i$ → 像素图像（视觉渲染，DDPM 解码器）

与同期模型对比：
- **Imagen**（Google，2022）：T5-XXL 文本编码 + 像素级级联 DDPM，不用 CLIP 图像先验
- **Stable Diffusion**（2022）：CLIP 文本编码 + **潜空间**扩散（VAE 压缩 8×），开源
- **DALL-E 2**：CLIP 文本+图像双编码 + 像素级扩散，不开源

---

## 2. 核心架构

```
输入文本 y："a photo of a cat sitting by the sea at sunset"
    │
    ▼
CLIP 文本编码器（ViT-L/14，参数冻结）
    │  yc ∈ R^768（文本语义嵌入）
    ▼
Prior 先验网络  pθ(zi | yc)
    │  DDPM：学习从文本语义坐标 → 图像语义坐标
    │  允许多次采样 → 同文本不同语义风格
    │  zi ∈ R^768（CLIP 图像嵌入）
    ▼
DDPM 解码器  pφ(x | zi)
    │  以 zi 为条件（通过投影层注入各扩散步）
    │  生成 64×64 基础像素图
    ▼
超分上采样（两级 DDPM）
    │  64×64 → 256×256 → 1024×1024
    ▼
最终输出图像
```

### 2.1 Prior 先验网络

Prior 的训练目标：给定 CLIP 文本嵌入 $y_c$，预测配对的 CLIP 图像嵌入 $z_i$：

$$p_\theta(z_i \mid y_c)$$

训练数据：CLIP 训练集中已有的（图文对 → 双塔各自编码 → 配对嵌入向量）

实现方式（论文对比了两种，DDPM 更优）：
- 自回归 Prior：自回归地预测量化后的 $z_i$ token（更差）
- **扩散 Prior**（采用）：标准 DDPM，在连续向量空间对 $z_i$ 去噪

Prior 的价值：**引入多样性**——同一文本 $y_c$ 多次采样 $z_i$ 会得到不同的 CLIP 图像嵌入，解码后图像语义相同但视觉细节各异（姿态、构图、色调）。

### 2.2 DDPM 解码器

以 CLIP 图像嵌入 $z_i$ 为条件的 DDPM，基础输出分辨率 64×64：

$$p_\phi(x \mid z_i, [y_c])$$

实现细节：
- $z_i$ 通过可学习线性投影层注入 DDPM 的每个 U-Net 层（类似时间步嵌入）
- 同时也可选注入文本嵌入 $y_c$ 作为辅助条件（增强文本-图像对齐）
- 去噪目标：标准 $\epsilon$-prediction 或 $v$-prediction

### 2.3 级联超分辨率

| 阶段 | 模型 | 输入 | 输出 | 备注 |
|------|------|------|------|------|
| 基础解码 | DDPM | $z_i$ | 64×64 | 语义由 $z_i$ 决定 |
| 上采样 1 | DDPM | 64×64 + 低频 | 256×256 | 条件：低分辨率图 + CLIP 文本嵌入 |
| 上采样 2 | DDPM | 256×256 + 低频 | 1024×1024 | 增加高频细节 |

两级上采样器各有独立参数，以低分辨率图 + 文本信号为条件。

---

## 3. 核心能力（CLIP 语义空间赋予）

### 3.1 文本到图像生成（Text-to-Image）

完整流程：$y$ → CLIP 文本编码 → Prior → 解码 → 超分。主要功能，2022 年上半年质量领先。

### 3.2 图像变体（Variations）

给定参考图 $x$：

$$z_i = \text{CLIP\_image}(x) \quad \text{（跳过 Prior，直接用图像的 CLIP 嵌入）}$$

多次用 Decoder 解码同一 $z_i$ 得到**语义一致但视觉各异**的变体图。相当于在 CLIP 语义空间固定语义坐标，解码时引入随机性。

### 3.3 图像插值（Interpolation）

两张图 $x_1$, $x_2$ 的 CLIP 图像嵌入做球面线性插值（SLERP）：

$$z_{i,\lambda} = \text{SLERP}(z_{i,1},\, z_{i,2},\, \lambda), \quad \lambda \in [0, 1]$$

中间嵌入解码后得到**语义渐变**的中间图像，可生成插值动画。

### 3.4 图像编辑（Inpainting / Outpainting）

Decoder 支持 mask 条件：给定已知区域像素 + 二值掩码，DDPM 在条件去噪时仅对 mask 区域去噪，其余区域固定——利用扩散模型的条件概率实现语义一致的局部填充。

---

## 4. 训练细节

| 项目 | 规格 |
|------|------|
| 文本编码器 | CLIP ViT-L/14（OpenAI 预训练，冻结） |
| Prior 架构 | Transformer-based DDPM（~1B 参数） |
| Decoder 架构 | DDPM with U-Net（~3.5B 参数含超分） |
| 训练数据 | ~2.5 亿图文对（来源未公开） |
| Guidance | Classifier-Free Guidance（CFG），$w \approx 1.0$ |
| 训练精度 | FP16 混合精度 |
| COCO 零样本 FID | ~10.4（Zero-shot，Imagen 7.3，SD 8.6） |

---

## 5. 与同期模型对比

| 维度 | DALL-E 1（2021） | **DALL-E 2（2022）** | Imagen（2022） | SD v1（2022） |
|------|-----------------|---------------------|----------------|---------------|
| 文本→图像方法 | dVAE + 自回归 Transformer | CLIP Prior + 级联 DDPM | T5-XXL + 像素级级联 DDPM | CLIP + 潜空间 DDPM |
| 文本编码器 | BPE（简单词片） | CLIP ViT-L/14 | T5-XXL（4.6B，强大） | CLIP ViT-L/14 |
| 图像编码器 | dVAE 离散 | CLIP ViT-L/14（图像先验） | 无（纯文本条件） | VAE（连续潜空间） |
| 潜空间压缩 | dVAE（256 token） | 无（像素级扩散） | 无（像素级） | VAE 8× 压缩 |
| 最高分辨率 | 256×256 | 1024×1024 | 1024×1024 | 512（可扩到 768） |
| 图像变体/插值 | 无 | **✓（CLIP 空间运算）** | 无 | 需 IP-Adapter |
| 开源 | 否 | 否 | 否 | **是** |
| 核心优势 | 首次高质量文生图 | 变体/插值/编辑 | 文本理解更强 | 速度/定制/生态 |

> **Imagen vs DALL-E 2**：Imagen 用 T5-XXL 文本编码器，对属性绑定（"红色的球在蓝色的盒子左边"）理解更准确；DALL-E 2 的 CLIP 文本编码器在细粒度属性组合上有时失误。人工评测显示 Imagen 在 DrawBench 上胜出。

---

## 6. 历史地位与局限

**地位**：
- 2022 年上半年文生图质量标杆，第一次让"AI 生成图像"引发广泛公众讨论
- 首次提出"先验网络分离语义推理与视觉渲染"的范式，在 CLIP 嵌入空间做图像变体/插值
- 推动了 2022 年图像生成质量的快速竞争（Imagen、SD 相继推出）
- DALL-E 3（2023）延续公司级 API 方式，用更强的文本重标注（GPT-4V 描述图）提升对齐

**局限**：
- 不开源，同年 8 月 Stable Diffusion 开源后，社区生态被 SD 迅速主导
- CLIP 文本编码器对细粒度属性绑定不如 T5（Imagen 超越的原因）
- 像素级扩散（非潜空间）导致高分辨率生成计算成本高
- 1024px 生成仍有时出现与文本不匹配的细节

---

## 7. 与本项目的关系

- **本项目第四章 CLIP 零样本识别**：直接使用 CLIP ViT-L/14 编码器，与 DALL-E 2 共享同一基础模型。DALL-E 2 证明 CLIP 图像嵌入空间具有丰富语义结构（可插值、可解码），印证了用 CLIP 相似度做零样本分类的合理性。
- **本项目数据增强（ControlNet）**：ControlNet 基于 SD（潜空间扩散），技术上是 DALL-E 2 同期竞品的开源版本，用于合成稀缺类路面抛洒物样本。
- **论文第二章相关工作**：DALL-E 2 是"视觉语言模型用于生成"方向的重要里程碑，可在 VLM 综述中简要提及。

---

## 参考文献

- Ramesh A, Dhariwal P, Nichol A, et al. *Hierarchical Text-Conditional Image Generation with CLIP Latents*. arXiv:2204.06125, 2022.
- 前置基础：33 CLIP（Radford 2021）· 46 DDPM 与 DDIM（Ho 2020）
- 同期竞品：Saharia C, et al. *Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding (Imagen)*. NeurIPS 2022.
- 同期开源替代：47 Latent / Stable Diffusion（Rombach 2022）
- 后续演进：DALL-E 3（2023，GPT-4V 数据重标注 + Sora 同框架）
