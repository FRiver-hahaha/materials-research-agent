"""贝叶斯优化（路线 A 搜索算法之一）。
纯 Python 实现核岭回归代理模型 + 期望提升(EI)采集，无需 numpy。
用于在连续成分空间中寻找「目标带隙≈1.3eV 且相稳定性最高」的最优组成。
LLM 提供初始种子点(seed)并参与剪枝（见 route_a/explorer.py）。"""
import math
import random


def _solve(A, b):
    """高斯消元解线性方程组 Ax=b（小规模，N<=数十）。"""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        piv = M[i][i] or 1e-12
        for j in range(i, n + 1):
            M[i][j] /= piv
        for r in range(n):
            if r != i:
                f = M[r][i]
                for j in range(i, n + 1):
                    M[r][j] -= f * M[i][j]
    return [M[i][n] for i in range(n)]


def _expected_improvement(mean, var, best):
    """EI 采集函数（解析形式，假设高斯噪声）。"""
    if var <= 1e-9:
        return 0.0
    z = (mean - best) / math.sqrt(var)
    return (mean - best) * _cdf(z) + math.sqrt(var) * _pdf(z)


def _cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _pdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


class BayesianOptimizer:
    def __init__(self, bounds, n_init=4, n_iter=12, seed=0, length=0.6, sigma=1.0):
        self.bounds = bounds
        self.dim = len(bounds)
        self.length, self.sigma = length, sigma
        self.n_iter = n_iter
        self.n_init = n_init
        random.seed(seed)
        self.X, self.y = [], []

    def _kernel(self, a, b):
        d2 = sum((x - y) ** 2 for x, y in zip(a, b))
        return self.sigma ** 2 * math.exp(-0.5 * d2 / (self.length ** 2))

    def _posterior(self, x):
        N = len(self.X)
        K = [[self._kernel(self.X[i], self.X[j]) + (1e-6 if i == j else 0)
              for j in range(N)] for i in range(N)]
        k = [self._kernel(x, self.X[i]) for i in range(N)]
        alpha = _solve(K, self.y)
        mean = sum(k[i] * alpha[i] for i in range(N))
        v = _solve(K, k)
        var = self.sigma ** 2 - sum(k[i] * v[i] for i in range(N))
        return mean, max(var, 1e-9)

    def step(self, objective, seed=None):
        if seed:
            random.seed(seed)
        # 冷启动：尚无评估点时随机采样
        if not self.y:
            x = [random.uniform(lo, hi) for lo, hi in self.bounds]
            y = objective(x)
            self.X.append(x)
            self.y.append(y)
            return x, y
        best = max(self.y)
        best_x, best_ei = None, -1e9
        for _ in range(300):
            x = [random.uniform(lo, hi) for lo, hi in self.bounds]
            mean, var = self._posterior(x)
            ei = _expected_improvement(mean, var, best)
            if ei > best_ei:
                best_ei, best_x = ei, x
        y = objective(best_x)
        self.X.append(best_x)
        self.y.append(y)
        return best_x, y

    def run(self, objective):
        for _ in range(self.n_init):
            self.step(objective)
        for _ in range(self.n_iter):
            self.step(objective)
        bi = max(range(len(self.y)), key=lambda i: self.y[i])
        return self.X[bi], self.y[bi], self.X, self.y
