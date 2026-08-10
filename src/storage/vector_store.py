"""轻量向量库：纯 Python 实现余弦相似度检索（Sci-Base 本地 RAG 的 Local Search）。
零依赖；生产环境可替换为 FAISS / Chroma / pgvector。"""
import math
from .base import VectorStore


def cosine(a, b) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self._items = []  # (id, vector, payload)

    def add(self, id: str, vector, payload: dict) -> None:
        self._items.append((id, list(vector), dict(payload)))

    def search(self, vector, top_k: int = 5) -> list:
        scored = [(cosine(vector, v), i, p) for i, v, p in self._items]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"id": i, "score": round(s, 4), "payload": p} for s, i, p in scored[:top_k]]
