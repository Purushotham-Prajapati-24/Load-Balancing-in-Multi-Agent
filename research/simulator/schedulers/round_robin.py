"""
Round-Robin scheduler — baseline for comparison.
"""

from simulator.agents import AgentPool
from simulator.tasks import Task


class RoundRobinScheduler:
    """Assign tasks in round-robin fashion across agents."""

    name = "Round Robin"

    def schedule(self, agents: AgentPool, tasks: list[Task]) -> float:
        agents.reset_all()
        for idx, task in enumerate(tasks):
            agent = agents.agents[idx % agents.M]
            agent.assign_task(task.task_id, task.size)
        return agents.makespan()
