#!/usr/bin/env python3
"""开题答辩PPT v5：基于v4模板，修正所有内容以匹配最新实验结果。

运行: conda run -n vlm-rd-detect python scripts/rebuild_ppt_v5.py
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

PROJECT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT / "paper/ppt/archive/开题答辩旧版本"
SRC = ARCHIVE / "朱守亮-开题答辩v4.pptx"
DST = ARCHIVE / "朱守亮-开题答辩v5.pptx"


def set_text(slide, replacements):
    """Replace text in all shapes and tables of a slide."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    for old, new in replacements:
                        if old in run.text:
                            run.text = run.text.replace(old, new)
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for p in cell.text_frame.paragraphs:
                        full = p.text
                        for old, new in replacements:
                            if old in full:
                                for run in p.runs:
                                    run.text = run.text.replace(old, new)


def clear_add_text(slide, top_text, body_text, body_size=11):
    """Clear all text shapes and add new content."""
    for shape in list(slide.shapes):
        if shape.has_text_frame:
            sp = shape._element
            sp.getparent().remove(sp)

    # Title
    t = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    tf = t.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = top_text
    p.font.size = Pt(22); p.font.bold = True

    # Body
    b = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9), Inches(6.5))
    bf = b.text_frame; bf.word_wrap = True
    p2 = bf.paragraphs[0]; p2.text = body_text
    p2.font.size = Pt(body_size)


def set_notes(slide, text):
    ns = slide.notes_slide
    ns.notes_text_frame.clear()
    ns.notes_text_frame.paragraphs[0].text = text


def main():
    prs = Presentation(str(SRC))

    # === P1: 标题页 ===
    set_text(prs.slides[0], [
        ("基于YOLO和视觉语言模型的抛洒物检测研究",
         "融合视觉语言模型的路面抛洒物检测与异常识别方法研究"),
    ])
    set_notes(prs.slides[0],
        "本研究提出改进小目标检测与CLIP开放类识别的两阶段方法。数据集4,651张/6,108框，18组检测消融。")

    # === P4: 背景页 ===
    set_text(prs.slides[3], [
        ("据公安部交管局统计，路面散落物引发事故约占高速公路总事故量6%，致死致伤率远高于普通事故",
         "路面抛洒物是高速公路行车安全的重要隐患，种类多、形态变化大，固定监控摄像头为自动检测提供了硬件基础"),
        ("抛洒物类别不固定、形态多变，亟需引入开放类检测与零样本语义识别加以解决。",
         "抛洒物类别无法穷举，传统固定类别检测器难以覆盖；需引入视觉语言模型的零样本识别能力处理开放类别。"),
    ])
    set_notes(prs.slides[3], "核心挑战：小目标低对比度检测 + 未知类别开放识别。")

    # === P6: 文献综述 ===
    set_text(prs.slides[5], [
        ("DETR 系列：引入 Transformer，消除冗余结构。",
         "Grounding DINO / YOLO-World：开放词汇检测；小目标固定监控场景适应性待验证。"),
    ])
    set_notes(prs.slides[5], "现有通用检测器在小目标场景不足；路面抛洒物领域专门研究少，缺受控消融和可复现评估。")

    # === P8: 检测方法 ===
    set_text(prs.slides[7], [
        ("对标注数据集进行类别合并：聚焦高危物体（如：轮胎、金属、锥桶）。",
         "8类完整标注，训练6类（PL/ME/ST/VP/TD/OT），预留GL/RU为CLIP零样本评估类。"),
        ("引入数据增强与合成样本策略，缓解样本不足。",
         "近重复隔离(dHash≤2)正式划分：train 3,021/val 650/test 650，确保评估独立性。"),
        ("引入浅层特征融合与注意力机制改进检测头，重点提升小目标检测精度。",
         "引入P2浅层检测层(160×160) + CBAM，通过固定头宽2×2因子设计区分结构效应与头宽混杂。"),
    ])
    set_notes(prs.slides[7], "YOLOv8s基线。GL/RU不参与训练。固定分类头宽度区分P2结构效应与训练框架自动头宽变化。")

    # === P10: CLIP方法（完全重写） ===
    clear_add_text(prs.slides[9], "CLIP零样本识别与评估框架",
"""方法：检测框裁剪 → CLIP ViT-B/32编码 → surveillance_v2文本模板 → 余弦相似度 → top-1命名

评估体系（阈值在val选择，test仅作一次性历史确认）：
1. Prompt Engineering：11组策略val对比，baseline 27.3% → surveillance_v2 50.9%（+23.6pp）
   历史test 52.5%，但曾被早期prompt探索查看，不称为独立确认
2. 端到端级联（P2+CBAM seed0, conf=0.10）：recall 28.8%, P=1.7%, F1=3.3%
3. 联合拒识校准（semantic_margin × detector_conf）：F1 1.68%→10.00%（约6倍改善）
4. 错误分解（5028候选框）：漏检45.8% | 语义误分类18.6% | 正确35.6%
5. Crop padding消融（冻结prompt, val only）：最优0.15=52.73%，仅+1/55框，McNemar p=1.0
6. 管线测速：RTX 3090, 120W, batch=1 → 12.91 FPS（YOLO 13.9ms + CLIP 31.2ms）

关键发现：Prompt engineering翻倍零样本上界；联合校准大幅改善precision但绝对值仍低；
瓶颈分布在检测漏检/语义混淆/虚假候选三维度，不能归于单一原因。""", body_size=10)
    set_notes(prs.slides[9], "CLIP贡献定位为评估框架，非通用ODV。上界→端到端→校准→分解的四级证据链。")

    # === P12: 研究方案总览 ===
    clear_add_text(prs.slides[11], "研究方案",
"""贡献1：面向固定监控小目标的受控结构消融
• 通过固定分类头宽度128的2×2因子设计（4变体×3seed + 6组头宽控制 = 18组训练）
• 区分P2特征层、CBAM注意力及训练框架自动头宽变化的独立效应
• COCO标准尺寸分层（640 letterbox后面积），量化small(<32²) vs medium(32²~96²)

贡献2：detector→CLIP级联的开放类识别与评估框架
• 建立「真值框上界→端到端级联→拒识校准→错误分解」四级评估协议
• 验证集选择prompt和校准阈值，冻结至一次性评估
• 区分漏检(recall侧)、语义混淆和虚假阳性(precision侧)对指标的不同作用
• 六面板定性案例图 + 完整管线测速 + t-SNE特征可视化

不做：
• 未实施的数据合成（Stable Diffusion/ControlNet）→ 不列入
• ONNX/TensorRT → 未来工作""", body_size=12)
    set_notes(prs.slides[11], "两个贡献以可复现评估协议为支撑，不声称模块发明或通用ODV。")

    # === P13: 检测贡献 ===
    set_text(prs.slides[12], [
        ("阶段一：YOLOv8s + 改进小目标检测头（创新点1）", "贡献1：固定头宽受控消融——P2浅层特征的配置效应"),
        ("采用YOLOv8s作为基线框架（CSPDarkNet + PAN-FPN结构）。", "以YOLOv8s为基线（CSPDarkNet + PAN-FPN），4变体×3 seed = 12组 + 6组头宽控制。"),
        ("检测头嵌入注意力机制（CBAM/SE），增强小目标区域激活响应；", "CBAM注意力模块，通过2×2因子设计区分其独立效应。"),
        ("    输出：候选框 + 类别置信度；EXP-004a/004b 消融实验验证改进贡献。",
         "关键发现：原P2配置伴随分类头宽度从128→64的自动变化；固定128后P2独立效应+3.37±1.91pp（3/3 seed正）。"),
    ])
    set_notes(prs.slides[12], "固定头宽P2 3/3 seed为正。CBAM在P2条件下3/3 seed为负(-1.39pp)。不做协同宣称。")

    # === P14: CLIP贡献 ===
    clear_add_text(prs.slides[13], "贡献2：CLIP零样本识别与评估框架",
"""方法：检测候选框 → CLIP ViT-B/32 → surveillance_v2模板 → 余弦相似度 → 分类+OOD分数

评估体系（全部阈值在val选择）：
1. Prompt engineering: 11组策略, baseline 27.3%→best 50.9%(val), +23.6pp
2. 端到端级联: recall 28.8%, P=1.7%, F1=3.3%（P2+CBAM seed0, conf=0.10）
3. 拒识校准: joint(margin+conf) F1 1.68%→10.00%, P 0.86%→8.64%（历史test）
4. 错误分解: 漏检45.8%|语义错误18.6%|正确35.6%
   recall侧→检测漏检限制 | precision侧→虚假候选框限制
5. Crop padding消融（冻结prompt）: 0.15=52.73%，仅+1/55框
6. 管线测速: 12.91 FPS, 77.4ms/图, 峰值显存1242MB

ViT-L/14对比（探索性）: top-1 44.1% < B/32 52.5%
但RU +39.4pp, GL -58.8pp——模型规模不能单独预测性能""", body_size=9)
    set_notes(prs.slides[13], "CLIP定位为评估框架。四级证据链完整。主动披露padding消融效果微弱。")

    # === P15: 替换为尺寸分层结果 ===
    clear_add_text(prs.slides[14], "固定头宽控制实验与尺寸分层",
"""固定分类头宽度128后的2×2因子对照（各3 seed）：

| 效应 | ΔmAP50 | 方向一致性 |
|---|---|---|
| P2效应（无CBAM, p2_head128−baseline） | +3.37±1.91pp | 3/3 正 |
| P2效应（有CBAM, p2_cbam_head128−cbam_only） | +1.04±0.98pp | 3/3 正 |
| CBAM效应（有P2, p2_cbam_head128−p2_head128） | −1.39±0.70pp | 3/3 负 |
| P2×CBAM交互 | −2.33±2.17pp | 负交互 |

尺寸分层（COCO标准, small<32², n=720）：
| 对比 | Small AP50 配对增益 |
|---|---|
| 固定头宽P2 vs baseline | +5.06±0.89pp |
| p2_cbam_head128 vs cbam_only | +2.67±0.39pp |

结论：P2浅层检测对小目标有稳定配置效应(+5.06pp)；
CBAM在P2存在时未带来增益，为如实报告的方法局限性；
不声称协同或创新模块，定位为受控实验下的配置效应发现。""", body_size=11)
    set_notes(prs.slides[14], "固定头宽控制是关键实验。P2 3/3正；CBAM在P2条件下3/3负。不使用协同表述。")

    # === P16: 创新点诚实定位 ===
    clear_add_text(prs.slides[15], "创新点定位与局限性",
"""贡献1：固定头宽控制下P2对小目标检测的受控配置效应
• 18组训练消除头宽混杂，P2独立效应+3.37pp，3/3方向一致
• 交互效应为负，不声称协同。定位为配置效应发现，非模块创新

贡献2：detector→CLIP级联的评估框架与诊断方法
• 四级评估协议（上界/端到端/校准/错误分解）
• 联合拒识校准F1改善6倍（1.68%→10.00%）
• 错误分解分别定位recall/precision瓶颈

诚实局限：
• 仅3个seed，不做显著性检验
• 零样本仅59框（GL 17, RU 42），置信区间宽
• 端到端F1绝对值仍低（10%）；ST类0%
• test曾参与早期prompt探索，所有test数值标为「历史探索性」
• 固定监控单一视角，不外推跨场景泛化""", body_size=10)
    set_notes(prs.slides[15], "创新点诚实地定位。局限主动列出，准备好解释每个局限的整改方向。")

    # === P17: 检测核心结果 ===
    clear_add_text(prs.slides[16], "检测实验核心结果",
"""原始4变体×3seed（未控制头宽，含头宽变化混杂）：

| 变体 | mAP50 | Δ vs baseline | FPS |
|---|---|---|---|
| baseline | 0.4146±0.0113 | — | 154 |
| P2+CBAM | 0.4429±0.0052 | +2.82±0.79pp | 116 |
| P2 only | 0.4314±0.0230 | +1.68±3.02pp | 136 |
| CBAM only | 0.4240±0.0152 | +0.94±1.61pp | 127 |

交互效应：+0.21±4.39pp（≈零，无协同）

分类别AP50（3 seed均值）：
| | PL | ME | ST | VP | TD | OT |
|---|---|---|---|---|---|---|
| baseline | 0.568 | 0.480 | 0.438 | 0.462 | 0.212 | 0.328 |
| P2+CBAM | 0.553 | 0.560 | 0.501 | 0.448 | 0.251 | 0.345 |

注：P2+CBAM标准差最小(0.0052)，但该配置包含头宽变化，
不能归因于CBAM的稳定化机制。正式归因以固定128头宽控制为准。""", body_size=11)
    set_notes(prs.slides[16], "原始结果作为参考。标准差小≠CBAM稳定化。正式结论以固定头宽为准。")

    # === P18: CLIP核心结果 ===
    clear_add_text(prs.slides[17], "CLIP零样本识别核心结果",
"""Prompt Engineering（11策略val对比）：
   val baseline 27.3% → surveillance_v2 50.9%（+23.6pp）
   历史test 52.5%，但曾被探索查看→不称为独立确认

Crop padding消融（冻结prompt, val only）：
   default 0.10=50.91% | best 0.15=52.73%（+1/55框, +1.82pp）
   图像bootstrap CI [0.00, 5.45]pp, McNemar p=1.0 → 边界效果

ViT-L/14探索性对比（沿用B/32所选prompt, 历史test）：
   B/32 top-1 52.5% > L/14 44.1%（-8.4pp）
   但L/14 RU +39.4pp, GL -58.8pp——类别偏好截然不同
   提示prompt-模型适配比规模重要

ST类（沙石）：ViT-B/32全部实验0%；L/14首次7.9%（val）
在当前模型/模板/数据设定的有效范围内如实报告失败""", body_size=10)
    set_notes(prs.slides[17], "Prompt engineering是最强改进。Padding效果微弱。ViT-L/14整体不优但偏好不同。")

    # === P19: 端到端校准 ===
    clear_add_text(prs.slides[18], "端到端校准与错误分解",
"""Conf阈值扫描（P2+CBAM seed0）：
| conf | dets | TP | P | R | F1 |
| 0.01 | 5028 | 21 | 0.86% | 35.6% | 1.68% |
| 0.10 | 2060 | 17 | 1.75% | 28.8% | 3.29% |
| 0.15 | 1677 | 16 | 2.06% | 27.1% | 3.83% (峰值F1) |

联合拒识校准（val选阈值，test冻结）：
| 方法 | test F1 | test P | test R |
| raw | 1.68% | 0.86% | 35.6% |
| joint | 10.00% | 8.64% | 11.9% |
改善方向val/test一致，但绝对值仍低；test属于历史探索性

错误分解（conf=0.01, 5028候选框）：
• 检测漏检27/59(45.8%)——RU 24/42最突出 → recall瓶颈
• CLIP语义误分类11/59(18.6%)——RU→VP(4次)最常见
• 已知类误报346个 + 未匹配框误报2072个 → precision瓶颈
结论：recall、语义正确率和precision受不同错误类型限制，须分别讨论。""", body_size=9)
    set_notes(prs.slides[18], "联合校准改善方向一致但绝对值低。错误分解是论文最实用贡献——精确定位瓶颈。")

    # === P20: 架构 ===
    set_text(prs.slides[19], [
        ("部署模块：ONNX → TensorRT 加速推理", "未来工作：ONNX/TensorRT导出（不在当前范围）"),
    ])
    set_notes(prs.slides[19], "两阶段架构。ONNX/TensorRT作为未来工作。OOD作为辅助诊断非独立模块。")

    # === P21: 技术路线 ===
    set_text(prs.slides[20], [
        (" 浅层融合+注意力机制 → 小目标检测改进（EXP-002）",
         " 固定头宽2×2因子消融 → P2/CBAM效应分离"),
        ("数据采集 → LabelMe标注 → 改进YOLOv8s训练（创新点1，EXP-001/002）",
         "数据采集 → LabelMe标注 → 近重复隔离 → 4变体×3seed基线"),
        ("Prompt Engineering(11组) → 尺寸分层分析 → ViT-L/14对照 → Conf扫描",
         "Prompt Eng(val选择) → 端到端 → 拒识校准(val→test冻结) → 错误分解 → 管线测速"),
    ])
    set_notes(prs.slides[20], "数据→检测消融→CLIP上界→端到端→校准→错误分解。完整闭环。")

    # === P22: 预期成果 ===
    set_text(prs.slides[21], [
        ("实现ONNX/TensorRT推理部署，延迟 < 100ms；申请软件著作权×1；预期发表EI论文×1（SCI为加分项）。",
         "提供可复现实验材料：18组检测消融、CLIP评估框架、错误分解诊断、完整管线测速。学位论文基于完整实验证据链撰写。"),
    ])
    set_notes(prs.slides[21], "成果聚焦论文和实验材料。软著/EI/SCI不列入（需确认学院制度）。")

    # === P24: 时间线 ===
    set_text(prs.slides[23], [
        ("2026.5—2026.8（已完成✅）", "✅ 已完成（2026.5—2026.8）：全部实验 + 论文章节草稿 + PPT"),
        ("2026.9—2026.11（开题答辩）", "进行中（2026.9—11）：文献精读完善、开题答辩、论文修改"),
        ("2026.12—2027.3（送盲审）", "后续（2026.12—2027.3）：论文终稿、送盲审"),
        ("2027.4—2028.4（毕业答辩）", "最终（2027.4—2028.4）：毕业答辩"),
        ("文章+数据集(5-8月✅) → 改进检测+消融(8月✅) → CLIP实验+PromptEng(8月✅) → 论文写作(9-12月) → 送审(2027.3) → 答辩(2028.4)",
         "数据+检测(✅) → CLIP全套(✅) → 论文草稿(✅) → 文献完善+修改(9-11月) → 送审(2027.3) → 答辩(2028.4)"),
    ])
    set_notes(prs.slides[23], "前期实验全部完成。当前进入论文完善和开题准备。已完成项显著，开题信心足。")

    # === P26: 参考文献 ===
    set_text(prs.slides[25], [
        ("[8] Yu F, Chen H, Wang X, et al. BDD100K: A Diverse Driving Video Dataset.",
         "[8] Roth K et al. Towards Total Recall in Industrial Anomaly Detection. CVPR 2022. (PatchCore)"),
        ("[9] Du D, Zhu P, Wen L, et al. VisDrone-DET2019.",
         "[9] Ming Y et al. Delving into OOD Detection with Vision-Language Models. NeurIPS 2022. (MCM)"),
    ])

    # === P3,5,7,9,11,23,25 过渡页：标记压缩（保留但修改为简洁） ===
    for idx, text in [(2, "研究背景"), (4, "相关工作"), (6, "抛洒物检测"),
                       (8, "CLIP开放类识别"), (10, "研究方案"),
                       (22, "项目进度"), (24, "参考文献")]:
        sl = prs.slides[idx]
        for shape in sl.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    for run in p.runs:
                        if run.text.strip().startswith("0") or len(run.text.strip()) <= 3:
                            run.text = ""

    # Save
    prs.save(str(DST))
    print(f"✅ PPT v5 已保存: {DST}")
    print(f"   大小: {DST.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
