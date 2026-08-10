"""PDF 解析 Agent：封装 MinerU（https://mineru.net）将 PDF 转为结构化内容。
生产环境调用 MinerU API/CLI；Demo 中语料已是解析后的结构化 JSON，此处做规范化与缺失兜底。"""
import json
import urllib.request
from src.agents.state import AgentState


class MinerUClient:
    """MinerU 解析客户端（真实接入占位）。"""
    def __init__(self, token: str = "", api_url: str = "https://api.mineru.net/v1/pdf"):
        self.token = token
        self.api_url = api_url

    def parse(self, pdf_path: str) -> dict:
        if not self.token:
            raise RuntimeError("未配置 MinerU token；Demo 使用预解析语料")
        req = urllib.request.Request(pdf_path, headers={"Authorization": f"Bearer {self.token}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))


def parse_papers(state: AgentState) -> AgentState:
    for pid in state.filtered_ids:
        p = state.papers.get(pid)
        if not p:
            continue
        secs = p.parsed.get("sections", {})
        if not secs:
            # 兜底：用 abstract 充当单一 section
            p.parsed["sections"] = {"abstract": p.abstract}
        state.log(f"[parse] {pid} 解析完成，含 {len(p.parsed.get('sections', {}))} 个章节")
    return state
