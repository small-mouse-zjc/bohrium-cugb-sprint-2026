# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `introduction_draft` | 是 | 四部件完整成稿；空判 partial |
| `paragraphs` | 是 | 每段的 part/text/refs/source_ref/status |
| `claims` | 是 | 贡献条目与证据 refs |
| `artifacts` | 是 | `draft`、`review` 绝对路径，必须存在 |
| `summary` | 否 | 四部件、引用数、空白支撑数 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- 只使用输入里真实存在的 work id / claim id。
- 空白必须由至少 2 篇已引工作推出；贡献必须有方法/图表/实验锚点。
- 不出现“首次”“颠覆”“显著提升”等强断言，除非有证据。
- `status=success` 要求：四部件齐全、`draft_review` gate 不为 fail、`validate_result.py` 通过。

