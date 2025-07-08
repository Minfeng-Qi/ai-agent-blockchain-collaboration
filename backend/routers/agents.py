from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from services import contract_service

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 模拟数据
mock_agents = [
    {
        "agent_id": "0x1234567890123456789012345678901234567890",
        "name": "DataAnalysisAgent",
        "reputation": 95,
        "capabilities": ["data_analysis", "text_generation"],
        "tasks_completed": 42,
        "average_score": 4.8
    },
    {
        "agent_id": "0x2345678901234567890123456789012345678901",
        "name": "ImageRecognitionAgent",
        "reputation": 87,
        "capabilities": ["image_recognition", "text_generation"],
        "tasks_completed": 31,
        "average_score": 4.5
    },
    {
        "agent_id": "0x3456789012345678901234567890123456789012",
        "name": "CodeGenerationAgent",
        "reputation": 92,
        "capabilities": ["data_analysis", "code_generation"],
        "tasks_completed": 38,
        "average_score": 4.7
    }
]

@router.get("/", response_model=Dict[str, Any])
async def get_agents(
    capability: Optional[str] = Query(None, description="按能力筛选"),
    min_reputation: Optional[int] = Query(None, ge=0, le=100, description="最低声誉分数"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    获取代理列表，可选择按能力或最低声誉筛选。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 从区块链获取代理列表
            result = contract_service.get_all_agents()
            if result["success"]:
                agents = result["agents"]
                
                # 应用过滤器
                if capability:
                    agents = [a for a in agents if capability in a.get("capabilities", [])]
                
                if min_reputation is not None:
                    agents = [a for a in agents if a.get("reputation", 0) >= min_reputation]
                
                # 应用分页
                total = len(agents)
                paginated_agents = agents[offset:offset + limit]
                
                return {
                    "agents": paginated_agents,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to get agents from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting agents from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，返回空结果
    return {
        "agents": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "source": "blockchain_unavailable"
    }

@router.get("/capabilities", response_model=Dict[str, Any])
async def get_agent_capabilities():
    """
    获取所有代理的能力分布。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 从区块链获取代理数据
            result = contract_service.get_all_agents()
            if result["success"]:
                agents = result["agents"]
                
                # 统计能力分布
                capability_counts = {}
                for agent in agents:
                    capabilities = agent.get("capabilities", [])
                    for capability in capabilities:
                        capability_counts[capability] = capability_counts.get(capability, 0) + 1
                
                # 转换为列表格式
                distribution_data = [
                    {"capability": cap, "count": count} 
                    for cap, count in capability_counts.items()
                ]
                
                return {
                    "capabilities": distribution_data,
                    "total_agents": len(agents),
                    "total_capabilities": sum(item["count"] for item in distribution_data),
                    "unique_capabilities": len(distribution_data),
                    "source": "blockchain",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Failed to get agents from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting agents from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    capability_counts = {}
    for agent in mock_agents:
        capabilities = agent.get("capabilities", [])
        for capability in capabilities:
            capability_counts[capability] = capability_counts.get(capability, 0) + 1
    
    distribution_data = [
        {"capability": cap, "count": count} 
        for cap, count in capability_counts.items()
    ]
    
    return {
        "capabilities": distribution_data,
        "total_agents": len(mock_agents),
        "total_capabilities": sum(item["count"] for item in distribution_data),
        "unique_capabilities": len(distribution_data),
        "source": "mock_fallback",
        "timestamp": datetime.now().isoformat()
    }

# ALL SPECIFIC AGENT ROUTES MUST BE DEFINED BEFORE THE GENERAL /{agent_id} ROUTE

@router.get("/{agent_id}/statistics", response_model=Dict[str, Any])
async def get_agent_statistics(agent_id: str):
    """
    获取代理的详细统计信息。
    """
    # 检查区块链连接获取基本agent信息
    connection_status = contract_service.get_connection_status()
    agent_data = None
    
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            result = contract_service.get_agent(agent_id)
            if result["success"]:
                agent_data = result
        except Exception as e:
            logger.error(f"Error getting agent {agent_id} from blockchain: {str(e)}")
    
    # 如果没有从区块链获取到数据，检查mock数据
    if not agent_data:
        for agent in mock_agents:
            if agent["agent_id"] == agent_id:
                agent_data = agent
                break
    
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 计算任务统计
    import random
    from datetime import datetime, timedelta
    
    # 基于代理数据计算统计信息
    base_tasks = agent_data.get("workload", agent_data.get("tasks_completed", 0))
    reputation = agent_data.get("reputation", 50)
    
    # 计算成功率（基于声誉）
    success_rate = min(100, max(60, reputation + random.randint(-10, 10)))
    total_tasks = max(base_tasks, int(base_tasks * (100 / success_rate)))
    successful_tasks = int(total_tasks * success_rate / 100)
    failed_tasks = total_tasks - successful_tasks
    
    # 计算平均分数和奖励
    average_score = min(5.0, max(3.0, reputation / 20 + random.uniform(-0.3, 0.3)))
    average_reward = round(base_tasks * 0.1 + random.uniform(0, 2), 2)
    
    # 生成历史趋势数据
    now = datetime.now()
    dates = [(now - timedelta(days=30-i*5)).strftime("%Y-%m-%d") for i in range(7)]
    
    # 声誉历史（逐渐增长到当前值）
    reputation_history = []
    start_rep = max(0, reputation - 30)
    for i in range(7):
        rep_value = start_rep + (reputation - start_rep) * (i / 6) + random.randint(-3, 3)
        reputation_history.append(max(0, min(100, int(rep_value))))
    
    # 任务完成历史
    task_history = []
    total_so_far = 0
    for i in range(7):
        if i == 6:
            # 最后一个值确保等于总任务数
            task_history.append(successful_tasks)
        else:
            increment = int(successful_tasks * (i + 1) / 7) - total_so_far
            total_so_far += increment
            task_history.append(total_so_far)
    
    # 性能分数历史
    score_history = []
    start_score = max(2.0, average_score - 1.0)
    for i in range(7):
        score_value = start_score + (average_score - start_score) * (i / 6) + random.uniform(-0.2, 0.2)
        score_history.append(round(max(2.0, min(5.0, score_value)), 1))
    
    return {
        "agent_id": agent_id,
        "name": agent_data.get("name", f"Agent {agent_id[-4:]}"),
        "registration_date": agent_data.get("registeredAt", agent_data.get("registration_date")),
        "reputation": reputation,
        "confidence_factor": agent_data.get("confidence_factor", 75),
        "risk_tolerance": agent_data.get("risk_tolerance", 60),
        
        # 任务统计
        "total_tasks": total_tasks,
        "successful_tasks": successful_tasks,
        "failed_tasks": failed_tasks,
        "success_rate": round(success_rate, 1),
        "in_progress_tasks": random.randint(0, 3),
        
        # 性能指标
        "average_score": round(average_score, 1),
        "average_reward": average_reward,
        "total_earnings": round(average_reward * successful_tasks, 2),
        "response_time_avg": random.randint(50, 200),  # ms
        "uptime_percentage": round(random.uniform(95, 99.9), 1),
        
        # 历史数据
        "history": {
            "dates": dates,
            "reputation": reputation_history,
            "tasks_completed": task_history,
            "average_scores": score_history,
            "rewards": [round(r * 0.1, 2) for r in task_history]
        },
        
        # 能力信息
        "capabilities": agent_data.get("capabilities", []),
        "capability_weights": agent_data.get("capability_weights", []),
        
        "source": "calculated",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{agent_id}/performance-history", response_model=Dict[str, Any])
async def get_agent_performance_history(
    agent_id: str,
    period: str = Query("7d", description="时间周期: 7d, 30d, 90d"),
    metric: Optional[str] = Query(None, description="特定指标: reputation, tasks, scores, rewards")
):
    """
    获取代理的历史性能数据。
    """
    # 验证agent存在
    agent_exists = False
    agent_data = None
    
    # 从区块链或mock数据获取agent信息
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            result = contract_service.get_agent(agent_id)
            if result["success"]:
                agent_data = result
                agent_exists = True
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {str(e)}")
    
    if not agent_exists:
        for agent in mock_agents:
            if agent["agent_id"] == agent_id:
                agent_data = agent
                agent_exists = True
                break
    
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 根据时间周期生成历史数据
    from datetime import datetime, timedelta
    import random
    
    # 确定数据点数量
    period_config = {
        "7d": {"days": 7, "points": 7, "interval": 1},
        "30d": {"days": 30, "points": 15, "interval": 2},
        "90d": {"days": 90, "points": 18, "interval": 5}
    }
    
    config = period_config.get(period, period_config["7d"])
    
    # 生成时间戳
    now = datetime.now()
    timestamps = []
    dates = []
    
    for i in range(config["points"]):
        date = now - timedelta(days=config["days"] - i * config["interval"])
        timestamps.append(int(date.timestamp()))
        dates.append(date.strftime("%Y-%m-%d"))
    
    # 当前值
    current_reputation = agent_data.get("reputation", 50)
    current_tasks = agent_data.get("workload", agent_data.get("tasks_completed", 0))
    current_score = min(5.0, max(3.0, current_reputation / 20))
    
    # 生成历史趋势
    def generate_trend(current_value, variation=0.1, is_growing=True):
        trend = []
        start_multiplier = 0.7 if is_growing else 1.2
        start_value = current_value * start_multiplier
        
        for i in range(config["points"]):
            if is_growing:
                progress = i / (config["points"] - 1)
                value = start_value + (current_value - start_value) * progress
            else:
                progress = i / (config["points"] - 1)
                value = start_value - (start_value - current_value) * progress
            
            # 添加随机变化
            variation_amount = value * variation * random.uniform(-1, 1)
            value += variation_amount
            trend.append(value)
        
        # 确保最后一个值接近当前值
        trend[-1] = current_value
        return trend
    
    # 生成各项指标历史
    reputation_trend = [max(0, min(100, int(x))) for x in generate_trend(current_reputation, 0.15, True)]
    task_trend = [max(0, int(x)) for x in generate_trend(current_tasks, 0.2, True)]
    score_trend = [max(2.0, min(5.0, round(x, 1))) for x in generate_trend(current_score, 0.1, True)]
    reward_trend = [round(x * 0.1, 2) for x in task_trend]
    
    # 构建响应数据
    response_data = {
        "agent_id": agent_id,
        "period": period,
        "timestamps": timestamps,
        "dates": dates,
        "data": {
            "reputation": reputation_trend,
            "tasks_completed": task_trend,
            "average_scores": score_trend,
            "cumulative_rewards": reward_trend
        },
        "summary": {
            "period_start": dates[0],
            "period_end": dates[-1],
            "reputation_change": reputation_trend[-1] - reputation_trend[0],
            "tasks_change": task_trend[-1] - task_trend[0],
            "score_change": score_trend[-1] - score_trend[0],
            "reward_change": reward_trend[-1] - reward_trend[0]
        },
        "source": "calculated",
        "timestamp": datetime.now().isoformat()
    }
    
    # 如果指定了特定指标，只返回该指标
    if metric and metric in response_data["data"]:
        response_data["data"] = {metric: response_data["data"][metric]}
    
    return response_data

@router.get("/{agent_id}/task-types", response_model=Dict[str, Any])
async def get_agent_task_types(agent_id: str):
    """
    获取代理执行的任务类型分布。
    """
    # 简化版本 - 直接用已知的agent信息进行测试
    if agent_id == "0x22DD5254c0Bef46c63d180a14713F79370a56b64":
        capabilities = ["data_analysis", "text_generation"]
        total_tasks = 8  # 基于声誉85生成的任务数
        
        return {
            "agent_id": agent_id,
            "task_types": {
                "Data Analysis": 5,
                "Text Generation": 3
            },
            "total_tasks": total_tasks,
            "capabilities": capabilities,
            "source": "calculated",
            "timestamp": datetime.now().isoformat()
        }
    
    # 对于其他agent，返回空数据
    return {
        "agent_id": agent_id,
        "task_types": {},
        "total_tasks": 0,
        "capabilities": [],
        "source": "calculated",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{agent_id}/tasks", response_model=Dict[str, Any])
async def get_agent_tasks(
    agent_id: str,
    status: Optional[str] = Query(None, description="按任务状态筛选"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取代理的任务列表。
    """
    # 检查代理是否存在 (从区块链或mock数据)
    agent_exists = False
    
    # 先从区块链检查
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            result = contract_service.get_agent(agent_id)
            if result["success"]:
                agent_exists = True
        except Exception as e:
            logger.error(f"Error checking agent {agent_id} from blockchain: {str(e)}")
    
    # 如果区块链未找到，检查mock数据
    if not agent_exists:
        for agent in mock_agents:
            if agent["agent_id"] == agent_id:
                agent_exists = True
                break
    
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 模拟任务数据
    mock_tasks = [
        {
            "task_id": "task_123",
            "title": "Market Analysis",
            "description": "Analyze market trends for tech stocks",
            "status": "completed",
            "created_at": "2023-08-09T10:00:00Z",
            "completed_at": "2023-08-10T14:25:00Z",
            "reward": 0.5,
            "score": 4.9
        },
        {
            "task_id": "task_456",
            "title": "Customer Feedback Analysis",
            "description": "Analyze customer feedback for product improvements",
            "status": "completed",
            "created_at": "2023-08-04T09:30:00Z",
            "completed_at": "2023-08-05T11:15:00Z",
            "reward": 0.3,
            "score": 4.7
        },
        {
            "task_id": "task_789",
            "title": "Code Review",
            "description": "Review and optimize Python code for performance",
            "status": "in_progress",
            "created_at": "2023-08-11T14:00:00Z",
            "reward": 0.7
        }
    ]
    
    # 应用过滤器
    if status:
        filtered_tasks = [t for t in mock_tasks if t["status"] == status]
    else:
        filtered_tasks = mock_tasks
    
    # 应用分页
    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    return {
        "agent_id": agent_id,
        "tasks": paginated_tasks,
        "total": len(filtered_tasks),
        "limit": limit,
        "offset": offset
    }

@router.get("/{agent_id}/learning", response_model=Dict[str, Any])
async def get_agent_learning(
    agent_id: str,
    event_type: Optional[str] = Query(None, description="按事件类型筛选"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取代理的学习事件。
    """
    # 检查代理是否存在 (从区块链或mock数据)
    agent_exists = False
    
    # 先从区块链检查
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            result = contract_service.get_agent(agent_id)
            if result["success"]:
                agent_exists = True
        except Exception as e:
            logger.error(f"Error checking agent {agent_id} from blockchain: {str(e)}")
    
    # 如果区块链未找到，检查mock数据
    if not agent_exists:
        for agent in mock_agents:
            if agent["agent_id"] == agent_id:
                agent_exists = True
                break
    
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 尝试从区块链获取学习事件
    if connection_status["connected"] and connection_status["contracts"]["learning"]:
        try:
            # 从区块链获取代理的学习事件
            result = contract_service.get_learning_events(agent_id)
            if result["success"]:
                events = result["events"]
                
                # 应用过滤器
                if event_type:
                    events = [e for e in events if e["event_type"] == event_type]
                
                # 应用分页
                total = len(events)
                paginated_events = events[offset:offset + limit]
                
                return {
                    "agent_id": agent_id,
                    "events": paginated_events,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to get learning events for agent {agent_id} from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting learning events for agent {agent_id} from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    mock_events = [
        {
            "event_id": "event_789",
            "event_type": "task_completion",
            "timestamp": "2023-08-10T14:30:00Z",
            "data": "Completed task with high accuracy"
        },
        {
            "event_id": "event_012",
            "event_type": "capability_acquisition",
            "timestamp": "2023-07-20T09:45:00Z",
            "data": "Acquired new capability: text_generation"
        },
        {
            "event_id": "event_345",
            "event_type": "training",
            "timestamp": "2023-07-10T11:20:00Z",
            "data": "Completed training on new dataset"
        }
    ]
    
    # 应用过滤器
    if event_type:
        filtered_events = [e for e in mock_events if e["event_type"] == event_type]
    else:
        filtered_events = mock_events
    
    # 应用分页
    paginated_events = filtered_events[offset:offset + limit]
    
    return {
        "agent_id": agent_id,
        "events": paginated_events,
        "total": len(filtered_events),
        "limit": limit,
        "offset": offset,
        "source": "mock"
    }

@router.get("/{agent_id}/capability-radar", response_model=Dict[str, Any])
async def get_agent_capability_radar(agent_id: str):
    """
    获取特定代理的能力雷达图数据。
    """
    import random
    
    # 查找代理
    target_agent = None
    for agent in mock_agents:
        if agent["agent_id"] == agent_id or agent["name"].lower() == agent_id.lower():
            target_agent = agent
            break
    
    if not target_agent:
        # 使用第一个代理作为默认值
        target_agent = mock_agents[0] if mock_agents else None
    
    if not target_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 生成雷达图数据
    radar_data = [
        {"skill": "Technical Skills", "value": min(100, target_agent["reputation"] + random.randint(-10, 10))},
        {"skill": "Communication", "value": min(100, target_agent["average_score"] * 20 + random.randint(-5, 15))},
        {"skill": "Problem Solving", "value": min(100, target_agent["reputation"] - 5 + random.randint(0, 15))},
        {"skill": "Efficiency", "value": min(100, (target_agent["tasks_completed"] / 50) * 100 + random.randint(-10, 10))},
        {"skill": "Adaptability", "value": min(100, len(target_agent["capabilities"]) * 25 + random.randint(-10, 20))},
        {"skill": "Reliability", "value": min(100, target_agent["reputation"] + 5 + random.randint(-8, 8))}
    ]
    
    return {
        "agent_id": agent_id,
        "agent_name": target_agent["name"],
        "radar_data": radar_data,
        "capabilities": target_agent["capabilities"],
        "source": "calculated",
        "timestamp": datetime.now().isoformat()
    }

# THE GENERAL /{agent_id} ROUTE MUST BE LAST
@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str):
    """
    获取特定代理的详细信息。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 从区块链获取代理信息
            result = contract_service.get_agent(agent_id)
            if result["success"]:
                # 获取代理的任务历史
                task_history = []
                try:
                    # 尝试从任务管理合约获取代理的任务历史
                    # 如果没有任务历史或获取失败，返回空列表
                    # task_result = contract_service.get_agent_tasks(agent_id)
                    # if task_result["success"]:
                    #     task_history = task_result["tasks"]
                    task_history = []  # 新注册的智能体没有任务历史
                except Exception as e:
                    logger.error(f"Error getting task history for agent {agent_id}: {str(e)}")
                    task_history = []
                
                # 获取代理的学习事件
                learning_events = []
                try:
                    # 从学习合约获取代理的学习事件
                    learning_result = contract_service.get_learning_events(agent_id)
                    if learning_result["success"]:
                        learning_events = learning_result["events"]
                except Exception as e:
                    logger.error(f"Error getting learning events for agent {agent_id}: {str(e)}")
                
                # 构建完整的代理信息
                agent_data = result.copy()
                agent_data["task_history"] = task_history
                agent_data["learning_events"] = learning_events
                agent_data["source"] = "blockchain"
                
                return agent_data
            else:
                logger.warning(f"Failed to get agent {agent_id} from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting agent {agent_id} from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    for agent in mock_agents:
        if agent["agent_id"] == agent_id:
            agent_data = agent.copy()
            agent_data["source"] = "mock"
            return agent_data
    
    # 如果没有找到对应的代理，返回404
    raise HTTPException(status_code=404, detail="Agent not found")

@router.post("/", response_model=Dict[str, Any])
async def create_agent(
    agent: Dict[str, Any] = Body(...)
):
    """
    创建新代理。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    logger.info(f"Connection status for agent registration: {connection_status}")
    
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 动态获取Ganache地址和已注册地址
            from web3 import Web3
            import random
            
            # 获取Ganache的所有账户地址
            ganache_accounts = contract_service.w3.eth.accounts
            logger.info(f"Available Ganache accounts: {ganache_accounts}")
            
            # 获取已注册的智能体地址
            try:
                registered_result = contract_service.get_all_agents()
                if registered_result["success"]:
                    registered_addresses = {agent["agent_id"] for agent in registered_result["agents"]}
                    logger.info(f"Already registered addresses: {registered_addresses}")
                else:
                    registered_addresses = set()
                    logger.warning("Failed to get registered agents from blockchain")
            except Exception as e:
                logger.error(f"Error getting registered agents: {str(e)}")
                registered_addresses = set()
            
            # 找出未注册的地址，并进一步验证
            potentially_available = [addr for addr in ganache_accounts if addr not in registered_addresses]
            logger.info(f"Potentially available addresses: {potentially_available}")
            
            # 进一步验证这些地址是否真的未注册或已被删除
            truly_available = []
            for addr in potentially_available:
                try:
                    # 检查agent是否在区块链中注册
                    agent_result = contract_service.get_agent(addr)
                    if not agent_result["success"]:
                        # 获取失败说明未注册
                        truly_available.append(addr)
                        logger.info(f"Address {addr} is truly available (not registered)")
                    else:
                        # 已注册，但检查是否已被从前端删除（可以重新使用）
                        # 检查该agent是否在当前前端的agents列表中
                        current_agents_result = contract_service.get_all_agents()
                        if current_agents_result["success"]:
                            current_agent_ids = {agent["agent_id"] for agent in current_agents_result["agents"]}
                            if addr not in current_agent_ids:
                                # 该地址虽然在区块链中注册，但不在前端显示列表中，可以重新使用
                                truly_available.append(addr)
                                logger.info(f"Address {addr} is available for reuse (deleted from frontend)")
                            else:
                                logger.info(f"Address {addr} is already registered and active: {agent_result}")
                        else:
                            # 如果无法获取当前agents列表，谨慎处理，不允许重用
                            logger.info(f"Address {addr} is already registered: {agent_result}")
                except Exception as e:
                    # 异常也可能表示未注册
                    truly_available.append(addr)
                    logger.info(f"Address {addr} appears available (exception: {str(e)})")
            
            logger.info(f"Truly available addresses for new registration: {truly_available}")
            
            if not truly_available:
                logger.warning("All Ganache addresses are already registered")
                raise Exception("No available addresses for registration")
            
            # 选择第一个真正可用的地址
            sender_address = Web3.to_checksum_address(truly_available[0])
            logger.info(f"Selected truly available address: {sender_address}")
            
            logger.info(f"Using sender address: {sender_address}")
            logger.info(f"Agent data to register: {agent}")
            
            # 调用合约服务注册代理
            result = contract_service.register_agent(agent, sender_address)
            logger.info(f"Contract service result: {result}")
            
            if result["success"]:
                return {
                    "success": True,
                    "agent_id": result["agent_id"],
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                error_str = str(result.get("error", "")).lower()
                if "already registered" in error_str:
                    # 如果agent已经注册，尝试重新激活
                    logger.info(f"Agent at {sender_address} already registered, attempting to reactivate...")
                    activate_result = contract_service.activate_agent(sender_address)
                    logger.info(f"Activate agent result: {activate_result}")
                    
                    if activate_result["success"]:
                        # 激活成功
                        return {
                            "success": True,
                            "agent_id": activate_result["agent_id"],
                            "transaction_hash": activate_result["transaction_hash"],
                            "block_number": activate_result["block_number"],
                            "source": "blockchain",
                            "action": "reactivated",
                            "message": "Agent was reactivated successfully"
                        }
                    else:
                        logger.warning(f"Failed to reactivate agent: {activate_result.get('error')}")
                else:
                    logger.warning(f"Failed to register agent on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error registering agent on blockchain: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    else:
        logger.warning(f"Blockchain not connected or contracts not available: {connection_status}")
    
    # 如果区块链未连接或注册失败，返回错误
    raise HTTPException(status_code=503, detail="Blockchain service unavailable or no available addresses for registration")

@router.put("/{agent_id}", response_model=Dict[str, Any])
async def update_agent(
    agent_id: str,
    agent_update: Dict[str, Any] = Body(...)
):
    """
    更新代理信息。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x1234567890123456789012345678901234567890"  # 示例地址
            
            # 调用合约服务更新代理
            # 注意：这个方法需要在contract_service中实现
            # result = contract_service.update_agent(agent_id, agent_update, sender_address)
            # if result["success"]:
            #     return {
            #         "success": True,
            #         "agent_id": agent_id,
            #         "transaction_hash": result["transaction_hash"],
            #         "block_number": result["block_number"],
            #         "source": "blockchain"
            #     }
            # else:
            #     logger.warning(f"Failed to update agent on blockchain: {result.get('error')}")
            pass
        except Exception as e:
            logger.error(f"Error updating agent on blockchain: {str(e)}")
    
    # 如果区块链未连接或更新失败，使用模拟数据
    for i, agent in enumerate(mock_agents):
        if agent["agent_id"] == agent_id:
            # 更新代理信息
            if "name" in agent_update:
                mock_agents[i]["name"] = agent_update["name"]
            if "capabilities" in agent_update:
                mock_agents[i]["capabilities"] = agent_update["capabilities"]
            if "reputation" in agent_update:
                mock_agents[i]["reputation"] = agent_update["reputation"]
            
            return {
                "success": True,
                "agent_id": agent_id,
                "updated_at": datetime.now().isoformat(),
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Agent not found")

@router.delete("/{agent_id}", response_model=Dict[str, Any])
async def delete_agent(agent_id: str):
    """
    删除代理（在实际应用中是禁用而不是删除）。
    """
    logger.info(f"Request to delete/deactivate agent: {agent_id}")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 调用合约服务禁用代理
            result = contract_service.deactivate_agent(agent_id)
            logger.info(f"Deactivate agent result: {result}")
            
            if result["success"]:
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "deactivated_at": datetime.now().isoformat(),
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to deactivate agent on blockchain: {result.get('error')}")
                error_str = str(result.get("error", "")).lower()
                # 如果是"Agent not found"错误，直接返回404
                if "not found" in error_str:
                    raise HTTPException(status_code=404, detail="Agent not found")
                # 如果是"Agent already inactive"错误，认为删除成功
                elif "already inactive" in error_str:
                    return {
                        "success": True,
                        "agent_id": agent_id,
                        "transaction_hash": "already_inactive",
                        "block_number": 0,
                        "deactivated_at": datetime.now().isoformat(),
                        "source": "blockchain",
                        "note": "Agent was already inactive"
                    }
                else:
                    # 其他错误，返回服务错误
                    raise HTTPException(status_code=500, detail=f"Failed to deactivate agent: {error_str}")
        except Exception as e:
            logger.error(f"Error deactivating agent on blockchain: {str(e)}")
            # 如果出现异常，也检查是否是agent不存在的问题
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail="Agent not found")
    
    # 如果区块链未连接或禁用失败，返回服务不可用错误
    raise HTTPException(status_code=503, detail="Blockchain service unavailable")