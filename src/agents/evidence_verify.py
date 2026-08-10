"""证据核验 Agent：确保每个产出结论（Gap / 假设）都能追溯到具体证据对象。
评审关键项：文献溯源。此处做完整性校验并生成核验摘要。"""
from src.agents.state import AgentState


def verify(state: AgentState) -> AgentState:
    issues = []
    for g in state.gaps:
        missing = [eid for eid in g.related_evidence if eid not in state.evidence]
        if missing:
            issues.append(f"Gap {g.gap_id} 缺失证据: {missing}")
    for h in state.hypotheses:
        missing = [eid for eid in h.evidence_ids if eid not in state.evidence]
        if missing:
            issues.append(f"假设 {h.id} 缺失证据: {missing}")
    state.audit_log.append(f"[verify] 证据核验: 证据总数={len(state.evidence)}, 问题={len(issues)}")
    if issues:
        for i in issues:
            state.log(f"[verify-warn] {i}")
    else:
        state.log("[verify] 全部结论均可溯源 ✅")
    return state
