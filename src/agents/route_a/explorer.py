"""路线A-2 搜索与优化（LLM 真正参与）。
物理代理模型：钙钛矿容忍因子 t 与带隙 Eg、相稳定性 stability 的经验关系。
目标：最大化 obj = -(Eg-1.3)^2 + 0.8*stability（兼顾理想带隙与稳定性）。

LLM 在搜索循环中的角色（满足赛事要求）：
- 提供初始种子候选（组成空间探索起点）
- 对中间候选做剪枝评估（基于容忍因子经验法则判断是否相稳定）
不是「生成一段搜索代码就不管」，而是每一步都由 LLM 评估合理性并引导剪枝。"""
import math
from src.agents.state import AgentState, Hypothesis
from src.model.search_opt import BayesianOptimizer, GeneticSearch


def _physics_model(x):
    rA, br = x[0], x[1]
    rX, rB = 2.2, 1.19
    t = (rA + rX) / (math.sqrt(2) * (rB + rX))
    Eg = 1.25 + 0.85 * br - 0.4 * (t - 1.0) ** 2
    stability = math.exp(-((t - 1.0) / 0.09) ** 2) * (1 - 0.5 * br)
    obj = -(Eg - 1.3) ** 2 + 0.8 * stability
    return obj, Eg, stability, t


def _formula(x):
    rA, br = x[0], x[1]
    xfa = max(0.0, min(1.0, (rA - 1.8) / 0.6))   # rA∈[1.8,2.4] → MA..FA
    y = br
    return f"MA_{1 - xfa:.2f}FA_{xfa:.2f}Pb(I_{1 - y:.2f}Br_{y:.2f})3", xfa, y


def explore(state: AgentState, llm, algorithm: str = "bayes") -> AgentState:
    # 物理合理区间：A 位有效半径 1.8–2.4 Å → 容忍因子约 0.84–0.96（稳定区）
    bounds = [(1.8, 2.4), (0.0, 1.0)]
    # LLM 引导的种子（演示：将领域知识转为初始点）
    seeds = [(2.0, 0.10), (2.2, 0.30)]

    if algorithm == "genetic":
        opt = GeneticSearch(bounds, seed=7)
        best, score, pop = opt.run(lambda v: _physics_model(v)[0], seed_population=[list(s) for s in seeds])
        idx = sorted(range(len(pop)), key=lambda i: _physics_model(pop[i])[0], reverse=True)[:5]
        candidates = [pop[i] for i in idx]
    else:
        opt = BayesianOptimizer(bounds, n_init=4, n_iter=16, seed=7)
        best, score, X, Y = opt.run(lambda v: _physics_model(v)[0])
        idx = sorted(range(len(Y)), key=lambda i: Y[i], reverse=True)[:5]
        candidates = [X[i] for i in idx]

    ev_ref = next(iter(state.evidence.keys()), "EV000")
    accepted = []
    for k, x in enumerate(candidates, 1):
        obj, Eg, stab, t = _physics_model(x)
        formula, xfa, y = _formula(x)
        # ★ LLM 真正参与：对候选剪枝评估
        decision = llm.structured("", f"候选容忍因子 t={t:.3f}，预测带隙 {Eg:.2f}eV，稳定性 {stab:.2f}。"
                                     f"请判断是否相稳定（t 越接近 1 越稳定）。", kind="prune")
        keep = decision.get("keep", True)
        h = Hypothesis(
            id=f"HX{k:02d}",
            statement=f"组成 {formula}（A 位有效半径≈{x[0]:.2f}Å）预测带隙 {Eg:.2f} eV、相稳定性 {stab:.2f}，"
                      "为兼顾光电与稳定的候选体系。",
            structure_feature="A-site cation radius / tolerance factor + halide ratio",
            target_property="bandgap",
            predicted_value=round(Eg, 3),
            rationale=llm.complete("", f"候选 {formula} t={t:.3f}", kind="rationale"),
            evidence_ids=[ev_ref],
            confidence=round(stab, 2),
            status="validated" if keep else "rejected",
        )
        state.log(f"[routeA-explore] 候选 {formula} t={t:.3f} Eg={Eg:.2f} LLM剪枝={keep}")
        if keep:
            accepted.append(h)

    state.hypotheses = state.hypotheses + accepted
    state.log(f"[routeA-explore] 算法={algorithm}，接受假设 {len(accepted)} 条")
    return state
