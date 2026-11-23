---
name: intro-architect
description: 引言与相关工作撰写。从真实已给文献出发搭出背景—缺口—贡献—路线的引言成稿；段落与主张逐条回指来源，不编文献 id，不写无证据的强断言。
---

# intro-architect

## 读什么

1. `/input/task.md`：论文主题、引言结构要求、篇幅。
2. `/input/case.json`：可用文献（`works` / `sources`，带 `id`）、已有主张（`claims`）、贡献线索。先确认每个 id 真实存在。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "introduction_draft": "引言成稿（背景—缺口—贡献—路线）",
    "paragraphs": [
      {"part": "background", "text": "段落", "refs": ["w1"],
       "source_ref": "w1", "status": "supported | inferred | gap"}
    ],
    "claims": [
      {"claim": "主张", "source_ref": "w1", "status": "supported | inferred"}
    ],
    "artifacts": {"draft": "/app/output/intro.md",
                  "review": "/app/output/review.json"}
  },
  "evidence": [{"anchor": "段落/主张", "note": "来源依据"}],
  "uncertainty": [{"issue": "证据不足/缺口判断存疑"}]
}
```

## 怎么做（4 步）

1. **盘文献**：把可用 work id 列出来；只引用这些 id，不造新文献。
2. **搭结构**：背景 → 已有工作 → 缺口 → 本文贡献 → 路线。缺口至少由两篇已引工作共同支撑；贡献要落到方法、图表或实验锚点。
3. **逐条回指**：每段、每条主张标 `source_ref` 与 `status`；证据不足的标 `inferred` 并进 `uncertainty`。
4. **核验落盘**：写 `intro.md`、`review.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 引用输入里不存在的 work id / claim id；
- 把单篇工作的局限写成领域空白；
- 写“首次 / 颠覆 / 显著提升 / 填补空白”等强断言却没有证据；
- 只给提纲，不交成稿。

## 评分关注

结构完整、来源可回指、缺口与贡献有依据。先立得住，再润色。
