---
name: pdf-layout
description: 文献文档解析。从真实 PDF/版面还原正文、章节、表格、公式与阅读顺序；双栏、跨页表、图注不得静默丢失，页码可回查；解析后端不可用时如实降级，不编版面结构。
---

# pdf-layout

## 读什么

1. `/input/task.md`：解析目标（正文/表格/公式/版面）。
2. `/input/case.json`：PDF 路径或内嵌文本、版面元信息。先确认 PDF 可被当前后端读取。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "reading_text": "按阅读顺序还原的正文",
    "sections": [
      {"title": "章节标题", "body": "正文", "page": 3}
    ],
    "tables": [
      {"title": "表 1", "rows": [["列1", "列2"]], "columns": 2, "page": 3}
    ],
    "equations": [{"latex": "...", "page": 3}],
    "layout": {"pages": 8, "two_column_pages": [2, 3], "reading_order": "single|two-column"},
    "artifacts": {"reading_text_md": "/app/output/reading.md",
                  "sections_json": "/app/output/sections.json",
                  "tables_md": "/app/output/tables.md"}
  },
  "evidence": [{"anchor": "页码/区域", "note": "文本来源"}],
  "uncertainty": [{"issue": "双栏交错/跨页表识别存疑"}]
}
```

## 怎么做（4 步）

1. **选后端**：优先 PyMuPDF；不可用时走 `pdftotext` 回退；后端都不可用就标 `partial`，不要硬猜版面。
2. **还原顺序**：先定单栏/双栏，再按阅读顺序抽正文；标题、正文、图注、表注分开登记。
3. **结构化**：章节进 `sections`，表格进 `tables`（无表给空数组），公式进 `equations`；每条带页码。双栏交错、跨页表在 `uncertainty` 标注存疑处。
4. **核验落盘**：写 `reading.md`、`sections.json`、`tables.md`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 正文不来自真实 PDF/版面；
- 双栏、跨页表、图注被静默丢弃；
- 编造页码、行列、公式或 bbox；
- 后端不可用却宣称解析完整。

## 包内附带（平台 expected artifacts）

本题为 `llm_judge_topic_markdown`，包内还需提供：`arm_manifest.json`、`README.md`、`src/reproduce.py`、`execution/run.log`、`execution/results/`、`characterization.json`、`trace/trace.jsonl`。这些随 Skill 包组织，`guard.py` 只校验主产物结构。

## 评分关注

正文完整、顺序正确、表格公式不丢、页码可回查。先读准版面，再整理结构。
