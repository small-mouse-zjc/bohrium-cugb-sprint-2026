# nanopub-archivist（冲刺版）

Nanopublication 构建作品：把论文断言拆成原子 claim，绑定原文证据、方法/条件和 provenance，输出可核验的 JSON。

- 输入：`/input/task.md` + `/input/case.json`（`paragraph`/`text`、`assertions`、`source_metadata`）。
- 主产物：`result.nanopublications`（每个含 assertion/evidence/provenance/status）。
- 运行：

```bash
python scripts/nanopub_engine.py pipeline /app/work/nanopub_input.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field nanopublications
```

- 判定：断言过宽、quote 在原文找不到、provenance 只写“来自论文”、复合断言未拆，都不能算 `success`。
- 边界：不把“可能相关”写成确定关系；证据不足时标 `partial`/`unsupported`，不硬凑。

设计取向：原子性、可查证据、可追来源，三者缺一不可。

