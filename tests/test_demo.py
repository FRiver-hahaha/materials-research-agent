"""冒烟测试：端到端运行流水线，断言关键产出存在且合理。
运行：python tests/test_demo.py   （在 project 根目录执行）
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src.main import load_corpus, load_yaml, build_llm, build_emb
from src.storage import (InMemoryVectorStore, InMemoryEvidenceStore,
                         InMemoryKnowledgeGraph, InMemoryEntityDB)
from src.agents import (plan_task, retrieve, SciverseAdapter, SciBaseRAGAdapter,
                        filter_papers, parse_papers, extract, normalize, fuse,
                        identify_gaps, verify, generate_report)
from src.agents.route_a import generate_hypotheses, explore, validate
from src.agents.graph import Graph, Node
from src.agents.state import AgentState


def run_pipeline(algorithm="bayes"):
    cfg = load_yaml(os.path.join(BASE, "config.yaml"))
    papers = load_corpus(os.path.join(BASE, cfg["data"]["corpus"]))
    llm, emb = build_llm(cfg), build_emb(cfg)
    vs = InMemoryVectorStore(); ev = InMemoryEvidenceStore()
    kg = InMemoryKnowledgeGraph(); edb = InMemoryEntityDB()
    rag = SciBaseRAGAdapter(vs, emb); rag.index(papers)
    sciverse = SciverseAdapter("")

    s = AgentState(task="perovskite solar cell bandgap and phase stability")
    s.papers = papers
    g = Graph()
    g.add_node(Node("plan", plan_task))
    g.add_node(Node("retrieve", lambda st: retrieve(st, sciverse, rag)))
    g.add_node(Node("filter", lambda st: filter_papers(st, top_n=6)))
    g.add_node(Node("parse", parse_papers))
    g.add_node(Node("extract", lambda st: extract(st, ev, edb)))
    g.add_node(Node("normalize", lambda st: normalize(st, edb)))
    g.add_node(Node("fuse", lambda st: fuse(st, kg, edb)))
    g.add_node(Node("gap", lambda st: identify_gaps(st, edb)))
    g.add_node(Node("hyp", lambda st: generate_hypotheses(st, llm)))
    g.add_node(Node("explore", lambda st: explore(st, llm, algorithm=algorithm)))
    g.add_node(Node("validate", validate))
    g.add_node(Node("verify", verify))
    g.add_node(Node("report", lambda st: generate_report(
        st, llm, os.path.join(BASE, cfg["data"]["output"]))))
    g.set_entry("plan")
    for a, b in [("plan", "retrieve"), ("retrieve", "filter"), ("filter", "parse"),
                 ("parse", "extract"), ("extract", "normalize"), ("normalize", "fuse"),
                 ("fuse", "gap"), ("gap", "hyp"), ("hyp", "explore"),
                 ("explore", "validate"), ("validate", "verify"), ("verify", "report")]:
        g.add_edge(a, b)
    return g.run(s)


def main():
    s = run_pipeline("bayes")
    # 断言
    assert s.retrieved_ids, "未检索到文献"
    assert s.entities, "未抽取到实体"
    assert s.gaps, "未识别 Gap"
    kinds = {g.kind for g in s.gaps}
    assert {"underexplored", "contradiction", "missing_link"} <= kinds, \
        f"Gap 类型不全: {kinds}"
    pred = [h for h in s.hypotheses if h.predicted_value is not None]
    assert pred, "路线A 未产出带预测值的假设"
    assert os.path.exists(s.report), "报告未生成"
    assert any("evidence_chain" in f for f in os.listdir(os.path.join(BASE, "data/output"))), \
        "证据链未生成"
    print(f"[PASS] retrieved={len(s.retrieved_ids)} entities={len(s.entities)} "
          f"gaps={len(s.gaps)} hypotheses={len(s.hypotheses)} report={s.report}")


if __name__ == "__main__":
    main()
