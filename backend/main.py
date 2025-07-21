"""
Agent Learning System API
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# 在导入其他模块之前加载环境变量
load_dotenv()

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from routers import agents, tasks, learning, blockchain, collaboration, analytics, agent_selection, simple_task_assignment
from services import contract_service
from services.background_task_executor import start_background_executor

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


import time
from datetime import datetime

# 健康检查中间件
@app.middleware("http")
async def health_check_middleware(request: Request, call_next):
    """记录请求处理时间，监控健康检查性能"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # 如果是健康检查端点且处理时间过长，记录警告
    if request.url.path == "/health" and process_time > 1.0:
        logger.warning(f"Health check took {process_time:.2f}s - potential performance issue")
    
    # 添加响应时间头
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    
    return response

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
app.include_router(collaboration, prefix="/collaboration", tags=["collaboration"])
app.include_router(analytics, prefix="/analytics", tags=["analytics"])
app.include_router(agent_selection, prefix="/agent-selection", tags=["agent_selection"])
app.include_router(simple_task_assignment, prefix="/task-assignment", tags=["task_assignment"])

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

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("🚀 Starting Agent Learning System...")
    
    # 初始化后端服务
    logger.info("Initializing backend services...")
    
    # 初始化Web3连接
    try:
        contract_service.init_web3()
        logger.info("Web3 connection initialized successfully")
    except Exception as e:
        logger.warning(f"Web3 initialization failed: {e}")
    
    # 初始化智能合约
    try:
        contract_service.initialize_contracts()
        logger.info("Smart contracts initialized successfully")
    except Exception as e:
        logger.warning(f"Contract initialization failed: {e}")
    
    # 启用后台任务执行器
    logger.info("Starting background task executor...")
    await start_background_executor()
    logger.info("✅ Background task executor started")

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

@app.get("/executor/status")
async def executor_status():
    """
    检查后台任务执行器状态。
    """
    from services.background_task_executor import get_background_executor
    
    try:
        executor = get_background_executor()
        if executor:
            status = executor.get_status()
            return {
                "executor_running": status.get("is_running", False),
                "check_interval": status.get("check_interval", 30),
                "service_type": status.get("service_type", "unknown")
            }
        else:
            return {
                "executor_running": False,
                "error": "Executor instance not found"
            }
    except Exception as e:
        return {
            "executor_running": False,
            "error": str(e)
        }

@app.post("/executor/check-tasks")
async def manual_task_check():
    """
    手动触发任务检查和执行。
    """
    from services.background_task_executor import get_background_executor
    
    try:
        executor = get_background_executor()
        if not executor:
            return {"success": False, "error": "Executor not found"}
        
        # 手动触发一次任务检查
        assigned_tasks = await executor._get_assigned_tasks()
        
        return {
            "success": True,
            "assigned_tasks_found": len(assigned_tasks),
            "tasks": [{"task_id": task.get("task_id"), "title": task.get("title"), "status": task.get("status")} for task in assigned_tasks]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/executor/execute-task")
async def manual_task_execution():
    """
    手动执行下一个assigned任务。
    """
    from services.background_task_executor import get_background_executor
    
    try:
        executor = get_background_executor()
        if not executor:
            return {"success": False, "error": "Executor not found"}
        
        # 获取assigned任务
        assigned_tasks = await executor._get_assigned_tasks()
        if not assigned_tasks:
            return {"success": False, "message": "No assigned tasks found"}
        
        # 排序任务
        sorted_tasks = executor._sort_tasks_by_assignment_time(assigned_tasks)
        next_task = sorted_tasks[0]
        
        # 执行任务
        await executor._execute_task(next_task)
        
        return {
            "success": True,
            "executed_task": {
                "task_id": next_task.get("task_id"),
                "title": next_task.get("title"),
                "status": next_task.get("status")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/stats")
async def system_stats():
    """
    获取系统统计数据。
    """
    try:
        # 从 routers 模块导入模拟数据
        from routers.agents import mock_agents
        from routers.tasks import mock_tasks
        from routers.learning import mock_learning_events
        from routers.blockchain import mock_transactions, mock_blocks
        
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

@app.post("/scheduled/auto-evaluate")
async def scheduled_auto_evaluate():
    """
    定时任务：自动评价超期未评价的任务
    
    这个端点可以被外部调度器调用，比如 cron job 或者其他定时任务系统
    建议每天运行一次
    """
    try:
        logger.info("🕐 Running scheduled auto-evaluation task...")
        
        # 调用任务路由中的自动评价端点
        from routers.tasks import auto_evaluate_overdue_tasks
        result = await auto_evaluate_overdue_tasks()
        
        # 记录结果
        if result.get("success"):
            evaluated_count = result.get("data", {}).get("auto_evaluated", 0)
            logger.info(f"✅ Scheduled auto-evaluation completed: {evaluated_count} tasks evaluated")
        else:
            logger.warning(f"⚠️ Scheduled auto-evaluation failed: {result.get('message', 'Unknown error')}")
        
        return {
            "scheduled_task": "auto_evaluate",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Error in scheduled auto-evaluation: {str(e)}")
        return {
            "scheduled_task": "auto_evaluate", 
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("Initializing backend services...")
    
    # 初始化Web3连接
    if contract_service.init_web3():
        logger.info("Web3 connection initialized successfully")
        # 初始化合约
        if contract_service.initialize_contracts():
            logger.info("Smart contracts initialized successfully")
        else:
            logger.warning("Failed to initialize smart contracts")
    else:
        logger.warning("Failed to initialize Web3 connection")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)