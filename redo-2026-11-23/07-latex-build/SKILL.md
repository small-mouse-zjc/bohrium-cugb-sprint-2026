---
name: latex-build
description: LaTeX 写作与编译。写出可编辑 TeX 源码，在有 TeX 的环境真实编译出 PDF，跑通引用与文献处理，交付 PDF + 源码；编译失败要定位报错，禁止用旧 PDF、空 PDF 或截图冒充编译产物。
---

# latex-build

## 读什么

1. `/input/task.md`：文档类型（论文/摘要/报告）、篇幅、模板要求。
2. `/input/case.json`：正文素材、参考文献（`references` / `.bib` 条目）、图表。先确认素材齐全再写源码。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "latex_source": "\\documentclass{article} ...",
    "compiled_pdf": {"path": "/app/output/main.pdf", "pages": 3,
                     "bytes": 182430, "compile_ok": true},
    "pdf_text_check": {"ok": true, "backend": "pdftotext", "chars": 4120},
    "compile": {"engine": "xelatex", "errors": [], "missing_files": [],
                "log_tail": "末轮编译日志摘要"},
    "artifacts": {"pdf_path": "/app/output/main.pdf",
                  "source_main_tex": "/app/output/main.tex"}
  },
  "evidence": [{"anchor": "编译日志", "note": "引擎/轮次/引用收敛"}],
  "uncertainty": [{"issue": "缺字体/缺宏包/缺文献条目"}]
}
```

## 怎么做（5 步）

1. **写源码**：搭好 `main.tex`，正文、公式、图表、引用就位；有 `.bib` 就用 `\bibliography` / `biblatex`。
2. **真实编译**：在有 TeX 的环境按顺序跑——引擎（pdflatex/xelatex/lualatex）→ bibtex 或 biber → 再跑引擎两遍，让引用与目录收敛。把引擎、报错、缺文件记进 `compile`。
3. **校验 PDF**：确认 PDF 存在、非空、页数 >0；抽取文本看字符数，记进 `pdf_text_check`。
4. **报错处理**：编译失败先看日志首条错误，补宏包/字体/条目；补不齐的进 `uncertainty`，标 `partial`。
5. **落盘核验**：写 `main.tex`、`main.pdf`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 无 TeX 环境却写 `compile_ok: true`；
- 交旧 PDF、空 PDF、截图当编译产物；
- 跳过 bibtex/biber，引用留 `[?]` 仍判成功；
- 编造页数、字节数、文本字符数。

## 评分关注

源码可编辑、PDF 真实可读、引用收敛、报错如实记录。先编译成功，再排版美观。
