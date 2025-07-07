from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel

from backend.services import contract_service

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# Models
class LearningEventBase(BaseModel):
    agent_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None

class LearningEventCreate(LearningEventBase):
    pass

class LearningEvent(LearningEventBase):
    event_id: str
    transaction_hash: Optional[str] = None

# Mock data for development
mock_learning_events = [
    {
        "event_id": "event_001",
        "agent_id": "0x1234567890123456789012345678901234567890",
        "event_type": "task_completion",
        "data": {
            "task_id": "task_123",
            "performance_score": 4.8,
            "insights_gained": ["market trend analysis improved", "sentiment detection enhanced"]
        },
        "timestamp": "2023-08-10T09:15:00Z",
        "transaction_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"
    },
    {
        "event_id": "event_002",
        "agent_id": "0x2345678901234567890123456789012345678901",
        "event_type": "training",
        "data": {
            "model_version": "v2.1",
            "training_duration": 3600,
            "performance_improvement": 0.15
        },
        "timestamp": "2023-08-11T14:22:00Z",
        "transaction_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678"
    },
    {
        "event_id": "event_003",
        "agent_id": "0x3456789012345678901234567890123456789012",
        "event_type": "capability_acquisition",
        "data": {
            "capability": "image_recognition",
            "source": "marketplace",
            "cost": 0.25
        },
        "timestamp": "2023-08-09T11:45:00Z",
        "transaction_hash": "0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012"
    }
]

@router.get("/", response_model=Dict[str, Any])
async def get_learning_events(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get a list of learning events with optional filtering.
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["learning"]:
        try:
            events = []
            
            if agent_id:
                # 从区块链获取特定代理的学习事件
                result = contract_service.get_learning_events(agent_id)
                if result["success"]:
                    events = result["events"]
                    
                    # 应用事件类型过滤
                    if event_type:
                        events = [e for e in events if e["event_type"] == event_type]
            else:
                # 获取所有代理的学习事件
                # 注意：这个可能需要在contract_service中实现一个新方法
                # 暂时使用模拟数据
                events = mock_learning_events
                if event_type:
                    events = [e for e in events if e["event_type"] == event_type]
            
            # 应用分页
            total = len(events)
            paginated_events = events[offset:offset + limit]
            
            return {
                "events": paginated_events,
                "total": total,
                "limit": limit,
                "offset": offset,
                "source": "blockchain"
            }
        except Exception as e:
            logger.error(f"Error getting learning events from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    filtered_events = mock_learning_events
    
    if agent_id:
        filtered_events = [e for e in filtered_events if e["agent_id"] == agent_id]
    
    if event_type:
        filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
    
    # 应用分页
    paginated_events = filtered_events[offset:offset + limit]
    
    return {
        "events": paginated_events,
        "total": len(filtered_events),
        "limit": limit,
        "offset": offset,
        "source": "mock"
    }

@router.get("/{event_id}", response_model=Dict[str, Any])
async def get_learning_event(event_id: str):
    """
    Get details of a specific learning event.
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["learning"]:
        try:
            # 从区块链获取学习事件
            # 注意：这个方法需要在contract_service中实现
            # result = contract_service.get_learning_event(event_id)
            # if result["success"]:
            #     return {
            #         **result,
            #         "source": "blockchain"
            #     }
            # else:
            #     logger.warning(f"Failed to get learning event {event_id} from blockchain: {result.get('error')}")
            pass
        except Exception as e:
            logger.error(f"Error getting learning event {event_id} from blockchain: {str(e)}")
    
    # 如果区块链未连接或获取失败，使用模拟数据
    for event in mock_learning_events:
        if event["event_id"] == event_id:
            return {
                **event,
                "source": "mock"
            }
    
    raise HTTPException(status_code=404, detail="Learning event not found")

@router.post("/", response_model=Dict[str, Any])
async def create_learning_event(event: LearningEventCreate = Body(...)):
    """
    Record a new learning event.
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if connection_status["connected"] and connection_status["contracts"]["learning"]:
        try:
            # 获取发送者地址（在实际应用中，这可能来自认证系统）
            sender_address = "0x9876543210987654321098765432109876543210"  # 示例地址
            
            # 准备数据
            event_data = str(event.data)  # 将数据转换为字符串
            
            # 调用合约服务记录学习事件
            result = contract_service.record_learning_event(
                event.agent_id,
                event.event_type,
                event_data,
                sender_address
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "event_id": result["event_id"],
                    "transaction_hash": result["transaction_hash"],
                    "block_number": result["block_number"],
                    "timestamp": event.timestamp or datetime.now().isoformat(),
                    "source": "blockchain"
                }
            else:
                logger.warning(f"Failed to record learning event on blockchain: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error recording learning event on blockchain: {str(e)}")
    
    # 如果区块链未连接或记录失败，使用模拟数据
    try:
        new_event_id = f"event_{str(uuid.uuid4())[:8]}"
        transaction_hash = f"0x{uuid.uuid4().hex}"
        
        new_event = {
            "event_id": new_event_id,
            "agent_id": event.agent_id,
            "event_type": event.event_type,
            "data": event.data,
            "timestamp": event.timestamp or datetime.now().isoformat(),
            "transaction_hash": transaction_hash
        }
        
        mock_learning_events.append(new_event)
        
        return {
            "success": True,
            "event_id": new_event_id,
            "transaction_hash": transaction_hash,
            "timestamp": new_event["timestamp"],
            "source": "mock"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create learning event: {str(e)}")

@router.get("/agent/{agent_id}/progress", response_model=Dict[str, Any])
async def get_agent_learning_progress(agent_id: str):
    """
    Get the learning progress of a specific agent.
    """
    # 检查代理是否存在
    agent_exists = False
    for event in mock_learning_events:
        if event["agent_id"] == agent_id:
            agent_exists = True
            break
    
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 获取代理的学习事件
    agent_events = [e for e in mock_learning_events if e["agent_id"] == agent_id]
    
    # 分析学习进度
    task_completions = [e for e in agent_events if e["event_type"] == "task_completion"]
    trainings = [e for e in agent_events if e["event_type"] == "training"]
    capability_acquisitions = [e for e in agent_events if e["event_type"] == "capability_acquisition"]
    
    # 计算平均性能分数
    avg_performance = 0
    if task_completions:
        performance_scores = [e["data"].get("performance_score", 0) for e in task_completions if "performance_score" in e["data"]]
        if performance_scores:
            avg_performance = sum(performance_scores) / len(performance_scores)
    
    # 获取已获得的能力
    acquired_capabilities = []
    for event in capability_acquisitions:
        if "capability" in event["data"]:
            acquired_capabilities.append(event["data"]["capability"])
    
    # 计算总体学习进度（示例算法）
    progress = min(100, (len(task_completions) * 5 + len(trainings) * 10 + len(capability_acquisitions) * 15))
    
    return {
        "agent_id": agent_id,
        "progress": progress,
        "task_completions": len(task_completions),
        "trainings": len(trainings),
        "capability_acquisitions": len(capability_acquisitions),
        "acquired_capabilities": acquired_capabilities,
        "avg_performance": avg_performance,
        "total_events": len(agent_events),
        "last_event": agent_events[-1]["timestamp"] if agent_events else None
    }

@router.get("/insights", response_model=Dict[str, Any])
async def get_learning_insights():
    """
    Get insights from learning events across all agents.
    """
    # 分析所有学习事件
    task_completions = [e for e in mock_learning_events if e["event_type"] == "task_completion"]
    trainings = [e for e in mock_learning_events if e["event_type"] == "training"]
    capability_acquisitions = [e for e in mock_learning_events if e["event_type"] == "capability_acquisition"]
    
    # 按代理分组
    agents = {}
    for event in mock_learning_events:
        agent_id = event["agent_id"]
        if agent_id not in agents:
            agents[agent_id] = {
                "task_completions": 0,
                "trainings": 0,
                "capability_acquisitions": 0,
                "performance_scores": []
            }
        
        if event["event_type"] == "task_completion":
            agents[agent_id]["task_completions"] += 1
            if "performance_score" in event["data"]:
                agents[agent_id]["performance_scores"].append(event["data"]["performance_score"])
        elif event["event_type"] == "training":
            agents[agent_id]["trainings"] += 1
        elif event["event_type"] == "capability_acquisition":
            agents[agent_id]["capability_acquisitions"] += 1
    
    # 计算每个代理的平均性能
    for agent_id, data in agents.items():
        if data["performance_scores"]:
            data["avg_performance"] = sum(data["performance_scores"]) / len(data["performance_scores"])
        else:
            data["avg_performance"] = 0
        del data["performance_scores"]
    
    # 获取最常获取的能力
    capability_counts = {}
    for event in capability_acquisitions:
        if "capability" in event["data"]:
            capability = event["data"]["capability"]
            capability_counts[capability] = capability_counts.get(capability, 0) + 1
    
    top_capabilities = sorted(capability_counts.items(), key=lambda x: x[1], reverse=True)
    
    # 获取性能最高的代理
    top_agents = sorted(
        [(agent_id, data["avg_performance"]) for agent_id, data in agents.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        "total_events": len(mock_learning_events),
        "event_types": {
            "task_completion": len(task_completions),
            "training": len(trainings),
            "capability_acquisition": len(capability_acquisitions)
        },
        "agent_count": len(agents),
        "top_performing_agents": top_agents[:3],
        "top_capabilities": top_capabilities[:5],
        "agents": agents
    }