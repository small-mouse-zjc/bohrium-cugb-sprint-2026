#!/usr/bin/env python3
"""06 笔记轻量校验：章节对齐、锚点齐全、卡片字段完整。

内容提炼与结论边界由 Agent 把握；脚本只查结构与锚点回指。
"""
import argparse
import json
import os
import sys

STATUS = {"success", "partial", "needs_attention"}
CARD_FIELDS = ("problem", "data", "method", "findings", "limitations", "premises")


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

    notes = str(res.get("structured_notes", ""))
    if not notes.strip():
        errors.append("structured_notes 为空")
    elif len(notes.strip()) < 200:
        warnings.append("笔记不足 200 字符，按契约应判 partial")

    card = res.get("reading_card")
    if not isinstance(card, dict):
        errors.append("reading_card 不是对象")
    else:
        for field in CARD_FIELDS:
            if not str(card.get(field, "")).strip():
                warnings.append(f"reading_card 缺 {field}")

    alignment = res.get("section_alignment")
    if not isinstance(alignment, list) or not alignment:
        errors.append("section_alignment 为空或不是数组")
        alignment = []
    for i, item in enumerate(alignment):
        if not isinstance(item, dict):
            errors.append(f"section_alignment[{i}] 不是对象")
            continue
        if not item.get("section"):
            errors.append(f"section_alignment[{i}] 缺 section")
        if not item.get("notes"):
            errors.append(f"section_alignment[{i}] 缺 notes")
        if not item.get("anchor"):
            errors.append(f"section_alignment[{i}] 缺 anchor（不可回链）")

    verify = res.get("anchor_verification")
    if verify is not None and not isinstance(verify, list):
        errors.append("anchor_verification 不是数组")
    elif isinstance(verify, list):
        for i, v in enumerate(verify):
            if not isinstance(v, dict):
                errors.append(f"anchor_verification[{i}] 不是对象")
                continue
            if not v.get("note_id"):
                errors.append(f"anchor_verification[{i}] 缺 note_id")
            if not v.get("anchor"):
                errors.append(f"anchor_verification[{i}] 缺 anchor")

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
    if len(notes.strip()) < 200 and suggested == "success":
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
