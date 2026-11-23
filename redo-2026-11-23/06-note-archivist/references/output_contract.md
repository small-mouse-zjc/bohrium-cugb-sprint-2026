# 输出契约 · 06 文献总结与笔记

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 笔记、卡片、章节对齐、锚点核验、产物 |
| `evidence` | 锚点与原文对应 |
| `uncertainty` | 定位不清、内容缺失 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `structured_notes` | 是 | 逐节笔记，合计 ≥200 字符 |
| `reading_card` | 是 | `problem / data / method / findings / limitations / premises` |
| `section_alignment` | 是 | `[{section, notes, anchor}]`，按原文章节顺序 |
| `anchor_verification` | 是 | `[{note_id, anchor, verified}]` |
| `artifacts` | 是 | `notes_md` / `reading_card_json` 绝对路径 |

## 硬规则

- 按论文自身章节顺序；每条笔记有可回链锚点。
- 结论带条件与局限；不编造页码、章节号、引文。
- `success` 要求：笔记达标、锚点齐全、`guard.py` 无 error。
