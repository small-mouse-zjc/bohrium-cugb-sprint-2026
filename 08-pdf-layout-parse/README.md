# pdf-layout-parse（冲刺版）

文献 PDF/版面解析作品：从真实 PDF 或带坐标版面还原阅读顺序、章节、表格、公式、图表标题，输出可校对的正文。

- 输入：`/input/task.md` + `/input/case.json`（`pdf_path` 或 `layout`、`pages`、`target_sections`）。
- 主产物：`result.reading_text`（可读正文）+ `result.sections`/`tables`/`layout`。
- 运行：

```bash
python scripts/pdf_layout_engine.py extract /input/paper.pdf > /app/work/layout.json
python scripts/pdf_layout_engine.py pipeline /app/work/pipeline_input.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field reading_text
```

- 判定：双栏顺序错、表格/公式/题注静默丢失、页码不可回查，都不能算 `success`；无解析后端只能 `partial`。
- 边界：不凭标题生成正文；`pdftotext` 回退只保证文本，不保证复杂版面。

设计取向：阅读顺序和结构完整性是主指标；先还原，再谈漂亮。

