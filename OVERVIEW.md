# 概览：材料科学文献调研智能体（初赛 · 路线 A）

## 做了什么
在 `D:\gitclone\materials-research-agent` 下交付了一个**零第三方依赖、可端到端跑通**的材料科学文献调研智能体，
选择并实现了**路线 A：构效关系发现**。系统以「证据对象」为中心，工作流编排为主、Agent 自主决策为辅。

## 架构（三层分离）
- **存储层** `src/storage/`：向量库(RAG)、证据库、知识图谱、实体库（均为可替换的内存实现）。
- **模型层** `src/model/`：LLM / Embedding 可插拔适配器（Mock / OpenAI 兼容）+ 搜索优化算法（贝叶斯优化 / 遗传算法 / MCTS / 符号回归）。
- **业务层** `src/agents/`：自研轻量状态图编排器 + 各 Agent 节点（检索→筛选→解析→抽取→归一→融合→Gap→路线A→核验→报告）+ `route_a/` 三件套。

## 初赛交付物
| 文件 | 内容 |
|------|------|
| `data/output/report.md` | 调研报告（Gap 清单 + 文献交叉引用 + 证据链） |
| `data/output/evidence_chain.md` | 可审计证据链 |
| `README.md` | Agent 系统说明（架构 + 增量设计 + 真实接入指引） |
| `PROPOSAL.md` | 路线 A 项目方案 |
| `tests/test_demo.py` | 冒烟测试（已通过） |

## 关键增量设计（相对直接用开源框架）
1. 自研 LangGraph 式状态图，全程 `audit_log` → 天然可审计证据链。
2. Evidence 对象贯穿全链路，结论 100% 可溯源。
3. 双数据来源：Sciverse(web) + Sci-Base(local RAG)。
4. LLM **真正参与**搜索：提供种子 + 逐候选剪枝评估，非"生成代码就不管"。
5. 邻近化学式消歧，避免比较句造成的性质误归因。

## 运行
```bash
cd D:\gitclone\materials-research-agent
python -m src.main                 # 默认贝叶斯优化
python -m src.main --algorithm genetic
```
输出：检索 6 篇、抽取 39 实体、知识图谱 15 节点、识别 6 个 Gap（未探索/矛盾/缺失连接三类齐全）、
路线 A 产出 5 条新颖构效假设（预测带隙 ≈1.25–1.29 eV，贴近单结最佳 1.3 eV）并经材料数据库交叉验证。

## 复赛过渡
业务层无需改动，仅将 `config.yaml` 的 provider 改为 openai 并填 key，替换 Sciverse / MinerU / Materials Project 适配器即可升级到真实数据。
