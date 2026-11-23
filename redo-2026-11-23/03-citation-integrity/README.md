# 03 · 引用管理（citation-integrity）

正文引用与文献表闭环、去重合并、编号映射。

- **主产物**：`editable_manuscript` + `bibliography`。
- **辅助**：`number_mapping`、`claim_source_map`。
- **交付文件**：`manuscript.md`、`bibliography.json`。
- **校验**：`scripts/guard.py` 查正文编号均能在文献表找到、条目元数据结构完整、无悬空引用。
