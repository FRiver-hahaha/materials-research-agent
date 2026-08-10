"""文献检索 Agent。双数据来源策略（参考 deepresearch 数据思路）：
- SciverseAdapter：语义检索（web search），REST 直连 https://api.sciverse.space。
- SciBaseRAGAdapter：本地向量库检索（local search），基于专属领域语料。
两者结果汇入检索集合，保证数据来源可靠且可审计。无 Sciverse key 时自动退回本地 RAG。

Sciverse REST 契约（取自官方 SDK 0.13.1 源码，已核对）：
  鉴权：Authorization: Bearer <SCIVERSE_API_TOKEN>
  POST /meta-search     结构化元数据 -> hits[title,doc_id,authors,year,venue,abstract]
  POST /agentic-search  语义片段     -> hits[doc_id,chunk_id,text,score,source{title,year},offset]
  GET  /content         按字节切片   -> {text, next_offset, more}
"""
import os
import json
import time
import http.client
from urllib.parse import urlencode
from src.agents.state import AgentState, Paper


class SciverseAdapter:
    """Sciverse 语义检索客户端（REST 直连，零依赖，无需安装 SDK）。"""
    DEFAULT_BASE = "https://api.sciverse.space"

    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key or os.getenv("SCIVERSE_API_TOKEN", "")
        self.base_url = (base_url or os.getenv("SCIVERSE_BASE_URL", "")).rstrip("/") or self.DEFAULT_BASE
        self.host = self.base_url.replace("https://", "").replace("http://", "")

    def _request(self, method, path, body=None, params=None, timeout=30):
        last = None
        for wait in (0, 1, 2, 4):
            if wait:
                time.sleep(wait)
            try:
                conn = http.client.HTTPSConnection(self.host, timeout=timeout)
                try:
                    url = path + ("?" + urlencode(params) if params else "")
                    data = json.dumps(body).encode("utf-8") if body is not None else None
                    headers = {"Authorization": f"Bearer {self.api_key}",
                               "Content-Type": "application/json",
                               "Accept": "application/json"}
                    conn.request(method, url, body=data, headers=headers)
                    resp = conn.getresponse()
                    raw = resp.read().decode("utf-8", "ignore")
                    if resp.status in (429, 502, 503):
                        last = f"{resp.status} {raw[:120]}"
                        continue
                    if resp.status >= 400:
                        raise RuntimeError(f"Sciverse HTTP {resp.status}: {raw[:200]}")
                    return json.loads(raw) if raw.strip() else {}
                finally:
                    conn.close()
            except RuntimeError:
                raise
            except Exception as e:
                last = str(e)
                if wait == 4:
                    raise
        raise RuntimeError(f"Sciverse 重试仍失败: {last}")

    def _post(self, path, body):
        return self._request("POST", path, body=body)

    def _get(self, path, params):
        return self._request("GET", path, params=params)

    @staticmethod
    def _hits(resp):
        if not isinstance(resp, dict):
            return []
        return resp.get("hits") or resp.get("results") or []

    @staticmethod
    def _norm_authors(raw):
        out = []
        if isinstance(raw, dict):
            raw = [raw]
        for a in (raw or []):
            if isinstance(a, str):
                out.extend(x.strip() for x in a.split("|") if x.strip())
            elif isinstance(a, dict) and a.get("name"):
                out.append(a["name"])
        return out

    def search(self, query: str, top_k: int = 10) -> list:
        if not self.api_key:
            return []
        # 1) 语义检索（核心入口）：直接返回 doc_id/title/author/year/venue/chunk
        try:
            sem = self._post("/agentic-search",
                             {"query": query, "retrieval": "hybrid", "top_k": top_k})
        except Exception as e:
            import traceback as _tb
            _tb.print_exc()
            print(f"[sciverse] agentic-search 失败: {e}")
            sem = {}
        # 2) 元数据检索：补充 abstract / 引用等结构化信息
        try:
            meta = self._post("/meta-search", {"query": query, "page_size": min(top_k, 20)})
        except Exception as e:
            print(f"[sciverse] meta-search 失败: {e}")
            meta = {}

        docs = {}
        for h in self._hits(sem):
            did = h.get("doc_id")
            if not did:
                continue
            docs[did] = {
                "title": h.get("title", ""),
                "authors": self._norm_authors(h.get("author")),
                "year": int(h.get("publication_published_year") or 0) or 0,
                "venue": h.get("publication_venue_name_unified", "") or "",
                "abstract": (h.get("abstract") or ""),
                "chunks": [h["chunk"]] if h.get("chunk") else [],
            }
        # 3) 用 meta 结果按标题匹配，补全 abstract/venue/year
        for it in self._hits(meta):
            title = (it.get("title") or "").lower()
            abstract = it.get("abstract") or ""
            venue = it.get("publication_venue_name_unified", "") or ""
            year = int(it.get("publication_published_year") or 0) or 0
            matched = None
            for d in docs.values():
                t = d["title"].lower()
                if title and (title in t or t in title):
                    matched = d
                    break
            if matched:
                if not matched["abstract"] and abstract:
                    matched["abstract"] = abstract
                if not matched["venue"] and venue:
                    matched["venue"] = venue
                if not matched["year"] and year:
                    matched["year"] = year
            else:
                uid = it.get("unique_id") or title
                if not uid:
                    continue
                docs[uid] = {
                    "title": it.get("title", ""),
                    "authors": self._norm_authors(it.get("author")),
                    "year": year, "venue": venue,
                    "abstract": abstract, "chunks": [],
                }

        papers = []
        for did, d in docs.items():
            sections = {"abstract": d["abstract"]}
            # 4) 语义检索命中片段优先作为抽取源（精准、省额度）；
            #    仅当无 chunk 时再拉 /content 补全全文。
            for i, ch in enumerate(d["chunks"][:8], 1):
                sections[f"chunk_{i}"] = ch
            if not d["chunks"]:
                try:
                    c = self._get("/content", {"doc_id": did, "offset": 0, "limit": 8192})
                    full = c.get("text") or ""
                    if full:
                        sections["full_text"] = full
                except Exception:
                    pass
            papers.append(Paper(
                paper_id=did, title=d["title"], authors=d["authors"], year=d["year"],
                abstract=d["abstract"], parsed={"sections": sections},
                url=f"https://sciverse.opendatalab.com/doc/{did}"))
        return papers[:top_k]


class SciBaseRAGAdapter:
    """本地 RAG 检索：在已向量化的专属语料上做余弦相似度检索。"""
    def __init__(self, vector_store, embedding):
        self.vs = vector_store
        self.emb = embedding

    def index(self, papers: dict):
        for pid, p in papers.items():
            text = p.abstract + " " + " ".join(str(v) for v in p.parsed.get("sections", {}).values())
            self.vs.add(pid, self.emb.encode(text), {"title": p.title, "year": p.year})

    def search(self, query: str, top_k: int = 8) -> list:
        return self.vs.search(self.emb.encode(query), top_k=top_k)


def retrieve(state: AgentState, sciverse: SciverseAdapter, rag: SciBaseRAGAdapter) -> AgentState:
    # web：真实 Sciverse 文献（动态拉取，回流进 state.papers）
    web_papers = sciverse.search(state.task, top_k=8)
    for p in web_papers:
        state.papers[p.paper_id] = p
    if web_papers:
        state.log(f"[retrieval] Sciverse 命中 {len(web_papers)} 篇真实文献")
    # local：本地 RAG（基于预置/专属语料）
    local = rag.search(state.task, top_k=8)
    state.log(f"[retrieval] Sci-Base RAG 命中 {len(local)} 条")

    ids = []
    for p in web_papers:
        if p.paper_id not in ids:
            ids.append(p.paper_id)
    for hit in local:
        pid = hit["id"]
        if pid not in ids:
            ids.append(pid)
    state.retrieved_ids = ids
    return state
