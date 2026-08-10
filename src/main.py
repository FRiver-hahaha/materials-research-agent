"""材料科学文献调研智能体 — 入口。
运行：从项目根目录执行  `python -m src.main`
分层：存储层(storage) / 模型层(model) / 业务层(agents)，由轻量状态图编排。"""
import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)


def _scalar(v):
    if v in ("true", "false"):
        return v == "true"
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1]
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def load_yaml(path):
    """极简 YAML 解析（仅支持本项目扁平+两级嵌套结构，零依赖）。"""
    root = {}
    stack = [(-1, root)]
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            # 剥离行内注释（# 不出现在引号内的简单处理）
            if "#" in s and not (s.count('"') % 2) and not (s.count("'") % 2):
                s = s[:s.index("#")].rstrip()
                if not s:
                    continue
            indent = len(line) - len(line.lstrip(" "))
            key, _, val = s.partition(":")
            val = val.strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            parent = stack[-1][1]
            if val == "":
                node = {}
                parent[key] = node
                stack.append((indent, node))
            else:
                parent[key] = _scalar(val)
    return root


from src.agents import (Graph, Node, plan_task, retrieve, SciverseAdapter,
                        SciBaseRAGAdapter, filter_papers, parse_papers, extract,
                        normalize, fuse, identify_gaps, verify, generate_report)
from src.agents.llm_extraction import llm_extract
from src.agents.route_a import generate_hypotheses, explore, validate
from src.storage import (InMemoryVectorStore, InMemoryEvidenceStore,
                         InMemoryKnowledgeGraph, InMemoryEntityDB)
from src.model import MockLLM, OpenAICompatible, MockEmbedding, OpenAIEmbedding
from src.agents.state import AgentState, Paper


def load_corpus(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    papers = {}
    for p in data["papers"]:
        papers[p["paper_id"]] = Paper(
            paper_id=p["paper_id"], title=p["title"], authors=p.get("authors", []),
            year=p.get("year", 0), abstract=p.get("abstract", ""),
            parsed=p.get("parsed", {}), url=p.get("url"))
    return papers


def build_llm(cfg):
    l = cfg.get("llm", {})
    if l.get("provider") == "openai":
        o = l.get("openai", {})
        key = o.get("api_key") or os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
        if key:
            return OpenAICompatible(o.get("base_url", ""), key, o.get("model", ""))
    return MockLLM()


def build_emb(cfg):
    e = cfg.get("embedding", {})
    if e.get("provider") == "openai":
        o = e.get("openai", {})
        key = o.get("api_key") or os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
        if key:
            return OpenAIEmbedding(o.get("base_url", ""), key, o.get("model", ""))
    return MockEmbedding()


def main():
    ap = argparse.ArgumentParser(description="材料科学文献调研智能体")
    ap.add_argument("--task", default="perovskite solar cell bandgap and phase stability structure-property relationship")
    ap.add_argument("--algorithm", default=None, choices=["bayes", "genetic"])
    ap.add_argument("--corpus", default=None, help="本地语料路径；传空串 '' 则仅用 Sciverse 真实检索")
    ap.add_argument("--config", default=os.path.join(BASE, "config.yaml"))
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    algo = args.algorithm or cfg.get("route_a", {}).get("algorithm", "bayes")
    dcfg = cfg.get("data", {})

    llm, emb = build_llm(cfg), build_emb(cfg)
    corpus_path = args.corpus if args.corpus is not None else dcfg.get("corpus")
    if corpus_path and os.path.exists(os.path.join(BASE, corpus_path)):
        papers = load_corpus(os.path.join(BASE, corpus_path))
    else:
        papers = {}
        print(f"[warn] 未加载本地语料（corpus={corpus_path!r}），将仅依赖 Sciverse 检索")

    vs = InMemoryVectorStore()
    ev = InMemoryEvidenceStore()
    kg = InMemoryKnowledgeGraph()
    edb = InMemoryEntityDB()
    rag = SciBaseRAGAdapter(vs, emb)
    rag.index(papers)
    sciverse = SciverseAdapter(cfg.get("sciverse", {}).get("api_key", ""),
                                cfg.get("sciverse", {}).get("base_url", ""))

    state = AgentState(task=args.task)
    state.papers = papers

    g = Graph()
    g.add_node(Node("plan", plan_task))
    g.add_node(Node("retrieve", lambda s: retrieve(s, sciverse, rag)))
    g.add_node(Node("filter", lambda s: filter_papers(s, top_n=6)))
    g.add_node(Node("parse", parse_papers))
    g.add_node(Node("extract", lambda s: llm_extract(s, ev, edb, llm) if llm.is_real() else extract(s, ev, edb)))
    g.add_node(Node("normalize", lambda s: normalize(s, edb)))
    g.add_node(Node("fuse", lambda s: fuse(s, kg, edb)))
    g.add_node(Node("gap", lambda s: identify_gaps(s, edb, llm)))
    g.add_node(Node("routeA_hyp", lambda s: generate_hypotheses(s, llm)))
    g.add_node(Node("routeA_explore", lambda s: explore(s, llm, algorithm=algo)))
    g.add_node(Node("routeA_validate", validate))
    g.add_node(Node("verify", verify))
    g.add_node(Node("report", lambda s: generate_report(
        s, llm, os.path.join(BASE, dcfg.get("output", "data/output")))))

    g.set_entry("plan")
    for a, b in [("plan", "retrieve"), ("retrieve", "filter"), ("filter", "parse"),
                 ("parse", "extract"), ("extract", "normalize"), ("normalize", "fuse"),
                 ("fuse", "gap"), ("gap", "routeA_hyp"), ("routeA_hyp", "routeA_explore"),
                 ("routeA_explore", "routeA_validate"), ("routeA_validate", "verify"),
                 ("verify", "report")]:
        g.add_edge(a, b)

    state = g.run(state)

    print("=" * 64)
    print(f"任务方向 : {state.task}")
    print(f"检索/筛选 : {len(state.retrieved_ids)} / {len(state.filtered_ids)} 篇")
    print(f"实体/证据 : {len(state.entities)} / {len(state.evidence)}")
    print(f"知识图谱 : {len(kg.nodes())} 节点 / {len(kg.edges())} 边")
    print(f"Gap / 假设: {len(state.gaps)} / {len(state.hypotheses)}")
    for h in state.hypotheses:
        nov = "新颖" if h.is_novel else ("已知" if h.is_novel is False else "待验证")
        print(f"   - {h.id} {h.target_property} 预测={h.predicted_value} [{nov}] {h.status}")
    print(f"报告路径 : {state.report}")
    print("=" * 64)


if __name__ == "__main__":
    main()
