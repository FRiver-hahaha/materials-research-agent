"""跨文献融合 Agent：将归一化实体与证据构建为知识图谱。
节点：材料(composition) / 性质(property) / 方法(method)
边：composition -[has_property]-> property(带数值/单位/证据)
     composition -[studied_by]-> method
关联规则：性质/方法按「最近化学式消歧」归属到具体材料后连接，再跨文献汇聚。"""
from src.agents.state import AgentState


def fuse(state: AgentState, kg, entity_db) -> AgentState:
    comp_nodes, prop_nodes, meth_nodes = {}, {}, {}
    for e in entity_db.all():
        if e.kind == "composition":
            nid = kg.add_node("composition", e.normalized)
            comp_nodes[e.normalized] = nid
        elif e.kind == "property":
            nid = kg.add_node("property", f"{e.normalized}:{e.value}")
            prop_nodes.setdefault(e.normalized, []).append((nid, e))
        elif e.kind == "method":
            nid = kg.add_node("method", e.normalized)
            meth_nodes[e.normalized] = nid

    for e in entity_db.all():
        if e.kind in ("property", "method"):
            comp = e.composition
            if not comp or comp not in comp_nodes:
                continue
            if e.kind == "property":
                for pnid, pe in prop_nodes.get(e.normalized, []):
                    if pe.evidence_id == e.evidence_id:
                        kg.add_edge(comp_nodes[comp], pnid, "has_property",
                                    value=pe.value, unit=pe.unit, evidence=e.evidence_id)
            else:
                kg.add_edge(comp_nodes[comp], meth_nodes[e.normalized], "studied_by",
                            evidence=e.evidence_id)

    state.knowledge_graph = kg
    state.log(f"[fusion] 知识图谱：{len(kg.nodes())} 节点 / {len(kg.edges())} 边")
    return state
