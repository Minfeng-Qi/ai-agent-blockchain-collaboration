"""
Router for task-related endpoints.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse

from app.models.task import (
    TaskCreate, TaskUpdate, TaskAssign, TaskComplete,
    TaskResponse, TaskList, TaskStats, TaskStatus
)
from app.services.task_service import task_service

router = APIRouter()


@router.get("/", response_model=TaskList)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return"),
    status: Optional[str] = Query(None, description="Filter tasks by status")
):
    """
    Get a list of tasks.
    """
    tasks = await task_service.get_tasks(skip=skip, limit=limit, status=status)
    return tasks


@router.get("/available", response_model=TaskList)
async def get_available_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return")
):
    """
    Get a list of available tasks.
    """
    tasks = await task_service.get_tasks(skip=skip, limit=limit, status="available")
    return tasks


@router.get("/assigned", response_model=TaskList)
async def get_assigned_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return")
):
    """
    Get a list of assigned tasks.
    """
    tasks = await task_service.get_tasks(skip=skip, limit=limit, status="assigned")
    return tasks


@router.get("/completed", response_model=TaskList)
async def get_completed_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of tasks to return")
):
    """
    Get a list of completed tasks.
    """
    tasks = await task_service.get_tasks(skip=skip, limit=limit, status="completed")
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str = Path(..., description="The ID of the task")
):
    """
    Get details for a specific task.
    """
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate):
    """
    Create a new task.
    """
    task = await task_service.create_task(task_data)
    if not task:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_data: TaskUpdate,
    task_id: str = Path(..., description="The ID of the task")
):
    """
    Update an existing task.
    """
    # Check if task exists
    existing_task = await task_service.get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task is available
    if existing_task.status != TaskStatus.AVAILABLE:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot update task with status {existing_task.status}"
        )
    
    updated_task = await task_service.update_task(task_id, task_data)
    if not updated_task:
        raise HTTPException(status_code=500, detail="Failed to update task")
    
    return updated_task


@router.put("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    assign_data: TaskAssign,
    task_id: str = Path(..., description="The ID of the task")
):
    """
    Assign a task to an agent.
    """
    # Check if task exists
    existing_task = await task_service.get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task is available
    if existing_task.status != TaskStatus.AVAILABLE:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot assign task with status {existing_task.status}"
        )
    
    updated_task = await task_service.assign_task(task_id, assign_data)
    if not updated_task:
        raise HTTPException(status_code=500, detail="Failed to assign task")
    
    return updated_task


@router.put("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    complete_data: TaskComplete,
    task_id: str = Path(..., description="The ID of the task")
):
    """
    Mark a task as completed.
    """
    # Check if task exists
    existing_task = await task_service.get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task is assigned
    if existing_task.status != TaskStatus.ASSIGNED:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot complete task with status {existing_task.status}"
        )
    
    updated_task = await task_service.complete_task(task_id, complete_data)
    if not updated_task:
        raise HTTPException(status_code=500, detail="Failed to complete task")
    
    return updated_task


@router.get("/stats", response_model=TaskStats)
async def get_task_stats():
    """
    Get task statistics.
    """
    stats = await task_service.get_task_stats()
    return stats