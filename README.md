# 玻尔 CUGB 挑战赛 · 冲刺版（2026-11-23）

这是一套独立存放的 10 题“能冲高”版本。原 v8 工作副本保持不动；本目录只做新作品，不向平台提交。

## 设计取向

- **task-first**：先读 `/input/task.md` 与 `/input/case.json`，按真实结构办事，不假设固定字段。
- **artifact-first**：每题先交一个真实主产物（译文/润色稿/正文/引言/方法章节/笔记/PDF/阅读文本/纳米出版物/图谱），检查表只是附件。
- **薄 SKILL**：每题 2–3K，最多 4 步；硬规则 3–5 条；软检查只做 warning。
- **不替 Agent 成稿**：脚本保留解析、编译、核验、落盘能力；正文由 Agent 写，不走模板生成器成稿。

## 10 题

| 题 | 作品 | 主产物 | 包内文件 |
|---|---|---|---|
| 01 | translation-guard | `translations` 真实译文 | 13 |
| 02 | academic-polish-source-preserving | `polished_text` 保源润色稿 | 14 |
| 03 | citation-integrity | `editable_manuscript` + `bibliography` | 13 |
| 04 | intro-gap-architect | `introduction_draft` 四部件成稿 | 16 |
| 05 | methods-repro-guard | `method_experiment_draft` 方法章节 | 13 |
| 06 | paper-note-archivist | `structured_notes` 逐节笔记 | 10 |
| 07 | latex-build-guard | `compiled_pdf` + `latex_source` | 14 |
| 08 | pdf-layout-parse | `reading_text` 还原正文 | 12 |
| 09 | nanopub-archivist | `nanopublications` 断言集 | 12 |
| 10 | knowledge-graph-builder | `graph` + `query_answers` | 10 |

## GitHub

独立仓库：https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026

| 题 | 仓库目录 |
|---|---|
| 01 | [01-translation-guard](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/01-translation-guard) |
| 02 | [02-academic-polish](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/02-academic-polish) |
| 03 | [03-citation-integrity](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/03-citation-integrity) |
| 04 | [04-intro-gap-architect](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/04-intro-gap-architect) |
| 05 | [05-methods-repro-guard](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/05-methods-repro-guard) |
| 06 | [06-paper-note-archivist](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/06-paper-note-archivist) |
| 07 | [07-latex-build-guard](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/07-latex-build-guard) |
| 08 | [08-pdf-layout-parse](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/08-pdf-layout-parse) |
| 09 | [09-nanopub-archivist](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/09-nanopub-archivist) |
| 10 | [10-knowledge-graph-builder](https://github.com/small-mouse-zjc/bohrium-cugb-sprint-2026/tree/main/10-knowledge-graph-builder) |

## 自检

10 题 `examples/selftest.py` 全部通过（01 39/39、02 15/15、03 35/35、04 45/45、05 23/23、06 23/23、07 35/35、08 28/28、09 25/25、10 40/40）。自检只证明引擎行为，不代表平台分数。

## 边界

- 07 本机无 TeX 时只能走 `no_latex_compiler`，不能宣称编译成功。
- 08 本机无 PyMuPDF，`pdftotext` 回退未在真实 PDF 上验证。
- 09/10 的硬门槛需在真实案例上继续观察。
- 旧 v8 的 10 题自检与 GitHub 状态不适用于本目录。
