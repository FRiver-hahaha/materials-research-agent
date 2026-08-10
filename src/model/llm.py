"""模型层：LLM 适配器。可插拔：
- MockLLM：零依赖、确定性输出，用于无 Key 时端到端跑通 Demo（演示工作流）。
- OpenAICompatible：接入任意 OpenAI 兼容端点（OpenAI / DeepSeek / 本地 vLLM 等）。
真实参赛时把 config.yaml 的 provider 改为 openai 并填 key 即可，业务层无需改动。"""
import json
import os
import urllib.request
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str, kind: str = "text") -> str:
        """kind 用于让 mock / 真实模型产出结构化可控结果：
        text | rationale | report_intro | prune | hypotheses"""

    @abstractmethod
    def structured(self, system: str, prompt: str, kind: str) -> dict:
        """返回可解析的 dict（hypotheses / prune 等）。"""


class MockLLM(LLMProvider):
    """确定性 mock：依据 kind 与 prompt 中的关键实体生成可复现文本。
    注意：数值检索/搜索/抽取均由规则与算法完成，LLM 仅负责自然语言包装与假设种子。"""

    def is_real(self) -> bool:
        return False

    def complete(self, system: str, prompt: str, kind: str = "text") -> str:
        if kind == "report_intro":
            return ("本报告由材料科学文献调研智能体自动生成。系统围绕给定研究方向，"
                    "自主完成文献检索、结构化抽取、跨文献融合、Research Gap 识别与构效关系发现，"
                    "所有结论均附文献证据链。")
        if kind == "rationale":
            # 从 prompt 抽取关键短语做自然包装
            head = prompt.split("\n")[0][:120]
            return (f"基于检索到的文献证据，该候选在结构-性能权衡上具备合理性：{head}。"
                    "LLM 在搜索循环中作为评估器，依据容忍因子与相稳定性经验法则对候选剪枝。")
        return f"[mock-summary] {prompt[:160]}"

    def structured(self, system: str, prompt: str, kind: str) -> dict:
        if kind == "hypotheses":
            # 从 prompt 抽取目标性质，生成种子假设（真实系统由 LLM 自由生成）
            prop = "bandgap"
            for tok in ["bandgap", "stability", "Eg"]:
                if tok in prompt:
                    prop = tok
                    break
            return {
                "hypotheses": [
                    {
                        "statement": f"通过调节 A 位阳离子半径减小 Goldschmidt 容忍因子偏离，可在保持 {prop} 接近 1.3 eV 的同时提升相稳定性。",
                        "structure_feature": "A-site cation radius / tolerance factor",
                        "target_property": prop,
                        "rationale": "容忍因子越接近 1，三维钙钛矿骨架越稳定；但需兼顾光学带隙。",
                    },
                    {
                        "statement": f"提高卤素 Br 比例可展宽带隙并抑制离子迁移，从而改善 {prop} 与湿热稳定性。",
                        "structure_feature": "halide composition (I/Br ratio)",
                        "target_property": prop,
                        "rationale": "Br 替代 I 增大带隙、增强键强，但过高 Br 会降低电压。",
                    },
                ]
            }
        if kind == "prune":
            # 默认保留，除非 prompt 显式包含 unstable 关键词
            keep = "unstable" not in prompt.lower()
            return {"keep": keep, "reason": "容忍因子在稳定区间内" if keep else "容忍因子偏离过大，预测相不稳定"}
        return {}


class OpenAICompatible(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def is_real(self) -> bool:
        # 仅有非空 key 才视为真实 LLM；空 key 时管道自动降级到规则路径
        return bool(self.api_key)

    def _chat(self, system: str, prompt: str, want_json: bool) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        if want_json:
            payload["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    def complete(self, system: str, prompt: str, kind: str = "text") -> str:
        return self._chat(system, prompt, want_json=False)

    def structured(self, system: str, prompt: str, kind: str) -> dict:
        raw = self._chat(system, prompt, want_json=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # 容错：尝试提取第一个 JSON 块
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start:end + 1])
            return {}
