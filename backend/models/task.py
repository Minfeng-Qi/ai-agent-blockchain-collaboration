"""
Data models for task-related operations.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """
    Enum for task status values.
    """
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """
    Enum for task type values.
    """
    ANALYSIS = "analysis"
    GENERATION = "generation"
    CLASSIFICATION = "classification"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    OTHER = "other"


class TaskBase(BaseModel):
    """
    Base model for task data.
    """
    title: str
    description: str
    task_type: TaskType
    complexity: int = Field(..., ge=1, le=100, description="Task complexity (1-100)")
    reward: int = Field(..., ge=0, description="Reward amount for the task")
    deadline: Optional[datetime] = None
    tags: Dict[str, int] = Field(
        default_factory=dict,
        description="Dictionary mapping tag names to importance weights (0-100)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    """
    creator_address: str


class TaskUpdate(BaseModel):
    """
    Model for updating an existing task.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    complexity: Optional[int] = Field(
        None, ge=1, le=100, description="Task complexity (1-100)"
    )
    reward: Optional[int] = Field(
        None, ge=0, description="Reward amount for the task"
    )
    deadline: Optional[datetime] = None
    tags: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskAssign(BaseModel):
    """
    Model for assigning a task to an agent.
    """
    agent_address: str
    bid_amount: Optional[int] = None


class TaskComplete(BaseModel):
    """
    Model for completing a task.
    """
    result: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskInDB(TaskBase):
    """
    Model for a task as stored in the database.
    """
    task_id: str
    creator_address: str
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.AVAILABLE
    created_at: datetime
    updated_at: datetime
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    score: Optional[int] = None
    bid_amount: Optional[int] = None


class TaskResponse(TaskInDB):
    """
    Model for task data returned in API responses.
    """
    pass


class TaskList(BaseModel):
    """
    Model for a list of tasks.
    """
    tasks: List[TaskResponse]
    total: int


class TaskStats(BaseModel):
    """
    Model for task statistics.
    """
    total: int
    available: int
    assigned: int
    completed: int
    failed: int
    cancelled: int
    average_reward: float
    average_complexity: float
    average_completion_time: Optional[float] = None
    task_type_distribution: Dict[str, int]
    recent_tasks: List[TaskResponse]
    top_agents: List[Dict[str, Any]]