# 输出契约 · 05 方法与实验

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 成稿、参数表、六要素、可复现说明、产物 |
| `evidence` | 参数/段落的来源定位 |
| `uncertainty` | 材料未提供、数值存疑、缺项 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `method_experiment_draft` | 是 | 完整章节；<200 字符判 partial |
| `parameter_table` | 是 | `[{name, value, source}]` |
| `completeness` | 是 | 六要素覆盖状态 + `missing_items` |
| `reproducibility` | 是 | 可复现条件与限制 |
| `artifacts` | 是 | `draft_md` / `parameter_table_json` 绝对路径 |

## 六要素

`data`、`preprocessing`、`method`、`training_inference`、`evaluation`、`results`。

## 硬规则

- 每个数值须能在 `sources` 找到；找不到的进 `uncertainty`，不得编造。
- 不编造硬件、超参、种子、数据规模、结果。
- `success` 要求：章节完整、参数有来源、`guard.py` 无 error。
