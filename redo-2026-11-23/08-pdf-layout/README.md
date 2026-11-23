# 08 · 文献文档解析（pdf-layout）

真实 PDF 版面还原：正文、章节、表格、公式、阅读顺序。

- **主产物**：`reading_text`。
- **辅助**：`sections`、`tables`、`equations`、`layout`。
- **交付文件**：`reading.md`、`sections.json`、`tables.md`。
- **校验**：`scripts/guard.py` 查正文非空、章节/表格结构完整、页码可回查。
- **边界**：无解析后端只能 `partial`；双栏/跨页表存疑处进 `uncertainty`。
- **附带**：按平台要求提供 ARM manifest、reproduce.py、run.log、results、characterization、trace。
