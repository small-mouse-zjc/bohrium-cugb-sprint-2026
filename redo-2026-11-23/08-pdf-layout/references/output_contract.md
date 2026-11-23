# 输出契约 · 08 文献文档解析

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 正文、章节、表格、公式、版面、产物 |
| `evidence` | 页码/区域定位 |
| `uncertainty` | 双栏交错、跨页表、识别存疑处 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `reading_text` | 是 | 按阅读顺序还原的正文；空判 partial |
| `sections` | 是 | `[{title, body, page}]` |
| `tables` | 是 | `[{title, rows, columns?, page}]`；无表为空数组 |
| `equations` | 否 | `[{latex, page}]` |
| `layout` | 是 | `{pages, two_column_pages?, reading_order}` |
| `artifacts` | 是 | `reading_text_md` / `sections_json` / `tables_md` |

## 硬规则

- 正文必须来自真实 PDF/版面；页码、bbox 可回查。
- 双栏、跨页表、图注不得静默丢失。
- 无解析后端只能 `partial`；不编造版面结构。

## 平台附带 artifacts

`arm_manifest.json`、`README.md`、`src/reproduce.py`、`execution/run.log`、`execution/results/`、`characterization.json`、`trace/trace.jsonl`。
