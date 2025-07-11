from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import asyncio

from services import contract_service
from services.chatgpt_service import collaboration_service
from services.collaboration_db_service import collaboration_db_service
from services.agent_selection_service import agent_selection_service

def get_sender_address():
    """
    动态获取Ganache的第一个账户地址作为发送者
    """
    try:
        if contract_service.w3 and contract_service.w3.is_connected():
            accounts = contract_service.w3.eth.accounts
            if accounts and len(accounts) > 0:
                return accounts[0]
        # fallback地址，虽然可能不工作
        return "0xc74024c471D840D6cd996a1dd92Cd2F3993D1220"
    except Exception as e:
        logger.error(f"Error getting sender address: {str(e)}")
        return "0xc74024c471D840D6cd996a1dd92Cd2F3993D1220"

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
    logger.info(f"Blockchain connection status: {connection_status}")
    
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 从区块链获取任务列表
            logger.info("Getting tasks from blockchain...")
            result = contract_service.get_all_tasks()
            logger.info(f"Blockchain tasks result: success={result['success']}, tasks count={len(result.get('tasks', []))}")
            
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
                
                logger.info(f"Returning {len(paginated_tasks)} blockchain tasks")
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
    logger.info("Using mock tasks data")
    filtered_tasks = mock_tasks
    
    # 应用过滤器
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    if capability:
        filtered_tasks = [t for t in filtered_tasks if capability in t["required_capabilities"]]
    
    if agent_id:
        filtered_tasks = [t for t in filtered_tasks if t.get("assigned_agent") == agent_id]
    
    # 应用分页
    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    logger.info(f"Returning {len(paginated_tasks)} mock tasks")
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
                # 构建完整的任务信息
                task_data = result.copy()
                task_data["source"] = "blockchain"
                
                return {"task": task_data}
            else:
                logger.warning(f"Failed to get task {task_id} from blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting task {task_id} from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            # 返回模拟的详细信息
            return {"task": {
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
                "source": "mock"
            }}
    
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
            # 动态获取发送者地址
            sender_address = get_sender_address()
            
            # 调用合约服务创建任务
            result = contract_service.create_task(task, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "task": {
                        "task_id": result["task_id"],
                        "title": task.get("title"),
                        "description": task.get("description"),
                        "required_capabilities": task.get("required_capabilities", []),
                        "reward": task.get("reward"),
                        "status": "open"
                    },
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to create task on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error creating task on blockchain: {str(e)}")
    
    # 如果区块链未连接或创建失败，使用模拟数据
    task_id = f"task_{uuid.uuid4().hex[:6]}"
    new_task = {
        "task_id": task_id,
        "title": task.get("title", "New Task"),
        "type": task.get("type", "unknown"),
        "status": "open",
        "reward": task.get("reward", 0.1),
        "created_at": datetime.now().isoformat(),
        "required_capabilities": task.get("required_capabilities", [])
    }
    
    # 将新任务添加到全局mock_tasks列表，而不是局部变量
    global mock_tasks
    mock_tasks.append(new_task)
    
    return {
        "success": True,
        "task": new_task,
        "transaction_hash": f"0x{uuid.uuid4().hex}",
        "block_number": 123456,
        "source": "mock"
    }

@router.put("/{task_id}", response_model=Dict[str, Any])
async def update_task(
    task_id: str,
    task_data: Dict[str, Any] = Body(...)
):
    """
    更新任务信息。
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 动态获取发送者地址
            sender_address = get_sender_address()
            
            # 调用合约服务更新任务
            result = contract_service.update_task(task_id, task_data, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "task_id": task_id,
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to update task on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error updating task on blockchain: {str(e)}")
    
    # 如果区块链未连接或更新失败，使用模拟数据
    for task in mock_tasks:
        if task["task_id"] == task_id:
            # 更新模拟任务数据
            task.update({
                "title": task_data.get("title", task.get("title")),
                "description": task_data.get("description", task.get("description")),
                "reward": task_data.get("reward", task.get("reward")),
                "required_capabilities": task_data.get("required_capabilities", task.get("required_capabilities")),
                "min_reputation": task_data.get("min_reputation", task.get("min_reputation"))
            })
            
            return {
                "success": True,
                "task_id": task_id,
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "block_number": 123456,
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

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
            # 动态获取发送者地址
            sender_address = get_sender_address()
            
            # 调用合约服务取消任务
            result = contract_service.cancel_task(task_id, sender_address)
            if result["success"]:
                return {
                    "success": True,
                    "task_id": task_id,
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to cancel task on blockchain: {result.get('error')}")
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

@router.post("/{task_id}/start-collaboration", response_model=Dict[str, Any])
async def start_task_collaboration(
    task_id: str,
    collaboration_data: Dict[str, Any] = Body(...)
):
    """
    启动智能体协作完成任务，使用智能代理选择服务。
    """
    try:
        # 检查区块链连接
        connection_status = contract_service.get_connection_status()
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            try:
                # 获取任务信息
                task_result = contract_service.get_task(task_id)
                if not task_result["success"]:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                # contract_service.get_task() 直接返回任务数据
                task_info = task_result
                
                # 获取所有代理
                agents_result = contract_service.get_all_agents()
                if not agents_result["success"]:
                    raise HTTPException(status_code=500, detail="Failed to get agents")
                
                agents = agents_result.get("agents", [])
                
                # 使用智能代理选择服务选择最适合的代理
                max_agents = collaboration_data.get("max_agents", 3)
                selected_agents_details = await agent_selection_service.select_collaborative_agents(
                    task_info, 
                    agents, 
                    max_agents
                )
                
                if not selected_agents_details:
                    return {
                        "success": False,
                        "error": "No suitable agents found for this task using intelligent selection",
                        "source": "blockchain"
                    }
                
                # 提取代理地址 - 从区块链返回的agent数据中地址字段是"address"，不是"agent_id"
                selected_agents = [agent.get("address") for agent in selected_agents_details if agent.get("address")]
                
                # 生成协作ID
                collaboration_id = f"collab_{task_id}_{int(datetime.now().timestamp())}"
                
                # 动态获取发送者地址
                sender_address = get_sender_address()
                
                # 启动协作
                result = contract_service.start_agent_collaboration(
                    task_id, 
                    selected_agents, 
                    collaboration_id, 
                    sender_address
                )
                
                if result["success"]:
                    logger.info(f"Successfully started collaboration for task {task_id} with {len(selected_agents)} agents")
                    return {
                        "success": True,
                        "collaboration_id": collaboration_id,
                        "selected_agents": selected_agents,
                        "selected_agents_details": selected_agents_details,
                        "transaction_hash": result["transaction_hash"],
                        "block_number": result["block_number"],
                        "source": "blockchain",
                        "selection_method": "intelligent"
                    }
                else:
                    logger.warning(f"Failed to start collaboration on blockchain: {result.get('error')}")
                    raise Exception(f"Blockchain collaboration failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error starting collaboration for task {task_id}: {str(e)}")
                raise e
        
        # 如果区块链未连接，使用智能选择的模拟实现
        logger.warning("Blockchain not connected, using mock intelligent selection")
        
        # 模拟任务信息
        mock_task_info = {
            "task_id": task_id,
            "required_capabilities": ["analysis", "generation", "nlp"],
            "min_reputation": 50,
            "title": "Mock Task",
            "description": "Mock task for testing intelligent agent selection"
        }
        
        # 模拟代理信息
        mock_agents = [
            {
                "agent_id": "0x1234567890123456789012345678901234567890",
                "name": "Agent Alpha",
                "capabilities": ["analysis", "nlp", "data_processing"],
                "capability_weights": [85, 90, 75],
                "reputation": 85,
                "workload": 2,
                "tasks_completed": 15,
                "average_score": 4.2,
                "active": True
            },
            {
                "agent_id": "0x3456789012345678901234567890123456789012",
                "name": "Agent Beta",
                "capabilities": ["generation", "nlp", "text_processing"],
                "capability_weights": [95, 80, 70],
                "reputation": 78,
                "workload": 1,
                "tasks_completed": 12,
                "average_score": 4.0,
                "active": True
            },
            {
                "agent_id": "0x5678901234567890123456789012345678901234",
                "name": "Agent Gamma",
                "capabilities": ["analysis", "generation", "research"],
                "capability_weights": [80, 85, 90],
                "reputation": 92,
                "workload": 3,
                "tasks_completed": 20,
                "average_score": 4.5,
                "active": True
            }
        ]
        
        # 使用智能选择算法
        max_agents = collaboration_data.get("max_agents", 3)
        selected_agents_details = await agent_selection_service.select_collaborative_agents(
            mock_task_info, 
            mock_agents, 
            max_agents
        )
        
        if not selected_agents_details:
            return {
                "success": False,
                "error": "No suitable agents found using intelligent selection",
                "source": "mock"
            }
        
        # 提取代理地址 - 使用mock数据时地址字段是"agent_id"
        selected_agents = [agent.get("agent_id") for agent in selected_agents_details if agent.get("agent_id")]
        
        collaboration_id = f"collab_{task_id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Mock intelligent selection completed for task {task_id}, selected {len(selected_agents)} agents")
        
        return {
            "success": True,
            "collaboration_id": collaboration_id,
            "selected_agents": selected_agents,
            "selected_agents_details": selected_agents_details,
            "transaction_hash": f"0x{uuid.uuid4().hex}",
            "block_number": 123456,
            "source": "mock",
            "selection_method": "intelligent"
        }
        
    except Exception as e:
        logger.error(f"Error in start_task_collaboration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start collaboration: {str(e)}")

@router.get("/{task_id}/suitable-agents", response_model=Dict[str, Any])
async def get_suitable_agents(task_id: str):
    """
    获取适合完成指定任务的代理列表，使用智能代理选择服务。
    """
    try:
        # 检查区块链连接
        connection_status = contract_service.get_connection_status()
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            try:
                # 获取任务信息
                task_result = contract_service.get_task(task_id)
                if not task_result["success"]:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                # contract_service.get_task() 直接返回任务数据
                task_info = task_result
                
                # 获取所有代理
                agents_result = contract_service.get_all_agents()
                if not agents_result["success"]:
                    raise HTTPException(status_code=500, detail="Failed to get agents")
                
                agents = agents_result.get("agents", [])
                
                # 使用智能代理选择服务获取合适的代理
                suitable_agents_details = await agent_selection_service.select_collaborative_agents(
                    task_info, 
                    agents, 
                    max_agents=5  # 获取更多选项以供用户选择
                )
                
                # 提取代理地址 - 从区块链返回的agent数据中地址字段是"address"，不是"agent_id"
                suitable_agents = [agent.get("address") for agent in suitable_agents_details if agent.get("address")]
                
                return {
                    "task_id": task_id,
                    "suitable_agents": suitable_agents,
                    "suitable_agents_details": suitable_agents_details,
                    "required_capabilities": task_info.get("required_capabilities", []),
                    "min_reputation": task_info.get("min_reputation", 0),
                    "source": "blockchain",
                    "selection_method": "intelligent"
                }
                
            except Exception as e:
                logger.error(f"Error getting suitable agents for task {task_id}: {str(e)}")
                raise e
        
        # 如果区块链未连接，使用智能选择的模拟实现
        logger.warning("Blockchain not connected, using mock intelligent selection for suitable agents")
        
        # 模拟任务信息
        mock_task_info = {
            "task_id": task_id,
            "required_capabilities": ["analysis", "generation", "nlp"],
            "min_reputation": 50,
            "title": "Mock Task",
            "description": "Mock task for testing intelligent agent selection"
        }
        
        # 模拟代理信息（更多代理供选择）
        mock_agents = [
            {
                "agent_id": "0x1234567890123456789012345678901234567890",
                "name": "Agent Alpha",
                "capabilities": ["analysis", "nlp", "data_processing"],
                "capability_weights": [85, 90, 75],
                "reputation": 85,
                "workload": 2,
                "tasks_completed": 15,
                "average_score": 4.2,
                "active": True
            },
            {
                "agent_id": "0x3456789012345678901234567890123456789012", 
                "name": "Agent Beta",
                "capabilities": ["generation", "nlp", "text_processing"],
                "capability_weights": [95, 80, 70],
                "reputation": 78,
                "workload": 1,
                "tasks_completed": 12,
                "average_score": 4.0,
                "active": True
            },
            {
                "agent_id": "0x5678901234567890123456789012345678901234",
                "name": "Agent Gamma", 
                "capabilities": ["analysis", "generation", "research"],
                "capability_weights": [80, 85, 90],
                "reputation": 92,
                "workload": 3,
                "tasks_completed": 20,
                "average_score": 4.5,
                "active": True
            },
            {
                "agent_id": "0x789abc0123456789012345678901234567890123",
                "name": "Agent Delta",
                "capabilities": ["nlp", "analysis", "reporting"],
                "capability_weights": [88, 75, 82],
                "reputation": 67,
                "workload": 1,
                "tasks_completed": 8,
                "average_score": 3.8,
                "active": True
            },
            {
                "agent_id": "0x9abcdef012345678901234567890123456789012",
                "name": "Agent Epsilon",
                "capabilities": ["generation", "analysis", "creative_writing"],
                "capability_weights": [92, 78, 95],
                "reputation": 89,
                "workload": 2,
                "tasks_completed": 18,
                "average_score": 4.3,
                "active": True
            }
        ]
        
        # 使用智能选择算法获取合适的代理
        suitable_agents_details = await agent_selection_service.select_collaborative_agents(
            mock_task_info, 
            mock_agents, 
            max_agents=5
        )
        
        # 提取代理地址 - 使用mock数据时地址字段是"agent_id"
        suitable_agents = [agent.get("agent_id") for agent in suitable_agents_details if agent.get("agent_id")]
        
        return {
            "task_id": task_id,
            "suitable_agents": suitable_agents,
            "suitable_agents_details": suitable_agents_details,
            "required_capabilities": mock_task_info.get("required_capabilities", []),
            "min_reputation": mock_task_info.get("min_reputation", 0),
            "source": "mock",
            "selection_method": "intelligent"
        }
        
    except Exception as e:
        logger.error(f"Error in get_suitable_agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get suitable agents: {str(e)}")

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

@router.post("/{task_id}/start-real-collaboration", response_model=Dict[str, Any])
async def start_real_collaboration(
    task_id: str,
    collaboration_data: Dict[str, Any] = Body({})
):
    """
    启动真实的agent协作对话（调用ChatGPT API）
    """
    try:
        # 检查任务是否存在并且已分配
        task_result = contract_service.get_task(task_id)
        if not task_result["success"]:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_info = task_result
        if task_info.get("status") != "assigned":
            raise HTTPException(status_code=400, detail="Task must be assigned before starting collaboration")
        
        # 获取已分配的agents
        assigned_agents = task_info.get("assigned_agents", [])
        if not assigned_agents:
            # 如果没有assigned_agents，使用assigned_agent
            assigned_agent = task_info.get("assigned_agent")
            if assigned_agent:
                assigned_agents = [assigned_agent]
            else:
                raise HTTPException(status_code=400, detail="No agents assigned to this task")
        
        # 获取agent详细信息
        agents_details = []
        for agent_addr in assigned_agents:
            agent_result = contract_service.get_agent_by_address(agent_addr)
            if agent_result["success"]:
                agent_info = agent_result["agent"]
                agents_details.append({
                    "address": agent_addr,
                    "name": agent_info.get("name", f"Agent-{agent_addr[-4:]}"),
                    "capabilities": agent_info.get("capabilities", [])
                })
            else:
                # 如果无法获取agent信息，使用基础信息
                agents_details.append({
                    "address": agent_addr,
                    "name": f"Agent-{agent_addr[-4:]}",
                    "capabilities": ["general"]
                })
        
        # 创建对话
        conversation_id = collaboration_service.create_conversation(
            task_id=task_id,
            agents=agents_details,
            task_description=task_info.get("description", "Task collaboration")
        )
        
        # 保存对话到数据库
        collaboration_db_service.create_conversation(
            conversation_id=conversation_id,
            task_id=task_id,
            task_description=task_info.get("description", "Task collaboration"),
            participants=[agent["address"] for agent in agents_details],
            agent_roles=collaboration_service.conversations[conversation_id]["agent_roles"]
        )
        
        # 启动分布式协作对话
        messages = await collaboration_service.start_distributed_collaboration(conversation_id)
        
        # 保存消息到数据库
        for message in messages:
            collaboration_db_service.add_message(
                conversation_id=conversation_id,
                sender_address=message["sender"],
                content=message["content"],
                message_index=message["message_index"],
                agent_name=message.get("agent_name"),
                round_number=message.get("round")
            )
        
        # 在区块链上记录对话开始事件
        try:
            sender_address = get_sender_address()
            blockchain_result = contract_service.record_collaboration_conversation_start(
                task_id=task_id,
                conversation_id=conversation_id,
                participants=[agent["address"] for agent in agents_details],
                conversation_topic=task_info.get("title", "Task Collaboration"),
                sender_address=sender_address
            )
            
            if blockchain_result["success"]:
                collaboration_db_service.record_blockchain_event(
                    event_type="collaboration_conversation_started",
                    task_id=task_id,
                    conversation_id=conversation_id,
                    event_data=blockchain_result,
                    transaction_hash=blockchain_result.get("transaction_hash"),
                    block_number=blockchain_result.get("block_number")
                )
        except Exception as e:
            logger.warning(f"Failed to record blockchain event: {e}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "task_id": task_id,
            "participants": agents_details,
            "messages": messages,
            "message_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error starting real collaboration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/finalize-collaboration", response_model=Dict[str, Any])
async def finalize_collaboration(
    task_id: str,
    finalization_data: Dict[str, Any] = Body({})
):
    """
    完成协作对话并生成最终结果
    """
    try:
        conversation_id = finalization_data.get("conversation_id")
        if not conversation_id:
            raise HTTPException(status_code=400, detail="conversation_id is required")
        
        # 完成协作并生成结果
        result = await collaboration_service.finalize_collaboration(conversation_id)
        
        # 保存结果到数据库
        collaboration_db_service.save_collaboration_result(
            conversation_id=conversation_id,
            task_id=task_id,
            final_result=result["final_result"],
            conversation_summary=result["conversation_summary"],
            participants=result["participants"],
            message_count=result["message_count"],
            success=True
        )
        
        # 在区块链上记录协作结果
        try:
            sender_address = get_sender_address()
            blockchain_result = contract_service.record_collaboration_result(
                task_id=task_id,
                conversation_id=conversation_id,
                participants=result["participants"],
                final_result=result["final_result"],
                conversation_summary=result["conversation_summary"],
                sender_address=sender_address
            )
            
            if blockchain_result["success"]:
                collaboration_db_service.record_blockchain_event(
                    event_type="collaboration_result",
                    task_id=task_id,
                    conversation_id=conversation_id,
                    event_data=blockchain_result,
                    transaction_hash=blockchain_result.get("transaction_hash"),
                    block_number=blockchain_result.get("block_number")
                )
                
                # 更新任务状态为完成
                task_complete_result = contract_service.complete_task(
                    task_id=task_id,
                    result=result["final_result"],
                    sender_address=sender_address
                )
                
                if task_complete_result["success"]:
                    logger.info(f"Task {task_id} completed with collaboration result")
                    
        except Exception as e:
            logger.warning(f"Failed to record blockchain result: {e}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "task_id": task_id,
            "final_result": result["final_result"],
            "conversation_summary": result["conversation_summary"],
            "participants": result["participants"],
            "message_count": result["message_count"]
        }
        
    except Exception as e:
        logger.error(f"Error finalizing collaboration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/conversations", response_model=Dict[str, Any])
async def get_task_conversations(task_id: str):
    """
    获取任务的所有对话记录
    """
    try:
        conversations = collaboration_db_service.get_task_conversations(task_id)
        
        conversations_data = []
        for conv in conversations:
            conversations_data.append({
                "id": conv.id,
                "conversation_id": conv.conversation_id,
                "status": conv.status,
                "participants": conv.participants,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "completed_at": conv.completed_at.isoformat() if conv.completed_at else None,
                "message_count": len(conv.messages) if conv.messages else 0
            })
        
        return {
            "task_id": task_id,
            "conversations": conversations_data,
            "total": len(conversations_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting task conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_details(task_id: str, conversation_id: str):
    """
    获取对话的详细信息（包括消息和结果）
    """
    try:
        conversation_details = collaboration_db_service.get_conversation_with_details(conversation_id)
        
        if not conversation_details:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation_details["task_id"] != task_id:
            raise HTTPException(status_code=400, detail="Conversation does not belong to this task")
        
        return {
            "success": True,
            "conversation": conversation_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/conversations/{conversation_id}/messages", response_model=Dict[str, Any])
async def get_conversation_messages(task_id: str, conversation_id: str):
    """
    获取对话的消息列表
    """
    try:
        messages = collaboration_db_service.get_conversation_messages(conversation_id)
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                "id": msg.id,
                "sender_address": msg.sender_address,
                "agent_name": msg.agent_name,
                "content": msg.content,
                "message_index": msg.message_index,
                "round_number": msg.round_number,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            })
        
        return {
            "task_id": task_id,
            "conversation_id": conversation_id,
            "messages": messages_data,
            "total": len(messages_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/smart-assign", response_model=Dict[str, Any])
async def smart_assign_task(
    task_id: str,
    collaborative: bool = Query(False, description="是否启用多代理协作模式"),
    max_agents: int = Query(3, ge=1, le=10, description="协作模式下最多选择的代理数量")
):
    """
    智能分配任务给最合适的代理
    """
    try:
        if collaborative:
            result = await agent_selection_service.auto_assign_collaborative_task(task_id, max_agents)
        else:
            result = await agent_selection_service.auto_assign_task(task_id)
            
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to smart assign task: {result.get('error')}"
            )
    except Exception as e:
        logger.exception(f"Error in smart_assign_task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{task_id}/recommended-agents", response_model=Dict[str, Any])
async def get_recommended_agents(
    task_id: str,
    max_recommendations: int = Query(5, ge=1, le=20, description="最大推荐数量")
):
    """
    获取任务的推荐代理列表
    """
    try:
        # 获取任务信息
        task_result = contract_service.get_task(task_id)
        if not task_result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=f"Task not found: {task_result.get('error')}"
            )
        
        # contract_service.get_task() 直接返回任务数据，不需要 .get("task")
        task = task_result
        
        # 获取所有代理
        agents_result = contract_service.get_all_agents()
        if not agents_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get agents: {agents_result.get('error')}"
            )
        
        agents = agents_result.get("agents", [])
        
        # 选择协作代理
        selected_agents = await agent_selection_service.select_collaborative_agents(task, agents, max_recommendations)
        
        # 移除评分字段，添加匹配度
        for agent in selected_agents:
            match_score = agent.pop("score", 0) * 100  # 转换为百分比
            agent["match_score"] = round(match_score, 2)
        
        return {
            "task_id": task_id,
            "recommended_agents": selected_agents,
            "total_recommendations": len(selected_agents),
            "source": "smart_selection"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in get_recommended_agents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )