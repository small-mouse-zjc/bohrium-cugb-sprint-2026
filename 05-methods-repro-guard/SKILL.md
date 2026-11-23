---
name: methods-repro-guard
description: 方法与实验章节写作与复现。用于把配置、日志、代码、数据说明整理成方法/实验章节，确保六类要素齐全、数值有来源、复现清单完整、限制具体。
---

# methods-repro-guard（冲刺版）

## 先读什么

1. `/input/task.md`：确认章节范围、是否要参数表、复现粒度、限制写法。
2. `/input/case.json`：取 `case_id`、`section_text`/`draft`、`sources`（配置文件、日志、代码、数据说明）、`params`、`gaps`、`limitations`。数值只认来源里真实出现的值。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.method_experiment_draft` 是完整的方法/实验章节。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "method_experiment_draft": "章节全文",
    "parameter_table": [{"name": "...", "value": "...", "source": "..."}],
    "completeness": {"six_elements": ["..."], "missing": []},
    "reproducibility": {"items": ["..."], "missing": []},
    "artifacts": {"draft_md": "/app/output/method_experiment_draft.md", "parameter_table_json": "/app/output/parameter_table.json"}
  },
  "evidence": [{"value": "...", "source": "...", "line": "..."}],
  "uncertainty": [{"value": "...", "issue": "来源缺失/条件未说明"}]
}
```

## 工作流（最多 4 步）

1. **抽事实**：先读 `sources`，列出数据、预处理、模型、训练/推理配置、评价指标、baseline、实验结果；每个数值记来源位置。
2. **写章节**：按“数据→预处理→方法→训练/推理→评价→结果→限制”写。数值只写来源里的；缺的写进 `uncertainty`，不要补造。限制落到具体场景。
3. **落盘核验**：把全文写 `/app/work/method_experiment_draft.md`，跑：

```bash
python scripts/methods_engine.py pipeline /app/work/pipeline_input.json \
  --draft-file /app/work/method_experiment_draft.md --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 的 `result` 写进 `/app/output/result.json`，补 `case_id`、`status`、`evidence`、`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field method_experiment_draft
```

4. **交付**：`result.json` + `method_experiment_draft.md` + `parameter_table.json`。

## 不能造假

- 编造超参数、随机种子、硬件、数据集规模；
- 把“未报告”写成“默认”；
- 用“取得了显著效果”代替具体指标；
- 限制写成“受限于数据”这种空话。

## 评分关注

写得全、数值准、复现清单能照着做、限制具体。章节读起来要像作者写的，不像清单拼接。

