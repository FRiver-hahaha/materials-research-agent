"""模型层：Embedding 适配器。用于 Sci-Base 本地 RAG 的向量化。
- MockEmbedding：确定性哈希向量，零依赖，保证 Demo 可检索（同义文本相似度高）。
- 生产可替换为 OpenAI / BGE / 本地 sentence-transformers。"""
import hashlib
import math
import re
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def encode(self, text: str) -> list:
        ...


class MockEmbedding(EmbeddingProvider):
    """基于词频哈希的确定性向量：对相同/相近词袋给出高余弦相似度。"""
    DIM = 256

    def encode(self, text: str) -> list:
        tokens = re.findall(r"[a-z0-9\u4e00-\u9fff]+", text.lower())
        vec = [0.0] * self.DIM
        for t in tokens:
            h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
            idx = h % self.DIM
            vec[idx] += 1.0
        # L2 归一化
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


class OpenAIEmbedding(EmbeddingProvider):
    def __init__(self, base_url: str, api_key: str, model: str = "text-embedding-3-small"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def encode(self, text: str) -> list:
        import urllib.request, json
        payload = {"model": self.model, "input": text}
        req = urllib.request.Request(
            f"{self.base_url}/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["data"][0]["embedding"]
