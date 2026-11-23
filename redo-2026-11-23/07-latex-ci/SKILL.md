---
name: latex-ci
description: LaTeX 编译-修复闭环。把 .tex 工程真实编译成 PDF：多轮跑引擎与 bibtex/biber，日志解析到 文件:行号，用"引用是否收敛"判成败，并捕获 pdflatex 静默放过的表格列数/引用错配；无 TeX 环境降级为源码级定位，不谎报编译通过。
---

# latex-ci

面向"按模板交付一份能编译、能入稿、能被别人复现的 LaTeX 工程"。核心是一条命令跑完
探测→编译→解析→定级，把每处问题落到 `文件:行号`，并给出可直接执行的修法。

## 触发

输入里出现 `.tex` / `.bib` / 论文模板 / "编译报错" / "PDF 生成" / "引用 [??]" 时使用。
不用于：只用 Word/Markdown 的写作任务；纯 PDF 阅读（那是文档解析题）。

## 读什么

1. `/input/task.md`：模板类（article/IEEEtran/ctex...）、要改的章节、引擎要求、篇幅。
2. `/input/case.json`：`case_id`、工程文件（`files`/`project_dir`）、`main_tex`、`target`、
   以及可能的 `output_contract` / `required_fields`。
3. 有工程文件就**原样落盘**到 `/app/work/project`，禁止凭记忆重建源码或补造文献条目。

`case.json` 带 `output_contract` 时，最终 `result.json` 必须包含其中每个字段。

## 一条命令跑闭环

```bash
python scripts/latex_ci.py --project /app/work/project --main main.tex \
       --outdir /app/output --case /input/case.json --emit-result
```

它做四件事：

1. **清旧产物**：删掉工程里遗留的 `.aux/.log/.bbl/*.pdf`，从机制上排除"拿旧 PDF 冒充"。
2. **多轮编译**：引擎 →（有 `\bibliography` 跑 bibtex / 有 `\addbibresource` 跑 biber）→ 再引擎，
   最多 4 轮；用 `-file-line-error` 让每条错误带 `文件:行号`。
3. **判收敛**：不是看退出码，而是看日志里 `undefined references` 是否消失。第一轮的 `?!`
   属正常（标签后置），第二三轮仍在就是真问题。
4. **补静态检查**：编译通过后仍跑源码级检查，捕获 pdflatex 静默放过的错（见下）。

输出 `report.json`；加 `--emit-result` 同时写契约格式的 `result.json`。

## 为什么还要静态检查

实测：`\begin{tabular}{lll}` 只填两列数据时，pdflatex **零报错**、正常出 PDF，第三列是空白。
只看"编译通过"会把错内容判成满分。所以编译后必须再跑：
表格列数、`\ref`↔`\label`、`\cite`↔`.bib` key、环境配对、`$` 配对、命令与宏包声明。
这些在无 TeX 的机器上同样能定位，正是降级模式的价值。

## 修复循环

读 `report.json` 的 `result.fix_plan`，每条给了 `file/line/type/action`。按类型处理：

| type | 常见根因 | 怎么修 |
|---|---|---|
| `missing_package` | 发行版没装该宏包 | 换等价包或删非必需用法；不要留一条装不上的依赖 |
| `missing_font` | 字体族不在镜像里 | 换已装字体，或用 `ctex`/`fontspec` 已带字体 |
| `math_mode` | `$` 未闭合 | 补 `$`，注意 `\$` 是转义 |
| `alignment` | `&` 多于列声明 | 改列声明或删多余 `&` |
| `alignment_silent` | `&` 少于列声明 | 补单元格；这类编译不报错，必须主动修 |
| `undefined_ref` | 指向不存在的 label | 补 `\label` 或改正 key |
| `undefined_cite` | bib 里没有该 key | 补条目或改 key，不许留 `[?]` |
| `undefined_command` | 宏包没加载 | 按提示补 `\usepackage` |
| `undefined_env` | begin/end 交叉 | 改嵌套顺序 |
| `runaway` / `brace` | 花括号失衡 | 从报错行往前找第一个未配对 `{` |
| `fatal` | 级联中断 | 先修它前面第一条 `!` |

修完立刻重跑同一条命令；`fix_plan` 空了再进入交付。

## 定级（硬规则，不许放宽）

- `success`：`compile_ok=true`、`pages>0`、`bytes>0`、`pdf_text_check.ok=true`、
  `converged=true`、`fix_plan` 为空。
- `partial`：PDF 出来了但引用未收敛、或有 `alignment_silent` 类静态错、或无 TeX 只做了静态检查。
- `needs_attention`：没出 PDF（缺包/缺类/致命错误），必须给首因和修法。
- 无 TeX 时**只能** `partial`，并在 `uncertainty` 写明"未做真实编译"，不许写 `compile_ok: true`。

## 不能造假

- 没编译却写编译通过；拿旧 PDF / 空 PDF / 截图当产物；编造页数、字节数、字符数。
- 把 `no_latex_compiler` 写成 success；把 `[?]` 留着还判成功。
- 补造 `.bib` 条目、虚构文献、篡改模板必填项来凑"完整"。

## 边界

- `biber` 缺失而模板用 `biblatex`：记为 `partial`，在 `uncertainty` 说明，不伪造参考文献。
- 模板 `.cls` 缺失：先找同族模板替代并如实记录替换；替代不了就 `needs_attention`。
- 中文字体缺失：优先 `xelatex` + `ctex`；仍失败则 `partial` 并写明缺哪个字体。
- 只能在有写权限的目录构建；构建产物与源码都落到 `/app/output`，源码目录保持可继续编辑。
