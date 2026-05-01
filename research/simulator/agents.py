"""
Agent (Machine) model for the MAS scheduler simulator.
Each agent has a speed (computational capacity) and tracks its current load.
"""

import numpy as np


class Agent:
    """Represents a computational agent/machine with a given speed."""

    def __init__(self, agent_id: int, speed: float = 1.0):
        self.agent_id = agent_id
        self.speed = speed
        self.load = 0.0  # Current accumulated processing time
        self.assigned_tasks = []  # List of (task_id, processing_time_on_this_agent)

    def processing_time(self, task_size: float) -> float:
        """Time to process a task of given size on this agent."""
        return task_size / self.speed

    def completion_time(self, task_size: float) -> float:
        """Projected completion time if this task is assigned here."""
        return self.load + self.processing_time(task_size)

    def assign_task(self, task_id: int, task_size: float):
        """Assign a task to this agent and update load."""
        pt = self.processing_time(task_size)
        self.load += pt
        self.assigned_tasks.append((task_id, pt))

    def reset(self):
        """Reset agent state for a new experiment run."""
        self.load = 0.0
        self.assigned_tasks = []

    def __repr__(self):
        return f"Agent(id={self.agent_id}, speed={self.speed:.2f}, load={self.load:.4f})"


class AgentPool:
    """A pool of M agents with configurable speed distributions."""

    def __init__(self, agents: list[Agent]):
        self.agents = agents
        self.M = len(agents)

    @classmethod
    def identical(cls, m: int) -> "AgentPool":
        """Create M identical agents (P||Cmax setting)."""
        return cls([Agent(i, speed=1.0) for i in range(m)])

    @classmethod
    def uniform(cls, m: int, speed_range: tuple = (1.0, 10.0), seed: int = 42) -> "AgentPool":
        """Create M agents with uniform random speeds (Q||Cmax setting)."""
        rng = np.random.RandomState(seed)
        speeds = rng.uniform(speed_range[0], speed_range[1], size=m)
        return cls([Agent(i, speed=s) for i, s in enumerate(speeds)])

    @classmethod
    def bimodal(cls, m: int, slow_speed: float = 1.0, fast_speed: float = 10.0,
                fast_fraction: float = 0.3, seed: int = 42) -> "AgentPool":
        """Create agents with bimodal speed distribution (some fast, some slow)."""
        rng = np.random.RandomState(seed)
        n_fast = max(1, int(m * fast_fraction))
        speeds = [slow_speed] * (m - n_fast) + [fast_speed] * n_fast
        rng.shuffle(speeds)
        return cls([Agent(i, speed=s) for i, s in enumerate(speeds)])

    def reset_all(self):
        """Reset all agents for a new experiment."""
        for agent in self.agents:
            agent.reset()

    def makespan(self) -> float:
        """Current makespan (maximum load across all agents)."""
        return max(a.load for a in self.agents)

    def total_load(self) -> float:
        """Total load across all agents."""
        return sum(a.load for a in self.agents)

    def utilization(self) -> float:
        """Average utilization = total_load / (M * makespan)."""
        ms = self.makespan()
        if ms == 0:
            return 0.0
        return self.total_load() / (self.M * ms)

    def load_vector(self) -> list[float]:
        """Return the load on each agent."""
        return [a.load for a in self.agents]
