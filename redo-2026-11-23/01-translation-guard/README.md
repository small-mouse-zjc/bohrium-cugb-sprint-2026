# 01 · 文献翻译（translation-guard）

围绕科研论文高频翻译难点：术语一致性、长文分段、双语对照、译文核验。

- **主产物**：`result.translations`，每条 `{id, source, target, terms?}`。
- **交付文件**：`translations.md`（双语对照）、`translations.json`（结构化译文）。
- **校验**：`scripts/guard.py` 查段落覆盖、译文非空、数字/单位保留、产物落盘。
- **边界**：译不出的段落进 `uncertainty`，标 `partial`；不编造术语与事实。
