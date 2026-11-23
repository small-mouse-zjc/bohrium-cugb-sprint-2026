# translation-guard（冲刺版）

科研文献翻译作品：先读原文，再逐段翻译，最后用确定性脚本核验术语、数字、公式、引用与覆盖。

- 输入：`/input/task.md` + `/input/case.json`（`paragraphs`/`glossary`/`target_language`）。
- 主产物：`result.translations` 的真实译文；`translations.md`/`translations.json` 为同一内容的可读副本。
- 运行：

```bash
python scripts/translation_guard.py pipeline /app/work/result_input.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field translations
```

- 判定：译文为空判 `partial`；数字/公式/引用被改、术语不一致、段落缺失都必须在 `uncertainty` 里出现。
- 边界：脚本只做核验和落盘，不代替 Agent 翻译；没有真实译文时不标 `success`。

设计取向：主产物优先，检查表是附件，不是作品本身。

