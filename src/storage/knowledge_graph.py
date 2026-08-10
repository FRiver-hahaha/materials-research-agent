"""知识图谱：跨文献融合的结构化状态。节点=材料/结构特征/性质/方法/条件，
边=构效关系(composition->property)、方法(method->property)等。
用于支撑 Research Gap 识别（矛盾检测、缺失连接检测）。"""
from .base import KnowledgeGraph


class InMemoryKnowledgeGraph(KnowledgeGraph):
    def __init__(self):
        self._nodes = {}   # id -> {type, name, attrs}
        self._edges = []   # (src, dst, rel, attrs)
        self._counter = 0

    def _nid(self, node_type, name):
        return f"{node_type}:{name}"

    def add_node(self, node_type: str, name: str, **attrs) -> str:
        nid = self._nid(node_type, name)
        if nid not in self._nodes:
            self._nodes[nid] = {"type": node_type, "name": name, "attrs": dict(attrs)}
        else:
            self._nodes[nid]["attrs"].update(attrs)
        return nid

    def add_edge(self, src: str, dst: str, rel: str, **attrs) -> None:
        self._edges.append((src, dst, rel, dict(attrs)))

    def neighbors(self, node_id: str, rel: str = None) -> list:
        out = []
        for s, d, r, a in self._edges:
            if s == node_id and (rel is None or r == rel):
                out.append({"node": d, "rel": r, "attrs": a})
        return out

    def edges(self):
        return self._edges

    def nodes(self):
        return self._nodes
