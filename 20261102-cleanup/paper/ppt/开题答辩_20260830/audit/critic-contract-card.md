# 开题答辩 PPT — CONTRACT CARD

## Purpose

- purpose: 江苏大学硕士学位论文开题答辩，10–15 分钟，现场投影。
- audience: 学院开题评审专家；目标是认可研究问题、技术路线、前期证据和后续计划。
- delivery: presented；25 页（18 页主讲 + 7 页备查）；static，用户明确不要动画。
- deck message: 本课题用固定头宽受控消融和 detector→CLIP 三级证据协议，验证 P2 在当前小目标数据上的可重复收益，同时明确 CLIP 级联与跨域验证的能力边界，并据此补齐确认性验证。
- emotional curve: 场景压力 → 问题聚焦 → 方法清晰 → 证据建立 → 边界收紧 → 计划可信；peak = slide 16。

## Content contracts

- complete takeaway / role / question / beat table: `paper/ppt/开题答辩_20260830/audit/开题PPT内容规划_20260830.md` → “Per-slide content”（25 行，必须整表审阅）。
- complete claim ledger: 同文件 → “Claim ledger”（C01–C26，必须整表审阅，来源为论文页码与本地结构化结果）。
- figure carrying-element ledger: 同文件 → “Figure / table ledger”（F3-size 至 F4.2，必须按 carrying element 审阅）。
- source size: 主论文 58 页；与旧稿及辅助材料合计约 40,088 tokens，按 long-source mode 处理。
- source coverage: 同文件 → “Source-coverage map”；built-around / summarised / cut 为已批准取舍。
- composed-line triage: `/home/bornshine/Downloads/开题答辩_20260830/trace_composed.json`；269 行中 149 行近原文、120 行为作者重述，内容审查优先核对重述行和列出的数字。
- known forward-looking content: slide 17 的独立确认、跨帧、目标设备为拟开展工作，不是已完成结果。

## Narrative and design contracts

- chosen arc: 双问题—证据收束；rejected: 贡献先行—边界防守（过早进入防守）；可行性证据阶梯（更像中期汇报）。
- concept: “两条证据轨道在边界处收束”——检测线控制变量，语义线逐层加入真实误差，最终在 slide 16 对齐贡献、证据与不宣称。
- concept runners-up: 单纯论文目录式红白汇报；科技感 VLM/HUD 视觉。前者不回答评审问题，后者与校级模板和证据审计气质冲突。
- boldness: balanced+，受江苏大学 v7 锁定模板约束。
- signature move: 双证据轨道与“贡献—证据—不宣称”审计账本；carried_by = slides 6, 14, 16。
- signature proof: signature slide 6 → `render/slide06.png`; complex slide 16 → `render/slide16.png`; data slide 10 → `render/slide10.png`。
- money slide / WOW: slide 16；辅助英雄页为 slides 3、10。
- cover archetype: provided-template campus-band；home skeleton: mixed, split/island plurality。
- rhythm map / form ledger: `paper/ppt/开题答辩_20260830/audit/开题PPT设计规划_20260830.md` → “Deck rhythm” 与 “Form ledger”。
- direction gate: n/a — user required the provided v7 Jiangsu University look; no new direction competition.
- style: locked Jiangsu University v7 red/white academic register; custom look, no preset guards. Guard: no neon/HUD, no decorative gradients, no fake technology imagery.
- interior register: red title rule + footer + page number + faint university watermark/chrome on ordinary interior slides.
- semantic colour: school red = identity/navigation; blue = protocol/structure; teal = supported positive evidence; amber = boundary/to-be-confirmed; grey = neutral/not-supported.
- type tokens: title 24 pt; body 14–19 pt by role; captions 11.5–12.5 pt; CJK `Noto Sans CJK JP`, Latin `Liberation Sans`.
- logo plan: official Jiangsu University mark and campus band are inherited from the user-provided v7 template; no fabricated mark.
- checkpoint motif: labelled twin evidence rails; rail labels explain “检测证据线/语义证据线”, so the device is legible to a stranger.
- motion manifest: slides 1–25 all `static: user opted out`; transitions: none.

## Image and evidence provenance

- slide 1 | Jiangsu University campus band and mark | provided — user (own material).
- slide 3 | test size-distribution source figure | provided — user (own project artifact).
- slide 8 | P2/CBAM architecture source figure | provided — user (own project artifact).
- slide 12 | CLIP pipeline source figure | provided — user (own project artifact).
- slide 18 | reused campus band | provided — user (own material).
- slide 23 | confidence-tradeoff source figure | provided — user (own project artifact).
- no generated or web-downloaded content images.

## Mechanical evidence handed to critics

- final PPTX: `/home/bornshine/Downloads/开题答辩_20260830/朱守亮-开题答辩v8-开题版.pptx`
- renders: `/home/bornshine/Downloads/开题答辩_20260830/render/slide01.png` … `slide25.png`
- lint JSON: `/home/bornshine/Downloads/开题答辩_20260830/lint_report.json` (0 hard layout findings; stats are advisory and must still be judged).
- visual contract: `/home/bornshine/Downloads/开题答辩_20260830/visual-contract.json`; final result `visual-contract-final.json` = PASS.
- composition cues: whitespace 0.39–0.87; colorfulness 0.44–0.78; edge density 0.08–0.18; brightness contrast 0.57–0.84; text density 0.07–0.14; colour harmony 0.55–1.00; layout balance 0.55–0.85.
