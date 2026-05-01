"""
Offline LPT (Longest Processing Time) Scheduler.
Sorts tasks by descending size, then applies ECT greedy assignment.
This is Graham's LPT rule generalized to heterogeneous machines.

Approximation ratio:
  - Identical machines: (4/3 - 1/(3M))
  - General: bounded constant-factor approximation
"""

from simulator.agents import AgentPool
from simulator.tasks import Task


class OfflineLPTScheduler:
    """Offline scheduler using Longest Processing Time first rule."""

    name = "Offline LPT"

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        """
        Sort tasks by descending size (LPT order), then assign each
        to the agent with minimum projected completion time.

        Returns: makespan (max load across all agents).
        """
        agents.reset_all()

        # Sort tasks by descending processing requirement
        sorted_tasks = sorted(tasks, key=lambda t: t.size, reverse=True)

        for task in sorted_tasks:
            best_agent = None
            best_completion = float('inf')

            for agent in agents.agents:
                ct = agent.completion_time(task.size)
                if ct < best_completion:
                    best_completion = ct
                    best_agent = agent

            best_agent.assign_task(task.task_id, task.size)

        return agents.makespan()
