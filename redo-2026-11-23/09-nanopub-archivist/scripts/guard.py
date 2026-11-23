#!/usr/bin/env python3
"""09 Nanopub 轻量校验：断言字段齐全、证据可逐字回查、provenance 不空泛。

断言拆分质量与语气强度由 Agent 把握；脚本只查结构与证据回指。
"""
import argparse
import json
import os
import re
import sys

STATUS = {"success", "partial", "needs_attention"}
GENERIC_SOURCE = {"", "论文", "paper", "the paper", "source", "来源"}


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _source_text(case):
    parts = [case.get("source_text", ""), case.get("text", "")]
    for s in case.get("sources", []) or []:
        if isinstance(s, dict):
            parts.append(s.get("text", "") or s.get("content", ""))
        else:
            parts.append(str(s))
    for sec in case.get("sections", []) or []:
        if isinstance(sec, dict):
            parts.append(sec.get("text", ""))
    return "\n".join(parts)


def _norm(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


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

    pubs = res.get("nanopublications")
    if not isinstance(pubs, list) or not pubs:
        errors.append("nanopublications 为空或不是数组")
        pubs = []

    source_norm = _norm(_source_text(case)) if case else ""
    for i, p in enumerate(pubs):
        if not isinstance(p, dict):
            errors.append(f"nanopubs[{i}] 不是对象")
            continue
        for field in ("assertion", "subject", "relation", "object", "evidence", "evidence_location"):
            if not str(p.get(field, "")).strip():
                errors.append(f"nanopubs[{i}] 缺 {field}")
        assertion = str(p.get("assertion", ""))
        if re.search(r"\s(and|but|;)\s|，", assertion):
            warnings.append(f"nanopubs[{i}] 可能是复合句，需拆分")
        evidence = _norm(p.get("evidence", ""))
        if source_norm and evidence and evidence not in source_norm:
            errors.append(f"nanopubs[{i}] 证据在原文中逐字找不到: {p.get('evidence')}")

    prov = res.get("provenance")
    if not isinstance(prov, dict):
        errors.append("provenance 不是对象")
    else:
        if str(prov.get("source", "")).strip().lower() in GENERIC_SOURCE:
            errors.append("provenance.source 空泛（不得只写“来自论文”）")
        if not str(prov.get("method", "")).strip():
            warnings.append("provenance 缺 method")

    coverage = res.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage 不是对象")
    else:
        for field in ("source_assertions", "covered", "missing"):
            if field not in coverage:
                warnings.append(f"coverage 缺 {field}")

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
