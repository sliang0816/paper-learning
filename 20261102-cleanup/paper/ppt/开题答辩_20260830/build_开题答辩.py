#!/usr/bin/env python3
"""江苏大学开题答辩 PPT：18 页主讲 + 7 页备查。"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
SKILL = PROJECT / ".agents/skills/slide-maker/scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(ROOT))

import deckkit as dk
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from style import *

TEMPLATE = ROOT / "assets/template/江苏大学开题模板_v7.pptx"
OUT = ROOT / "朱守亮-开题答辩v8-开题版.pptx"

dk.FONT = FONT_EN
dk.DISPLAY = FONT_EN
dk.MONO = "DejaVu Sans Mono"
dk.EAFONT = FONT_CN
dk.EADISPLAY = FONT_CN
dk.EQ_MATHFONT = "STIXGeneral"

# Semantic icon provenance for the Codex visual contract. The raster assets in
# assets/icons were generated from this single Lucide outline family.
ICON_BUILD_TOKENS = [
    "lucide:search", "lucide:route", "lucide:chart-no-axes-column-increasing",
    "lucide:calendar-days", "lucide:database", "lucide:video", "lucide:cpu",
]

_MIXED_PUNCT = re.compile(r"([A-Za-z0-9%+\)\]])([。，、；：！？）》」』】])")
_ASCII_PUNCT = {
    "。": ".", "，": ",", "、": ",", "；": ";", "：": ":",
    "！": "!", "？": "?", "）": ")", "》": ">", "」": '"',
    "』": '"', "】": "]",
}


def normalize_mixed_punctuation(prs):
    """Avoid PowerPoint's uncontrollable gap before full-width punctuation."""
    def fix_text_frame(tf):
        for paragraph in tf.paragraphs:
            for run in paragraph.runs:
                run.text = _MIXED_PUNCT.sub(
                    lambda m: m.group(1) + _ASCII_PUNCT[m.group(2)], run.text
                )

    def visit(shape):
        if getattr(shape, "has_text_frame", False):
            fix_text_frame(shape.text_frame)
        if getattr(shape, "has_table", False):
            for row in shape.table.rows:
                for cell in row.cells:
                    fix_text_frame(cell.text_frame)
        if hasattr(shape, "shapes"):
            for child in shape.shapes:
                visit(child)

    for slide in prs.slides:
        for shape in slide.shapes:
            visit(shape)


def set_shape_font(shape, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    tf = shape.text_frame
    tf.word_wrap = True
    for p in tf.paragraphs:
        p.alignment = align
        for r in p.runs:
            dk.set_font(r, size, color, bold=bold, font=FONT_EN, ea=FONT_CN)


def new_content(prs, title, page, pale=False):
    s = prs.slides.add_slide(prs.slide_layouts[0])
    for ph in list(s.placeholders):
        idx = ph.placeholder_format.idx
        if idx not in {0, 12}:
            ph._element.getparent().remove(ph._element)
    title_shape = s.shapes.title
    title_shape.left = Inches(0.65)
    title_shape.top = Inches(0.22)
    title_shape.width = Inches(11.75)
    title_shape.height = Inches(0.66)
    title_shape.text = title
    set_shape_font(title_shape, 24, INK, True)
    for ph in s.placeholders:
        if ph.placeholder_format.idx == 12:
            ph.text = f"{page:02d}"
            set_shape_font(ph, 9, WHITE, True, PP_ALIGN.RIGHT)
    if pale:
        # Content-stage tint only; template chrome remains visible.
        dk.box(s, 0.34, 1.02, 12.65, 5.84, fill=BLUSH, line=BLUSH_2, line_w=0.8, round=True, r=0.09)
    if page >= 19:
        tx(s, 11.18, 1.08, 1.28, 0.20, f"备查 {page-18}/7", 11,
           EVID_BLUE, True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    return s


def tx(s, x, y, w, h, content, size=BODY, color=INK, bold=False,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=None):
    shp = dk.text(s, x, y, w, h, [[(content, size, color, bold, False, font or FONT_EN)]],
                  align=align, anchor=anchor, space_after=0)
    return shp


def label_box(s, x, y, w, h, label, *, fill=WHITE, color=INK, line=GRID,
              size=BODY, bold=False, r=0.10, align=PP_ALIGN.CENTER):
    shp = dk.box(s, x, y, w, h, fill=fill, line=line, line_w=0.8, round=True, r=r)
    # Nudge centred labels slightly upward. LibreOffice's CJK metrics sit lower
    # than PowerPoint's, so exact geometric centring can make the glyph ink look
    # cramped against the lower edge in the rendered deck.
    tx(s, x + 0.10, y + 0.04, w - 0.20, max(0.12, h - 0.16),
       label, size, color, bold, align, MSO_ANCHOR.MIDDLE)
    return shp


def dot(s, cx, cy, r, fill, line=None):
    shp = dk._flat(s.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(cx-r), Inches(cy-r), Inches(2*r), Inches(2*r)
    ))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line; shp.line.width = Pt(1)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    dk.overlap_intent(shp, "node marker intentionally sits on its connecting evidence rail")
    return shp


def source_note(s, text):
    tx(s, 0.72, 6.82, 11.75, 0.20, text, CAPTION, SLATE)


def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[2])


def rule(s, x, y, w, color=GRID, h=0.025):
    return dk.box(s, x, y, w, h, fill=color, line=color)


def note_chip(s, x, y, w, text_value, color=SLATE, fill=LIGHT, size=14):
    return label_box(s, x, y, w, 0.42, text_value, fill=fill, color=color,
                     line=fill, size=size, bold=True)


def metric_card(s, x, y, w, h, value, label, *, fill=WHITE, color=INK,
                line=GRID, value_size=27):
    dk.box(s, x, y, w, h, fill=fill, line=line, line_w=0.9, round=True, r=0.10)
    tx(s, x + 0.16, y + 0.14, w - 0.32, 0.44, value, value_size, color, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    tx(s, x + 0.16, y + h - 0.43, w - 0.32, 0.27, label, 13.5, color,
       False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def slide_01(prs):
    """role=cover | form=campus image band + title field | static"""
    s = blank_slide(prs)
    dk.picture(s, str(ROOT / "assets/template/campus_banner.jpg"), 0, 0, W, 2.72,
               fit="cover", alt="江苏大学校园横幅")
    dk.box(s, 0, 0, W, 0.18, fill=JU_RED, line=JU_RED)
    dk.box(s, 0, 2.72, W, 4.44, fill=WHITE, line=WHITE)
    dk.box(s, 0.76, 3.14, 0.08, 1.26, fill=JU_RED, line=JU_RED)
    tx(s, 1.08, 3.05, 11.35, 1.45,
       "融合视觉语言模型的路面抛洒物\n检测与异常识别方法研究",
       31, INK, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    tx(s, 1.10, 4.70, 5.7, 0.38, "硕士学位论文开题答辩", 19, JU_RED, True)
    dk.picture(s, str(ROOT / "assets/template/jiangsu_university_logo.png"), 8.62, 4.58,
               3.72, 1.12, fit="contain", alt="江苏大学标志")
    info = "汇报人：朱守亮\n学　院：电气信息工程学院\n专　业：控制工程（非全日制专业硕士）"
    tx(s, 1.10, 5.34, 6.65, 1.02, info, 16.5, SLATE, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    tx(s, 8.50, 5.94, 3.92, 0.34, "开题答辩 · 2026", 15, SLATE, False,
       PP_ALIGN.RIGHT, MSO_ANCHOR.TOP)
    dk.box(s, 0, 7.16, W, 0.34, fill=JU_RED, line=JU_RED)
    tx(s, 0.82, 7.17, 3.5, 0.24, "博 学  ·  求 是  ·  明 德", 10, WHITE, True)
    tx(s, 9.30, 7.17, 3.2, 0.24, "JIANGSU UNIVERSITY", 9.5, WHITE, False, PP_ALIGN.RIGHT)
    dk.design_intent(s, envelope="bleed", reason="bookend cover deliberately carries its own full-width footer chrome")
    dk.speaker_notes(s, "各位老师好，我是朱守亮。本课题关注固定监控场景中的两个难点：小目标容易漏检，预留类别即使被框出，也不一定能正确命名。下面我从问题、路线、前期证据和后续计划四个方面汇报。")
    return s


def slide_02(prs):
    """role=agenda | form=four-stop band | static"""
    s = new_content(prs, "汇报围绕“问题、路线、证据、计划”四个问题展开", 2)
    items = [
        ("选题依据", "为什么值得做", "search.png"),
        ("技术路线", "准备怎么做", "route.png"),
        ("前期证据", "现在知道什么", "chart.png"),
        ("创新与计划", "如何完成闭环", "calendar.png"),
    ]
    xs = [1.05, 4.03, 7.01, 9.99]
    rule(s, 1.25, 3.18, 10.75, JU_RED, 0.04)
    for i, ((title, sub, icon_name), x) in enumerate(zip(items, xs), start=1):
        dot(s, x + 0.72, 3.20, 0.18, JU_RED, WHITE)
        dk.icon(s, str(ROOT / f"assets/icons/{icon_name}"), x + 0.50, 1.68, 0.46,
                alt=title, disc="FCEDEE", disc_pad=0.10)
        tx(s, x - 0.30, 2.30, 2.05, 0.38, title, 20, INK, True, PP_ALIGN.CENTER)
        tx(s, x - 0.35, 3.62, 2.15, 0.38, sub, 15, SLATE, False, PP_ALIGN.CENTER)
    note_chip(s, 3.52, 5.43, 6.30, "不按论文目录复述，只回答评审最关心的四个问题", JU_RED, BLUSH, 16)
    dk.speaker_notes(s, "我不按论文目录逐章复述，而是围绕评审最关心的四个问题展开：为什么值得研究，准备怎么验证，现在已经有哪些可信证据，以及开题后如何补齐闭环。")
    return s


def slide_03(prs):
    """role=hook | form=big number + source chart | static"""
    s = new_content(prs, "固定监控把目标拍进画面，却仍难保留小目标细节", 3)
    tx(s, 0.76, 1.20, 3.15, 1.10, "83.5%", 49, JU_RED, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    tx(s, 3.65, 1.26, 3.18, 0.50, "720 / 862", 28, INK, True)
    tx(s, 3.65, 1.80, 4.30, 0.42, "test 目标属于 small", 18, SLATE, False)
    note_chip(s, 8.70, 1.42, 3.75, "640 letterbox 后的 COCO 面积分层", EVID_BLUE, EVID_BLUE_LIGHT, 14)
    dk.picture(s, str(PROJECT / "paper/figures/fig_ch3_size_distribution.png"), 0.76, 2.50, 11.82, 3.80,
               fit="contain", alt="测试集目标尺寸分布")
    source_note(s, "数据：测试集 862 个目标；small 720，medium 142。")
    dk.speaker_notes(s, "在我们的测试集中，862个目标里有720个属于small，占83.5%。这是640 letterbox后按COCO面积规则统计的尺寸分层，它说明小目标是当前数据的主要矛盾，因此不能只看总体精度。")
    return s


def slide_04(prs):
    """role=related-work gap | form=three-route comparison | static"""
    s = new_content(prs, "已有路线各解决一部分问题，但缺少可归因、可审计的一体化证据", 4)
    routes = [
        (0.72, "小目标检测", "P2 / CBAM", "改善定位细节", "单次提升难排除\n随机性与结构混杂", EVID_BLUE),
        (4.53, "开放词汇检测", "DINO / YOLO-World", "文本驱动定位", "跨域、词表与阈值\n改变结果边界", SUPPORT_TEAL),
        (8.34, "视觉语言识别", "CLIP / 区域匹配", "固定词表命名", "参考能力不等于\n端到端系统能力", JU_RED),
    ]
    for x, name, examples, ability, gap, col in routes:
        dk.box(s, x, 1.48, 3.53, 3.92, fill=WHITE, line=col, line_w=1.1, round=True)
        label_box(s, x+0.22, 1.70, 3.09, 0.58, name, fill=col, color=WHITE, line=col, size=18, bold=True)
        tx(s, x+0.30, 2.54, 2.93, 0.52, examples, 14.5, col, True, PP_ALIGN.CENTER)
        tx(s, x+0.30, 3.15, 2.93, 0.38, ability, 17, INK, True, PP_ALIGN.CENTER)
        tx(s, x+0.30, 3.76, 2.93, 0.84, gap, 15.5, SLATE, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    label_box(s, 1.18, 5.72, 11.00, 0.76,
              "本文缺口：固定头宽 5-seed 归因  +  三级证据诊断  +  外部与部署边界验证",
              fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=17, bold=True)
    source_note(s, "代表工作：CLIP[7]、Grounding DINO[9]、道路开放词汇评测[12]、小目标抛洒物注意力[17]、YOLO-World[39]。")
    dk.speaker_notes(s, "相关工作已经分别提供了三类能力：P2和注意力改善小目标定位，开放词汇检测器可按文本查询目标，CLIP可在给定词表中完成零样本命名。但它们没有自动回答本课题的三个证据问题：结构收益能否排除混杂，级联失败来自哪里，以及结论能否跨域和落到设备。因此本文的差异化定位是建立一条可归因、可审计的证据链，而不是宣称这些模块由本文首创。")
    return s


def slide_05(prs):
    """role=framework | form=two-RQ island + scope boundary | static"""
    s = new_content(prs, "本课题只回答两个可验证问题，并主动限制外推", 5)
    dk.box(s, 1.12, 1.28, 11.10, 4.72, fill=BLUSH, line=JU_RED, line_w=1.2, round=True, r=0.12)
    label_box(s, 1.58, 1.72, 4.64, 2.26, "RQ1\n控制头宽后，P2 收益能否重复？",
              fill=WHITE, color=EVID_BLUE, line=EVID_BLUE, size=21, bold=True)
    label_box(s, 7.10, 1.72, 4.64, 2.26, "RQ2\nCLIP 在分层协议中卡在哪里？",
              fill=WHITE, color=SUPPORT_TEAL, line=SUPPORT_TEAL, size=21, bold=True)
    tx(s, 6.24, 2.35, 0.86, 0.72, "共享\n证据原则", 12.5, JU_RED, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    limits = ["不宣称模块首创", "不宣称任意未知发现", "不宣称已成熟部署"]
    for x, label in zip([1.56, 4.75, 7.94], limits):
        note_chip(s, x, 4.83, 2.83, label, SLATE, LIGHT, 13.5)
    tx(s, 2.22, 6.23, 8.90, 0.40, "研究对象更小，但每一个结论都能被实验检验", 18, JU_RED, True, PP_ALIGN.CENTER)
    dk.speaker_notes(s, "开题的核心不是把系统包装得更大，而是把两个问题定义得足够清楚、能够验证。第一个问题关注P2的结构收益是否可归因；第二个问题关注CLIP在端到端链路中的真实能力边界。")
    return s


def slide_06(prs):
    """role=framework | form=labelled twin evidence rails | static: user opted out |
    takeaway='两条技术主线共享同一原则：先控制变量，再逐层加入真实误差'"""
    s = new_content(prs, "两条技术主线共享同一原则：先控制变量，再逐层加入真实误差", 6, pale=True)
    tx(s, 0.82, 1.28, 11.75, 0.38, "共同原则：每个结论都必须能回到配置、日志、结构化结果与适用边界", 17, SLATE, False, PP_ALIGN.CENTER)
    rails = [
        (2.58, "检测证据线", EVID_BLUE, ["重复隔离", "2×2×5", "尺寸分层", "RAOD"]),
        (4.55, "语义证据线", SUPPORT_TEAL, ["真值框", "检测框", "冻结阈值", "开放词汇"]),
    ]
    xs = [3.18, 5.55, 7.92, 10.29]
    for cy, rail_name, col, nodes in rails:
        label_box(s, 0.70, cy-0.34, 1.52, 0.68, rail_name, fill=col, color=WHITE, line=col, size=18, bold=True)
        dk.box(s, 2.46, cy-0.025, 8.78, 0.05, fill=col)
        for i, (cx, name) in enumerate(zip(xs, nodes), start=1):
            dot(s, cx, cy, 0.11, col, WHITE)
            label_box(s, cx-0.84, cy+0.28, 1.68, 0.68, name, fill=WHITE, color=INK, line=col, size=16.5, bold=(i==2))
        boundary = "检测\n边界" if rail_name == "检测证据线" else "语义\n边界"
        label_box(s, 11.45, cy-0.47, 1.14, 0.94, boundary, fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=15, bold=True)
    label_box(s, 3.35, 6.06, 6.63, 0.50, "统一输出：配置 · 日志 · 结构化结果 · 结论摘要", fill=JU_RED, color=WHITE, line=JU_RED, size=15, bold=True)
    source_note(s, "前期基础：固定头宽2×2×5-seed；CLIP真值框→端到端→冻结校准。")
    dk.speaker_notes(s, "本页给出完整技术路线。上方检测线回答P2的收益是否真实可归因，下方语义线回答CLIP在端到端系统中卡在哪里。两条线共用同一原则：先控制变量，再逐层加入真实误差，并保留配置、日志、结构化结果与结论摘要。")
    return s


def slide_10(prs):
    """role=evidence | form=paired dot board + evidence rail | static: user opted out |
    takeaway='控制头宽后，P2在自建域5/5正向，CBAM没有稳定独立贡献'"""
    s = new_content(prs, "控制头宽后，P2在自建域5/5正向，CBAM没有稳定独立贡献", 10)
    x0, x1 = 1.35, 7.75
    axis_min, axis_max = 40.0, 47.0
    def sx(v): return x0 + (v-axis_min)/(axis_max-axis_min)*(x1-x0)
    tx(s, 0.65, 1.15, 7.5, 0.32, "同 seed 配对的 test mAP@0.5（%）", 16, SLATE, True)
    # shared value axis
    dk.box(s, x0, 5.78, x1-x0, 0.025, fill=GRID)
    for tick in range(40, 48):
        xx = sx(tick)
        dk.box(s, xx, 5.72, 0.018, 0.12, fill=GRID)
        tx(s, xx-0.18, 5.86, 0.36, 0.23, str(tick), 11, MUTE, False, PP_ALIGN.CENTER)
    baseline = [42.75, 41.00, 40.64, 42.20, 41.55]
    p2 = [45.00, 43.28, 46.21, 43.49, 43.69]
    row_top, row_bottom = 1.85, 4.73
    row_pitch = (row_bottom - row_top) / (len(baseline) - 1)
    for i, (a, b) in enumerate(zip(baseline, p2)):
        cy = row_top + i * row_pitch
        tx(s, 0.65, cy-0.16, 0.62, 0.30, f"seed {i}", 14.5, SLATE, True, PP_ALIGN.RIGHT)
        dk.box(s, sx(a), cy-0.018, sx(b)-sx(a), 0.036, fill=SUPPORT_TEAL)
        dot(s, sx(a), cy, 0.095, SLATE)
        dot(s, sx(b), cy, 0.115, SUPPORT_TEAL)
    tx(s, 1.42, 6.20, 2.2, 0.28, "● baseline", 14.5, SLATE)
    tx(s, 3.25, 6.20, 2.4, 0.28, "● P2（head=128）", 14.5, SUPPORT_TEAL, True)
    # evidence rail
    label_box(s, 8.45, 1.34, 4.10, 1.18, "+2.71 ± 1.65 pp\n5 / 5 seed 正向", fill=SUPPORT_TEAL, color=WHITE, line=SUPPORT_TEAL, size=22, bold=True)
    label_box(s, 8.45, 2.78, 4.10, 0.93, "small AP@0.5\n+4.01 ± 1.58 pp", fill=SUPPORT_TEAL_LIGHT, color=SUPPORT_TEAL, line=SUPPORT_TEAL, size=18, bold=True)
    label_box(s, 8.45, 3.96, 4.10, 0.93, "CBAM独立效应\n方向不稳定", fill=LIGHT, color=SLATE, line=GRID, size=18, bold=True)
    label_box(s, 8.45, 5.14, 4.10, 0.93, "P2×CBAM 交互\n−1.53 ± 3.12 pp", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=18, bold=True)
    source_note(s, "固定分类头宽128；4配置×5 seeds。n=5，不作强显著性外推。")
    dk.speaker_notes(s, "这张图不只报均值，而是把五个相同随机种子的配对结果画出来。每一条线都从baseline指向P2，并且五条都向右。最稳妥的结论是P2在当前自建域和训练协议下重复获得收益，主要落在small目标；CBAM没有稳定独立收益，交互项也不支持正向协同。")
    return s


def slide_16(prs):
    """role=conclusion | form=three contribution bands + narrow boundary rail | static"""
    s = new_content(prs, "创新不在模块命名，而在可归因实验、分层诊断和边界验证", 16, pale=True)
    tx(s, 0.86, 1.22, 8.40, 0.44, "评审只需带走三件事", 19, JU_RED, True)
    rows = [
        (1.86, "01", "受控归因", "P2  +2.71 pp  ·  5/5 正向", EVID_BLUE, "非模块首创"),
        (3.28, "02", "分层诊断", "59  →  28  →  17", SUPPORT_TEAL, "非任意未知"),
        (4.70, "03", "边界验证", "RAOD · 开放词汇 · 原型测速", JU_RED, "非跨域 / 部署"),
    ]
    for y, num, contribution, evidence, col, boundary in rows:
        dk.box(s, 0.78, y, 8.62, 1.06, fill=WHITE, line=col, line_w=1.2, round=True)
        label_box(s, 1.02, y+0.17, 0.82, 0.72, num, fill=col, color=WHITE, line=col, size=20, bold=True)
        tx(s, 2.12, y+0.19, 2.30, 0.62, contribution, 21, col, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
        tx(s, 4.54, y+0.19, 4.46, 0.62, evidence, 22, INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    dk.box(s, 9.72, 1.22, 2.80, 4.55, fill=LIGHT, line=SLATE, line_w=1.0, round=True)
    tx(s, 9.98, 1.58, 2.28, 0.42, "结论边界", 19, SLATE, True, PP_ALIGN.CENTER)
    boundary_top, boundary_bottom = 2.35, 5.53
    boundary_pitch = (boundary_bottom - boundary_top) / len(rows)
    for idx, (_, _, _, _, _, boundary) in enumerate(rows):
        y = boundary_top + idx * boundary_pitch
        tx(s, 9.98, y, 2.28, 0.48, f"— {boundary}", 16.5, SLATE, True, PP_ALIGN.LEFT)
    label_box(s, 2.10, 6.18, 7.94, 0.54, "可归因  ·  可诊断  ·  可限定", fill=JU_RED, color=WHITE, line=JU_RED, size=19, bold=True)
    dk.speaker_notes(s, "这一页只保留三项可辩护贡献。第一，固定头宽和同种子配对让P2收益可归因，提升2.71个百分点且五次都为正。第二，三级协议把59个真值、28个匹配候选和17个正确命名拆开，失败能够定位。第三，RAOD、开放词汇对照和原型测速主动检验边界。右侧同时限定：不把它们写成模块首创、任意未知发现、普遍跨域提升或成熟部署。")
    return s


def slide_07(prs):
    """role=evidence | form=data-role flow + caution rail | static"""
    s = new_content(prs, "数据清单可核算：4,651 张源图像中排除 330 张预留类图像", 7)
    stages = [
        (0.72, 1.54, 3.36, "八类源数据", "4,651", "3,251 / 700 / 700", EVID_BLUE),
        (4.82, 1.54, 3.70, "排除含 GL/RU", "330", "230 / 50 / 50", CAUTION),
        (9.25, 1.54, 3.36, "六类 YOLO 清单", "4,321", "3,021 / 650 / 650", SUPPORT_TEAL),
    ]
    for i, (x, y, w, name, total, split, col) in enumerate(stages):
        if i < len(stages)-1:
            nx = stages[i+1][0]
            dk.connector(s, (x+w, 2.47), (nx, 2.47), color=JU_RED, width=2.2)
        dk.box(s, x, y, w, 1.86, fill=WHITE, line=col, line_w=1.1, round=True)
        tx(s, x+0.18, y+0.18, w-0.36, 0.34, name, 18, col, True, PP_ALIGN.CENTER)
        tx(s, x+0.18, y+0.61, w-0.36, 0.56, total, 30, INK, True, PP_ALIGN.CENTER)
        tx(s, x+0.18, y+1.25, w-0.36, 0.32, split, 16.5, SLATE, True, PP_ALIGN.CENTER)
    label_box(s, 1.10, 3.82, 11.12, 0.72,
              "330 张被排除图像保留给 CLIP 预留类评估；各划分角色按对应协议冻结",
              fill=EVID_BLUE_LIGHT, color=EVID_BLUE, line=EVID_BLUE, size=17, bold=True)
    label_box(s, 1.10, 4.82, 11.12, 1.12,
              "已控制：dHash ≤ 2 近重复不跨划分\n仍有边界：历史 test 曾参与 prompt 探索；回溯内部确认不是“从未查看”",
              fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=17, bold=True)
    source_note(s, "核算：4,651 − (230+50+50) = 4,321 = 3,021+650+650。")
    dk.speaker_notes(s, "先把数据总数核算清楚。八类源数据共4651张，原始划分是3251、700、700。六类检测训练要排除含GL或RU的图像，分别排除230、50、50张，共330张，因此YOLO清单是4321张，也就是3021、650、650。被排除图像保留给CLIP预留类评估，但历史test曾参与prompt探索，回溯内部确认也不等于从项目开始完全未查看。")
    return s


def slide_08(prs):
    """role=method | form=source architecture figure + callout | static"""
    s = new_content(prs, "P2 增加 160×160 浅层分支，目标是保留小目标空间信息", 8)
    dk.picture(s, str(PROJECT / "paper/figures/fig_p2cbam_architecture.png"), 0.72, 1.22, 11.90, 4.52,
               fit="contain", alt="P2和CBAM检测架构图")
    note_chip(s, 0.72, 5.90, 3.77, "P2：160×160 高分辨率分支", EVID_BLUE, EVID_BLUE_LIGHT, 14)
    note_chip(s, 4.79, 5.90, 3.77, "Detect 分类头宽度 = 128", SUPPORT_TEAL, SUPPORT_TEAL_LIGHT, 14)
    note_chip(s, 8.86, 5.90, 3.77, "CBAM：检测尺度后的对照因子", SLATE, LIGHT, 14)
    source_note(s, "结构来源：论文图3.1；P2与CBAM均不作模块首创宣称。")
    dk.speaker_notes(s, "P2不是新模块，它只是把更浅层的高分辨率特征纳入检测，将最高分辨率检测分支从80×80扩展到160×160。CBAM只作为另一个受控因子。真正需要验证的，是固定头宽后P2是否独立产生收益。")
    return s


def slide_09(prs):
    """role=diagnosis | form=2x2 factor matrix + five-seed rail | static"""
    s = new_content(prs, "原 P2 结果混入头宽 128→64，必须用 2×2×5-seed 重新归因", 9)
    tx(s, 0.72, 1.16, 7.20, 0.36, "固定分类头隐藏宽度 = 128", 17, EVID_BLUE, True)
    # axis labels
    tx(s, 2.35, 1.58, 4.80, 0.34, "P2 因子", 18, INK, True, PP_ALIGN.CENTER)
    tx(s, 0.72, 3.20, 1.18, 0.70, "CBAM\n因子", 18, INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    cols = [(2.02, "无 P2"), (4.75, "有 P2")]
    rows = [(2.12, "无 CBAM"), (3.72, "有 CBAM")]
    for x,label in cols:
        tx(s, x, 1.82, 2.38, 0.30, label, 17, SLATE, True, PP_ALIGN.CENTER)
    for y,label in rows:
        tx(s, 0.78, y+0.36, 1.12, 0.32, label, 16, SLATE, True, PP_ALIGN.RIGHT)
    cells = [
        (2.02,2.20,"baseline",WHITE,SLATE),
        (4.75,2.20,"p2_head128",SUPPORT_TEAL_LIGHT,SUPPORT_TEAL),
        (2.02,3.80,"cbam_only",LIGHT,SLATE),
        (4.75,3.80,"p2_cbam_head128",EVID_BLUE_LIGHT,EVID_BLUE),
    ]
    for x,y,label,fill,col in cells:
        label_box(s, x, y, 2.38, 1.18, label, fill=fill, color=col, line=col, size=17, bold=True)
    label_box(s, 7.85, 1.72, 4.52, 3.98, "5 个独立随机种子\n\nseed 0  ·  1  ·  2  ·  3  ·  4\n\n4 配置 × 5 seeds\n= 20 次训练",
              fill=BLUSH, color=JU_RED_DARK, line=JU_RED, size=20, bold=True)
    note_chip(s, 2.52, 5.86, 8.24, "5-seed 是重复训练和同 seed 配对，不是五折交叉验证", CAUTION, CAUTION_LIGHT, 15)
    source_note(s, "训练实参审计：21/26 组有直接日志，已覆盖的均解析为 AdamW。")
    dk.speaker_notes(s, "原始P2配置中，分类头隐藏宽度从128自动降到64。如果不固定头宽，所谓P2差异同时混入了模型容量变化。因此重跑4种配置乘以5个随机种子，共20次训练，目的是拿掉这个隐藏变量。")
    return s


def slide_11(prs):
    """role=comparison | form=two-metric external boundary board | static"""
    s = new_content(prs, "RAOD 只复现 Precision 提高，没有复现综合定位提升", 11)
    tx(s, 0.78, 1.18, 11.70, 0.34, "官方 test 一次性冻结评估 · 3 个同 seed 配对 · 单类 debris 定位", 16, SLATE, False, PP_ALIGN.CENTER)
    rows = [
        (2.02, "Precision", "84.76%", "86.10%", "+1.34 ± 0.70 pp", SUPPORT_TEAL, "3/3 正向"),
        (4.12, "AP50-95", "52.66%", "50.95%", "−1.70 ± 2.22 pp", CAUTION, "1/3 正向"),
    ]
    for y,label,a,b,delta,col,consistency in rows:
        tx(s, 0.82, y, 1.62, 0.40, label, 20, INK, True, PP_ALIGN.RIGHT)
        dk.box(s, 2.78, y+0.17, 5.92, 0.05, fill=GRID)
        dot(s, 4.00, y+0.19, 0.11, SLATE)
        dot(s, 7.22 if col==SUPPORT_TEAL else 5.72, y+0.19, 0.13, col)
        tx(s, 3.30, y-0.40, 1.42, 0.34, a, 16, SLATE, True, PP_ALIGN.CENTER)
        tx(s, (6.48 if col==SUPPORT_TEAL else 5.05), y+0.40, 1.42, 0.34, b, 16, col, True, PP_ALIGN.CENTER)
        label_box(s, 9.20, y-0.31, 3.22, 0.94, f"{delta}\n{consistency}", fill=(SUPPORT_TEAL_LIGHT if col==SUPPORT_TEAL else CAUTION_LIGHT), color=col, line=col, size=17, bold=True)
    label_box(s, 2.15, 5.74, 9.05, 0.65, "结论：自建域 P2 收益不能直接外推为普遍跨域提升", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=17, bold=True)
    source_note(s, "RAOD：baseline / p2_head128；Precision 与 AP50-95 同时报告。")
    dk.speaker_notes(s, "外部数据没有给出更强的结论，反而划出了边界。P2在RAOD上让Precision平均上升1.34个百分点，但3个seed配对中AP50-95平均下降1.70个百分点。因此我们不宣称P2已经获得稳定跨域提升。")
    return s


def slide_12(prs):
    """role=method | form=source CLIP pipeline + boundary notes | static"""
    s = new_content(prs, "CLIP 只在固定八类词表内命名检测框，不负责发现任意未知类", 12)
    dk.picture(s, str(PROJECT / "paper/figures/fig_clip_pipeline.png"), 0.72, 1.22, 11.88, 4.45,
               fit="contain", alt="检测器到CLIP的分层评估管线")
    note_chip(s, 0.92, 5.82, 4.16, "GL / RU 未参与检测训练｜名称进入固定词表", EVID_BLUE, EVID_BLUE_LIGHT, 13.0)
    note_chip(s, 5.30, 5.82, 3.08, "OOD 代理分数：只作诊断", SLATE, LIGHT, 13.5)
    note_chip(s, 8.60, 5.82, 3.76, "历史 test 数值：仅作探索性证据", CAUTION, CAUTION_LIGHT, 13.5)
    source_note(s, "共享核心：检测框裁剪 → CLIP 图文相似度 → 固定词表命名。")
    dk.speaker_notes(s, "这里的零样本指GL和RU没有参与检测器训练，并不是系统可以自动发现任意未知类。检测器生成候选框，裁剪后由CLIP在固定八类词表内命名。OOD代理分数只用于诊断和阈值组合，不是独立可靠的拒识器。")
    return s


def slide_13(prs):
    """role=framework | form=three-level protocol staircase | static"""
    s = new_content(prs, "三级证据逐层加入检测误差和阈值选择，避免单一指标替代系统分析", 13, pale=True)
    steps = [
        (0.82, 4.58, 3.35, 1.32, "1  真值框参考", "只测 CLIP 语义能力", EVID_BLUE),
        (4.14, 3.42, 3.85, 2.48, "2  端到端级联", "加入候选漏检\n与冗余候选", SUPPORT_TEAL),
        (7.96, 2.22, 4.54, 3.68, "3  验证集冻结校准", "val 选工作点后锁定\n再评估 precision / recall", JU_RED),
    ]
    for x,y,w,h,title,sub,col in steps:
        step_box = dk.box(s, x, y, w, h, fill=WHITE, line=col, line_w=1.2, round=True)
        dk.overlap_intent(step_box, "the three protocol terraces deliberately meet as one staircase")
        tx(s, x+0.18, y+0.18, w-0.36, 0.44, title, 19, col, True, PP_ALIGN.CENTER)
        tx(s, x+0.24, y+0.70, w-0.48, h-0.84, sub, 16, INK, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    note_chip(s, 8.64, 1.49, 3.30, "冻结锁：选择后不再看评估集调参", JU_RED, BLUSH, 13.5)
    note_chip(s, 1.15, 6.18, 4.92, "三层共享同一 CLIP 核心，不是三个模型", SLATE, LIGHT, 13.5)
    note_chip(s, 6.30, 6.18, 5.00, "内部确认 ≠ 从项目开始从未查看的确认集", CAUTION, CAUTION_LIGHT, 13.5)
    dk.speaker_notes(s, "三级证据不是三个模型，而是逐层加入真实误差。第一层用真值框只测语义能力；第二层换成真实检测框，加入候选漏检和冗余；第三层只在val选择工作点并冻结。它不是训练CLIP，也不是概率校准。")
    return s


def slide_14(prs):
    """role=diagnosis | form=two protocol zones | static"""
    s = new_content(prs, "两套协议分别说明：历史 test 的端到端瓶颈，与内部确认的阈值边界", 14)
    label_box(s, 0.74, 1.22, 8.02, 0.48, "历史 test｜conf=0.10｜59 个 GL/RU 真值", fill=EVID_BLUE, color=WHITE, line=EVID_BLUE, size=17, bold=True)
    funnel = [
        (0.82, "59", "预留类真值", EVID_BLUE_LIGHT, EVID_BLUE),
        (3.16, "28", "匹配候选", SUPPORT_TEAL_LIGHT, SUPPORT_TEAL),
        (5.50, "17", "正确命名", BLUSH, JU_RED),
    ]
    for i, (x, value, label, fill, col) in enumerate(funnel):
        if i < len(funnel)-1:
            dk.connector(s, (x+1.82, 2.54), (funnel[i+1][0], 2.54), color=SLATE, width=2)
        label_box(s, x, 1.92, 1.82, 1.24, f"{value}\n{label}", fill=fill, color=col, line=col, size=19, bold=True)
    label_box(s, 7.50, 1.92, 1.26, 1.24, "28.81%\n端到端 recall", fill=JU_RED, color=WHITE, line=JU_RED, size=17, bold=True)
    label_box(s, 9.08, 1.22, 3.48, 0.48, "冗余提议核算", fill=CAUTION, color=WHITE, line=CAUTION, size=17, bold=True)
    label_box(s, 9.08, 1.92, 3.48, 2.15,
              "2,060  全部提议\n973  被命名为 GL/RU\n\n641  未匹配框\n315  语义错误\n17  正确",
              fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=16.5, bold=True, align=PP_ALIGN.LEFT)
    label_box(s, 0.74, 4.42, 11.82, 0.48,
              "回溯内部确认｜230 张｜冻结后一次评估｜非严格独立确认",
              fill=SLATE, color=WHITE, line=SLATE, size=17, bold=True)
    label_box(s, 1.18, 5.16, 4.62, 0.88, "conf-only F1\n39.44%", fill=LIGHT, color=SLATE, line=GRID, size=19, bold=True)
    tx(s, 5.92, 5.31, 1.50, 0.46, ">", 25, CAUTION, True, PP_ALIGN.CENTER)
    label_box(s, 7.38, 5.16, 4.62, 0.88, "joint margin + conf F1\n32.45%", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=19, bold=True)
    source_note(s, "来源：results/实验发现与结论总结_20260811.md；results/confirmation/rejection_confirmation_v1.json。")
    dk.speaker_notes(s, "这页刻意分成两套协议。上半部是历史test、conf等于0.10：59个预留类真值中召回28个匹配候选，其中17个被CLIP正确命名，端到端recall为28.81%。同时，2060个检测提议里有973个被命名为GL或RU，其中641个没有匹配真值，315个是语义错误，只有17个正确。下半部是另一套回溯内部确认：230张图在阈值冻结后评估一次，conf-only F1为39.44%，联合语义margin后为32.45%。两组数字不能当成同一实验链直接比较。来源：results/实验发现与结论总结_20260811.md；results/confirmation/rejection_confirmation_v1.json。")
    return s


def slide_15(prs):
    """role=comparison | form=open-vocab matrix + efficiency hero | static"""
    s = new_content(prs, "直接开放词汇基线未形成有效检测，当前管线也仍有明显成本和类别权衡", 15)
    tx(s, 0.78, 1.18, 7.58, 0.34, "统一 640 输入 · 同 GL/RU 词表 · val 选阈值 · IoU=0.5", 15.5, EVID_BLUE, True)
    rows = [
        ["方法", "回溯内部确认 F1", "只能说明"],
        ["YOLO-World v2s", "0.00%", "当前冻结配置未匹配该域"],
        ["Grounding DINO tiny", "0.80%", "候选多，准确率极低"],
    ]
    dk.table(s, 0.76, 1.72, 7.72, rows, col_w=[2.34,2.08,3.30], size=16,
             row_h=0.70, head_c=EVID_BLUE, body_c=INK, rule_c=GRID, numeric_cols=[1])
    metric_card(s, 8.88, 1.54, 3.72, 2.26, "12.91 FPS", "旧 P2+CBAM seed0 原型",
                fill=SUPPORT_TEAL, color=WHITE, line=SUPPORT_TEAL, value_size=28)
    tx(s, 9.15, 4.08, 3.18, 0.38, "77.41 ms / 图", 21, INK, True, PP_ALIGN.CENTER)
    tx(s, 9.15, 4.52, 3.18, 0.34, "RTX 3090 · 120 W · batch=1", 15, SLATE, False, PP_ALIGN.CENTER)
    label_box(s, 0.78, 4.64, 7.68, 1.18,
              "定向 prompt 并非无代价\nGL/RU 宏平均：52.54% → 37.29%",
              fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=18, bold=True)
    note_chip(s, 8.92, 5.22, 3.66, "非最终推荐配置；只作量级参考", CAUTION, CAUTION_LIGHT, 14.5)
    source_note(s, "来源：results/open_vocab/*/summary.json；results/full_pipeline_benchmark.json。")
    dk.speaker_notes(s, "在统一640输入、同词表、val选阈值和IoU协议下，YOLO-World的内部确认F1为0，Grounding DINO为0.80%。这只说明当前冻结配置没有有效迁移到该场景，不能否定它们的一般能力。12.91 FPS来自旧P2加CBAM seed0、conf等于0.01的原型，并不是最终推荐的p2_head128配置，因此只作计算量级参考，不能外推为边缘部署结论。")
    return s


def slide_17(prs):
    """role=roadmap | form=relative-month milestones + fallback rail | static"""
    s = new_content(prs, "开题后 6 个月按依赖推进：先确认数据，再跨帧，最后上目标设备", 17)
    lanes = [
        (1.38, "database.png", "0–2 月｜独立确认", "输入：从未查看的同域新数据", "验收：冻结清单、一次评估、区间报告"),
        (3.15, "video.png", "2–4 月｜跨帧评估", "依赖：视频 ID 与时间戳", "验收：按视频隔离，帧级 + 事件级指标"),
        (4.92, "cpu.png", "4–6 月｜设备闭环", "依赖：芯片、功率与部署框架", "验收：P50/P95、内存、功耗、精度回归"),
    ]
    for i,(y,icon_name,title,inp,out) in enumerate(lanes):
        col = [EVID_BLUE, SUPPORT_TEAL, JU_RED][i]
        fill = [EVID_BLUE_LIGHT, SUPPORT_TEAL_LIGHT, BLUSH][i]
        dk.box(s, 0.76, y, 8.74, 1.38, fill=fill, line=col, line_w=1.0, round=True)
        dk.icon(s, str(ROOT / f"assets/icons/{icon_name}"), 1.00, y+0.41, 0.48, alt=title)
        tx(s, 1.66, y+0.15, 2.78, 0.44, title, 18, col, True)
        tx(s, 4.55, y+0.12, 4.58, 0.44, inp, 15.5, INK, False)
        tx(s, 4.55, y+0.74, 4.58, 0.46, out, 15.5, SLATE, True)
    dk.box(s, 9.82, 1.38, 2.70, 4.92, fill=CAUTION_LIGHT, line=CAUTION,
           line_w=0.8, round=True, r=0.10)
    tx(s, 10.00, 1.76, 2.34, 0.46, "风险与回退", 18, CAUTION, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    tx(s, 10.00, 2.30, 2.34, 1.52, "数据未到位：\n只报告公开集边界\n\n设备未到位：\n保留 GPU 原型结论", 15.5,
       CAUTION, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    tx(s, 10.00, 4.25, 2.34, 0.46, "共同留存", 17, CAUTION, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    tx(s, 10.00, 4.75, 2.34, 1.10, "配置 · 日志\n结构化结果\n结论摘要", 16,
       CAUTION, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    source_note(s, "未有真实材料前不伪造独立确认、跨帧或设备结果。")
    dk.speaker_notes(s, "计划按依赖分成开题后六个月。前两个月完成真正未查看的同域确认数据和冻结清单；第二到第四个月在拿到视频ID和时间戳后完成按视频隔离的帧级与事件级评估；第四到第六个月在目标芯片和部署框架明确后完成P50、P95、内存、功耗和精度回归。如果材料未到位，就只报告公开数据与GPU原型边界，不伪造同域、跨帧或设备结论。")
    return s


def slide_18(prs):
    """role=closing | form=mirrored campus closer | static"""
    s = blank_slide(prs)
    dk.picture(s, str(ROOT / "assets/template/campus_banner.jpg"), 7.26, 0, 6.07, 7.09,
               fit="cover", alt="江苏大学校园")
    dk.box(s, 0, 0, 0.18, H, fill=JU_RED, line=JU_RED)
    tx(s, 0.92, 1.55, 5.62, 1.22, "感谢各位老师指导", 35, INK, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    rule(s, 0.94, 2.94, 4.72, JU_RED, 0.045)
    tx(s, 0.96, 3.30, 5.24, 0.62, "恳请批评指正", 23, JU_RED, True)
    tx(s, 0.96, 4.04, 5.24, 0.72, "Q & A", 32, EVID_BLUE, True)
    tx(s, 0.96, 5.28, 5.45, 0.84, "希望获得评审对\n研究问题 · 验证协议 · 后续计划的建议", 16, SLATE, False)
    footer_bar = dk.box(s, 0, 7.16, W, 0.34, fill=JU_RED, line=JU_RED)
    dk.overlap_intent(footer_bar, "closing footer intentionally meets the full-height left accent rail")
    tx(s, 0.82, 7.17, 3.5, 0.24, "博 学  ·  求 是  ·  明 德", 10, WHITE, True)
    tx(s, 9.30, 7.17, 3.2, 0.24, "JIANGSU UNIVERSITY", 9.5, WHITE, False, PP_ALIGN.RIGHT)
    dk.design_intent(s, envelope="bleed", reason="mirrored closer deliberately carries its own photo and footer chrome")
    dk.speaker_notes(s, "我的汇报完毕，恳请各位老师对研究问题、验证协议和后续计划提出意见。")
    return s


def slide_19(prs):
    """role=backup | form=three-definition nested protocol | static"""
    s = new_content(prs, "近重复隔离、内部确认与严格独立确认是三个不同概念", 19, pale=True)
    rings = [
        (0.82, 1.32, 11.72, 5.06, BLUSH, JU_RED),
        (2.04, 2.31, 9.28, 3.46, CAUTION_LIGHT, CAUTION),
        (3.36, 3.31, 6.64, 2.05, EVID_BLUE_LIGHT, EVID_BLUE),
    ]
    for x,y,w,h,fill,col in rings:
        ring = dk.box(s, x, y, w, h, fill=fill, line=col, line_w=1.1, round=True)
        dk.overlap_intent(ring, "nested confirmation scopes intentionally contain the inner protocols")
    tx(s, 1.12, 1.54, 11.12, 0.34, "严格独立确认", 18, JU_RED, True, PP_ALIGN.CENTER)
    tx(s, 1.12, 1.90, 11.12, 0.30, "项目开始后从未查看的新采集数据｜待完成", 13.5, JU_RED, False, PP_ALIGN.CENTER)
    tx(s, 2.34, 2.52, 8.68, 0.34, "回溯内部确认", 18, CAUTION, True, PP_ALIGN.CENTER)
    tx(s, 2.34, 2.88, 8.68, 0.30, "后期定义确认角色，不能恢复时间上的独立性", 13.5, CAUTION, False, PP_ALIGN.CENTER)
    tx(s, 3.66, 3.62, 6.04, 0.34, "近重复成组隔离", 18, EVID_BLUE, True, PP_ALIGN.CENTER)
    tx(s, 3.66, 4.50, 6.04, 0.34, "dHash ≤ 2 不跨 train / val / test｜已完成", 13.5, EVID_BLUE, False, PP_ALIGN.CENTER)
    source_note(s, "定义强度：近重复隔离 < 回溯内部确认 < 从未查看的严格独立确认。")
    dk.speaker_notes(s, "这三个概念不能互换。近重复隔离控制相似帧跨划分；内部确认是后期冻结协议后的回溯验证；严格独立确认则必须使用从项目开始从未查看的新采集数据。")
    return s


def slide_20(prs):
    """role=backup | form=native result table + argument audit | static"""
    s = new_content(prs, "5-seed 完整表与训练实参支持复现，但直接日志覆盖为 21/26", 20)
    rows = [
        ["固定头宽配置", "mAP50", "mAP50-95", "参数量"],
        ["baseline", "0.4163 ± .0086", "0.2148 ± .0059", "11.13M"],
        ["cbam_only", "0.4226 ± .0178", "0.2172 ± .0122", "—"],
        ["p2_head128", "0.4433 ± .0125", "0.2438 ± .0079", "11.63M"],
        ["p2_cbam_head128", "0.4344 ± .0151", "0.2362 ± .0137", "—"],
    ]
    dk.table(s, 0.72, 1.36, 8.18, rows, col_w=[2.52,2.10,2.18,1.38], size=13.5,
             row_h=0.64, head_c=EVID_BLUE, body_c=INK, rule_c=GRID,
             highlight=2, numeric_cols=[1,2,3])
    label_box(s, 9.20, 1.36, 3.35, 3.83,
              "日志可直接核验的训练\n\noptimizer  AdamW\nlr  0.001\nmomentum  0.9\ndecay 组  0.0005\n\n覆盖：21 / 26",
              fill=LIGHT, color=SLATE, line=GRID, size=16, bold=True)
    note_chip(s, 1.12, 5.32, 7.42, "seeds 0–4 全部完成；无日志的 5 组不伪造直接证据", CAUTION, CAUTION_LIGHT, 14.5)
    note_chip(s, 9.22, 5.42, 3.30, "n=5，不作强显著性外推", JU_RED, BLUSH, 14)
    source_note(s, "数值来源：head_width_control_summary_5seed 与 training_argument_audit。")
    dk.speaker_notes(s, "四种固定头宽配置的5个seed已全部完成。当前26组相关训练中有21组有直接日志可核验，这些日志都显示optimizer=auto解析为AdamW，lr为0.001，momentum为0.9，权重衰减组为0.0005。其余5组不写成有直接日志证据。")
    return s


def slide_21(prs):
    """role=backup | form=four paired-effect axes | static"""
    s = new_content(prs, "同 seed 配对把 P2、CBAM 和交互项分开，避免只看最好模型", 21)
    effects = [
        (1.52, "P2｜无 CBAM", 2.71, "5/5 正向", SUPPORT_TEAL),
        (2.65, "P2｜有 CBAM", 1.17, "4/5 正向", SUPPORT_TEAL),
        (3.78, "CBAM｜无 P2", 0.64, "方向不稳定", SLATE),
        (4.91, "CBAM｜有 P2", -0.90, "平均为负", CAUTION),
    ]
    x0, scale = 6.45, 0.78
    for y,label,val,desc,col in effects:
        tx(s, 0.76, y, 2.58, 0.36, label, 16, INK, True, PP_ALIGN.RIGHT)
        rule(s, 3.64, y+0.18, 5.75, GRID, 0.035)
        rule(s, x0, y-0.08, 0.025, SLATE, 0.36)
        end = x0 + val*scale
        effect_bar = dk.box(s, min(x0,end), y+0.14, abs(end-x0), 0.08, fill=col, line=col)
        dk.overlap_intent(effect_bar, "effect segment intentionally overlays the shared zero-centred axis")
        dot(s, end, y+0.18, 0.11, col)
        tx(s, 9.70, y-0.03, 1.08, 0.38, f"{val:+.2f} pp", 16, col, True, PP_ALIGN.RIGHT)
        tx(s, 10.92, y-0.03, 1.52, 0.38, desc, 13.5, SLATE, False)
    label_box(s, 2.38, 5.94, 8.58, 0.62, "P2×CBAM 交互：−1.53 ± 3.12 pp  →  不支持正向协同叙事", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=17, bold=True)
    source_note(s, "水平轴单位：test mAP@0.5 配对差值（百分点）；零点为无效应。")
    dk.speaker_notes(s, "同seed配对的目的是减少随机性带来的比较噪声。P2在无CBAM时为5/5正向，有CBAM时平均也为正；CBAM在无P2时方向不稳定，在有P2时平均为负。交互项为负，所以不把P2加CBAM整体包装成协同创新。")
    return s


def slide_22(prs):
    """role=backup | form=RAOD protocol island + metric board | static"""
    s = new_content(prs, "RAOD 按视频 ID 分组并冻结 test，但只验证单类外部定位", 22)
    label_box(s, 0.78, 1.32, 12.00, 1.25,
              "数据协议：视频 ID 成组 → 单类 debris 映射 → baseline / P2 同 seed 训练 → 官方 test 一次性评估",
              fill=EVID_BLUE_LIGHT, color=EVID_BLUE, line=EVID_BLUE, size=17, bold=True)
    metric_card(s, 0.90, 3.02, 2.55, 1.66, "2,910", "图像", fill=WHITE, color=INK, line=GRID, value_size=28)
    metric_card(s, 3.72, 3.02, 2.55, 1.66, "3,868", "目标", fill=WHITE, color=INK, line=GRID, value_size=28)
    metric_card(s, 6.55, 3.02, 2.55, 1.66, "+1.34 pp", "Precision（3/3正向）", fill=SUPPORT_TEAL_LIGHT, color=SUPPORT_TEAL, line=SUPPORT_TEAL, value_size=25)
    metric_card(s, 9.38, 3.02, 2.55, 1.66, "−1.70 pp", "AP50-95（1/3正向）", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, value_size=25)
    label_box(s, 1.55, 5.22, 10.23, 0.78, "可支持：局部 Precision 改善　　不支持：P2 跨域提高综合定位指标", fill=LIGHT, color=SLATE, line=GRID, size=16.5, bold=True)
    source_note(s, "RAOD 仅作单类外部定位边界，不是同域预留类别的语义确认集。")
    dk.speaker_notes(s, "RAOD的视频帧按视频ID成组，避免相邻帧跨划分。三个seed的最佳权重在训练和验证决策完成后，才一次性评估官方test。但它只映射为单类debris定位，不能替代同域GL/RU语义确认。")
    return s


def slide_23(prs):
    """role=backup | form=source tradeoff chart + calibration rail | static"""
    s = new_content(prs, "Prompt、阈值和定向消融共同说明“选择有效”不等于“无代价”", 23)
    dk.picture(s, str(PROJECT / "paper/figures/fig_ch4_conf_tradeoff.png"), 0.72, 1.38, 7.66, 3.36,
               fit="contain", alt="CLIP置信度阈值权衡图")
    note_chip(s, 1.04, 4.84, 2.55, "val 选点：conf = 0.15", EVID_BLUE, EVID_BLUE_LIGHT, 14.5)
    label_box(s, 8.72, 1.36, 3.86, 1.20, "Prompt\nsurveillance_v2\n由 val 选出", fill=EVID_BLUE_LIGHT, color=EVID_BLUE, line=EVID_BLUE, size=17, bold=True)
    label_box(s, 8.72, 2.82, 3.86, 1.20, "冻结校准\nconf-only 39.44%\njoint 32.45%", fill=LIGHT, color=SLATE, line=GRID, size=17, bold=True)
    label_box(s, 8.72, 4.28, 3.86, 1.20, "类别代价\nGL/RU\n52.54% → 37.29%", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=17, bold=True)
    note_chip(s, 1.08, 5.42, 7.08, "B/32 val/test：50.91% / 52.54%；L/14：41.82% / 44.07%", SUPPORT_TEAL, SUPPORT_TEAL_LIGHT, 14.5)
    note_chip(s, 8.74, 5.78, 3.82, "历史 test 泄漏已披露，不写成严格确认", CAUTION, CAUTION_LIGHT, 13.5)
    source_note(s, "来源：results/实验发现与结论总结_20260811.md；results/confirmation/rejection_confirmation_v1.json。")
    dk.speaker_notes(s, "两个CLIP骨干都从同一11组候选prompt中在val选择surveillance_v2。但第三层冻结校准显示，语义margin与检测置信度联合后没有提供稳定额外价值。定向prompt还使GL/RU从52.54%降到37.29%，说明prompt会重新分配类别错误，不是只增不减。")
    return s


def slide_24(prs):
    """role=backup | form=unified protocol band + outcome table | static"""
    s = new_content(prs, "开放词汇比较统一了输入、词表、阈值和 IoU，但没有穷尽域适配", 24)
    stages = [(0.88,"640 输入"),(3.06,"GL/RU 英文词表"),(5.80,"val 选置信度"),(8.78,"IoU = 0.5")]
    for i,(x,label) in enumerate(stages):
        if i < len(stages)-1:
            dk.connector(s, (x+1.72,2.08), (stages[i+1][0],2.08), color=JU_RED, width=2)
        label_box(s, x, 1.66, 1.72 if i!=1 else 2.18, 0.84, label, fill=BLUSH, color=JU_RED_DARK, line=JU_RED, size=14.5, bold=True)
    rows = [
        ["直接开放词汇方法", "val 冻结阈值", "内部确认 F1", "主要现象"],
        ["YOLO-World v2s", "0.001", "0.00%", "20 个预测，0 TP"],
        ["Grounding DINO tiny", "0.300", "0.80%", "候选极多，precision 极低"],
    ]
    dk.table(s, 0.86, 3.08, 11.62, rows, col_w=[3.72,1.72,1.76,4.42], size=14.5,
             row_h=0.72, head_c=EVID_BLUE, body_c=INK, rule_c=GRID, numeric_cols=[1,2])
    label_box(s, 2.16, 5.68, 9.04, 0.66, "结论限于当前模型版本、提示、阈值搜索和本地领域；不否定域适配后的可能性", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=15.5, bold=True)
    source_note(s, "来源：YOLO-World 与 Grounding DINO 的 results/open_vocab/*/summary.json。")
    dk.speaker_notes(s, "比较公平性主要来自四个统一规则：640输入，同一GL/RU英文词表，只在val选置信度，并按IoU=0.5匹配。但这个比较没有穷尽提示设计、微调和域适配，所以结论只限于当前冻结配置。")
    return s


def slide_25(prs):
    """role=backup | form=latency decomposition + future gap rail | static"""
    s = new_content(prs, "测速只代表旧 P2+CBAM seed0 的 RTX 3090 原型，不是最终推荐配置", 25)
    vals = [("JPEG 解码",31.36,EVID_BLUE),("检测",13.94,SUPPORT_TEAL),("裁剪",0.70,SLATE),("CLIP 预处理",8.57,JU_RED),("CLIP 推理",22.62,CAUTION)]
    x, y, total_w = 0.86, 2.02, 7.78
    scale = total_w / sum(v for _,v,_ in vals)
    for label,val,col in vals:
        w = val*scale
        dk.box(s, x, y, w, 1.06, fill=col, line=WHITE, line_w=0.8)
        if w > 0.65:
            # Separate the phase name and value so pixel visibility checks do
            # not mistake the coloured gap between two lines for occlusion.
            display_label = "CLIP\n预处理" if label == "CLIP 预处理" else label
            tx(s, x+0.07, y+0.14, w-0.14, 0.40, display_label, 11.5,
               WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            tx(s, x+0.07, y+0.58, w-0.14, 0.25, f"{val:.2f}", 11.5,
               WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        x += w
    tx(s, 0.86, 1.42, 7.78, 0.38, "主要阶段平均延迟（ms / 图；其余 0.22 ms 未标注）", 16.5, INK, True)
    label_box(s, 0.86, 3.48, 7.78, 1.20, "端到端：77.41 ms / 图  ·  12.91 FPS\n中位 65.16 ms  ·  P95 121.94 ms", fill=LIGHT, color=INK, line=GRID, size=19, bold=True)
    label_box(s, 9.02, 1.42, 3.48, 3.26, "测速配置\n\n旧 P2+CBAM seed0\nconf = 0.01\nRTX 3090 · 120 W\nbatch = 1\n显存 1242 MB", fill=EVID_BLUE_LIGHT, color=EVID_BLUE, line=EVID_BLUE, size=16.5, bold=True)
    label_box(s, 1.28, 5.12, 10.74, 1.08, "仍需的真实输入：新采集独立确认数据 · 视频元数据 · 目标边缘设备\n在这些材料到位前，不宣称跨帧稳定或边缘可部署", fill=CAUTION_LIGHT, color=CAUTION, line=CAUTION, size=15.5, bold=True)
    source_note(s, "测速不含模型加载与预热；为顺序流式 batch=1，不代表离线批处理吞吐。")
    dk.speaker_notes(s, "平均延迟为77.41毫秒，其中图像解码和CLIP编码是主要额外开销。该测速来自旧P2加CBAM seed0、conf等于0.01的原型，而当前检测主结论支持的是固定头宽p2_head128，因此数字只作量级参考。它也只代表RTX3090、120W限功率和batch等于1的顺序流式环境，不是边缘设备结论。")
    return s


SLIDES = [
    slide_01, slide_02, slide_03, slide_04, slide_05,
    slide_06, slide_07, slide_08, slide_09, slide_10,
    slide_11, slide_12, slide_13, slide_14, slide_15,
    slide_16, slide_17, slide_18, slide_19, slide_20,
    slide_21, slide_22, slide_23, slide_24, slide_25,
]


def main():
    prs = dk.open_template(TEMPLATE)
    for fn in SLIDES:
        fn(prs)
    normalize_mixed_punctuation(prs)
    dk.declare_delivery(OUT, "presented", builds="static")
    dk.lint_layout(prs, strict=True)
    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
