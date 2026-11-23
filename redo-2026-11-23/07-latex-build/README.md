# 07 · LaTeX 写作与编译（latex-build）

可编辑源码 + 真实编译 PDF，引用收敛，报错如实记录。

- **主产物**：`compiled_pdf` + `latex_source`。
- **辅助**：`pdf_text_check`、`compile`（引擎/报错/缺文件）。
- **交付文件**：`main.pdf`、`main.tex`。
- **校验**：`scripts/guard.py` 查 PDF 存在且非空、页数 >0、`compile_ok` 与真实产物一致、文本抽取有字符。
- **边界**：无 TeX 环境只能 `partial`；不得用旧 PDF/空 PDF/截图冒充。
