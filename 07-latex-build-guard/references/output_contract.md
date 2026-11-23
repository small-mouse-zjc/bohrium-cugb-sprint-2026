# 输出契约（冲刺版）

> 若 `case.json` 提供 `output_contract` / `required_fields`，以它为准；本契约是补充，不得删掉官方字段。

## 顶层

`case_id`、`status`（success/partial/needs_attention）、`result`、`evidence`、`uncertainty` 必填。

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `latex_source` | 是 | 主文件与文件清单；空判 partial |
| `compiled_pdf` | 是 | `path`/`pages`/`bytes`/`compile_ok` |
| `pdf_text_check` | 是 | `ok`/`backend`/`chars`，用于排除空壳 PDF |
| `compile` | 是 | 引擎、errors、missing_files |
| `changes` | 否 | 修了哪些文件、为什么 |
| `artifacts` | 是 | `pdf_path`、`source_main_tex` 绝对路径；`pdf_path` 必须存在 |

## 硬规则

- 引擎内部状态 `ok` 表示可交付，写入 `status` 时统一为 `success`；`partial` / `needs_attention` 原样保留。

- `compiled_pdf.path` 必须存在且 `bytes>0`；`pages>0`。
- `artifacts.pdf_path` 必须与 `compiled_pdf.path` 一致且真实存在。
- `compile_ok=true` 必须有真实编译日志；无 TeX 时只能 `partial`。
- 不允许用旧 PDF、空 PDF、截图冒充。
- `pdf_text_check.ok=false` 必须降级为 `partial`。
- `validate_result.py --main-field latex_source` 必须通过。

