"""证据库：以「证据对象」为中心存储可审计的事实单元。
每个 Evidence 必须携带 paper_id + 页码/片段/数值/单位/条件，构成证据链的最小单元。"""
from .base import EvidenceStore
from src.agents.state import Evidence


class InMemoryEvidenceStore(EvidenceStore):
    def __init__(self):
        self._ev = {}
        self._by_paper = {}

    def put(self, evidence: Evidence) -> str:
        self._ev[evidence.evidence_id] = evidence
        self._by_paper.setdefault(evidence.paper_id, []).append(evidence.evidence_id)
        return evidence.evidence_id

    def get(self, evidence_id: str):
        return self._ev.get(evidence_id)

    def by_paper(self, paper_id: str) -> list:
        return [self._ev[i] for i in self._by_paper.get(paper_id, [])]
