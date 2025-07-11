"""
智能代理选择服务
负责根据任务要求自动选择最合适的代理，支持单代理分配和多代理协作
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime

from services import contract_service

logger = logging.getLogger(__name__)

# 配置权重参数
CAPABILITY_MATCH_WEIGHT = 0.4  # 能力匹配度权重
REPUTATION_WEIGHT = 0.25       # 声誉权重
WORKLOAD_WEIGHT = 0.15         # 工作负载权重
HISTORY_WEIGHT = 0.2           # 历史表现权重

# 最大工作负载（用于归一化）
MAX_WORKLOAD = 10

class AgentSelectionService:
    """智能代理选择服务类"""
    
    @staticmethod
    def calculate_capability_match_score(agent: Dict[str, Any], task: Dict[str, Any]) -> float:
        """
        计算代理能力与任务需求的匹配分数
        
        Args:
            agent: 代理信息
            task: 任务信息
            
        Returns:
            float: 匹配分数 (0-1)
        """
        required_capabilities = task.get("required_capabilities", [])
        agent_capabilities = agent.get("capabilities", [])
        agent_weights = agent.get("capability_weights", [])
        
        # 检查代理是否拥有至少一个必需能力（支持部分匹配以实现多agent协作）
        matched_capabilities = [cap for cap in required_capabilities if cap in agent_capabilities]
        if not matched_capabilities:
            return 0.0  # 如果没有任何匹配的能力，返回0分
            
        # 计算能力权重匹配度
        match_score = 0.0
        weight_map = {}
        
        # 创建能力-权重映射
        if len(agent_capabilities) == len(agent_weights):
            for i, cap in enumerate(agent_capabilities):
                weight_map[cap] = agent_weights[i] / 100.0  # 归一化到0-1
        else:
            # 如果权重信息不完整，则均匀分配
            for cap in agent_capabilities:
                weight_map[cap] = 0.8  # 默认权重
        
        # 计算匹配分数（基于实际匹配的能力）
        for cap in matched_capabilities:
            if cap in weight_map:
                match_score += weight_map[cap]
        
        # 归一化分数（基于匹配的能力数量）
        if matched_capabilities:
            match_score /= len(matched_capabilities)
            
        # 对部分匹配进行惩罚，鼓励完全匹配
        coverage_ratio = len(matched_capabilities) / len(required_capabilities) if required_capabilities else 1.0
        match_score *= (0.5 + 0.5 * coverage_ratio)  # 部分匹配最低50%评分
            
        return match_score
    
    @staticmethod
    def calculate_workload_score(agent: Dict[str, Any]) -> float:
        """
        计算代理工作负载分数（负载越低分数越高）
        
        Args:
            agent: 代理信息
            
        Returns:
            float: 工作负载分数 (0-1)
        """
        workload = agent.get("workload", 0)
        return max(0, 1 - (workload / MAX_WORKLOAD))
    
    @staticmethod
    def calculate_history_score(agent: Dict[str, Any]) -> float:
        """
        计算代理历史表现分数
        
        Args:
            agent: 代理信息
            
        Returns:
            float: 历史表现分数 (0-1)
        """
        tasks_completed = agent.get("tasks_completed", 0)
        average_score = agent.get("average_score", 0) / 5.0  # 假设评分是0-5
        
        # 如果没有完成过任务，给一个中等分数
        if tasks_completed == 0:
            return 0.5
            
        # 结合任务完成数和平均评分
        completion_factor = min(1.0, tasks_completed / 20.0)  # 最多20个任务计为满分
        return (completion_factor * 0.4) + (average_score * 0.6)
    
    @staticmethod
    def score_agent(agent: Dict[str, Any], task: Dict[str, Any]) -> float:
        """
        综合评分代理对特定任务的适合度
        
        Args:
            agent: 代理信息
            task: 任务信息
            
        Returns:
            float: 综合评分 (0-1)
        """
        # 计算各项分数
        capability_score = AgentSelectionService.calculate_capability_match_score(agent, task)
        
        # 如果能力不匹配，直接返回0分
        if capability_score == 0:
            return 0.0
            
        reputation_score = agent.get("reputation", 0) / 100.0  # 归一化到0-1
        workload_score = AgentSelectionService.calculate_workload_score(agent)
        history_score = AgentSelectionService.calculate_history_score(agent)
        
        # 加权计算总分
        total_score = (
            capability_score * CAPABILITY_MATCH_WEIGHT +
            reputation_score * REPUTATION_WEIGHT +
            workload_score * WORKLOAD_WEIGHT +
            history_score * HISTORY_WEIGHT
        )
        
        logger.debug(f"Agent {agent.get('name')} scored {total_score:.4f} for task {task.get('title')}")
        logger.debug(f"  Capability: {capability_score:.4f}, Reputation: {reputation_score:.4f}, " +
                    f"Workload: {workload_score:.4f}, History: {history_score:.4f}")
        
        return total_score
    
    @staticmethod
    async def select_best_agent(task: Dict[str, Any], agents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        为任务选择最佳代理
        
        Args:
            task: 任务信息
            agents: 可用代理列表
            
        Returns:
            Dict or None: 最佳代理信息，如果没有合适的代理则返回None
        """
        # 过滤出活跃的代理
        active_agents = [a for a in agents if a.get("active", True)]
        
        # 过滤出满足最低声誉要求的代理
        min_reputation = task.get("min_reputation", 0)
        qualified_agents = [a for a in active_agents if a.get("reputation", 0) >= min_reputation]
        
        if not qualified_agents:
            logger.warning(f"No qualified agents found for task {task.get('task_id')}")
            return None
        
        # 为每个代理评分
        for agent in qualified_agents:
            agent["score"] = AgentSelectionService.score_agent(agent, task)
        
        # 选择得分最高的代理
        best_agent = max(qualified_agents, key=lambda a: a["score"])
        
        # 如果最高分为0，表示没有合适的代理
        if best_agent["score"] == 0:
            logger.warning(f"No suitable agents found for task {task.get('task_id')}")
            return None
            
        return best_agent
    
    @staticmethod
    async def select_collaborative_agents(task: Dict[str, Any], agents: List[Dict[str, Any]], 
                                         max_agents: int = 3) -> List[Dict[str, Any]]:
        """
        为任务选择多个协作代理
        
        Args:
            task: 任务信息
            agents: 可用代理列表
            max_agents: 最多选择的代理数量
            
        Returns:
            List: 选中的代理列表
        """
        # 过滤出活跃的代理
        active_agents = [a for a in agents if a.get("active", True)]
        
        # 过滤出满足最低声誉要求的代理
        min_reputation = task.get("min_reputation", 0)
        qualified_agents = [a for a in active_agents if a.get("reputation", 0) >= min_reputation]
        
        if not qualified_agents:
            logger.warning(f"No qualified agents found for task {task.get('task_id')}")
            return []
        
        # 为每个代理评分
        for agent in qualified_agents:
            agent["score"] = AgentSelectionService.score_agent(agent, task)
        
        # 按得分降序排序
        sorted_agents = sorted(qualified_agents, key=lambda a: a["score"], reverse=True)
        
        # 选择得分大于0的前N个代理
        selected_agents = [a for a in sorted_agents if a["score"] > 0][:max_agents]
        
        return selected_agents
    
    @staticmethod
    async def assign_task(task_id: str, agent_id: str) -> Dict[str, Any]:
        """
        将任务分配给指定代理
        
        Args:
            task_id: 任务ID
            agent_id: 代理ID
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 调用区块链服务分配任务
            result = contract_service.assign_task(task_id, agent_id)
            
            if result.get("success"):
                logger.info(f"Task {task_id} assigned to agent {agent_id}")
                return {
                    "success": True,
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "transaction_hash": result.get("transaction_hash"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to assign task {task_id} to agent {agent_id}: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "task_id": task_id,
                    "agent_id": agent_id
                }
                
        except Exception as e:
            logger.exception(f"Error assigning task {task_id} to agent {agent_id}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "agent_id": agent_id
            }
    
    @staticmethod
    async def assign_collaborative_task(task_id: str, agent_ids: List[str]) -> Dict[str, Any]:
        """
        将任务分配给多个协作代理
        
        Args:
            task_id: 任务ID
            agent_ids: 代理ID列表
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 这里需要实现多代理协作分配的区块链调用
            # 目前区块链合约可能不支持多代理分配，这里提供一个模拟实现
            
            results = []
            success_count = 0
            
            for agent_id in agent_ids:
                # 为每个代理分配任务（可能需要修改合约以支持多代理协作）
                result = await AgentSelectionService.assign_task(task_id, agent_id)
                results.append(result)
                if result.get("success"):
                    success_count += 1
            
            return {
                "success": success_count > 0,
                "task_id": task_id,
                "agent_ids": agent_ids,
                "assigned_count": success_count,
                "total_count": len(agent_ids),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.exception(f"Error assigning collaborative task {task_id}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "agent_ids": agent_ids
            }
    
    @staticmethod
    async def auto_assign_task(task_id: str) -> Dict[str, Any]:
        """
        自动为任务选择并分配最佳代理
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 获取任务信息
            task_result = contract_service.get_task(task_id)
            if not task_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to get task: {task_result.get('error')}",
                    "task_id": task_id
                }
            
            task = task_result.get("task")
            
            # 获取所有代理
            agents_result = contract_service.get_all_agents()
            if not agents_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to get agents: {agents_result.get('error')}",
                    "task_id": task_id
                }
            
            agents = agents_result.get("agents", [])
            
            # 选择最佳代理
            best_agent = await AgentSelectionService.select_best_agent(task, agents)
            
            if not best_agent:
                return {
                    "success": False,
                    "error": "No suitable agent found",
                    "task_id": task_id
                }
            
            # 分配任务
            return await AgentSelectionService.assign_task(task_id, best_agent.get("agent_id"))
                
        except Exception as e:
            logger.exception(f"Error auto-assigning task {task_id}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    @staticmethod
    async def auto_assign_collaborative_task(task_id: str, max_agents: int = 3) -> Dict[str, Any]:
        """
        自动为任务选择并分配多个协作代理
        
        Args:
            task_id: 任务ID
            max_agents: 最多选择的代理数量
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 获取任务信息
            task_result = contract_service.get_task(task_id)
            if not task_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to get task: {task_result.get('error')}",
                    "task_id": task_id
                }
            
            task = task_result.get("task")
            
            # 获取所有代理
            agents_result = contract_service.get_all_agents()
            if not agents_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to get agents: {agents_result.get('error')}",
                    "task_id": task_id
                }
            
            agents = agents_result.get("agents", [])
            
            # 选择协作代理
            selected_agents = await AgentSelectionService.select_collaborative_agents(task, agents, max_agents)
            
            if not selected_agents:
                return {
                    "success": False,
                    "error": "No suitable agents found",
                    "task_id": task_id
                }
            
            # 获取代理ID列表
            agent_ids = [a.get("agent_id") for a in selected_agents]
            
            # 分配任务
            return await AgentSelectionService.assign_collaborative_task(task_id, agent_ids)
                
        except Exception as e:
            logger.exception(f"Error auto-assigning collaborative task {task_id}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }

# 创建服务实例
agent_selection_service = AgentSelectionService() 