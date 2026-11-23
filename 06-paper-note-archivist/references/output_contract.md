# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `structured_notes` | 是 | 按章节组织的完整笔记，正文合计 ≥200 字符；空判 partial |
| `reading_card` | 是 | 问题/数据/方法/发现/局限/前提 |
| `section_alignment` | 是 | 是否跟随论文自身章节 |
| `anchor_verification` | 是 | 每条笔记锚点是否可回链 |
| `artifacts` | 是 | `notes_md`、`reading_card_json` 绝对路径，必须存在 |
| `summary` | 否 | 覆盖章节、笔记数、缺锚点数 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 笔记必须按论文章节顺序组织，不按自定义模板硬套。
- 每条笔记要有可回链锚点；锚点不存在进 `uncertainty`。
- 结论必须带条件/局限，不得把“可能”写成“证明”。
- 不编造页码、章节号、引文。
- `status=success` 要求：笔记非空、锚点全部可回链、`validate_result.py` 通过。

