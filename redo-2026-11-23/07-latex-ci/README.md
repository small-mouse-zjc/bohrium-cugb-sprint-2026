# latex-ci · LaTeX 编译-修复闭环

把一份 `.tex` 工程真实编成 PDF，把每处问题定位到 `文件:行号`，并交回可继续编辑的源码。
不是"生成一段 LaTeX 文本"，而是"交付一份能编译、能入稿、别人能复现的工程"。

## 它解决什么

LaTeX 任务最常见的两种失败：

1. **编译不过就放弃**：缺一个宏包就交不出 PDF，或干脆判"环境不支持"。
2. **编译过了就以为对**：表格少一列、引用指向空 label，pdflatex 照样零报错出 PDF，
   内容是错的却判满分。

本 Skill 对第 1 种给多引擎回退 + 精准定位，对第 2 种用源码级静态检查兜住。

## 安装与依赖

无 Python 第三方依赖，Python ≥3.8。

可选（有则真编译，无则降级静态模式）：

| 工具 | 用途 | 缺失后果 |
|---|---|---|
| `pdflatex`/`xelatex`/`lualatex` | 编译 | 降级静态检查，状态最高 `partial` |
| `bibtex` | 传统文献 | 引用无法自动收敛 |
| `biber` | biblatex 文献 | 用 biblatex 的模板记 `partial` |
| `pdfinfo`/`pdftotext` | PDF 真实性核验 | 回退为读取 PDF 页对象计数 |

TeX Live 2022 及以上已验证可用。

## 用法

```bash
# 一条命令跑完：清理 -> 编译 -> 解析 -> 定级
python scripts/latex_ci.py --project /app/work/project --main main.tex \
       --outdir /app/output --case /input/case.json --emit-result

# 强制只做静态检查（快速看结构/引用/表格列数问题）
python scripts/latex_ci.py --project /app/work/project --outdir /tmp/chk --static-only

# 指定引擎
python scripts/latex_ci.py --project /app/work/project --engine xelatex
```

产物：`report.json`（完整诊断）、`result.json`（契约格式）、`main.pdf`、`source/`（源码副本）。

## 自带验证

```bash
python examples/selftest.py
```

用临时工程验证四类判定：健康工程判 `success`；缺宏包判 `needs_attention` 并定位到
`\usepackage` 行；永不收敛的 `\ref` 判 `partial`；表格少填一列时 PDF 虽生成但仍判非
`success`。本机实测 13 项断言全通过（TeX Live 2022 + xelatex）。

## 目录

```
SKILL.md                     主文档：触发、流程、定级、边界
scripts/latex_ci.py          主流程编排
scripts/logparse.py          编译日志 -> 结构化错误（文件:行号）
scripts/staticcheck.py       无 TeX 也能跑的语义检查
references/error_catalog.md  20 类报错的处置手册
references/output_contract.md 输出契约与判级硬条件
references/checklist.md      交付自查清单
examples/demo_project/       真实可编译的最小工程
examples/selftest.py         行为断言自检
examples/smoke_input.json    示例输入（非正式案例）
examples/smoke_output.json   示例输出（非正式案例）
```

## 限制

- 不替作者编造文献条目、不虚构页数、不补造模板必填内容。
- 文风、章节组织、图表设计由 Agent 结合材料决定，本 Skill 只保证"能编译、结构对、可复核"。
- 静态检查是启发式：`\newcommand` 宏展开后的列数、动态拼接的 label 可能漏判，
  有 TeX 时以真实编译日志为准。
