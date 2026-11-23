# 玻尔 CUGB 挑战赛 · 豆包重做版（2026-11-23）

这是按豆包自己的思路重写的一套 10 题 Skill 包。旧冲刺版与 v8 副本均保留不动；本目录只做本地重做，**不再向平台提交**（10 个题目额度已在上一轮用完）。

## 我对这套题的判断

平台加载 Skill 后，真正决定分数的是主产物本身：译文顺不顺、润色保不保源、引用对不对、章节像不像人写的、PDF 真不真、解析读不读得通、断言能不能回查、图谱能不能沿边 trace。脚本只该在"机器能硬判、不能靠嘴说"的地方兜底。

所以这一版相对旧版的取舍：

- **SKILL 一页讲清**：读什么 → 产出什么 → 哪几条不能造假 → 怎么自检。不堆状态枚举、不抄字段字典。
- **脚本做减法**：每题一个轻量 `guard.py`，只负责落盘、结构校验和硬事实检查（覆盖、引用存在、数值回指、PDF 非空、证据逐字匹配）；不替 Agent 写正文，不做模板生成器成稿。
- **主产物优先**：先把真实主产物交出来，证据和未决项附在后面；辅助字段只在契约要求时保留。
- **判断交给 Agent**：语气、详略、章节组织由 Agent 结合真实材料决定；脚本不设"必须凑够几条"的硬门槛，软缺口只进 `uncertainty`。

## 10 题

| 目录 | 题目 | 主产物 |
|---|---|---|
| 01-translation-guard | 阅读03 文献翻译 | `translations` 真实译文 |
| 02-academic-polish | 写作02 学术语言润色 | `polished_text` 保源润色稿 |
| 03-citation-integrity | 写作04 引用管理 | `editable_manuscript` + `bibliography` |
| 04-intro-architect | 写作08 引言与相关工作 | `introduction_draft` 四部件成稿 |
| 05-methods-guard | 写作09 方法与实验 | `method_experiment_draft` 方法章节 |
| 06-note-archivist | 阅读10 文献总结与笔记 | `structured_notes` 逐节笔记 |
| 07-latex-build | 写作13 LaTeX 写作与编译 | `compiled_pdf` + `latex_source` |
| 08-pdf-layout | 阅读01 文献文档解析 | `reading_text` 还原正文 |
| 09-nanopub-archivist | 阅读14 Nanopublication | `nanopublications` 断言集 |
| 10-kg-builder | 阅读15 文献知识图谱 | `graph` + `query_answers` |

## 包内结构（每题一致）

```
SKILL.md                     操作手册：读什么、写什么、不能造假、自检
README.md                    本题一句话说明与字段口径
scripts/guard.py             轻量校验：结构 + 硬事实 + 产物落盘
examples/selftest.py         最小自检，只跑核心硬规则
examples/smoke_input.json     最小输入样例
examples/smoke_output.json    期望输出骨架
references/output_contract.md 本题输出字段与硬规则（与平台契约对齐）
```

## 边界

- 自检只证明校验引擎行为，不代表平台分数；真实三案例由平台 Agent 加载后跑。
- 07 无 TeX 环境时只能降级 `partial`，不能宣称编译成功。
- 08 无 PyMuPDF 时走 `pdftotext` 回退，双栏/表格顺序需人工复核。
- 本目录未发布 GitHub；如需发布，再单独建分支或新仓库。
