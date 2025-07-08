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
mock_tasks = [
    {
        "task_id": "task_123",
        "title": "Analyze Customer Feedback",
        "type": "data_analysis",
        "status": "open",
        "reward": 0.5,
        "created_at": "2023-08-10T09:15:00Z",
        "required_capabilities": ["data_analysis", "nlp"]
    },
    {
        "task_id": "task_456",
        "title": "Generate Product Descriptions",
        "type": "text_generation",
        "status": "assigned",
        "reward": 0.3,
        "created_at": "2023-08-11T14:22:00Z",
        "required_capabilities": ["text_generation"],
        "assigned_agent": "0x1234567890123456789012345678901234567890"
    },
    {
        "task_id": "task_789",
        "title": "Classify Images",
        "type": "image_recognition",
        "status": "completed",
        "reward": 0.4,
        "created_at": "2023-08-09T11:45:00Z",
        "required_capabilities": ["image_recognition"],
        "assigned_agent": "0x2345678901234567890123456789012345678901",
        "completed_at": "2023-08-09T15:30:00Z"
    }
]

@router.get("/", response_model=Dict[str, Any])
async def get_tasks(
    status: Optional[str] = Query(None, description="按状态筛选"),
    capability: Optional[str] = Query(None, description="按所需能力筛选"),
    agent_id: Optional[str] = Query(None, description="按分配的代理筛选"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    获取任务列表，可选择按状态、所需能力或分配的代理筛选。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 从区块链获取任务列表
            result = contract_service.get_all_tasks()
            if result["success"]:
                tasks = result["tasks"]
                
                # 应用过滤器
                if status:
                    tasks = [t for t in tasks if t.get("status") == status]
                
                if capability:
                    tasks = [t for t in tasks if capability in t.get("required_capabilities", [])]
                
                if agent_id:
                    tasks = [t for t in tasks if t.get("assigned_to") == agent_id]
                
                # 应用分页
                total = len(tasks)
                paginated_tasks = tasks[offset:offset + limit]
                
                return {
                    "tasks": paginated_tasks,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to get tasks from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting tasks from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    filtered_tasks = mock_tasks
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    if capability:
        filtered_tasks = [t for t in filtered_tasks if capability in t["required_capabilities"]]
    
    if agent_id:
        filtered_tasks = [t for t in filtered_tasks if t.get("assigned_agent") == agent_id]
    
    # 应用分页
    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    return {
        "tasks": paginated_tasks,
        "total": len(filtered_tasks),
        "limit": limit,
        "offset": offset,
        "source": "mock"
    }

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task(task_id: str):
    """
    获取特定任务的详细信息。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 从区块链获取任务信息
            result = contract_service.get_task(task_id)
            if result["success"]:
                # 获取任务的竞标信息
                bids = []
                try:
                    # 这里可以从任务管理合约获取任务的竞标信息
                    # 暂时使用模拟数据
                    bids = [
                        {
                            "agent_id": "0x1234567890123456789012345678901234567890",
                            "amount": 0.45,
                            "timestamp": "2023-08-10T10:30:00Z"
                        },
                        {
                            "agent_id": "0x3456789012345678901234567890123456789012",
                            "amount": 0.5,
                            "timestamp": "2023-08-10T11:15:00Z"
                        }
                    ]
                except Exception as e:
                    logger.error(f"Error getting bids for task {task_id}: {str(e)}")
                
                # 构建完整的任务信息
                task_data = result.copy()
                task_data["bids"] = bids
                task_data["source"] = "blockchain"
                
                return task_data
            else:
                logger.warning(f"Failed to get task {task_id} from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting task {task_id} from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            # 返回模拟的详细信息
            return {
                "task_id": task["task_id"],
                "title": task["title"],
                "description": "Analyze customer feedback data to identify key trends and sentiment patterns.",
                "status": task["status"],
                "reward": task["reward"],
                "created_at": task["created_at"],
                "deadline": "2023-08-20T23:59:59Z",
                "required_capabilities": task["required_capabilities"],
                "complexity": "medium",
                "assigned_agent": task.get("assigned_agent"),
                "assigned_at": task.get("assigned_at"),
                "completed_at": task.get("completed_at"),
                "result": task.get("result"),
                "creator": "0x9876543210987654321098765432109876543210",
                "bids": [
                    {
                        "agent_id": "0x1234567890123456789012345678901234567890",
                        "amount": 0.45,
                        "timestamp": "2023-08-10T10:30:00Z"
                    },
                    {
                        "agent_id": "0x3456789012345678901234567890123456789012",
                        "amount": 0.5,
                        "timestamp": "2023-08-10T11:15:00Z"
                    }
                ],
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/", response_model=Dict[str, Any])
async def create_task(
    task: Dict[str, Any] = Body(...)
):
    """
    创建新任务。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x9876543210987654321098765432109876543210"  # 示例地址
            
            # 调用合约服务创建任务
            result = contract_service.create_task(task, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "task_id": result["task_id"],
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to create task on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error creating task on blockchain: {str(e)}")
    
    # 如果区块链未连接或创建失败，使用模拟数据
    new_task = {
        "task_id": f"task_{uuid.uuid4().hex[:6]}",
        "title": task.get("title", "New Task"),
        "type": task.get("type", "unknown"),
        "status": "open",
        "reward": task.get("reward", 0.1),
        "created_at": datetime.now().isoformat(),
        "required_capabilities": task.get("required_capabilities", [])
    }
    
    mock_tasks.append(new_task)
    
    return {
        "success": True,
        "task_id": new_task["task_id"],
        "transaction_hash": f"0x{uuid.uuid4().hex}",
        "block_number": 123456,
        "source": "mock"
    }

@router.post("/{task_id}/assign", response_model=Dict[str, Any])
async def assign_task(
    task_id: str,
    assignment: Dict[str, Any] = Body(...)
):
    """
    将任务分配给代理。
    """
    agent_id = assignment.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id is required")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x9876543210987654321098765432109876543210"  # 示例地址
            
            # 调用合约服务分配任务
            result = contract_service.assign_task(task_id, agent_id, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to assign task on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error assigning task on blockchain: {str(e)}")
    
    # 如果区块链未连接或分配失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            task["status"] = "assigned"
            task["assigned_agent"] = agent_id
            task["assigned_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "task_id": task_id,
                "agent_id": agent_id,
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "block_number": 123456,
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/{task_id}/complete", response_model=Dict[str, Any])
async def complete_task(
    task_id: str,
    completion: Dict[str, Any] = Body(...)
):
    """
    标记任务为已完成。
    """
    result = completion.get("result")
    if not result:
        raise HTTPException(status_code=400, detail="result is required")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x1234567890123456789012345678901234567890"  # 示例地址，应该是执行任务的代理
            
            # 调用合约服务完成任务
            contract_result = contract_service.complete_task(task_id, result, sender_address)
            if contract_result["success"]:
                return {
                    "success": True,
                    "task_id": task_id,
                    "transaction_hash": contract_result["transaction_hash"],
                    "block_number": contract_result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to complete task on blockchain: {contract_result.get('error')}")
        except Exception as e:
            logger.error(f"Error completing task on blockchain: {str(e)}")
    
    # 如果区块链未连接或完成失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            
            return {
                "success": True,
                "task_id": task_id,
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "block_number": 123456,
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/{task_id}/bid", response_model=Dict[str, Any])
async def place_bid(
    task_id: str,
    bid: Dict[str, Any] = Body(...)
):
    """
    为任务投标。
    """
    agent_id = bid.get("agent_id")
    amount = bid.get("amount")
    
    if not agent_id or amount is None:
        raise HTTPException(status_code=400, detail="agent_id and amount are required")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = agent_id  # 示例地址，应该是投标的代理
            
            # 调用合约服务投标
            # 注意：这个方法需要在contract_service中实现
            # result = contract_service.place_bid(task_id, amount, sender_address)
            # if result["success"]:
            #     return {
            #         "success": True,
            #         "task_id": task_id,
            #         "agent_id": agent_id,
            #         "amount": amount,
            #         "transaction_hash": result["transaction_hash"],
            #         "block_number": result["block_number"],
            #         "source": "blockchain"
            #     }
            # else:
            #     logger.warning(f"Failed to place bid on blockchain: {result.get('error')}")
            pass
        except Exception as e:
            logger.error(f"Error placing bid on blockchain: {str(e)}")
    
    # 如果区块链未连接或投标失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            if "bids" not in task:
                task["bids"] = []
            
            new_bid = {
                "agent_id": agent_id,
                "amount": amount,
                "timestamp": datetime.now().isoformat()
            }
            
            task["bids"].append(new_bid)
            
            return {
                "success": True,
                "task_id": task_id,
                "agent_id": agent_id,
                "amount": amount,
                "timestamp": new_bid["timestamp"],
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/{task_id}", response_model=Dict[str, Any])
async def delete_task(task_id: str):
    """
    删除任务（在实际应用中可能是取消而不是删除）。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x9876543210987654321098765432109876543210"  # 示例地址，应该是任务创建者
            
            # 调用合约服务取消任务
            # 注意：这个方法需要在contract_service中实现
            # result = contract_service.cancel_task(task_id, sender_address)
            # if result["success"]:
            #     return {
            #         "success": True,
            #         "task_id": task_id,
            #         "transaction_hash": result["transaction_hash"],
            #         "block_number": result["block_number"],
            #         "source": "blockchain"
            #     }
            # else:
            #     logger.warning(f"Failed to cancel task on blockchain: {result.get('error')}")
            pass
        except Exception as e:
            logger.error(f"Error canceling task on blockchain: {str(e)}")
    
    # 如果区块链未连接或取消失败，使用模拟数据
    for i, task in enumerate(mock_tasks):
        if task["task_id"] == task_id:
            mock_tasks.pop(i)
            
            return {
                "success": True,
                "task_id": task_id,
                "deleted_at": datetime.now().isoformat(),
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/status-distribution", response_model=Dict[str, Any])
async def get_task_status_distribution():
    """
    获取任务状态分布数据，用于前端图表展示。
    """
    # 首先尝试从合约获取数据
    contract_result = contract_service.get_contract_task_status_distribution()
    
    if contract_result["success"] and contract_result["data"]:
        return {
            "data": contract_result["data"],
            "total_tasks": contract_result["total_tasks"],
            "source": "contract",
            "timestamp": datetime.now().isoformat()
        }
    
    # 如果合约数据获取失败，使用模拟数据
    logger.warning("Failed to get contract data, using mock data")
    
    # 计算状态分布
    status_counts = {}
    for task in mock_tasks:
        status = task.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # 转换为图表数据格式
    distribution_data = []
    for status, count in status_counts.items():
        distribution_data.append({
            "id": status,
            "label": status.replace("_", " ").title(),
            "value": count,
            "color": {
                "open": "#2196F3",
                "assigned": "#FF9800",
                "completed": "#4CAF50",
                "cancelled": "#F44336"
            }.get(status, "#9E9E9E")
        })
    
    # 如果没有任务，提供默认数据
    if not distribution_data:
        distribution_data = [
            {"id": "open", "label": "Open", "value": 5, "color": "#2196F3"},
            {"id": "assigned", "label": "Assigned", "value": 8, "color": "#FF9800"},
            {"id": "completed", "label": "Completed", "value": 12, "color": "#4CAF50"}
        ]
    
    return {
        "data": distribution_data,
        "total_tasks": sum(item["value"] for item in distribution_data),
        "source": "mock_fallback",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/completion-trend", response_model=Dict[str, Any])
async def get_task_completion_trend():
    """
    获取任务完成趋势数据，用于前端趋势图表。
    """
    # 首先尝试从合约获取数据
    contract_result = contract_service.get_contract_task_completion_trend()
    
    if contract_result["success"] and contract_result["data"]:
        return {
            "data": contract_result["data"],
            "period": contract_result["period"],
            "source": "contract",
            "timestamp": datetime.now().isoformat()
        }
    
    # 如果合约数据获取失败，使用模拟数据
    logger.warning("Failed to get contract trend data, using mock data")
    
    from datetime import timedelta
    import random
    
    # 生成过去30天的趋势数据
    trend_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        # 模拟数据：工作日更多任务
        is_weekend = current_date.weekday() >= 5
        base_tasks = 3 if is_weekend else 8
        
        trend_data.append({
            "x": current_date.strftime("%Y-%m-%d"),
            "y": base_tasks + random.randint(-2, 4),
            "completed": base_tasks + random.randint(-1, 3),
            "created": base_tasks + random.randint(0, 5)
        })
    
    return {
        "data": trend_data,
        "period": "30_days",
        "source": "mock_fallback",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{task_id}/history", response_model=Dict[str, Any])
async def get_task_history(task_id: str):
    """
    获取任务的历史记录。
    """
    # 检查任务是否存在
    task_exists = False
    for task in mock_tasks:
        if task["task_id"] == task_id:
            task_exists = True
            break
    
    if not task_exists:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 模拟任务历史记录
    mock_history = [
        {
            "event": "created",
            "timestamp": "2023-08-10T09:15:00Z",
            "actor": "0x9876543210987654321098765432109876543210",
            "details": "Task created with reward of 0.5 ETH"
        },
        {
            "event": "bid_placed",
            "timestamp": "2023-08-10T10:30:00Z",
            "actor": "0x1234567890123456789012345678901234567890",
            "details": "Bid placed for 0.45 ETH"
        },
        {
            "event": "bid_placed",
            "timestamp": "2023-08-10T11:15:00Z",
            "actor": "0x3456789012345678901234567890123456789012",
            "details": "Bid placed for 0.5 ETH"
        },
        {
            "event": "assigned",
            "timestamp": "2023-08-11T09:00:00Z",
            "actor": "0x9876543210987654321098765432109876543210",
            "details": "Task assigned to agent 0x1234567890123456789012345678901234567890"
        }
    ]
    
    # 如果任务已完成，添加完成记录
    for task in mock_tasks:
        if task["task_id"] == task_id and task["status"] == "completed" and task.get("completed_at"):
            mock_history.append({
                "event": "completed",
                "timestamp": task["completed_at"],
                "actor": task.get("assigned_agent", "unknown"),
                "details": f"Task completed with result: {task.get('result', 'No result provided')}"
            })
    
    return {
        "task_id": task_id,
        "history": mock_history
    }