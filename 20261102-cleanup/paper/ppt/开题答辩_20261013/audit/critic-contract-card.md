# 开题答辩 v9 — CONTRACT CARD

## Purpose

- purpose: 江苏大学硕士学位论文开题答辩，11–14 分钟，现场投影。
- audience: 学院开题评审专家；目标是认可研究问题、技术路线、前期证据和后续计划，不把开题证据误写成论文实验全部完成。
- delivery: presented；33 页，其中 1–27 为正式汇报，28–33 为答辩备查；static，用户已确认无动画。
- deck memory sentence: 固定监控中的路面抛洒物需要先解决小目标定位，再诊断候选区域命名；现有受控实验支持继续验证 P2，但开放词汇、严格独立确认和目标设备部署仍是开题后的工作。
- emotional curve: 场景压力 → 两类瓶颈 → 研究缺口 → 受控路线 → 前期证据 → 边界收紧 → 依赖式计划；peak = slide 22。

## Content contracts

- complete per-slide takeaway / role / evidence table: `paper/ppt/开题答辩_20261013/.deck-gates.json` → `content.slides`，共 33 行，必须整表审阅。
- source size: 论文草稿 6 章、项目总结、15 个核心结构化结果/审计来源以及 51 条参考文献；按 long-source mode 处理。
- source coverage: slides 4–8 交代场景、三条相关路线与证据缺口；slides 10–13 定义两个目标和三项内容；slides 15–18 给出路线与依赖；slides 20–24 只主张已有受控证据并明确后续边界；slides 28–33 为审计、外部验证、错误链、开放词汇负结果和速度备查。
- composed-line triage: `paper/ppt/开题答辩_20261013/audit/trace_composed.json`；383 行中 183 行近原文、200 行为作者重述。内容审查优先核对重述行和 21 条数字/标识符提示；其中学校英文名、文件名和参考文献英文题名属于来源匹配器的可预期提示，仍需人工确认。
- known forward-looking content: 严格独立同域确认、可靠时间/相机元数据、开放词汇闭环、目标边缘设备实测与广泛跨道路泛化均未完成，不得写成成果。

### Claim ledger — load-bearing rows

| ID | Slides | Claim | Primary local evidence |
|---|---:|---|---|
| C01 | 5 | test 集 862 个 GT 框，其中 small 720、medium 142、large 0，small 占 83.5% | `results/dataset_audit.json`; `paper/figures/fig_ch3_size_distribution.png` |
| C02 | 11,16,22,29 | 固定分类头隐藏宽度 128，P2×CBAM 2×2×5 seeds 共 20 次主实验 | `results/head_width_control_summary_5seed.md` |
| C03 | 22,29 | P2 对 mAP50 的配对主效应 +2.71±1.65 pp，5/5 为正 | 同上 |
| C04 | 22,29 | P2 对 small AP50 的配对主效应 +4.01±1.58 pp，5/5 为正 | 同上 |
| C05 | 22 | CBAM 未显示稳定独立收益；交互项 −1.53±3.12 pp | 同上 |
| C06 | 23 | GT 框 GL/RU top-1 为 50.91% | `paper/drafts/ch4_clip.md` 及对应结构化结果 |
| C07 | 23 | 230 图回溯内部确认：conf-only F1 39.44%，joint F1 32.45% | `paper/drafts/ch4_clip.md`; 回溯规则结果 |
| C08 | 23,32 | 冻结开放词汇内部确认：YOLO-World F1 0%，Grounding DINO F1 0.80% | 两个 `results/open_vocab/*internal_confirm_v1/summary.json` |
| C09 | 29 | 26 次正式训练纳入审计；21 次有直接 optimizer 日志，5 次缺失 | `results/training_argument_audit.md` |
| C10 | 30 | RAOD：Precision +1.34±0.70 pp；AP50-95 −1.70±2.22 pp | `results/external_validation/raod_test_v1/summary.md` |
| C11 | 31 | 历史 test 条件诊断为 59 个预留类真值 → 28 个匹配候选 → 17 个正确命名 | `paper/drafts/ch4_clip.md`; `paper/figures/fig_error_analysis.png` |
| C12 | 33 | RTX 3090 旧 P2+CBAM seed0 原型：77.41 ms/图、12.91 FPS、P95 121.94 ms | `results/full_pipeline_benchmark.json` |

### Figure carrying elements

- slide 5: `fig_ch3_size_distribution.png`; carrying element = small 720 / 862 = 83.5%，不是装饰背景。
- slide 15: `fig_framework_overview.png`; carrying element = 检测候选框交给语义命名并由审计/边界收束。
- slide 16: `fig_p2cbam_architecture.png`; carrying element = 仅 P2 与 CBAM 变化，Detect 头宽固定 128。
- slide 17: `fig_clip_pipeline.png`; carrying element = GT 框、检测框、冻结规则三层证据，不是三个模型。
- slide 22: `fig_ch3_size_stratified_map.png`; carrying element = 早期 3-seed 图作视觉证据，右侧文字必须以最终 5-seed 汇总为准。
- slide 23: `fig_qualitative_pipeline_cases.png`; carrying element = 定位、语义和背景误报三类瓶颈；右侧数值来自不同协议，不得写成单一同队列比较。
- slide 31: `fig_error_analysis.png`; carrying element = 59→28→17 只用于历史 test 条件诊断。

## Narrative and design contracts

- chosen arc: 开题标准型“问题—路线—证据—边界—计划”；rejected: 成果先行型（像中期汇报）、贡献先行型（过早放大尚未闭环的结论）。
- concept: “同一微小目标先被框住再被命名”，以开放角目标窗连接定位与语义两条证据轨；runners-up: 完整道路处置链、实验审计账本。
- boldness: conservative，正式开题和用户锁定参考模板共同要求克制。
- signature move: slide 22 用开放角目标窗切入 small 目标证据图带并承载 5/5；carried_by = slides 5,15,22。
- signature proof: signature slide 22 → `render/slide22.png`; complex slide 15 → `render/slide15.png`; problem slide 5 → `render/slide05.png`。
- money slide / WOW: slide 22；辅助关键页 slides 5、15、23。
- cover archetype: provided-template campus-band；home skeleton: mixed diagrams / comparisons / evidence pages / chapter breathers。
- direction gate: Mode A faithful mimic，用户确认参照江苏大学红白学术模板，内容改为本项目现状。
- style: custom locked Jiangsu University red/white register；guard = 不使用霓虹 HUD、装饰渐变、虚构科技图片或不真实部署场景。
- interior register: 淡红标题圆、细红标题线、底部校红页脚与英文校名，普通内页一致延续。
- semantic colour: school red = identity / conclusion；blue = detection / protocol；purple = semantic diagnosis；green = supported positive evidence；ochre = boundary / negative result；grey = neutral context。
- type tokens: display 108 pt；titles 23 pt；body mainly 14–18 pt；source 10.5 pt；`Hiragino Sans GB` + Arial / Arial Black。
- logo plan: 官方江苏大学标识与校园横幅继承自用户提供的参考模板，不重绘、不新增假标识。
- checkpoint motif: 开放角目标窗，含义为“当前被检查的候选目标”；首次出现在 slide 4 的道路小目标上，后续只在 slides 5/15/22 作结构性复用。
- motion manifest: slides 1–33 all `static: user opted out`; transitions: none。
- image provenance: 校园照片与校标来自用户参考模板；其余图片均为用户项目图和结果图；没有网络下载或生成式内容图片。

## Mechanical evidence

- final PPTX: `paper/ppt/开题答辩_20261013/朱守亮-开题答辩v9-参考模板版.pptx`
- renders: `paper/ppt/开题答辩_20261013/render/slide01.png` … `slide33.png`
- contact sheets: `render/contact_01.png` … `contact_03.png`
- lint JSON: `audit/lint_report.json`; build-time lint = 0 critical，模板母版相关和统计性提示仍需人工判断。
- component audit: `audit/components.json`; hand-built slides 4/13/24 are deliberate template-locked diagrams, reason recorded in `.deck-gates.json`.
- visual contract: `audit/visual_contract.json` = PASS，4/4 fragile local relationships clear by at least 0.12 in。
- preflight: 33/33 slides have speaker notes；static by choice；all fonts resolve locally；no placeholder/TODO/meta text。
