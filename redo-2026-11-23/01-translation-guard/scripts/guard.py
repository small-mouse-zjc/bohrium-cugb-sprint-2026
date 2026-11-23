#!/usr/bin/env python3
"""01 翻译轻量校验：结构、段落覆盖、译文非空、数字保留、产物落盘。

只做机器能硬判的事；译文质量由 Agent 负责。
"""
import argparse
import json
import os
import re
import sys

STATUS = {"success", "partial", "needs_attention"}
NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _case_ids(case):
    """从 case.json 提取待译段落 id；兼容 paragraphs/segments 列表与 dict。"""
    ids = set()
    for key in ("paragraphs", "segments", "sentences", "items"):
        data = case.get(key)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("id"):
                    ids.add(str(item["id"]))
                elif isinstance(item, str):
                    ids.add(str(item))
        elif isinstance(data, dict):
            ids.update(str(k) for k in data.keys())
    return ids


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

    trans = res.get("translations")
    seen = set()
    if not isinstance(trans, list) or not trans:
        errors.append("translations 为空")
    else:
        for i, t in enumerate(trans):
            if not isinstance(t, dict):
                errors.append(f"translations[{i}] 不是对象")
                continue
            tid = t.get("id")
            src, tgt = str(t.get("source", "")), str(t.get("target", ""))
            if not tid:
                errors.append(f"translations[{i}] 缺 id")
            if not tgt.strip():
                errors.append(f"{tid} target 为空")
            elif tgt.strip() == src.strip():
                warnings.append(f"{tid} 译文与原文相同（专名需在 uncertainty 说明）")
            if src and tgt:
                lost = set(NUM_RE.findall(src)) - set(NUM_RE.findall(tgt))
                if lost:
                    errors.append(f"{tid} 丢失数字: {sorted(lost)}")
            seen.add(str(tid))

    if case:
        missing = _case_ids(case) - seen
        if missing:
            errors.append(f"未覆盖段落: {sorted(missing)}")

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
