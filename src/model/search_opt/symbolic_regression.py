"""符号回归（路线 A 搜索算法之一）。
用遗传编程从 (结构特征, 性质) 数据中发现可解释的「构效关系方程」，
比黑箱模型更符合赛事对「可解释性」的要求。纯 Python 表达式树进化。"""
import random


class SymbolicRegression:
    def __init__(self, operators=("+", "-", "*", "sin", "cos"), pop_size=40, n_gen=20, seed=0):
        self.ops = operators
        self.pop_size = pop_size
        self.n_gen = n_gen
        random.seed(seed)

    def _rand_tree(self, depth=2, var="x"):
        if depth <= 0 or random.random() < 0.3:
            return var if random.random() < 0.5 else str(round(random.uniform(-3, 3), 2))
        op = random.choice(self.ops)
        if op in ("sin", "cos"):
            return [op, self._rand_tree(depth - 1, var)]
        return [op, self._rand_tree(depth - 1, var), self._rand_tree(depth - 1, var)]

    @staticmethod
    def _eval(tree, x):
        try:
            if isinstance(tree, str):
                return float(tree) if tree.replace(".", "", 1).replace("-", "", 1).isdigit() else x
            op, *args = tree
            if op == "+":
                return _safe(SymbolicRegression._eval(args[0], x) + SymbolicRegression._eval(args[1], x))
            if op == "-":
                return _safe(SymbolicRegression._eval(args[0], x) - SymbolicRegression._eval(args[1], x))
            if op == "*":
                return _safe(SymbolicRegression._eval(args[0], x) * SymbolicRegression._eval(args[1], x))
            if op == "sin":
                return _safe(math_sin(SymbolicRegression._eval(args[0], x)))
            if op == "cos":
                return _safe(math_cos(SymbolicRegression._eval(args[0], x)))
        except Exception:
            return 0.0
        return 0.0

    def _fitness(self, tree, data):
        err = 0.0
        for x, y in data:
            err += (self._eval(tree, x) - y) ** 2
        return -err  # 越大越好

    def run(self, data):
        pop = [self._rand_tree() for _ in range(self.pop_size)]
        for _ in range(self.n_gen):
            scored = sorted(pop, key=lambda t: self._fitness(t, data), reverse=True)
            elite = scored[: max(2, self.pop_size // 5)]
            new_pop = elite[:]
            while len(new_pop) < self.pop_size:
                a, b = random.choice(elite), random.choice(elite)
                child = self._crossover(a, b)
                if random.random() < 0.2:
                    child = self._mutate(child)
                new_pop.append(child)
            pop = new_pop
        best = max(pop, key=lambda t: self._fitness(t, data))
        return best, -self._fitness(best, data)


def _safe(v):
    if v != v or v in (float("inf"), float("-inf")):
        return 0.0
    return v


def math_sin(v):
    import math
    return math.sin(v)


def math_cos(v):
    import math
    return math.cos(v)


def _crossover(a, b, p=0.5):
    if not isinstance(a, list) or random.random() > p:
        return a if random.random() < 0.5 else b
    op = a[0]
    if op in ("sin", "cos"):
        return [op, _crossover(a[1], b[1] if isinstance(b, list) else b)]
    return [op, _crossover(a[1], b[1] if isinstance(b, list) and len(b) > 1 else b),
            _crossover(a[2], b[2] if isinstance(b, list) and len(b) > 2 else b)]


def _mutate(t):
    if isinstance(t, list):
        return SymbolicRegression()._rand_tree(depth=1)
    return str(round(random.uniform(-3, 3), 2))
