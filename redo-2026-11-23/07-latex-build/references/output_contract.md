# 输出契约 · 07 LaTeX 写作与编译

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准。

## 顶层（必填）

| 字段 | 说明 |
|---|---|
| `case_id` | 与输入一致 |
| `status` | `success` / `partial` / `needs_attention` |
| `result` | 源码、PDF、文本校验、编译记录、产物 |
| `evidence` | 编译日志与引用收敛依据 |
| `uncertainty` | 缺字体/宏包/文献条目、编译受限 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `latex_source` | 是 | 主 `.tex` 源码；空判 partial |
| `compiled_pdf` | 是 | `{path, pages, bytes, compile_ok}` |
| `pdf_text_check` | 是 | `{ok, backend, chars}` |
| `compile` | 是 | `{engine, errors, missing_files, log_tail?}` |
| `artifacts` | 是 | `pdf_path` / `source_main_tex` 绝对路径 |

## 硬规则

- PDF 真实存在：`bytes > 0`、`pages > 0`。
- `compile_ok = true` 必须有真实编译日志；无 TeX 环境只能 `partial`。
- 禁止旧 PDF / 空 PDF / 截图冒充；`pdf_text_check.ok = false` 降级 `partial`。
- 文献处理须跑 bibtex/biber，引用不得留 `[?]` 即判成功。
