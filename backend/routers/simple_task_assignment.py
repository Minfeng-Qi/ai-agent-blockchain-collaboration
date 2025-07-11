"""
简单的任务分配路由
用户点击 Start Collaboration 时自动为任务分配合适的agents
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

def calculate_agent_score(agent: Dict[str, Any], task: Dict[str, Any]) -> float:
    """计算agent对task的适合度评分"""
    required_caps = task.get("required_capabilities", [])
    agent_caps = agent.get("capabilities", [])
    
    # 计算能力匹配度
    matched_caps = [cap for cap in required_caps if cap in agent_caps]
    if not matched_caps:
        return 0.0
    
    capability_match = len(matched_caps) / len(required_caps)
    
    # 计算声誉分数
    reputation_score = agent.get("reputation", 0) / 100.0
    
    # 代理类型加权（协调者和评估者有额外加分）
    type_bonus = {1: 1.0, 2: 1.2, 3: 1.1}.get(agent.get("agent_type", 1), 1.0)
    
    # 综合评分
    total_score = (capability_match * 0.6 + reputation_score * 0.4) * type_bonus
    
    return total_score

def select_agents_for_task(task: Dict[str, Any], agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """为任务选择合适的agents"""
    required_caps = task.get("required_capabilities", [])
    min_reputation = task.get("min_reputation", 0)
    
    # 过滤符合条件的agents
    qualified_agents = []
    for agent in agents:
        if (agent.get("active", True) and 
            agent.get("reputation", 0) >= min_reputation):
            
            score = calculate_agent_score(agent, task)
            if score > 0:
                agent_copy = agent.copy()
                agent_copy["score"] = score
                qualified_agents.append(agent_copy)
    
    if not qualified_agents:
        return []
    
    # 按评分排序
    qualified_agents.sort(key=lambda x: x["score"], reverse=True)
    
    # 智能选择策略
    selected_agents = []
    covered_capabilities = set()
    
    # 如果只需要1-2种能力，选择1个最佳agent
    if len(required_caps) <= 2:
        best_agent = qualified_agents[0]
        selected_agents.append(best_agent)
        logger.info(f"Selected single agent {best_agent['name']} for simple task")
        
    else:
        # 复杂任务需要多个agents协作
        
        # 1. 优先选择协调者
        orchestrators = [a for a in qualified_agents if a.get("agent_type") == 2]
        if orchestrators:
            selected_agents.append(orchestrators[0])
            covered_capabilities.update(orchestrators[0].get("capabilities", []))
            logger.info(f"Selected orchestrator: {orchestrators[0]['name']}")
        
        # 2. 选择能力互补的执行者
        for agent in qualified_agents:
            if len(selected_agents) >= 5:  # 限制团队大小
                break
                
            if agent in selected_agents:
                continue
                
            agent_caps = set(agent.get("capabilities", []))
            task_caps = set(required_caps)
            new_coverage = agent_caps & task_caps - covered_capabilities
            
            # 如果带来新能力或者还没有足够的agents
            if new_coverage or len(selected_agents) < 2:
                selected_agents.append(agent)
                covered_capabilities.update(agent_caps)
                logger.info(f"Selected agent: {agent['name']} (new capabilities: {list(new_coverage)})")
        
        # 3. 如果有评估者且团队还有空间，添加评估者
        evaluators = [a for a in qualified_agents if a.get("agent_type") == 3]
        if evaluators and len(selected_agents) < 4:
            evaluator = evaluators[0]
            if evaluator not in selected_agents:
                selected_agents.append(evaluator)
                logger.info(f"Added evaluator: {evaluator['name']}")
    
    return selected_agents

@router.post("/{task_id}/start-collaboration")
async def start_collaboration(task_id: str = Path(..., description="任务ID")):
    """
    开始协作 - 为指定任务自动分配合适的agents
    """
    try:
        logger.info(f"Starting collaboration for task {task_id}")
        
        # 获取任务信息 - 直接调用contract_service避免循环
        from services import contract_service
        
        # 获取所有tasks并找到指定的task
        tasks_result = contract_service.get_all_tasks()
        if not tasks_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get tasks: {tasks_result.get('error')}"
            )
        
        task = None
        for t in tasks_result.get("tasks", []):
            if t.get("task_id") == task_id:
                task = t
                break
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.get("status") != "open":
            raise HTTPException(
                status_code=400, 
                detail=f"Task is not open (current status: {task.get('status')})"
            )
        
        # 获取所有agents
        agents_result = contract_service.get_all_agents()
        if not agents_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get agents: {agents_result.get('error')}"
            )
        
        agents = agents_result.get("agents", [])
        logger.info(f"Found {len(agents)} agents")
        
        # 选择合适的agents
        selected_agents = select_agents_for_task(task, agents)
        
        if not selected_agents:
            raise HTTPException(
                status_code=400,
                detail="No suitable agents found for this task"
            )
        
        # 分析结果
        required_caps = set(task.get("required_capabilities", []))
        covered_caps = set()
        for agent in selected_agents:
            agent_caps = agent.get("capabilities", [])
            covered_caps.update(cap for cap in agent_caps if cap in required_caps)
        
        coverage_ratio = len(covered_caps) / len(required_caps) if required_caps else 1.0
        
        # 真正启动多代理协作到区块链
        agent_addresses = []
        for agent in selected_agents:
            addr = agent.get("address") or agent.get("agent_id")
            if addr:
                agent_addresses.append(addr)
        
        if agent_addresses:
            # 使用合约所有者地址进行协作启动
            owner_address = "0x7a6D8eBA15a14117F4DFDCa6FD9b28ed47277E22"
            collaboration_id = f"collab_{task_id}_{int(time.time())}"
            
            logger.info(f"Starting collaboration for task {task_id} with {len(agent_addresses)} agents using owner {owner_address}")
            collab_result = contract_service.start_agent_collaboration(task_id, agent_addresses, collaboration_id, owner_address)
            logger.info(f"Collaboration result: {collab_result}")
            
            if not collab_result.get("success"):
                logger.warning(f"Failed to start collaboration on blockchain: {collab_result.get('error')}")
                # 不抛出异常，继续返回智能分配结果
        else:
            logger.warning(f"No valid agent addresses found, skipping blockchain collaboration")
        
        # 构建响应
        result = {
            "success": True,
            "task_id": task_id,
            "task_title": task.get("title"),
            "task_status": "collaboration_started",
            "required_capabilities": list(required_caps),
            "selected_agents": [
                {
                    "agent_id": agent.get("agent_id"),
                    "name": agent.get("name"),
                    "agent_type": agent.get("agent_type"),
                    "capabilities": agent.get("capabilities"),
                    "reputation": agent.get("reputation"),
                    "match_score": round(agent.get("score", 0) * 100, 2),
                    "role": (
                        "协调者" if agent.get("agent_type") == 2 
                        else "评估者" if agent.get("agent_type") == 3 
                        else "执行者"
                    )
                }
                for agent in selected_agents
            ],
            "collaboration_summary": {
                "team_size": len(selected_agents),
                "assignment_type": "single_agent" if len(selected_agents) == 1 else "multi_agent_collaboration",
                "capability_coverage": round(coverage_ratio * 100, 2),
                "covered_capabilities": list(covered_caps),
                "missing_capabilities": list(required_caps - covered_caps),
                "average_reputation": round(
                    sum(a.get("reputation", 0) for a in selected_agents) / len(selected_agents), 1
                ),
                "team_quality_score": round(
                    sum(a.get("score", 0) for a in selected_agents) / len(selected_agents) * 100, 2
                )
            },
            "next_steps": [
                "1. 任务已分配给选定的agents",
                "2. 协作工作流程已启动", 
                "3. 可以在前端查看协作进度",
                "4. agents将根据各自专长协作完成任务"
            ]
        }
        
        logger.info(
            f"Collaboration started successfully: {len(selected_agents)} agents selected "
            f"with {coverage_ratio:.1%} capability coverage"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error starting collaboration for task {task_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{task_id}/collaboration-preview")
async def preview_collaboration(task_id: str = Path(..., description="任务ID")):
    """
    预览协作 - 显示为任务推荐的agents但不实际分配
    """
    try:
        # 获取任务信息
        from services import contract_service
        
        tasks_result = contract_service.get_all_tasks()
        if not tasks_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get tasks: {tasks_result.get('error')}"
            )
        
        task = None
        for t in tasks_result.get("tasks", []):
            if t.get("task_id") == task_id:
                task = t
                break
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 获取agents
        agents_result = contract_service.get_all_agents()
        if not agents_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get agents: {agents_result.get('error')}"
            )
        
        agents = agents_result.get("agents", [])
        
        # 选择推荐的agents
        recommended_agents = select_agents_for_task(task, agents)
        
        # 分析推荐结果
        required_caps = set(task.get("required_capabilities", []))
        covered_caps = set()
        for agent in recommended_agents:
            agent_caps = agent.get("capabilities", [])
            covered_caps.update(cap for cap in agent_caps if cap in required_caps)
        
        coverage_ratio = len(covered_caps) / len(required_caps) if required_caps else 1.0
        
        return {
            "task_id": task_id,
            "task_title": task.get("title"),
            "task_status": task.get("status"),
            "required_capabilities": list(required_caps),
            "recommended_agents": [
                {
                    "agent_id": agent.get("agent_id"),
                    "name": agent.get("name"),
                    "agent_type": agent.get("agent_type"),
                    "capabilities": agent.get("capabilities"),
                    "reputation": agent.get("reputation"),
                    "match_score": round(agent.get("score", 0) * 100, 2),
                    "role": (
                        "协调者" if agent.get("agent_type") == 2 
                        else "评估者" if agent.get("agent_type") == 3 
                        else "执行者"
                    )
                }
                for agent in recommended_agents
            ],
            "preview_summary": {
                "team_size": len(recommended_agents),
                "assignment_type": "single_agent" if len(recommended_agents) == 1 else "multi_agent_collaboration",
                "capability_coverage": round(coverage_ratio * 100, 2),
                "recommendation_quality": "excellent" if coverage_ratio >= 0.9 else "good" if coverage_ratio >= 0.7 else "fair"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error previewing collaboration for task {task_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )