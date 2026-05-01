"""
Hybrid Adaptive Scheduler (HAS) — NOVEL CONTRIBUTION.

Combines offline batching (LPT) with online greedy (ECT) via a tunable
parameter alpha that controls the batch fraction.

  alpha = 0: Pure online greedy (ECT)
  alpha = 1: Full offline LPT
  0 < alpha < 1: Collect alpha fraction of tasks in a buffer, sort and
                  assign in LPT order, then handle remaining tasks online.

Key insight: Batching the first alpha*N tasks and applying LPT provides
a "warm start" that improves the competitive ratio from (2-1/M) toward
(4/3-1/3M), while still handling the remaining (1-alpha)*N tasks online.

Competitive ratio (Theorem 3):
  C_HAS <= alpha * (4/3 - 1/(3M)) + (1 - alpha) * (2 - 1/M)  [identical]
  C_HAS <= O(log(n * (1-alpha)))  [unrelated, for alpha > 0]
"""

from simulator.agents import AgentPool
from simulator.tasks import Task


class HybridAdaptiveScheduler:
    """
    Hybrid Adaptive Scheduler with tunable batch parameter alpha.

    Parameters:
        alpha: float in [0, 1] — fraction of tasks to batch before scheduling.
               0 = pure online, 1 = pure offline LPT.
    """

    def __init__(self, alpha: float = 0.5):
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be in [0, 1], got {alpha}")
        self.alpha = alpha
        self.name = f"HAS (a={alpha:.2f})"

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        """
        Schedule tasks using the hybrid batch+online strategy.

        Phase 1 (Batch): Collect first alpha*N tasks, sort by LPT, assign greedily.
        Phase 2 (Online): Assign remaining tasks one-by-one using ECT.

        Returns: makespan (max load across all agents).
        """
        agents.reset_all()
        n = len(tasks)
        batch_size = int(self.alpha * n)

        # ── Phase 1: Batch (LPT) ──────────────────────────────────
        batch_tasks = tasks[:batch_size]
        online_tasks = tasks[batch_size:]

        # Sort batch by descending size (LPT order)
        batch_sorted = sorted(batch_tasks, key=lambda t: t.size, reverse=True)

        for task in batch_sorted:
            best_agent = self._find_best_agent(agents, task)
            best_agent.assign_task(task.task_id, task.size)

        # ── Phase 2: Online (ECT) ─────────────────────────────────
        for task in online_tasks:
            best_agent = self._find_best_agent(agents, task)
            best_agent.assign_task(task.task_id, task.size)

        return agents.makespan()

    @staticmethod
    def _find_best_agent(agents: AgentPool, task: Task):
        """Find agent with minimum completion time for the given task."""
        best_agent = None
        best_completion = float('inf')
        for agent in agents.agents:
            ct = agent.completion_time(task.size)
            if ct < best_completion:
                best_completion = ct
                best_agent = agent
        return best_agent
