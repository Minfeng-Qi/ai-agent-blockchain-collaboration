"""
Collaboration API Router for Agent Learning System
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import time
import uuid
from services.agent_collaboration_service import agent_collaboration_service

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    tags=["collaboration"],
    responses={404: {"description": "Not found"}},
)

# 模型定义
class AgentInfo(BaseModel):
    agent_id: str
    name: Optional[str] = None
    capabilities: List[str] = []
    reputation: Optional[float] = None

class TaskData(BaseModel):
    task_id: str
    title: str
    description: str
    type: Optional[str] = None
    requirements: Optional[str] = None
    reward: Optional[float] = None
    deadline: Optional[str] = None

class CollaborationRequest(BaseModel):
    task_data: TaskData

class CollaborationResponse(BaseModel):
    collaboration_id: str
    task_id: str
    status: str
    created_at: float = Field(default_factory=time.time)

class ConversationMessage(BaseModel):
    role: str
    content: str

class ConversationResponse(BaseModel):
    collaboration_id: str
    task_id: str
    task_title: str
    status: Optional[str] = None
    agents: List[Dict[str, Any]]
    conversation: List[ConversationMessage]
    ipfs_cid: str
    ipfs_url: str
    tx_hash: Optional[str] = None
    timestamp: float
    agent_updates: Optional[List[Dict[str, Any]]] = None

# API路由
@router.post("/", response_model=CollaborationResponse)
async def create_collaboration(request: CollaborationRequest):
    """创建一个新的代理协作"""
    try:
        collaboration_id = await agent_collaboration_service.create_collaboration(
            request.task_data.task_id,
            request.task_data.dict()
        )
        
        return {
            "collaboration_id": collaboration_id,
            "task_id": request.task_data.task_id,
            "status": "created",
            "created_at": time.time()
        }
    except Exception as e:
        logger.error(f"Error creating collaboration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collaboration_id}/run", response_model=ConversationResponse)
async def run_collaboration(
    collaboration_id: str,
    request: CollaborationRequest
):
    """运行代理协作"""
    try:
        result = await agent_collaboration_service.run_collaboration(
            collaboration_id,
            request.task_data.dict()
        )
        return result
    except Exception as e:
        logger.error(f"Error running collaboration {collaboration_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collaboration_id}", response_model=CollaborationResponse)
async def get_collaboration(collaboration_id: str):
    """获取协作详情"""
    try:
        collaboration = await agent_collaboration_service.get_collaboration(collaboration_id)
        return collaboration
    except Exception as e:
        logger.error(f"Error getting collaboration {collaboration_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Collaboration {collaboration_id} not found")

@router.get("/{collaboration_id}/conversation", response_model=ConversationResponse)
async def get_conversation(collaboration_id: str):
    """获取协作对话记录"""
    try:
        # 先获取协作详情
        collaboration = await agent_collaboration_service.get_collaboration(collaboration_id)
        
        # 从IPFS获取对话记录
        if "ipfs_cid" in collaboration and collaboration["ipfs_cid"]:
            conversation_data = await agent_collaboration_service.get_conversation_from_ipfs(collaboration["ipfs_cid"])
            return conversation_data
        else:
            raise HTTPException(status_code=404, detail=f"Conversation for collaboration {collaboration_id} not found")
    except Exception as e:
        logger.error(f"Error getting conversation for collaboration {collaboration_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ipfs/{ipfs_cid}")
async def get_conversation_by_ipfs(ipfs_cid: str):
    """通过IPFS CID获取对话记录"""
    try:
        conversation_data = await agent_collaboration_service.get_conversation_from_ipfs(ipfs_cid)
        logger.info(f"Retrieved conversation data for IPFS CID {ipfs_cid}")
        return conversation_data
    except Exception as e:
        logger.error(f"Error getting conversation from IPFS {ipfs_cid}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-openai")
async def test_openai_connection():
    """测试OpenAI API连接"""
    try:
        # 测试OpenAI客户端状态
        service_status = {
            "openai_client_available": agent_collaboration_service.openai_client is not None,
            "mock_mode": agent_collaboration_service.mock_mode,
            "api_key_configured": bool(agent_collaboration_service.api_key),
            "api_key_length": len(agent_collaboration_service.api_key) if agent_collaboration_service.api_key else 0
        }
        
        # 如果有真实API客户端，进行简单测试
        if agent_collaboration_service.openai_client and not agent_collaboration_service.mock_mode:
            try:
                test_response = await agent_collaboration_service._call_openai_api([
                    {"role": "user", "content": "Say 'OpenAI API connection successful' if you can read this."}
                ])
                service_status["openai_test_result"] = test_response[:100] + "..." if len(test_response) > 100 else test_response
                service_status["openai_test_success"] = True
            except Exception as e:
                service_status["openai_test_result"] = f"Error: {str(e)}"
                service_status["openai_test_success"] = False
        
        return service_status
    except Exception as e:
        logger.error(f"Error testing OpenAI connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))