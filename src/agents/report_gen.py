"""报告生成 Agent：汇总 Gap 清单、文献交叉引用与完整证据链，输出结构化调研报告。
同时单独导出 evidence_chain.md 作为可审计证据链文件。"""
import os
from src.agents.state import AgentState


def _md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines)


def generate_report(state: AgentState, llm, out_dir: str = "data/output") -> AgentState:
    os.makedirs(out_dir, exist_ok=True)
    intro = llm.complete("", f"研究方向：{state.task}", kind="report_intro")

    # 文献交叉引用表
    paper_rows = []
    for pid in state.filtered_ids:
        p = state.papers.get(pid)
        if p:
            paper_rows.append([pid, p.year, p.title, ", ".join(p.authors[:3])])

    # 实体表
    ent_rows = [[e.kind, e.name, e.normalized, e.value if e.value is not None else "-",
                 e.unit or "-", e.evidence_id or "-"] for e in state.entities]

    # Gap 表
    gap_rows = [[g.gap_id, g.kind, g.statement, ";".join(g.related_evidence)] for g in state.gaps]

    # 假设/构效关系表
    hyp_rows = []
    for h in state.hypotheses:
        nov = "新颖" if h.is_novel else ("已知" if h.is_novel is False else "待验证")
        hyp_rows.append([h.id, h.target_property, h.predicted_value if h.predicted_value is not None else "-",
                         nov, h.status, ";".join(h.evidence_ids)])

    report = f"""# 材料科学文献调研报告（初赛）

> 研究方向：**{state.task}**
> 生成方式：材料科学文献调研智能体（自动检索/抽取/推理/报告）

## 0. 摘要
{intro}

## 1. 方法论（系统架构）
- 检索：Sciverse 语义检索(web) + Sci-Base 本地 RAG(local)
- 解析：MinerU（PDF→结构化）
- 抽取：规则化知识抽取（成分/结构/性质/方法/条件），每条生成证据对象
- 融合：跨文献知识图谱
- Gap：未探索 / 矛盾 / 缺失连接 三类识别
- 路线A：LLM 假设生成 + 贝叶斯优化/遗传算法搜索 + 材料数据库交叉验证
- 核验：结论 100% 可溯源至证据对象

## 2. 检索到的核心文献（交叉引用）
{_md_table(['ID','年份','标题','作者'], paper_rows)}

## 3. 结构化抽取结果
{_md_table(['类型','原始','归一化','数值','单位','证据'], ent_rows)}

## 4. Research Gap 清单
{_md_table(['ID','类型','描述','证据'], gap_rows)}

## 5. 路线A：构效关系发现
{_md_table(['假设','目标性质','预测值','新颖性','状态','证据'], hyp_rows)}

## 6. 证据链（部分）
"""  # 证据链续写在下方

    # 证据链明细
    ev_lines = []
    for eid, ev in state.evidence.items():
        loc = f"p.{ev.page}" if ev.page else "—"
        val = f"{ev.value}{ev.unit}" if ev.value is not None else "—"
        ev_lines.append(f"- **{eid}** [{ev.paper_id} {loc}] {ev.snippet}  →  `{val}`"
                        + (f" 条件:{ev.condition}" if ev.condition else ""))
    report += "\n".join(ev_lines[:40]) + ("\n..." if len(ev_lines) > 40 else "")

    report += f"\n\n## 7. 审计轨迹（节选）\n```\n" + "\n".join(state.audit_log[-25:]) + "\n```\n"

    # 写出
    rpath = os.path.join(out_dir, "report.md")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(report)
    epath = os.path.join(out_dir, "evidence_chain.md")
    with open(epath, "w", encoding="utf-8") as f:
        f.write("# 证据链\n\n" + "\n".join(ev_lines))

    state.report = rpath
    state.log(f"[report] 报告已生成: {rpath}")
    state.log(f"[report] 证据链已生成: {epath}")
    return state
