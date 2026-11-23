# latex-build-guard（冲刺版）

LaTeX 写作与编译作品：先把工程真实落盘，再真实编译，按 `file:line` 修错，最后交付 PDF 与可编辑源码。

- 输入：`/input/task.md` + `/input/case.json`（`project_dir`/`files`、`main_tex`、`target`）。
- 主产物：`result.compiled_pdf`（真实 PDF）+ `result.latex_source`（可编辑工程）+ `result.pdf_text_check`。
- 运行：

```bash
python scripts/compile_latex.py /app/work/project --main main.tex --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field latex_source
```

- 判定：无真实编译、`pages=0`、PDF 文本为空、`compile_ok` 与日志不符，只能 `partial`；环境无 TeX 必须如实说明。
- 参考文献：源码含 `\bibliography`/`\addbibresource` 且工程内有 `.bib` 时，脚本会在首轮编译后自动跑 `bibtex`（biblatex 用 `biber`）再编译；引用/交叉引用未收敛（PDF 里出现 `[?]`、undefined refs、仍提示 Rerun）时 `compile_ok=false`，只能交 `partial`。
- 边界：不用旧 PDF/空 PDF/截图冒充；`latex_engine.py` 只做静态检查，编译结论以 `compile_latex.py` 的日志为准。

设计取向：能编译是第一目标，排版美化排在后面；错误定位必须落到文件行号。

