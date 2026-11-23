# 输出契约 · 04 引言与相关工作

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 成稿、段落、主张、产物 |
| `evidence` | 段落/主张的来源依据 |
| `uncertainty` | 证据不足、缺口存疑、未决表述 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `introduction_draft` | 是 | 引言成稿；空判 partial |
| `paragraphs` | 是 | `[{part, text, refs, source_ref, status}]` |
| `claims` | 是 | `[{claim, source_ref, status}]` |
| `artifacts` | 是 | `draft` / `review` 绝对路径，必须存在 |

## 硬规则

- 只用输入真实存在的 work id / claim id；编造 id 判 error。
- 空白须由至少两篇已引工作共同推出。
- 贡献须有方法 / 图表 / 实验锚点。
- “首次 / 颠覆 / 显著提升”等强断言必须有证据，否则降级为限定表述。
- `success` 要求：成稿完整、回指闭环、`guard.py` 无 error。
