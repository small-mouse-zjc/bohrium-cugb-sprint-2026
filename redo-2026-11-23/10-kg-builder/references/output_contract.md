# 输出契约 · 10 文献知识图谱

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 图谱、查询答案、覆盖、产物 |
| `evidence` | 节点/边来源依据 |
| `uncertainty` | 关系不确定、孤立节点、未答查询 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `graph` | 是 | `{nodes, edges}`；节点 `{id, label, type?, source}`，边 `{source, target, relation, source_doc?, evidence?}` |
| `query_answers` | 是 | ≥3 条 `{query_id, answer, trace, sources}` |
| `coverage` | 是 | `{queries, answerable, nodes, edges, isolated}` |
| `artifacts` | 是 | `graph_json` / `query_answers_json` / `coverage_json` |

## 硬规则

- 每个节点有 `label` 与 `source`；每条边有 `source_doc` 或证据句。
- 边端点与答案 trace 必须命中图内节点；答案可沿边回链。
- 不为凑规模重复造实体/边；孤立节点补边或进 `uncertainty`。
