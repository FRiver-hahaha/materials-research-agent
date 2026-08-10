"""路线A-1 假设生成：LLM 基于真实抽取证据提出候选构效关系假设（种子）。
增量改进：把实际抽取到的组成/带隙/条件作为上下文喂给 LLM，使假设数据接地，而非空泛模板。"""
from src.agents.state import AgentState, Hypothesis

_SYSTEM = """你是钙钛矿材料构效关系研究专家。基于给定的真实文献证据摘要，提出可检验的构效关系假设。
只输出 JSON：{"hypotheses":[{"statement":"假设陈述(中文,≤80字)","structure_feature":"结构特征","target_property":"bandgap|stability","rationale":"依据(中文,≤60字)"}]}
要求：假设必须源于给定证据，聚焦 A 位阳离子/卤素比例/容忍因子对带隙与相稳定性的影响，避免空泛。"""


def generate_hypotheses(state: AgentState, llm) -> AgentState:
    # 构建真实证据上下文，喂给 LLM（接地气）
    comps = {}
    for e in state.entities:
        if e.kind == "composition":
            comps.setdefault(e.normalized, set()).add(e.paper_id)
    bgs = [(e.composition, e.value) for e in state.entities
           if e.kind == "property" and e.normalized == "bandgap" and e.value is not None]
    ctx = (f"任务: {state.task}\n"
           f"材料组成(文献数): { {c: len(ps) for c, ps in comps.items()} }\n"
           f"带隙证据(组成, eV): {bgs[:12]}\n"
           f"总证据条数: {len(state.evidence)}")
    seed_evs = [eid for eid, ev in state.evidence.items() if ev.value is not None][:5]
    raw = llm.structured(_SYSTEM, ctx, kind="hypotheses")
    hyps = []
    for i, h in enumerate(raw.get("hypotheses", []), 1):
        hyps.append(Hypothesis(
            id=f"H{i:02d}",
            statement=h.get("statement", ""),
            structure_feature=h.get("structure_feature", ""),
            target_property=h.get("target_property", "bandgap"),
            predicted_value=None,
            rationale=h.get("rationale", ""),
            evidence_ids=seed_evs,
            confidence=0.6 if llm.is_real() else 0.5,
        ))
    state.hypotheses = hyps
    state.log(f"[routeA] 生成种子假设 {len(hyps)} 条（LLM 基于真实证据）")
    return state
