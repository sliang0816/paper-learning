#!/usr/bin/env python3
"""Build the 33-slide Jiangsu University opening-proposal deck."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
SKILL_SCRIPTS = PROJECT / ".agents/skills/slide-maker/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
sys.path.insert(0, str(ROOT))

import deckkit as dk
from style import apply_text_defaults, normalize_mixed_punctuation
import section_a
import section_b
import section_c

TEMPLATE = Path("/Users/shouliang/Documents/mac_pro/Personal/研究生/开题/和巳程_开题报告.pptx")
OUT = ROOT / "朱守亮-开题答辩v9-参考模板版.pptx"


def main():
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Reference template not found: {TEMPLATE}")
    prs = dk.open_template(TEMPLATE)
    section_a.build(prs, PROJECT, ROOT)
    section_b.build(prs, PROJECT, ROOT)
    section_c.build(prs, PROJECT, ROOT)
    if len(prs.slides) != 33:
        raise RuntimeError(f"expected 33 slides, got {len(prs.slides)}")
    normalize_mixed_punctuation(prs)
    apply_text_defaults(prs)
    dk.declare_delivery(OUT, "presented", builds="static")
    dk.lint_layout(prs, strict=True)
    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
