"""
Online Greedy Scheduler (List Scheduling / ECT Rule).
Assigns each task to the agent with the earliest completion time.
This is the baseline online algorithm — Graham's List Scheduling generalized
to heterogeneous machines.

Competitive ratio:
  - Identical machines: (2 - 1/M)
  - Related machines: O(log M)
  - Unrelated machines: O(log n)
"""

from simulator.agents import AgentPool
from simulator.tasks import Task


class OnlineGreedyScheduler:
    """Online greedy scheduler using Earliest Completion Time (ECT) rule."""

    name = "Online Greedy (ECT)"

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        """
        Assign tasks one-by-one in arrival order to the agent
        with minimum projected completion time.

        Returns: makespan (max load across all agents).
        """
        agents.reset_all()

        for task in tasks:
            # Find agent that minimizes completion time for this task
            best_agent = None
            best_completion = float('inf')

            for agent in agents.agents:
                ct = agent.completion_time(task.size)
                if ct < best_completion:
                    best_completion = ct
                    best_agent = agent

            best_agent.assign_task(task.task_id, task.size)

        return agents.makespan()
