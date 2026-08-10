# 材料科学文献调研智能体（AI for Science 算法赛 · 初赛）

> 赛道：材料科学文献驱动的科学发现智能体
> 选择路线：**A — 构效关系发现（Structure–Property Relationship Discovery）**
> 运行：`python -m src.main`（零第三方依赖，开箱即跑；Demo 用 mock 提供器端到端演示）

---

## 1. 系统简介

本系统是一个**以证据对象为中心、工作流编排为主、Agent 自主决策为辅**的材料科学文献调研智能体。
围绕给定研究方向，自主完成：

1. 文献检索与筛选（Sciverse 语义检索 web + Sci-Base 本地 RAG local）
2. PDF 解析（MinerU）与结构化知识抽取（成分 / 结构 / 性质 / 方法 / 条件）
3. 实体归一化与跨文献知识图谱融合
4. Research Gap 识别（未探索 / 矛盾 / 缺失连接）
5. **路线 A**：LLM 假设生成 → 搜索优化（贝叶斯优化 / 遗传算法 / MCTS / 符号回归）→ 材料数据库交叉验证
6. 证据核验与调研报告生成（Gap 清单 + 文献交叉引用 + 完整证据链）

---

## 2. 分层架构

```
┌──────────────────────────────────────────────────────────┐
│  业务层 (src/agents)  — 状态图编排 + 各 Agent 节点          │
│  task_plan → retrieve → filter → parse → extract →         │
│  normalize → fuse → gap → routeA(hyp/explore/validate) →   │
│  verify → report                                           │
├──────────────────────────────────────────────────────────┤
│  模型层 (src/model)  — 可插拔适配器                         │
│  LLMProvider(Mock/OpenAI) · Embedding(Mock/OpenAI) ·       │
│  search_opt: BayesianOptimizer / GeneticSearch / MCTS /    │
│  SymbolicRegression                                        │
├──────────────────────────────────────────────────────────┤
│  存储层 (src/storage)  — 可替换实现                         │
│  VectorStore(RAG) · EvidenceStore(证据链) ·               │
│  KnowledgeGraph(融合) · EntityDB(实体)                     │
└──────────────────────────────────────────────────────────┘
```

**关键设计增量（相对直接使用开源框架）：**
- **自研轻量状态图编排器**（`src/agents/graph.py`，LangGraph 式但零依赖）：节点 + 条件边 + 循环，全程记录 `audit_log`，天然形成**可审计证据链**。
- **证据对象（Evidence）为核心数据单元**：每个事实携带 `paper_id / page / snippet / value / unit / condition`，所有结论 100% 可溯源。
- **双数据来源策略**：Sciverse（web search，MCP/Skill 接入）+ Sci-Base（local RAG），参考 deepresearch 的数据可靠性思路。
- **LLM 真正参与搜索过程**（路线 A）：LLM 提供种子候选并**逐候选剪枝评估**，而非"生成一段搜索代码就不管"。
- **邻近化学式消歧**：性质/方法按"同段落最近化学式"归属到具体材料，避免比较句（如 "lower than MAPbI3"）造成的误归因。

---

## 3. 目录结构

```
materials-research-agent/
├── config.yaml                # 提供器/API 配置（mock → openai 切换）
├── src/
│   ├── main.py               # 入口：加载配置、装配状态图、运行、输出摘要
│   ├── storage/              # 存储层
│   ├── model/                # 模型层（LLM/Embedding 适配器 + 搜索优化算法）
│   │   └── search_opt/       # 贝叶斯优化 / 遗传算法 / MCTS / 符号回归
│   └── agents/               # 业务层
│       ├── graph.py          # 轻量状态图编排器
│       ├── retrieval/extraction/fusion/gap_identification/...
│       └── route_a/          # 路线A：假设生成 / LLM引导搜索 / 数据库验证
├── data/
│   ├── sample_literature/    # Sci-Base 预处理后的专属语料（演示子集）
│   └── output/               # 生成的 report.md + evidence_chain.md
├── tests/test_demo.py        # 冒烟测试
└── PROPOSAL.md               # 路线A 项目方案
```

---

## 4. 运行

```bash
cd materials-research-agent
python -m src.main                         # 默认贝叶斯优化
python -m src.main --algorithm genetic      # 遗传算法
python -m src.main --task "your research direction"
```

输出：`data/output/report.md`（调研报告）、`data/output/evidence_chain.md`（证据链）。

---

## 5. 接入真实数据/工具（初赛→复赛过渡）

### 5.1 Sciverse 真实检索（已端到端验证）

`SciverseAdapter` 采用 **REST 直连 `https://api.sciverse.space`**（零依赖，标准库 `http.client`），
鉴权 `Authorization: Bearer <SCIVERSE_API_TOKEN>`。无需安装官方 SDK（mingw 环境装不上 pydantic-core）。
端点（已对照官方 SDK 0.13.1 源码核对）：`POST /meta-search`、`POST /agentic-search`、`GET /content`。

```bash
# 1) 申请 token：https://sciverse.opendatalab.com/tokens
# 2) 仅用真实检索（跳过本地 mock 语料，报告 100% 真实引用）：
export SCIVERSE_API_TOKEN=sv-xxxx
python -m src.main --task "perovskite solar cell bandgap and phase stability" --corpus ""
#   --corpus "" 表示不加载本地语料；不传则默认混合 mock 语料
```

实测：8 篇真实文献 → 抽取 45 实体 → 17 节点/12 边知识图谱 → 25 个 Research Gap → 路线 A 5 条新颖假设（带数据库交叉验证）。

### 5.2 真实 LLM / 嵌入（推荐，提升抽取与 Gap 质量）

规则抽取器对真实 LaTeX 文献有噪声，接真实 LLM 可显著提升知识抽取与 Gap 质量：

```yaml
llm:
  provider: openai          # 改为 openai
  openai: { base_url: https://api.openai.com/v1, api_key: sk-xxx, model: gpt-4o-mini }
embedding:
  provider: openai          # 同上填 key
```

### 5.3 其他组件

| 组件 | 当前 | 真实接入 |
|------|------|----------|
| PDF 解析 | 预解析 JSON / Sciverse `/content` | MinerU API（`MinerUClient` 已实现） |
| 材料数据库 | 模拟 MP 表 | `route_a/validator.py` 替换为 materialsproject.org / OQMD / NOMAD |

业务层代码**无需改动**，仅替换配置与适配器实现即可升级到真实数据。

---

## 6. 对应评审标准

**基础任务（约 50%）**
- Research Gap 识别：准确（三类）、具体（绑定证据）、新颖（演示子集即触发矛盾与缺失连接）。
- 文献检索质量：双来源、相关度阈值 + 兜底，覆盖关键文献。
- 知识抽取质量：规则化抽取成分/结构/工艺/性质/实验条件。
- 文献溯源：Evidence 对象贯穿全链路，核验环节保证 0 缺失。
- 报告质量：结构化、可读、证据链完整。
- Agent 完整性：真正执行检索→抽取→推理→报告，而非仅调用大模型写作。

**进阶任务 A（约 50%）**
- 新关联：搜索优化发现带隙≈1.3 eV 且高相稳定性的新组成，给出物理解释。
- 搜索方法合理：BO/GA/MCTS 可切换，LLM 参与种子与剪枝。
- 交叉验证：与材料数据库比对，标注"新颖 / 已知"。
