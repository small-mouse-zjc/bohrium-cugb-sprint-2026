---
name: citation-integrity
description: 学术引用管理。把正文引用标记与文后文献表对齐、去重合并、编号映射；只保留真实来源，不编造作者、年份、期刊、DOI，不留下悬空编号。
---

# citation-integrity

## 读什么

1. `/input/task.md`：引用风格（数字编号 / 作者-年份）、输出要求。
2. `/input/case.json`：原稿正文、原始文献表或来源条目。先核对每条来源是否真实存在。

`case.json` 若带 `output_contract` / `required_fields`，最终字段必须包含。

## 主产物

```json
{
  "case_id": "...",
  "status": "success | partial | needs_attention",
  "result": {
    "editable_manuscript": "可编辑正文，引用标记保留在原位",
    "bibliography": [
      {"id": "1", "key": "smith2020", "author": "Smith J.", "year": "2020",
       "title": "...", "source": "Journal ...", "doi": "..."}
    ],
    "number_mapping": [{"citation": "[1]", "key": "smith2020", "bib_id": "1"}],
    "claim_source_map": [{"claim": "观点", "source_key": "smith2020"}],
    "artifacts": {"manuscript": "/app/output/manuscript.md",
                  "bibliography": "/app/output/bibliography.json"}
  },
  "evidence": [{"anchor": "正文位置", "note": "对应文献条目"}],
  "uncertainty": [{"issue": "来源缺失/元数据不全"}]
}
```

## 怎么做（4 步）

1. **盘点来源**：列出正文每条主张对应的真实文献；元数据不全的进 `uncertainty`，不要补全。
2. **对齐编号**：正文引用与文献表一一对应；重复条目合并，保留真实元数据；删掉正文没用到的条目或在 `uncertainty` 说明。
3. **核验落盘**：写 `manuscript.md`、`bibliography.json`，填 `result.json`，跑：

```bash
python scripts/guard.py --result /app/output/result.json --outdir /app/output --case /input/case.json
```

4. **交付**：`result.json` + `manuscript.md` + `bibliography.json`。

## 不能造假

- 编造作者、年份、标题、期刊、DOI、卷期页码；
- 正文引用了文献表没有的编号（悬空引用）；
- 把不同文献合并成一条，或给条目安上不存在的来源；
- 只交文献表、不交可编辑正文。

## 评分关注

引用-文献闭环、去重干净、元数据真实可回查。先对齐，再排版。
