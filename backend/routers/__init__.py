"""
Routers package for the Agent Learning System API.
"""
from .agents import router as agents
from .tasks import router as tasks
from .learning import router as learning
from .blockchain import router as blockchain
# from .collaboration import router as collaboration  # Temporarily disabled due to missing openai dependency
from .analytics import router as analytics
from .agent_selection import router as agent_selection
from .simple_task_assignment import router as simple_task_assignment

__all__ = ["agents", "tasks", "learning", "blockchain", "analytics", "agent_selection", "simple_task_assignment"]  # "collaboration" temporarily disabled