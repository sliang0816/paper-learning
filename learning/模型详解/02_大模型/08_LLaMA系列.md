# 30i. LLaMA 系列

> **定位**：开源 LLM 里程碑，现代 VLM 骨干的事实标准
> **论文**：
> - LLaMA 1：*LLaMA: Open and Efficient Foundation Language Models*（Touvron et al., Meta，2023-02）
> - LLaMA 2：*Llama 2: Open Foundation and Fine-Tuned Chat Models*（Touvron et al., Meta，2023-07）
> - LLaMA 3：*The Llama 3 Herd of Models*（Meta，2024-07）
> **必读前置**：28 Transformer · 30g RoPE · 30e InstructGPT/RLHF
> **配套图**：[figures/m30i_llama.svg](../figures/m30i_llama.svg)

---

## 1. 提出背景

2022 年 ChatGPT 爆火时，GPT-3/4 全部闭源。学界和开源社区迫切需要一个**可公开使用、可本地运行**的强大基础 LLM。

2023 年 2 月，Meta 发布 LLaMA 1，震撼点：

> **7B 参数 LLaMA** 在许多 benchmark 上**超越 175B 参数 GPT-3**。
> 原因：训练 token 数量，更多更高质量数据（1.4T token），而非更大模型。

LLaMA 系列迅速成为开源 LLM 的事实标准，Vicuna、Alpaca、Mistral、InternLM、Qwen 均以此为蓝本，进而成为 LLaVA、InternVL 等主流 VLM 的语言骨干。

---

## 2. 架构设计（相对于原版 Transformer 的四处修改）

LLaMA 使用标准 Decoder-only 自回归 Transformer，但针对训练稳定性和推理效率做了四处关键修改：

### 2.1 Pre-normalization：RMSNorm（取代 Post-LayerNorm）

**原版 Transformer**：残差输出之后做 LayerNorm（Post-Norm）

**LLaMA**：残差输出**之前**做 RMSNorm（Pre-Norm）→ 训练更稳定

$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\dfrac{1}{d}\sum_{i=1}^d x_i^2 + \epsilon}} \cdot \gamma$$

相比 LayerNorm 去掉了均值减法（无需计算 $\mu$），计算量降低约 15%，实验表明效果等同。

### 2.2 SwiGLU 激活（取代 ReLU FFN）

**原版 FFN**：$\text{FFN}(x) = \text{ReLU}(xW_1) W_2$（2 个矩阵）

**LLaMA FFN**（SwiGLU）：

$$\text{FFN}_{\text{SwiGLU}}(x) = \bigl(\underbrace{\text{SiLU}(xW_1)}_{\text{门控}} \odot \underbrace{xW_3}_{\text{值}}\bigr) W_2$$

$$\text{SiLU}(x) = x \cdot \sigma(x) = \frac{x}{1+e^{-x}} \quad \text{（等同 Swish）}$$

- 3 个投影矩阵（$W_1, W_2, W_3$）替代原来 2 个
- 中间维度从 $4d$ 缩到 $\frac{8d}{3}$（保持参数量相近）
- 门控结构允许网络"选择性通过"信息，实验上比 ReLU 显著更好

### 2.3 RoPE（取代绝对位置编码）

不添加绝对 position embedding，而是在每个 Attention 层的 Q/K 向量上施加旋转矩阵注入相对位置（详见 30g RoPE）。

好处：上下文长度可以在推理时超出训练时的最大长度（配合外推策略），是后来 LLaMA 3 实现 128K 上下文的基础。

### 2.4 GQA：Grouped Query Attention（LLaMA 2+）

| 方案 | Q heads | K/V heads | KV Cache 大小 |
|------|---------|-----------|---------------|
| MHA（标准） | H | H | $O(n \cdot H \cdot d_k)$ |
| MQA（多查询） | H | 1 | $O(n \cdot d_k)$ |
| **GQA**（分组）| H | G（G < H） | $O(n \cdot G \cdot d_k)$ |

每组 $H/G$ 个 Q heads 共享一对 K/V heads：

$$\text{GQA}: \quad \text{Attn}(Q_i, K_{\lfloor i/g \rfloor}, V_{\lfloor i/g \rfloor}), \quad g = H/G$$

LLaMA 2-70B 采用 $H=64, G=8$，KV Cache 减少为 MHA 的 1/8，推理显存大幅下降，性能接近 MHA。

---

## 3. LLaMA 1（2023-02）

**核心贡献**：在公开数据上训练高效 LLM，打破"更大才更好"的参数迷信。

| 模型 | 参数量 | 层数 | 头数 | 隐维 | 训练 Token |
|------|--------|------|------|------|-----------|
| LLaMA-7B | 7B | 32 | 32 | 4096 | 1.0T |
| LLaMA-13B | 13B | 40 | 40 | 5120 | 1.0T |
| LLaMA-33B | 33B | 60 | 52 | 6656 | 1.4T |
| LLaMA-65B | 65B | 80 | 64 | 8192 | 1.4T |

**训练数据（1.4T token）**：
- CommonCrawl（去重）：~67%
- C4：~15%
- GitHub：~4.5%
- Wikipedia：~4.5%
- Books（Gutenberg + Books3）：~4.5%
- ArXiv：~2.5%
- StackExchange：~2%

**关键结论**：LLaMA-13B 在 CommonsenseQA、BoolQ、NaturalQuestions 等 benchmark 上超越 GPT-3（175B）；LLaMA-65B 接近 Chinchilla（70B）和 PaLM（540B）。

**开源策略**：学术研究可申请权重（研究许可证，不允许商用）。

---

## 4. LLaMA 2（2023-07）

**核心贡献**：对齐训练（RLHF）+ GQA + 上下文加倍，推出可商用版本。

| 模型 | 参数量 | 上下文 | GQA | 对齐 |
|------|--------|--------|-----|------|
| LLaMA 2-7B/13B | 7B/13B | 4096 | MHA（无 GQA）| SFT+RLHF（Chat）|
| LLaMA 2-34B | 34B | 4096 | GQA | SFT+RLHF（Chat）|
| LLaMA 2-70B | 70B | 4096 | GQA（G=8）| SFT+RLHF（Chat）|

**训练数据**：2T token，比 LLaMA 1 增加约 40%，包含更多代码和安全过滤。

**对齐训练流程（Chat 版本）**：
1. **SFT（有监督微调）**：人工编写的高质量对话数据
2. **两个奖励模型**：分别用于有用性（helpfulness）和无害性（safety）
3. **RLHF with PPO + 拒绝采样**（Rejection Sampling Fine-tuning）

**Ghost Attention（GAtt）**：解决多轮对话中指令遗忘问题——将系统提示注入每轮的注意力中，让模型在长对话中维持角色设定。

**上下文 2048→4096**：通过 RoPE 频率调整（$\theta$ 从 10000 上调为 500000 用于 LLaMA 3）实现。

---

## 5. LLaMA 3 / 3.1（2024-04/07）

**核心贡献**：128K 词汇表 + 128K 上下文 + DPO 对齐 + 多模态支持，405B 达到 GPT-4 级别。

| 模型 | 参数量 | 上下文 | Vocab | GQA |
|------|--------|--------|-------|-----|
| LLaMA 3-8B | 8B | 8K（→ 128K 通过 3.1）| 128K | G=8 |
| LLaMA 3-70B | 70B | 8K（→ 128K）| 128K | G=8 |
| LLaMA 3.1-405B | 405B | **128K** | 128K | G=8 |

**128K 词汇表（vs LLaMA 2 的 32K）**：
- BPE tokenizer 词汇量扩大 4×
- 更好的多语言支持（中日韩等非英语）
- 每个 token 覆盖更多字符，序列更短，效率更高

**训练数据：15T token**（LLaMA 2 的 7.5×）：
- 数据质量过滤（分类器判断数据质量）
- 代码数据大幅增加（→ 代码理解能力显著提升）

**对齐：SFT + DPO（Direct Preference Optimization）**：
- 替代 PPO 的 RLHF，不训练独立奖励模型
- 直接对偏好对数据（chosen/rejected pairs）优化策略：
$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}\left[\log \sigma\!\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]$$

**LLaMA 3.2（2024-09）**：新增多模态支持（11B/90B Vision 版本），将 ViT 图像编码器接入 LLaMA 3 → 直接成为 VLM。

---

## 6. 三代对比总览

| 维度 | LLaMA 1（2023-02） | LLaMA 2（2023-07） | LLaMA 3.1（2024-07） |
|------|-------------------|-------------------|--------------------|
| 最大参数量 | 65B | 70B | **405B** |
| 上下文长度 | 2048 | 4096 | **128K** |
| 词汇表大小 | 32K | 32K | **128K** |
| GQA | 无 | 70B 有 | **全部** |
| 对齐方式 | 无 | SFT + PPO/RLHF | SFT + **DPO** |
| 训练 Token | 1.4T | 2T | **15T** |
| 开源许可 | 研究 | 可商用 | 可商用 |
| 多模态 | 无 | 无 | **3.2 加 Vision** |
| 代表能力 | 超 GPT-3 的 7B | Chat 对齐 | 接近 GPT-4o |

---

## 7. 架构演进中的技术传承

```
原版 Transformer（2017）
    ↓ 去掉 Encoder，仅 Decoder，改 Post-Norm → Pre-Norm
GPT-2/3（2019/2020）
    ↓ + RMSNorm + SwiGLU + RoPE
LLaMA 1（2023）← 当前文件
    ↓ + GQA + RLHF + 4K 上下文
LLaMA 2（2023）
    ↓ + 128K vocab + DPO + 128K 上下文 + Vision
LLaMA 3/3.1/3.2（2024）
```

---

## 8. 与本项目的关系

- **本项目第四章（CLIP 零样本识别）**：LLaMA 不直接参与检测推理，但 LLaMA 是 LLaVA（37 LLaVA/InternVL）的语言骨干——理解 LLaMA 架构有助于理解 VLM 如何将视觉特征输入进语言模型。
- **论文第二章相关工作**：VLM 综述中需提及大语言模型发展（从 GPT-3→LLaMA→VLM）；LLaMA 是连接"纯语言 LLM"到"多模态 VLM"的关键桥梁。
- **LoRA 微调（30c LoRA）**：本项目如考虑微调 VLM，最常见的目标模型正是 LLaMA-based VLM（LLaVA/InternVL），LoRA 微调方案直接适用。

---

## 参考文献

- Touvron H, et al. *LLaMA: Open and Efficient Foundation Language Models*. arXiv:2302.13971, 2023.
- Touvron H, et al. *Llama 2: Open Foundation and Fine-Tuned Chat Models*. arXiv:2307.09288, 2023.
- Meta. *The Llama 3 Herd of Models*. arXiv:2407.21783, 2024.
- 前置：28 Transformer · 30g RoPE · 30e InstructGPT/RLHF · 30c LoRA
- 下游应用：37 LLaVA/InternVL（LLaMA 作为 VLM 语言骨干）
