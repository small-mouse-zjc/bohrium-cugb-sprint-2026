# 输出契约 · 01 文献翻译

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准；本契约是补充，不得删掉官方字段。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 译文、术语、产物 |
| `evidence` | 每段译文的原文定位与译法依据 |
| `uncertainty` | 未定术语、原文歧义、未译段落 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `translations` | 是 | `[{id, source, target, terms?}]`，target 是真实译文；空数组判 partial |
| `bilingual` | 否 | 原文/译文对照 |
| `glossary_used` | 否 | 实际使用的术语表 |
| `artifacts` | 是 | `translations_md` / `translations_json` 绝对路径，必须存在 |
| `summary` | 否 | 覆盖段数、术语数、未译项 |

## 硬规则

- 覆盖输入全部待译段；漏段进 `uncertainty`。
- `target` 不得是原文复制；确需保留的专名在 `uncertainty` 说明。
- 数字、单位、公式、引用与原文逐项一致。
- `success` 要求：译文非空、段落覆盖、`guard.py` 无 error。
