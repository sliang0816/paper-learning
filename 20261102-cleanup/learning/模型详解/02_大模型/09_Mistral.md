# 30j. Mistral 7B / Mixtral 8×7B

> **定位**：滑动窗口注意力 + 稀疏 MoE，开源 LLM 效率的新标杆
> **论文**：
> - Mistral 7B：*Mistral 7B*（Jiang et al., Mistral AI，2023-09）
> - Mixtral：*Mixtral of Experts*（Jiang et al., Mistral AI，2023-12）
> **必读前置**：30i LLaMA 系列 · 28 Transformer
> **配套图**：[figures/m30j_mistral.svg](../figures/m30j_mistral.svg)

---

## 1. 提出背景

LLaMA 2-13B 已相当强大，但需要 26GB 显存加载，推理慢。2023 年 9 月，Mistral AI 发布 Mistral 7B，给出了一个令人惊讶的结果：

> **7B 参数的 Mistral 在所有 benchmark 上全面超越 LLaMA 2-13B**，
> 在 Reasoning 任务上甚至超越 LLaMA 2-34B。

核心原因是两个架构创新：**滑动窗口注意力（SWA）** 和 **Rolling Buffer KV Cache**——不是参数更多，而是更高效地利用有限上下文。

三个月后（2023-12），Mistral AI 进一步发布 Mixtral 8×7B，引入**稀疏 Mixture of Experts（MoE）**：总参数 46.7B，但每个 token 只激活 12.9B，推理成本等同于 12.9B 密集模型，性能超越 LLaMA 2-70B。

---

## 2. Mistral 7B：滑动窗口注意力

### 2.1 全局注意力的问题

标准 Self-Attention：位置 $i$ 的 token 可以 attend 到序列中所有位置（0 到 $i$）。

- **计算复杂度**：$O(n^2 \cdot d)$（$n$ 为序列长度）
- **KV Cache 大小**：$O(n \cdot H \cdot d_k)$（随序列增长线性增大）
- 对于长序列（16K+ token），KV Cache 可超过数十 GB

### 2.2 滑动窗口注意力（SWA）

位置 $i$ 的 token 只 attend 到最近的 $w$ 个位置（$i-w$ 到 $i$）：

$$\text{SWA}: \quad \text{Attn}(Q_i, K_{i-w:i}, V_{i-w:i})$$

Mistral 使用 $w = 4096$（窗口大小）。

**关键问题**：窗口宽 4096，是否只能捕捉短程依赖？

**答案：不是**。通过多层叠加，感受野随层数扩大：

$$\text{感受野（第 } L \text{ 层）} = L \times w$$

以 Mistral 32 层、$w=4096$ 为例：第 32 层的感受野 = $32 \times 4096 = 131072$ 个 token。

这与 CNNs 的卷积堆叠逻辑完全类比：局部卷积 × 多层 = 全局感受野。

| 对比维度 | 全局注意力 | 滑动窗口注意力 |
|---------|----------|---------------|
| 每层复杂度 | $O(n^2)$ | $O(n \times w)$ |
| KV Cache | $O(n)$ | $O(w)$（固定上限）|
| 单层感受野 | 全序列 | 最近 $w$ 个 |
| 多层感受野 | 全序列 | $L \times w$（指数增长视角）|

### 2.3 Rolling Buffer KV Cache（滚动 KV 缓存）

SWA 只需要最近 $w=4096$ 个位置的 K/V，因此 KV Cache 大小**固定为 4096**，不随序列增长：

$$\text{位置 } i \text{ 的 K/V 存入 Cache 槽位 } (i \bmod w)$$

超出 $w$ 的旧 K/V 自动被新值覆盖（循环缓冲区）。

效果：32K token 长序列的 KV Cache 内存占用**与 4K 等同**，为长文本推理打开了新空间。

### 2.4 Chunk Prefill（分块预填充）

对于长 prompt（如 RAG 场景的长文档），Mistral 将 prompt 切成大小为 $w$ 的 chunk 逐块处理：

- 每个 chunk 的 KV 写入 Rolling Buffer
- 生成阶段正常使用 SWA + Rolling Buffer
- 好处：prefill 阶段内存峰值可控，无需加载全部 prompt 的 KV

---

## 3. Mistral 7B 架构总览

Mistral 7B 本质上是 **LLaMA 架构 + SWA + GQA**：

| 组件 | 规格 |
|------|------|
| 层数 | 32 |
| 隐维（d_model）| 4096 |
| Q heads | 32 |
| KV heads（GQA）| 8 |
| FFN 类型 | SwiGLU（继承 LLaMA）|
| 归一化 | RMSNorm（继承 LLaMA）|
| 位置编码 | RoPE（继承 LLaMA）|
| 注意力 | **SWA（w=4096）** |
| 上下文长度 | 8192（通过 SWA 高效处理）|
| 参数量 | 7.24B |

---

## 4. Mixtral 8×7B：稀疏 Mixture of Experts

### 4.1 核心思想

普通 Transformer 的每个 token 都经过**同一个 FFN**。MoE 的想法：每层有 $N$ 个**专家 FFN**，每个 token 动态路由到其中最相关的 $k$ 个专家：

$$\text{MoE-FFN}(x) = \sum_{i \in \text{Top-k}} G_i(x) \cdot \text{Expert}_i(x)$$

$$G(x) = \text{softmax}(\text{TopK}(x \cdot W_g, k))$$

其中 $W_g$ 是路由权重矩阵，$\text{TopK}$ 只保留得分最高的 $k$ 个，其余置零（稀疏）。

### 4.2 Mixtral 8×7B 配置

| 项目 | 规格 |
|------|------|
| 每层专家数 $N$ | **8** |
| 每 token 激活专家数 $k$ | **2**（top-2）|
| 总参数量 | 46.7B |
| 每 token 激活参数 | **12.9B**（推理等同 12.9B 密集模型）|
| 架构基础 | Mistral 7B（SWA + GQA）|
| 上下文长度 | 32K |

计算过程（每层，对一个 token）：
1. Router 计算 8 个专家的得分：$g = \text{softmax}(xW_g) \in \mathbb{R}^8$
2. 取 top-2 得分对应的专家：$i_1, i_2 = \text{argsort}(g)[-2:]$
3. 加权求和：$\text{out} = g_{i_1} \cdot E_{i_1}(x) + g_{i_2} \cdot E_{i_2}(x)$

### 4.3 为什么 MoE 高效？

- **参数量 vs 计算量解耦**：Mixtral 总参数 46.7B（存储需求大），但每 token 只计算 12.9B（推理速度快）
- **专家专业化**：不同专家自发学习不同类型的知识（代码专家、数学专家等），无需人工标注
- **推理并行**：多 GPU 部署时不同专家可分布在不同设备，通信开销可接受

### 4.4 负载均衡问题

MoE 的潜在问题：路由器可能反复选择相同少数几个专家（专家崩塌）。
解决：辅助损失（auxiliary loss），惩罚专家负载不均：

$$\mathcal{L}_{\text{aux}} = \alpha \cdot \sum_{i=1}^N f_i \cdot P_i$$

其中 $f_i$ 是专家 $i$ 被选中的频率，$P_i$ 是路由器给专家 $i$ 的平均概率。

---

## 5. 性能对比

| 模型 | 参数量（激活）| MMLU | HellaSwag | HumanEval | 显存需求 |
|------|-------------|------|-----------|-----------|---------|
| LLaMA 2-7B | 7B | 45.3 | 77.2 | 12.8 | ~14GB |
| **Mistral 7B** | 7B | 60.1 | 81.3 | 30.5 | ~14GB |
| LLaMA 2-13B | 13B | 54.8 | 80.7 | 18.3 | ~26GB |
| LLaMA 2-70B | 70B | 68.9 | 87.3 | 29.9 | ~140GB |
| **Mixtral 8×7B** | 12.9B（总 46.7B）| 70.6 | 89.1 | 40.2 | ~90GB（总）|

> Mistral 7B 以 7B 参数超越 LLaMA 2-13B；Mixtral 8×7B 以 12.9B 激活参数超越 LLaMA 2-70B。

---

## 6. 与 LLaMA 架构的关系

```
LLaMA 架构（RMSNorm + SwiGLU + RoPE + GQA）
    │
    ├── Mistral 7B：+ 滑动窗口注意力（SWA）+ Rolling Buffer KV Cache
    │       → 长上下文高效推理
    │
    └── Mixtral 8×7B：Mistral 7B 骨干 + 每层 FFN 替换为 8 专家 MoE
            → 参数多、推理不慢（top-2 稀疏激活）
```

Mistral 证明了 SWA 可以在不损失精度的前提下大幅降低 KV Cache 内存；Mixtral 证明了 MoE 可以在不增加推理成本的前提下大幅提升模型容量。两者的思路已被后续模型广泛采纳（DeepSeek-MoE、Qwen-MoE 等）。

---

## 7. 与本项目的关系

- **间接关系**：本项目使用 CLIP + YOLOv8 做检测，不直接用 Mistral。
- **技术背景**：Mistral 的 SWA 思路（局部注意力 + 多层全局感受野）与 CNN 卷积的感受野扩展逻辑完全类比，论文第二章讲注意力与局部性时可作对比示例。
- **MoE 方向**：DeepSeek-V2/V3（已在本领域引发广泛关注）正是将 MoE 推向极致的代表；Mixtral 是理解 MoE 的入门基础。

---

## 参考文献

- Jiang A Q, et al. *Mistral 7B*. arXiv:2310.06825, 2023.
- Jiang A Q, et al. *Mixtral of Experts*. arXiv:2401.04088, 2023.（注：发布于 2023-12，arXiv 编号为 2401，因时区/日期差异）
- 前置：30i LLaMA 系列 · 28 Transformer
- 延伸：DeepSeek-V2（Multi-Head Latent Attention + MoE）；Qwen-MoE
