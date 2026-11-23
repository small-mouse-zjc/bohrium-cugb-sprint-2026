# 02 · 学术语言润色（academic-polish）

保源最小润色：只改表达，不改主张与事实。

- **主产物**：`result.polished_text` 完整润色正文。
- **辅助**：`changes`（逐句改动）、`preserved`（数字/引用/限定词/否定保留清单）。
- **交付文件**：`polished.md`、`audit.json`。
- **校验**：`scripts/guard.py` 查正文非空、数字与引用标记未丢失、改动记录可追溯。
