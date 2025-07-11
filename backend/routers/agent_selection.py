"""
智能代理选择路由
提供自动分配代理的API接口
"""
from fastapi import APIRouter, HTTPException, Query, Body, Path
from typing import Dict, Any, List, Optional
import logging

from services.agent_selection_service import agent_selection_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{task_id}/auto-assign", response_model=Dict[str, Any])
async def auto_assign_agent(
    task_id: str = Path(..., description="任务ID"),
):
    """
    自动为任务选择并分配最佳代理
    """
    try:
        result = await agent_selection_service.auto_assign_task(task_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to auto-assign task: {result.get('error')}"
            )
    except Exception as e:
        logger.exception(f"Error in auto_assign_agent: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{task_id}/auto-assign-collaborative", response_model=Dict[str, Any])
async def auto_assign_collaborative(
    task_id: str = Path(..., description="任务ID"),
    max_agents: int = Query(3, ge=1, le=10, description="最多选择的代理数量")
):
    """
    自动为任务选择并分配多个协作代理
    """
    try:
        result = await agent_selection_service.auto_assign_collaborative_task(task_id, max_agents)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to auto-assign collaborative task: {result.get('error')}"
            )
    except Exception as e:
        logger.exception(f"Error in auto_assign_collaborative: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{task_id}/recommend", response_model=Dict[str, Any])
async def recommend_agents(
    task_id: str = Path(..., description="任务ID"),
    max_agents: int = Query(5, ge=1, le=20, description="推荐的最大代理数量")
):
    """
    为任务推荐合适的代理（不进行分配，仅推荐）
    """
    try:
        # 获取任务信息
        task_result = agent_selection_service.contract_service.get_task(task_id)
        if not task_result.get("success"):
            raise HTTPException(
                status_code=404, 
                detail=f"Task not found: {task_result.get('error')}"
            )
        
        task = task_result.get("task")
        
        # 获取所有代理
        agents_result = agent_selection_service.contract_service.get_all_agents()
        if not agents_result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to get agents: {agents_result.get('error')}"
            )
        
        agents = agents_result.get("agents", [])
        
        # 选择协作代理
        selected_agents = await agent_selection_service.select_collaborative_agents(task, agents, max_agents)
        
        # 移除评分字段，添加匹配度
        for agent in selected_agents:
            match_score = agent.pop("score", 0) * 100  # 转换为百分比
            agent["match_score"] = round(match_score, 2)
        
        return {
            "task_id": task_id,
            "recommended_agents": selected_agents,
            "total_recommendations": len(selected_agents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in recommend_agents: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{task_id}/assign-multiple", response_model=Dict[str, Any])
async def assign_multiple_agents(
    task_id: str = Path(..., description="任务ID"),
    agent_ids: List[str] = Body(..., description="要分配的代理ID列表")
):
    """
    将任务分配给多个指定的代理
    """
    try:
        if not agent_ids:
            raise HTTPException(
                status_code=400, 
                detail="No agent IDs provided"
            )
            
        result = await agent_selection_service.assign_collaborative_task(task_id, agent_ids)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to assign task to multiple agents: {result.get('error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in assign_multiple_agents: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/capability-coverage", response_model=Dict[str, Any])
async def get_capability_coverage():
    """
    获取当前系统中各种能力的覆盖情况
    """
    try:
        # 获取所有代理
        agents_result = agent_selection_service.contract_service.get_all_agents()
        if not agents_result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to get agents: {agents_result.get('error')}"
            )
        
        agents = agents_result.get("agents", [])
        
        # 统计各种能力的覆盖情况
        capability_counts = {}
        capability_agents = {}
        total_agents = len(agents)
        
        for agent in agents:
            if not agent.get("active", True):
                continue
                
            capabilities = agent.get("capabilities", [])
            for cap in capabilities:
                if cap not in capability_counts:
                    capability_counts[cap] = 0
                    capability_agents[cap] = []
                    
                capability_counts[cap] += 1
                capability_agents[cap].append(agent.get("agent_id"))
        
        # 转换为列表格式
        coverage_data = []
        for cap, count in capability_counts.items():
            coverage_data.append({
                "capability": cap,
                "agent_count": count,
                "coverage_percentage": round((count / total_agents) * 100, 2) if total_agents > 0 else 0,
                "agent_ids": capability_agents[cap]
            })
        
        # 按覆盖率排序
        coverage_data.sort(key=lambda x: x["coverage_percentage"], reverse=True)
        
        return {
            "total_agents": total_agents,
            "capabilities": coverage_data,
            "unique_capabilities": len(coverage_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in get_capability_coverage: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        ) 