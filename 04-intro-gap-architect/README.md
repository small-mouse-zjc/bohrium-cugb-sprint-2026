# intro-gap-architect（冲刺版）

引言与相关工作写作作品：由 Agent 先读真实文献，再写“背景 → 相关工作 → 空白 → 贡献”四部件；脚本只做结构核验。

- 输入：`/input/task.md` + `/input/case.json`（`works`/`references`、`background`、`claims`、`target`）。
- 主产物：`result.introduction_draft` 完整引言；`result.paragraphs` 标出四部件；`result.claims` 给贡献与证据锚点。
- 运行：

```bash
python scripts/draft_review.py --draft /app/work/introduction_draft.md --case /input/case.json --outdir /app/output
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field introduction_draft
```

- 判定：四部件缺失、空白只由 1 篇文献推出、贡献没有方法/图表/实验锚点、出现无证据的“首次/显著提升”，都判 `needs_attention`。
- 边界：不使用 `solve`/`render-draft` 生成成稿；`compose` 只可作为结构参考，正文必须由 Agent 写。

设计取向：引言是论证文，不是字段表；引用必须服务于论证链。

