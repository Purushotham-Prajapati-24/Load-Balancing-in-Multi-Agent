"""
Task generation module.
Generates N heterogeneous tasks with configurable size distributions.
"""

import numpy as np


class Task:
    """A single task with an ID and processing requirement."""

    def __init__(self, task_id: int, size: float):
        self.task_id = task_id
        self.size = size  # p_j: intrinsic processing requirement

    def __repr__(self):
        return f"Task(id={self.task_id}, size={self.size:.4f})"


class TaskGenerator:
    """Generate task sets with various distributions."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def uniform(self, n: int, low: float = 1.0, high: float = 100.0) -> list[Task]:
        """Tasks with uniformly distributed sizes."""
        sizes = self.rng.uniform(low, high, size=n)
        return [Task(i, s) for i, s in enumerate(sizes)]

    def pareto(self, n: int, alpha: float = 1.5, scale: float = 1.0) -> list[Task]:
        """Tasks with Pareto (heavy-tail) distributed sizes.
        Models real workloads where few tasks are very large.
        """
        sizes = (self.rng.pareto(alpha, size=n) + 1) * scale
        return [Task(i, s) for i, s in enumerate(sizes)]

    def bimodal(self, n: int, small_range: tuple = (1.0, 10.0),
                large_range: tuple = (50.0, 100.0), large_fraction: float = 0.2) -> list[Task]:
        """Bimodal distribution: mostly small tasks with some large ones."""
        n_large = max(1, int(n * large_fraction))
        n_small = n - n_large
        small_sizes = self.rng.uniform(small_range[0], small_range[1], size=n_small)
        large_sizes = self.rng.uniform(large_range[0], large_range[1], size=n_large)
        all_sizes = np.concatenate([small_sizes, large_sizes])
        self.rng.shuffle(all_sizes)
        return [Task(i, s) for i, s in enumerate(all_sizes)]

    def exponential(self, n: int, mean: float = 10.0) -> list[Task]:
        """Tasks with exponentially distributed sizes."""
        sizes = self.rng.exponential(mean, size=n)
        sizes = np.maximum(sizes, 0.1)  # Ensure minimum size
        return [Task(i, s) for i, s in enumerate(sizes)]

    def adversarial(self, n: int, m: int) -> list[Task]:
        """Adversarial instance designed to expose worst-case greedy behavior.
        Creates tasks that force greedy to make suboptimal assignments.
        """
        # Pattern: m large tasks of size m, then m*(m-1) small tasks of size 1
        sizes = []
        n_large = min(m, n)
        n_small = n - n_large
        sizes.extend([float(m)] * n_large)
        sizes.extend([1.0] * n_small)
        return [Task(i, s) for i, s in enumerate(sizes)]
