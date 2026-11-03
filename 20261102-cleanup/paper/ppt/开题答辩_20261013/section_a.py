"""Slides 1–13 for the v9 opening-proposal defense deck.

This section follows the supplied Jiangsu University Mode-A reference: red/white,
square geometry, restrained rules, and source figures shown as evidence rather than
decoration.  It appends slides to the shared presentation and never saves the deck.
"""
from __future__ import annotations

from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import deckkit as dk
import style


ROAD = RGBColor(0xD9, 0xD9, 0xD9)
ROAD_LIGHT = RGBColor(0xE7, 0xE7, 0xE7)


def _native_shape(slide, kind, x, y, w, h, *, fill, line=None, line_w=0.8):
    shape = dk._flat(slide.shapes.add_shape(
        kind, Inches(x), Inches(y), Inches(w), Inches(h)
    ))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(line_w)
    return shape


def _dot(slide, cx, cy, r=0.08, fill=style.JU_RED, line=None):
    return style.circle(slide, cx, cy, r, fill=fill, line=line)


def _line(slide, p0, p1, *, color=style.GRID, width=1.2, arrow=False,
          style_name="solid"):
    return dk.connector(
        slide, p0, p1, color=color, width=width,
        style=style_name, arrow=arrow,
    )


def _cover(prs, project: Path):
    """role=cover | form=campus banner + white curve | static: user opted out"""
    slide = style.add_blank(prs)
    campus = style.asset(
        project, "paper/ppt/开题答辩_20260830/assets/template/campus_banner.jpg"
    )
    logo = style.asset(
        project,
        "paper/ppt/开题答辩_20260830/assets/template/jiangsu_university_logo.png",
    )

    style.picture(
        slide, campus, 0, 0, style.W, 4.18,
        "江苏大学校园入口横幅", fit="cover",
    )
    style.rect(slide, 0, 0, style.W, 0.12, fill=style.JU_RED,
               line=style.JU_RED, line_w=0)
    # A single native ellipse recreates the reference cover's white wave without
    # gradients, shadows, or a raster mask.
    curve = _native_shape(
        slide, MSO_SHAPE.OVAL, -0.62, 2.92, 14.55, 3.05,
        fill=style.WHITE,
    )
    dk.bleed_intent(curve, "the cover's white curve intentionally continues beyond both trim edges")

    style.picture(slide, logo, 0.72, 0.46, 3.05, 0.92,
                  "江苏大学官方标志", fit="contain")
    style.rule(slide, 0.82, 4.12, 0.10, style.JU_RED, 1.16)
    style.tx(
        slide, 1.16, 3.98, 11.16, 1.30,
        "融合视觉语言模型的路面抛洒物\n检测与异常识别方法研究",
        31, style.INK, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
    )
    style.tx(slide, 1.18, 5.42, 5.40, 0.38, "硕士学位论文开题答辩",
             18, style.JU_RED, True)
    style.tx(slide, 1.18, 5.98, 3.60, 0.36, "汇报人：朱守亮",
             17, style.BODY_INK, False)
    style.tx(slide, 8.46, 5.98, 3.86, 0.36, "江苏大学",
             17, style.BODY_INK, True, PP_ALIGN.RIGHT)
    style.rect(slide, 0, 7.16, style.W, 0.34, fill=style.JU_RED,
               line=style.JU_RED, line_w=0)
    style.tx(slide, 0.82, 7.17, 3.60, 0.22, "博 学  ·  求 是  ·  明 德",
             9.5, style.WHITE, True)
    style.tx(slide, 9.28, 7.17, 3.18, 0.22, "JIANGSU UNIVERSITY",
             9, style.WHITE, False, PP_ALIGN.RIGHT)
    dk.design_intent(
        slide, envelope="bleed", weight="left",
        reason="封面沿用参考模板的校园横幅和白色曲线，标题左倾形成正式开场。",
    )
    style.note(
        slide,
        "各位老师好，我是朱守亮。本课题面向固定监控场景中的路面抛洒物，重点回答两个问题：小目标能否稳定定位，候选区域能否正确命名。本次汇报区分已有开题证据与尚待完成的论文实验。",
    )


def _agenda(prs):
    """role=agenda | form=seven-item numbered index | static: user opted out"""
    slide = style.add_content(prs, "汇报内容", 2)
    items = [
        ("01", "选题依据"),
        ("02", "国内外研究现状"),
        ("03", "研究目标与内容"),
        ("04", "技术路线与研究方案"),
        ("05", "创新点与难点"),
        ("06", "前期基础与计划"),
        ("07", "参考文献"),
    ]
    positions = [
        (0.90, 1.40), (0.90, 2.58), (0.90, 3.76), (0.90, 4.94),
        (6.90, 1.40), (6.90, 2.58), (6.90, 3.76),
    ]
    for (number, label), (x, y) in zip(items, positions):
        style.tx(slide, x, y, 0.92, 0.50, number, 25, style.JU_RED, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.rule(slide, x + 0.98, y + 0.23, 0.54, style.JU_RED, 0.025)
        style.tx(slide, x + 1.70, y, 4.35, 0.50, label, 19, style.INK, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    style.rule(slide, 6.38, 1.30, 0.018, style.GRID, 4.48)
    style.tx(slide, 7.02, 5.25, 4.65, 0.72,
             "从问题出发\n以证据和边界收束",
             18, style.MUTE, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    style.note(
        slide,
        "汇报按七个部分展开。前三部分说明为什么做、现有方法还缺什么，以及本课题准备回答什么。随后给出技术方案、创新与难点、前期基础及计划，最后列出参考文献。",
    )


def _divider(prs, number, title, subtitle, page, notes):
    slide = style.add_section(prs, number, title, subtitle, page)
    style.note(slide, notes)


def _background(prs):
    """role=problem | form=fixed-camera field schematic | static: user opted out"""
    slide = style.add_content(
        prs, "固定监控持续看路，却不会自动“看清”和“叫对”", 4
    )
    # Monitoring geometry: a fixed camera, sight rays, a long road, and one tiny target.
    # Sight rays are laid down first so the camera and road cover their endpoints;
    # this preserves the intended depth without lines crossing block interiors.
    _line(slide, (1.80, 2.02), (5.76, 3.88), color=style.JU_RED, width=1.1)
    _line(slide, (1.80, 2.16), (5.76, 4.56), color=style.JU_RED, width=1.1)
    style.rect(slide, 1.25, 2.02, 0.10, 2.72, fill=style.INK,
               line=style.INK, line_w=0)
    style.rect(slide, 1.04, 1.78, 0.74, 0.46, fill=style.INK,
               line=style.INK, line_w=0)
    _native_shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, 1.62, 1.87, 0.34, 0.28,
                  fill=style.INK)
    style.tx(slide, 0.96, 4.90, 1.38, 0.38, "固定监控", 15, style.INK, True,
             PP_ALIGN.CENTER)
    style.rect(slide, 2.15, 3.46, 5.12, 1.62, fill=ROAD,
               line=ROAD, line_w=0)
    for x in (2.72, 3.86, 5.00, 6.14):
        style.rect(slide, x, 4.20, 0.58, 0.07, fill=style.BODY_INK,
                   line=style.BODY_INK, line_w=0)
    style.rect(slide, 5.90, 4.12, 0.16, 0.08, fill=style.INK,
               line=style.INK, line_w=0)
    _native_shape(slide, MSO_SHAPE.OVAL, 5.98, 4.05, 0.11, 0.12,
                  fill=style.INK)
    style.target_window(slide, 5.70, 3.86, 0.62, 0.52, style.JU_RED, 2.1)
    style.tx(slide, 4.60, 5.34, 2.82, 0.40, "远处目标只占少量像素",
             15, style.JU_RED, True, PP_ALIGN.CENTER)

    steps = [
        ("01", "连续采集", "摄像机位置固定，视野长期稳定"),
        ("02", "尺度损失", "远处抛洒物细节在下采样中丢失"),
        ("03", "语义命名", "即使给出候选框，仍需判断它是什么"),
    ]
    style.rule(slide, 8.40, 1.55, 0.035, style.JU_RED, 4.30)
    for i, (num, head, body) in enumerate(steps):
        y = 1.50 + i * 1.43
        _dot(slide, 8.42, y + 0.30, 0.11, style.JU_RED, style.WHITE)
        style.tx(slide, 8.72, y, 0.62, 0.48, num, 16, style.JU_RED, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.tx(slide, 9.38, y, 2.70, 0.40, head, 19, style.INK, True)
        style.tx(slide, 9.38, y + 0.46, 2.88, 0.58, body, 14.5, style.MUTE,
                 False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    style.takeaway(slide, "固定视角稳定了画面，却把尺度与语义问题串在了同一条链上")
    style.note(
        slide,
        "固定监控能够长时间记录道路，但远处抛洒物在画面中通常只占少量像素，多次下采样后容易遗失。即使检测器给出了候选区域，系统仍需在有限视觉信息下判断具体类别，因此定位与命名是连续的两道瓶颈。",
    )


def _two_bottlenecks(prs, project: Path):
    """role=problem | form=source chart + repeated target window | static"""
    slide = style.add_content(
        prs, "六类检测 test：83.5% 为 small，“找不到”会继续放大“认不对”", 5
    )
    fig = style.asset(project, "paper/figures/fig_ch3_size_distribution.png")
    style.picture(slide, fig, 0.72, 1.25, 7.55, 2.66,
                  "test集目标尺寸分布", fit="contain")
    style.tx(slide, 8.73, 1.30, 3.45, 0.95, "83.5%", 43, style.JU_RED, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
    style.tx(slide, 8.73, 2.22, 3.45, 0.36, "720 / 862 个六类 test GT 框",
             15.5, style.INK, True, PP_ALIGN.CENTER)
    style.tx(slide, 8.73, 2.73, 3.45, 0.70,
             "small 720\nmedium 142  ·  large 0",
             15, style.MUTE, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.rule(slide, 0.90, 4.18, 11.48, style.GRID, 0.02)

    # The same candidate geometry appears twice: first as a localization target,
    # then as the semantic crop. Only the diagnostic question changes.
    for x in (1.24, 7.04):
        style.rect(slide, x + 0.30, 4.64, 1.26, 0.82, fill=ROAD_LIGHT,
                   line=style.GRID, line_w=0.7)
        style.rect(slide, x + 0.82, 5.08, 0.18, 0.08, fill=style.INK,
                   line=style.INK, line_w=0)
        _native_shape(slide, MSO_SHAPE.OVAL, x + 0.94, 5.00, 0.12, 0.14,
                      fill=style.INK)
        style.target_window(slide, x + 0.56, 4.82, 0.82, 0.55,
                            style.JU_RED, 2.1)
    _line(slide, (3.82, 5.05), (6.58, 5.05), color=style.JU_RED,
          width=1.8, arrow=True)
    style.tx(slide, 2.90, 4.49, 2.42, 0.50, "找不到", 27,
             style.DETECT, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 2.96, 5.08, 2.48, 0.72, "小目标细节丢失\n候选框未被提出",
             15, style.MUTE, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 8.70, 4.49, 2.42, 0.50, "认不对", 27,
             style.SEMANTIC, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 8.76, 5.08, 2.48, 0.72, "候选框已存在\n但类别名称判断错误",
             15, style.MUTE, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.source(slide, "数据：六类检测 test 共 862 个框；完整八类 test=921，GL/RU 预留类 59 个另作语义诊断。")
    style.note(
        slide,
        "六类检测 test 共有862个真值框，其中720个属于small，占83.5%，且没有large目标。完整八类 test 有921个框，其中GL/RU预留类59个不计入这项检测尺度统计，另作语义诊断。这说明小目标不是边缘情况，而是当前数据的主要矛盾。",
    )


def _related_work(prs):
    """role=related work | form=three-route capability map | static"""
    slide = style.add_content(
        prs, "三类研究路线各自提供能力，但都只解决了链路的一部分", 7
    )
    routes = [
        ("小目标检测", "P2 / 多尺度特征 / 注意力", "改善空间细节和候选框质量",
         "但结构收益易与头宽、随机种子和交互效应混杂", style.DETECT),
        ("道路异常检测", "异常分数 / 前景掩膜 / 开放集", "发现与常见路面外观不一致区域",
         "但“异常”不自动给出抛洒物的具体语义名称", style.SUPPORT),
        ("视觉语言模型", "CLIP / 区域—文本匹配", "在给定词表内补充区域级语义",
         "但区域命名能力不等于端到端的可靠检测", style.SEMANTIC),
    ]
    xs = [0.72, 4.66, 8.60]
    for x, (name, examples, ability, limit, color) in zip(xs, routes):
        style.rule(slide, x, 1.34, 3.22, color, 0.055)
        style.tx(slide, x, 1.58, 3.22, 0.52, name, 22, color, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
        style.tx(slide, x, 2.18, 3.22, 0.45, examples, 14.5, style.MUTE, True)
        style.tx(slide, x, 2.84, 3.22, 0.34, "已提供", 13, color, True)
        style.tx(slide, x, 3.22, 3.22, 0.84, ability, 16, style.INK, False,
                 PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
        style.rule(slide, x, 4.20, 3.22, style.GRID, 0.018)
        style.tx(slide, x, 4.48, 3.22, 0.34, "仍不足", 13, style.JU_RED, True)
        style.tx(slide, x, 4.86, 3.22, 0.92, limit, 15, style.BODY_INK, False,
                 PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    _line(slide, (2.33, 5.95), (2.33, 6.18), color=style.JU_RED, width=1.5)
    _line(slide, (6.27, 5.95), (6.27, 6.18), color=style.JU_RED, width=1.5)
    _line(slide, (10.21, 5.95), (10.21, 6.18), color=style.JU_RED, width=1.5)
    style.rule(slide, 2.33, 6.16, 7.88, style.JU_RED, 0.025)
    style.tx(slide, 3.25, 6.27, 6.04, 0.36,
             "共同缺口：缺少一条可归因、可分解、可限定的证据链",
             16, style.JU_RED, True, PP_ALIGN.CENTER)
    style.source(slide, "文献范围：小目标检测、道路异常检测、视觉语言模型；完整条目见第26页。")
    style.note(
        slide,
        "相关研究大致分为三条路线。小目标检测强化定位细节，道路异常检测寻找异常区域，视觉语言模型则提供区域与文本的匹配能力。它们都有价值，但不会自动形成可归因的结构结论，也不会自动解释端到端链路中的误差来源。",
    )


def _gap(prs):
    """role=gap | form=two-sided typographic rupture | static"""
    slide = style.add_content(
        prs, "研究缺口不是缺一个模块，而是缺少对收益与失败的证据解释", 8
    )
    style.tx(slide, 0.82, 1.34, 5.24, 0.54, "结构收益", 29, style.DETECT, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 0.82, 1.98, 5.24, 0.70, "缺少受控归因", 33, style.INK, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.rule(slide, 1.30, 2.94, 4.28, style.DETECT, 0.04)
    left_items = ["检测头宽度是否一致", "多个随机种子是否同向", "P2 与 CBAM 是否真有交互"]
    for i, item in enumerate(left_items):
        y = 3.24 + i * 0.63
        style.tx(slide, 1.14, y, 0.42, 0.32, f"{i+1:02d}", 13, style.DETECT, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.tx(slide, 1.70, y, 3.98, 0.34, item, 16, style.BODY_INK, False)

    style.rule(slide, 6.64, 1.32, 0.028, style.JU_RED, 4.26)
    style.tx(slide, 7.16, 1.34, 5.24, 0.54, "语义能力", 29, style.SEMANTIC, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 7.16, 1.98, 5.24, 0.70, "缺少端到端误差分解", 31, style.INK, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.rule(slide, 7.64, 2.94, 4.28, style.SEMANTIC, 0.04)
    right_items = ["候选目标是否已被漏掉", "候选区域是否语义混淆", "阈值筛选是否造成额外损失"]
    for i, item in enumerate(right_items):
        y = 3.24 + i * 0.63
        style.tx(slide, 7.48, y, 0.42, 0.32, f"{i+1:02d}", 13, style.SEMANTIC, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.tx(slide, 8.04, y, 3.98, 0.34, item, 16, style.BODY_INK, False)

    style.rule(slide, 1.32, 5.48, 10.68, style.GRID, 0.025)
    chain = [
        (1.36, "控制变量", style.DETECT),
        (5.18, "分层协议", style.SEMANTIC),
        (9.00, "审计与边界", style.JU_RED),
    ]
    for i, (x, label, color) in enumerate(chain):
        style.tx(slide, x, 5.78, 2.78, 0.44, label, 20, color, True,
                 PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        if i < 2:
            _line(slide, (x + 2.88, 6.00), (x + 3.58, 6.00),
                  color=style.JU_RED, width=1.8, arrow=True)
    style.note(
        slide,
        "本课题的缺口不是再堆叠一个模块，而是把两类证据问题分开。在检测侧，需要固定头宽、多种子重复并检查交互效应，才能说明P2的独立收益。在语义侧，需要把候选漏检、区域混淆与阈值筛选分层计算，而不是用单一指标代替系统分析。",
    )


def _objectives(prs):
    """role=scope | form=two objectives + boundary rail | static"""
    slide = style.add_content(
        prs, "开题证据已足以支撑研究路线，但不代表论文实验已全部闭环", 10
    )
    style.tx(slide, 0.82, 1.24, 8.02, 0.36, "两个研究目标", 17, style.JU_RED, True)
    rows = [
        (1.78, "01", "改善小目标定位", "在固定头宽与同种子对照下，检验 P2 与 CBAM 的独立效应及交互。", style.DETECT),
        (3.62, "02", "诊断候选区域命名", "按真值框、检测框和冻结规则三层协议，区分定位、语义与筛选失败。", style.SEMANTIC),
    ]
    for y, number, head, body, color in rows:
        style.tx(slide, 0.88, y, 0.78, 0.82, number, 35, color, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.rule(slide, 1.78, y + 0.09, 0.06, color, 1.15)
        style.tx(slide, 2.08, y, 5.94, 0.46, head, 22, style.INK, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
        style.tx(slide, 2.08, y + 0.56, 6.08, 0.75, body, 15.5, style.BODY_INK,
                 False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)

    style.rect(slide, 9.10, 1.24, 3.15, 4.75, fill=style.BOUNDARY_LIGHT,
               line=style.BOUNDARY, line_w=0.9)
    style.tx(slide, 9.40, 1.56, 2.55, 0.43, "当前边界", 20,
             style.BOUNDARY, True, PP_ALIGN.CENTER)
    boundaries = [
        "严格独立的同域确认尚未完成",
        "视频、摄像头与时间元数据仍不可靠",
        "目标边缘设备尚未锁定",
        "不宣称已实现广泛跨道路泛化与成熟部署",
    ]
    for i, text in enumerate(boundaries):
        y = 2.26 + i * 0.88
        style.tx(slide, 9.38, y, 0.38, 0.30, "—", 16, style.BOUNDARY, True)
        style.tx(slide, 9.80, y, 2.10, 0.68, text, 14.3, style.BOUNDARY,
                 False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    style.takeaway(slide, "目标是改善定位、诊断命名；未完成的跨域与设备验证保留为后续计划")
    style.note(
        slide,
        "本课题有两个明确目标：一是在固定监控下提高小目标候选框质量，并用受控实验分离P2和CBAM的效应；二是通过三层协议诊断固定词表命名的失败来源。当前证据可以支撑开题和路线判断，但严格独立确认、时空元数据、边缘设备和广泛泛化尚未闭环。",
    )


def _content_detection(prs):
    """role=method | form=2x2 factor matrix + five-seed rail | static"""
    slide = style.add_content(
        prs, "内容一：固定头宽的 P2×CBAM 2×2×5-seed 受控实验", 11
    )
    style.tx(slide, 0.82, 1.18, 7.28, 0.36, "共同条件：Detect 分类头隐藏宽度 = 128",
             16, style.DETECT, True)
    style.tx(slide, 2.42, 1.62, 4.90, 0.34, "P2 因子",
             18, style.INK, True, PP_ALIGN.CENTER)
    style.tx(slide, 0.78, 3.24, 1.14, 0.64, "CBAM\n因子",
             18, style.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 2.10, 1.96, 2.38, 0.30, "无 P2", 16, style.MUTE, True,
             PP_ALIGN.CENTER)
    style.tx(slide, 5.03, 1.96, 2.38, 0.30, "有 P2", 16, style.DETECT, True,
             PP_ALIGN.CENTER)
    style.tx(slide, 0.82, 2.68, 1.08, 0.32, "无 CBAM", 15, style.MUTE, True,
             PP_ALIGN.RIGHT)
    style.tx(slide, 0.82, 4.18, 1.08, 0.32, "有 CBAM", 15, style.SEMANTIC, True,
             PP_ALIGN.RIGHT)
    cells = [
        (2.10, 2.40, "baseline", style.WHITE, style.MUTE),
        (5.03, 2.40, "p2_head128", style.DETECT_LIGHT, style.DETECT),
        (2.10, 3.90, "cbam_only", style.SEMANTIC_LIGHT, style.SEMANTIC),
        (5.03, 3.90, "p2_cbam_head128", style.PALE_RED, style.JU_RED),
    ]
    for x, y, label, fill, line in cells:
        style.rect(slide, x, y, 2.38, 1.14, fill=fill, line=line, line_w=1.0)
        style.tx(slide, x + 0.12, y + 0.06, 2.14, 1.02, label, 16.5, line, True,
                 PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)

    style.rule(slide, 8.05, 1.38, 0.03, style.GRID, 4.34)
    style.tx(slide, 8.58, 1.48, 3.32, 0.56, "× 5", 42, style.JU_RED, True,
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
    style.tx(slide, 8.58, 2.30, 3.32, 0.42, "独立随机种子", 18,
             style.INK, True, PP_ALIGN.CENTER)
    style.tx(slide, 8.58, 2.88, 3.32, 0.40, "seed 0  ·  1  ·  2  ·  3  ·  4",
             15, style.MUTE, True, PP_ALIGN.CENTER)
    style.rule(slide, 8.88, 3.56, 2.72, style.JU_RED, 0.03)
    style.tx(slide, 8.58, 3.86, 3.32, 0.92, "4 个配置\n× 5 seeds = 20 次训练",
             22, style.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    style.tx(slide, 8.58, 5.04, 3.32, 0.50, "同 seed 配对，减少训练波动影响",
             14.5, style.MUTE, False, PP_ALIGN.CENTER)
    style.takeaway(slide, "只有先锁定隐藏头宽，才能把 P2、CBAM 与交互效应分开")
    style.note(
        slide,
        "第一项研究内容是固定检测头隐藏宽度为128，将P2和CBAM作为两个二值因子，形成4个可直接比较的配置。每个配置重复5个独立随机种子，共计20次训练，并在同一种子内配对。这一设计的目的是把结构效应与隐藏头变化、随机波动分开。",
    )


def _content_semantic(prs):
    """role=method | form=three-level protocol staircase | static"""
    slide = style.add_content(
        prs, "内容二：三级输入逐层加入真实误差", 12
    )
    stages = [
        (0.82, 3.80, 3.42, 1.52, "01", "GT 框", "只测区域命名能力", "不含检测漏检与框偏移", style.DETECT),
        (4.48, 2.90, 3.42, 2.42, "02", "检测框", "加入真实候选误差", "候选漏检 · 框偏移 · 冗余提议", style.SEMANTIC),
        (8.14, 2.00, 4.12, 3.32, "03", "冻结规则", "在 val 选工作点并锁定", "评估置信度和 margin 筛选的额外代价", style.JU_RED),
    ]
    for x, y, w, h, num, head, sub, detail, color in stages:
        style.rect(slide, x, y, w, h, fill=style.WHITE, line=color, line_w=1.2)
        style.tx(slide, x + 0.22, y + 0.18, 0.64, 0.46, num, 23, color, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
        style.tx(slide, x + 0.90, y + 0.18, w - 1.12, 0.46, head, 21, style.INK,
                 True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
        style.rule(slide, x + 0.22, y + 0.80, w - 0.44, color, 0.025)
        style.tx(slide, x + 0.24, y + 1.00, w - 0.48, 0.48, sub, 15.5, color, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
        if h > 1.8:
            style.tx(slide, x + 0.24, y + 1.62, w - 0.48, h - 1.82, detail,
                     14.3, style.MUTE, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    _line(slide, (4.24, 4.52), (4.48, 4.52), color=style.JU_RED,
          width=1.8, arrow=True)
    _line(slide, (7.90, 3.62), (8.14, 3.62), color=style.JU_RED,
          width=1.8, arrow=True)
    style.tx(slide, 1.10, 1.32, 6.56, 0.50,
             "三级证据不是三个模型\n而是逐层放入检测和筛选环节",
             18, style.MUTE, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    style.takeaway(slide, "第一层给出语义上限，第二层测级联误差，第三层检验冻结规则的净价值")
    style.note(
        slide,
        "第二项研究内容是三层语义诊断。第一层使用真值框，只问CLIP在固定八类词表内能否命名；第二层换成真实检测框，加入漏检、框偏移和冗余候选；第三层只在验证集选择工作点并冻结，用于检验置信度与语义margin规则是否真正改善端到端结果。",
    )


def _content_audit(prs):
    """role=method | form=audit trace + error/boundary branches | static"""
    slide = style.add_content(
        prs, "内容三：用审计追溯、误差分解和边界验证约束每一条结论", 13
    )
    trace = [
        (0.82, "配置 / 权重"),
        (3.48, "训练 / 推理日志"),
        (6.14, "结构化结果"),
        (8.80, "图表 / 结论边界"),
    ]
    for i, (x, label) in enumerate(trace):
        style.rect(slide, x, 1.42, 2.22, 0.82, fill=style.WHITE,
                   line=style.JU_RED if i == 3 else style.GRID, line_w=1.0)
        style.tx(slide, x + 0.12, 1.48, 1.98, 0.68, label, 15.5,
                 style.JU_RED if i == 3 else style.INK, True,
                 PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        if i < 3:
            _line(slide, (x + 2.22, 1.83), (x + 2.58, 1.83),
                  color=style.JU_RED, width=1.6, arrow=True)
    style.tx(slide, 11.34, 1.54, 1.04, 0.52, "可追溯", 15,
             style.JU_RED, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)

    columns = [
        (0.82, "审计追溯", ["结论回到配置、日志与结果文件", "直接证据与推定信息分开"], style.JU_RED),
        (4.66, "误差分解", ["定位漏检：候选框没有进入语义阶段", "语义误分与过滤分别统计"], style.SEMANTIC),
        (8.50, "边界验证", ["同域独立确认、外部定位与开放词表对照", "设备未锁定时只报告 GPU 原型量级"], style.BOUNDARY),
    ]
    for x, head, bullets, color in columns:
        style.rule(slide, x, 2.88, 3.02, color, 0.055)
        style.tx(slide, x, 3.10, 3.02, 0.48, head, 21, color, True,
                 PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
        for i, body in enumerate(bullets):
            y = 3.86 + i * 1.02
            style.tx(slide, x, y, 0.34, 0.30, f"{i+1:02d}", 12.5, color, True,
                     PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, style.FONT_DISPLAY)
            style.tx(slide, x + 0.46, y - 0.02, 2.56, 0.74, body, 14.4,
                     style.BODY_INK, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP)
    style.takeaway(slide, "结论必须能回到证据；尚未完成的验证则显式保留为后续边界")
    style.note(
        slide,
        "第三项内容是把实验结论纳入可追溯的审计链。每个数字应能回到配置、权重、日志和结构化结果；端到端失败要拆成候选漏检、语义误分和规则过滤。同时用独立同域数据、外部数据、开放词表对照和目标设备验证适用范围，没有闭环的部分不提前写成结果。",
    )


def build(prs, project: Path, root: Path):
    """Append slides 1–13 to ``prs`` in approved narrative order."""
    del root  # Section A uses repository assets only; keep the shared signature stable.
    _cover(prs, project)
    _agenda(prs)
    _divider(
        prs, "01", "选题依据", "从固定监控的两道真实瓶颈出发", 3,
        "第一部分说明选题依据。我将从固定监控的成像特点和数据尺度分布出发，引出“找不到”与“认不对”两道连续瓶颈。",
    )
    _background(prs)
    _two_bottlenecks(prs, project)
    _divider(
        prs, "02", "国内外研究现状", "三条研究路线与尚未闭合的证据缺口", 6,
        "第二部分把相关工作分为小目标检测、道路异常检测和视觉语言模型三条路线，重点不是罗列模块，而是找出它们之间未被解释的证据空白。",
    )
    _related_work(prs)
    _gap(prs)
    _divider(
        prs, "03", "研究目标与内容", "两个目标、三项内容与明确的结论边界", 9,
        "第三部分给出本课题的研究目标和三项主要内容。我会同时标明哪些证据已能支撑开题，以及哪些独立确认、跨域与设备实验仍属于后续任务。",
    )
    _objectives(prs)
    _content_detection(prs)
    _content_semantic(prs)
    _content_audit(prs)
