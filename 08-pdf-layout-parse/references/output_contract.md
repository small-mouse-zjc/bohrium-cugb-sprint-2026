# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `reading_text` | 是 | 按阅读顺序还原的正文，空判 partial |
| `sections` | 是 | 章节标题/正文/页码 |
| `tables` | 是 | 表格标题/行列；无表格可为空数组 |
| `equations` | 否 | 公式 LaTeX/页码 |
| `layout` | 是 | 页数/双栏页数/阅读顺序 |
| `artifacts` | 是 | `reading_text_md`、`sections_json`、`tables_md` 绝对路径，必须存在 |

## 硬规则

- 正文必须来自真实 PDF/版面，不允许凭标题生成。
- 双栏、跨页表格、图注不能静默丢失；处理不了进 `uncertainty`。
- 页码/bbox 必须可回查。
- 无 PDF 解析后端时只能 `partial`，不能写 `success`。
- `validate_result.py --main-field reading_text` 必须通过。

