---
name: translation-guard
description: 科研文献翻译。中英互译、长文分段、术语锁定、数字/单位/公式/引用保真，交付可对照的双语译文；先把译文写顺，再核验，不把检查当译文。
---

# translation-guard

## 读什么

1. `/input/task.md`：源/目标语言、段落范围、术语口径、是否要双语。
2. `/input/case.json`：`case_id`、待译段落（`paragraphs` 或长文本）、`glossary`、`domain`。先读完原文再定译法。

`case.json` 若带 `output_contract` / `required_fields`，最终 `result.json` 必须包含其中每个字段；本手册字段只是最低要求。

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
    "artifacts": {"translations_md": "/app/output/translations.md",
                   "translations_json": "/app/output/translations.json"}
  },
  "evidence": [{"id": "P1", "source_anchor": "P1", "note": "译法依据"}],
  "uncertainty": [{"id": "P1", "issue": "术语未定/原文歧义"}]
}
```

## 怎么做（4 步）

1. **读原文**：列出术语候选；有 `glossary` 就用，没有就自建，未确认的译名不要写死。
2. **逐段译**：数字、单位、化学式、公式、引用标记原样保留；否定、限定、因果方向、比较级不能改；长文译完再统一术语。
3. **核验落盘**：写好 `translations.md` 和 `translations.json`，把结果填进 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

   按 `errors` 修；`warnings` 是提示，不阻断。
4. **交付**：`result.json` + `translations.md` + `translations.json`。确实译不出的段落进 `uncertainty`，标 `partial`，不要编。

## 不能造假

- 没译却写“已翻译”；
- 数字、单位、公式、引用被改写或删掉；
- 同一术语前后不一致；
- 把校验脚本的输出当译文。

## 评分关注

术语稳、段落全、事实保真、译文可读。先把话写顺，再谈检查。
