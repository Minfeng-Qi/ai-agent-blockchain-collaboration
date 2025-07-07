"""
Data models for learning-related operations.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LearningMetrics(BaseModel):
    """
    Model for agent learning metrics.
    """
    agent_address: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_score: float = 0.0
    average_reward: float = 0.0
    capability_growth: Dict[str, float] = Field(default_factory=dict)
    confidence_factor: int = Field(
        50, ge=0, le=100, description="Agent's confidence factor (0-100)"
    )
    risk_tolerance: int = Field(
        50, ge=0, le=100, description="Agent's risk tolerance (0-100)"
    )
    learning_rate: float = 0.001
    exploration_rate: float = 0.1
    last_updated: datetime


class LearningUpdate(BaseModel):
    """
    Model for updating agent learning parameters.
    """
    learning_rate: Optional[float] = None
    exploration_rate: Optional[float] = None
    confidence_factor: Optional[int] = Field(
        None, ge=0, le=100, description="Agent's confidence factor (0-100)"
    )
    risk_tolerance: Optional[int] = Field(
        None, ge=0, le=100, description="Agent's risk tolerance (0-100)"
    )


class TaskResult(BaseModel):
    """
    Model for task result data used in learning.
    """
    task_id: str
    task_type: str
    score: int = Field(..., ge=0, le=100, description="Task score (0-100)")
    reward: int
    tags: Dict[str, int] = Field(
        default_factory=dict,
        description="Dictionary mapping tag names to scores (0-100)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningEvent(BaseModel):
    """
    Model for a learning event.
    """
    event_id: str
    agent_address: str
    event_type: str
    task_id: Optional[str] = None
    timestamp: datetime
    details: Dict[str, Any]
    capability_changes: Dict[str, float] = Field(default_factory=dict)


class LearningReport(BaseModel):
    """
    Model for an agent learning report.
    """
    agent_address: str
    report_id: str
    timestamp: datetime
    metrics: LearningMetrics
    capabilities: Dict[str, int]
    capability_changes: Dict[str, float]
    recent_events: List[LearningEvent]
    task_type_distribution: Dict[str, int]
    performance_trend: Dict[str, List[float]]
    recommendations: Dict[str, Any]