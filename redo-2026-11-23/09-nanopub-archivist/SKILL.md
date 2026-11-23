---
name: nanopub-archivist
description: Nanopublication 原子断言整理。把论文观点拆成单一主谓宾的小断言，每条配可在原文逐字找到的证据短句与出处；记录来源、方法、条件与覆盖情况，断言强度不超过原文。
---

# nanopub-archivist

## 读什么

1. `/input/task.md`：断言粒度、是否要置信度。
2. `/input/case.json`：论文正文或分节文本（`text` / `sections` / `sources`）。先通读，标出可断言的观点句。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "nanopublications": [
      {
        "assertion": "CO2 solubility rises with pressure.",
        "subject": "CO2",
        "relation": "solubility rises with",
        "object": "pressure",
        "evidence": "Solubility increases as pressure rises.",
        "evidence_location": "§Methods, p.2",
        "confidence": "high | medium | low"
      }
    ],
    "provenance": {"source": "输入论文标题/DOI", "method": "人工拆分原子断言",
                   "conditions": "常温常压以外的适用条件"},
    "coverage": {"source_assertions": 12, "covered": 10, "missing": ["未定位的观点句"]},
    "artifacts": {"nanopublications_json": "/app/output/nanopubs.json",
                  "assertion_evidence_map_json": "/app/output/map.json"}
  },
  "evidence": [{"anchor": "断言 id", "note": "证据出处"}],
  "uncertainty": [{"issue": "复合句难拆/证据模糊"}]
}
```

## 怎么做（4 步）

1. **抽观点**：逐句找可成断言的陈述；一句含多个结论就拆开。
2. **原子化**：每条只留一个主谓宾；标 `subject / relation / object`；断言语气对齐原文（may 不写成 proves）。
3. **配证据**：每条断言附一条能在原文**逐字找到**的 `evidence` 与 `evidence_location`；找不到原文支撑的不进断言。
4. **核验落盘**：写 `nanopubs.json`、`map.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 一条断言塞多个主谓宾（复合句不拆）；
- 证据不是原文逐字短句，或编出处；
- provenance 只写“来自论文”；
- 断言强度超过原文（推测写成定论）。

## 评分关注

断言原子、证据可逐字回查、覆盖如实。先拆干净，再配对证据。
