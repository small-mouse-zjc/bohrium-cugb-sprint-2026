---
name: academic-polish
description: 学术语言润色。在不改变原意、主张强度和事实的前提下把句子写得更顺、更地道；逐句记录改动，保住数字、引用、限定词与否定，不替原文加观点。
---

# academic-polish

## 读什么

1. `/input/task.md`：润色口径（语气、目标期刊风格、是否允许换句）。
2. `/input/case.json`：原文正文（`text` / `draft` / `paragraphs`）、数字与引用来源。先读完全文，再动手。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含；本手册只是最低要求。

## 主产物

**`result.polished_text` 是润色后的完整正文，不是几句例句。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "polished_text": "润色后的完整正文",
    "changes": [
      {"original": "原句", "revised": "改后句", "reason": "理顺主谓/时态/搭配"}
    ],
    "preserved": {"numbers": ["25"], "citations": ["[3]"], "hedges": ["may"], "negations": ["not"]},
    "artifacts": {"polished_md": "/app/output/polished.md",
                  "audit_json": "/app/output/audit.json"}
  },
  "evidence": [{"anchor": "句段位置", "note": "改动依据"}],
  "uncertainty": [{"issue": "语气拿不准/歧义句"}]
}
```

## 怎么做（4 步）

1. **通读原文**：标出数字、单位、引用、图表编号、限定词（may / might / likely）、否定和比较级——这些先列入 `preserved`。
2. **最小编辑**：能不改就不改；只修语法、搭配、冗余、语序和学术措辞。每处改动写进 `changes`，给理由。
3. **核验落盘**：写 `polished.md`、`audit.json`，填好 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

4. **交付**：`result.json` + `polished.md` + `audit.json`。拿不准的句子进 `uncertainty`，不要硬改主张。

## 不能造假

- 新增原文没有的事实、数据、引用或结论；
- 把“may / 可能”改成“证明 / 显著”，否定、因果方向、比较级被翻转；
- 删掉或改动数字、单位、引用、图表编号；
- 只给润色片段，不给完整正文。

## 评分关注

原意保住、句子地道、改动可追溯。先保源，再求顺。
