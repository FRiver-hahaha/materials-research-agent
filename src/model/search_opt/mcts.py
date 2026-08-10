"""蒙特卡洛树搜索（路线 A 搜索算法之一）。
在离散组成决策树上搜索：依次选择 A 位 / B 位 / X 位卤素，UCB 选择 + 随机 rollout。
适合「组合空间可枚举、每步有明确物理约束」的构效搜索场景。"""
import math
import random


class _Node:
    def __init__(self, choice=None, parent=None):
        self.choice = choice
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0.0


class MCTS:
    def __init__(self, choices_per_level, n_sim=200, seed=0, c=1.4):
        # choices_per_level: list[list[str]]，每个决策层的可选项
        self.levels = choices_per_level
        self.n_sim = n_sim
        self.c = c
        random.seed(seed)
        self.root = _Node()

    def _rollout(self, partial):
        # partial: 已选路径；补齐剩余层后评估
        while len(partial) < len(self.levels):
            partial = partial + [random.choice(self.levels[len(partial)])]
        return self.evaluate(partial)

    def evaluate(self, path):
        """由子类/外部赋值；默认返回 0。explorer 中替换为真实评分。"""
        return 0.0

    def _select(self, node):
        path = []
        while node.children:
            best, best_u = None, -1e9
            for ch in node.children.values():
                u = (ch.value / ch.visits if ch.visits else 0) + \
                    self.c * math.sqrt(math.log(node.visits + 1) / (ch.visits + 1))
                if u > best_u:
                    best_u, best = u, ch
            node = best
            path.append(node.choice)
        return node, path

    def _expand(self, node, depth):
        if depth >= len(self.levels):
            return node
        for opt in self.levels[depth]:
            node.children[opt] = _Node(choice=opt, parent=node)
        return random.choice(list(node.children.values()))

    def run(self):
        for _ in range(self.n_sim):
            leaf, path = self._select(self.root)
            depth = len(path)
            if leaf.visits == 0 and depth < len(self.levels):
                leaf = self._expand(leaf, depth)
                path = path + [leaf.choice]
            reward = self._rollout(path)
            # 回溯
            node = leaf
            while node:
                node.visits += 1
                node.value += reward
                node = node.parent
        # 返回根下访问最多的子节点路径
        best = max(self.root.children.values(), key=lambda n: n.visits)
        return self._best_path(best)

    def _best_path(self, node):
        path = []
        while node and node.choice is not None:
            path.append(node.choice)
            node = max(node.children.values(), key=lambda n: n.visits) if node.children else None
        return path
