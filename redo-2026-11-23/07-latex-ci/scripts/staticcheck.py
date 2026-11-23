#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""staticcheck.py — 不依赖 TeX 的源码级语义检查。

为什么需要它：实测发现"表格声明 3 列却只填 2 列数据"这类错误 pdflatex 不报错、
静默产出空白列并正常出 PDF。只靠编译退出码会把错的内容判成 success。
本模块在无 TeX 的环境里也能把这些错误定位到 文件:行号，作为真实证据交付。
"""
import io, os, re

BEGIN_ENV = re.compile(r"\\begin\{(?P<env>[^}]+)\}")
END_ENV = re.compile(r"\\end\{(?P<env>[^}]+)\}")
LABEL = re.compile(r"\\label\{(?P<key>[^}]+)\}")
REF = re.compile(r"\\(?:ref|eqref|autoref|pageref|cref|Cref)\{(?P<key>[^}]+)\}")
CITE = re.compile(r"\\(?:cite|citep|citet|parencite|textcite|autocite|nocite)\*?(?:\[[^\]]*\])*\{(?P<key>[^}]+)\}")
TABULAR = re.compile(r"\\begin\{(?P<env>tabular[a-z]*|array)\}\{(?P<spec>[^}]*)\}")
USEPKG = re.compile(r"\\usepackage(?:\[[^\]]*])?\{(?P<pkgs>[^}]+)\}")
BIB_ENTRY = re.compile(r"@\w+\s*\{\s*(?P<key>[^,\s]+)\s*,")

# 命令 -> 所属宏包（用于"命令用了但宏包没声明"的检查，只收高置信度映射）
CMD_PACKAGE = {
    "\\toprule": "booktabs", "\\midrule": "booktabs", "\\bottomrule": "booktabs",
    "\\eqref": "amsmath", "\\text": "amsmath", "\\mathbb": "amssymb",
    "\\includegraphics": "graphicx", "\\SI": "siunitx", "\\num": "siunitx",
    "\\bm": "bm", "\\checkmark": "amssymb",
}

TRIVIAL_LINES = re.compile(r"^\s*(%|\\hline|\\toprule|\\midrule|\\bottomrule|\\cline|\\end|\\begin|\\caption|\\centering|\\label|$)")


def iter_tex_files(root):
    for d, _, fs in os.walk(root):
        for f in sorted(fs):
            if f.endswith(".tex"):
                yield os.path.join(d, f)


def read(path):
    try:
        return io.open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return None


def strip_comments(text):
    """去掉 % 注释，保留换行以便行号不偏。"""
    out = []
    for line in text.splitlines():
        # 处理 \% 转义
        idx = None
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                idx = i
                break
            i += 1
        out.append(line if idx is None else line[:idx])
    return "\n".join(out)


def spec_columns(spec):
    """把 {lll} / {p{3cm}l} / {@{}lll@{}} 解析成列数。"""
    s = re.sub(r"@\{\}", "", spec)
    s = re.sub(r"@\{[^}]*\}", "", s)
    s = re.sub(r"!\{[^}]*\}", "", s)
    s = re.sub(r">\{[^}]*\}", "", s)
    s = re.sub(r"<\{[^}]*\}", "", s)
    cols = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c in "lcrX":
            cols += 1
            i += 1
        elif c in "pmb":
            cols += 1
            # 跳过参数 {..}
            depth = 0
            j = i + 1
            while j < len(s):
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            i = j + 1
        elif c == "*":
            i += 1
        else:
            i += 1
    return cols


def count_cols_in_row(line):
    """统计一行中未被花括号保护的 & 个数；返回 (单元格数, 是否含多列合并)。"""
    depth = 0
    amps = 0
    has_multi = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\":
            # 跳过转义序列（如 \&）
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == "&" and depth == 0:
            amps += 1
        i += 1
    if "\\multicolumn" in line or "\\multirow" in line:
        has_multi = True
    return amps + 1, has_multi


def check_tabular_cols(report, path, text):
    """表格列数一致性：每行单元格数与列声明比较。"""
    lines = text.splitlines()
    for li, line in enumerate(lines, 1):
        m = TABULAR.search(line)
        if not m:
            continue
        ncol = spec_columns(m.group("spec"))
        env = m.group("env")
        depth = 1
        # 从 begin 行往后扫到匹配的 \end
        j = li  # 0-based next line index
        rowbuf = []
        # 若 begin 行同一行有内容，先取该行 begin 之后部分
        tail = line[m.end():]
        if tail.strip():
            rowbuf.append((li, tail))
        while j < len(lines):
            cur = lines[j]
            if "\\end{%s}" % env in cur:
                break
            if "\\begin{%s}" % env in cur and j != li - 1:
                depth += 1
            if "\\end{%s}" % env in cur:
                depth -= 1
                if depth == 0:
                    break
            if not TRIVIAL_LINES.match(cur):
                rowbuf.append((j + 1, cur))
            j += 1
        for rline, rtext in rowbuf:
            if "\\\\" not in rtext and rline != rowbuf[-1][0]:
                # 行末尾没有 \\ 说明数据可能跨行续写，跳过严格判定
                pass
            ncell, has_multi = count_cols_in_row(rtext)
            if has_multi:
                continue
            if ncell > ncol:
                report["errors"].append({
                    "file": path, "line": rline, "type": "alignment",
                    "message": "该行有 %d 个单元格，但表格声明只有 %d 列（%s）" % (ncell, ncol, m.group("spec")),
                })
            elif ncell < ncol and rtext.strip() and not rtext.strip().startswith("%"):
                # 少于声明列数：静默空白列，pdflatex 不报错，必须静态捕获
                report["errors"].append({
                    "file": path, "line": rline, "type": "alignment_silent",
                    "message": "该行只有 %d 个单元格，表格声明 %d 列，将产生空白列且编译不报错" % (ncell, ncol),
                })


def check_structure(report, path, text):
    """环境配对、数学模式、花括号。"""
    stack = []
    for li, line in enumerate(text.splitlines(), 1):
        for m in BEGIN_ENV.finditer(line):
            stack.append((m.group("env"), li))
        for m in END_ENV.finditer(line):
            env = m.group("env")
            if not stack:
                report["errors"].append({"file": path, "line": li, "type": "undefined_env",
                                         "message": "\\end{%s} 前没有对应的 \\begin" % env})
                continue
            if stack[-1][0] != env:
                report["errors"].append({
                    "file": path, "line": li, "type": "undefined_env",
                    "message": "\\end{%s} 与第 %d 行的 \\begin{%s} 不匹配（嵌套错位）" % (env, stack[-1][1], stack[-1][0])})
                stack.pop()
            else:
                stack.pop()
    for env, li in stack:
        report["errors"].append({"file": path, "line": li, "type": "undefined_env",
                                 "message": "\\begin{%s} 没有闭合的 \\end{%s}" % (env, env)})

    # 美元符号配对（粗略，跳过 \$ 与 $$）
    for li, line in enumerate(text.splitlines(), 1):
        cnt = 0
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "$":
                cnt += 1
            i += 1
        if cnt % 2 != 0:
            report["errors"].append({"file": path, "line": li, "type": "math_mode",
                                     "message": "该行 $ 数量为奇数，数学模式可能未闭合"})


def check_refs(report, tex_texts):
    labels, refs, cites = set(), [], []
    for path, text in tex_texts:
        for m in LABEL.finditer(text):
            labels.add(m.group("key"))
        for li, line in enumerate(text.splitlines(), 1):
            for m in REF.finditer(line):
                for k in m.group("key").split(","):
                    refs.append({"key": k.strip(), "file": path, "line": li})
            for m in CITE.finditer(line):
                for k in m.group("key").split(","):
                    if k.strip() and k.strip() != "*":
                        cites.append({"key": k.strip(), "file": path, "line": li})
    return labels, refs, cites


def check_packages(report, path, text, declared_pkgs):
    for cmd, pkg in CMD_PACKAGE.items():
        if cmd + "{" in text or (cmd in text and cmd not in ("\\text",)):
            if pkg not in declared_pkgs:
                # 找首次出现的行
                for li, line in enumerate(text.splitlines(), 1):
                    if cmd in line:
                        report["errors"].append({
                            "file": path, "line": li, "type": "undefined_command",
                            "message": "使用了 %s 但未 \\usepackage{%s}" % (cmd, pkg)})
                        break


def check(root, main="main.tex", bib_files=None):
    report = {"errors": [], "warnings": [], "checked_files": [], "labels": [], "refs": [],
              "cites": [], "bib_keys": [], "has_tex": False}
    tex_texts = []
    declared_pkgs = set()
    for path in iter_tex_files(root):
        text = read(path)
        if text is None:
            continue
        text = strip_comments(text)
        rel = os.path.relpath(path, root)
        report["checked_files"].append(rel)
        report["has_tex"] = True
        tex_texts.append((rel, text))
        for m in USEPKG.finditer(text):
            for p in m.group("pkgs").split(","):
                declared_pkgs.add(p.strip())
        check_structure(report, rel, text)
        check_tabular_cols(report, rel, text)
        check_packages(report, rel, text, declared_pkgs)

    labels, refs, cites = check_refs(report, tex_texts)
    report["labels"] = sorted(labels)
    report["refs"] = refs
    report["cites"] = cites

    bib_keys = set()
    bib_paths = []
    for path in (bib_files or []):
        t = read(path)
        if t:
            bib_paths.append(path)
            for m in BIB_ENTRY.finditer(t):
                bib_keys.add(m.group("key"))
    if not bib_paths:
        for d, _, fs in os.walk(root):
            for f in fs:
                if f.endswith(".bib"):
                    p = os.path.join(d, f)
                    t = read(p)
                    if t:
                        for m in BIB_ENTRY.finditer(t):
                            bib_keys.add(m.group("key"))
    report["bib_keys"] = sorted(bib_keys)

    for r in refs:
        if r["key"] not in labels:
            report["errors"].append({"file": r["file"], "line": r["line"], "type": "undefined_ref",
                                     "key": r["key"],
                                     "message": "引用了未定义的 label `%s`" % r["key"]})
    for c in cites:
        if bib_keys and c["key"] not in bib_keys:
            report["errors"].append({"file": c["file"], "line": c["line"], "type": "undefined_cite",
                                     "key": c["key"],
                                     "message": "引用了 .bib 中不存在的 key `%s`" % c["key"]})
    return report


if __name__ == "__main__":
    import sys, json
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(check(root), ensure_ascii=False, indent=2))
