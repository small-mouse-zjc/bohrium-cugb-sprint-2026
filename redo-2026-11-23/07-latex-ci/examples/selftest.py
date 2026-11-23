#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selftest.py — 用临时工程验证引擎在四类情形下的判定是否与预期一致。

断言的是行为，不是分数：
1. 健康工程 -> success，PDF 真存在；
2. 缺宏包   -> needs_attention，错误定位到 \\usepackage 所在 文件:行号；
3. 永不收敛的 \\ref -> partial，undefined_refs 非空（不许判 success）；
4. 表格少填一列（编译不报错）-> 非 success，且命中 alignment_silent。

第 4 条是本 Skill 存在的理由：pdflatex 对这类错误完全静默。
无 TeX 时自动降级为静态模式，第 3、4 条仍必须命中。
"""
import io, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
import latex_ci
import staticcheck

DEMO = os.path.join(HERE, "demo_project")
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name + ((" | " + detail) if detail and not cond else ""))
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  -> " + detail) if detail and not cond else ""))


def make_case(tmp, mutate):
    dst = os.path.join(tmp, "proj")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(DEMO, dst)
    mutate(dst)
    return dst


def run_ci(project, outdir):
    out = os.path.join(os.path.dirname(project), "out")
    rp = os.path.join(out, "report.json")
    if os.path.exists(rp):
        os.remove(rp)
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "latex_ci.py"),
                         "--project", project, "--outdir", out],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    if not os.path.exists(rp):
        return None
    return json.loads(io.open(rp, encoding="utf-8").read())


def patch(path, old, new):
    s = io.open(path, encoding="utf-8").read()
    if old not in s:
        raise SystemExit("selftest 注入失败，模板已变：%s" % old)
    io.open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))


def main():
    tmp = tempfile.mkdtemp(prefix="latexci_selftest_")
    engine, _ = latex_ci.detect_engine("auto")
    print("TeX 引擎: %s\n" % (engine or "未探测到（进入静态模式断言）"))

    # 1 健康
    p = make_case(tmp, lambda d: None)
    d = run_ci(p, "out")
    check("健康工程判 success", d and d["status"] == "success", str(d and d["status"]))
    if engine:
        pdf = d["result"]["compiled_pdf"]
        check("健康工程产出真实 PDF", pdf["bytes"] > 0 and pdf["pages"] > 0,
              "bytes=%s pages=%s" % (pdf["bytes"], pdf["pages"]))
        check("引用收敛", d["result"]["compile"]["converged"] is True)

    # 2 缺宏包
    def add_pkg(d):
        patch(os.path.join(d, "main.tex"), "\\usepackage{booktabs}",
              "\\usepackage{booktabs}\n\\usepackage{nonexistentpkgxyz}")
    p = make_case(tmp, add_pkg)
    d = run_ci(p, "out")
    if engine:
        check("缺宏包不判 success", d and d["status"] != "success", str(d and d["status"]))
        types = [e.get("type") for e in d["result"]["compile"]["errors"]]
        check("缺宏包被识别", "missing_package" in types, str(types))
        mf = d["result"]["compile"]["missing_files"]
        check("缺宏包定位到 \\usepackage 行", bool(mf) and mf[0].get("line") is not None,
              str(mf[:1]))
    else:
        st = staticcheck.check(p)
        check("静态模式可运行", st["has_tex"] is True)

    # 3 永不收敛的引用
    def bad_ref(d):
        patch(os.path.join(d, "sections/intro.tex"), "\\ref{sec:methods}", "\\ref{sec:nope}")
    p = make_case(tmp, bad_ref)
    d = run_ci(p, "out")
    check("坏引用不判 success", d and d["status"] != "success", str(d and d["status"]))
    ur = d["result"]["compile"].get("undefined_refs", []) if d else []
    check("坏引用被抓到", any(u.get("key") == "sec:nope" for u in ur), str(ur))
    st = staticcheck.check(p)
    check("静态检查独立也能定位坏引用",
          any("sec:nope" in e["message"] for e in st["errors"]), str(st["errors"][:1]))

    # 4 表格少填一列
    def short_row(d):
        patch(os.path.join(d, "main.tex"), "Ours     & 0.88 & 0.21 \\\\", "Ours     & 0.88 \\\\")
    p = make_case(tmp, short_row)
    d = run_ci(p, "out")
    check("表格少列不判 success", d and d["status"] != "success", str(d and d["status"]))
    types = [e.get("type") for e in d["result"]["compile"]["errors"]] if d else []
    check("表格少列命中 alignment_silent", "alignment_silent" in types, str(types))
    if engine:
        check("表格少列时 PDF 仍生成（证明编译不报错）",
              d["result"]["compiled_pdf"]["bytes"] > 0, "bytes=%s" % d["result"]["compiled_pdf"]["bytes"])

    # 5 静态检查不产生噪声：健康工程零错误
    st = staticcheck.check(DEMO)
    check("健康工程静态检查零误报", st["errors"] == [], str(st["errors"][:2]))

    shutil.rmtree(tmp, ignore_errors=True)
    print("\nPASS=%d FAIL=%d" % (len(PASS), len(FAIL)))
    if FAIL:
        print("失败项:")
        for f in FAIL:
            print(" -", f)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
