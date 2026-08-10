"""实体库：存储从文献抽取并归一化后的结构化实体（成分/结构/性质/方法/条件）。"""
from .base import EntityDB
from src.agents.state import Entity


class InMemoryEntityDB(EntityDB):
    def __init__(self):
        self._entities = []

    def add(self, entity: Entity) -> None:
        self._entities.append(entity)

    def query(self, kind: str = None, normalized: str = None) -> list:
        res = self._entities
        if kind is not None:
            res = [e for e in res if e.kind == kind]
        if normalized is not None:
            res = [e for e in res if e.normalized == normalized]
        return res

    def all(self) -> list:
        return self._entities
