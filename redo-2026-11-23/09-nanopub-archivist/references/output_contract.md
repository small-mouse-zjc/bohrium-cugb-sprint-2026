# 输出契约 · 09 Nanopublication

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 断言集、provenance、覆盖、产物 |
| `evidence` | 断言-证据对应 |
| `uncertainty` | 难拆复合句、证据模糊 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `nanopublications` | 是 | `[{assertion, subject, relation, object, evidence, evidence_location, confidence?}]` |
| `provenance` | 是 | `{source, method, conditions}` |
| `coverage` | 是 | `{source_assertions, covered, missing}` |
| `artifacts` | 是 | `nanopublications_json` / `assertion_evidence_map_json` |

## 硬规则

- 一条断言只表达一个主谓宾；复合句必须拆分。
- 每条至少一条可在原文逐字找到的 `evidence`。
- provenance 不得只写“来自论文”；断言强度不超原文。
