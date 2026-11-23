# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `graph` | 是 | `nodes[]` + `edges[]`；空判 partial |
| `query_answers` | 是 | ≥3 个查询，含 answer/trace/sources |
| `coverage` | 是 | 查询总数/可答数/节点/边/孤立点 |
| `artifacts` | 是 | `graph_json`、`answers_json`、`coverage_json` 绝对路径，必须存在 |
| `summary` | 否 | 节点/边/查询覆盖概况 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 每个节点必须有 `source`；每条边必须有 `source_doc` 或证据句。
- 至少 3 个查询，且答案必须能沿节点/边 trace 回链。
- 不允许为凑规模重复造实体或边。
- 孤立节点必须补边或进 `uncertainty`。
- `status=success` 要求：图谱非空、查询≥3 且可答、`validate_result.py` 通过。

