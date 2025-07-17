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
                                         max_agents: int = None) -> List[Dict[str, Any]]:
        """
        为任务选择多个协作代理
        Args:
            task: 任务信息
            agents: 可用代理列表
            max_agents: 最多选择的代理数量（可选）
        Returns:
            List: 选中的代理列表
        """
        # 过滤出活跃的代理
        active_agents = [a for a in agents if a.get("active", True)]
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
        # 动态分配：优先覆盖所有 required_capabilities
        required_caps = set(task.get("required_capabilities", []))
        covered_caps = set()
        selected_agents = []
        for agent in sorted_agents:
            agent_caps = set(agent.get("capabilities", []))
            new_caps = agent_caps & required_caps - covered_caps
            if agent["score"] > 0 and (new_caps or not selected_agents):
                selected_agents.append(agent)
                covered_caps.update(agent_caps)
                # 如果已覆盖所有能力且未指定 max_agents，则提前结束
                if not max_agents and covered_caps >= required_caps:
                    break
            # 如果指定了 max_agents，上限截断
            if max_agents and len(selected_agents) >= max_agents:
                break
        # 如果没覆盖所有能力，补充剩余高分 agent
        if covered_caps < required_caps:
            for agent in sorted_agents:
                if agent not in selected_agents and agent["score"] > 0:
                    selected_agents.append(agent)
                    covered_caps.update(agent.get("capabilities", []))
                    if not max_agents and covered_caps >= required_caps:
                        break
                if max_agents and len(selected_agents) >= max_agents:
                    break
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
            import requests
            
            # 通过API获取任务信息，避免循环调用
            try:
                task_response = requests.get(f"http://localhost:8001/tasks/{task_id}", timeout=10)
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    task = task_data.get("task")
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get task: HTTP {task_response.status_code}",
                        "task_id": task_id
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to get task via API: {str(e)}",
                    "task_id": task_id
                }
            
            if not task:
                return {
                    "success": False,
                    "error": "Task not found or empty",
                    "task_id": task_id
                }
            
            # 通过API获取所有代理
            try:
                agents_response = requests.get(f"http://localhost:8001/agents/", timeout=10)
                if agents_response.status_code == 200:
                    agents_data = agents_response.json()
                    agents = agents_data.get("agents", [])
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get agents: HTTP {agents_response.status_code}",
                        "task_id": task_id
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to get agents via API: {str(e)}",
                    "task_id": task_id
                }
            
            # 选择最佳代理
            best_agent = await AgentSelectionService.select_best_agent(task, agents)
            
            if not best_agent:
                return {
                    "success": False,
                    "error": "No suitable agent found",
                    "task_id": task_id
                }
            
            # 返回推荐结果（不实际分配，只是推荐）
            return {
                "success": True,
                "task_id": task_id,
                "selected_agent": {
                    "agent_id": best_agent.get("agent_id"),
                    "name": best_agent.get("name"),
                    "capabilities": best_agent.get("capabilities"),
                    "reputation": best_agent.get("reputation"),
                    "match_score": round(best_agent.get("score", 0) * 100, 2)
                },
                "task_title": task.get("title"),
                "required_capabilities": task.get("required_capabilities"),
                "message": "Best agent selected successfully"
            }
                
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
            from services import contract_service
            
            # 直接使用contract_service获取任务信息，避免API循环调用
            task = None
            connection_status = contract_service.get_connection_status()
            
            if connection_status["connected"]:
                task_result = contract_service.get_task(task_id)
                if task_result["success"]:
                    # task_result already contains the task data, no need to access ["task"]
                    task = {
                        "task_id": task_result["task_id"],
                        "title": task_result["title"],
                        "description": task_result["description"],
                        "required_capabilities": task_result["required_capabilities"],
                        "min_reputation": task_result["min_reputation"],
                        "reward": task_result["reward"],
                        "status": task_result["status"],
                        "creator": task_result["creator"],
                        "deadline": task_result["deadline"]
                    }
            
            # 如果区块链获取失败，尝试从mock数据获取
            if not task:
                from routers.tasks import mock_tasks
                for mock_task in mock_tasks:
                    if mock_task["task_id"] == task_id:
                        task = mock_task
                        break
            
            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "task_id": task_id
                }
            
            # 直接使用contract_service获取代理信息
            agents = []
            if connection_status["connected"]:
                try:
                    agents_result = contract_service.get_all_agents()
                    if agents_result.get("success"):
                        raw_agents = agents_result.get("agents", [])
                        # 修复数据格式：将'address'字段映射为'agent_id'
                        agents = []
                        for agent in raw_agents:
                            fixed_agent = agent.copy()
                            if 'address' in agent and 'agent_id' not in agent:
                                fixed_agent['agent_id'] = agent['address']
                            agents.append(fixed_agent)
                        logger.info(f"Successfully loaded {len(agents)} agents from blockchain")
                except Exception as e:
                    logger.warning(f"Failed to get agents from blockchain: {e}")
                    agents = []
            
            # 如果区块链获取失败，使用mock数据
            if not agents:
                from routers.agents import mock_agents_data
                agents = mock_agents_data.get("agents", [])
            
            # 选择协作代理
            selected_agents = await AgentSelectionService.select_collaborative_agents(task, agents, max_agents)
            
            if not selected_agents:
                return {
                    "success": False,
                    "error": "No suitable agents found",
                    "task_id": task_id
                }
            
            # 分析团队能力覆盖
            required_capabilities = set(task.get("required_capabilities", []))
            covered_capabilities = set()
            for agent in selected_agents:
                agent_caps = agent.get("capabilities", [])
                covered_capabilities.update(cap for cap in agent_caps if cap in required_capabilities)
            
            coverage_ratio = len(covered_capabilities) / len(required_capabilities) if required_capabilities else 1.0
            
            # 返回协作团队推荐结果
            return {
                "success": True,
                "task_id": task_id,
                "task_title": task.get("title"),
                "required_capabilities": list(required_capabilities),
                "selected_agents": [
                    {
                        "agent_id": agent.get("agent_id"),
                        "name": agent.get("name"),
                        "agent_type": agent.get("agent_type"),
                        "capabilities": agent.get("capabilities"),
                        "reputation": agent.get("reputation"),
                        "match_score": round(agent.get("score", 0) * 100, 2),
                        "role": "Coordinator" if agent.get("agent_type") == 2 else "Evaluator" if agent.get("agent_type") == 3 else "Executor"
                    }
                    for agent in selected_agents
                ],
                "team_analysis": {
                    "team_size": len(selected_agents),
                    "capability_coverage": round(coverage_ratio * 100, 2),
                    "covered_capabilities": list(covered_capabilities),
                    "missing_capabilities": list(required_capabilities - covered_capabilities),
                    "average_reputation": round(sum(a.get("reputation", 0) for a in selected_agents) / len(selected_agents), 1),
                    "team_score": round(sum(a.get("score", 0) for a in selected_agents) / len(selected_agents) * 100, 2)
                },
                "message": f"Successfully selected {len(selected_agents)} agents for collaborative task"
            }
                
        except Exception as e:
            logger.exception(f"Error auto-assigning collaborative task {task_id}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }

# 创建服务实例
agent_selection_service = AgentSelectionService() 