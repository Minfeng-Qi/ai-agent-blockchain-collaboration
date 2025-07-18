"""
后台任务执行器
自动检查assigned状态的任务并通过agent协作完成任务
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from . import contract_service
from .agent_collaboration_service import AgentCollaborationService

logger = logging.getLogger(__name__)

class BackgroundTaskExecutor:
    """后台任务执行器"""
    
    def __init__(self):
        self.collaboration_service = AgentCollaborationService()
        self.is_running = False
        self.check_interval = 10  # 检查间隔（秒）
        self._execution_task = None
        
    async def start(self):
        """启动后台任务执行器"""
        if self.is_running:
            logger.warning("Background task executor is already running")
            return
            
        self.is_running = True
        logger.info("🚀 Starting background task executor")
        
        # 启动主循环并保持引用
        self._execution_task = asyncio.create_task(self._execution_loop())
        
    async def stop(self):
        """停止后台任务执行器"""
        self.is_running = False
        logger.info("🛑 Stopping background task executor")
        
        # 取消执行任务
        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
            self._execution_task = None
        
    async def _execution_loop(self):
        """主执行循环"""
        logger.info(f"🔄 Background task execution loop started (check interval: {self.check_interval}s)")
        while self.is_running:
            try:
                # 获取所有assigned状态的任务
                assigned_tasks = await self._get_assigned_tasks()
                
                # 按assigned_at时间排序
                sorted_tasks = self._sort_tasks_by_assignment_time(assigned_tasks)
                
                # 执行第一个任务（如果有的话）
                if sorted_tasks:
                    logger.info(f"⏰ Found {len(sorted_tasks)} tasks to execute, starting with first task...")
                    await self._execute_task(sorted_tasks[0])
                else:
                    logger.debug(f"💤 No assigned tasks found, sleeping for {self.check_interval}s")
                    
                # 等待下一次检查
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in background task execution loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
                
    async def _get_assigned_tasks(self) -> List[Dict[str, Any]]:
        """获取所有assigned或in_progress状态的任务"""
        try:
            # 从区块链获取任务
            tasks_result = contract_service.get_all_tasks()
            
            if not tasks_result.get("success"):
                logger.error("Failed to get tasks from blockchain")
                return []
                
            tasks = tasks_result.get("tasks", [])
            
            # 过滤出assigned或in_progress状态的任务
            executable_tasks = [
                task for task in tasks 
                if task.get("status") in ["assigned", "in_progress"]
            ]
            
            if executable_tasks:
                logger.info(f"📋 Found {len(executable_tasks)} executable tasks (assigned/in_progress)")
            
            return executable_tasks
            
        except Exception as e:
            logger.error(f"Error getting executable tasks: {str(e)}")
            return []
            
    def _sort_tasks_by_assignment_time(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按assigned_at时间排序任务"""
        def get_assigned_time(task):
            assigned_at = task.get("assigned_at")
            if not assigned_at:
                return float('inf')
            
            if isinstance(assigned_at, (int, float)):
                return assigned_at
            elif isinstance(assigned_at, str):
                try:
                    return datetime.fromisoformat(assigned_at.replace('Z', '+00:00')).timestamp()
                except:
                    return float('inf')
            else:
                return float('inf')
                
        sorted_tasks = sorted(tasks, key=get_assigned_time)
        
        if sorted_tasks:
            logger.info(f"📅 Next task to execute: {sorted_tasks[0].get('task_id')} - {sorted_tasks[0].get('title')}")
            
        return sorted_tasks
        
    async def _execute_task(self, task: Dict[str, Any]):
        """执行单个任务"""
        task_id = task.get("task_id")
        title = task.get("title", "Unknown Task")
        task_status = task.get("status", "assigned")
        
        try:
            logger.info(f"🎯 Starting execution of task: {task_id} - {title} (status: {task_status})")
            
            # 直接创建协作，不需要改变任务状态到InProgress
            collaboration_id = await self.collaboration_service.create_collaboration(task_id, task)
            
            # 运行协作
            collaboration_result = await self.collaboration_service.run_collaboration(collaboration_id, task)
            
            if collaboration_result.get("status") == "completed":
                # 完成任务（根据当前状态选择合适的完成方法）
                await self._complete_task(task_id, collaboration_result, task_status)
                logger.info(f"✅ Task {task_id} completed successfully")
            else:
                logger.error(f"❌ Task {task_id} collaboration failed: {collaboration_result.get('error', collaboration_result.get('status', 'unknown error'))}")
                
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            
    async def _complete_task(self, task_id: str, collaboration_result: Dict[str, Any], task_status: str = "assigned"):
        """完成任务"""
        try:
            # 添加调试日志来查看collaboration_result的内容
            logger.info(f"🔍 DEBUG: collaboration_result keys: {list(collaboration_result.keys())}")
            logger.info(f"🔍 DEBUG: ipfs_cid value: {collaboration_result.get('ipfs_cid')}")
            logger.info(f"🔍 DEBUG: ipfs_url value: {collaboration_result.get('ipfs_url')}")
            logger.info(f"🔍 DEBUG: agents value: {collaboration_result.get('agents')}")
            logger.info(f"🔍 DEBUG: timestamp value: {collaboration_result.get('timestamp')}")
            
            # 提取结果 - 使用正确的字段名
            result = {
                "collaboration_id": collaboration_result.get("collaboration_id"),
                "conversation_ipfs": collaboration_result.get("ipfs_cid"),  # 修正字段名
                "final_result": collaboration_result.get("ipfs_url"),  # 使用ipfs_url作为最终结果
                "participants": collaboration_result.get("agents", []),
                "execution_time": collaboration_result.get("timestamp"),  # 使用timestamp
                "completed_at": datetime.now().isoformat()
            }
            
            logger.info(f"🔍 DEBUG: mapped result: {result}")
            
            # 获取发送方地址 - 首先尝试从协作events获取，然后检查单个agent分配
            assigned_agents = await self._get_assigned_agents(task_id)
            
            # 如果没有找到协作agents，检查任务是否有单个assigned_agent
            if not assigned_agents:
                try:
                    # 获取任务详情来检查assigned_agent字段
                    task_result = contract_service.get_task(task_id)
                    if task_result.get("success") and task_result.get("assigned_agent"):
                        single_agent = task_result.get("assigned_agent")
                        logger.info(f"📝 Found single assigned agent for task {task_id}: {single_agent}")
                        assigned_agents = [single_agent]
                    else:
                        logger.info(f"📝 Task result for {task_id}: success={task_result.get('success')}, assigned_agent={task_result.get('assigned_agent')}")
                except Exception as e:
                    logger.error(f"Error getting task details for {task_id}: {str(e)}")
            
            if not assigned_agents:
                # 如果没有分配的代理，这个任务可能有问题，跳过它
                logger.warning(f"⚠️ Task {task_id} has no assigned agents but is in {task_status} status. This may indicate a data inconsistency.")
                logger.warning(f"⚠️ Skipping completion for task {task_id} to avoid infinite retry loop.")
                
                # 标记任务为失败状态，而不是继续尝试
                try:
                    sender_address = contract_service.get_default_sender_address()
                    if sender_address:
                        # 尝试将任务标记为失败
                        import json
                        failure_result = {
                            "error": "No assigned agents found for this task",
                            "collaboration_id": result.get("collaboration_id"),
                            "completed_at": datetime.now().isoformat(),
                            "status": "failed"
                        }
                        
                        # 直接调用失败的合约方法
                        logger.info(f"🚫 Marking task {task_id} as failed due to missing agent assignments")
                        completion_result = contract_service.complete_assigned_task(
                            task_id=task_id,
                            result=json.dumps(failure_result, ensure_ascii=False),
                            sender_address=sender_address
                        )
                        
                        if completion_result.get("success"):
                            logger.info(f"✅ Task {task_id} marked as failed on blockchain")
                        else:
                            logger.error(f"❌ Failed to mark task {task_id} as failed: {completion_result.get('error')}")
                except Exception as e:
                    logger.error(f"Error marking task {task_id} as failed: {str(e)}")
                
                return
            else:
                # 使用第一个分配的代理地址
                sender_address = assigned_agents[0]
                logger.info(f"Using assigned agent {sender_address} to complete task {task_id} (status: {task_status})")
            
            # 根据任务状态选择合适的完成方法
            import json
            if task_status == "assigned":
                # 对于assigned任务，使用complete_assigned_task（内部会先启动再完成）
                completion_result = contract_service.complete_assigned_task(
                    task_id=task_id,
                    result=json.dumps(result, ensure_ascii=False),
                    sender_address=sender_address
                )
            else:
                # 对于in_progress任务，直接完成
                completion_result = contract_service.complete_task(
                    task_id=task_id,
                    result=json.dumps(result, ensure_ascii=False),
                    sender_address=sender_address
                )
            
            if completion_result.get("success"):
                logger.info(f"🎉 Task {task_id} completed on blockchain")
            else:
                logger.error(f"Failed to complete task {task_id} on blockchain: {completion_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {str(e)}")
            
    async def _get_assigned_agents(self, task_id: str) -> List[str]:
        """获取任务分配的代理地址"""
        try:
            # 将task_id转换为bytes格式
            if task_id.startswith('0x'):
                task_id_bytes = bytes.fromhex(task_id[2:])
            else:
                if len(task_id) == 64:
                    task_id_bytes = bytes.fromhex(task_id)
                else:
                    raise ValueError(f"Invalid task_id length: {len(task_id)}")
            
            # 从合约服务获取分配的代理
            assigned_agents = contract_service.get_task_collaboration_agents(task_id_bytes)
            return assigned_agents
            
        except Exception as e:
            logger.error(f"Error getting assigned agents for task {task_id}: {str(e)}")
            return []
            
    def get_status(self) -> Dict[str, Any]:
        """获取执行器状态"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "service_type": "background_task_executor"
        }
        
    def update_settings(self, settings: Dict[str, Any]):
        """更新设置"""
        if "check_interval" in settings:
            self.check_interval = max(5, settings["check_interval"])
            logger.info(f"📝 Updated check interval to {self.check_interval} seconds")

# 全局执行器实例
_executor_instance = None

def get_background_executor() -> BackgroundTaskExecutor:
    """获取后台任务执行器实例"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = BackgroundTaskExecutor()
    return _executor_instance

async def start_background_executor():
    """启动后台任务执行器"""
    executor = get_background_executor()
    await executor.start()

async def stop_background_executor():
    """停止后台任务执行器"""
    executor = get_background_executor()
    await executor.stop()