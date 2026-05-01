"""
Random assignment scheduler — baseline for comparison.
"""

import numpy as np
from simulator.agents import AgentPool
from simulator.tasks import Task


class RandomScheduler:
    """Randomly assign each task to an agent (uniform random)."""

    name = "Random"

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        agents.reset_all()
        for task in tasks:
            idx = self.rng.randint(0, agents.M)
            agents.agents[idx].assign_task(task.task_id, task.size)
        return agents.makespan()
