---
name: note-archivist
description: 文献总结与笔记。按论文自身章节顺序整理逐节笔记与阅读卡片（问题/数据/方法/发现/局限/前提），每条笔记带可回链锚点；结论保留条件与局限，不编页码、章节号与引文。
---

# note-archivist

## 读什么

1. `/input/task.md`：笔记详略、卡片字段要求。
2. `/input/case.json`：论文正文或分节文本（`sections` / `text`）、标题与页码信息。先理清章节顺序。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "structured_notes": "按章节组织的逐节笔记（合计 ≥200 字符）",
    "reading_card": {
      "problem": "研究问题",
      "data": "数据/样本",
      "method": "方法",
      "findings": "主要发现",
      "limitations": "局限",
      "premises": "前提假设"
    },
    "section_alignment": [
      {"section": "章节标题", "notes": "该节笔记", "anchor": "页码/小节号/原文定位"}
    ],
    "anchor_verification": [
      {"note_id": "S1", "anchor": "§2 / p.3", "verified": true}
    ],
    "artifacts": {"notes_md": "/app/output/notes.md",
                  "reading_card_json": "/app/output/reading_card.json"}
  },
  "evidence": [{"anchor": "定位", "note": "对应原文"}],
  "uncertainty": [{"issue": "定位不清/内容缺失"}]
}
```

## 怎么做（4 步）

1. **理章节**：按论文自身顺序列出章节；每节先抓主张，再补证据。
2. **写笔记**：逐节记录问题、数据、方法、发现；发现写成带条件的结论，注明局限。
3. **做卡片**：汇总成阅读卡片六字段；锚点能回到原文位置。
4. **核验落盘**：写 `notes.md`、`reading_card.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 编造页码、章节号、引文；
- 把作者未说的结论写成定论；
- 打乱章节顺序或跨节拼接；
- 笔记过短、无锚点。

## 评分关注

章节对齐、锚点可回查、结论有边界。先忠实原文，再提炼。
