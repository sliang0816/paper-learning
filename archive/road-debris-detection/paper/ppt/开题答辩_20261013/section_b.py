"""Slides 14-24: technical route, innovation, prior evidence, and plan."""
from __future__ import annotations

from pathlib import Path

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

import deckkit as dk
import style as st


def _metric(slide, x, y, w, value, label, *, color=st.JU_RED, value_size=28):
    """Direct-on-canvas metric stack; no card or shadow."""
    st.tx(slide, x, y, w, 0.48, value, value_size, color, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, st.FONT_EN)
    st.tx(slide, x, y + 0.64, w, 0.34, label, 13.5, st.MUTE, False)
    st.rule(slide, x, y + 1.10, w, st.GRID, 0.014)


def _numbered_dependency(slide, y, number, title, body):
    st.tx(slide, 0.78, y, 0.72, 0.48, number, 27, st.JU_RED, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 1.58, y - 0.01, 3.10, 0.38, title, 18, st.INK, True)
    st.tx(slide, 4.82, y - 0.01, 3.62, 0.50, body, 14.5, st.BODY_INK, False)
    st.rule(slide, 1.58, y + 0.56, 6.86, st.GRID, 0.014)
    st.arrow(slide, (8.68, y + 0.23), (9.70, y + 0.23), st.JU_RED, 1.55)


def slide_14(prs, project: Path, root: Path):
    """role=divider | form=section | static: chapter change | takeaway='技术路线与研究方案'"""
    slide = st.add_section(
        prs, "04", "技术路线与研究方案",
        "从候选检测、语义命名到审计边界，逐层说明方案如何闭环。", 14,
    )
    st.note(slide, "下面进入技术路线与研究方案。重点不是罗列模块，而是说明检测、语义和审计三部分如何衔接，以及哪些环节目前已有证据、哪些仍需后续确认。")


def slide_15(prs, project: Path, root: Path):
    """role=method overview | form=whole source figure + evidence rail | static: scan as a whole | takeaway='总体路线以两级诊断串起检测、命名与边界审计'"""
    slide = st.add_content(prs, "总体路线以两级诊断串起检测、命名与边界审计", 15)
    fig = st.asset(project, "paper/figures/fig_framework_overview.png")
    st.picture(
        slide, fig, 0.72, 1.02, 11.85, 4.38,
        "总体技术路线：监控图像经候选检测与裁剪后，由固定八类词表进行语义命名，并输出审计分数。",
    )
    st.target_window(slide, 5.38, 2.82, 0.72, 0.58, st.JU_RED, 2.0)
    st.rule(slide, 0.72, 5.56, 11.85, st.JU_RED, 0.025)
    st.tx(slide, 0.82, 5.72, 1.05, 0.25, "任务链", 12, st.JU_RED, True)
    st.tx(slide, 1.80, 5.69, 4.45, 0.38, "监控图像 → 候选框 → 固定词表命名", 15.5, st.INK, True)
    st.tx(slide, 6.72, 5.72, 1.05, 0.25, "审计链", 12, st.JU_RED, True)
    st.tx(slide, 7.70, 5.69, 4.55, 0.38, "置信度、语义 margin 与 OOD 代理分数", 15.5, st.INK, True)
    st.tx(slide, 0.82, 6.19, 11.35, 0.30,
          "输出既服务于识别，也服务于定位失败来源与限定结论边界。",
          14, st.MUTE, False, PP_ALIGN.CENTER)
    st.source(slide, "来源：项目图 fig_framework_overview.png；本课题技术路线汇总")
    st.note(slide, "这一页先交代整体技术路线。前半段由固定监控图像进入候选检测，解决“找不到”；后半段对候选框做固定八类语义命名，解决“认不对”。最右侧的审计与边界用于区分模型失败、规则失败和证据不足。本路线证明方案结构已明确，不代表外部确认和部署验证已经完成。")


def slide_16(prs, project: Path, root: Path):
    """role=method detail | form=source architecture + direct experiment spec | static: figure needs simultaneous scan | takeaway='检测方案只改变 P2 与 CBAM，头宽与训练协议保持固定'"""
    slide = st.add_content(prs, "检测方案：只改变 P2 与 CBAM，训练协议保持固定", 16)
    fig = st.asset(project, "paper/figures/fig_p2cbam_architecture.png")
    st.picture(
        slide, fig, 0.72, 1.15, 8.05, 4.57,
        "P2 与 CBAM 检测结构：P2 扩展高分辨率检测层，四个分类分支的隐藏宽度统一为 128。",
    )
    st.rule(slide, 9.05, 1.26, 3.42, st.JU_RED, 0.035)
    st.tx(slide, 9.05, 1.47, 3.42, 0.56, "2 × 2 × 5", 36, st.JU_RED, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 9.07, 2.24, 3.30, 0.31, "四种配置 · 每种五个种子", 14, st.MUTE, False)
    st.rule(slide, 9.05, 2.62, 3.42, st.GRID, 0.018)
    st.tx(slide, 9.05, 2.82, 3.42, 0.38, "P2 ∈ {关，开}", 18, st.DETECT, True)
    st.tx(slide, 9.05, 3.28, 3.42, 0.38, "CBAM ∈ {关，开}", 18, st.SEMANTIC, True)
    st.rule(slide, 9.05, 3.82, 3.42, st.GRID, 0.018)
    st.tx(slide, 9.05, 4.05, 3.42, 0.32, "控制变量", 12, st.JU_RED, True)
    st.tx_lines(slide, 9.05, 4.43, 3.35, 1.02,
                ["固定分类头宽 128", "固定训练协议与数据划分", "比较主效应与交互项"],
                14.5, st.BODY_INK, False, line_spacing=1.0, space_after=5)
    st.tx(slide, 0.86, 5.94, 11.46, 0.36,
          "目的：把结构改动与随机种子波动分开，而不是用单次最优结果下结论。",
          15, st.INK, True, PP_ALIGN.CENTER)
    st.source(slide, "来源：项目图 fig_p2cbam_architecture.png；P2×CBAM 固定头宽受控实验")
    st.note(slide, "检测方案的核心是控制变量。只切换 P2 和 CBAM 两个因素，形成二乘二配置，每种配置重复五个随机种子；分类头宽固定为 128，训练协议和数据划分保持一致。这样可以区分 P2 主效应、CBAM 主效应及交互项。它支持可归因比较，但仍需独立数据确认能否外推。")


def slide_17(prs, project: Path, root: Path):
    """role=diagnostic method | form=whole source figure | static: three levels compared at once | takeaway='语义方案用三层输入逐步定位错误来自哪里'"""
    slide = st.add_content(prs, "语义方案用三层输入逐步定位错误来自哪里", 17)
    fig = st.asset(project, "paper/figures/fig_clip_pipeline.png")
    st.picture(
        slide, fig, 0.72, 1.02, 11.85, 5.33,
        "三层语义诊断流程：真值框参考、检测框端到端评估，以及在验证集上冻结阈值后的历史测试。",
    )
    st.rule(slide, 0.90, 6.37, 11.48, st.JU_RED, 0.022)
    st.tx(slide, 0.92, 6.43, 11.42, 0.26,
          "GT 框测分类上限 · 检测框测端到端损失 · 冻结规则测历史迁移边界",
          13.5, st.INK, True, PP_ALIGN.CENTER)
    st.source(slide, "来源：项目图 fig_clip_pipeline.png；语义诊断实验协议")
    st.note(slide, "语义部分不是只报告一个最终准确率，而是分三层诊断。真值框隔离检测误差，回答分类本身能做到什么；检测框进入端到端流程，观察召回与条件分类如何共同损失；最后只在验证集确定阈值，再应用到历史测试。三层结果能定位瓶颈，但历史测试仍不能替代新的独立确认集。")


def slide_18(prs, project: Path, root: Path):
    """role=dependency boundary | form=three dependency rails converging to closure | static: claim boundary | takeaway='完整闭环依赖独立数据、时间信息与目标硬件'"""
    slide = st.add_content(prs, "完整闭环依赖独立数据、时间信息与目标硬件", 18)
    _numbered_dependency(slide, 1.40, "01", "独立同域数据", "确认受控增益与规则阈值能否复现")
    _numbered_dependency(slide, 2.84, "02", "时间与相机元数据", "支撑视频连续性、跨时段与开放集分析")
    _numbered_dependency(slide, 4.28, "03", "目标边缘设备", "决定算力、内存与端侧延迟约束")
    st.rule(slide, 9.80, 1.32, 0.035, st.JU_RED, 4.02)
    st.tx(slide, 10.16, 1.66, 2.12, 0.36, "满足条件后", 13, st.MUTE, True)
    st.tx_lines(slide, 10.14, 2.18, 2.20, 1.48,
                ["独立确认", "开放集研究", "端侧验证"],
                22, st.JU_RED, True, line_spacing=0.96, space_after=7)
    st.tx(slide, 10.14, 4.05, 2.15, 0.84,
          "才构成\n完整闭环", 24, st.INK, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    st.rule(slide, 0.72, 5.55, 11.85, st.JU_RED, 0.028)
    st.tx(slide, 0.82, 5.76, 11.55, 0.58,
          "当前可以答辩：方案与内部证据充分；当前不能承诺：外部泛化与部署已经完成。",
          16, st.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    st.note(slide, "这三项不是附属工作，而是完整闭环的前提。独立同域数据用于确认内部受控增益是否复现；可靠的视频、相机与时间元数据决定能否做连续性和开放集研究；目标边缘设备决定真实部署约束。当前证据足以支持开题方案，但不足以宣称跨摄像头泛化或端侧部署已经完成。")


def slide_19(prs, project: Path, root: Path):
    """role=divider | form=section | static: chapter change | takeaway='创新点与难点'"""
    slide = st.add_section(
        prs, "05", "创新点与难点",
        "创新不在堆叠模块，而在可归因实验与分层诊断；难点是守住证据边界。", 19,
    )
    st.note(slide, "下面概括本研究的创新点和主要难点。创新强调如何获得可解释证据，难点则集中在独立确认、开放集条件和部署约束。")


def slide_20(prs, project: Path, root: Path):
    """role=innovation + difficulty | form=editorial split with claim boundary | static: paired comparison | takeaway='创新在于可归因与可诊断，难点在于证据边界'"""
    slide = st.add_content(prs, "贡献在于可归因与可诊断，难点在于证据边界", 20)
    st.tx(slide, 0.76, 1.30, 1.05, 0.62, "01", 42, st.JU_RED, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 1.72, 1.38, 4.55, 0.46, "设计贡献：结构收益不靠单次最优", 19, st.INK, True)
    st.rule(slide, 0.78, 2.08, 5.48, st.JU_RED, 0.025)
    st.tx_lines(slide, 0.86, 2.34, 5.28, 1.68,
                ["固定头宽与训练协议", "P2 × CBAM 二乘二设计", "五个种子报告主效应与交互项"],
                17, st.BODY_INK, False, line_spacing=1.06, space_after=8)
    st.tx(slide, 6.95, 1.30, 1.05, 0.62, "02", 42, st.JU_RED, True,
          PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 7.92, 1.38, 4.60, 0.46, "设计贡献：错误来源可被拆开", 19, st.INK, True)
    st.rule(slide, 6.96, 2.08, 5.46, st.JU_RED, 0.025)
    st.tx_lines(slide, 7.04, 2.34, 5.26, 1.68,
                ["GT 框测分类能力上限", "检测框测召回与条件分类", "冻结规则测历史迁移与开放集边界"],
                17, st.BODY_INK, False, line_spacing=1.06, space_after=8)
    st.rule(slide, 6.61, 1.25, 0.025, st.GRID, 3.12)
    st.rule(slide, 0.72, 4.52, 11.85, st.JU_RED, 0.032)
    st.tx(slide, 0.82, 4.77, 2.05, 0.30, "可以主张", 13, st.JU_RED, True)
    st.tx(slide, 2.50, 4.72, 9.72, 0.40,
          "研究设计与内部证据链已经形成", 18, st.INK, True)
    st.tx(slide, 0.82, 5.40, 2.05, 0.30, "不能主张", 13, st.MUTE, True)
    st.tx(slide, 2.50, 5.34, 9.72, 0.50,
          "独立确认、跨摄像头泛化、开放词汇闭环与端侧部署已经完成", 17, st.BODY_INK, False)
    st.tx(slide, 0.82, 6.12, 11.45, 0.34,
          "难点不是继续叠模块，而是取得足够独立、可追溯且与应用条件一致的证据。",
          14.5, st.MUTE, False, PP_ALIGN.CENTER)
    st.note(slide, "本研究的创新点有两层。第一，用固定头宽的二乘二多种子实验，把 P2、CBAM 与随机波动分开；第二，用真值框、检测框和冻结规则三层诊断，把检测、分类和阈值问题分开。真正的难点是证据边界：内部可归因不等于外部已确认，原型可运行也不等于端侧部署完成。")


def slide_21(prs, project: Path, root: Path):
    """role=divider | form=section | static: chapter change | takeaway='前期基础与计划'"""
    slide = st.add_section(
        prs, "06", "前期基础与计划",
        "已有受控实验与语义诊断基础；后续按证据依赖补齐独立确认与部署验证。", 21,
    )
    st.note(slide, "下面汇报已经完成的前期基础，并据此安排后续计划。请注意，这里区分已获得的内部证据和仍待完成的独立确认。")


def slide_22(prs, project: Path, root: Path):
    """role=detection evidence | form=whole source plot + direct metrics | static: compare evidence and caveat | takeaway='P2 的增益跨 5 个种子一致，CBAM 未显示稳定独立收益'"""
    slide = st.add_content(prs, "P2 的增益跨 5 个种子一致，CBAM 未显示稳定独立收益", 22)
    fig = st.asset(project, "paper/figures/fig_ch3_size_stratified_map.png")
    st.picture(
        slide, fig, 0.72, 1.30, 7.58, 3.75,
        "早期三种子尺度分层 mAP50 图，展示 P2 相关配置对小目标与中目标的变化。",
    )
    st.target_window(slide, 4.78, 3.18, 0.62, 0.92, st.JU_RED, 2.0)
    st.tx(slide, 0.82, 5.12, 7.36, 0.38,
          "图为早期 3-seed 尺度分层视图；右侧为最终 5-seed 受控主实验。",
          12.5, st.MUTE, False, PP_ALIGN.CENTER)
    _metric(slide, 8.66, 1.42, 3.70, "+2.71 ± 1.65 pp", "P2 对整体 mAP50 · 5/5 为正", color=st.JU_RED)
    _metric(slide, 8.66, 2.76, 3.70, "+4.01 ± 1.58 pp", "P2 对小目标 AP50 · 5/5 为正", color=st.JU_RED)
    st.tx(slide, 8.66, 4.24, 3.70, 0.38, "CBAM：无稳定独立增益", 17, st.INK, True)
    st.tx(slide, 8.66, 4.68, 3.70, 0.34, "交互项 −1.53 ± 3.12 pp", 14, st.MUTE, False)
    st.rule(slide, 8.66, 5.24, 3.70, st.GRID, 0.014)
    st.tx(slide, 0.82, 5.74, 11.42, 0.50,
          "现有证据支持继续验证 P2，不支持把 CBAM 描述为稳定提升来源。",
          16, st.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    st.source(slide, "来源：项目图 fig_ch3_size_stratified_map.png；固定头宽 P2×CBAM 五种子主实验")
    st.note(slide, "右侧数字来自最终五种子受控实验：P2 对 mAP50 平均提升 2.71 个百分点，对小目标 AP50 提升 4.01 个百分点，而且五个种子均为正。CBAM 没有稳定独立收益，交互项也高度波动。左图只是早期三种子尺度分层视图，用来展示结构趋势，不能替代右侧五种子统计。")


def slide_23(prs, project: Path, root: Path):
    """role=semantic evidence | form=qualitative source figure + metric ladder | static: cases and limits | takeaway='GT 框分类仍有限，冻结开放词汇基线远未闭环'"""
    slide = st.add_content(prs, "GT 框分类仍有限，冻结开放词汇基线远未闭环", 23)
    fig = st.asset(project, "paper/figures/fig_qualitative_pipeline_cases.png")
    st.picture(
        slide, fig, 0.72, 1.18, 8.02, 3.82,
        "YOLO-CLIP 代表性案例：正确 GL、正确 RU、语义混淆、漏检、已知类误报与背景误报。",
    )
    st.tx(slide, 0.82, 5.08, 2.38, 0.28, "定位漏检", 17, st.DETECT, True, PP_ALIGN.CENTER)
    st.tx(slide, 3.38, 5.08, 2.38, 0.28, "语义混淆", 17, st.SEMANTIC, True, PP_ALIGN.CENTER)
    st.tx(slide, 5.94, 5.08, 2.38, 0.28, "背景误报", 17, st.BOUNDARY, True, PP_ALIGN.CENTER)
    st.tx(slide, 0.82, 5.40, 7.92, 0.28,
          "六格案例共同说明：定位、语义与背景误报都可能成为瓶颈。",
          12.5, st.MUTE, False, PP_ALIGN.CENTER)
    st.tx(slide, 9.02, 1.06, 3.28, 0.18, "val｜GT 框分类｜top-1", 9.2, st.DETECT, True)
    _metric(slide, 9.02, 1.36, 3.28, "50.91%", "GL/RU top-1", color=st.JU_RED, value_size=29)
    st.tx(slide, 9.02, 2.28, 3.28, 0.14, "internal-confirm-230｜检测框规则｜F1", 8.3, st.SEMANTIC, True)
    _metric(slide, 9.02, 2.63, 3.28, "39.44% > 32.45%", "置信度规则 F1 > 置信度+margin", color=st.INK, value_size=19)
    st.tx(slide, 9.02, 4.04, 3.28, 0.22, "internal-confirm-230｜直接开放词汇｜F1", 8.3, st.JU_RED, True)
    st.tx(slide, 9.02, 4.42, 1.30, 0.42, "0%", 22, st.INK, True,
          PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 9.02, 4.84, 1.30, 0.28, "YOLO-World", 10.5, st.MUTE, False,
          PP_ALIGN.CENTER)
    st.tx(slide, 10.78, 4.42, 1.52, 0.42, "0.80%", 20, st.INK, True,
          PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, st.FONT_DISPLAY)
    st.tx(slide, 10.78, 4.84, 1.52, 0.28, "GDINO", 10.5, st.MUTE, False,
          PP_ALIGN.CENTER)
    st.rule(slide, 9.02, 5.10, 3.28, st.GRID, 0.014)
    st.tx(slide, 0.82, 5.84, 11.42, 0.50,
          "230 图回溯确认支持误差分析，但不等于新的独立测试；开放词汇仍是后续问题。",
          15, st.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    st.source(slide, "来源：项目图 fig_qualitative_pipeline_cases.png；CLIP、回溯规则与冻结基线实验")
    st.note(slide, "语义部分的上限仍然有限：在真值框条件下，GL/RU 二类 top-1 只有 50.91%。对 230 张图的回溯确认中，单独使用置信度的 F1 为 39.44%，反而高于置信度加 margin 的 32.45%。YOLO-World 与 Grounding DINO 冻结基线接近失败，说明开放词汇闭环尚未建立，回溯结果也不能视为独立测试。")


def slide_24(prs, project: Path, root: Path):
    """role=roadmap | form=timeline + aligned entry conditions | static: relative phases | takeaway='后续工作按证据依赖推进，不提前承诺开放词汇与部署'"""
    slide = st.add_content(prs, "后续工作按证据依赖推进，不提前承诺部署", 24)
    events = [
        ("0–2 月", "独立确认与审计", "同域复现；日志覆盖率达标"),
        ("2–5 月", "时间与开放集", "元数据可用；冻结协议预注册"),
        ("5–8 月", "目标设备验证", "输出延迟、内存、精度报告"),
    ]
    dk.timeline(
        slide, 0.86, 1.24, 11.60, events,
        orientation="h", highlight=0, accent=st.JU_RED, ink=st.INK,
        axis_c=st.GRID, h=1.55, polarity="below", spacing="even", label_w=3.30,
    )
    st.rule(slide, 0.82, 3.28, 11.66, st.JU_RED, 0.028)
    centers = [2.18, 6.66, 11.14]
    entry = [
        ("验收出口", "主实验可复现，26 次训练审计链闭合"),
        ("验收出口", "视频、相机与时间元数据可用"),
        ("验收出口", "设备及算力约束明确，完成实测"),
    ]
    for cx, (lab, body) in zip(centers, entry):
        st.tx(slide, cx - 1.58, 3.62, 3.16, 0.28, lab, 11.5, st.JU_RED, True,
              PP_ALIGN.CENTER)
        st.tx(slide, cx - 1.58, 4.03, 3.16, 0.78, body, 15, st.BODY_INK, False,
              PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    st.rule(slide, 4.43, 3.57, 0.018, st.GRID, 1.62)
    st.rule(slide, 8.88, 3.57, 0.018, st.GRID, 1.62)
    st.rule(slide, 0.82, 5.42, 11.66, st.GRID, 0.018)
    st.tx(slide, 0.92, 5.72, 11.46, 0.52,
          "采用答辩后相对月份：上一阶段的证据与验收出口满足后，再进入下一阶段。",
          16, st.INK, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    st.tx(slide, 0.92, 6.39, 11.46, 0.24,
          "计划边界：严格同域确认、开放集全闭环与目标设备验证尚未完成。",
          12.5, st.MUTE, False, PP_ALIGN.CENTER)
    st.note(slide, "后续计划采用答辩后相对月份，不虚构学校绝对日期。0到2个月完成独立同域确认、日志补齐和审计闭合；2到5个月只有在元数据可靠时开展时间与开放集研究；5到8个月在目标设备确定后完成速度、内存和精度验证。每一阶段都有验收出口，未满足则停留在当前边界。")


SLIDES = [
    slide_14, slide_15, slide_16, slide_17, slide_18, slide_19,
    slide_20, slide_21, slide_22, slide_23, slide_24,
]


def build(prs, project: Path, root: Path):
    """Append slides 14-24 in the approved order."""
    for builder in SLIDES:
        builder(prs, project, root)
