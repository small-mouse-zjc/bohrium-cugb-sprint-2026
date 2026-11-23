---
name: latex-build-guard
description: LaTeX 写作与编译。用于按模板编写/修复 LaTeX 工程、真实编译、把报错定位到文件行号、交付 PDF 与可编辑源码。
---

# latex-build-guard（冲刺版）

## 先读什么

1. `/input/task.md`：确认模板、主文件、编译引擎、要改的章节、参考文献/图表要求。
2. `/input/case.json`：取 `case_id`、`project_dir`、`files`、`main_tex`、`target`。如果只有文件内容，先把它们原样落到 `/app/work/project`，不要凭记忆补文件。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.compiled_pdf` 指向真实编译出的 PDF；`result.latex_source` 是可编辑工程。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "latex_source": {"main_tex": "main.tex", "files": ["..."]},
    "compiled_pdf": {"path": "/app/output/main.pdf", "pages": 8, "bytes": 123456, "compile_ok": true},
    "pdf_text_check": {"ok": true, "backend": "pdftotext", "chars": 500},
    "compile": {"engine": "xelatex", "errors": [], "missing_files": []},
    "changes": [{"file": "main.tex", "reason": "修 \\ref 未定义"}],
    "artifacts": {"pdf_path": "/app/output/main.pdf", "source_main_tex": "/app/output/main.tex"}
  },
  "evidence": [{"error": "Undefined control sequence", "file": "main.tex", "line": 42, "fix": "..."}],
  "uncertainty": [{"issue": "环境无 TeX", "action": "partial"}]
}
```

## 工作流（最多 4 步）

1. **落盘工程**：把 case 里的文件原样写入 `/app/work/project`；保存一份 `baseline.diff` 或文件副本。
2. **先编译一次**：跑

```bash
python scripts/compile_latex.py /app/work/project --main main.tex --outdir /app/output
```

   记下 `compile_ok`、`errors`、`missing_files`、`pages`，以及 `bib_ok` / `references_ok`。脚本在检测到 `\bibliography` 或 `\addbibresource` 时会自动跑 `bibtex`/`biber`，不要手工跳过；引用未收敛（`[?]`、undefined refs）时只能按 `partial` 处理。**不要先静态猜错，先让 TeX 报。**
3. **修一轮、编一轮**：按 `file:line` 修；每次修完立即重编。常见修法：缺包、缺文件、未定义引用、中文引擎、表格列数、数学环境未闭合。
4. **交付**：把编译输出的 `pdf`/`source_dir`/`pdf_text_check` 映射到 `result.compiled_pdf`、`result.latex_source`、`result.pdf_text_check`，`artifacts.pdf_path` 指向真实 PDF；`compile_ok=true`、`pages>0`、`pdf_text_check.ok` 不为 `false` 才算 success，否则 `partial` 并说明卡在哪。最后跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field latex_source
```

## 不能造假

- 没编译却写“编译通过”；
- 拿旧 PDF/空 PDF 冒充；
- 改坏模板后不重编；
- 把 `no_latex_compiler` 写成 success。

## 评分关注

真实 PDF、真实页数、可读文字、可编辑源码、报错修复链。先修到能编译，再谈排版美化。

