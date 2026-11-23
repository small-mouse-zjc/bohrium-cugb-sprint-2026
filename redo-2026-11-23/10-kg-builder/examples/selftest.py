import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import guard  # noqa: E402


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    case = load("smoke_input.json")
    good = load("smoke_output.json")

    rep = guard.check_result(good, case, outdir=HERE)
    assert rep["ok"], f"合法样例应通过: {rep}"

    bad = json.loads(json.dumps(good))
    bad["result"]["graph"]["edges"][0]["target"] = "n99"
    rep = guard.check_result(bad, case, outdir=HERE)
    assert not rep["ok"] and any("不存在节点" in e for e in rep["errors"]), rep

    bad2 = json.loads(json.dumps(good))
    bad2["result"]["query_answers"][0]["trace"] = ["n99"]
    rep = guard.check_result(bad2, case, outdir=HERE)
    assert not rep["ok"] and any("图外节点" in e for e in rep["errors"]), rep

    print("10 selftest OK")


if __name__ == "__main__":
    main()
