from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from backend.services import contract_service

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
    
    # 如果区块链未连接或获取失败，使用模拟数据
    filtered_agents = mock_agents
    
    if capability:
        filtered_agents = [a for a in filtered_agents if capability in a["capabilities"]]
    
    if min_reputation is not None:
        filtered_agents = [a for a in filtered_agents if a["reputation"] >= min_reputation]
    
    # 应用分页
    paginated_agents = filtered_agents[offset:offset + limit]
    
    return {
        "agents": paginated_agents,
        "total": len(filtered_agents),
        "limit": limit,
        "offset": offset,
        "source": "mock"
    }

@router.get("/performance", response_model=Dict[str, Any])
async def get_agent_performance():
    """
    获取代理性能数据，用于前端Dashboard展示。
    """
    # 首先尝试从合约获取数据
    contract_result = contract_service.get_contract_agent_performance()
    
    if contract_result["success"] and contract_result["data"]:
        return {
            "data": contract_result["data"],
            "total_agents": contract_result["total_agents"],
            "source": "contract",
            "timestamp": datetime.now().isoformat()
        }
    
    # 如果合约数据获取失败，使用模拟数据
    logger.warning("Failed to get contract agent performance data, using mock data")
    
    import random
    
    # 生成性能数据
    performance_data = []
    for agent in mock_agents:
        # 计算成功率
        success_rate = min(100, agent["reputation"] + random.randint(-5, 5))
        
        performance_data.append({
            "id": agent["agent_id"],
            "name": agent["name"],
            "reputation": agent["reputation"],
            "tasksCompleted": agent["tasks_completed"],
            "successRate": success_rate,
            "averageScore": agent["average_score"],
            "capabilities": agent["capabilities"],
            "earnings": round(agent["tasks_completed"] * 0.1 + random.uniform(0, 2), 2),
            "responseTime": random.randint(50, 300),  # ms
            "uptime": random.uniform(95, 99.9)  # percentage
        })
    
    return {
        "data": performance_data,
        "total_agents": len(performance_data),
        "source": "mock_fallback",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/capabilities-distribution", response_model=Dict[str, Any])
async def get_agent_capabilities_distribution():
    """
    获取代理能力分布数据，用于前端图表展示。
    """
    # 首先尝试从合约获取数据
    contract_result = contract_service.get_contract_agent_capabilities_distribution()
    
    if contract_result["success"] and contract_result["data"]:
        return {
            "data": contract_result["data"],
            "total_capabilities": contract_result["total_capabilities"],
            "unique_capabilities": contract_result["unique_capabilities"],
            "source": "contract",
            "timestamp": datetime.now().isoformat()
        }
    
    # 如果合约数据获取失败，使用模拟数据
    logger.warning("Failed to get contract agent capabilities data, using mock data")
    
    # 统计各种能力的分布
    capabilities_count = {}
    for agent in mock_agents:
        for capability in agent["capabilities"]:
            capabilities_count[capability] = capabilities_count.get(capability, 0) + 1
    
    # 转换为图表数据格式
    distribution_data = []
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    
    for i, (capability, count) in enumerate(capabilities_count.items()):
        distribution_data.append({
            "capability": capability.replace("_", " ").title(),
            "count": count,
            "percentage": round((count / len(mock_agents)) * 100, 1),
            "color": colors[i % len(colors)]
        })
    
    # 如果没有数据，提供默认数据
    if not distribution_data:
        distribution_data = [
            {"capability": "Data Analysis", "count": 8, "percentage": 40.0, "color": "#1f77b4"},
            {"capability": "Text Generation", "count": 6, "percentage": 30.0, "color": "#ff7f0e"},
            {"capability": "Image Recognition", "count": 4, "percentage": 20.0, "color": "#2ca02c"},
            {"capability": "Code Generation", "count": 3, "percentage": 15.0, "color": "#d62728"}
        ]
    
    return {
        "data": distribution_data,
        "total_capabilities": sum(item["count"] for item in distribution_data),
        "unique_capabilities": len(distribution_data),
        "source": "mock_fallback",
        "timestamp": datetime.now().isoformat()
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
        {"skill": "Reliability", "value": min(100, target_agent["reputation"] + random.randint(-5, 5))},
        {"skill": "Learning Ability", "value": min(100, len(target_agent["capabilities"]) * 25 + random.randint(0, 20))}
    ]
    
    return {
        "data": radar_data,
        "agent_id": target_agent["agent_id"],
        "agent_name": target_agent["name"],
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }

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
                    # 这里可以从任务管理合约获取代理的任务历史
                    # 暂时使用模拟数据
                    task_history = [
                        {
                            "task_id": "task_123",
                            "title": "Market Analysis",
                            "completed_at": "2023-08-10T14:25:00Z",
                            "score": 4.9
                        },
                        {
                            "task_id": "task_456",
                            "title": "Customer Feedback Analysis",
                            "completed_at": "2023-08-05T11:15:00Z",
                            "score": 4.7
                        }
                    ]
                except Exception as e:
                    logger.error(f"Error getting task history for agent {agent_id}: {str(e)}")
                
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
            # 返回模拟的详细信息
            return {
                "agent_id": agent["agent_id"],
                "name": agent.get("name", f"Agent {agent_id[-4:]}"),
                "description": "An AI agent specialized in data analysis and pattern recognition.",
                "reputation": agent["reputation"],
                "capabilities": agent["capabilities"],
                "registration_date": "2023-07-15T10:30:00Z",
                "tasks_completed": agent["tasks_completed"],
                "average_score": agent["average_score"],
                "confidence_factor": 0.85,
                "risk_tolerance": 0.6,
                "task_history": [
                    {
                        "task_id": "task_123",
                        "title": "Market Analysis",
                        "completed_at": "2023-08-10T14:25:00Z",
                        "score": 4.9
                    },
                    {
                        "task_id": "task_456",
                        "title": "Customer Feedback Analysis",
                        "completed_at": "2023-08-05T11:15:00Z",
                        "score": 4.7
                    }
                ],
                "learning_events": [
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
                    }
                ],
                "source": "mock"
            }
    
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
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x1234567890123456789012345678901234567890"  # 示例地址
            
            # 调用合约服务注册代理
            result = contract_service.register_agent(agent, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "agent_id": result["agent_id"],
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to register agent on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error registering agent on blockchain: {str(e)}")
    
    # 如果区块链未连接或注册失败，使用模拟数据
    new_agent = {
        "agent_id": f"0x{uuid.uuid4().hex}",
        "name": agent.get("name", "New Agent"),
        "reputation": agent.get("reputation", 50),
        "capabilities": agent.get("capabilities", []),
        "tasks_completed": 0,
        "average_score": 0
    }
    
    mock_agents.append(new_agent)
    
    return {
        "success": True,
        "agent_id": new_agent["agent_id"],
        "transaction_hash": f"0x{uuid.uuid4().hex}",
        "block_number": 123456,
        "source": "mock"
    }

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
    删除代理（在实际应用中可能是禁用而不是删除）。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["agent_registry"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x1234567890123456789012345678901234567890"  # 示例地址
            
            # 调用合约服务禁用代理
            # 注意：这个方法需要在contract_service中实现
            # result = contract_service.disable_agent(agent_id, sender_address)
            # if result["success"]:
            #     return {
            #         "success": True,
            #         "agent_id": agent_id,
            #         "transaction_hash": result["transaction_hash"],
            #         "block_number": result["block_number"],
            #         "source": "blockchain"
            #     }
            # else:
            #     logger.warning(f"Failed to disable agent on blockchain: {result.get('error')}")
            pass
        except Exception as e:
            logger.error(f"Error disabling agent on blockchain: {str(e)}")
    
    # 如果区块链未连接或禁用失败，使用模拟数据
    for i, agent in enumerate(mock_agents):
        if agent["agent_id"] == agent_id:
            mock_agents.pop(i)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "deleted_at": datetime.now().isoformat(),
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Agent not found")

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
    # 检查代理是否存在
    agent_exists = False
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
    # 检查代理是否存在
    agent_exists = False
    for agent in mock_agents:
        if agent["agent_id"] == agent_id:
            agent_exists = True
            break
    
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
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