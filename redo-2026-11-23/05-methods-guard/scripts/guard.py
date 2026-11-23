#!/usr/bin/env python3
"""05 方法实验轻量校验：章节完整、参数有来源、数值可回指材料。

材料未提供的要素登记为 missing；脚本不替 Agent 补参数、不编结果。
"""
import argparse
import json
import os
import re
import sys

STATUS = {"success", "partial", "needs_attention"}
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
SIX = ("data", "preprocessing", "method", "training_inference", "evaluation", "results")


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _source_text(case):
    parts = [case.get("source_text", "")]
    for s in case.get("sources", []) or []:
        if isinstance(s, dict):
            parts.append(s.get("text", "") or s.get("content", ""))
        else:
            parts.append(str(s))
    for k in ("draft", "original_text"):
        if isinstance(case.get(k), str):
            parts.append(case[k])
    return "\n".join(parts)


def check_result(result, case=None, outdir=None):
    errors, warnings = [], []
    if not isinstance(result, dict):
        return {"ok": False, "errors": ["result 不是对象"], "warnings": [],
                "suggested_status": "needs_attention"}

    for k in ("case_id", "status", "result"):
        if k not in result:
            errors.append(f"缺顶层字段 {k}")
    status = result.get("status")
    if status not in STATUS:
        errors.append(f"status 非法: {status!r}")

    res = result.get("result")
    if not isinstance(res, dict):
        errors.append("result.result 不是对象")
        return {"ok": False, "errors": errors, "warnings": warnings,
                "suggested_status": "needs_attention"}

    draft = str(res.get("method_experiment_draft", ""))
    if not draft.strip():
        errors.append("method_experiment_draft 为空")
    elif len(draft.strip()) < 200:
        warnings.append("章节不足 200 字符，按契约应判 partial")

    params = res.get("parameter_table")
    if not isinstance(params, list):
        errors.append("parameter_table 不是数组")
        params = []
    for i, p in enumerate(params):
        if not isinstance(p, dict):
            errors.append(f"parameter_table[{i}] 不是对象")
            continue
        for field in ("name", "value", "source"):
            if not str(p.get(field, "")).strip():
                errors.append(f"parameter_table[{i}] 缺 {field}")

    completeness = res.get("completeness")
    if not isinstance(completeness, dict):
        errors.append("completeness 不是对象")
    else:
        for key in SIX:
            if key not in completeness:
                warnings.append(f"completeness 未登记要素 {key}")
        if "missing_items" not in completeness:
            warnings.append("completeness 缺 missing_items")

    if not str(res.get("reproducibility", "")).strip():
        warnings.append("缺 reproducibility 可复现说明")

    source_nums = set()
    if case:
        source_nums = set(NUM_RE.findall(_source_text(case)))
        if source_nums:
            for i, p in enumerate(params):
                if isinstance(p, dict):
                    lost = set(NUM_RE.findall(str(p.get("value", "")))) - source_nums
                    if lost:
                        errors.append(f"参数 {p.get('name', i)} 数值在材料中找不到: {sorted(lost)}")
            lost_draft = set(NUM_RE.findall(draft)) - source_nums
            if lost_draft:
                warnings.append(f"草稿数值在材料中找不到，需复核: {sorted(lost_draft)}")

    for k in ("evidence", "uncertainty"):
        if k in result and not isinstance(result[k], list):
            errors.append(f"{k} 不是数组")

    art = res.get("artifacts")
    if isinstance(art, dict):
        for key, p in art.items():
            if not p:
                continue
            path = p if os.path.isabs(p) else os.path.join(outdir or ".", p)
            if not os.path.exists(path):
                warnings.append(f"产物不存在: {key}={p}")

    suggested = "success" if not errors else ("partial" if status in STATUS else "needs_attention")
    if len(draft.strip()) < 200 and suggested == "success":
        suggested = "partial"
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "suggested_status": suggested}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--outdir", default="/app/output")
    ap.add_argument("--case")
    args = ap.parse_args()

    result = _load(args.result)
    case = _load(args.case) if args.case else None
    report = check_result(result, case, args.outdir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
