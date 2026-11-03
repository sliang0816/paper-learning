# 49a. Sora

> **定位**：时空 Patch DiT 扩散，2024 视频生成里程碑
> **技术报告**：*Video generation models as world simulators*（OpenAI，2024-02，非同行评审）
> **必读前置**：48 DiT · 46 DDPM 与 DDIM · 31 ViT
> **配套图**：[figures/m49a_sora.svg](../figures/m49a_sora.svg)

---

## 1. 提出背景

2024 年 2 月，OpenAI 发布 Sora 技术博客（不是同行评审论文），演示了最长 1 分钟的 1080p 高清视频生成，引发业界震动。

Sora **不是全新架构**。它的技术洞察极其简洁：

> **视频 = 时空 Patch 序列**。ViT 把图像切成空间 patch 送进 Transformer；Sora 把视频切成时空 patch（$t_p \times h_p \times w_p$）送进 DiT——完全一样的范式，从 2D 扩展到 3D。

由此带来两个核心优势：
1. DiT 天然支持可变长序列 → 视频时长/分辨率/宽高比可以在训练时任意混合
2. DiT 已被证明扩展性良好（参见 48 DiT）→ 直接堆规模

---

## 2. 核心架构

```
输入视频 V ∈ R^{T×H×W×C}
    │
    ▼
Video VAE（时空压缩）
    │  时间压缩 ~4×，空间压缩 ~8×
    │  z ∈ R^{T'×H'×W'×C'}（潜空间视频）
    ▼
时空 Patch 划分
    │  Patch 大小：(t_p, h_p, w_p) = 例如 (1, 8, 8)
    │  Token 序列：x ∈ R^{L×d}
    │  L = (T'/t_p) × (H'/h_p) × (W'/w_p)
    ▼
线性投影 + 3D 位置编码
    │  每个 patch → d 维 token；加入时空位置信息
    ▼
DiT（扩散 Transformer）× N 层
    │  Transformer blocks + adaLN-Zero 条件注入
    │  条件：时间步 t + 文本嵌入（CLIP / T5）
    │  自注意力覆盖所有 L 个时空 token（全局时序一致性）
    ▼
逆变换：tokens → patches → 潜空间视频
    │
    ▼
Video VAE 解码
    │
    ▼
输出视频帧序列
```

---

## 3. 关键技术点

### 3.1 时空 Patch Token（核心创新）

**ViT 图像 patch**（2D）：

$$V_{\text{img}} \in \mathbb{R}^{H \times W \times C} \xrightarrow{\text{patch} (h_p, w_p)} x \in \mathbb{R}^{L \times d}, \quad L = \frac{HW}{h_p w_p}$$

**Sora 时空 patch**（3D，完全类比）：

$$V_{\text{vid}} \in \mathbb{R}^{T \times H \times W \times C} \xrightarrow{\text{patch} (t_p, h_p, w_p)} x \in \mathbb{R}^{L \times d}, \quad L = \frac{T}{t_p} \cdot \frac{H}{h_p} \cdot \frac{W}{w_p}$$

这个推广使得 Transformer 对视频的自注意力**同时覆盖时间维度和空间维度**：任意两帧中的任意两个空间位置可以直接相互 attend，无需额外设计时序模块（如 3D 卷积、时序注意力单独堆叠）。

### 3.2 Video VAE（压缩到潜空间）

与 SD 的图像 VAE 完全类比：
- SD：$x_{\text{img}} \in \mathbb{R}^{H \times W \times 3}$ → VAE → $z \in \mathbb{R}^{(H/8) \times (W/8) \times 4}$（8× 空间压缩）
- Sora：$V \in \mathbb{R}^{T \times H \times W \times C}$ → Video VAE → $z \in \mathbb{R}^{(T/4) \times (H/8) \times (W/8) \times C'}$（时间 4× + 空间 8×）

在潜空间做扩散（而非像素空间）大幅降低计算量。

### 3.3 可变时长/分辨率训练

**传统视频生成**：固定 256×256、16 帧，训练和推理分辨率必须一致。

**Sora**：训练时以**原生分辨率、原生宽高比、原生帧率**直接输入，不做 resize 或 pad：
- 16:9 横屏、9:16 竖屏、1:1 方屏混合训练
- 时长从 1 秒到 1 分钟混合
- 技术关键：位置编码支持可变长度（类似 3D 版 RoPE，在时间/高度/宽度三个维度各自编码相对位置）

推理时直接指定分辨率和时长，模型自适应。

### 3.4 DiT 条件注入（adaLN-Zero）

与图像 DiT 完全相同的条件注入机制：

$$\text{adaLN-Zero}:\quad \gamma, \beta = \text{MLP}(c), \quad c = \text{Embed}(t) + \text{TextEmbed}(y)$$

- $t$：当前扩散时间步（标量嵌入）
- $y$：文本描述（CLIP 或 T5 编码的文本嵌入）
- 每个 Transformer 层的 LayerNorm 参数由 $(γ, β)$ 动态调制

残差门控初始化为 0（Zero 初始化），训练初期等同于标准 Transformer，梯度稳定。

### 3.5 训练数据与重新标注（DALL-E 3 范式）

原始视频往往配有简短或低质量的字幕（甚至没有）。Sora 采用与 DALL-E 3 相同的**重新标注策略**：

1. 用视频理解模型（类 GPT-4V）对所有训练视频自动生成高质量、详细的文字描述
2. 用重新标注的描述替换原始字幕
3. 训练时以高质量描述为文本条件

效果：显著提升视频-文本对齐质量，减少"语义漂移"（生成内容与文本不符）。

---

## 4. "世界模拟器"能力

Sora 技术报告的副标题 *"world simulators"* 暗示更大目标——从视频生成向**物理世界建模**迈进：

| 能力 | 描述 |
|------|------|
| 长程时序一致性 | 同一物体/场景在数十秒内保持连贯（全局自注意力的自然结果）|
| 摄像机运动理解 | 推拉摇移、轨道运动、第一人称视角忠实执行 |
| 物理现象涌现 | 流体、碰撞、遮挡等简单物理规律隐式建模（未显式编程）|
| 多镜头剪辑 | 场景切换后角色、物体保持视觉一致 |
| 视频延伸 | 向前/向后扩展现有视频片段（图像级类似修复/外推）|
| 可控生成 | 根据文本/图像/视频片段指定风格、内容、运动 |

**技术报告坦承的局限**：
- 仍会产生物理错误（玻璃碎裂方向异常、人物肢体穿模）
- 长视频中细节随时间漂移（角色外貌缓慢变化）
- 复杂动作序列逻辑不一致（如接球轨迹物理不正确）
- 空间推理弱（"左/右/上/下"等方位关系有时混淆）

---

## 5. 与同期/后续视频模型对比

| 维度 | **Sora (2024-02)** | CogVideoX (2024) | Wan2.1 (2025) | HunyuanVideo (2024) |
|------|-------------------|------------------|---------------|---------------------|
| 机构 | OpenAI | 智谱 AI | 阿里 | 腾讯 |
| 开源 | **否** | 是 | 是 | 是 |
| 骨干 | DiT（全注意力时空）| DiT（Expert Attn）| DiT（改进）| DiT |
| 文本编码 | CLIP + T5（推测）| T5-XXL | UMT5 | LLaMA + CLIP |
| 可变时长 | **✓（训练时混合）** | 有限 | ✓ | ✓ |
| 最长视频 | ~60s | ~10s | ~25s | ~16s |
| 最高分辨率 | 1080p | 720p | 720p | 720p |
| 核心贡献 | 时空 patch 范式 | 专家注意力 | 开源高质量 | 双流架构 |

> 注：Sora 架构细节大部分推断自技术报告，CogVideoX/Wan2.1 等开源模型的设计受 Sora 启发，细节更清晰。

---

## 6. 历史地位

**里程碑意义**：
- 视频生成从"几秒低分辨率片段"跨越到"分钟级高清视频"，公众关注度引爆
- **时空 Patch + DiT** 范式被随后几乎所有视频生成模型（CogVideoX、Wan2.1、HunyuanVideo、Movie Gen 等）采纳，成为行业标准
- 证明 DiT 的扩展性可以从图像无缝推广到时序维度，无需专门的时序建模
- "视频作为世界模拟器"的叙事影响了后续 World Model、视频预测等研究方向

**注意**：
- Sora 是**技术博客**而非完整学术论文，许多关键细节（数据规模、模型参数量、训练 recipe、具体位置编码方案）未公开
- 截至 2025 年仍未开源，开源社区通过复现推断架构细节

---

## 7. 与本项目的关系

Sora 对本项目无直接技术依赖，但有以下关联：

- **生成模型脉络**：本项目用 ControlNet（基于 SD）合成稀缺类路面抛洒物，处于 Sora 所在扩散生成链的上游；论文数据增强章节描述技术背景时可提及生成模型的发展方向。
- **DiT 骨干**：理解 Sora 的前置是 48 DiT，DiT 同样是理解 SD3/FLUX.1（44d Flow Matching）的基础，技术脉络一致。
- **论文第二章相关工作**：生成模型综述结尾可简要提及 Sora，作为"视觉基础模型+扩散"向视频领域扩展的最新进展。

---

## 参考文献

- OpenAI. *Video generation models as world simulators*. Technical Report, 2024-02.
- 前置架构：48 DiT · 47 Latent / Stable Diffusion · 31 ViT
- 开源同类（更多技术细节）：
  - Yang Z, et al. *CogVideoX: Text-to-Video Diffusion Models with an Expert Transformer*. 2024.
  - Wan2.1 Technical Report, Alibaba, 2025.
  - Kong X, et al. *HunyuanVideo: A Systematic Framework for Large Video Generation Model*. 2024.
