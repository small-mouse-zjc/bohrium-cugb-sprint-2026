# 交付自查清单（10 条）

逐条打勾，任一条不过就不许报 `success`。

1. [ ] 工程落盘在原位，未凭记忆重建源码。
2. [ ] `latex_ci.py` 已跑，`report.json` 为本次生成（PDF mtime 与运行时间一致）。
3. [ ] `compile_ok=true`，`pages>0`，`bytes>0`。
4. [ ] `pdf_text_check.ok=true`，抽得到正文（不是空白页）。
5. [ ] `converged=true`：`undefined_refs`、`undefined_cites` 均为空。
6. [ ] PDF 中无 `??`、无 `[?]`。
7. [ ] `fix_plan` 为空；`alignment_silent` 已清零。
8. [ ] 表格列数与数据一致，无空白列、无 Overfull 溢出裁切。
9. [ ] 源码目录在 `/app/output`，`main.tex` 可继续编辑，`\input` 路径有效。
10. [ ] `uncertainty` 如实写了缺字体/缺包/biber 缺失/未真实编译等限制。

## 常见"假通过"信号

- PDF 只有 1 页却要求 8 页；正文字符数远小于预期。
- `converged` 假成立、`passes=1`：可能残留 `.aux` 让首轮假收敛。
- 日志有 `Overfull \hbox` 但 PDF 看着正常：仍要记录，量大需修。
