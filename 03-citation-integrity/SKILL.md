---
name: citation-integrity
description: 参考文献与引用一致性。用于引用插入定位、正文编号与文后表同步、文献去重合并、GB/T 7714 格式化、引用-claim 对应核验。
---

# citation-integrity（冲刺版）

## 先读什么

1. `/input/task.md`：确认引用制（顺序编码/作者-年）、文后表格式、是否允许改正文。
2. `/input/case.json`：取 `case_id`、`manuscript`、`entries`/`references`、`claims`、`works`、`style`。正文与文献表以真实输入为准。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.editable_manuscript` 是改好编号的完整正文；`result.bibliography` 是配套文后表。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "editable_manuscript": "正文全文",
    "bibliography": ["[1] ...", "[2] ..."],
    "number_mapping": {"old": "new"},
    "claim_source_map": [{"claim": "...", "refs": ["[1]"], "anchor": "..."}],
    "artifacts": {"manuscript": "/app/output/manuscript_updated.md", "bibliography": "/app/output/references.txt"}
  },
  "evidence": [{"type": "citation", "old": "[3]", "new": "[1]", "reason": "..."}],
  "uncertainty": [{"entry": "...", "issue": "元数据缺失/重复"}]
}
```

## 工作流（最多 4 步）

1. **读稿**：读正文和文献表，标出每个 `[n]` / 作者-年引用出现的位置。
2. **改**：按首次出现顺序重编号；同步正文、文后表、图表引用。重复条目合并，但保留所有真实元数据。每条引用尽量对应到它支撑的句子，写进 `claim_source_map`。
3. **落盘**：把正文写 `/app/work/manuscript.md`，组合输入（`case_id` + `entries` + `manuscript`）到 `/app/work/case_pipeline.json`，跑：

```bash
python scripts/citation_engine.py pipeline /app/work/case_pipeline.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field editable_manuscript
```

4. **交付**：`result.json` + `manuscript_updated.md` + `references.txt`。

## 不能造假

- 编造文献条目、DOI、作者、年份；
- 正文编号与文后表不一致；
- 把没有引用的句子硬塞引用；
- 删除真实引用只为“看起来干净”。

## 评分关注

正文/文后表同步、编号顺序、格式统一、去重正确、每条 claim 能追到来源。

