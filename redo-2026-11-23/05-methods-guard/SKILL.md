---
name: methods-guard
description: 方法与实验章节撰写。按数据—预处理—方法—训练/推理—评价—结果六要素组织成稿，参数逐条标注来源；所有数值必须能在给定材料中找到，不编硬件、超参、种子、数据规模与结果。
---

# methods-guard

## 读什么

1. `/input/task.md`：方法/实验章节要求、目标读者。
2. `/input/case.json`：原始方法材料、参数、实验设置、已有结果（`sources` / `source_text` / `draft`）。先把材料里出现过的数值列出来。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "method_experiment_draft": "方法与实验章节成稿",
    "parameter_table": [
      {"name": "batch size", "value": "32", "source": "case source §3.1"}
    ],
    "completeness": {
      "data": "covered | missing",
      "preprocessing": "covered | missing",
      "method": "covered | missing",
      "training_inference": "covered | missing",
      "evaluation": "covered | missing",
      "results": "covered | missing",
      "missing_items": ["未给随机种子"]
    },
    "reproducibility": "可复现条件与限制说明",
    "artifacts": {"draft_md": "/app/output/methods.md",
                  "parameter_table_json": "/app/output/params.json"}
  },
  "evidence": [{"anchor": "参数/段落", "note": "来源位置"}],
  "uncertainty": [{"issue": "材料未提供/数值存疑"}]
}
```

## 怎么做（4 步）

1. **盘材料**：按六要素归类已有信息；材料没给的要素进 `completeness.missing_items`，不要补。
2. **写成稿**：先搭方法流程，再填实验设置；参数进 `parameter_table`，每条标 `source`。
3. **数值回指**：草稿里每个数字都要能在材料中找到；找不到的删掉或进 `uncertainty`。
4. **核验落盘**：写 `methods.md`、`params.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

## 不能造假

- 编造硬件、超参、随机种子、数据规模、训练轮次、评价指标或结果数值；
- 参数表条目没有来源；
- 把材料里的“示例值”写成实际实验设置；
- 只给提纲，不交完整章节。

## 评分关注

六要素齐全、参数可回指、可复现性写清楚。先忠实材料，再组织表达。
