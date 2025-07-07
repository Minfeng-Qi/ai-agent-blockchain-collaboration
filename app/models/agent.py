"""
Data models for agent-related operations.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Capability(BaseModel):
    """
    Represents an agent's capability in a specific area.
    """
    name: str
    weight: int = Field(..., ge=0, le=100, description="Weight value between 0 and 100")
    description: Optional[str] = None


class AgentBase(BaseModel):
    """
    Base model for agent data.
    """
    name: Optional[str] = None
    description: Optional[str] = None


class AgentCreate(AgentBase):
    """
    Model for creating a new agent.
    """
    address: str
    public_key: str
    capabilities: Dict[str, int] = Field(
        ..., description="Dictionary mapping capability names to weights (0-100)"
    )
    confidence_factor: Optional[int] = Field(
        50, ge=0, le=100, description="Agent's confidence factor (0-100)"
    )
    risk_tolerance: Optional[int] = Field(
        50, ge=0, le=100, description="Agent's risk tolerance (0-100)"
    )


class AgentUpdate(AgentBase):
    """
    Model for updating an existing agent.
    """
    capabilities: Optional[Dict[str, int]] = None
    confidence_factor: Optional[int] = Field(
        None, ge=0, le=100, description="Agent's confidence factor (0-100)"
    )
    risk_tolerance: Optional[int] = Field(
        None, ge=0, le=100, description="Agent's risk tolerance (0-100)"
    )


class AgentInDB(AgentBase):
    """
    Model for an agent as stored in the database.
    """
    address: str
    public_key: str
    capabilities: Dict[str, int]
    reputation: int = Field(
        50, ge=0, le=100, description="Agent's reputation score (0-100)"
    )
    workload: int = Field(
        0, ge=0, description="Current workload of the agent"
    )
    confidence_factor: int = Field(
        50, ge=0, le=100, description="Agent's confidence factor (0-100)"
    )
    risk_tolerance: int = Field(
        50, ge=0, le=100, description="Agent's risk tolerance (0-100)"
    )
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_rewards: int = 0
    registration_date: datetime
    last_updated: datetime


class AgentResponse(AgentInDB):
    """
    Model for agent data returned in API responses.
    """
    average_score: Optional[float] = None
    average_reward: Optional[float] = None
    task_type_distribution: Optional[Dict[str, int]] = None
    learning_metrics: Optional[Dict[str, float]] = None


class AgentCapabilitiesUpdate(BaseModel):
    """
    Model for updating agent capabilities.
    """
    capabilities: Dict[str, int] = Field(
        ..., description="Dictionary mapping capability names to weights (0-100)"
    )


class AgentList(BaseModel):
    """
    Model for a list of agents.
    """
    agents: List[AgentResponse]
    total: int