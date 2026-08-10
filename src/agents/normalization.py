"""实体归一化 Agent：将抽取出的实体规范为统一表示，便于跨文献融合与去重。
- 化学式：统一大写、去空格、规范小数下标（演示级规范化）。
- 性质名：统一为英文小写键（bandgap / stability / efficiency）。"""
import re
from src.agents.state import AgentState


_SUBSCRIPT = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def normalize_formula(f: str) -> str:
    f = f.translate(_SUBSCRIPT).replace(" ", "").replace("_", "")
    # 碘(I) 误识别为小写 l 的安全网（与抽取端保持一致，保护 Cl/Al/Tl/Fl）
    f = re.sub(r"(?<!C|F|A|T)l(\d)", r"I\1", f)
    return f


def normalize_property(name: str) -> str:
    name = name.lower().strip()
    mapping = {
        "bandgap": "bandgap", "e_g": "bandgap", "eg": "bandgap",
        "stability": "stability", "efficiency": "efficiency",
    }
    return mapping.get(name, name)


def normalize(state: AgentState, entity_db) -> AgentState:
    for e in entity_db.all():
        if e.kind == "composition":
            e.normalized = normalize_formula(e.name)
        elif e.kind == "property":
            e.normalized = normalize_property(e.name)
    state.entities = entity_db.all()
    state.log("[normalize] 实体归一化完成")
    return state
