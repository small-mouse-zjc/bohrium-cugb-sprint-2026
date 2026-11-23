# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `method_experiment_draft` | 是 | 完整章节；<200 字符判 partial |
| `parameter_table` | 是 | 参数名/值/来源 |
| `completeness` | 是 | 六类要素与缺失项 |
| `reproducibility` | 是 | 复现清单与缺失项 |
| `artifacts` | 是 | `draft_md`、`parameter_table_json` 绝对路径，必须存在 |
| `summary` | 否 | 覆盖范围、数值数、缺口数 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 正文每个数值必须能在 `sources` 找到；找不到进 `uncertainty`。
- 不编造硬件、超参数、随机种子、数据规模、评价结果。
- 六类要素至少：数据、预处理、方法、训练/推理、评价、结果；限制要具体到场景。
- `status=success` 要求：章节非空、数值全部有源、复现清单完整、`validate_result.py` 通过。

