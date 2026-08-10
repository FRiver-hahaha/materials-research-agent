"""遗传算法（路线 A 搜索算法之一）。
在离散/连续混合组成空间中进化候选材料，适应度=目标性质评分。
LLM 提供初始种群种子并参与变异方向引导（explorer 中调用）。"""
import random


class GeneticSearch:
    def __init__(self, bounds, pop_size=12, n_gen=10, seed=0, mutate_rate=0.3):
        self.bounds = bounds
        self.pop_size = pop_size
        self.n_gen = n_gen
        self.mutate_rate = mutate_rate
        random.seed(seed)

    def _random(self):
        return [random.uniform(lo, hi) for lo, hi in self.bounds]

    def _mutate(self, x):
        return [min(max(v + random.gauss(0, (hi - lo) * 0.15), lo), hi)
                for v, (lo, hi) in zip(x, self.bounds)]

    def _crossover(self, a, b):
        return [a[i] if random.random() < 0.5 else b[i] for i in range(len(a))]

    def run(self, objective, seed_population=None):
        pop = list(seed_population) if seed_population else []
        while len(pop) < self.pop_size:
            pop.append(self._random())
        scored = [(objective(x), x) for x in pop]
        for _ in range(self.n_gen):
            scored.sort(key=lambda t: t[0], reverse=True)
            elite = [x for _, x in scored[: max(2, self.pop_size // 4)]]
            new_pop = elite[:]
            while len(new_pop) < self.pop_size:
                if random.random() < self.mutate_rate:
                    new_pop.append(self._mutate(random.choice(elite)))
                else:
                    new_pop.append(self._crossover(random.choice(elite), random.choice(elite)))
            scored = [(objective(x), x) for x in new_pop]
        scored.sort(key=lambda t: t[0], reverse=True)
        return scored[0][1], scored[0][0], [x for _, x in scored]
