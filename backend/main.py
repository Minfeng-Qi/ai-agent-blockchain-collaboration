"""
Agent Learning System API
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from backend.routers import agents, tasks, learning, blockchain, analytics  # collaboration temporarily disabled
from backend.services import contract_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("backend")

# 创建FastAPI应用
app = FastAPI(
    title="Agent Learning System API",
    description="API for managing AI agents, tasks, and learning events",
    version="1.0.0"
)

# 配置CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(agents, prefix="/agents", tags=["agents"])
app.include_router(tasks, prefix="/tasks", tags=["tasks"])
app.include_router(learning, prefix="/learning", tags=["learning"])
app.include_router(blockchain, prefix="/blockchain", tags=["blockchain"])
# app.include_router(collaboration, prefix="/collaboration", tags=["collaboration"])  # Temporarily disabled
app.include_router(analytics, prefix="/analytics", tags=["analytics"])

# 自定义OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Agent Learning System API",
        version="1.0.0",
        description="API for managing AI agents, tasks, and learning events on the blockchain",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
async def root():
    """
    检查API状态。
    """
    return {
        "status": "ok",
        "message": "Agent Learning System API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    检查API和区块链服务的健康状态。
    """
    blockchain_status = contract_service.get_connection_status()
    
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "blockchain": "up" if blockchain_status["connected"] else "down"
        },
        "blockchain_details": blockchain_status
    }

@app.get("/stats")
async def system_stats():
    """
    获取系统统计数据。
    """
    try:
        # 从 backend.routers 模块导入模拟数据
        from backend.routers.agents import mock_agents
        from backend.routers.tasks import mock_tasks
        from backend.routers.learning import mock_learning_events
        from backend.routers.blockchain import mock_transactions, mock_blocks
        
        # 获取代理统计数据
        agent_count = len(mock_agents)
        
        # 获取任务统计数据
        task_count = len(mock_tasks)
        open_tasks = len([t for t in mock_tasks if t["status"] == "open"])
        assigned_tasks = len([t for t in mock_tasks if t["status"] == "assigned"])
        completed_tasks = len([t for t in mock_tasks if t["status"] == "completed"])
        
        # 获取学习事件统计数据
        learning_event_count = len(mock_learning_events)
        
        # 获取区块链统计数据
        blockchain_stats = {
            "transaction_count": len(mock_transactions),
            "block_count": len(mock_blocks),
            "latest_block": max([block["number"] for block in mock_blocks]) if mock_blocks else 0
        }
        
        return {
            "agents": {
                "total": agent_count,
                "capabilities": {
                    "data_analysis": len([a for a in mock_agents if "data_analysis" in a["capabilities"]]),
                    "text_generation": len([a for a in mock_agents if "text_generation" in a["capabilities"]]),
                    "image_recognition": len([a for a in mock_agents if "image_recognition" in a["capabilities"]]),
                    "code_generation": len([a for a in mock_agents if "code_generation" in a["capabilities"]])
                }
            },
            "tasks": {
                "total": task_count,
                "open": open_tasks,
                "assigned": assigned_tasks,
                "completed": completed_tasks
            },
            "learning": {
                "total_events": learning_event_count,
                "event_types": {
                    "task_completion": len([e for e in mock_learning_events if e["event_type"] == "task_completion"]),
                    "training": len([e for e in mock_learning_events if e["event_type"] == "training"]),
                    "capability_acquisition": len([e for e in mock_learning_events if e["event_type"] == "capability_acquisition"])
                }
            },
            "blockchain": blockchain_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating system stats: {str(e)}")
        return {
            "error": "Failed to generate system statistics",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)