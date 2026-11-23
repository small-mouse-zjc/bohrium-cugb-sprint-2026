#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logparse.py — 把 LaTeX 编译日志解析成结构化诊断。

设计要点：
- 优先使用 `-file-line-error` 的 `file:line: message` 格式，可直接定位；
- 传统格式回退到 `! message` + 随后的 `l.<line>`；
- 缺文件/缺宏包单独抽取包名，供修复器做别名替换；
- 未定义引用/文献单独抽取 key，用于"收敛判定"（这决定 success/partial）。
纯函数，无副作用，便于单测。
"""
import re

# file:line 形式（pdflatex -file-line-error 输出）
FILE_LINE = re.compile(r"^(?P<file>[^ :][^:\n]*?):(?P<line>\d+):\s*(?P<msg>.+)$")
# 传统形式：! 开头
BANG = re.compile(r"^!\s*(?P<msg>.+)$")
# 传统行号提示：l.42
L_ANCHOR = re.compile(r"^l\.(\d+)\s")

MISSING_FILE = re.compile(r"File `(?P<name>[^']+)' not found")
MISSING_CLASS = re.compile(r"Class `(?P<name>[^']+)' not found")
UNDEF_REF = re.compile(r"LaTeX Warning: Reference `(?P<key>[^']+)' on page .*? undefined on input line (?P<line>\d+)")
UNDEF_CITE = re.compile(r"LaTeX Warning: Citation `(?P<key>[^']+)' .*?undefined on input line (?P<line>\d+)")
UNDEF_SUMMARY = re.compile(r"There were undefined references")
LABEL_MULTI = re.compile(r"LaTeX Warning: Label `(?P<key>[^']+)' multiply defined")
OVERFULL = re.compile(r"Overfull \\[hv]box \((?P<amt>[0-9.]+)pt too (?:wide|high)\)(?: in paragraph)? at lines (?P<l1>\d+)--(?P<l2>\d+)")
UNDERFULL = re.compile(r"Underfull \\[hv]box")
EMERGENCY = re.compile(r"Emergency stop")
RUNAWAY = re.compile(r"Runaway argument")
EXTRA_TAB = re.compile(r"Extra alignment tab has been changed to \\cr")
MISSING_DOLLAR = re.compile(r"Missing \$ inserted")
ENV_UNDEF = re.compile(r"Environment (?P<env>\S+) undefined")

# 错误分型：把原始消息映射成可操作的根因类别
ERROR_TYPES = [
    ("missing_package", re.compile(r"File `[^']+\.(sty|cls)' not found")),
    ("missing_font", re.compile(r"Font .*? not (?:loadable|found)|mktexpk|Font shape .*? undefined")),
    ("encoding", re.compile(r"Unicode character|inputenc Error|Invalid UTF-8")),
    ("math_mode", re.compile(r"Missing \$ inserted|Display math should end with|Bad math environment delimiter")),
    ("alignment", re.compile(r"Extra alignment tab|Misplaced alignment tab|Too many columns")),
    ("runaway", re.compile(r"Runaway argument|File ended while scanning")),
    ("brace", re.compile(r"Too many }'s|Missing } inserted|Extra }")),
    ("undefined_command", re.compile(r"Undefined control sequence")),
    ("undefined_env", re.compile(r"Environment .* undefined|\\begin\{.*\} on input line .* ended by")),
    ("undefined_ref", re.compile(r"Reference .* undefined")),
    ("undefined_cite", re.compile(r"Citation .* undefined|There were undefined references")),
    ("fatal", re.compile(r"Emergency stop|Fatal error")),
]


def classify(msg):
    for name, pat in ERROR_TYPES:
        if pat.search(msg):
            return name
    return "other"


def parse_log(text, main="main.tex"):
    """返回结构化诊断字典。"""
    lines = text.splitlines()
    errors, warnings = [], []
    missing_files, undef_refs, undef_cites = [], [], []
    overfull, underfull = [], 0
    converged_flag = True

    last_file, last_line = None, None
    for i, raw in enumerate(lines):
        s = raw.rstrip("\n")

        m_missing = MISSING_FILE.search(s)
        if m_missing:
            missing_files.append({"name": m_missing.group("name"), "line": last_line,
                                  "file": last_file, "log_line": i + 1})
        m_class = MISSING_CLASS.search(s)
        if m_class:
            missing_files.append({"name": m_class.group("name"), "line": last_line,
                                  "file": last_file, "log_line": i + 1})

        m_ref = UNDEF_REF.search(s)
        if m_ref:
            undef_refs.append({"key": m_ref.group("key"), "line": int(m_ref.group("line"))})
            converged_flag = False
        m_cite = UNDEF_CITE.search(s)
        if m_cite:
            undef_cites.append({"key": m_cite.group("key"), "line": int(m_cite.group("line"))})
            converged_flag = False
        if UNDEF_SUMMARY.search(s):
            converged_flag = False

        m_fl = FILE_LINE.match(s)
        if m_fl and (".tex" in m_fl.group("file") or ".sty" in m_fl.group("file")
                     or ".cls" in m_fl.group("file") or ".bib" in m_fl.group("file")):
            msg = m_fl.group("msg").strip()
            last_file, last_line = m_fl.group("file"), int(m_fl.group("line"))
            if msg.startswith("!") or "Error" in msg or "Undefined" in msg or "Missing" in msg:
                errors.append({"file": last_file, "line": last_line,
                               "type": classify(msg), "message": msg, "log_line": i + 1})
            continue

        m_bang = BANG.match(s)
        if m_bang:
            msg = m_bang.group("msg").strip()
            # 找后续的 l.<line> 作为行号锚点
            anchor_line = None
            for nxt in lines[i + 1:i + 6]:
                a = L_ANCHOR.match(nxt.strip())
                if a:
                    anchor_line = int(a.group(1))
                    break
            errors.append({"file": last_file or main,
                           "line": anchor_line if anchor_line else last_line,
                           "type": classify(msg), "message": msg, "log_line": i + 1})
            continue

        m_over = OVERFULL.search(s)
        if m_over:
            overfull.append({"amount_pt": float(m_over.group("amt")),
                             "lines": [int(m_over.group("l1")), int(m_over.group("l2"))]})
        if UNDERFULL.search(s):
            underfull += 1
        if LABEL_MULTI.search(s):
            warnings.append({"type": "label_multiply_defined", "message": s.strip()})

    return {
        "errors": errors,
        "warnings": warnings,
        "missing_files": missing_files,
        "undefined_refs": undef_refs,
        "undefined_cites": undef_cites,
        "overfull": overfull,
        "underfull_count": underfull,
        "converged": converged_flag,
        "error_count": len(errors),
        "first_error": errors[0] if errors else None,
    }


if __name__ == "__main__":
    import sys, json
    txt = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    print(json.dumps(parse_log(txt), ensure_ascii=False, indent=2))
