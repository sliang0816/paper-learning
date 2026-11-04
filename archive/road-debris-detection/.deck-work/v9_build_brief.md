# v9 deck build brief

## Fixed contract

- 33 slides, 16:9, static, Chinese live opening-proposal defense.
- Template: `/Users/shouliang/Documents/mac_pro/Personal/研究生/开题/和巳程_开题报告.pptx` opened with DeckKit `open_template`.
- Shared style: `paper/ppt/开题答辩_20261013/style.py`.
- Keep reference-master chrome. Do not use rounded cards, gradients, shadows or decorative AI art.
- Every slide must have Chinese speaker notes. Slides 28–33 are Q&A backup; slide 28 must call `dk.design_intent(..., role="appendix", ...)`.
- Never invent mentor, college, major or defense date. Cover only shows `朱守亮`, `硕士学位论文开题答辩`, `江苏大学`.
- Main claim boundary: opening-defense evidence is sufficient; the thesis experiments are not all complete.

## Verified project facts

- Fixed-monitor road-debris scenario; two bottlenecks: `找不到` (small-object localization) and `认不对` (semantic naming).
- Dataset: 4,651 images, 6,108 boxes, 8 classes. Detector trains 6 classes; GL/RU are reserved for semantic/open-set evaluation.
- Test GT boxes: 862 total, 720 small, 142 medium, 0 large.
- Fixed-head controlled experiment: P2 × CBAM, 2×2 configurations, 5 seeds each.
- P2: mAP50 `+2.71±1.65 pp`, 5/5 positive; small AP50 `+4.01±1.58 pp`, 5/5 positive.
- CBAM has no stable independent gain; interaction `−1.53±3.12 pp`.
- RAOD external positioning: Precision `+1.34±0.70 pp`, AP50-95 `−1.70±2.22 pp`.
- CLIP val GT-box GL/RU top-1 `50.91%`.
- 230-image retrospective confirmation: confidence-only F1 `39.44%`; joint confidence+margin F1 `32.45%`.
- Frozen open-vocabulary baselines: YOLO-World F1 `0%`; Grounding DINO F1 `0.80%`.
- Prototype on RTX3090: `77.41 ms/image`, `12.91 FPS`, P95 `121.94 ms`.
- 26 formal training runs: 21 have direct optimizer logs, 5 logs missing.
- Incomplete: strict independent same-domain confirmation; reliable video/camera/time metadata; target edge device; historical-test full closure for open vocabulary; five optimizer logs; broad cross-camera/road generalization.

## Existing project figures

- `paper/figures/fig_ch3_size_distribution.png`
- `paper/figures/fig_framework_overview.png`
- `paper/figures/fig_p2cbam_architecture.png`
- `paper/figures/fig_clip_pipeline.png`
- `paper/figures/fig_ch3_size_stratified_map.png`
- `paper/figures/fig_qualitative_pipeline_cases.png`
- `paper/figures/fig_error_analysis.png`

## Section allocation

- `section_a.py`: slides 1–13.
- `section_b.py`: slides 14–24.
- `section_c.py`: slides 25–33.
- Each module exposes `build(prs, project: Path, root: Path)` and appends slides in order.

## Slide map

1 cover — title and presenter only; campus banner + white curve, official logo.
2 agenda — seven numbered sections.
3 divider 01 — 选题依据.
4 background — fixed cameras capture the road continuously, but distant debris occupies few pixels and naming requires semantics.
5 two bottlenecks — 找不到 / 认不对; show size distribution and the same candidate target window.
6 divider 02 — 国内外研究现状.
7 related-work map — small-object detection / anomaly detection / VLM; each solves part only.
8 gap — structural gains lack controlled attribution; semantic capability lacks end-to-end error decomposition.
9 divider 03 — 研究目标与内容.
10 objectives/boundary — improve localization and diagnose naming under fixed monitoring; do not claim deployment/generalization complete.
11 content 1 — fixed-head P2×CBAM 2×2×5-seed experiment.
12 content 2 — GT-box → detector-box → frozen-rule, three-level semantic diagnosis.
13 content 3 — audit trace, error decomposition and boundary validation.
14 divider 04 — 技术路线与研究方案.
15 overall route — detection → candidate box → semantic naming → audit/boundary, use `fig_framework_overview.png`.
16 detection scheme — use `fig_p2cbam_architecture.png`; fixed head width, 2×2, 5 seeds.
17 semantic scheme — use `fig_clip_pipeline.png`; GT/detector/frozen-rule levels.
18 key dependencies — independent data, temporal metadata, target edge device are prerequisites for full closure.
19 divider 05 — 创新点与难点.
20 innovation/difficulty — controlled attribution + layered diagnosis; explicitly state claim/non-claim boundary.
21 divider 06 — 前期基础与计划.
22 detection basis — use `fig_ch3_size_stratified_map.png`; P2 5/5 positive, +2.71±1.65 pp mAP50, +4.01±1.58 pp small AP50; CBAM not stable.
23 semantic basis/boundary — use `fig_qualitative_pipeline_cases.png`; CLIP GT-box 50.91%, confidence-only better than joint retrospective rule; open-vocab baselines weak.
24 schedule — three relative phases: independent confirmation/audit completion; temporal/open-set study if metadata supports; edge-device validation after device is fixed.
25 divider 07 — 参考文献.
26 references — concise two-column list from local paper bibliography; no invented citations.
27 thanks — campus photo bookend, `恳请各位老师批评指正`.
28 backup — internal repeated seeds ≠ independent confirmation.
29 backup — full 2×2×5-seed result/audit table; 21/26 logs direct, 5 missing.
30 backup — RAOD external positioning; precision up, AP50-95 down.
31 backup — error bottleneck 59→28→17, use `fig_error_analysis.png` and explain conditional nature.
32 backup — YOLO-World vs Grounding DINO frozen baseline negative results.
33 backup — RTX3090 prototype speed and edge-device boundary.

## Notes tone

Formal, concise, 100–180 Chinese characters on content slides; dividers 1–2 sentences. Explain what the visual proves and what it does not prove. Backup notes say when to use the slide in Q&A.
