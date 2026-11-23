# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `polished_text` | 是 | 润色后的完整正文，空或过短判 partial |
| `changes` | 是 | 逐条修改记录；无改动也要说明 |
| `preserved` | 是 | 数字/引用/hedge/否定清单 |
| `artifacts` | 是 | `polished_md`、`audit_json` 的绝对路径，必须存在 |
| `summary` | 否 | 一段话说明改了几类、保住了什么 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 最小编辑：能不改就不改；每处修改给理由。
- 不得新增原文没有的事实、数据、引用。
- hedge（可能/倾向于）、否定、因果方向、比较级不得改变。
- 数字、单位、引用、图表编号必须保留。
- `status=success` 要求：`polished_text` 非空、`changes` 可解释、`validate_result.py` 通过。

