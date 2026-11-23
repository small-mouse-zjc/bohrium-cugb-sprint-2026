# academic-polish-source-preserving（冲刺版）

学术语言润色作品：在保留事实、术语、数字、引用和 hedge 的前提下，做最小编辑，让表达更清楚、更符合学术语域。

- 输入：`/input/task.md` + `/input/case.json`（`source_text` 或附件稿件、`termbase`、`target_style`）。
- 主产物：`result.polished_text` 完整润色稿；`result.changes` 逐条说明改了什么、为什么。
- 运行：

```bash
python scripts/case_io.py /input/case.json --out /app/work/case.json --dump-text /app/work/source.txt
python scripts/polish_audit.py check --source /app/work/source.txt --revised /app/work/polished.md --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field polished_text
```

- 判定：数字、引用、否定、限定、术语被改动且无说明，判 `needs_attention`；未改动语句应给出理由或保留。
- 边界：不做“整篇重写”，不补原文没有的事实；`office_io.py` 只负责读取附件，不参与润色判断。

设计取向：润色稿本身是主产物，audit 只是保源证据。

