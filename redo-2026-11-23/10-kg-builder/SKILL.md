---
name: kg-builder
description: 文献知识图谱构建。从给定材料抽实体与关系成图，每个节点、每条边都带来源；查询答案沿节点与边可回链 trace；不凑规模造重复实体，孤立节点补边或登记进不确定性。
---

# kg-builder

## 读什么

1. `/input/task.md`：实体/关系类型、查询问题清单。
2. `/input/case.json`：论文正文或分节文本、已知实体关系线索。先通读再抽。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "graph": {
      "nodes": [
        {"id": "n1", "label": "CO2", "type": "fluid", "source": "§1 sentence 1"}
      ],
      "edges": [
        {"source": "n1", "target": "n2", "relation": "increases",
         "source_doc": "case", "evidence": "Solubility increases as pressure rises."}
      ]
    },
    "query_answers": [
      {"query_id": "q1", "answer": "CO2 solubility increases with pressure.",
       "trace": ["n1", "e1", "n2"],
       "sources": {"matched_nodes": ["n1", "n2"], "matched_edges": ["e1"],
                   "evidence": "Solubility increases as pressure rises."}}
    ],
    "coverage": {"queries": 3, "answerable": 3, "nodes": 2, "edges": 1,
                 "isolated": []},
    "artifacts": {"graph_json": "/app/output/graph.json",
                  "query_answers_json": "/app/output/answers.json",
                  "coverage_json": "/app/output/coverage.json"}
  },
  "evidence": [{"anchor": "节点/边 id", "note": "来源依据"}],
  "uncertainty": [{"issue": "关系不确定/孤立节点未补边"}]
}
```

## 怎么做（4 步）

1. **抽实体**：先列材料里出现的实体，给 `label` 与 `source`；同义实体合并，不重复造节点。
2. **连关系**：每条边写明 `source / target / relation`，附 `source_doc` 或证据句；端点必须是已登记节点。
3. **答查询**：对每个问题沿边找答案，`trace` 记录经过的节点/边；`sources` 回链匹配节点、边与证据。答不了的登记进 `coverage`。
4. **核验落盘**：写 `graph.json`、`answers.json`、`coverage.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 节点/边没有来源或证据；
- 边指向不存在的节点；
- 答案 trace 走的节点/边不在图里；
- 为凑规模重复造实体、编造关系；孤立节点既不补边也不登记。

## 评分关注

实体关系有据、答案可沿边回查、覆盖如实。先建得对，再建得全。
