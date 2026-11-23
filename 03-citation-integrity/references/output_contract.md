# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `editable_manuscript` | 是 | 改好编号的正文全文；空判 partial |
| `bibliography` | 是 | 文后参考文献条目列表，格式按任务要求 |
| `number_mapping` | 是 | 旧编号到新编号的映射 |
| `claim_source_map` | 否 | 每条 claim 对应引用与正文位置 |
| `artifacts` | 是 | `manuscript`、`bibliography` 绝对路径，必须存在 |
| `summary` | 否 | 改了几处、合并几条、剩余问题 |

## 硬规则

- 正文引用与文后表一一对应，不出现悬空编号。
- 不编造条目、DOI、作者、年份、期刊。
- 重复条目合并时保留真实元数据，不丢作者/年份。
- 引用顺序按正文首次出现（顺序编码制）或任务指定格式。
- `status=success` 要求：正文非空、表非空、映射完整、`validate_result.py` 通过。

