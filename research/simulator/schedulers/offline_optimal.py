"""
Offline Optimal Scheduler — brute-force / ILP for small instances.
Used as the ground-truth baseline C* for computing competitive ratios.

For large N this is intractable; we use it only for N <= 20 or as a
lower-bound estimator via the LP relaxation.
"""

import itertools
from simulator.agents import AgentPool
from simulator.tasks import Task


class OfflineOptimalScheduler:
    """
    Compute (or approximate) the optimal offline makespan.

    For small instances (N <= max_brute_force): exact brute-force enumeration.
    For larger instances: uses lower bounds max(sum(p_j)/(sum(s_i)), max(p_j/max(s_i))).
    """

    name = "Offline Optimal"

    def __init__(self, max_brute_force: int = 15):
        self.max_brute_force = max_brute_force

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        """Compute the optimal makespan (or best lower bound)."""
        agents.reset_all()
        n = len(tasks)
        m = agents.M

        if n <= self.max_brute_force and m <= 8:
            return self._brute_force(agents, tasks)
        else:
            return self._lower_bound(agents, tasks)

    def _brute_force(self, agents: AgentPool, tasks: list[Task]) -> float:
        """Enumerate all possible assignments to find the true optimum."""
        n = len(tasks)
        m = agents.M
        best_makespan = float('inf')

        # Each task can go to any of M agents: M^N assignments
        for assignment in itertools.product(range(m), repeat=n):
            loads = [0.0] * m
            for task_idx, agent_idx in enumerate(assignment):
                loads[agent_idx] += tasks[task_idx].size / agents.agents[agent_idx].speed
            makespan = max(loads)
            if makespan < best_makespan:
                best_makespan = makespan

        return best_makespan

    def _lower_bound(self, agents: AgentPool, tasks: list[Task]) -> float:
        """
        Compute a lower bound on OPT using two standard bounds:
          LB1 = sum(p_j) / sum(s_i)   (total work / total capacity)
          LB2 = max(p_j) / max(s_i)   (largest task on fastest machine)

        Returns max(LB1, LB2).
        """
        total_work = sum(t.size for t in tasks)
        total_speed = sum(a.speed for a in agents.agents)
        max_speed = max(a.speed for a in agents.agents)
        max_task = max(t.size for t in tasks)

        lb1 = total_work / total_speed
        lb2 = max_task / max_speed

        return max(lb1, lb2)

    def compute_optimal_or_bound(self, agents: AgentPool, tasks: list[Task]) -> tuple[float, bool]:
        """
        Returns (makespan, is_exact).
        is_exact = True if brute-force was used, False if lower bound.
        """
        n = len(tasks)
        m = agents.M
        if n <= self.max_brute_force and m <= 8:
            return self._brute_force(agents, tasks), True
        else:
            return self._lower_bound(agents, tasks), False
