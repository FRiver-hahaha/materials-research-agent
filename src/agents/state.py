"""共享结构化状态与核心数据模型（Schema）。
所有 Agent 节点围绕这些「证据对象」交换数据，而不是自由群聊。
评审要点：每个结论必须能追溯到具体论文/页码/原文片段/数值/单位/条件。"""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Evidence:
    """证据对象：可审计事实的最小单元（证据链节点）。"""
    evidence_id: str
    paper_id: str
    title: str
    page: Optional[int]
    snippet: str           # 原文片段
    value: Optional[float] = None
    unit: Optional[str] = None
    condition: Optional[str] = None   # 实验条件
    source_url: Optional[str] = None
    section: Optional[str] = None     # 出处章节


@dataclass
class Entity:
    """从文献抽取的实体。"""
    kind: str              # composition / structure / property / method / condition
    name: str
    normalized: str        # 归一化后的规范名
    value: Optional[float] = None
    unit: Optional[str] = None
    evidence_id: Optional[str] = None
    paper_id: Optional[str] = None
    section: Optional[str] = None
    composition: Optional[str] = None  # 该性质/方法所归属的材料（最近化学式消歧）


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: list
    year: int
    abstract: str
    parsed: dict           # MinerU 解析后的结构化内容
    url: Optional[str] = None


@dataclass
class Gap:
    """Research Gap：未被充分探索 / 矛盾结论 / 缺失连接。"""
    gap_id: str
    kind: str              # underexplored / contradiction / missing_link
    statement: str
    related_evidence: list
    research_value: str
    actionable: bool


@dataclass
class Hypothesis:
    """路线 A：构效关系假设。"""
    id: str
    statement: str
    structure_feature: str
    target_property: str
    predicted_value: Optional[float]
    rationale: str
    evidence_ids: list
    confidence: float
    is_novel: Optional[bool] = None   # 经数据库交叉验证后判定
    status: str = "candidate"         # candidate / validated / rejected


@dataclass
class AgentState:
    """贯穿整个 Agent 循环的共享状态（LangGraph 式 state）。"""
    task: str = ""
    plan: list = field(default_factory=list)
    papers: dict = field(default_factory=dict)          # paper_id -> Paper
    retrieved_ids: list = field(default_factory=list)
    filtered_ids: list = field(default_factory=list)
    entities: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)        # evidence_id -> Evidence
    knowledge_graph: Any = None
    gaps: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    report: str = ""
    audit_log: list = field(default_factory=list)        # 审计轨迹（证据链）

    def log(self, msg: str):
        self.audit_log.append(msg)
