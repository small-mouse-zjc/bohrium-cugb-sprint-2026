---
name: intro-gap-architect
description: 引言与相关工作写作。用于基于真实论文材料撰写/改写引言、研究背景、相关工作、研究空白与贡献；四部件由 Agent 主写，脚本只核验。
---

# intro-gap-architect（冲刺版）

## 先读什么

1. `/input/task.md`：确认目标期刊/模板、篇幅、是否要相关工作、是否要贡献列表。
2. `/input/case.json`：取 `case_id`、`works`/`references`、`background`、`claims`、`evidence_index`、`target`。只使用真实存在的 work id 和 claim id。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.introduction_draft` 是完整、可直接编辑的引言全文。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "introduction_draft": "四部件完整成稿",
    "paragraphs": [{"part": "背景|相关工作|空白|贡献", "text": "...", "refs": ["w1"], "status": "ok"}],
    "claims": [{"id": "c1", "text": "贡献", "evidence_refs": ["w2", "exp1"]}],
    "artifacts": {"draft": "/app/output/introduction_draft.md", "review": "/app/output/draft_review.json"}
  },
  "evidence": [{"claim": "c1", "work": "w1", "quote": "...", "anchor": "..."}],
  "uncertainty": [{"issue": "...", "action": "..."}]
}
```

## 工作流（最多 4 步）

1. **读材料**：先读 `works` 的题目/摘要/结论，按“问题/方法/数据/评价”分组；不要按年份排队。
2. **写四部件**：背景从领域脉络落到具体问题；相关工作按同一维度比较；空白由至少 2 篇已引工作的共同局限推出；贡献逐条对应方法/图表/实验结果。
3. **落盘核验**：把全文写 `/app/work/introduction_draft.md`，跑：

```bash
python scripts/draft_review.py --draft /app/work/introduction_draft.md --case /input/case.json \
  --outdir /app/output --out /app/work/draft_review.json
```

   把引言全文写进 `/app/output/result.json` 的 `result.introduction_draft`，把 `draft_review.json` 的 gate/citations 和 `--outdir` 生成的 `artifacts` 一起写进 `result`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field introduction_draft
```

4. **交付**：`result.json` + `introduction_draft.md` + `draft_review.json`。

## 不能造假

- 不编造 work、作者、年份、DOI、实验数据；
- 不把“相关工作没覆盖”写成“无人研究”；
- 不把贡献写成“显著提升”却没有对应证据；
- 不用模板句拼接四部件。

## 评分关注

引言要有论证链：背景→问题→已有工作→空白→本文贡献。每句尽量有锚点，不要堆形容词。

