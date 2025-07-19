from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import asyncio
import time

from services import contract_service
from services.agent_collaboration_service import agent_collaboration_service as collaboration_service
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

@router.get("/debug/connection")
async def debug_connection():
    """
    Debug endpoint to test connection status
    """
    logger.info("Debug connection endpoint called")
    connection_status = contract_service.get_connection_status()
    logger.info(f"Debug connection status: {connection_status}")
    return {"status": "ok", "connection": connection_status}

@router.get("/debug/task/{task_id}")
async def debug_task(task_id: str):
    """
    Debug endpoint to test task retrieval
    """
    # Force initialization
    if not contract_service.w3 or not contract_service.w3.is_connected():
        contract_service.init_web3()
        contract_service.initialize_contracts()
    
    # Debug contract status
    debug_info = {
        "w3_connected": contract_service.w3.is_connected() if contract_service.w3 else False,
        "task_manager_contract_exists": contract_service.task_manager_contract is not None,
    }
    
    # Test raw event filtering
    collaboration_agents = []
    all_events = []
    try:
        if contract_service.task_manager_contract:
            # Get all collaboration events
            try:
                event_filter = contract_service.task_manager_contract.events.AgentCollaborationStarted.create_filter(
                    from_block='earliest',
                    to_block='latest'
                )
            except TypeError:
                event_filter = contract_service.task_manager_contract.events.AgentCollaborationStarted.create_filter(
                    fromBlock='earliest',
                    toBlock='latest'
                )
            all_events = event_filter.get_all_entries()
            debug_info["total_collaboration_events"] = len(all_events)
            
            # Get specific events for this task
            task_id_bytes = bytes.fromhex(task_id)
            try:
                task_filter = contract_service.task_manager_contract.events.AgentCollaborationStarted.create_filter(
                    from_block='earliest',
                    to_block='latest',
                    argument_filters={'taskId': task_id_bytes}
                )
            except TypeError:
                task_filter = contract_service.task_manager_contract.events.AgentCollaborationStarted.create_filter(
                    fromBlock='earliest',
                    toBlock='latest',
                    argument_filters={'taskId': task_id_bytes}
                )
            task_events = task_filter.get_all_entries()
            debug_info["task_collaboration_events"] = len(task_events)
            
            if task_events:
                collaboration_agents = list(task_events[-1]['args']['selectedAgents'])
        
    except Exception as e:
        debug_info["error"] = str(e)
    
    # Get task directly from blockchain
    result = contract_service.get_task(task_id)
    
    return {
        "task_id": task_id,
        "debug_info": debug_info,
        "blockchain_result": result,
        "collaboration_agents": collaboration_agents,
        "collaboration_agents_count": len(collaboration_agents),
        "all_events_count": len(all_events)
    }


async def auto_execute_collaboration(task_id: str, task_info: Dict[str, Any]):
    """
    自动执行agent协作的后台任务
    """
    try:
        logger.info(f"🚀 Starting automatic collaboration for task {task_id}")
        logger.info(f"📋 Task info: {task_info.get('title', 'Unknown')} - {task_info.get('type', 'unknown type')}")
        
        # 创建协作ID
        collaboration_id = await collaboration_service.create_collaboration(task_id, task_info)
        logger.info(f"✅ Created collaboration {collaboration_id} for task {task_id}")
        
        # 减少等待时间以便快速测试
        logger.info(f"⏳ Preparing collaboration environment...")
        await asyncio.sleep(3)  # 3秒准备时间
        
        # 运行协作
        logger.info(f"🤖 Running agent collaboration for task {task_id}")
        collaboration_result = await collaboration_service.run_collaboration(collaboration_id, task_info)
        logger.info(f"📊 Collaboration result status: {collaboration_result.get('status')}")
        logger.info(f"📄 Result summary: {collaboration_result.get('conversation', [{}])[-1].get('content', 'No content')[:200]}...")
        
        if collaboration_result.get("status") == "completed":
            # 自动将任务状态更新为completed
            logger.info(f"🎯 Collaboration completed successfully! Updating task status...")
            await auto_complete_task(task_id, collaboration_result)
            logger.info(f"✅ Task {task_id} automatically marked as completed")
        else:
            logger.warning(f"⚠️ Collaboration for task {task_id} failed or incomplete. Status: {collaboration_result.get('status')}")
            
    except Exception as e:
        logger.error(f"❌ Error in automatic collaboration for task {task_id}: {str(e)}")

async def auto_complete_task(task_id: str, collaboration_result: Dict[str, Any]):
    """
    自动完成任务并更新状态
    """
    try:
        logger.info(f"🔄 Auto-completing task {task_id}")
        logger.info(f"📊 Result data: IPFS CID: {collaboration_result.get('ipfs_cid', 'N/A')}")
        
        # 检查区块链连接
        connection_status = contract_service.get_connection_status()
        
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            try:
                # 获取发送者地址
                sender_address = get_sender_address()
                logger.info(f"🔗 Completing task on blockchain with sender: {sender_address}")
                
                # 调用合约服务完成任务
                result = contract_service.complete_task(
                    task_id=task_id,
                    result_data=collaboration_result.get("ipfs_cid", ""),
                    sender_address=sender_address
                )
                
                if result["success"]:
                    logger.info(f"✅ Task {task_id} completed on blockchain: {result['transaction_hash']}")
                else:
                    logger.warning(f"⚠️ Failed to complete task {task_id} on blockchain: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ Error completing task {task_id} on blockchain: {str(e)}")
        
        # 更新mock数据
        logger.info(f"📝 Updating mock data for task {task_id}")
        for task in mock_tasks:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                task["result"] = collaboration_result.get("ipfs_cid", "")
                logger.info(f"✅ Updated mock task {task_id} status to completed at {task['completed_at']}")
                logger.info(f"📄 Task result stored: {task.get('result', 'No result')}")
                break
        else:
            logger.warning(f"⚠️ Task {task_id} not found in mock_tasks list")
                
    except Exception as e:
        logger.error(f"❌ Error auto-completing task {task_id}: {str(e)}")

# 模拟数据
mock_tasks = [
    {
        "task_id": "task_123",
        "title": "Analyze Customer Feedback",
        "description": "Analyze customer feedback data to identify patterns and sentiment trends for product improvement",
        "type": "data_analysis",
        "status": "open",
        "reward": 0.5,
        "created_at": "2023-08-10T09:15:00Z",
        "deadline": "2025-08-20T23:59:59Z",
        "required_capabilities": ["data_analysis", "nlp"],
        "complexity": "medium",
        "creator": "0x9876543210987654321098765432109876543210"
    },
    {
        "task_id": "task_456",
        "title": "Generate Product Descriptions",
        "description": "Create compelling product descriptions for new e-commerce listings using AI collaboration",
        "type": "text_generation",
        "status": "assigned",
        "reward": 0.3,
        "created_at": "2023-08-11T14:22:00Z",
        "assigned_at": datetime.now().isoformat(),
        "required_capabilities": ["text_generation"],
        "assigned_agent": "0x1234567890123456789012345678901234567890"
    },
    {
        "task_id": "task_789",
        "title": "Classify Images",
        "description": "Classify product images into categories for better search and discovery",
        "type": "image_recognition",
        "status": "completed",
        "reward": 0.4,
        "created_at": "2023-08-09T11:45:00Z",
        "required_capabilities": ["image_recognition"],
        "assigned_agent": "0x2345678901234567890123456789012345678901",
        "completed_at": "2023-08-09T15:30:00Z"
    },
    {
        "task_id": "task_999",
        "title": "Test Agent Collaboration",
        "description": "Test task for verifying multi-agent collaboration functionality with real data",
        "type": "data_analysis",
        "status": "open",
        "reward": 0.8,
        "created_at": "2025-07-14T15:00:00Z",
        "deadline": "2025-08-20T23:59:59Z",
        "required_capabilities": ["data_analysis", "nlp", "text_generation"],
        "complexity": "high",
        "creator": "0x9876543210987654321098765432109876543210"
    },
    {
        "task_id": "task_888",
        "title": "Real-time Agent Collaboration Test",
        "description": "Demonstrate multi-agent collaboration with live agent selection and task assignment",
        "type": "data_analysis",
        "status": "open",
        "reward": 1.0,
        "created_at": "2025-07-14T16:00:00Z",
        "deadline": "2025-08-25T23:59:59Z",
        "required_capabilities": ["data_analysis", "nlp"],
        "complexity": "medium",
        "creator": "0x9876543210987654321098765432109876543210"
    },
    {
        "task_id": "task_777",
        "title": "Complete Workflow Test",
        "description": "Test the complete workflow from open -> assigned -> completed with blockchain integration",
        "type": "data_analysis",
        "status": "assigned",
        "reward": 1.5,
        "created_at": "2025-07-14T17:00:00Z",
        "deadline": "2025-08-30T23:59:59Z",
        "required_capabilities": ["data_analysis", "text_generation"],
        "complexity": "high",
        "creator": "0x9876543210987654321098765432109876543210",
        "assigned_agent": "0x1234567890123456789012345678901234567890",
        "assigned_at": "2025-07-14T23:40:48.376203"
    },
    {
        "task_id": "task_555",
        "title": "Frontend Test Task",
        "description": "Test task for frontend Start Agent Collaboration functionality",
        "type": "data_analysis",
        "status": "open",
        "reward": 0.8,
        "created_at": "2025-07-14T18:00:00Z",
        "deadline": "2025-08-31T23:59:59Z",
        "required_capabilities": ["data_analysis", "nlp"],
        "complexity": "medium",
        "creator": "0x9876543210987654321098765432109876543210"
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
                
                # 获取已删除的任务列表
                deleted_task_ids = set()
                try:
                    from services.collaboration_db_service import collaboration_db_service
                    deleted_events = collaboration_db_service.get_blockchain_events(
                        event_type="TaskDeleted",
                        limit=1000
                    )
                    deleted_task_ids = {event.get("task_id") for event in deleted_events if event.get("task_id")}
                    logger.info(f"Found {len(deleted_task_ids)} deleted tasks to filter out")
                except Exception as e:
                    logger.warning(f"Failed to get deleted tasks list: {e}")
                
                # 过滤掉已删除的任务
                tasks = [t for t in tasks if t.get("task_id") not in deleted_task_ids]
                
                # 默认过滤掉已取消的任务，除非明确请求
                if status != "cancelled":
                    tasks = [t for t in tasks if t.get("status") != "cancelled"]
                
                # 应用状态过滤器
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
    
    # 默认过滤掉已取消的任务，除非明确请求
    if status != "cancelled":
        filtered_tasks = [t for t in filtered_tasks if t.get("status") != "cancelled"]
    
    # 应用状态过滤器
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
    # 强制初始化合约服务如果需要
    if not contract_service.w3 or not contract_service.w3.is_connected():
        contract_service.init_web3()
        contract_service.initialize_contracts()
    
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
                
                # 如果assigned_agents为空，强制重新获取
                if not task_data.get("assigned_agents"):
                    try:
                        task_id_bytes = bytes.fromhex(task_id)
                        collaboration_agents = contract_service.get_task_collaboration_agents(task_id_bytes)
                        if collaboration_agents:
                            task_data["assigned_agents"] = collaboration_agents
                    except Exception as e:
                        logger.warning(f"Failed to get collaboration agents for task {task_id}: {e}")
                
                # 检查数据库中是否有更新的协作结果
                try:
                    from services.collaboration_db_service import collaboration_db_service
                    updated_result = collaboration_db_service.get_task_collaboration_result(task_id)
                    if updated_result and updated_result.get('ipfs_cid'):
                        logger.info(f"Found updated collaboration result for task {task_id}: {updated_result['ipfs_cid']}")
                        task_data["result"] = updated_result['ipfs_cid']
                        task_data["result_source"] = "database_updated"
                except Exception as e:
                    logger.debug(f"No updated collaboration result found for task {task_id}: {e}")
                
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
    将任务分配给代理并自动启动协作。
    """
    agent_id = assignment.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id is required")
    
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    assignment_result = None
    
    if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x9876543210987654321098765432109876543210"  # 示例地址
            
            # 调用合约服务分配任务
            result = contract_service.assign_task(task_id, agent_id, sender_address)
            if result["success"]:
                assignment_result = {
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
    if not assignment_result:
        for task in mock_tasks:
            if task["task_id"] == task_id:
                task["status"] = "assigned"
                task["assigned_agent"] = agent_id
                task["assigned_at"] = datetime.now().isoformat()
                
                assignment_result = {
                    "success": True,
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "transaction_hash": f"0x{uuid.uuid4().hex}",
                    "block_number": 123456,
                    "source": "mock"
                }
                break
    
    if not assignment_result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 自动启动agent协作
    try:
        logger.info(f"Starting automatic collaboration for task {task_id}")
        
        # 获取任务信息
        task_info = None
        if connection_status["connected"]:
            task_result = contract_service.get_task(task_id)
            if task_result["success"]:
                task_info = task_result["task"]
        
        if not task_info:
            # 使用mock数据
            for task in mock_tasks:
                if task["task_id"] == task_id:
                    task_info = task
                    break
        
        if task_info:
            # 启动后台协作任务
            asyncio.create_task(auto_execute_collaboration(task_id, task_info))
            
            assignment_result["collaboration_status"] = "started"
            assignment_result["message"] = "Task assigned successfully. Agent collaboration is starting in the background."
        
    except Exception as e:
        logger.error(f"Error starting automatic collaboration: {str(e)}")
        assignment_result["collaboration_status"] = "failed"
        assignment_result["message"] = "Task assigned successfully, but failed to start collaboration."
    
    return assignment_result

@router.get("/{task_id}/status", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    获取任务的实时状态和协作进度
    """
    try:
        # 检查区块链连接
        connection_status = contract_service.get_connection_status()
        task_info = None
        
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            try:
                task_result = contract_service.get_task(task_id)
                if task_result["success"]:
                    task_info = task_result["task"]
            except Exception as e:
                logger.error(f"Error getting task from blockchain: {str(e)}")
        
        # 如果区块链未连接或获取失败，使用模拟数据
        if not task_info:
            for task in mock_tasks:
                if task["task_id"] == task_id:
                    task_info = task
                    break
        
        if not task_info:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 构建状态响应
        status_response = {
            "task_id": task_id,
            "status": task_info.get("status", "unknown"),
            "assigned_agent": task_info.get("assigned_agent"),
            "assigned_at": task_info.get("assigned_at"),
            "completed_at": task_info.get("completed_at"),
            "collaboration_progress": get_collaboration_progress(task_info.get("status")),
            "estimated_completion": get_estimated_completion_time(task_info.get("assigned_at")),
            "message": get_status_message(task_info.get("status"))
        }
        
        return status_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_collaboration_progress(status: str) -> Dict[str, Any]:
    """获取协作进度信息"""
    import time
    
    if status == "open":
        return {"percentage": 0, "stage": "Waiting for assignment"}
    elif status == "assigned":
        # 模拟动态进度，基于当前时间
        current_second = int(time.time()) % 60
        if current_second < 10:
            return {"percentage": 25, "stage": "Initializing agent collaboration..."}
        elif current_second < 20:
            return {"percentage": 40, "stage": "Agents analyzing task requirements..."}
        elif current_second < 30:
            return {"percentage": 55, "stage": "Agents working on task components..."}
        elif current_second < 40:
            return {"percentage": 70, "stage": "Agents collaborating and sharing results..."}
        elif current_second < 50:
            return {"percentage": 85, "stage": "Integrating collaborative results..."}
        else:
            return {"percentage": 95, "stage": "Finalizing collaboration output..."}
    elif status == "completed":
        return {"percentage": 100, "stage": "Task completed successfully"}
    elif status == "failed":
        return {"percentage": 0, "stage": "Task failed"}
    else:
        return {"percentage": 0, "stage": "Unknown status"}

def get_estimated_completion_time(assigned_at: str) -> Optional[str]:
    """获取预估完成时间"""
    if not assigned_at:
        return None
    
    try:
        from datetime import datetime, timedelta
        assigned_time = datetime.fromisoformat(assigned_at.replace('Z', '+00:00'))
        # 假设协作需要1-2分钟完成（用于快速测试）
        estimated_time = assigned_time + timedelta(minutes=1, seconds=30)
        return estimated_time.isoformat()
    except:
        return None

def get_status_message(status: str) -> str:
    """获取状态消息"""
    messages = {
        "open": "Task is available for assignment",
        "assigned": "Agents are working on this task. Please wait for completion...",
        "completed": "Task has been completed successfully. You can now view the results.",
        "failed": "Task execution failed. Please try reassigning or check the requirements."
    }
    return messages.get(status, "Unknown task status")

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

@router.post("/{task_id}/evaluate", response_model=Dict[str, Any])
async def evaluate_task(task_id: str, evaluation_data: Dict[str, Any]):
    """
    评估任务完成情况并更新agent学习数据
    """
    try:
        logger.info(f"🎯 Evaluating task {task_id} with data: {evaluation_data}")
        
        # 检查是否已经评价过（除非是系统自动评价）
        evaluation_check = collaboration_db_service.check_task_evaluation_exists(task_id)
        evaluator = evaluation_data.get("evaluator", "user")
        
        if evaluation_check["evaluated"]:
            if evaluator != "system":
                # 用户重复评价：直接拒绝
                logger.warning(f"⚠️ Task {task_id} has already been evaluated by user")
                last_eval = evaluation_check["last_evaluation"]
                
                raise HTTPException(
                    status_code=400, 
                    detail=f"Task has already been evaluated on {last_eval['timestamp']} by {last_eval['evaluator']}. Duplicate evaluations are not allowed."
                )
            else:
                # 系统自动评价：如果用户已评价过，就跳过系统评价
                logger.info(f"⏭️ Task {task_id} already evaluated by user, skipping system auto-evaluation")
                return {
                    "success": True,
                    "message": f"Task already evaluated by user, system auto-evaluation skipped.",
                    "data": {
                        "task_id": task_id,
                        "evaluation_data": evaluation_data,
                        "skipped": True,
                        "reason": "User evaluation already exists"
                    }
                }
        
        # 获取任务信息
        task_result = contract_service.get_task(task_id)
        if not task_result.get("success"):
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        task_data = task_result.copy()
        
        # 检查任务状态
        if task_data.get("status") != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Task must be completed before evaluation. Current status: {task_data.get('status')}"
            )
        
        # Get assigned agents from task data or evaluation data
        assigned_agents = task_data.get("assigned_agents", [])
        if not assigned_agents and task_data.get("assigned_agent"):
            assigned_agents = [task_data.get("assigned_agent")]
        
        # Allow overriding assigned agents from evaluation data (for testing/Force Complete scenarios)
        if evaluation_data.get("assigned_agents"):
            assigned_agents = evaluation_data.get("assigned_agents")
        
        logger.info(f"📋 Task has {len(assigned_agents)} assigned agents")
        
        # 评估数据
        success = evaluation_data.get("success", True)
        rating = evaluation_data.get("rating", 5)
        evaluator = evaluation_data.get("evaluator", "system")
        notes = evaluation_data.get("notes", "")
        
        # 为每个参与的agent创建学习事件
        learning_events = []
        for agent_id in assigned_agents:
            try:
                # 计算奖励和声誉变化
                reward_multiplier = rating / 5.0  # 将评分转换为奖励倍数
                reputation_change = 5 if success else -3  # 成功+5，失败-3
                reputation_change = int(reputation_change * reward_multiplier)
                
                # 创建学习事件数据
                learning_event_data = {
                    "agent_id": agent_id,
                    "event_type": "task_evaluation",
                    "data": {
                        "task_id": task_id,
                        "task_title": task_data.get("title", "Unknown Task"),
                        "success": success,
                        "rating": rating,
                        "reputation_change": reputation_change,
                        "reward": task_data.get("reward", 0) * reward_multiplier if success else 0,
                        "capabilities_used": task_data.get("required_capabilities", []),
                        "evaluator": evaluator,
                        "notes": notes,
                        "timestamp": time.time()
                    }
                }
                
                # 调用学习API创建事件
                from services.agent_collaboration_service import agent_collaboration_service
                learning_result = await agent_collaboration_service.create_learning_event(
                    agent_id, 
                    learning_event_data
                )
                
                learning_events.append({
                    "agent_id": agent_id,
                    "learning_event": learning_result,
                    "reputation_change": reputation_change,
                    "reward": learning_event_data["data"]["reward"]
                })
                
                logger.info(f"✅ Created learning event for agent {agent_id}: reputation {reputation_change:+d}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create learning event for agent {agent_id}: {e}")
                continue
        
        # 记录评估结果
        evaluation_result = {
            "task_id": task_id,
            "evaluation_data": evaluation_data,
            "learning_events": learning_events,
            "total_agents_updated": len(learning_events),
            "timestamp": time.time()
        }
        
        logger.info(f"🎉 Task evaluation completed: {len(learning_events)} agents updated")
        
        return {
            "success": True,
            "message": f"Task evaluated successfully. {len(learning_events)} agents updated.",
            "data": evaluation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error evaluating task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-evaluate", response_model=Dict[str, Any])
async def auto_evaluate_overdue_tasks():
    """
    检查并自动评价超过2天未评价的已完成任务
    """
    try:
        logger.info("🤖 Starting automatic evaluation of overdue tasks...")
        
        # 获取待评价任务信息
        pending_info = collaboration_db_service.get_tasks_pending_evaluation(days_threshold=2)
        evaluated_task_ids = set(pending_info["evaluated_task_ids"])
        
        # 获取所有已完成的任务
        completed_tasks = []
        connection_status = contract_service.get_connection_status()
        
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            # 从区块链获取已完成任务
            tasks_result = contract_service.get_all_tasks()
            if tasks_result.get("success") and tasks_result.get("tasks"):
                from datetime import datetime, timedelta
                threshold_time = datetime.fromisoformat(pending_info["threshold_time"].replace('Z', '+00:00'))
                
                for task in tasks_result["tasks"]:
                    if (task.get("status") == "completed" and 
                        task.get("task_id") not in evaluated_task_ids):
                        
                        # 检查任务完成时间是否超过2天
                        completed_at = task.get("completed_at")
                        if completed_at:
                            try:
                                completed_datetime = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                                if completed_datetime < threshold_time:
                                    completed_tasks.append(task)
                            except ValueError:
                                logger.warning(f"Invalid completed_at format for task {task.get('task_id')}: {completed_at}")
                                continue
        
        logger.info(f"Found {len(completed_tasks)} tasks pending auto-evaluation")
        
        # 自动评价每个任务
        auto_evaluated = []
        for task in completed_tasks:
            try:
                task_id = task.get("task_id")
                
                # 获取任务的协作结果来评估完成质量
                collaboration_result = None
                try:
                    collaboration_result = collaboration_db_service.get_task_collaboration_result(task_id)
                except:
                    pass  # 如果没有协作结果，使用默认评分
                
                # 基于任务完成情况进行自动评分
                auto_rating = 3  # 默认中等评分
                auto_success = True
                auto_notes = "Automatic evaluation after 2 days - task completed without user feedback"
                
                # 如果有协作结果，尝试基于结果质量调整评分
                if collaboration_result and collaboration_result.get("success"):
                    auto_rating = 4  # 有成功的协作结果，提高评分
                    auto_notes = "Automatic evaluation - task completed successfully with collaboration result"
                
                # 构建自动评价数据
                evaluation_data = {
                    "success": auto_success,
                    "rating": auto_rating,
                    "evaluator": "system",
                    "notes": auto_notes,
                    "auto_evaluation": True
                }
                
                # 调用评价函数
                result = await evaluate_task(task_id, evaluation_data)
                
                if result.get("success"):
                    auto_evaluated.append({
                        "task_id": task_id,
                        "title": task.get("title", "Unknown"),
                        "rating": auto_rating,
                        "agents_updated": result.get("data", {}).get("total_agents_updated", 0)
                    })
                    logger.info(f"✅ Auto-evaluated task {task_id} with rating {auto_rating}")
                
            except Exception as e:
                logger.error(f"❌ Failed to auto-evaluate task {task.get('task_id')}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Auto-evaluation completed. {len(auto_evaluated)} tasks evaluated.",
            "data": {
                "total_pending": len(completed_tasks),
                "auto_evaluated": len(auto_evaluated),
                "evaluated_tasks": auto_evaluated,
                "threshold_days": 2
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in auto-evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/evaluation-status", response_model=Dict[str, Any])
async def get_task_evaluation_status(task_id: str):
    """
    获取任务的评价状态
    """
    try:
        evaluation_check = collaboration_db_service.check_task_evaluation_exists(task_id)
        return {
            "success": True,
            "task_id": task_id,
            "evaluation_status": evaluation_check
        }
    except Exception as e:
        logger.error(f"❌ Error checking evaluation status for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/{task_id}/delete-preview", response_model=Dict[str, Any])
async def preview_task_deletion(task_id: str):
    """
    预览删除任务会影响哪些数据，不执行实际删除。
    """
    try:
        logger.info(f"🔍 Previewing deletion impact for task {task_id}")
        
        # 检查任务是否存在
        task_result = contract_service.get_task(task_id)
        if not task_result.get("success"):
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_result
        task_status = task_data.get("status", "unknown")
        
        # 获取相关数据摘要
        data_summary = {}
        try:
            from services.collaboration_db_service import collaboration_db_service
            data_summary = collaboration_db_service.get_task_related_data_summary(task_id)
        except Exception as e:
            logger.warning(f"Failed to get data summary: {e}")
            data_summary = {"error": str(e)}
        
        # 检查是否可以删除
        can_delete = task_status not in ["in_progress"]
        deletion_warnings = []
        
        if not can_delete:
            deletion_warnings.append(f"Task status '{task_status}' prevents deletion")
        
        if data_summary.get("total_records", 0) > 0:
            deletion_warnings.append("This task has associated collaboration data that will be permanently deleted")
        
        preview_result = {
            "task_id": task_id,
            "task_status": task_status,
            "can_delete": can_delete,
            "data_impact": data_summary,
            "warnings": deletion_warnings,
            "deletion_actions": [
                "Cancel task on blockchain (if connected)",
                "Delete collaboration conversations and messages",
                "Delete blockchain events and learning records",
                "Remove from local/mock data if present"
            ]
        }
        
        logger.info(f"📋 Deletion preview for task {task_id}: {preview_result}")
        return preview_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error previewing deletion for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{task_id}", response_model=Dict[str, Any])
async def delete_task(task_id: str):
    """
    删除任务并清理所有相关数据。
    注意：此操作会永久删除任务及其所有协作数据，不可恢复。
    """
    try:
        logger.info(f"🗑️ Starting deletion of task {task_id}")
        
        # 1. 首先检查任务是否存在和可删除
        task_result = contract_service.get_task(task_id)
        if not task_result.get("success"):
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_result
        task_status = task_data.get("status", "unknown")
        
        # 检查任务状态是否允许删除
        if task_status in ["in_progress"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete task with status '{task_status}'. Please cancel the task first."
            )
        
        logger.info(f"📋 Task {task_id} has status '{task_status}' and can be deleted")
        
        # 2. 清理数据库相关数据
        cleanup_results = {}
        
        try:
            from services.collaboration_db_service import collaboration_db_service
            
            # 清理协作对话数据
            conversations_deleted = collaboration_db_service.delete_conversations_by_task_id(task_id)
            cleanup_results["conversations_deleted"] = conversations_deleted
            
            # 清理区块链事件数据
            events_deleted = collaboration_db_service.delete_blockchain_events_by_task_id(task_id)
            cleanup_results["blockchain_events_deleted"] = events_deleted
            
            logger.info(f"🧹 Database cleanup completed: {cleanup_results}")
            
        except Exception as e:
            logger.warning(f"Failed to clean up database records: {e}")
            cleanup_results["database_cleanup_error"] = str(e)
        
        # 3. 尝试从区块链取消/删除任务
        blockchain_result = None
        connection_status = contract_service.get_connection_status()
        if connection_status["connected"] and connection_status["contracts"]["task_manager"]:
            try:
                # 动态获取发送者地址
                sender_address = get_sender_address()
                
                # 调用合约服务取消任务
                blockchain_result = contract_service.cancel_task(task_id, sender_address)
                if blockchain_result["success"]:
                    logger.info(f"✅ Task {task_id} cancelled on blockchain: {blockchain_result.get('transaction_hash')}")
                else:
                    logger.warning(f"Failed to cancel task on blockchain: {blockchain_result.get('error')}")
            except Exception as e:
                logger.error(f"Error canceling task on blockchain: {str(e)}")
                blockchain_result = {"success": False, "error": str(e)}
        
        # 4. 清理模拟数据（如果存在）
        mock_cleanup = False
        for i, task in enumerate(mock_tasks):
            if task["task_id"] == task_id:
                mock_tasks.pop(i)
                mock_cleanup = True
                logger.info(f"🧹 Removed task {task_id} from mock data")
                break
        
        # 5. 记录任务为已删除状态（即使区块链取消失败）
        try:
            from services.collaboration_db_service import collaboration_db_service
            # 记录删除事件，即使区块链操作失败
            collaboration_db_service.record_blockchain_event(
                event_type="TaskDeleted",
                task_id=task_id,
                event_data={
                    "deleted_at": datetime.now().isoformat(),
                    "deleted_by": "system",
                    "blockchain_success": blockchain_result.get("success", False) if blockchain_result else False,
                    "reason": "Manual deletion"
                },
                transaction_hash=blockchain_result.get("transaction_hash") if blockchain_result and blockchain_result.get("success") else None
            )
            logger.info(f"📝 Recorded TaskDeleted event for task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to record deletion event: {e}")
        
        # 6. 构建删除结果
        deletion_result = {
            "success": True,
            "task_id": task_id,
            "deleted_at": datetime.now().isoformat(),
            "cleanup_summary": {
                "database_cleanup": cleanup_results,
                "blockchain_cancellation": blockchain_result,
                "mock_data_cleanup": mock_cleanup
            },
            "warnings": []
        }
        
        # 添加警告信息
        if blockchain_result and not blockchain_result.get("success"):
            deletion_result["warnings"].append("Failed to cancel task on blockchain")
        
        if cleanup_results.get("database_cleanup_error"):
            deletion_result["warnings"].append("Some database records may not have been cleaned up")
        
        # 添加区块链信息（如果成功）
        if blockchain_result and blockchain_result.get("success"):
            deletion_result["transaction_hash"] = blockchain_result.get("transaction_hash")
            deletion_result["block_number"] = blockchain_result.get("block_number")
            deletion_result["source"] = "blockchain"
        elif mock_cleanup:
            deletion_result["transaction_hash"] = f"0x{uuid.uuid4().hex}"
            deletion_result["source"] = "mock"
        
        logger.info(f"🎉 Task {task_id} deletion completed successfully")
        return deletion_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
                    
                    # 启动后台协作任务
                    asyncio.create_task(auto_execute_collaboration(task_id, task_info))
                    logger.info(f"🚀 Started background collaboration execution for task {task_id}")
                    
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

@router.post("/{task_id}/execute-collaboration", response_model=Dict[str, Any])
async def execute_assigned_task_collaboration(task_id: str):
    """
    为已分配的任务执行agents协作，使用真实的OpenAI API调用。
    这是第二步：在任务已经分配后，启动真实的AI协作。
    """
    try:
        logger.info(f"🚀 Starting collaboration execution for assigned task {task_id}")
        
        # 检查区块链连接
        connection_status = contract_service.get_connection_status()
        if not connection_status["connected"]:
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        # 获取任务信息
        task_result = contract_service.get_task(task_id)
        if not task_result["success"]:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_info = task_result
        
        # 检查任务状态 - 只有assigned状态的任务才能执行协作
        if task_info.get("status") != "assigned":
            raise HTTPException(
                status_code=400, 
                detail=f"Task must be in 'assigned' status to execute collaboration. Current status: {task_info.get('status')}"
            )
        
        # 检查是否已有分配的agents
        assigned_agents = task_info.get("assigned_agents", [])
        
        # 如果没有assigned_agents，但有assigned_agent，创建多agent测试环境
        if not assigned_agents and task_info.get("assigned_agent"):
            logger.info("No assigned_agents found, but task has assigned_agent. Creating multi-agent test environment...")
            
            # 获取所有可用agents进行模拟协作
            try:
                import requests
                logger.info("Fetching agents for collaboration setup...")
                agents_response = requests.get("http://localhost:8001/agents/", timeout=10)
                logger.info(f"Agents API response: {agents_response.status_code}")
                
                if agents_response.status_code == 200:
                    agents_data = agents_response.json()
                    available_agents = agents_data.get("agents", [])
                    logger.info(f"Found {len(available_agents)} available agents")
                    
                    # 选择合适的agents进行协作（包括已分配的agent）
                    primary_agent = task_info.get("assigned_agent")
                    task_capabilities = task_info.get("required_capabilities", [])
                    logger.info(f"Primary agent: {primary_agent}")
                    logger.info(f"Task capabilities: {task_capabilities}")
                    
                    # 构建协作团队
                    collaboration_agents = []
                    
                    # 首先添加主要分配的agent
                    for agent in available_agents:
                        if agent.get("agent_id") == primary_agent:
                            collaboration_agents.append({
                                "agent_id": agent["agent_id"],
                                "name": agent["name"],
                                "capabilities": agent.get("capabilities", []),
                                "reputation": agent.get("reputation", 50),
                                "role": "Primary"
                            })
                            logger.info(f"Added primary agent: {agent['name']}")
                            break
                    
                    # 然后基于任务需求添加额外的agents
                    for agent in available_agents:
                        if (len(collaboration_agents) < 4 and 
                            agent.get("agent_id") != primary_agent and
                            agent.get("active", True)):
                            
                            agent_caps = set(agent.get("capabilities", []))
                            task_caps = set(task_capabilities)
                            
                            # 如果agent有相关能力，加入协作
                            if agent_caps & task_caps or len(collaboration_agents) < 2:
                                collaboration_agents.append({
                                    "agent_id": agent["agent_id"],
                                    "name": agent["name"],
                                    "capabilities": agent.get("capabilities", []),
                                    "reputation": agent.get("reputation", 50),
                                    "role": "Collaborator"
                                })
                    
                    assigned_agents = collaboration_agents
                    logger.info(f"✅ Created test collaboration team with {len(assigned_agents)} agents")
                    for agent in assigned_agents:
                        logger.info(f"  - {agent['name']} ({agent['role']})")
                    
                else:
                    logger.error(f"Failed to get agents for collaboration setup: status {agents_response.status_code}")
                    logger.error(f"Response text: {agents_response.text[:200]}")
                    
            except Exception as e:
                logger.error(f"Error setting up collaboration team: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        # 如果仍然没有agents，抛出错误
        if not assigned_agents:
            raise HTTPException(status_code=400, detail="No agents assigned to this task and unable to create collaboration team")
        
        logger.info(f"📋 Found {len(assigned_agents)} assigned agents for task {task_id}")
        
        # 创建协作ID
        collaboration_id = f"collab_{task_id}_{int(datetime.now().timestamp())}"
        
        # 启动真实的AI协作
        logger.info(f"🤖 Starting real AI collaboration for task: {task_info.get('title', 'Unknown')}")
        collaboration_result = await collaboration_service.run_collaboration(collaboration_id, task_info)
        
        # 检查协作是否成功
        if collaboration_result.get("status") != "completed":
            logger.error(f"❌ Collaboration failed for task {task_id}: {collaboration_result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "task_id": task_id,
                "collaboration_id": collaboration_id,
                "error": f"Collaboration failed: {collaboration_result.get('error', 'Unknown error')}",
                "status": "failed"
            }
        
        # 协作成功，更新任务状态为completed
        logger.info(f"✅ Collaboration completed successfully! Updating task {task_id} to completed status")
        
        # 使用分配的代理地址而不是默认地址
        assigned_agent = task_info.get("assigned_agent")
        if not assigned_agent:
            assigned_agent = assigned_agents[0] if assigned_agents else get_sender_address()
        
        # 将task_id转换为bytes32格式
        task_id_bytes = bytes.fromhex(task_id)
        
        # 第一步：启动任务（assigned -> InProgress）
        logger.info(f"🔄 Starting task {task_id} (assigned -> InProgress)")
        start_result = contract_service.start_task(
            task_id=task_id_bytes,
            sender_address=assigned_agent
        )
        
        if not start_result["success"]:
            logger.error(f"❌ Failed to start task {task_id}: {start_result.get('error')}")
            return {
                "success": False,
                "task_id": task_id,
                "collaboration_id": collaboration_id,
                "error": f"Collaboration succeeded but failed to start task: {start_result.get('error')}",
                "status": "collaboration_completed_start_failed",
                "collaboration_result": {
                    "ipfs_cid": collaboration_result.get("ipfs_cid"),
                    "conversation_length": len(collaboration_result.get("conversation", [])),
                    "agents_count": len(assigned_agents),
                    "api_mode": "real"
                }
            }
        
        logger.info(f"✅ Task {task_id} started successfully! TX: {start_result['transaction_hash']}")
        
        # 第二步：完成任务（InProgress -> Completed）
        logger.info(f"🎯 Completing task {task_id} (InProgress -> Completed)")
        completion_result = contract_service.complete_task(
            task_id=task_id_bytes,
            result=collaboration_result.get('ipfs_cid', ''),
            sender_address=assigned_agent
        )
        
        if completion_result["success"]:
            logger.info(f"🎉 Task {task_id} completed successfully on blockchain! TX: {completion_result['transaction_hash']}")
            
            return {
                "success": True,
                "task_id": task_id,
                "collaboration_id": collaboration_id,
                "status": "completed",
                "collaboration_result": {
                    "ipfs_cid": collaboration_result.get("ipfs_cid"),
                    "conversation_length": len(collaboration_result.get("conversation", [])),
                    "agents_count": len(assigned_agents),
                    "api_mode": "real"
                },
                "blockchain_result": {
                    "start_transaction_hash": start_result["transaction_hash"],
                    "start_block_number": start_result["block_number"],
                    "completion_transaction_hash": completion_result["transaction_hash"],
                    "completion_block_number": completion_result["block_number"]
                },
                "message": "Task collaboration completed successfully and status updated to completed"
            }
        else:
            logger.error(f"❌ Failed to complete task {task_id} on blockchain: {completion_result.get('error')}")
            return {
                "success": False,
                "task_id": task_id,
                "collaboration_id": collaboration_id,
                "error": f"Collaboration succeeded but failed to update task status: {completion_result.get('error')}",
                "status": "collaboration_completed_blockchain_failed",
                "collaboration_result": {
                    "ipfs_cid": collaboration_result.get("ipfs_cid"),
                    "conversation_length": len(collaboration_result.get("conversation", [])),
                    "agents_count": len(assigned_agents),
                    "api_mode": "real"
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error executing collaboration for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute collaboration: {str(e)}")

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
    # 检查任务是否存在（先检查区块链，再检查mock数据）
    task_exists = False
    
    # 尝试从区块链获取任务
    try:
        task_result = contract_service.get_task(task_id)
        if task_result.get("success"):
            task_exists = True
    except Exception as e:
        logger.debug(f"Could not get task {task_id} from blockchain: {e}")
    
    # 如果区块链中没有，检查mock数据
    if not task_exists:
        for task in mock_tasks:
            if task["task_id"] == task_id:
                task_exists = True
                break
    
    if not task_exists:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 获取真实的区块链历史事件
    real_history = []
    
    # 首先尝试从区块链获取真实的任务历史
    try:
        if contract_service.w3 and contract_service.w3.is_connected():
            blockchain_history = contract_service.get_task_history(task_id)
            if blockchain_history.get("success") and blockchain_history.get("history"):
                for event in blockchain_history["history"]:
                    # 转换区块链事件格式为统一格式
                    timestamp = event.get('timestamp')
                    if isinstance(timestamp, int):
                        # 区块号格式，保持为区块号显示
                        timestamp_str = f"Block #{timestamp}"
                    else:
                        # 已经是时间戳格式
                        timestamp_str = str(timestamp)
                    
                    real_history.append({
                        "event": event.get("type", "unknown"),
                        "timestamp": timestamp_str,
                        "actor": event.get("details", {}).get("creator") or event.get("details", {}).get("agent") or "unknown",
                        "details": event.get("description", ""),
                        "blockchain_data": event.get("details", {})
                    })
                logger.info(f"✅ Retrieved {len(real_history)} real blockchain events for task {task_id}")
    except Exception as e:
        logger.warning(f"Could not get blockchain history for task {task_id}: {e}")
    
    # 如果没有区块链数据，使用基础mock数据作为fallback
    if not real_history:
        real_history = [
            {
                "event": "created",
                "timestamp": "2023-08-10T09:15:00Z", 
                "actor": "unknown",
                "details": "Task created (blockchain data not available)"
            }
        ]
    
    # 如果任务已完成，添加完成记录（如果区块链历史中没有的话）
    has_completion = any(event.get("event") == "task_completed" or event.get("event") == "completed" for event in real_history)
    
    if not has_completion:
        for task in mock_tasks:
            if task["task_id"] == task_id and task["status"] == "completed" and task.get("completed_at"):
                real_history.append({
                    "event": "completed",
                    "timestamp": task["completed_at"],
                    "actor": task.get("assigned_agent", "unknown"),
                    "details": f"Task completed with result: {task.get('result', 'No result provided')}"
                })
    
    # 添加真实的评价事件
    try:
        # 获取所有评价事件，然后过滤出当前任务的事件
        evaluation_events = collaboration_db_service.get_blockchain_events(
            event_type="task_evaluation", 
            limit=100  # 获取更多事件以确保包含相关的
        )
        
        for eval_event in evaluation_events:
            event_data = eval_event.get('data') or eval_event.get('event_data') or {}
            if isinstance(event_data, str):
                import json
                try:
                    event_data = json.loads(event_data)
                except:
                    event_data = {}
            
            # 只添加与当前任务相关的评价事件
            if event_data.get('task_id') == task_id:
                evaluator = event_data.get('evaluator', 'user')
                rating = event_data.get('rating', 'N/A')
                agent_id = eval_event.get('agent_id', 'unknown')
                timestamp = eval_event.get('timestamp')
                
                if timestamp:
                    timestamp_str = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
                else:
                    timestamp_str = eval_event.get('created_at', 'unknown')
                
                # 获取区块信息，如果没有则使用最新的区块号
                block_number = eval_event.get('block_number')
                transaction_hash = eval_event.get('transaction_hash', 'unknown')
                
                # 如果没有区块号，尝试获取当前最新区块号
                if not block_number or block_number == 'None':
                    try:
                        if contract_service.w3 and contract_service.w3.is_connected():
                            latest_block = contract_service.w3.eth.get_block('latest')
                            block_number = latest_block.number
                    except Exception as e:
                        # 如果获取失败，使用一个默认的高区块号确保评价事件排在后面
                        block_number = 999999
                
                real_history.append({
                    "event": "evaluated", 
                    "timestamp": f"Block #{block_number}",
                    "actor": agent_id,
                    "details": f"Task evaluated by {evaluator} with rating {rating}/5 for agent {agent_id[:10]}...",
                    "evaluation_data": {
                        "evaluator": evaluator,
                        "rating": rating,
                        "agent_id": agent_id,
                        "reward": event_data.get('reward', 0),
                        "reputation_change": event_data.get('reputation_change', 0)
                    },
                    "blockchain_data": {
                        "block_number": block_number,
                        "transaction_hash": transaction_hash
                    }
                })
        
        logger.info(f"Added {len(evaluation_events)} evaluation events to task {task_id} history")
        
    except Exception as e:
        logger.warning(f"Failed to get evaluation events for task {task_id}: {e}")
    
    # 按区块号和事件类型排序历史记录
    def sort_key(event):
        timestamp = event['timestamp']
        event_type = event['event']
        
        # 提取区块号
        if 'Block #' in str(timestamp):
            try:
                block_num = int(str(timestamp).replace('Block #', ''))
            except:
                block_num = 999999  # 无法解析的放到最后
        else:
            block_num = 999999  # 非区块格式的放到最后
        
        # 事件类型排序优先级（同一个区块内的排序）
        event_priority = {
            'task_created': 1,
            'collaboration_started': 2, 
            'task_assigned': 3,
            'task_completed': 4,
            'evaluated': 5  # 评价事件在完成事件之后
        }
        
        priority = event_priority.get(event_type, 6)
        
        return (block_num, priority)
    
    try:
        real_history.sort(key=sort_key)
    except Exception as e:
        logger.warning(f"Failed to sort history by block and event type: {e}")
    
    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "history": real_history,
            "total_events": len(real_history),
            "data_source": "blockchain + evaluation_events"
        }
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
        # 如果数据库没有查到任何对话，尝试用任务 result 字段（IPFS CID）拉取协作内容
        if not conversations_data:
            from services import contract_service
            task_result = contract_service.get_task(task_id)
            if task_result.get("success"):
                result_cid = task_result.get("result")
                if result_cid and result_cid.startswith("Qm"):
                    # 尝试从 IPFS 拉取协作内容
                    from services.agent_collaboration_service import agent_collaboration_service
                    ipfs_data = await agent_collaboration_service.get_conversation_from_ipfs(result_cid)
                    if ipfs_data and "conversation" in ipfs_data:
                        # 组装 conversations_data
                        conversations_data.append({
                            "id": result_cid,
                            "conversation_id": result_cid,
                            "status": "completed",
                            "participants": ipfs_data.get("agents", []),
                            "created_at": None,
                            "completed_at": None,
                            "message_count": len(ipfs_data.get("conversation", []))
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
    智能分配任务给最合适的代理并自动启动协作
    """
    try:
        if collaborative:
            result = await agent_selection_service.auto_assign_collaborative_task(task_id, max_agents)
        else:
            result = await agent_selection_service.auto_assign_task(task_id)
            
        if result.get("success"):
            # 更新任务状态为assigned并记录到区块链
            try:
                logger.info(f"Updating task {task_id} status to assigned and recording on blockchain")
                
                # 获取选中的代理
                selected_agents = result.get("selected_agents", [])
                if not selected_agents:
                    raise Exception("No agents were selected")
                
                # 获取主要代理（通常是第一个或协调者）
                primary_agent = selected_agents[0]
                agent_address = primary_agent.get("agent_id")
                
                if not agent_address:
                    # 如果agent_id为空，从agents API获取第一个可用的agent
                    try:
                        import requests
                        agents_response = requests.get("http://localhost:8001/agents/", timeout=10)
                        if agents_response.status_code == 200:
                            agents_data = agents_response.json()
                            agents_list = agents_data.get("agents", [])
                            # 选择第一个active agent
                            for agent in agents_list:
                                if agent.get("active", True) and agent.get("agent_id"):
                                    agent_address = agent["agent_id"]
                                    logger.info(f"Using fallback agent: {agent_address} ({agent.get('name', 'Unknown')})")
                                    break
                    except Exception as e:
                        logger.error(f"Error getting fallback agent: {str(e)}")
                
                if not agent_address:
                    raise Exception("No valid agent address found for assignment")
                
                # 更新区块链上的任务状态
                connection_status = contract_service.get_connection_status()
                blockchain_updated = False
                
                if connection_status["connected"]:
                    try:
                        sender_address = get_sender_address()
                        
                        # 如果是协作任务，先启动collaboration（在任务还是Open状态时）
                        logger.info(f"Checking collaboration condition: selected_agents count = {len(selected_agents)}")
                        if len(selected_agents) > 1:
                            try:
                                # 生成协作ID
                                collaboration_id = f"collab_{task_id}_{uuid.uuid4().hex[:8]}"
                                
                                # 获取所有选中代理的地址
                                selected_agent_addresses = [
                                    agent.get("agent_id") or f"0x{i:040x}" 
                                    for i, agent in enumerate(selected_agents, 1)
                                ]
                                
                                logger.info(f"Starting agent collaboration before task assignment...")
                                # 启动agent collaboration（任务仍在Open状态）
                                collab_result = contract_service.start_agent_collaboration(
                                    task_id, 
                                    selected_agent_addresses, 
                                    collaboration_id,
                                    sender_address
                                )
                                
                                if collab_result.get("success"):
                                    logger.info(f"Agent collaboration started for task {task_id}, collaboration_id: {collaboration_id}")
                                    result["collaboration_id"] = collaboration_id
                                    result["collaboration_transaction"] = collab_result.get("transaction_hash")
                                else:
                                    logger.warning(f"Failed to start agent collaboration: {collab_result.get('error')}")
                                    
                            except Exception as e:
                                logger.error(f"Error starting agent collaboration: {str(e)}")
                        
                        # 然后分配任务到区块链
                        assign_result = contract_service.assign_task(task_id, agent_address, sender_address)
                        if assign_result.get("success"):
                            blockchain_updated = True
                            logger.info(f"Task {task_id} successfully assigned to {agent_address} on blockchain")
                            result["transaction_hash"] = assign_result.get("transaction_hash")
                        else:
                            logger.warning(f"Failed to assign task on blockchain: {assign_result.get('error')}")
                    except Exception as e:
                        logger.error(f"Error assigning task on blockchain: {str(e)}")
                
                # 更新mock数据中的任务状态
                logger.info(f"Updating mock data for task {task_id}")
                for task in mock_tasks:
                    if task["task_id"] == task_id:
                        task["status"] = "assigned"
                        task["assigned_agent"] = agent_address
                        task["assigned_at"] = datetime.now().isoformat()
                        task["assigned_agents"] = [
                            {
                                "agent_id": agent.get("agent_id") or f"0x{i:040x}",
                                "name": agent.get("name"),
                                "role": agent.get("role"),
                                "capabilities": agent.get("capabilities", []),
                                "reputation": agent.get("reputation", 0),
                                "match_score": agent.get("match_score", 0)
                            }
                            for i, agent in enumerate(selected_agents, 1)
                        ]
                        logger.info(f"Updated task {task_id} status to assigned with {len(selected_agents)} agents")
                        break
                
                # 更新结果消息
                result["status"] = "assigned"
                result["assigned_agent"] = agent_address
                result["assigned_agents"] = selected_agents
                result["blockchain_updated"] = blockchain_updated
                result["collaboration_status"] = "assigned"
                result["message"] = f"Task successfully assigned to {len(selected_agents)} agent(s). Collaboration will begin shortly."
                
            except Exception as e:
                logger.error(f"Error starting automatic collaboration for smart-assigned task: {str(e)}")
                result["collaboration_status"] = "failed"
                result["message"] = "Task smart-assigned successfully, but failed to start collaboration."
            
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

# Learning Dashboard Endpoints

@router.get("/agents/{agent_id}/learning-events", response_model=Dict[str, Any])
async def get_agent_learning_events(agent_id: str, limit: int = Query(50, ge=1, le=100)):
    """
    获取agent的学习事件（来自任务评估系统）
    """
    try:
        # 尝试从数据库获取学习事件
        learning_events = collaboration_db_service.get_agent_learning_events(agent_id, limit)
        
        if learning_events:
            return {
                "success": True,
                "agent_id": agent_id,
                "learning_events": learning_events,
                "total": len(learning_events),
                "source": "database"
            }
        else:
            # 如果数据库没有数据，返回空列表
            logger.info(f"No learning events found for agent {agent_id}")
            return {
                "success": True,
                "agent_id": agent_id,
                "learning_events": [],
                "total": 0,
                "source": "database"
            }
            
    except Exception as e:
        logger.error(f"Error getting learning events for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/agent-statistics", response_model=Dict[str, Any])
async def get_agent_learning_statistics():
    """
    获取所有agent的学习统计数据（用于Learning Dashboard）
    """
    try:
        # 获取所有agents
        agents_result = contract_service.get_all_agents()
        if not agents_result.get("success"):
            logger.error(f"Failed to get agents from blockchain: {agents_result.get('error')}")
            raise HTTPException(status_code=503, detail="Blockchain service unavailable")
        
        agents = agents_result.get("agents", [])
        learning_statistics = []
        
        # 为每个agent获取学习统计数据
        for agent in agents:
            agent_id = agent.get("agent_id") or agent.get("address")
            if not agent_id:
                continue
            
            try:
                # 获取agent的学习事件
                learning_events = collaboration_db_service.get_agent_learning_events(agent_id, 20)
                
                # 计算统计数据
                recent_evaluations = len([e for e in learning_events if e.get("event_type") == "task_evaluation"])
                successful_evaluations = len([e for e in learning_events 
                                           if e.get("event_type") == "task_evaluation" 
                                           and e.get("data", {}).get("success", False)])
                
                # 从区块链数据获取基础信息，结合学习事件更新
                reputation = agent.get("reputation", 0)
                tasks_completed = agent.get("tasks_completed", 0)
                average_score = agent.get("average_score", 0)
                average_reward = agent.get("average_reward", 0)
                
                # 基于学习事件计算改进
                for event in learning_events:
                    if event.get("event_type") == "task_evaluation":
                        event_data = event.get("data", {})
                        if event_data.get("reputation_change"):
                            reputation += event_data.get("reputation_change", 0)
                        if event_data.get("reward"):
                            average_reward = (average_reward + event_data.get("reward", 0)) / 2
                
                # Calculate confidence factor and risk tolerance based on performance
                confidence_factor = min(100, max(10, reputation + (successful_evaluations * 2) - (recent_evaluations - successful_evaluations) * 3))
                risk_tolerance = min(100, max(20, reputation - 20 + (successful_evaluations * 1.5)))
                
                agent_stats = {
                    "agent_id": agent_id,
                    "agent_name": agent.get("name", f"Agent-{agent_id[-4:]}"),
                    "reputation": max(0, min(100, reputation)),  # 限制在0-100范围内
                    "confidence_factor": int(confidence_factor),
                    "risk_tolerance": int(risk_tolerance),
                    "average_score": average_score,
                    "average_reward": average_reward,
                    "tasks_completed": tasks_completed,
                    "success_rate": (successful_evaluations / max(recent_evaluations, 1) * 100) if recent_evaluations > 0 else 0,
                    "recent_evaluations": recent_evaluations,
                    "successful_evaluations": successful_evaluations,
                    "failed_evaluations": recent_evaluations - successful_evaluations,
                    "learning_velocity": len(learning_events) / 30,  # 最近30天的学习速度
                    "performance_trend": "improving" if successful_evaluations > recent_evaluations * 0.7 else "stable",
                    "last_evaluation": learning_events[0].get("timestamp") if learning_events else None,
                    "total_learning_events": len(learning_events),
                    "source": "evaluation_system"
                }
                
                learning_statistics.append(agent_stats)
                
            except Exception as e:
                logger.error(f"Error processing learning statistics for agent {agent_id}: {str(e)}")
                continue
        
        # 计算总体摘要
        if learning_statistics:
            summary = {
                "total_agents": len(learning_statistics),
                "avg_reputation": sum(a["reputation"] for a in learning_statistics) / len(learning_statistics),
                "avg_success_rate": sum(a["success_rate"] for a in learning_statistics) / len(learning_statistics),
                "total_evaluations": sum(a["recent_evaluations"] for a in learning_statistics),
                "total_learning_events": sum(a["total_learning_events"] for a in learning_statistics),
                "performance_distribution": {
                    "improving": len([a for a in learning_statistics if a["performance_trend"] == "improving"]),
                    "stable": len([a for a in learning_statistics if a["performance_trend"] == "stable"]),
                    "declining": len([a for a in learning_statistics if a["performance_trend"] == "declining"])
                }
            }
        else:
            # 如果没有学习数据，返回空统计
            summary = {
                "total_agents": 0,
                "avg_reputation": 0,
                "avg_success_rate": 0,
                "total_evaluations": 0,
                "total_learning_events": 0,
                "performance_distribution": {
                    "improving": 0,
                    "stable": 0,
                    "declining": 0
                }
            }
            return {
                "success": True,
                "data": {
                    "agents": [],
                    "summary": summary,
                    "timestamp": datetime.now().isoformat(),
                    "source": "blockchain"
                }
            }
        
        return {
            "success": True,
            "data": {
                "agents": learning_statistics,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "source": "evaluation_system"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent learning statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning statistics: {str(e)}")

@router.get("/events/cancelled", response_model=Dict[str, Any])
async def get_cancelled_task_events(
    limit: int = Query(default=50, description="Number of events to return"),
    offset: int = Query(default=0, description="Number of events to skip"),
    task_id: Optional[str] = Query(default=None, description="Filter by specific task ID"),
    actor: Optional[str] = Query(default=None, description="Filter by actor who cancelled the task")
):
    """
    获取TaskCancelled事件的专用API。
    返回已删除/取消的任务事件列表，方便前端跟踪。
    """
    try:
        # 获取TaskCancelled事件
        cancelled_events = collaboration_db_service.get_blockchain_events(
            event_type="TaskCancelled",
            limit=limit,
            offset=offset,
            task_id=task_id
        )
        
        # 处理事件数据
        processed_events = []
        for event in cancelled_events:
            try:
                # 解析事件参数
                event_data = event.get('event_data', {})
                
                # 提取关键信息
                processed_event = {
                    "id": event.get("id"),
                    "task_id": event.get("task_id"),
                    "transaction_hash": event.get("transaction_hash"),
                    "block_number": event.get("block_number"),
                    "timestamp": event.get("timestamp"),
                    "actor": event_data.get("actor"),
                    "reason": event_data.get("reason", "Task cancelled"),
                    "event_timestamp": event_data.get("timestamp"),
                    "created_at": event.get("created_at"),
                    "raw_event": event  # 包含完整的原始事件数据
                }
                
                # 如果有actor过滤器，应用过滤
                if actor and processed_event.get("actor") != actor:
                    continue
                    
                processed_events.append(processed_event)
                
            except Exception as e:
                logger.warning(f"Failed to process cancelled event {event.get('id')}: {e}")
                continue
        
        # 统计信息
        total_cancelled = len(processed_events)
        
        # 如果没有提供特定的task_id，获取总数统计
        if not task_id:
            try:
                all_cancelled_events = collaboration_db_service.get_blockchain_events(
                    event_type="TaskCancelled",
                    limit=1000,  # 获取更多数据用于统计
                    offset=0
                )
                total_cancelled = len(all_cancelled_events)
            except Exception as e:
                logger.warning(f"Failed to get total cancelled events count: {e}")
        
        return {
            "success": True,
            "data": {
                "events": processed_events,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_cancelled,
                    "has_more": total_cancelled > offset + len(processed_events)
                },
                "filters": {
                    "task_id": task_id,
                    "actor": actor
                },
                "summary": {
                    "total_cancelled_tasks": total_cancelled,
                    "events_returned": len(processed_events)
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting cancelled task events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cancelled events: {str(e)}")

@router.get("/agents/{agent_id}/history", response_model=Dict[str, Any])
async def get_agent_history(agent_id: str, days: int = Query(180, ge=30, le=365)):
    """
    获取agent的历史数据用于图表展示
    """
    try:
        from datetime import datetime, timedelta
        import calendar
        
        # 获取学习事件用于构建历史趋势
        learning_events = collaboration_db_service.get_agent_learning_events(agent_id, 100)
        
        # 获取当前agent信息，优先使用评价系统的真实数据
        agent_result = contract_service.get_agent(agent_id)
        current_reputation = 50
        current_tasks = 0
        
        # 从评价系统获取真实的任务完成数据
        try:
            # 直接从数据库获取学习事件数量作为任务完成数
            current_tasks = len(learning_events) if learning_events else 0
            logger.info(f"Using learning events count as tasks completed for {agent_id}: {current_tasks}")
        except Exception as e:
            logger.warning(f"Failed to get learning events count: {e}")
        
        # 获取区块链声誉数据
        if agent_result and agent_result.get("success"):
            agent_data = agent_result.get("agent", {})
            current_reputation = agent_data.get("reputation", 50)
            
            # 根据学习事件计算最新声誉（加上所有声誉变化）
            if learning_events:
                total_reputation_change = sum(event['data'].get('reputation_change', 0) for event in learning_events)
                current_reputation = current_reputation + total_reputation_change
        
        # 简化版本：基于学习事件生成历史数据，避免复杂的日期处理
        logger.info(f"Generating history for {agent_id} with {len(learning_events)} events")
        
        # 生成简单的时间序列
        now = datetime.now()
        dates = []
        reputation_history = []
        tasks_history = []
        scores_history = []
        rewards_history = []
        
        # 最近6个时间点
        for i in range(6):
            days_ago = 5 - i
            date_obj = now - timedelta(days=days_ago)
            dates.append(date_obj.strftime('%m/%d'))
            
            # 简单的历史逻辑：只在最后一天显示学习事件的影响
            if i == 5:  # 最后一天（今天）
                reputation_history.append(current_reputation)
                tasks_history.append(current_tasks)
            else:
                # 之前的天数，显示逐步增长
                base_reputation = max(10, current_reputation - 5)
                reputation_history.append(base_reputation + i)
                tasks_history.append(int(current_tasks * i / 5))
            
            # 基于声誉计算其他指标
            rep = reputation_history[i]
            scores_history.append(min(100, max(50, rep + 15)))
            rewards_history.append(round(max(0.1, rep * 0.02), 2))
        
        history_data = {
            "agent_id": agent_id,
            "period_days": days,
            "history": {
                "dates": dates,
                "reputation": reputation_history,
                "tasks_completed": tasks_history,
                "average_scores": scores_history,
                "rewards": rewards_history
            },
            "summary": {
                "reputation_change": reputation_history[-1] - reputation_history[0],
                "tasks_growth": tasks_history[-1] - tasks_history[0],
                "score_trend": "improving" if scores_history[-1] > scores_history[0] else "stable",
                "reward_trend": "increasing" if rewards_history[-1] > rewards_history[0] else "stable"
            },
            "source": "calculated_from_events"
        }
        
        return {
            "success": True,
            "data": history_data
        }
        
    except Exception as e:
        logger.error(f"Error getting agent history for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/task-types", response_model=Dict[str, Any])
async def get_agent_task_types(agent_id: str):
    """
    获取agent的任务类型分布数据
    """
    try:
        # 获取agent的能力信息
        agent_result = contract_service.get_agent(agent_id)
        
        if not agent_result or not agent_result.get("success"):
            # 如果无法获取agent信息，返回默认分布
            default_distribution = {
                "data_analysis": 5,
                "text_generation": 3, 
                "classification": 2,
                "translation": 1,
                "summarization": 1
            }
            
            return {
                "success": True,
                "agent_id": agent_id,
                "task_types": default_distribution,
                "total_tasks": sum(default_distribution.values()),
                "source": "default"
            }
        
        agent_data = agent_result.get("agent", {})
        capabilities = agent_data.get("capabilities", [])
        capability_weights = agent_data.get("capability_weights", [])
        total_tasks = agent_data.get("tasks_completed", 0)
        
        # 基于能力权重分配任务类型
        task_distribution = {}
        
        # 标准化能力映射
        capability_map = {
            "data_analysis": ["data_analysis", "analysis", "analytics"],
            "text_generation": ["text_generation", "generation", "nlp"],
            "classification": ["classification", "categorization"], 
            "translation": ["translation", "language"],
            "summarization": ["summarization", "summary"]
        }
        
        # 计算每种任务类型的分配
        total_weight = sum(capability_weights) if capability_weights else len(capabilities)
        
        for i, capability in enumerate(capabilities):
            weight = capability_weights[i] if i < len(capability_weights) else 50
            
            # 映射到标准任务类型
            mapped_type = None
            for task_type, aliases in capability_map.items():
                if capability.lower() in aliases:
                    mapped_type = task_type
                    break
            
            if not mapped_type:
                mapped_type = capability  # 使用原始能力名称
            
            # 基于权重分配任务数量
            if total_weight > 0:
                task_count = max(1, int((weight / total_weight) * total_tasks))
            else:
                task_count = max(1, total_tasks // len(capabilities))
                
            task_distribution[mapped_type] = task_distribution.get(mapped_type, 0) + task_count
        
        # 确保至少有一些基础任务类型
        if not task_distribution:
            task_distribution = {
                "data_analysis": max(1, total_tasks // 2),
                "text_generation": max(1, total_tasks // 3),
                "classification": max(1, total_tasks // 4)
            }
        
        return {
            "success": True,
            "agent_id": agent_id,
            "task_types": task_distribution,
            "total_tasks": sum(task_distribution.values()),
            "capabilities": capabilities,
            "capability_weights": capability_weights,
            "source": "blockchain_calculated"
        }
        
    except Exception as e:
        logger.error(f"Error getting task types for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

