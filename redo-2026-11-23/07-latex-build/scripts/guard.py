#!/usr/bin/env python3
"""07 LaTeX 轻量校验：PDF 真实非空、编译标记与产物一致、文本可抽取。

脚本不执行编译；真实编译由 Agent 在有 TeX 的环境完成并写入日志。
"""
import argparse
import json
import os
import sys

STATUS = {"success", "partial", "needs_attention"}


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve(path, outdir):
    if not path:
        return None
    return path if os.path.isabs(path) else os.path.join(outdir or ".", path)


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

    if not str(res.get("latex_source", "")).strip():
        errors.append("latex_source 为空")

    pdf = res.get("compiled_pdf")
    if not isinstance(pdf, dict):
        errors.append("compiled_pdf 不是对象")
        pdf = {}
    else:
        pdf_path = _resolve(pdf.get("path", ""), outdir)
        exists = bool(pdf_path) and os.path.exists(pdf_path)
        if pdf.get("compile_ok"):
            if not exists:
                errors.append("compile_ok=true 但 PDF 文件不存在，疑似冒充产物")
            else:
                actual = os.path.getsize(pdf_path)
                if actual == 0:
                    errors.append("PDF 字节数为 0")
                declared = pdf.get("bytes")
                if isinstance(declared, int) and declared > 0 and actual != declared:
                    warnings.append(f"PDF 声明字节 {declared} 与实际 {actual} 不符")
        if isinstance(pdf.get("pages"), int) and pdf["pages"] <= 0:
            errors.append("PDF 页数必须 >0")
        if isinstance(pdf.get("bytes"), int) and pdf["bytes"] <= 0 and not pdf.get("compile_ok"):
            warnings.append("未编译成功，bytes 为 0")

    text_check = res.get("pdf_text_check")
    if not isinstance(text_check, dict):
        warnings.append("缺 pdf_text_check")
    else:
        if text_check.get("ok") and (text_check.get("chars") or 0) <= 0:
            errors.append("pdf_text_check.ok=true 但抽取字符数为 0")

    compile_log = res.get("compile")
    if not isinstance(compile_log, dict):
        warnings.append("缺 compile 编译记录")
    else:
        if not compile_log.get("engine"):
            warnings.append("compile 未记录引擎")
        if not isinstance(compile_log.get("errors"), list):
            errors.append("compile.errors 不是数组")
        if not isinstance(compile_log.get("missing_files"), list):
            errors.append("compile.missing_files 不是数组")

    for k in ("evidence", "uncertainty"):
        if k in result and not isinstance(result[k], list):
            errors.append(f"{k} 不是数组")

    art = res.get("artifacts")
    if isinstance(art, dict):
        for key, p in art.items():
            if not p:
                continue
            path = _resolve(p, outdir)
            if path and not os.path.exists(path):
                warnings.append(f"产物不存在: {key}={p}")

    suggested = "success" if not errors else ("partial" if status in STATUS else "needs_attention")
    if isinstance(pdf, dict) and pdf.get("compile_ok") is False and suggested == "success":
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
