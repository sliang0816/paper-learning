"""Slides 25--33: references, close, and Q&A backup material."""
from __future__ import annotations

from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

import deckkit as dk

from style import (
    BODY_INK,
    BOUNDARY,
    BOUNDARY_LIGHT,
    DETECT,
    FONT_CN,
    FONT_DISPLAY,
    FONT_EN,
    GRID,
    INK,
    JU_BRIGHT,
    JU_RED,
    LIGHT,
    MUTE,
    SUPPORT,
    SUPPORT_LIGHT,
    WHITE,
    add_blank,
    add_content,
    add_section,
    arrow,
    asset,
    note,
    picture,
    rect,
    rule,
    source,
    takeaway,
    tx,
    tx_lines,
)


def _reference_column(slide, x: float, y: float, w: float, entries: list[str]) -> None:
    """Place a compact, open reference column without a card container."""
    for idx, entry in enumerate(entries):
        cy = y + idx * 0.82
        tx(slide, x, cy, 0.48, 0.30, f"{idx + 1:02d}", 13, JU_RED, True,
           PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_EN)
        tx(slide, x + 0.52, cy, w - 0.52, 0.60, entry, 12.5, BODY_INK, False,
           PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_EN)
        # Deliberately omit per-entry rules: long bibliographic lines may wrap,
        # and open whitespace is closer to the supplied reference deck.


def _metric_block(slide, x: float, y: float, w: float, label_text: str,
                  value: str, detail: str, color) -> None:
    """Open metric composition: rule + numeral + qualifier, never a card."""
    rule(slide, x, y, w, color, 0.035)
    tx(slide, x, y + 0.15, w, 0.26, label_text, 13, MUTE, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_CN)
    tx(slide, x, y + 0.42, w, 0.70, value, 31, color, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_DISPLAY)
    tx(slide, x, y + 1.12, w, 0.42, detail, 14, BODY_INK, False,
       PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_CN)


def build(prs, project: Path, root: Path) -> None:
    # 25 — divider 07
    slide = add_section(
        prs,
        "07",
        "参考文献",
        "核心依据与研究位置",
        25,
    )
    note(slide, "最后列出与本课题直接相关的核心文献。正文和后续论文仍保留完整参考文献表，答辩页只呈现支撑研究问题、技术路线与实验协议的代表性工作。")

    # 26 — concise reference list
    slide = add_content(prs, "参考文献", 26)
    left_refs = [
        "XU Y, HU H, ZHU X, et al. RAOD: Road abandoned-object benchmark. IEEE Access, 2024.（外部边界）",
        "RADFORD A, KIM J W, HALLACY C, et al. CLIP. ICML, 2021.（固定词表语义）",
        "LIN T Y, DOLLÁR P, GIRSHICK R, et al. Feature Pyramid Networks. CVPR, 2017.（多尺度基础）",
        "WOO S, PARK J, LEE J Y, et al. CBAM. ECCV, 2018. 注意力因子",
        "CHENG T, SONG L, GE Y, et al. YOLO-World. CVPR, 2024.（开放词汇对照）",
        "LIU S, ZENG Z, REN T, et al. Grounding DINO. ECCV, 2024.（开放词汇对照）",
    ]
    right_refs = [
        "WU X, WANG J, ZHANG S, et al. Small Target Spillage Detection. Springer, 2025.（近邻任务）",
        "李旭, 宋焕生, 史勤, 等. CIEFRNet：高速公路抛洒物检测. 计算机工程与应用, 2024.（近邻任务）",
        "ZHU H, LIU Z, SUN Z, et al. Beyond Pixel Uncertainty. ICCV, 2025.（道路开放集）",
        "MA W, ZHANG X, YAO Q, et al. AA-CLIP. CVPR, 2025. 异常语义",
        "REDMON J, DIVVALA S, GIRSHICK R, et al. YOLO. CVPR, 2016.（检测基线）",
        "LIN T Y, MAIRE M, BELONGIE S, et al. Microsoft COCO. ECCV, 2014.（评估规范）",
    ]
    _reference_column(slide, 0.78, 1.20, 5.77, left_refs)
    _reference_column(slide, 6.79, 1.20, 5.77, right_refs)
    tx(slide, 0.80, 6.12, 11.76, 0.32,
       "注：此处为答辩核心文献节选，完整 51 条文献及格式见论文参考文献表。",
       14, JU_RED, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    source(slide, "来源：paper/drafts/references.md；此页保留 12 条核心依据，完整 51 条见论文参考文献表。")
    note(slide, "本页只列十二条核心参考文献，分别覆盖道路遗留物数据、YOLO与特征金字塔、CBAM、CLIP以及直接开放词汇检测。完整五十一条文献仍以论文参考文献表为准，这里不额外新增或改写无法核验的来源。")

    # 27 — thanks, using the supplied Jiangsu University campus banner
    slide = add_blank(prs)
    campus = asset(project, "paper/ppt/开题答辩_20260830/assets/template/campus_banner.jpg")
    logo = asset(project, "paper/ppt/开题答辩_20260830/assets/template/jiangsu_university_logo.png")
    picture(slide, campus, 0.00, 3.15, 13.333, 4.35,
            "江苏大学校园建筑横幅，用于答辩致谢页", fit="cover")
    curve = dk._flat(slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(-1.05), Inches(1.42), Inches(15.45), Inches(3.00)
    ))
    curve.fill.solid(); curve.fill.fore_color.rgb = WHITE
    curve.line.fill.background()
    dk.bleed_intent(curve, "白色椭圆越出画布以形成参考模板的校园照片曲线切口")
    picture(slide, logo, 0.72, 0.26, 3.16, 0.72,
            "江苏大学官方校名与校徽", fit="contain")
    rule(slide, 0.75, 1.17, 2.25, JU_RED, 0.045)
    tx(slide, 0.78, 1.48, 5.50, 0.82, "谢谢！", 42, INK, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    tx(slide, 0.80, 2.31, 6.40, 0.52, "恳请各位老师批评指正", 24, JU_RED, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    tx(slide, 10.50, 7.15, 1.98, 0.18, "27", 9, WHITE, True,
       PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, FONT_EN)
    dk.design_intent(slide, weight="left", reason="结束页以左侧短句和下部校园横幅完成与封面的书挡呼应。")
    note(slide, "我的汇报到这里结束。当前材料已经能够支撑开题阶段对研究问题、方法路线、已有基础和后续计划的说明，恳请各位老师对研究边界、实验设计和后续验证重点提出意见。")

    # 28 — backup: internal repetition is not independent confirmation
    slide = add_content(prs, "内部重复种子不等于独立确认", 28)
    dk.design_intent(slide, role="appendix", reason="从本页开始为答辩问答时按需调用的备查材料。")
    tx(slide, 0.86, 1.22, 4.78, 0.42, "当前已有", 22, SUPPORT, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    tx_lines(slide, 0.88, 1.84, 4.70, 2.62, [
        "固定头宽的 2×2×5-seed 控制实验",
        "同 seed 配对与尺寸分层评估",
        "RAOD 冻结 test 的 3-seed 外部定位",
        "回溯内部确认与开放词汇冻结对照",
    ], 17, BODY_INK, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_CN, 1.12, 10)
    rule(slide, 6.16, 1.18, 0.028, JU_RED, 4.38)
    tx(slide, 5.57, 2.61, 1.22, 1.10, "≠", 64, JU_RED, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_DISPLAY)
    tx(slide, 6.76, 1.22, 4.92, 0.42, "仍需补齐", 22, BOUNDARY, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    tx_lines(slide, 6.78, 1.84, 4.82, 2.62, [
        "从项目开始未查看的同域确认数据",
        "可靠的视频、相机与时间元数据",
        "目标边缘设备确定后的实机测量",
        "更广相机、道路与类别的外部验证",
    ], 17, BODY_INK, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP, FONT_CN, 1.12, 10)
    takeaway(slide, "内部复现提高可信度，但不能替代严格独立确认；这正是开题后的优先工作。",
             color=BOUNDARY, y=5.82, fill=BOUNDARY_LIGHT)
    source(slide, "来源：paper/论文与实验思路梳理_20260822.md；paper/drafts/ch6_conclusion.md")
    note(slide, "若老师追问实验是否已经全部完成，就使用这一页回答。现有重复种子、冻结外部测试和内部确认足以证明课题可行并支撑开题，但它们不能替代从项目开始未查看的独立数据，也不能证明跨相机泛化和边缘部署已经完成。")

    # 29 — backup: full controlled result and optimizer-log audit
    slide = add_content(prs, "固定头宽 2×2×5-seed 结果与训练审计", 29)
    tx(slide, 0.80, 1.11, 5.80, 0.34,
       "主对照：分类头隐藏宽度统一为 128｜4 种配置 × 5 seeds = 20 次",
       15, DETECT, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    rows = [
        ["配置", "mAP50", "mAP50-95", "small AP50"],
        ["baseline", "0.4163 ± 0.0086", "0.2148 ± 0.0059", "0.3585 ± 0.0076"],
        ["CBAM", "0.4226 ± 0.0178", "0.2172 ± 0.0122", "0.3580 ± 0.0142"],
        ["P2", "0.4433 ± 0.0125", "0.2438 ± 0.0079", "0.3986 ± 0.0135"],
        ["P2 + CBAM", "0.4344 ± 0.0151", "0.2362 ± 0.0137", "0.3867 ± 0.0158"],
    ]
    dk.table(
        slide, 0.82, 1.62, 11.68, rows,
        col_w=[2.30, 3.10, 3.15, 3.13], header=True, highlight=2,
        numeric_cols=[1, 2, 3], size=14.5, row_h=0.55,
        head_c=INK, body_c=BODY_INK, rule_c=GRID,
        hi_fill=SUPPORT_LIGHT, hi_c=SUPPORT, font=FONT_EN,
    )
    tx(slide, 0.84, 4.70, 2.20, 0.28, "训练实参审计", 15, JU_RED, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    rule(slide, 0.84, 5.06, 11.64, GRID, 0.018)
    _metric_block(slide, 0.84, 5.20, 3.28, "正式训练运行", "26", "纳入统一审计", DETECT)
    _metric_block(slide, 4.47, 5.20, 3.28, "直接日志证据", "21 / 26", "均解析为 AdamW", SUPPORT)
    _metric_block(slide, 8.10, 5.20, 4.38, "缺少优化器日志", "5 / 26", "保持未恢复，不猜测", BOUNDARY)
    source(slide, "来源：results/head_width_control_summary_5seed.md；results/size_stratified_head128_controls_5seed.md；results/training_argument_audit.md")
    note(slide, "本页用于回答完整消融和可复现性问题。固定头宽的二乘二主实验共二十次训练，P2单独配置在三项指标上最高；CBAM没有稳定独立收益。更广的二十六次正式运行中，二十一次可由优化器日志直接恢复，五次缺日志，因此保持未恢复而不反推参数。")

    # 30 — backup: RAOD external positioning
    slide = add_content(prs, "RAOD 外部验证给出边界，而非普遍提升", 30)
    tx(slide, 0.83, 1.08, 11.55, 0.32,
       "官方 test 一次性评估｜3 个配对 seed｜baseline → p2_head128",
       15, DETECT, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    dk.dumbbell_board(
        slide, 0.86, 1.72, 11.20,
        [
            ("Precision", "", 84.76, 86.10, 83.5, 87.0, "%"),
            ("AP50-95", "", 52.66, 50.95, 49.5, 54.0, "%"),
        ],
        row_h=0.92, label_w=1.50, accent=SUPPORT, before_c=MUTE,
        track_c=GRID, ink=INK, mute=MUTE, regress={1},
        label_size=16, sub_size=11, value_size=14, before_size=11,
        font=FONT_EN,
    )
    _metric_block(slide, 0.88, 3.84, 5.42, "Precision 配对效应", "+1.34 ± 0.70 pp", "3 / 3 正向", SUPPORT)
    _metric_block(slide, 6.74, 3.84, 5.42, "AP50-95 配对效应", "−1.70 ± 2.22 pp", "1 / 3 正向", BOUNDARY)
    takeaway(slide, "P2 在 RAOD 上提高了 Precision，但没有复现综合定位指标的提升。",
             color=BOUNDARY, y=5.78, fill=BOUNDARY_LIGHT)
    source(slide, "来源：results/external_validation/raod_test_v1/summary.md", y=6.72)
    note(slide, "如果老师询问跨数据域是否也有效，就展示本页。RAOD三组配对中Precision平均提高一点三四个百分点，但AP50-95平均下降一点七个百分点。因此外部验证的价值是限定结论：当前只能主张自建域中的受控配置效应，不能外推为普遍跨域提升。")

    # 31 — backup: historical-test bottleneck
    slide = add_content(prs, "历史 test 的错误瓶颈：59 → 28 → 17", 31)
    error_fig = asset(project, "paper/figures/fig_error_analysis.png")
    picture(slide, error_fig, 0.72, 1.12, 11.89, 3.70,
            "历史测试集预留类别错误分解、类别召回与CLIP语义混淆图", fit="contain")
    tx(slide, 0.95, 4.92, 2.45, 0.48, "59 个预留类真值", 21, INK, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    arrow(slide, (3.51, 5.16), (4.39, 5.16), JU_RED, 2.0)
    tx(slide, 4.48, 4.92, 2.45, 0.48, "28 个匹配候选", 21, DETECT, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    arrow(slide, (7.05, 5.16), (7.93, 5.16), JU_RED, 2.0)
    tx(slide, 8.03, 4.92, 2.78, 0.48, "17 个正确命名", 21, SUPPORT, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    takeaway(slide, "定位遗漏与语义混淆共同限制端到端结果；该链仅用于历史 test 的条件性诊断。",
             color=BOUNDARY, y=5.76, fill=BOUNDARY_LIGHT)
    source(slide, "来源：paper/drafts/ch4_clip.md；paper/figures/fig_error_analysis.png")
    note(slide, "本页用于解释五十九到二十八再到十七的条件链。五十九个GL和RU真值中，检测器召回二十八个匹配候选，其中十七个被CLIP正确命名。图中还显示RU定位更弱、GL与RU存在语义混淆。历史test曾参与早期探索，因此只用于错误定位，不作严格独立证据。")

    # 32 — backup: frozen open-vocabulary negative baselines
    slide = add_content(prs, "直接开放词汇基线在当前冻结配置下仍很弱", 32)
    tx(slide, 0.82, 1.08, 11.68, 0.34,
       "统一协议：640 输入｜GL/RU 固定英文词表｜val 选阈值 → 回溯内部确认｜IoU = 0.5",
       14.5, DETECT, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    rule(slide, 6.47, 1.65, 0.025, JU_RED, 3.65)
    tx(slide, 1.05, 1.78, 4.95, 0.42, "YOLO-World v2s", 22, INK, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    tx(slide, 1.05, 2.40, 4.95, 0.90, "0%", 54, JU_RED, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_DISPLAY)
    tx(slide, 1.05, 3.35, 4.95, 0.34, "F1", 16, MUTE, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    tx(slide, 1.05, 4.07, 4.95, 0.34, "0 TP / 16 predictions", 17, BODY_INK, False,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    tx(slide, 6.96, 1.78, 4.95, 0.42, "Grounding DINO tiny", 22, INK, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    tx(slide, 6.96, 2.40, 4.95, 0.90, "0.80%", 54, BOUNDARY, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_DISPLAY)
    tx(slide, 6.96, 3.35, 4.95, 0.34, "F1", 16, MUTE, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    tx(slide, 6.96, 4.07, 4.95, 0.34, "2 TP / 236 predictions", 17, BODY_INK, False,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_EN)
    takeaway(slide, "负结果只约束当前词表、阈值与道路监控域，不否定两类模型的一般能力。",
             color=BOUNDARY, y=5.76, fill=BOUNDARY_LIGHT)
    source(slide, "来源：results/open_vocab/yoloworld_v2s_gl_ru_internal_confirm_v1/summary.json；Grounding DINO 对应 summary.json")
    note(slide, "若老师询问为什么不直接采用开放词汇检测器，就展示这一页。在相同六百四十输入、固定词表和冻结阈值下，YOLO-World确认F1为零，Grounding DINO为百分之零点八。结果说明当前配置没有有效迁移到本场景，但不代表模型本身普遍无效，也不构成方案优越性证明。")

    # 33 — backup: prototype throughput and device boundary
    slide = add_content(prs, "RTX 3090 原型速度只说明量级，不代表边缘部署", 33)
    _metric_block(slide, 0.86, 1.28, 4.18, "平均端到端延迟", "77.41 ms/图", "顺序流式，batch = 1", DETECT)
    _metric_block(slide, 0.86, 3.02, 4.18, "整管线吞吐率", "12.91 FPS", "模型加载与预热不计入", SUPPORT)
    _metric_block(slide, 0.86, 4.76, 4.18, "尾部延迟", "P95 121.94 ms", "700 张历史 test 图像", BOUNDARY)
    tx(slide, 5.64, 1.18, 6.65, 0.34, "阶段平均延迟（ms）", 15, INK, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_CN)
    dk.native_chart(
        slide, 5.52, 1.58, 6.70, 3.98,
        ["拒识", "CLIP推理", "CLIP预处理", "候选框裁剪", "检测器", "图像解码"],
        [("平均延迟", [0.10, 22.62, 8.57, 0.70, 13.94, 31.36])],
        kind="bar", palette=[DETECT], font=FONT_CN,
        legend=False, value_fmt='0.0" ms"', zero_base=True,
    )
    rect(slide, 5.54, 5.72, 6.68, 0.72, fill=BOUNDARY_LIGHT, line=BOUNDARY_LIGHT)
    tx(slide, 5.74, 5.77, 6.26, 0.60,
       "RTX 3090｜120 W｜旧 P2+CBAM seed0 原型；目标边缘设备尚未确定",
       14, BOUNDARY, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, FONT_CN)
    source(slide, "来源：results/full_pipeline_benchmark.json")
    note(slide, "本页用于回答实时性和部署问题。旧P2加CBAM seed0原型在RTX 3090、120瓦、顺序batch一条件下平均七十七点四一毫秒每图，约十二点九一帧每秒，P95为一百二十一点九四毫秒。目标边缘设备尚未确定，因此这些数字只作量级参考，不能外推为部署性能。")
