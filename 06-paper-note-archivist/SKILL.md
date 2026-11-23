---
name: paper-note-archivist
description: 文献总结与结构化笔记。用于阅读真实论文并输出按章节组织、可回链原文的笔记、论文卡片、知识点；每条结论保留前提与局限。
---

# paper-note-archivist（冲刺版）

## 先读什么

1. `/input/task.md`：确认笔记粒度、要哪些字段、是否要论文卡片/知识点、锚点格式。
2. `/input/case.json`：取 `case_id`、`paper_sections`、`notes`、`card`、`knowledge_points`、`valid_anchors`；论文正文可能是 `text` 或附件 PDF/XML。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.structured_notes` 是逐节写出来的完整笔记。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "structured_notes": [
      {"id": "n1", "section": "method", "text": "作者做了什么、数据/条件、结论、局限", "anchor": "§3.2"}
    ],
    "reading_card": {"question": "...", "data": "...", "method": "...", "findings": "...", "limitations": "...", "conditions": "..."},
    "section_alignment": {"aligned": true, "missing": []},
    "anchor_verification": {"all_anchored": true, "missing": []},
    "artifacts": {"notes_md": "/app/output/structured_notes.md", "reading_card_json": "/app/output/reading_card.json"}
  },
  "evidence": [{"note_id": "n1", "anchor": "§3.2", "quote": "..."}],
  "uncertainty": [{"note_id": "n1", "issue": "原文未报告..."}]
}
```

## 工作流（最多 4 步）

1. **读论文**：先按论文章节顺序读，记下每节的主张、数据、方法条件、结论、局限。不要只读摘要。
2. **写笔记**：笔记骨架跟随论文章节；每条笔记尽量包含“问题/数据/方法条件/发现/局限/前提”，并给可回链锚点。笔记要能独立看懂，不要只写“作者提出了方法”。
3. **落盘核验**：把笔记组合成 `/app/work/notes_input.json`（`case_id` + `paper_sections` + `notes:[{id,section,text,anchor}]` + `card`），跑：

```bash
python scripts/notes_engine.py pipeline /app/work/notes_input.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field structured_notes
```

4. **交付**：`result.json` + `structured_notes.md` + `reading_card.json`。

## 不能造假

- 编造页码、章节号、引文；
- 把摘要里的“可能”写成“证明”；
- 每条笔记只写结论、不写前提和局限；
- 笔记不按论文章节，按自己的模板硬套。

## 评分关注

对得上、留得住、找得回、用得上。笔记要忠实、具体、可回查，不是摘要复述。

