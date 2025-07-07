"""
Router for learning-related endpoints.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Path, Body
from fastapi.responses import JSONResponse

from app.models.learning import (
    LearningMetrics, LearningUpdate, TaskResult, LearningReport
)
from app.services.learning_service import learning_service
from app.services.agent_service import agent_service

router = APIRouter()


@router.get("/{agent_address}", response_model=LearningMetrics)
async def get_learning_metrics(
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Get learning metrics for an agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    metrics = await learning_service.get_learning_metrics(agent_address)
    if not metrics:
        raise HTTPException(status_code=404, detail="Learning metrics not found")
    
    return metrics


@router.put("/{agent_address}", response_model=LearningMetrics)
async def update_learning_parameters(
    update_data: LearningUpdate,
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Update learning parameters for an agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    updated_metrics = await learning_service.update_learning_parameters(
        agent_address, 
        update_data
    )
    
    if not updated_metrics:
        raise HTTPException(status_code=500, detail="Failed to update learning parameters")
    
    return updated_metrics


@router.post("/{agent_address}/task-result", response_model=Dict[str, Any])
async def process_task_result(
    task_result: TaskResult,
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Process a task result for learning.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    result = await learning_service.process_task_result(agent_address, task_result)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to process task result")
    
    return result


@router.get("/{agent_address}/report", response_model=LearningReport)
async def generate_learning_report(
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Generate a learning report for an agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    report = await learning_service.generate_learning_report(agent_address)
    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate learning report")
    
    return report