#!/usr/bin/env python3
"""08 PDF 解析轻量校验：正文完整、章节/表格结构齐全、页码可回查。

版面识别质量由 Agent 结合后端判断；脚本只查结构与定位字段。
"""
import argparse
import json
import os
import sys

STATUS = {"success", "partial", "needs_attention"}


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    if not str(res.get("reading_text", "")).strip():
        errors.append("reading_text 为空")

    sections = res.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("sections 为空或不是数组")
        sections = []
    for i, s in enumerate(sections):
        if not isinstance(s, dict):
            errors.append(f"sections[{i}] 不是对象")
            continue
        if not s.get("title"):
            errors.append(f"sections[{i}] 缺 title")
        if not s.get("body"):
            errors.append(f"sections[{i}] 缺 body")
        if s.get("page") in (None, ""):
            warnings.append(f"sections[{i}] 缺页码，无法回查")

    tables = res.get("tables")
    if not isinstance(tables, list):
        errors.append("tables 不是数组")
        tables = []
    for i, t in enumerate(tables):
        if not isinstance(t, dict):
            errors.append(f"tables[{i}] 不是对象")
            continue
        if not t.get("title"):
            warnings.append(f"tables[{i}] 缺 title")
        rows = t.get("rows")
        if not isinstance(rows, list) or not rows:
            errors.append(f"tables[{i}] 缺 rows")

    equations = res.get("equations")
    if equations is not None and not isinstance(equations, list):
        errors.append("equations 不是数组")

    layout = res.get("layout")
    if not isinstance(layout, dict):
        warnings.append("缺 layout 版面信息")
    elif layout.get("pages") in (None, ""):
        warnings.append("layout 缺 pages")

    if res.get("backend") in (None, ""):
        warnings.append("未记录解析后端；若后端不可用应判 partial")

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
