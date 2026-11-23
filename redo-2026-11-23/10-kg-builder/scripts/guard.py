#!/usr/bin/env python3
"""10 知识图谱轻量校验：节点/边来源齐全、端点存在、答案 trace 可回链。

实体抽取与关系判断由 Agent 把握；脚本只查图内一致性与回指闭环。
"""
import argparse
import json
import os
import sys

STATUS = {"success", "partial", "needs_attention"}


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

    graph = res.get("graph")
    if not isinstance(graph, dict):
        errors.append("graph 不是对象")
        graph = {"nodes": [], "edges": []}

    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        errors.append("graph.nodes 不是数组")
        nodes = []
    node_ids = set()
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            errors.append(f"nodes[{i}] 不是对象")
            continue
        nid = str(n.get("id", ""))
        if not nid:
            errors.append(f"nodes[{i}] 缺 id")
        else:
            node_ids.add(nid)
        if not n.get("label"):
            errors.append(f"节点 {nid} 缺 label")
        if not n.get("source"):
            errors.append(f"节点 {nid} 缺 source")

    edges = graph.get("edges")
    if not isinstance(edges, list):
        errors.append("graph.edges 不是数组")
        edges = []
    connected = set()
    edge_ids = set()
    for i, e in enumerate(edges):
        if not isinstance(e, dict):
            errors.append(f"edges[{i}] 不是对象")
            continue
        eid = str(e.get("id", ""))
        if eid:
            edge_ids.add(eid)
        s, t = str(e.get("source", "")), str(e.get("target", ""))
        if not e.get("relation"):
            errors.append(f"edges[{i}] 缺 relation")
        for endpoint, name in ((s, "source"), (t, "target")):
            if endpoint and endpoint not in node_ids:
                errors.append(f"edges[{i}] {name} 指向不存在节点 {endpoint}")
        if s:
            connected.add(s)
        if t:
            connected.add(t)
        if not e.get("source_doc") and not e.get("evidence"):
            warnings.append(f"edges[{i}] 缺 source_doc 与 evidence")

    isolated = node_ids - connected
    if isolated:
        warnings.append(f"孤立节点（需补边或进 uncertainty）: {sorted(isolated)}")

    answers = res.get("query_answers")
    if not isinstance(answers, list):
        errors.append("query_answers 不是数组")
        answers = []
    if len(answers) < 3:
        warnings.append("query_answers 少于 3 条")
    for i, a in enumerate(answers):
        if not isinstance(a, dict):
            errors.append(f"query_answers[{i}] 不是对象")
            continue
        for field in ("query_id", "answer", "trace", "sources"):
            if not a.get(field):
                errors.append(f"query_answers[{i}] 缺 {field}")
        trace = a.get("trace") or []
        if isinstance(trace, list):
            for nid in trace:
                if str(nid) not in node_ids and str(nid) not in edge_ids:
                    errors.append(f"答案 {a.get('query_id', i)} trace 命中图外节点/边 {nid}")
        sources = a.get("sources")
        if isinstance(sources, dict):
            for nid in sources.get("matched_nodes", []) or []:
                if str(nid) not in node_ids:
                    errors.append(f"答案 {a.get('query_id', i)} matched_nodes 含图外节点 {nid}")

    coverage = res.get("coverage")
    if not isinstance(coverage, dict):
        warnings.append("缺 coverage")
    else:
        for field in ("queries", "answerable", "nodes", "edges", "isolated"):
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
