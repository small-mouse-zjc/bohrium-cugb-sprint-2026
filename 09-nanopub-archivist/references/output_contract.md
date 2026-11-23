# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `nanopublications` | 是 | 每个含 assertion/evidence/provenance/confidence/status；空判 partial |
| `coverage` | 是 | 原文断言数/已覆盖/缺失 |
| `artifacts` | 是 | `nanopubs_json`、`evidence_map_json` 绝对路径，必须存在 |
| `summary` | 否 | 断言数、覆盖数、unsupported 数 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 一条 assertion 只表达一个主谓宾；复合断言必须拆。
- 每条 assertion 至少一条 `quote`，且 quote 能在原文中逐字找到。
- provenance 必须写来源、方法/条件；不能只写“来自论文”。
- 断言强度不得超过原文；不确定的标 `partial`/`unsupported`。
- `status=success` 要求：断言非空、证据全部可查、`validate_result.py` 通过。

