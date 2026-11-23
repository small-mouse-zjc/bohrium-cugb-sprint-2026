import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import guard  # noqa: E402


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    case = load("smoke_input.json")
    good = load("smoke_output.json")

    tmp = tempfile.mkdtemp()
    try:
        pdf = os.path.join(tmp, "main.pdf")
        with open(pdf, "wb") as f:
            f.write(b"%PDF-1.4 dummy body\n")
        good["result"]["compiled_pdf"]["bytes"] = os.path.getsize(pdf)

        rep = guard.check_result(good, case, outdir=tmp)
        assert rep["ok"], f"合法样例应通过: {rep}"

        bad = json.loads(json.dumps(good))
        bad["result"]["compiled_pdf"]["path"] = "nope.pdf"
        rep = guard.check_result(bad, case, outdir=tmp)
        assert not rep["ok"] and any("不存在" in e for e in rep["errors"]), rep

        empty = os.path.join(tmp, "empty.pdf")
        open(empty, "wb").close()
        bad2 = json.loads(json.dumps(good))
        bad2["result"]["compiled_pdf"]["path"] = "empty.pdf"
        rep = guard.check_result(bad2, case, outdir=tmp)
        assert not rep["ok"] and any("字节数为 0" in e for e in rep["errors"]), rep
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("07 selftest OK")


if __name__ == "__main__":
    main()
