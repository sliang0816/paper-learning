"""Shared visual system for the v9 opening-proposal deck.

The deck deliberately preserves the supplied Jiangsu University layout masters and
draws only within their content area.  All geometry is expressed in inches.
"""
from __future__ import annotations

import re
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import deckkit as dk

W, H = 13.333, 7.5

JU_RED = RGBColor(0xC0, 0x00, 0x00)
JU_BRIGHT = RGBColor(0xFF, 0x00, 0x00)
PALE_RED = RGBColor(0xF6, 0xD7, 0xD4)
INK = RGBColor(0x00, 0x08, 0x00)
BODY_INK = RGBColor(0x33, 0x33, 0x33)
MUTE = RGBColor(0x66, 0x66, 0x66)
GRID = RGBColor(0xD9, 0xD9, 0xD9)
LIGHT = RGBColor(0xF2, 0xF2, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DETECT = RGBColor(0x2F, 0x55, 0x97)
DETECT_LIGHT = RGBColor(0xE8, 0xEE, 0xF8)
SEMANTIC = RGBColor(0x6A, 0x3D, 0x7C)
SEMANTIC_LIGHT = RGBColor(0xF0, 0xE8, 0xF3)
SUPPORT = RGBColor(0x1B, 0x6E, 0x3C)
SUPPORT_LIGHT = RGBColor(0xE6, 0xF1, 0xEA)
BOUNDARY = RGBColor(0x8A, 0x4B, 0x08)
BOUNDARY_LIGHT = RGBColor(0xF6, 0xEA, 0xDD)

FONT_CN = "Hiragino Sans GB"
FONT_EN = "Arial"
FONT_DISPLAY = "Arial Black"

dk.set_palette(
    deep=INK, blue=DETECT, teal=SUPPORT, magenta=JU_RED,
    slate=BODY_INK, mute=MUTE, font=FONT_EN, display=FONT_DISPLAY,
    eafont=FONT_CN, eadisplay=FONT_CN,
    accents=[JU_RED, DETECT, SEMANTIC, SUPPORT, BOUNDARY],
)
dk.set_geometry(radius=0, rule_w=0.85)
dk.FONT = FONT_EN
dk.DISPLAY = FONT_DISPLAY
dk.EAFONT = FONT_CN
dk.EADISPLAY = FONT_CN

_MIXED_PUNCT = re.compile(r"([A-Za-z0-9%+\)\]])([。，、；：！？）》」』】])")
_ASCII_PUNCT = {
    "。": ".", "，": ",", "、": ",", "；": ";", "：": ":",
    "！": "!", "？": "?", "）": ")", "》": ">", "」": '"',
    "』": '"', "】": "]",
}


def tx(slide, x, y, w, h, value, size=18, color=BODY_INK, bold=False,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=None, italic=False):
    return dk.text(
        slide, x, y, w, h,
        [[(str(value), size, color, bold, italic, font or FONT_EN)]],
        align=align, anchor=anchor, space_after=0,
    )


def tx_lines(slide, x, y, w, h, lines, size=18, color=BODY_INK,
             bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             font=None, line_spacing=1.05, space_after=4):
    paragraphs = [[(str(line), size, color, bold, False, font or FONT_EN)] for line in lines]
    return dk.text(slide, x, y, w, h, paragraphs, align=align, anchor=anchor,
                   line_spacing=line_spacing, space_after=space_after)


def rect(slide, x, y, w, h, fill=WHITE, line=GRID, line_w=0.8):
    return dk.box(slide, x, y, w, h, fill=fill, line=line, line_w=line_w,
                  round=False)


def rule(slide, x, y, w, color=GRID, h=0.018):
    return dk.box(slide, x, y, w, h, fill=color, line=color, line_w=0)


def circle(slide, cx, cy, r, fill=JU_RED, line=None, line_w=0.8):
    shp = dk._flat(slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(cx-r), Inches(cy-r), Inches(2*r), Inches(2*r)
    ))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line; shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    return shp


def arrow(slide, p0, p1, color=JU_RED, width=1.8, style="solid"):
    return dk.connector(slide, p0, p1, color=color, width=width,
                        style=style, arrow=True)


def label(slide, x, y, w, h, value, *, fill=LIGHT, color=BODY_INK,
          line=None, size=15, bold=True, align=PP_ALIGN.CENTER):
    rect(slide, x, y, w, h, fill=fill, line=line or fill, line_w=0.7)
    tx(slide, x+0.10, y+0.02, w-0.20, h-0.04, value, size, color, bold,
       align, MSO_ANCHOR.MIDDLE)


def add_content(prs, title, page):
    """Reference layout 0: title marker, rule, red footer and page number."""
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    for ph in list(slide.placeholders):
        idx = ph.placeholder_format.idx
        if idx not in {0, 12}:
            ph._element.getparent().remove(ph._element)
    title_shape = slide.shapes.title
    # Keep the title clear of the reference template's pale marker circle.
    title_shape.left, title_shape.top = Inches(0.82), Inches(0.19)
    title_shape.width, title_shape.height = Inches(11.88), Inches(0.62)
    title_shape.text = title
    title_shape.text_frame.word_wrap = False
    for p in title_shape.text_frame.paragraphs:
        for r in p.runs:
            dk.set_font(r, 23, INK, bold=True, font=FONT_EN, ea=FONT_CN)
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == 12:
            ph.text = f"{page:02d}"
            for p in ph.text_frame.paragraphs:
                p.alignment = PP_ALIGN.RIGHT
                for r in p.runs:
                    dk.set_font(r, 9, WHITE, bold=True, font=FONT_EN, ea=FONT_CN)
    return slide


def add_section(prs, number, title, subtitle, page):
    """Reference layout 1 plus a restrained chapter title block."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    tx(slide, 0.72, 1.26, 3.10, 1.45, number, 108, JU_BRIGHT, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, FONT_DISPLAY)
    rule(slide, 0.78, 3.05, 4.00, JU_RED, 0.035)
    tx(slide, 0.80, 3.32, 6.70, 0.78, title, 34, INK, True,
       PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    tx(slide, 0.82, 4.20, 6.75, 0.48, subtitle, 17, MUTE, False)
    tx(slide, 11.57, 7.20, 0.95, 0.18, f"{page:02d}", 9, WHITE, True,
       PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    dk.design_intent(slide, envelope="upper", reason="章节页以大数字和留白承担叙事换气。")
    return slide


def add_blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[2])


def source(slide, value, y=6.78, color=MUTE):
    return tx(slide, 0.72, y, 11.85, 0.20, value, 10.5, color, False)


def takeaway(slide, value, *, color=JU_RED, y=6.18, fill=PALE_RED):
    rect(slide, 0.72, y, 11.85, 0.50, fill=fill, line=fill)
    tx(slide, 0.94, y+0.03, 11.42, 0.42, value, 16, color, True,
       PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def target_window(slide, x, y, w, h, color=JU_RED, line_w=2.4):
    """Open-corner target window. Meaning is fixed: the candidate under inspection."""
    seg = min(0.34, w*0.18, h*0.24)
    thickness = max(0.018, line_w / 72.0)
    for x0, y0, x1, y1 in [
        (x, y+seg, x, y), (x, y, x+seg, y),
        (x+w-seg, y, x+w, y), (x+w, y, x+w, y+seg),
        (x, y+h-seg, x, y+h), (x, y+h, x+seg, y+h),
        (x+w-seg, y+h, x+w, y+h), (x+w, y+h-seg, x+w, y+h),
    ]:
        if abs(x1 - x0) < 1e-6:
            mark = dk.box(slide, x0-thickness/2, min(y0, y1), thickness,
                          abs(y1-y0), fill=color, line=color, line_w=0)
        else:
            mark = dk.box(slide, min(x0, x1), y0-thickness/2, abs(x1-x0),
                          thickness, fill=color, line=color, line_w=0)
        dk.overlap_intent(mark, "开放角目标窗的线段有意围绕候选目标叠放。")
    return slide


def picture(slide, path, x, y, w, h, alt, fit="contain"):
    return dk.picture(slide, str(path), x, y, w, h, fit=fit, alt=alt)


def note(slide, value):
    return dk.speaker_notes(slide, value)


def normalize_mixed_punctuation(prs):
    def fix_tf(tf):
        for p in tf.paragraphs:
            for r in p.runs:
                r.text = _MIXED_PUNCT.sub(
                    lambda m: m.group(1) + _ASCII_PUNCT[m.group(2)], r.text
                )
    def visit(shape):
        if getattr(shape, "has_text_frame", False):
            fix_tf(shape.text_frame)
        if getattr(shape, "has_table", False):
            for row in shape.table.rows:
                for cell in row.cells:
                    fix_tf(cell.text_frame)
        if hasattr(shape, "shapes"):
            for child in shape.shapes:
                visit(child)
    for slide in prs.slides:
        for shape in slide.shapes:
            visit(shape)


def apply_text_defaults(prs):
    """Stamp EA fonts on generated and inherited runs without changing deliberate sizes."""
    dk.retrofit_ea(prs, face=FONT_CN, layouts=True)


def asset(project: Path, relative: str) -> Path:
    p = project / relative
    if not p.exists():
        raise FileNotFoundError(p)
    return p
