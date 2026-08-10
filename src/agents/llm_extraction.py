"""LLM 增强抽取 Agent（自研增量设计）。
接入真实 LLM 时，用结构化提示从文献段落抽取 组成/性质/方法/条件，并自动校正化学式
（如 FAPbl3 -> FAPbI3、Cs0.05FA0.95PbI3）。正则抽取作为逐段降级回退，保证无 Key 仍可端到端运行。
设计动机：纯正则抽取对 LaTeX/下标/合金比例鲁棒性差，易产生 FAPbl3 等噪声化学式；
LLM 抽取把"化学式归一化 + 噪声过滤 + 属性归属"交给模型，从源头消除噪声。"""
from src.agents.state import AgentState, Entity, Evidence
from src.agents.extraction import regex_extract_section

_SYSTEM = """你是材料科学文献结构化抽取专家。只输出 JSON，不要任何解释。
对给定的文献段落，抽取结构化实体，严格遵循格式：
{"entities":[{"type":"composition|property|method|condition","name":"...","value":数值或null,"unit":"eV或null","composition":"关联的化学式或空串","text":"原文片段(≤120字符)"}]}
约束：
- composition 必须是正确材料化学式（含金属阳离子与阴离子 I/Br/Cl/O/S 等）。校正常见笔误：FAPbl3->FAPbI3、MAPbl3->MAPbI3。剔除 PCE/WBG/PSCs/MPP 等缩写噪声与纯章节词（Figure/Table）。
- property 聚焦 bandgap(带隙，须给数值与单位 eV)、phase_stability(相稳定性)。
- method 如 DFT、HSE06、PBE、MD、VASP 等；condition 如退火温度、湿度等实验条件。
- property/method/condition 条目若可归属到具体材料，请在 composition 字段给出该化学式，否则填空串。
- 仅抽取段落中真实存在的信息，绝不臆造。"""


def _snip(txt):
    return (txt or "").replace("\n", " ")[:120]


def llm_extract(state: AgentState, ev_store, entity_db, llm) -> AgentState:
    ev_counter = [0]

    def add(pid, title, page, snippet, value, unit, kind, name, norm, comp):
        ev_counter[0] += 1
        eid = f"EV{ev_counter[0]:03d}"
        ev = Evidence(eid, pid, title, page, snippet, value, unit, None)
        ev_store.put(ev)
        state.evidence[eid] = ev
        entity_db.add(Entity(kind, name, norm, value, unit, eid, paper_id=pid, composition=comp))

    for pid in state.filtered_ids:
        p = state.papers.get(pid)
        if not p:
            continue
        page = 1
        for sec_name, sec_text in p.parsed.get("sections", {}).items():
            if not isinstance(sec_text, str) or not sec_text.strip():
                continue
            try:
                raw = llm.structured(_SYSTEM, sec_text[:3500], kind="extract")
            except Exception:
                raw = None
            items = raw.get("entities") if isinstance(raw, dict) else None
            if not items:
                # 降级：该段用正则抽取，保证不丢数据
                regex_extract_section(state, ev_store, entity_db, pid, p, sec_name, sec_text, page, ev_counter)
                continue
            for it in items:
                t = it.get("type")
                name = (it.get("name") or "").strip()
                if not name or t not in ("composition", "property", "method", "condition"):
                    continue
                val = it.get("value") if isinstance(it.get("value"), (int, float)) else None
                unit = it.get("unit") or None
                comp = it.get("composition") or None
                comp = comp if (isinstance(comp, str) and comp.strip()) else None
                txt = _snip(it.get("text"))
                if t == "composition":
                    add(pid, p.title, page, txt, None, None, "composition", name, name, None)
                else:
                    add(pid, p.title, page, txt, val, unit, t, name, name, comp)
    state.entities = entity_db.all()
    state.log(f"[llm-extract] 抽取实体 {len(state.entities)} 条，证据 {len(state.evidence)} 条")
    return state
