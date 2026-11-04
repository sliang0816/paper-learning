# Paper Learning · 论文阅读、解析与学习

独立的论文学习项目：从论文原文出发，整理模型原理、公式与图解，通过答疑和小型代码练习验证理解。目前以计算机视觉、目标检测和视觉语言模型为主，资料最初来自路面抛洒物检测课题，后续在这里持续维护。

## 从这里开始

| 你想做什么 | 入口 |
|---|---|
| 系统阅读模型与论文解析 | [模型详解目录](learning/模型详解/README.md) |
| 查找论文原文 | [论文清单与本地 PDF](learning/模型详解/papers/论文清单.md) |
| 接着上次的进度读 | [阅读进度](learning/模型详解/阅读进度.md) |
| 回顾问题和待理解的概念 | [答疑总目录](learning/模型详解/答疑记录.md)、[待读清单](learning/模型详解/待读清单_暂留概念.md) |
| 把公式落实为代码 | [学习资料与手写练习](learning/README.md) |
| 新增一篇论文笔记 | [笔记模板](templates/paper-note.md)、[维护约定](docs/维护约定.md) |
| 查阅旧课题文稿、制度与脚本 | [历史资料](archive/road-debris-detection/README.md) |

建议沿着“原文 → 模型解析 → 答疑 → 小型练习 → 更新阅读进度”的顺序学习。现有 `00_必读` 按原课题相关性组织，可按自己的学习目标选择，不代表所有方向都必须读完。

## 目录结构

```text
paper-learning/
├── learning/                       # 持续维护的笔记、原文、图解与练习
│   ├── 模型详解/                    # 分类解析、答疑、阅读进度
│   │   ├── papers/                 # 论文 PDF 与清单
│   │   └── figures/                # 图解与论文原图
│   └── exercises/                  # 五项手写练习
├── templates/                      # 新笔记模板
├── docs/                           # 本项目的维护与迁移说明
└── archive/road-debris-detection/   # 原课题的历史资料
```

## 运行学习练习

阅读 Markdown、PDF 和图解无需安装 Python。练习需要安装 PyTorch 的 Python 环境；可复用已有环境，不绑定原实验项目的 Conda 环境名称。在仓库根目录执行：

```bash
python learning/check_environment.py --device cpu
python learning/check_progress.py
```

练习模板尚待手写，进度检查报告未完成是正常状态。完成后可运行 `python learning/check_progress.py --strict` 验收。详细要求见[练习说明](learning/README.md)。

## 项目边界与来源

本仓库维护学习资料和小型练习；正式训练、数据集评估与实验结论在独立的 [vlm-rd-detect 项目](https://gitee.com/shouliangz/vlm-rd-detect) 中维护。本地同级目录如存在，可用于代码对照，但不是阅读本仓库的前提。

旧笔记中的“本项目”“第三章”“创新点”等表述通常指原课题，保留作学习背景，不表示本仓库已经复现对应结果。历史脚本含原机器路径与依赖，归档不代表可以在这里直接运行。

来源、原始快照校验值与目录迁移关系见[迁移记录](docs/迁移记录.md)。第三方 PDF、图件与历史文稿保留原有来源和许可证，不统一重新授权。

仓库远端：<https://github.com/sliang0816/paper-learning>。缓存由 `.gitignore` 排除；本地整理后按需提交并推送。
