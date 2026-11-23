#!/usr/bin/env python3
"""04 引言轻量校验：成稿完整、段落/主张回指真实 id、强断言提示复核。

论证质量与缺口判断由 Agent 负责；脚本只查 id 闭环与结构。
"""
import argparse
import json
import os
import re
import sys

STATUS = {"success", "partial", "needs_attention"}
STRONG_TERMS = ["首次", "first", "颠覆", "revolutionary", "显著提升",
                "significantly outperform", "填补空白", "state-of-the-art"]


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _known_ids(case):
    ids = set()
    for key in ("works", "sources", "references", "claims"):
        data = case.get(key)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("id"):
                    ids.add(str(item["id"]))
    return ids


def _split_refs(value):
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(str(v).replace(";", ",").split(","))
        return [v.strip() for v in out if v.strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.replace(";", ",").split(",") if v.strip()]
    return []


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

    draft = str(res.get("introduction_draft", ""))
    if not draft.strip():
        errors.append("introduction_draft 为空")

    known = _known_ids(case) if case else None

    paragraphs = res.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        errors.append("paragraphs 为空或不是数组")
        paragraphs = []
    for i, p in enumerate(paragraphs):
        if not isinstance(p, dict):
            errors.append(f"paragraphs[{i}] 不是对象")
            continue
        if not p.get("part"):
            errors.append(f"paragraphs[{i}] 缺 part")
        if not p.get("text"):
            errors.append(f"paragraphs[{i}] 缺 text")
        refs = _split_refs(p.get("refs")) + _split_refs(p.get("source_ref"))
        if not refs:
            warnings.append(f"paragraphs[{i}] 无来源回指")
        if known is not None:
            unknown = [r for r in refs if r not in known]
            if unknown:
                errors.append(f"paragraphs[{i}] 引用未知 id: {unknown}")

    claims = res.get("claims")
    if claims is not None and not isinstance(claims, list):
        errors.append("claims 不是数组")
    elif isinstance(claims, list):
        for i, c in enumerate(claims):
            if not isinstance(c, dict):
                errors.append(f"claims[{i}] 不是对象")
                continue
            if not c.get("claim"):
                errors.append(f"claims[{i}] 缺 claim")
            refs = _split_refs(c.get("source_ref"))
            if not refs:
                warnings.append(f"claims[{i}] 无来源回指")
            if known is not None:
                unknown = [r for r in refs if r not in known]
                if unknown:
                    errors.append(f"claims[{i}] 引用未知 id: {unknown}")

    low = draft.lower()
    for term in STRONG_TERMS:
        if term.lower() in low:
            warnings.append(f"出现强断言词“{term}”，需确认有证据支撑")

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
