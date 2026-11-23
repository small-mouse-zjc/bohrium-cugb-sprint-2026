# 输出契约 · LaTeX 编译

> `case.json` 自带 `output_contract` / `required_fields` 时以它为准；本契约为兜底口径。

## 顶层

| 字段 | 必填 | 说明 |
|---|---|---|
| `case_id` | 是 | 与输入一致 |
| `status` | 是 | `success` / `partial` / `needs_attention` |
| `result` | 是 | 源码、PDF、文本校验、编译记录、修复清单、产物 |
| `evidence` | 是 | 每条错误/收敛依据的 `文件:行号` |
| `uncertainty` | 是 | 缺字体/宏包/文献、未做真实编译、引用未收敛 |

## result

| 字段 | 必填 | 说明 |
|---|---|---|
| `latex_source` | 是 | `{main_tex, files[]}`，交付可继续编辑的源码目录 |
| `compiled_pdf` | 是 | `{path, pages, bytes, compile_ok}` |
| `pdf_text_check` | 是 | `{ok, backend, chars}` |
| `compile` | 是 | `{engine, passes, errors[], error_count, missing_files[], undefined_refs[], undefined_cites[], converged, overfull_count}` |
| `fix_plan` | 是 | `[{file, line, type, action}]`，按行可执行 |
| `artifacts` | 是 | `{pdf_path, source_dir}` 绝对路径 |

增强（非契约必需，但评审有用）：`mode`（`real_compile`/`static_only`）、`env`
（引擎路径、TeX 版本、bibtex/biber 可用性、轮次）、`cleaned_before_build`。

## 判级硬条件

| 状态 | 条件 |
|---|---|
| `success` | `compile_ok` 且 `pages>0` 且 `bytes>0` 且 `pdf_text_check.ok` 且 `converged` 且 `fix_plan` 为空 |
| `partial` | 出了 PDF 但引用未收敛 / 有 `alignment_silent` / 无 TeX 仅静态检查 |
| `needs_attention` | 未出 PDF（缺包、缺类、致命错误），必须给首因 |

## 禁止

- `compile_ok: true` 而无真实日志；旧 PDF / 空 PDF / 截图冒充；编造页数与字符数。
- 引用留 `[?]` 仍判 `success`；`alignment_silent` 未处理仍判 `success`。
