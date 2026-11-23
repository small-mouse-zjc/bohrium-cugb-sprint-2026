---
name: knowledge-graph-builder
description: 文献知识图谱构建。用于从真实论文语料抽取实体/关系/属性，生成带 provenance 的图谱，并用 3 个以上查询做覆盖验证与答案回链。
---

# knowledge-graph-builder（冲刺版）

## 先读什么

1. `/input/task.md`：确认实体类型、关系类型、查询要求、是否要图查询结果、节点/边规模。
2. `/input/case.json`：取 `case_id`、`sources`、`entities`、`relations`、`queries`、`schema`。每个节点/边都要能回到真实 source id。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.graph` 是带来源的知识图谱；查询答案必须能回链。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "graph": {
      "nodes": [{"id": "n1", "type": "Method|Dataset|Finding|...", "label": "...", "source": "s1"}],
      "edges": [{"source": "n1", "target": "n2", "relation": "...", "source_doc": "s1"}]
    },
    "query_answers": [
      {"query": "...", "answer": "...", "trace": ["n1", "e1", "n2"], "sources": ["s1"]}
    ],
    "coverage": {"queries_total": 3, "queries_answerable": 3, "nodes": 12, "edges": 15, "orphan_nodes": []},
    "artifacts": {"graph_json": "/app/output/graph.json", "answers_json": "/app/output/query_answers.json", "coverage_json": "/app/output/coverage_check.json"}
  },
  "evidence": [{"node": "n1", "source": "s1", "quote": "..."}],
  "uncertainty": [{"node": "n1", "issue": "实体消歧未定"}]
}
```

## 工作流（最多 4 步）

1. **抽实体/关系**：先读每篇 source，按 schema 抽实体；合并同义/缩写但保留别名；每条关系记 `source_doc` 与证据句。
2. **建图**：先保证连通性，再补细节；孤立节点要么补边，要么进 `uncertainty`。不要为了规模造节点。
3. **跑查询**：至少 3 个真实问题；每个答案给节点/边 trace 和 source。查询答不出就改图或降级。
4. **落盘核验**：写 `/app/work/kg_input.json`（`case_id` + `source_index` + `entities` + `relations` + `queries`），跑：

```bash
python scripts/kg_engine.py pipeline /app/work/kg_input.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field graph
```

## 不能造假

- 节点/边没有 source；
- 为凑规模重复造实体；
- 查询答案与图结构对不上；
- 把“可能相关”写成确定关系。

## 评分关注

实体类型清楚、关系有方向、来源可回链、查询能答、图不是散点。

