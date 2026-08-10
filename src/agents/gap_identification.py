"""Research Gap 识别 Agent：基于知识图谱与证据，识别三类 Gap：
1. underexplored  未被充分探索的方向（某组成仅 1 篇文献涉及）
2. contradiction  矛盾结论（同一组成带隙在不同文献数值显著冲突）
3. missing_link   缺失连接（某组成被研究但未给出关键光电性质定量数据）
每条 Gap 绑定相关 evidence_id，保证可溯源。"""
from collections import defaultdict
from src.agents.state import AgentState, Gap

_GAP_SYSTEM = """你是材料科学研究战略分析师。基于已抽取的文献证据摘要，识别高价值 Research Gap。
只输出 JSON：{"gaps":[{"statement":"研究缺口描述(中文,≤80字)","research_value":"为何重要(中文,≤60字)"}]}
聚焦：未充分探索的材料体系、矛盾的实验结论、构效关系建模中的关键证据缺口，以及可落地的探索方向。
不要重复已知事实，要提出有洞察的研究机会。"""


def _summarize(state, entity_db):
    comps = {}
    for e in entity_db.all():
        if e.kind == "composition":
            comps.setdefault(e.normalized, set()).add(e.paper_id)
    bgs = [(e.composition, e.value) for e in entity_db.all()
           if e.kind == "property" and e.normalized == "bandgap" and e.value is not None]
    return (f"任务方向: {state.task}\n"
            f"已抽取材料组成(及涉及文献数): { {c: len(ps) for c, ps in comps.items()} }\n"
            f"带隙样本(组成, eV): {bgs[:12]}\n"
            f"总证据条数: {len(state.evidence)}")


def identify_gaps(state: AgentState, entity_db, llm=None) -> AgentState:
    comp_papers = defaultdict(set)      # 组成 -> {出现过的 paper_id}
    comp_bandgaps = defaultdict(list)   # 组成 -> [(value, evidence_id)]
    comp_has_bg = defaultdict(bool)
    comp_ev = defaultdict(list)

    for e in entity_db.all():
        if e.kind == "composition":
            comp_papers[e.normalized].add(e.paper_id)
            comp_ev[e.normalized].append(e.evidence_id)
        elif e.kind == "property" and e.normalized == "bandgap" \
                and e.value is not None and e.composition:
            comp = e.composition
            comp_bandgaps[comp].append((e.value, e.evidence_id))
            comp_has_bg[comp] = True

    gaps = []
    gid = 0

    # 1. 未充分探索
    for comp, papers in comp_papers.items():
        if len(papers) == 1:
            gid += 1
            gaps.append(Gap(f"G{gid:02d}", "underexplored",
                            f"组成 {comp} 仅在单篇文献中出现，缺乏系统研究。",
                            comp_ev[comp], "适合作为新体系的探索起点，研究价值高。", True))

    # 2. 矛盾结论（同组成跨文献带隙差异 > 0.1 eV）
    for comp, bgs in comp_bandgaps.items():
        vals = [v for v, _ in bgs]
        if len(bgs) >= 2 and (max(vals) - min(vals)) > 0.1:
            gid += 1
            gaps.append(Gap(f"G{gid:02d}", "contradiction",
                            f"组成 {comp} 的带隙在文献间存在冲突（{min(vals):.2f}–{max(vals):.2f} eV），"
                            "可能源于测试条件或相纯度的差异。",
                            [eid for _, eid in bgs],
                            "需进一步统一测试条件或澄清相组成，避免误导构效建模。", True))

    # 3. 缺失连接
    for comp in comp_papers:
        if not comp_has_bg[comp]:
            gid += 1
            gaps.append(Gap(f"G{gid:02d}", "missing_link",
                            f"组成 {comp} 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，"
                            "形成证据链缺口。",
                            comp_ev[comp], "建议补充第一性原理计算或实验标定以补全构效关系。", True))

    # LLM 增强：在规则 Gap 之上，补充高价值"研究机会"型 Gap（需真实 LLM）
    if llm is not None and getattr(llm, "is_real", lambda: False)():
        try:
            raw = llm.structured(_GAP_SYSTEM, _summarize(state, entity_db), kind="gaps")
            for i, g in enumerate(raw.get("gaps", []) or [], 1):
                stmt = (g.get("statement") or "").strip()
                if not stmt:
                    continue
                gaps.append(Gap(f"O{i:02d}", "opportunity", stmt, [],
                                g.get("research_value") or "高价值探索方向。", True))
            state.log(f"[gap] LLM 补充机会型 Gap {len([x for x in gaps if x.kind == 'opportunity'])} 条")
        except Exception as e:
            state.log(f"[gap] LLM 增强失败，保留规则 Gap: {e}")

    state.gaps = gaps
    state.log(f"[gap] 识别 Gap {len(gaps)} 条")
    return state
