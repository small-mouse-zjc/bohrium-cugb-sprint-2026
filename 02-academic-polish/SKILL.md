---
name: academic-polish-source-preserving
description: 学术语言润色（保源最小编辑）。用于论文摘要、引言、方法、审稿回复的语法/语域/连贯性润色；只改表达，不改主张强度、事实、数字和引用。
---

# academic-polish-source-preserving（冲刺版）

## 先读什么

1. `/input/task.md`：确认润色目标（语法/语域/简洁/连贯）、目标语言、是否保留原结构。
2. `/input/case.json`：取 `case_id`、`source_text` 或 `text`、`termbase`、`target_style`。没有 `source_text` 时读附件里的真实稿件。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.polished_text` 是润色后的完整正文。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "polished_text": "完整润色稿",
    "changes": [
      {"source": "原句", "revised": "改句", "type": "grammar|register|clarity|cohesion", "reason": "为什么改"}
    ],
    "preserved": {"numbers": [], "citations": [], "hedges": [], "negations": []},
    "artifacts": {"polished_md": "/app/output/polished.md", "audit_json": "/app/output/polish_audit.json"}
  },
  "evidence": [{"type": "preserved", "value": "...", "anchor": "..."}],
  "uncertainty": [{"issue": "...", "action": "..."}]
}
```

## 工作流（最多 4 步）

1. **取正文**：`python scripts/case_io.py /input/case.json --out /app/work/case.json --dump-text /app/work/source.txt`，读 `source.txt`。
2. **润色**：逐段改。只做最小编辑；专业术语、 hedging、否定、因果、数字、引用、图表编号不动。不要为了“更像论文”加新事实。
3. **落盘核验**：把改后全文写 `/app/work/polished.md`，跑：

```bash
python scripts/polish_audit.py check --source /app/work/source.txt --revised /app/work/polished.md \
  --out /app/work/audit.json --outdir /app/output
```

有 `termbase.csv` 时再加 `--termbase /app/work/termbase.csv`；没有就不加，不要临时编术语表。

然后跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field polished_text
```

`result.polished_text` 必须放完整改文；`changes` 用 `sentence_pairs`；`artifacts` 用 `polish_audit` 输出的路径。

4. **交付**：`result.json` + `polished.md` + `polish_audit.json`。

## 不能造假

- 改掉原文没有的意思；
- 把“可能/建议”改成“证明/必然”；
- 删除或改写数字、引用、图表编号；
- 用同义词替换专业术语导致概念漂移。

## 评分关注

改得对、说得像、没改坏、讲得清。润色稿要像人改的，不要像模板重写。

