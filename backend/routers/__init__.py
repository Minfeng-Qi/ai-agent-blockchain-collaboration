"""
Routers package for the Agent Learning System API.
"""
from .agents import router as agents
from .tasks import router as tasks
from .learning import router as learning
from .blockchain import router as blockchain
from .collaboration import router as collaboration

__all__ = ["agents", "tasks", "learning", "blockchain", "collaboration"]