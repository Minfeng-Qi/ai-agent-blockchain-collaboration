"""
Router for agent-related endpoints.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse

from app.models.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentList, AgentCapabilitiesUpdate
)
from app.services.agent_service import agent_service

router = APIRouter()


@router.get("/", response_model=AgentList)
async def get_agents(
    skip: int = Query(0, ge=0, description="Number of agents to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of agents to return")
):
    """
    Get a list of registered agents.
    """
    agents = await agent_service.get_agents(skip=skip, limit=limit)
    return agents


@router.get("/{agent_address}", response_model=AgentResponse)
async def get_agent(
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Get details for a specific agent.
    """
    agent = await agent_service.get_agent(agent_address)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(agent_data: AgentCreate):
    """
    Register a new agent.
    """
    # Check if agent already exists
    existing_agent = await agent_service.get_agent(agent_data.address)
    if existing_agent:
        raise HTTPException(status_code=400, detail="Agent already registered")
    
    agent = await agent_service.create_agent(agent_data)
    if not agent:
        raise HTTPException(status_code=500, detail="Failed to register agent")
    
    return agent


@router.put("/{agent_address}", response_model=AgentResponse)
async def update_agent(
    agent_data: AgentUpdate,
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Update an existing agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    updated_agent = await agent_service.update_agent(agent_address, agent_data)
    if not updated_agent:
        raise HTTPException(status_code=500, detail="Failed to update agent")
    
    return updated_agent


@router.get("/{agent_address}/capabilities")
async def get_agent_capabilities(
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Get capabilities for a specific agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    capabilities = await agent_service.get_agent_capabilities(agent_address)
    return JSONResponse(content=capabilities)


@router.put("/{agent_address}/capabilities", response_model=AgentResponse)
async def update_agent_capabilities(
    capabilities_data: AgentCapabilitiesUpdate,
    agent_address: str = Path(..., description="The address of the agent")
):
    """
    Update capabilities for a specific agent.
    """
    # Check if agent exists
    existing_agent = await agent_service.get_agent(agent_address)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    updated_agent = await agent_service.update_agent_capabilities(
        agent_address, 
        capabilities_data.capabilities
    )
    
    if not updated_agent:
        raise HTTPException(status_code=500, detail="Failed to update agent capabilities")
    
    return updated_agent