# citation-integrity（冲刺版）

参考文献与引用一致性作品：把正文引用、编号顺序、文后表、去重与 claim 对应关系一次改齐。

- 输入：`/input/task.md` + `/input/case.json`（`manuscript`、`entries`/`references`、`claims`、`style`）。
- 主产物：`result.editable_manuscript`（完整正文）+ `result.bibliography`（文后表）。
- 运行：

```bash
python scripts/citation_engine.py pipeline /app/work/case_pipeline.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field editable_manuscript
```

- 判定：正文编号与文后表不一致、引用落点错误、重复条目未合并，都必须进 `uncertainty`，不能静默通过。
- 边界：不编造 DOI/作者/年份；合并重复条目时保留可核验元数据；无法确认的条目只标 `partial`。

设计取向：正文和文后表是同一份交付的两个面，不能只交一张检查表。

