"""业务层：轻量状态图编排器（自研，LangGraph 式）。
设计增量：相比直接调用 LLM 写作，本编排器以「带条件路由的有向图」驱动 Agent，
节点间通过共享 AgentState（证据对象）交换数据，并完整记录 audit_log（可审计证据链）。
支持：节点、条件边、人工/LLM 决策分支、循环（如 Route A 搜索循环）。"""
from src.agents.state import AgentState


class Node:
    def __init__(self, name: str, fn):
        self.name = name
        self.fn = fn  # fn(state: AgentState) -> AgentState

    def run(self, state: AgentState) -> AgentState:
        return self.fn(state)


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}   # src -> [(dst, cond_fn_or_None)]
        self.entry = None

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        return self

    def add_edge(self, src: str, dst: str, cond=None):
        self.edges.setdefault(src, []).append((dst, cond))
        return self

    def set_entry(self, name: str):
        self.entry = name
        return self

    def run(self, state: AgentState, max_steps: int = 200):
        cur = self.entry
        steps = 0
        while cur:
            if cur not in self.nodes:
                raise KeyError(f"未知节点: {cur}")
            node = self.nodes[cur]
            state = node.run(state)
            state.log(f"[node] {cur} executed")
            nxt = None
            for dst, cond in self.edges.get(cur, []):
                if cond is None or cond(state):
                    nxt = dst
                    break
            cur = nxt
            steps += 1
            if steps > max_steps:
                state.log("[warn] 达到最大步数，强制终止")
                break
        return state
