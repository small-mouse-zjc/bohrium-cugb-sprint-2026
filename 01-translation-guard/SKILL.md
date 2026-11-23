---
name: translation-guard
description: 科研文献翻译。用于中英互译、长文分段、术语锁定、数字/单位/公式/引用保真、段落对齐与双语交付；先翻译，再核验，不把检查表当译文。
---

# translation-guard（冲刺版）

## 先读什么

1. `/input/task.md`：确认源语言、目标语言、要翻的段落范围、术语表口径、是否要求双语。
2. `/input/case.json`：取 `case_id`、`paragraphs`、`glossary`、`domain`、`target_language`。段落可能是 `[{id,text}]`，也可能是一段长文本；以真实结构为准。

不要先跑一堆命令。先把原文读完，再决定术语和译法。

`case.json` 可能带 `output_contract` / `required_fields`。最终 `result.json` 必须包含其中每个字段（放顶层或 `result` 内）；本 Skill 列出的主产物字段只是最低要求。

## 主产物

**`result.translations` 必须是真实译文，不是“已翻译”的声明。**

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "translations": [
      {"id": "P1", "source": "原文", "target": "译文", "terms": ["term"]}
    ],
    "bilingual": [{"id": "P1", "source": "...", "target": "..."}],
    "glossary_used": [{"source": "...", "target": "..."}],
    "artifacts": {"translations_md": "/app/output/translations.md", "translations_json": "/app/output/translations.json"}
  },
  "evidence": [{"id": "P1", "source_anchor": "P1", "note": "译法依据"}],
  "uncertainty": [{"id": "P1", "issue": "术语未定/原文歧义"}]
}
```

## 工作流（最多 4 步）

1. **准备**：读原文，列出术语候选；有 `glossary` 就用，没有就自己建，但不要把未确认的译名硬写死。
2. **翻译**：逐段翻译。数字、单位、公式、化学式、引用标记原样保留；否定、限定、因果方向不能改。长文先译完再统一术语。
3. **核验**：把逐段译文写进 `/app/work/result_input.json` 的 `translations`（`{"P1": "译文", ...}`），跑：

```bash
python scripts/translation_guard.py pipeline /app/work/result_input.json --outdir /app/output > /app/work/checks.json
```

   把 `checks.json` 里的 `result` 写入 `/app/output/result.json` 的 `result`，补 `case_id`、`status` 和 `evidence`/`uncertainty`，再跑：

```bash
python scripts/validate_result.py --result /app/output/result.json --outdir /app/output --case /input/case.json --main-field translations
```

4. **交付**：`/app/output/result.json` + `translations.md` + `translations.json`。如果某段确实无法翻译，标 `partial`，不要编。

## 不能造假

- 不翻译却写“已翻译”；
- 数字、单位、公式、引用被改写或删除；
- 术语前后不一致；
- 把检查脚本的输出当成译文。

## 评分关注

术语稳、段落全、事实保真、译文可读。先把中文/英文写顺，再谈检查。

