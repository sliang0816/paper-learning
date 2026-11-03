# paper-learning

本仓库保存路面抛洒物检测项目移出活动目录的历史资料，方便单独备份和查阅。活动实验项目位于同级 `../vlm-rd-detect/`，现有远端为 <https://gitee.com/shouliangz/vlm-rd-detect>。

本项目远端：<https://github.com/sliang0816/paper-learning>。

## 来源与完整性

- 资料最初于 2026-11-02 整理到主项目 `.local-archive/20261102-cleanup/`。
- 2026-11-03 整体移动至本独立项目的 `20261102-cleanup/`，保留文件内容和内部路径。
- 分离时主项目提交为 `d7a51d9`，共迁移 1,022 个文件，约 560 MB（包括不纳入 Git 的缓存）。
- 移动前后，对按路径排序的全部文件计算 SHA-256 清单，再对清单计算 SHA-256，均为 `84d3ecca3127d26fbde87827754ade906e9e3422b56ef5551b389317477ebec5`。
- 这是独立快照仓库，不继承主项目 Git 历史。曾被主项目跟踪的文件仍可通过主项目历史追溯。

## 内容

| 归档内路径 | 内容 |
|---|---|
| `learning/` | 学习笔记、练习、参考资料 |
| `docs/` | 历史要求、制度文件与说明 |
| `paper/ppt/` | 历史演示稿、构建源文件、渲染与审计材料 |
| `paper/word/` | 旧 Word 文稿 |
| `scripts/` | 历史队列、调度、构建与转换脚本 |
| `.agents/`、`.deck-work/`、`.codex-backups/` | 历史工具资料和备份 |
| `runtime-cache/`、`__pycache__/` | 本机缓存，保留但不提交 Git |

目录均位于 `20261102-cleanup/` 下。历史脚本和文档按原样归档，部分引用仍指向原项目，不保证在本仓库独立运行。查阅脚本不等于需要重新执行训练或安装调度任务。

## GitHub 同步

本地仓库使用 `main` 分支，远端为 `https://github.com/sliang0816/paper-learning.git`。旧本地 Git 元数据已移至项目外备份，本仓库从当前文件重新建立独立历史。后续修改后在本目录提交并推送：

```bash
git add -A
git commit -m "docs: update learning materials"
git push origin main
```

当前文件未发现超过 50 MiB 的单文件，未配置 Git LFS。缓存不随 Git 上传；如需完整本机快照，还需另行备份忽略文件。

资料包含第三方学习 PDF、制度文件和带姓名的历史文稿，未进行完整的公开分发授权或个人信息审查。建议先使用私有仓库；计划公开时逐项核对，第三方原有许可证保持在对应目录，本归档不统一重新授权。
