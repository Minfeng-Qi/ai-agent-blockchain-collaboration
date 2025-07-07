"""
Routers package for the Agent Learning System API.
"""
from .agents import router as agents
from .tasks import router as tasks
from .learning import router as learning
from .blockchain import router as blockchain
# from .collaboration import router as collaboration  # Temporarily disabled due to missing openai dependency
from .analytics import router as analytics

__all__ = ["agents", "tasks", "learning", "blockchain", "analytics"]  # "collaboration" temporarily disabled