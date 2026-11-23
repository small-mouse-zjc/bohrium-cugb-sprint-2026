---
name: pdf-layout-parse
description: 文献 PDF/版面解析。用于从真实 PDF 还原阅读顺序、章节、段落、表格、公式与图表标题，输出可校对的阅读文本和结构 JSON。
---

# pdf-layout-parse（冲刺版）

## 先读什么

1. `/input/task.md`：确认要解析 PDF 还是已有版面 JSON、要哪些结构、是否保留表格/公式、输出语言。
2. `/input/case.json`：取 `case_id`、`pdf_path`、`layout`、`pages`、`target_sections`。有 PDF 就用 PDF，不要凭文件名猜内容。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.reading_text` 是还原后的可读正文，不是“解析完成”的声明。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "reading_text": "按阅读顺序还原的全文",
    "sections": [{"id": "s1", "title": "...", "text": "...", "page": 1}],
    "tables": [{"id": "t1", "caption": "...", "rows": [["..."]]}],
    "equations": [{"id": "e1", "latex": "...", "page": 2}],
    "layout": {"pages": 8, "columns": 2, "reading_order": "..."},
    "artifacts": {"reading_text_md": "/app/output/reading_text.md", "sections_json": "/app/output/sections.json", "tables_md": "/app/output/tables.md"}
  },
  "evidence": [{"section": "s1", "page": 1, "bbox": [0, 0, 100, 100]}],
  "uncertainty": [{"page": 3, "issue": "双栏串行/公式不可读"}]
}
```

引擎另给 `formulas` 候选（原文文本、页码、编号）；`equations.latex` 由 Agent 复核后补写，不要把候选文本直接当 LaTeX。

## 工作流（最多 4 步）

1. **解析**：有 PDF 先跑

```bash
python scripts/pdf_layout_engine.py extract /input/paper.pdf > /app/work/layout.json
```

   没有 PyMuPDF 时会回退 `pdftotext -layout`；把实际后端记进 `uncertainty`。
2. **还原**：按阅读顺序拼正文；双栏先左后右，表格按行列还原，公式尽量转 LaTeX，图注跟着图。不要把所有文本按 PDF 坐标硬拼成一段。
3. **落盘核验**：把 `extract` 输出的 `pages` 原样放进 `/app/work/pipeline_input.json`（或作为 `input_layout`），保留 `case_id`，跑：

```bash
python scripts/pdf_layout_engine.py pipeline /app/work/pipeline_input.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field reading_text
```

4. **交付**：`result.json` + `reading_text.md` + `sections.json` + `tables.md`。

## 不能造假

- 没解析却写“已提取”；
- 表格/公式被静默丢掉；
- 双栏顺序错乱还标 success；
- 编造页码、章节标题。

## 评分关注

阅读顺序对、结构全、表格能看懂、公式不丢、页码可回查。

