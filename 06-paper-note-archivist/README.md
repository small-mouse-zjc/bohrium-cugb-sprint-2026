# paper-note-archivist（冲刺版）

文献总结与结构化笔记作品：按论文自身章节读，按章节写笔记，每条结论带锚点、前提和局限。

- 输入：`/input/task.md` + `/input/case.json`（`paper_sections`、`notes`、`card`、`knowledge_points`、`valid_anchors`）。
- 主产物：`result.structured_notes`（逐节笔记）+ `result.reading_card`（论文卡片）。
- 运行：

```bash
python scripts/notes_engine.py pipeline /app/work/notes_input.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field structured_notes
```

- 判定：笔记正文 <200 字符、章节顺序错、锚点不可回链、结论没有前提/局限，都不能算 `success`。
- 边界：不编造页码/章节/引文；摘要里的“可能”不得写成“证明”。

设计取向：笔记是给未来的自己看的，不是摘要复述；能回链比写得多更重要。

