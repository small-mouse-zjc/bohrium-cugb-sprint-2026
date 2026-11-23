# 10 · 文献知识图谱（kg-builder）

实体—关系图谱 + 可回链查询答案 + 覆盖登记。

- **主产物**：`graph` + `query_answers`。
- **辅助**：`coverage`（查询数/可答数/节点/边/孤立点）。
- **交付文件**：`graph.json`、`answers.json`、`coverage.json`。
- **校验**：`scripts/guard.py` 查节点 label/source、边端点存在、答案 trace 命中图内节点、孤立点提示。
