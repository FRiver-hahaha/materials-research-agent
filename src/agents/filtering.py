"""文献筛选 Agent：基于检索相关度与关键词匹配，保留真正相关的文献。
兼容中英文：拉丁词做子串匹配，CJK 字符做集合覆盖匹配。
兜底：若全部低于阈值，保留检索返回的 top_n，避免流水线断流。"""
import re
from src.agents.state import AgentState


def _relevance(paper, task: str) -> float:
    text = (paper.title + " " + paper.abstract).lower()
    cjk = set("".join(re.findall(r"[\u4e00-\u9fff]", task)))
    latin = [t for t in re.split(r"\W+", task.lower()) if len(t) > 2]
    total, hits = 0, 0
    for ch in cjk:
        total += 1
        if ch in text:
            hits += 1
    for w in latin:
        total += 1
        if w in text:
            hits += 1
    return hits / max(1, total)


def filter_papers(state: AgentState, top_n: int = 6, min_rel: float = 0.1) -> AgentState:
    scored = []
    for pid in state.retrieved_ids:
        p = state.papers.get(pid)
        if not p:
            continue
        rel = _relevance(p, state.task)
        if rel >= min_rel:
            scored.append((rel, pid))
    scored.sort(reverse=True)
    kept = [pid for _, pid in scored[:top_n]]
    # 兜底：相关度全 0 时退回检索结果，保证后续节点有输入
    if not kept and state.retrieved_ids:
        kept = state.retrieved_ids[:top_n]
        state.log("[filter] 相关度普遍偏低，已退回检索 top_n 兜底")
    state.filtered_ids = kept
    state.log(f"[filter] 保留 {len(state.filtered_ids)} 篇高相关文献: {state.filtered_ids}")
    return state
