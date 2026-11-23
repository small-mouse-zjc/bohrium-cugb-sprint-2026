# methods-repro-guard（冲刺版）

方法与实验章节作品：把配置、日志、代码、数据说明整理成“能照着做”的方法章节，并保证每个数值有来源。

- 输入：`/input/task.md` + `/input/case.json`（`sources`、`params`、`gaps`、`limitations`）。
- 主产物：`result.method_experiment_draft` 完整章节 + `result.parameter_table`。
- 运行：

```bash
python scripts/methods_engine.py pipeline /app/work/pipeline_input.json --draft-file /app/work/method_experiment_draft.md --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field method_experiment_draft
```

- 判定：六类要素（数据/预处理/方法/训练推理/评价/结果）缺失、数值无来源、复现清单缺项、限制写成套话，都不算 `success`。
- 边界：不编造硬件、超参数、随机种子、数据规模；`case_io.py`/`compare_engine.py` 仅辅助读取与对照。

设计取向：章节要像作者写的，而不是检查项拼接；每个数字都能指回配置或日志。

