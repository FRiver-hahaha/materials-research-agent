"""路线A-3 数据库交叉验证：将搜索得到的构效关系与公开材料数据库比对。
此处用内置的「模拟 Materials Project 钙钛矿带隙表」演示交叉验证流程；
生产环境替换为 materialsproject.org / OQMD / NOMAD 的真实 API。"""
from src.agents.state import AgentState

# 模拟已知钙钛矿带隙（eV），演示交叉验证
KNOWN_BANDGAPS = {
    "MAPbI3": 1.55, "MAPbBr3": 2.30, "FAPbI3": 1.48, "FAPbBr3": 2.20,
    "CsPbI3": 1.73, "CsPbBr3": 2.36, "FA0.83Cs0.17PbI3": 1.50,
}


def validate(state: AgentState) -> AgentState:
    for h in state.hypotheses:
        pred = h.predicted_value
        if pred is None:
            continue
        is_novel = True
        for name, bg in KNOWN_BANDGAPS.items():
            if abs(pred - bg) < 0.05:
                is_novel = False
                h.statement += f" 〔交叉验证〕该带隙与已知体系 {name}({bg}eV) 接近，判定为已知构效关系。"
                break
        h.is_novel = is_novel
        if h.status.startswith("validated"):
            h.status = "validated+db_crosschecked"
    novel = sum(1 for h in state.hypotheses if h.is_novel is True)
    state.log(f"[routeA-validate] 与 Materials Project(模拟)交叉验证完成，新颖假设 {novel} 条")
    return state
