"""存储层抽象接口（ABC）。所有存储实现都必须满足这些契约，
便于在内存实现 / FAISS / Chroma / PostgreSQL 之间无缝替换。"""
from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    def add(self, id: str, vector, payload: dict) -> None: ...

    @abstractmethod
    def search(self, vector, top_k: int = 5) -> list: ...


class EvidenceStore(ABC):
    @abstractmethod
    def put(self, evidence) -> str: ...

    @abstractmethod
    def get(self, evidence_id: str): ...

    @abstractmethod
    def by_paper(self, paper_id: str) -> list: ...


class KnowledgeGraph(ABC):
    @abstractmethod
    def add_node(self, node_type: str, name: str, **attrs) -> str: ...

    @abstractmethod
    def add_edge(self, src: str, dst: str, rel: str, **attrs) -> None: ...

    @abstractmethod
    def neighbors(self, node_id: str, rel: str = None) -> list: ...


class EntityDB(ABC):
    @abstractmethod
    def add(self, entity) -> None: ...

    @abstractmethod
    def query(self, kind: str = None, normalized: str = None) -> list: ...
