# knowledge-graph-builder（冲刺版）

文献知识图谱作品：从多篇真实论文抽实体/关系，建成带来源的图，再用至少 3 个查询验证可答性与回链。

- 输入：`/input/task.md` + `/input/case.json`（`sources`、`entities`、`relations`、`queries`、`schema`）。
- 主产物：`result.graph`（nodes/edges）+ `result.query_answers`（答案/trace/sources）。
- 运行：

```bash
python scripts/kg_engine.py pipeline /app/work/kg_input.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field graph
```

- 判定：节点/边无来源、查询<3、答案不能沿图回链、孤立节点未处理，都不能算 `success`。
- 边界：不为凑规模重复造实体；跨篇同名实体只有在证据支持时才合并。

设计取向：图要能回答真实问题，不是节点和边的堆量。

