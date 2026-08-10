"""任务规划 Agent：将研究方向拆解为可审计的工作流步骤。"""
from src.agents.state import AgentState


def plan_task(state: AgentState) -> AgentState:
    state.plan = [
        "1. 文献检索：Sciverse 语义检索(web) + Sci-Base 本地 RAG(local)",
        "2. 文献筛选：按相关度阈值保留高相关文献",
        "3. PDF 解析(MinerU) 与结构化知识抽取（成分/结构/性质/方法/条件）",
        "4. 实体归一化与跨文献融合（知识图谱）",
        "5. Research Gap 识别（未探索 / 矛盾结论 / 缺失连接）",
        "6. 路线A 构效关系发现：LLM 假设生成 + 搜索优化(BO/GA/MCTS) + 数据库交叉验证",
        "7. 证据核验与调研报告生成（Gap 清单 + 文献交叉引用 + 证据链）",
    ]
    state.log(f"[plan] 研究方向={state.task}")
    return state
