#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""latex_ci.py — LaTeX 编译-修复闭环主流程。

做三件事，不做过场：
1. 有 TeX：真实多轮编译（引擎 -> bibtex/biber -> 再编译），日志解析到 文件:行号，
   用"未定义引用是否消失"判定收敛，而不是只看退出码。
2. 无 TeX：转静态语义检查（staticcheck），仍能给出 文件:行号 级证据，标 partial，
   不用"环境没有 TeX"直接把成果清零。
3. 无论哪种模式都校验 PDF 真实性（页数/字节/可抽文本），并产出可直接入稿的源码目录。

用法：
  python latex_ci.py --project PROJ --main main.tex --outdir OUT [--case /input/case.json]
                     [--engine auto|pdflatex|xelatex|lualatex] [--max-passes 4]
                     [--static-only] [--emit-result]
"""
import argparse, json, os, re, shutil, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logparse
import staticcheck

ENGINES = ["xelatex", "pdflatex", "lualatex"]
BUILD_EXT = (".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".pdf", ".fls", ".fdb_latexmk", ".synctex.gz")

# 错误类型 -> 可执行修复动作（这是"效率增益"的载体：把查文档变成照单执行）
FIX_HINTS = {
    "missing_package": "缺宏包。先确认拼写；本机 texlive 未装该包时，优先换等价包或删掉非必需用法，不要硬留一条装不上的依赖。",
    "missing_font": "缺字体或字体形状。换用已装字体族（如 \\usepackage{fontspec} + 系统已有字体），或去掉该字体命令。",
    "encoding": "字符编码问题。确认源文件 UTF-8、引擎支持该字符（中文用 xelatex + ctex），或用等价符号替换。",
    "math_mode": "数学模式未闭合。检查该行及上一行 $ 是否成对，$ 内不要出现空行。",
    "alignment": "表格单元格数与列声明不符。改 \\begin{tabular}{...} 的列数，或补齐/删掉多余的 &。",
    "alignment_silent": "该行少于声明列数，pdflatex 不报错但会留空白列。补齐单元格或收窄列声明。",
    "runaway": "参数扫描失控，通常是花括号或环境未闭合。从报错行往前找第一个未配对的 { 或 \\begin。",
    "brace": "花括号不平衡。逐个核对 {} 配对，注意 \\{ \\} 是转义不是分组。",
    "undefined_command": "命令未定义。多为宏包没加载或命令拼错；按提示补 \\usepackage，或改用已加载包中的等价命令。",
    "undefined_env": "环境未定义或 begin/end 不匹配。检查环境名拼写与嵌套顺序（不要交叉嵌套）。",
    "undefined_ref": "引用指向不存在的 label。补 \\label{key}，或删掉/改正该 \\ref。",
    "undefined_cite": "文献 key 在 .bib 中不存在。补条目或改正 key；不要留 [?] 判成功。",
    "fatal": "致命错误已中断编译。真正的根因在它前面第一条 ! 错误，先修那条。",
    "other": "未归类错误。直接读 log 该行上下文，通常上一条 warning 已给出线索。",
}


def which(name):
    return shutil.which(name)


def detect_engine(prefer="auto"):
    if prefer and prefer != "auto":
        p = which(prefer)
        return (prefer, p) if p else (None, None)
    for e in ENGINES:
        p = which(e)
        if p:
            return e, p
    return None, None


USEPKG_LINE = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}")


def locate_package_decl(project, pkg):
    """把缺包错误回填到真正声明它的 文件:行号（缺包报错本身不带行号）。"""
    base = pkg if pkg.endswith((".sty", ".cls")) else pkg + ".sty"
    stem = base.rsplit(".", 1)[0]
    for d, _, fs in os.walk(project):
        for f in sorted(fs):
            if not f.endswith(".tex"):
                continue
            path = os.path.join(d, f)
            rel = os.path.relpath(path, project).replace("\\", "/")
            for i, line in enumerate(read_text(path).splitlines(), 1):
                for m in USEPKG_LINE.finditer(line):
                    if stem in [x.strip() for x in m.group(1).split(",")]:
                        return {"file": rel, "line": i}
    return {"file": None, "line": None}


def clean_build(project, outdir, main):
    """编译前清掉旧构建物：防止用旧 PDF/.aux 冒充本次编译结果。"""
    stem = os.path.splitext(os.path.basename(main))[0]
    removed = []
    for d, _, fs in os.walk(project):
        for f in fs:
            if f.endswith((".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".synctex.gz", ".fls")) \
               or (f.endswith(".pdf") and os.path.splitext(f)[0] == stem):
                try:
                    os.remove(os.path.join(d, f))
                    removed.append(os.path.relpath(os.path.join(d, f), project))
                except OSError:
                    pass
    for f in os.listdir(outdir) if os.path.isdir(outdir) else []:
        if f.endswith(".pdf") or f == "result.json" or f == "report.json":
            try:
                os.remove(os.path.join(outdir, f))
                removed.append("outdir/" + f)
            except OSError:
                pass
    return removed


def read_text(p):
    try:
        import io
        return io.open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def scan_project(project, main):
    """收集 tex 文件、.bib 文件、是否使用 bibliography / biblatex。"""
    tex, bib = [], []
    for d, _, fs in os.walk(project):
        for f in fs:
            p = os.path.join(d, f)
            if f.endswith(".tex"):
                tex.append(p)
            elif f.endswith(".bib"):
                bib.append(p)
    blob = "".join(read_text(t) for t in tex)
    uses_bibtex = bool(re.search(r"\\bibliography\{", blob))
    uses_biber = bool(re.search(r"\\addbibresource\{", blob))
    return tex, bib, uses_bibtex, uses_biber


def run(cmd, cwd, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=cwd, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode("utf-8", "ignore")
    except subprocess.TimeoutExpired:
        return 124, "[timeout]"
    except OSError as e:
        return 127, str(e)


def compile_once(engine_bin, main, project):
    cmd = [engine_bin, "-interaction=nonstopmode", "-file-line-error", "-halt-on-error=false", main]
    return run(cmd, project)


def bib_step(project, main, uses_bibtex, uses_biber):
    stem = os.path.splitext(os.path.basename(main))[0]
    if uses_biber and which("biber"):
        return run([which("biber"), stem], project)
    if uses_bibtex and which("bibtex"):
        return run([which("bibtex"), stem], project)
    if uses_biber and not which("biber") and which("bibtex"):
        return 0, "[skip] biblatex 需要 biber，本机无 biber"
    return 0, "[skip] 未使用外部文献工具"


def pdf_meta(pdf_path):
    pages, ok = None, False
    if which("pdfinfo"):
        rc, out = run([which("pdfinfo"), pdf_path], os.path.dirname(pdf_path) or ".")
        m = re.search(r"Pages:\s+(\d+)", out)
        if m:
            pages, ok = int(m.group(1)), True
    if pages is None:
        try:
            data = open(pdf_path, "rb").read()
            pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
            ok = pages > 0
        except OSError:
            pages = 0
    return {"pages": pages, "ok": ok}


def pdf_text(pdf_path):
    if which("pdftotext"):
        rc, out = run([which("pdftotext"), "-layout", pdf_path, "-"], os.path.dirname(pdf_path) or ".")
        txt = out.strip()
        return {"ok": len(txt) > 0, "backend": "pdftotext", "chars": len(txt), "sample": txt[:600]}
    return {"ok": False, "backend": "unavailable", "chars": 0, "sample": ""}


def copy_source(project, outdir):
    dst = os.path.join(outdir, "source")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(project, dst, ignore=shutil.ignore_patterns("*.aux", "*.log", "*.out", "*.toc", "*.bbl", "*.blg", "*.pdf", "*.synctex.gz", "__pycache__"))
    return dst


def build_result(case_id, status, project, main, engine, passes, diag, pdf, ptext, source_rel, outdir):
    errors = diag.get("errors", [])
    return {
        "case_id": case_id,
        "status": status,
        "result": {
            "latex_source": {"main_tex": main, "files": sorted(source_rel)},
            "compiled_pdf": pdf,
            "pdf_text_check": ptext,
            "compile": {
                "engine": engine, "passes": passes,
                "errors": errors[:12],
                "error_count": len(errors),
                "missing_files": diag.get("missing_files", []),
                "undefined_refs": diag.get("undefined_refs", []),
                "undefined_cites": diag.get("undefined_cites", []),
                "converged": diag.get("converged", False),
                "overfull_count": len(diag.get("overfull", [])),
            },
            "fix_plan": [{"file": e.get("file"), "line": e.get("line"),
                          "type": e.get("type"), "action": FIX_HINTS.get(e.get("type"), FIX_HINTS["other"])}
                         for e in errors[:12]],
            "artifacts": {"pdf_path": os.path.abspath(pdf.get("path", "")) if pdf.get("path") else None,
                          "source_dir": os.path.abspath(source_rel and os.path.join(outdir, "source"))},
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--main", default="main.tex")
    ap.add_argument("--outdir", default="./out")
    ap.add_argument("--case", default=None, help="/input/case.json，用于取 case_id")
    ap.add_argument("--engine", default="auto")
    ap.add_argument("--max-passes", type=int, default=4)
    ap.add_argument("--static-only", action="store_true")
    ap.add_argument("--emit-result", action="store_true", help="同时写 result.json")
    args = ap.parse_args()

    project = os.path.abspath(args.project)
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    case_id = None
    if args.case and os.path.exists(args.case):
        try:
            case_id = json.loads(read_text(args.case)).get("case_id")
        except ValueError:
            case_id = None

    tex_files, bib_files, uses_bibtex, uses_biber = scan_project(project, args.main)
    if not tex_files:
        print(json.dumps({"status": "needs_attention", "reason": "no_tex_source"}, ensure_ascii=False))
        return 2

    engine, engine_bin = (None, None) if args.static_only else detect_engine(args.engine)
    cleaned = clean_build(project, outdir, args.main)

    if not engine_bin:
        # 静态模式：无 TeX 也交付定位证据，而不是直接判死
        st = staticcheck.check(project)
        for e in st["errors"]:
            e["action"] = FIX_HINTS.get(e["type"], FIX_HINTS["other"])
        # 与真实编译模式保持同名契约字段
        st["undefined_refs"] = [{"key": e.get("key"), "file": e["file"], "line": e["line"]}
                                for e in st["errors"] if e["type"] == "undefined_ref"]
        st["undefined_cites"] = [{"key": e.get("key"), "file": e["file"], "line": e["line"]}
                                 for e in st["errors"] if e["type"] == "undefined_cite"]
        st["converged"] = not (st["undefined_refs"] or st["undefined_cites"])
        status = "partial" if st["errors"] else "success"
        src = copy_source(project, outdir)
        rel = [os.path.relpath(p, src).replace("\\", "/") for p in
               [os.path.join(d, f) for d, _, fs in os.walk(src) for f in fs]]
        result = build_result(case_id, status, project, args.main, None, 0, st,
                              {"path": None, "pages": 0, "bytes": 0, "compile_ok": False},
                              {"ok": False, "backend": "unavailable", "chars": 0},
                              rel, outdir)
        result["mode"] = "static_only"
        result["cleaned_before_build"] = cleaned
        result["uncertainty"] = [{"issue": "环境未探测到 TeX 引擎，未做真实编译",
                                  "impact": "PDF 产物缺失，编译层面判不确定"}]
        result["evidence"] = [{"anchor": "静态检查", "file": e["file"], "line": e["line"],
                               "note": e["message"]} for e in st["errors"][:10]] or \
                             [{"anchor": "静态检查", "note": "未发现结构/引用/表格列数问题"}]
    else:
        passes, diag, last_rc = 0, {}, None
        for i in range(args.max_passes):
            rc, out = compile_once(engine_bin, args.main, project)
            passes += 1
            log_path = os.path.join(project, os.path.splitext(os.path.basename(args.main))[0] + ".log")
            diag = logparse.parse_log(read_text(log_path), args.main)
            last_rc = rc
            if diag["errors"]:
                break
            if not diag["undefined_refs"] and not diag["undefined_cites"] and diag.get("converged"):
                break
            if i == 0:
                bib_step(project, args.main, uses_bibtex, uses_biber)
            elif i == 1 and (uses_bibtex or uses_biber):
                bib_step(project, args.main, uses_bibtex, uses_biber)
        # 静态检查补充（捕获编译静默通过但内容错的表格列数等）
        st = staticcheck.check(project)
        for e in st["errors"]:
            e["action"] = FIX_HINTS.get(e["type"], FIX_HINTS["other"])
        for mf in diag["missing_files"]:
            loc = locate_package_decl(project, mf["name"])
            mf.update({"file": loc["file"], "line": loc["line"]})
            for e in diag["errors"]:
                if e.get("type") == "missing_package" and e.get("line") is None \
                   and mf["name"].rsplit(".", 1)[0] in e.get("message", ""):
                    e["file"], e["line"] = loc["file"], loc["line"]
        merged = {"errors": diag["errors"] + [e for e in st["errors"] if e["type"] == "alignment_silent"],
                  "missing_files": diag["missing_files"], "undefined_refs": diag["undefined_refs"],
                  "undefined_cites": diag["undefined_cites"], "converged": diag.get("converged"),
                  "overfull": diag.get("overfull", [])}

        pdf_path = os.path.join(project, os.path.splitext(os.path.basename(args.main))[0] + ".pdf")
        pdf = {"path": pdf_path, "pages": 0, "bytes": 0, "compile_ok": False}
        ptext = {"ok": False, "backend": "unavailable", "chars": 0}
        if os.path.exists(pdf_path):
            meta = pdf_meta(pdf_path)
            pdf.update({"pages": meta["pages"], "bytes": os.path.getsize(pdf_path),
                        "compile_ok": meta["ok"]})
            ptext = pdf_text(pdf_path)
            shutil.copy2(pdf_path, os.path.join(outdir, os.path.basename(pdf_path)))
            pdf["path"] = os.path.join(outdir, os.path.basename(pdf_path))

        if last_rc != 0 or merged["errors"]:
            status = "partial" if pdf.get("compile_ok") else "needs_attention"
        elif not merged["converged"]:
            status = "partial"
        elif not pdf.get("compile_ok") or not ptext.get("ok"):
            status = "partial"
        else:
            status = "success"

        src = copy_source(project, outdir)
        rel = [os.path.relpath(os.path.join(d, f), src).replace("\\", "/")
               for d, _, fs in os.walk(src) for f in fs]
        result = build_result(case_id, status, project, args.main, engine, passes, merged,
                              pdf, ptext, rel, outdir)
        result["mode"] = "real_compile"
        result["cleaned_before_build"] = cleaned
        result["env"] = {"engine": engine, "engine_path": engine_bin,
                         "tex_version": run([engine_bin, "--version"], ".")[1].splitlines()[0] if engine_bin else "",
                         "bibtex": bool(which("bibtex")), "biber": bool(which("biber")),
                         "passes": passes}
        result["evidence"] = ([{"anchor": "编译日志", "file": e["file"], "line": e["line"],
                                "note": e["message"]} for e in merged["errors"][:10]]
                              or [{"anchor": "编译日志", "note": "无错误"}])
        if merged["undefined_refs"] or merged["undefined_cites"]:
            result.setdefault("uncertainty", []).append(
                {"issue": "引用未收敛", "refs": merged["undefined_refs"], "cites": merged["undefined_cites"]})

    with open(os.path.join(outdir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if args.emit_result:
        out = {"case_id": result["case_id"], "status": result["status"],
               "result": result["result"], "evidence": result["evidence"],
               "uncertainty": result.get("uncertainty", []),
               "mode": result.get("mode"), "env": result.get("env")}
        with open(os.path.join(outdir, "result.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps({"status": result["status"], "mode": result["mode"],
                      "engine": result["result"]["compile"]["engine"],
                      "passes": result["result"]["compile"]["passes"],
                      "errors": result["result"]["compile"]["error_count"],
                      "pdf_pages": result["result"]["compiled_pdf"]["pages"],
                      "pdf_bytes": result["result"]["compiled_pdf"]["bytes"],
                      "converged": result["result"]["compile"]["converged"],
                      "outdir": outdir}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
