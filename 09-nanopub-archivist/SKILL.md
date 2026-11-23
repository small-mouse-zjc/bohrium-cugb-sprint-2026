---
name: nanopub-archivist
description: Nanopublication 构建。用于把论文断言拆成原子 claim，绑定原文证据、方法/条件与 provenance，输出可校验的 assertion/evidence/nanopub JSON-LD。
---

# nanopub-archivist（冲刺版）

## 先读什么

1. `/input/task.md`：确认断言粒度、要哪些字段、provenance 口径、是否要 JSON-LD。
2. `/input/case.json`：取 `case_id`、`paragraph`/`text`、`assertions`、`evidence`、`provenance`、`valid_anchors`。只使用原文真实存在的句子作证据。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.nanopublications` 是一组可独立核验的纳米出版物。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "nanopublications": [
      {
        "id": "np1",
        "assertion": {"subject": "...", "predicate": "...", "object": "...", "qualifier": "..."},
        "evidence": [{"quote": "原文句", "anchor": "P2"}],
        "provenance": {"source": "...", "method": "...", "conditions": "..."},
        "confidence": "high|medium|low",
        "status": "supported|partial|unsupported"
      }
    ],
    "coverage": {"source_assertions": 5, "covered": 5, "missing": []},
    "artifacts": {"nanopubs_json": "/app/output/nanopublications.json", "evidence_map_json": "/app/output/assertion_evidence_map.json"}
  },
  "evidence": [{"np": "np1", "quote": "...", "anchor": "P2"}],
  "uncertainty": [{"np": "np1", "issue": "条件缺失"}]
}
```

## 工作流（最多 4 步）

1. **拆原子句**：一句只表达一个主谓宾；复合句拆开；不要把一个段落塞进一个 assertion。
2. **绑定证据**：每个 assertion 至少一条原文 quote + anchor；quote 必须原文可查。条件、方法、数据来源写进 provenance。
3. **落盘核验**：把结构化输入写 `/app/work/nanopub_input.json`（`case_id` + `assertions` + `source_metadata`，断言字段用 `text/subject/relation/object/evidence/anchor/confidence`），跑：

```bash
python scripts/nanopub_engine.py pipeline /app/work/nanopub_input.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field nanopublications
```

4. **交付**：`result.json` + `nanopublications.json` + `assertion_evidence_map.json`。

## 不能造假

- 断言比原文更强/更绝对；
- quote 原文找不到；
- provenance 只写“来自论文”；
- 一条 assertion 塞多个 claim 导致不可核验。

## 评分关注

原子性、证据可查、条件完整、provenance 清楚、覆盖原文主要断言。

