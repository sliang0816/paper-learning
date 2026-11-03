# 模型详解

> 每个文件聚焦一种模型/架构，深度解读：背景 → 原理（结构图/公式）→ 关键创新 → 与本项目（路面抛洒物检测）的关系（仅真正相关的才写）→ 参考文献。
> **已按"项目相关性"分 6 个文件夹**：`00_必读`（课题关键路径）+ 5 个分类拓展。文件名内的编号 = 文件夹内阅读顺序。

> ❓ 阅读疑问与解答（Q1–Q185）：专属某模型的在该文末尾"📋 模型答疑"；跨模型/通用的在主题分册（[基础与序列](答疑_01_基础与序列.md)、[CNN 骨干](答疑_02_CNN骨干.md)、[目标检测](答疑_03_目标检测.md)、[Transformer 与视觉语言](答疑_04_Transformer与视觉语言.md)）。总入口见 [答疑总目录](答疑记录.md)。
> 📌 暂留概念记到 [待读清单](待读清单_暂留概念.md)｜📄 arXiv 原文见 [papers/论文清单](papers/论文清单.md)｜📈 [阅读进度](阅读进度.md)｜📊 [输入/输出速查表](模型输入输出速查.md)

---

## 00_必读（课题关键路径，40 篇）

> 两个创新点直接依赖：检测改进（YOLO 全线 + FPN/CBAM）+ CLIP 开放类识别（Transformer→ViT→CLIP）+ OOD（PatchCore）+ 数据增强。

**基础序列**
| 文件 | 一句话 |
|------|--------|
| [01 感知机与反向传播](00_必读/01_感知机与反向传播.md) | 神经网络起点与训练算法基石 |
| [02 RNN](00_必读/02_RNN.md) | 序列建模起点，seq2seq 与注意力的根基 |
| [03 LSTM](00_必读/03_LSTM.md) | 解决 RNN 长程依赖的门控机制 |

**骨干与模块**
| 文件 | 一句话 |
|------|--------|
| [04 CNN 卷积原理](00_必读/04_CNN卷积神经网络原理.md) ⭐ | 卷积/池化/感受野/权重共享，总纲 |
| [05 ResNet](00_必读/05_ResNet.md) ⭐ | 残差连接，现代 CNN 基石 |
| [06 MobileNet 系列](00_必读/06_MobileNet系列.md) ⭐ | 深度可分离卷积，边缘部署 |
| [07 BatchNorm/LayerNorm](00_必读/07_BatchNorm与LayerNorm.md) ⭐ | 稳定分布、加速收敛 |
| [08 数据增强 Mixup/CutMix/Mosaic](00_必读/08_Mixup_CutMix.md) | YOLOv8 默认 Mosaic，本项目直接用 |
| [09 SE-Net](00_必读/09_SENet.md) | 通道注意力鼻祖 |
| [10 CBAM](00_必读/10_CBAM.md) ⭐ | 通道+空间注意力，第三章改进组件 |
| [11 Deformable Conv](00_必读/11_DeformableConv.md) | 卷积采样位置可学习 |
| [12 PANet](00_必读/12_PANet.md) ⭐ | 自底向上增强，YOLO PAN 颈部来源 |

**目标检测全线**
| 文件 | 一句话 |
|------|--------|
| [13 R-CNN](00_必读/13_RCNN.md) | 两阶段检测开山 |
| [14 Fast R-CNN](00_必读/14_Fast_RCNN.md) | RoI Pooling，整图共享特征 |
| [15 Faster R-CNN](00_必读/15_Faster_RCNN.md) | RPN 端到端，两阶段标杆 |
| [16 FPN](00_必读/16_FPN.md) ⭐ | 多尺度融合，第三章 P2 理论基础 |
| [17 YOLOv1](00_必读/17_YOLOv1.md) | 单阶段实时检测开山 |
| [18 SSD](00_必读/18_SSD.md) | 多尺度特征图单阶段检测 |
| [19 RetinaNet](00_必读/19_RetinaNet.md) ⭐ | Focal Loss 解决正负不平衡 |
| [20 YOLO 演进总览](00_必读/20_YOLO演进_v2到v11.md) ⭐ | v8 基线的来龙去脉（下分 5 篇） |
| [21 YOLOv2/v3](00_必读/21_YOLOv2_v3.md) | 锚框 + BatchNorm + 三尺度金字塔 |
| [22 YOLOv4/v5](00_必读/22_YOLOv4_v5.md) | CSP 骨干 + PAN 颈部 + Mosaic |
| [23 YOLOv6/v7](00_必读/23_YOLOv6_v7.md) | 重参数化 / E-ELAN |
| [24 YOLOv8](00_必读/24_YOLOv8.md) ⭐ | **本项目基线**：anchor-free+解耦头+C2f+DFL |
| [25 YOLOv9/v10/v11](00_必读/25_YOLOv9_v10_v11.md) | PGI / 去 NMS / C3k2（v11 参考） |
| [26 FCOS](00_必读/26_FCOS.md) | 每像素回归 + centerness，v8 解耦头前身 |
| [27 CenterNet](00_必读/27_CenterNet.md) | 关键点热力图，无锚框中心点检测 |
| [28 CornerNet](00_必读/28_CornerNet.md) | 角点配对，无锚框先驱 |
| [29 Deformable DETR](00_必读/29_DeformableDETR.md) | 稀疏采样注意力，收敛快、多尺度小目标 |

**Transformer → CLIP 线**
| 文件 | 一句话 |
|------|--------|
| [30 注意力机制](00_必读/30_注意力机制.md) | "聚焦"思想的数学化 |
| [31 Transformer](00_必读/31_Transformer.md) ⭐ | 自注意力架构，一切的底座 |
| [32 DETR](00_必读/32_DETR.md) | Transformer 集合预测、无 NMS |
| [33 BERT](00_必读/33_BERT.md) | 双向预训练，NLP 迁移范式 |
| [34 GPT 系列](00_必读/34_GPT系列.md) | 自回归生成与涌现能力 |
| [35 ViT](00_必读/35_ViT.md) ⭐ | 图像切块进 Transformer |
| [36 Swin Transformer](00_必读/36_Swin_Transformer.md) ⭐ | 窗口注意力 + 层级金字塔 |
| [37 CLIP](00_必读/37_CLIP.md) ⭐ | **本项目核心**，图文对比学习零样本 |
| [38 Grounding DINO](00_必读/38_GroundingDINO.md) | 开放词汇检测，相关工作对比 |

**辅助**
| 文件 | 一句话 |
|------|--------|
| [39 扩散模型 DDPM→SD→ControlNet](00_必读/39_扩散模型_DDPM与ControlNet.md) ⭐ | 数据增强引擎，结构可控生成 |
| [40 PatchCore](00_必读/40_PatchCore.md) ⭐ | 特征记忆库+最近邻判异常，OOD 打分依据 |

---

## 01_基础与其他骨干（14 篇）

| 文件 | 一句话 |
|------|--------|
| [01 Seq2Seq](01_基础与其他骨干/01_Seq2Seq.md) | 两个 LSTM 压缩+展开，attention/Transformer 前身 |
| [02 Word2Vec](01_基础与其他骨干/02_Word2Vec.md) | 词嵌入开山，自监督学线性语义结构 |
| [03 LeNet](01_基础与其他骨干/03_LeNet.md) | 第一个成功的卷积网络 |
| [04 AlexNet](01_基础与其他骨干/04_AlexNet.md) | 深度学习元年，ReLU+Dropout+GPU |
| [05 VGGNet](01_基础与其他骨干/05_VGGNet.md) | 3×3 小卷积堆叠的极简哲学 |
| [06 GoogLeNet/Inception](01_基础与其他骨干/06_GoogLeNet_Inception.md) | 并行多尺度 + 1×1 降维 |
| [07 ResNeXt](01_基础与其他骨干/07_ResNeXt.md) | "基数"第三维 + 分组卷积 |
| [08 DenseNet](01_基础与其他骨干/08_DenseNet.md) | 拼接式特征复用 |
| [09 EfficientNet](01_基础与其他骨干/09_EfficientNet.md) | 深度/宽度/分辨率协同缩放 |
| [10 ConvNeXt](01_基础与其他骨干/10_ConvNeXt.md) | 纯卷积追平 Transformer |
| [11 Adam 优化器](01_基础与其他骨干/11_Adam优化器.md) | 一阶矩+二阶矩+偏差修正 |
| [12 Dropout](01_基础与其他骨干/12_Dropout.md) | 训练随机丢弃+推理权重缩放 |
| [13 知识蒸馏](01_基础与其他骨干/13_知识蒸馏.md) | 软标签+温度让小模型学大模型 |
| [14 Non-local Networks](01_基础与其他骨干/14_NonLocal.md) | CNN 里第一个全局自注意力，ViT 前身 |

---

## 02_大模型（9 篇）

| 文件 | 一句话 |
|------|--------|
| [01 Scaling Laws](02_大模型/01_ScalingLaws.md) | 损失-规模幂律，"做大模型"依据 |
| [02 LoRA](02_大模型/02_LoRA.md) ⭐ | 冻结原权重+低秩矩阵微调 |
| [03 Chain-of-Thought](02_大模型/03_ChainOfThought.md) | 提示加中间推理步骤，涌现 |
| [04 InstructGPT / RLHF](02_大模型/04_InstructGPT_RLHF.md) | SFT+RM+PPO 对齐训练 |
| [05 FlashAttention](02_大模型/05_FlashAttention.md) | SRAM 分块+在线 softmax，推理加速 |
| [06 RoPE](02_大模型/06_RoPE.md) | 旋转位置编码，LLaMA/Qwen 标配 |
| [07 Mamba](02_大模型/07_Mamba.md) | 状态空间模型，O(N) 长序列 |
| [08 LLaMA 系列](02_大模型/08_LLaMA系列.md) | 开源 LLM/VLM 骨干事实标准 |
| [09 Mistral / Mixtral](02_大模型/09_Mistral.md) | 滑动窗口注意力 + 稀疏 MoE |

---

## 03_视觉语言 VLM（15 篇）

> 脉络地图：[00 多模态脉络地图](03_视觉语言VLM/01_多模态脉络地图.md)（视觉端越来越轻 / 图文融合越来越深 / 与语言模型越来越统一）。

| 文件 | 一句话 |
|------|--------|
| [01 多模态脉络地图](03_视觉语言VLM/01_多模态脉络地图.md) | VLM 主线导航 |
| [02 MAE](03_视觉语言VLM/02_MAE.md) | 自监督预训练 ViT，"BERT for images" |
| [03 MoCo/SimCLR](03_视觉语言VLM/03_MoCo_SimCLR.md) | 对比自监督，CLIP 无监督前身 |
| [04 DINO](03_视觉语言VLM/04_DINO.md) | 自监督 ViT，DINOv2→SAM/GDINO 基础 |
| [05 DeiT](03_视觉语言VLM/05_DeiT.md) | 数据高效 ViT，蒸馏 token |
| [06 区域特征 VLP](03_视觉语言VLM/06_区域特征VLP.md) | 多模态起点：区域特征 + 图文预训练 |
| [07 ViLT](03_视觉语言VLM/07_ViLT.md) | 最精简 VLM，图文单流深度融合 |
| [08 ALBEF](03_视觉语言VLM/08_ALBEF.md) | 先对齐再融合 + 动量蒸馏，BLIP 前身 |
| [09 ALIGN](03_视觉语言VLM/09_ALIGN.md) | 18 亿噪声图文对，规模>过滤 |
| [10 BLIP / BLIP-2](03_视觉语言VLM/10_BLIP系列.md) | Q-Former 桥接视觉与 LLM |
| [11 CoCa](03_视觉语言VLM/11_CoCa.md) | 对比 + 生成合一的图文基础模型 |
| [12 Flamingo](03_视觉语言VLM/12_Flamingo.md) | 冻结视觉+LLM，门控交叉注意力，少样本 |
| [13 SAM](03_视觉语言VLM/13_SAM.md) | 可提示的通用分割基础模型 |
| [14 LLaVA / InternVL](03_视觉语言VLM/14_LLaVA_InternVL.md) | ViT+LLM 图像问答 |
| [15 原生多模态大模型](03_视觉语言VLM/15_原生多模态大模型.md) | 图像也 token 化、图文统一自回归 |

---

## 04_图像分割（8 篇）

> 脉络地图：[00 分割脉络地图](04_图像分割/01_分割脉络地图.md)。正式学分割按 FCN → U-Net 顺序。

| 文件 | 一句话 |
|------|--------|
| [01 分割脉络地图](04_图像分割/01_分割脉络地图.md) | 分割主线导航 |
| [02 U-Net](04_图像分割/02_U-Net.md) | 编解码 + 跳跃连接，分割经典/扩散骨干 |
| [03 HRNet](04_图像分割/03_HRNet.md) | 多分辨率并行，全程保持高分辨率 |
| [04 FCN](04_图像分割/04_FCN.md) | 语义分割开山，逐像素稠密预测 |
| [05 DeepLab 系列](04_图像分割/05_DeepLab系列.md) | 空洞卷积 + ASPP 多尺度 |
| [06 Mask R-CNN](04_图像分割/06_Mask_RCNN.md) | 实例分割：检测 + mask 分支 |
| [07 SegFormer](04_图像分割/07_SegFormer.md) | 分层 Transformer + 全 MLP 轻解码器 |
| [08 MaskFormer/Mask2Former](04_图像分割/08_MaskFormer_Mask2Former.md) | mask 分类统一语义/实例/全景 |

---

## 05_生成模型（11 篇）

> 脉络地图：[00 生成模型脉络地图](05_生成模型/01_生成模型脉络地图.md)。

| 文件 | 一句话 |
|------|--------|
| [01 生成模型脉络地图](05_生成模型/01_生成模型脉络地图.md) | 生成主线导航 |
| [02 VQVAE/VQGAN](05_生成模型/02_VQVAE_VQGAN.md) | codebook + 直通梯度，图像 token 化 |
| [03 StyleGAN](05_生成模型/03_StyleGAN.md) | 映射网络+AdaIN，GAN 质量顶峰 |
| [04 Flow Matching](05_生成模型/04_Flow_Matching.md) | 噪声→图像直线 ODE，SD3/FLUX 核心 |
| [05 VAE / GAN](05_生成模型/05_VAE_GAN.md) | 扩散前两大生成前身 |
| [06 DDPM 与 DDIM](05_生成模型/06_DDPM与DDIM.md) | 去噪扩散；DDIM 少步加速 |
| [07 Latent/Stable Diffusion](05_生成模型/07_Latent_Stable_Diffusion.md) | 潜空间扩散 + 文本条件 + CFG |
| [08 DALL-E 2](05_生成模型/08_DALL-E2.md) | CLIP 先验 + 级联 DDPM 解码器 |
| [09 DiT](05_生成模型/09_DiT.md) | 去噪骨干 U-Net → Transformer |
| [10 一致性模型与加速](05_生成模型/10_一致性模型与加速.md) | 一致性 + LCM，1~4 步实时出图 |
| [11 Sora](05_生成模型/11_Sora.md) | 时空 Patch + DiT，分钟级视频生成 |

---

## 与本项目的技术栈映射

```
本项目模块                直接来源
─────────────            ───────────────
CNN 卷积原理（总纲）  ←   CNN 原理
YOLOv8 骨干+颈部     ←   ResNet + FPN + YOLO 演进 + CSP
轻量骨干（边缘部署） ←   MobileNet（深度可分离卷积）
P2 浅层特征融合       ←   FPN 多尺度思想
正负不平衡/Focal Loss ←  RetinaNet
CBAM 注意力           ←   SE-Net → CBAM
CLIP 零样本识别       ←   Transformer → ViT → CLIP
OOD 已知类相似度打分  ←   CLIP（当前实现）｜PatchCore（距离异常检测背景）
开放词汇检测对比      ←   Grounding DINO
稀缺类数据增强        ←   扩散模型（ControlNet 可控合成）
```
