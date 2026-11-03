#!/usr/bin/env python3
"""将 Markdown 论文草稿转换为 Word (.docx) 格式。
输出：paper/word/论文初稿.docx（六章合并）
"""
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

PROJECT = Path(__file__).resolve().parents[1]
DRAFTS = PROJECT / "paper/drafts"
OUTPUT = PROJECT / "paper/word"
OUTPUT.mkdir(parents=True, exist_ok=True)

CHAPTERS = [
    ("declaration.md", "独创性声明"),
    ("abstract.md", "摘要"),
    ("ch1_introduction.md", "第一章  绪论"),
    ("ch2_related_work.md", "第二章  相关理论与技术基础"),
    ("ch3_method.md", "第三章  面向路面小目标的改进检测方法"),
    ("ch4_clip.md", "第四章  基于CLIP的预留类别识别与OOD评估"),
    ("ch5_experiments.md", "第五章  实验与分析"),
    ("ch6_conclusion.md", "结论"),
    ("references.md", "参考文献"),
    ("acknowledgments.md", "致谢"),
    ("publications.md", "在学期间发表的学术论文及其他科研成果"),
]


def is_table_line(line):
    return line.strip().startswith("|") and line.strip().endswith("|")


def is_separator(line):
    stripped = line.strip()
    return re.match(r'^\|[\s\-:|]+\|$', stripped) is not None


def parse_table(lines, start_idx):
    """解析 Markdown 表格"""
    end = start_idx
    while end < len(lines) and is_table_line(lines[end]):
        end += 1
    table_lines = lines[start_idx:end]
    # 过滤分隔线
    table_lines = [l for l in table_lines if not is_separator(l)]
    # 解析列
    rows = []
    for tl in table_lines:
        cells = [c.strip() for c in tl.strip().strip("|").split("|")]
        rows.append(cells)
    return rows, end


def add_paragraph(doc, text, style="Normal", bold=False, font_size=None, alignment=None):
    """添加段落，处理粗体标记。"""
    if not text.strip():
        p = doc.add_paragraph("")
        return p

    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment

    # 处理 `**text**` 粗体
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = p.add_run(part[2:-2])
            run.bold = True
        else:
            run = p.add_run(part)
        if font_size:
            run.font.size = Pt(font_size)

    # 设置段落样式
    if "Normal" in doc.styles:
        p.style = doc.styles["Normal"]
        if font_size:
            p.style.font.size = Pt(font_size)

    return p


def convert_chapter(md_path, chapter_title, doc):
    """将单个 Markdown 章节转为 Word 内容。"""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 添加章节标题
    h = doc.add_heading(chapter_title, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # 去掉 YAML 前言和 H1 标题
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and chapter_title.split(" ", 1)[0] in line:
            content_start = i + 1
            break

    i = content_start
    while i < len(lines):
        line = lines[i]

        # 跳过空行
        if not line.strip():
            i += 1
            continue

        # 跳过 > 引用块（草稿说明）
        if line.strip().startswith("> "):
            i += 1
            continue

        # 跳过分隔线和markdown标题标记
        if line.strip() == "---" or line.strip().startswith("# "):
            i += 1
            continue

        # 表格
        if is_table_line(line):
            rows, i = parse_table(lines, i)
            if rows and len(rows) >= 2:
                ncols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=ncols, style="Light Grid Accent 1")
                # 填入内容 + 设置格式
                for ri, row_data in enumerate(rows):
                    for ci, cell_text in enumerate(row_data[:ncols]):
                        cell = table.cell(ri, ci)
                        # 处理单元格内的粗体标记
                        p = cell.paragraphs[0]
                        p.clear()
                        parts = re.split(r'(\*\*.*?\*\*)', cell_text)
                        for part in parts:
                            if part.startswith("**") and part.endswith("**"):
                                run = p.add_run(part[2:-2])
                                run.bold = True
                            else:
                                run = p.add_run(part)
                            run.font.size = Pt(9)
                        p.paragraph_format.space_before = Pt(1)
                        p.paragraph_format.space_after = Pt(1)
            continue

        # 标题
        if line.startswith("### "):
            h = doc.add_heading(line[4:].strip(), level=3)
            i += 1
            continue
        if line.startswith("## "):
            h = doc.add_heading(line[3:].strip(), level=2)
            i += 1
            continue

        # 代码块
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = "\n".join(code_lines)
            p = doc.add_paragraph()
            run = p.add_run(code_text)
            run.font.name = "Courier New"
            run.font.size = Pt(9)
            continue

        # 列表项 - 使用 add_paragraph 处理粗体标记
        if re.match(r'^\s*[\-\*]\s+', line) or re.match(r'^\s*\d+[\.\)]\s+', line):
            # 去除列表前缀标记，保留内容
            content = re.sub(r'^\s*[\-\*]\s+', '', line.strip())
            content = re.sub(r'^\s*\d+[\.\)]\s+', '', content)
            p = add_paragraph(doc, content, font_size=12)
            if p.runs:
                p.style = doc.styles["List Bullet"]
            i += 1
            continue

        # 普通段落
        add_paragraph(doc, line, font_size=12)
        i += 1

    doc.add_page_break()


def main():
    doc = Document()

    # 设置默认字体
    style = doc.styles["Normal"]
    font = style.font
    font.name = "宋体"
    font.size = Pt(12)

    # 中文题名页
    for _ in range(4):
        doc.add_paragraph("")

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("融合视觉语言模型的路面抛洒物检测与异常识别方法研究")
    run.bold = True
    run.font.size = Pt(22)

    doc.add_paragraph("")

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub_p.add_run("Research on Road Debris Detection and Anomaly Recognition\nMethod Integrating Vision-Language Models")
    run.font.size = Pt(14)

    for _ in range(3):
        doc.add_paragraph("")

    info_lines = [
        "专业名称：控制工程",
        "指导教师：",
        "姓    名：朱守亮",
        "",
        "江苏大学",
        "2027 年 3 月",
    ]
    for line in info_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.size = Pt(14)

    doc.add_page_break()

    # 转换各章
    for filename, title in CHAPTERS:
        md_path = DRAFTS / filename
        if md_path.exists():
            print(f"转换: {title}")
            convert_chapter(md_path, title, doc)
        else:
            print(f"⚠ 文件不存在: {md_path}")

        # 在 Ch3 和 Ch4 之后插入框架图
        if filename == "ch3_method.md":
            img_path = PROJECT / "paper/figures/fig_p2cbam_architecture.png"
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(5.5))
                caption = doc.add_paragraph("图3.1  P2+CBAM 检测结构示意图")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption.runs[0].font.size = Pt(10) if caption.runs else None

            img_path2 = PROJECT / "paper/figures/fig_framework_overview.png"
            if img_path2.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(img_path2), width=Inches(5.5))
                caption = doc.add_paragraph("图3.2  整体方法框架图")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if filename == "ch4_clip.md":
            img_path = PROJECT / "paper/figures/fig_clip_pipeline.png"
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(5.5))
                caption = doc.add_paragraph("图4.1  CLIP固定词表识别流程图")
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 保存
    out_path = OUTPUT / "论文初稿.docx"
    doc.save(str(out_path))
    print(f"\n✅ 保存: {out_path}")
    print(f"   文件大小: {out_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
