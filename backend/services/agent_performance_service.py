"""
Agent Performance Evaluation and Update Service
智能代理表现评估和更新服务
"""

import json
import os
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """代理表现指标"""
    task_completion_score: float  # 任务完成质量分数 (0-10)
    collaboration_score: float    # 协作能力分数 (0-10)  
    response_quality: float       # 响应质量分数 (0-10)
    innovation_score: float       # 创新能力分数 (0-10)
    efficiency_score: float       # 效率分数 (0-10)

@dataclass
class AgentUpdate:
    """代理更新信息"""
    agent_id: str
    old_reputation: float
    new_reputation: float
    reputation_change: float
    tasks_completed: int
    performance_metrics: PerformanceMetrics
    capability_improvements: List[str]
    new_capabilities: List[str]
    timestamp: float

class AgentPerformanceService:
    """代理表现评估和更新服务"""
    
    def __init__(self):
        """初始化服务"""
        self.agent_data = {}  # 存储代理数据的内存缓存
        self.performance_history = {}  # 存储表现历史
        
    def evaluate_agent_performance(self, agent_id: str, conversation: List[Dict], task_data: Dict) -> PerformanceMetrics:
        """
        评估代理在协作中的表现
        
        Args:
            agent_id: 代理ID
            conversation: 完整对话记录
            task_data: 任务数据
            
        Returns:
            PerformanceMetrics: 表现指标
        """
        # 提取该代理的消息
        agent_messages = []
        for msg in conversation:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                # 检查是否是该代理的消息
                if self._is_agent_message(content, agent_id):
                    agent_messages.append(content)
        
        # 计算各项指标
        task_completion_score = self._evaluate_task_completion(agent_messages, task_data)
        collaboration_score = self._evaluate_collaboration(agent_messages, conversation)
        response_quality = self._evaluate_response_quality(agent_messages)
        innovation_score = self._evaluate_innovation(agent_messages, task_data)
        efficiency_score = self._evaluate_efficiency(agent_messages, len(conversation))
        
        return PerformanceMetrics(
            task_completion_score=task_completion_score,
            collaboration_score=collaboration_score,
            response_quality=response_quality,
            innovation_score=innovation_score,
            efficiency_score=efficiency_score
        )
    
    def _is_agent_message(self, content: str, agent_id: str) -> bool:
        """判断消息是否来自指定代理"""
        # 匹配Agent1, Agent2等格式
        agent_patterns = [
            rf"Agent\d+[:\s]",
            rf"{agent_id}[:\s]",
            rf"Agent\d+\s*\([^)]*\)[:\s]"
        ]
        
        for pattern in agent_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _evaluate_task_completion(self, agent_messages: List[str], task_data: Dict) -> float:
        """评估任务完成质量 (0-10)"""
        if not agent_messages:
            return 0.0
        
        # 基础分数
        base_score = 5.0
        
        # 检查是否提供了具体的解决方案
        solution_keywords = ['解决方案', '完成', '结果', '方案', '策略', '实现', '建议']
        solution_mentions = sum(1 for msg in agent_messages for keyword in solution_keywords if keyword in msg)
        solution_score = min(solution_mentions * 0.5, 2.0)
        
        # 检查是否与任务类型相关
        task_type = task_data.get('type', '').lower()
        type_keywords = {
            'analysis': ['分析', '数据', '趋势', '统计'],
            'text_generation': ['生成', '文本', '内容', '报告'],
            'classification': ['分类', '分组', '标记'],
            'translation': ['翻译', '语言'],
            'research': ['研究', '调查', '发现']
        }
        
        relevant_keywords = type_keywords.get(task_type, [])
        relevance_score = min(
            sum(1 for msg in agent_messages for keyword in relevant_keywords if keyword in msg) * 0.3,
            2.0
        )
        
        # 检查工作完成度
        completion_keywords = ['完成', '结束', '成功', '达成']
        completion_score = min(
            sum(1 for msg in agent_messages for keyword in completion_keywords if keyword in msg) * 0.5,
            1.0
        )
        
        total_score = base_score + solution_score + relevance_score + completion_score
        return min(total_score, 10.0)
    
    def _evaluate_collaboration(self, agent_messages: List[str], full_conversation: List[Dict]) -> float:
        """评估协作能力 (0-10)"""
        if not agent_messages:
            return 0.0
        
        # 基础分数
        base_score = 5.0
        
        # 检查协作相关词汇
        collaboration_keywords = ['协作', '合作', '配合', '团队', '一起', '共同', '支持', '帮助']
        collaboration_mentions = sum(1 for msg in agent_messages for keyword in collaboration_keywords if keyword in msg)
        collaboration_score = min(collaboration_mentions * 0.4, 2.0)
        
        # 检查是否引用其他代理的工作
        reference_keywords = ['Agent', '代理', '其他', '结合', '基于']
        reference_score = min(
            sum(1 for msg in agent_messages for keyword in reference_keywords if keyword in msg) * 0.3,
            1.5
        )
        
        # 检查建设性贡献
        contribution_keywords = ['建议', '提供', '贡献', '负责', '专长', '能力']
        contribution_score = min(
            sum(1 for msg in agent_messages for keyword in contribution_keywords if keyword in msg) * 0.3,
            1.5
        )
        
        total_score = base_score + collaboration_score + reference_score + contribution_score
        return min(total_score, 10.0)
    
    def _evaluate_response_quality(self, agent_messages: List[str]) -> float:
        """评估响应质量 (0-10)"""
        if not agent_messages:
            return 0.0
        
        # 基础分数
        base_score = 4.0
        
        # 检查平均消息长度（质量指标）
        total_length = sum(len(msg) for msg in agent_messages)
        avg_length = total_length / len(agent_messages) if agent_messages else 0
        
        # 长度分数 (50-200字符为最佳)
        if 50 <= avg_length <= 200:
            length_score = 2.0
        elif 30 <= avg_length < 50 or 200 < avg_length <= 300:
            length_score = 1.5
        elif avg_length < 30:
            length_score = 0.5
        else:
            length_score = 1.0
        
        # 检查专业术语使用
        professional_keywords = ['分析', '处理', '优化', '实现', '技术', '方法', '算法', '模型']
        professional_score = min(
            sum(1 for msg in agent_messages for keyword in professional_keywords if keyword in msg) * 0.2,
            2.0
        )
        
        # 检查结构化表达
        structure_keywords = ['首先', '然后', '最后', '因此', '同时', '另外']
        structure_score = min(
            sum(1 for msg in agent_messages for keyword in structure_keywords if keyword in msg) * 0.3,
            2.0
        )
        
        total_score = base_score + length_score + professional_score + structure_score
        return min(total_score, 10.0)
    
    def _evaluate_innovation(self, agent_messages: List[str], task_data: Dict) -> float:
        """评估创新能力 (0-10)"""
        if not agent_messages:
            return 0.0
        
        # 基础分数
        base_score = 5.0
        
        # 检查创新相关词汇
        innovation_keywords = ['创新', '新', '独特', '原创', '突破', '改进', '优化', '改善']
        innovation_mentions = sum(1 for msg in agent_messages for keyword in innovation_keywords if keyword in msg)
        innovation_score = min(innovation_mentions * 0.5, 2.0)
        
        # 检查解决方案的创造性
        creative_keywords = ['想法', '思路', '方案', '策略', '技巧', '方式', '方法']
        creative_score = min(
            sum(1 for msg in agent_messages for keyword in creative_keywords if keyword in msg) * 0.3,
            1.5
        )
        
        # 检查是否提出具体的实施步骤
        implementation_keywords = ['步骤', '流程', '实施', '执行', '操作', '具体']
        implementation_score = min(
            sum(1 for msg in agent_messages for keyword in implementation_keywords if keyword in msg) * 0.4,
            1.5
        )
        
        total_score = base_score + innovation_score + creative_score + implementation_score
        return min(total_score, 10.0)
    
    def _evaluate_efficiency(self, agent_messages: List[str], total_conversation_length: int) -> float:
        """评估效率 (0-10)"""
        if not agent_messages:
            return 0.0
        
        # 基础分数
        base_score = 5.0
        
        # 消息数量效率（既不过多也不过少）
        message_count = len(agent_messages)
        if 2 <= message_count <= 4:
            message_efficiency = 2.0
        elif message_count == 1 or message_count == 5:
            message_efficiency = 1.5
        elif message_count > 5:
            message_efficiency = 1.0
        else:
            message_efficiency = 0.5
        
        # 响应时机（在对话中的分布）
        timing_score = 1.5  # 默认合理的时机分数
        
        # 简洁性评估
        total_length = sum(len(msg) for msg in agent_messages)
        if 100 <= total_length <= 500:
            conciseness_score = 1.5
        elif 50 <= total_length < 100 or 500 < total_length <= 800:
            conciseness_score = 1.0
        else:
            conciseness_score = 0.5
        
        total_score = base_score + message_efficiency + timing_score + conciseness_score
        return min(total_score, 10.0)
    
    def calculate_reputation_change(self, performance_metrics: PerformanceMetrics, current_reputation: float) -> float:
        """
        根据表现指标计算声誉变化
        
        Args:
            performance_metrics: 表现指标
            current_reputation: 当前声誉值
            
        Returns:
            float: 声誉变化值
        """
        # 计算总体表现分数
        total_score = (
            performance_metrics.task_completion_score * 0.3 +
            performance_metrics.collaboration_score * 0.25 +
            performance_metrics.response_quality * 0.2 +
            performance_metrics.innovation_score * 0.15 +
            performance_metrics.efficiency_score * 0.1
        )
        
        # 基于表现计算声誉变化
        if total_score >= 8.0:
            reputation_change = 2.0  # 优秀表现
        elif total_score >= 7.0:
            reputation_change = 1.0  # 良好表现
        elif total_score >= 6.0:
            reputation_change = 0.5  # 一般表现
        elif total_score >= 5.0:
            reputation_change = 0.0  # 平均表现
        elif total_score >= 4.0:
            reputation_change = -0.5  # 较差表现
        else:
            reputation_change = -1.0  # 差表现
        
        # 考虑当前声誉值的影响（高声誉增长较慢，低声誉恢复较快）
        if current_reputation > 90:
            reputation_change *= 0.5
        elif current_reputation < 50:
            reputation_change *= 1.5
        
        return reputation_change
    
    def determine_capability_improvements(self, performance_metrics: PerformanceMetrics, current_capabilities: List[str], task_type: str) -> List[str]:
        """
        根据表现确定能力提升
        
        Args:
            performance_metrics: 表现指标
            current_capabilities: 当前能力列表
            task_type: 任务类型
            
        Returns:
            List[str]: 提升的能力列表
        """
        improvements = []
        
        # 根据不同指标的表现决定能力提升
        if performance_metrics.task_completion_score >= 8.0:
            if task_type == 'analysis' and 'advanced_data_analysis' not in current_capabilities:
                improvements.append('advanced_data_analysis')
            elif task_type == 'text_generation' and 'creative_writing' not in current_capabilities:
                improvements.append('creative_writing')
            elif task_type == 'classification' and 'advanced_classification' not in current_capabilities:
                improvements.append('advanced_classification')
        
        if performance_metrics.collaboration_score >= 8.0:
            if 'team_leadership' not in current_capabilities:
                improvements.append('team_leadership')
        
        if performance_metrics.innovation_score >= 8.0:
            if 'creative_problem_solving' not in current_capabilities:
                improvements.append('creative_problem_solving')
        
        if performance_metrics.efficiency_score >= 8.0:
            if 'process_optimization' not in current_capabilities:
                improvements.append('process_optimization')
        
        return improvements
    
    def update_agent_after_collaboration(self, agents_info: List[Dict], conversation: List[Dict], task_data: Dict) -> List[AgentUpdate]:
        """
        协作完成后更新所有参与的代理信息
        
        Args:
            agents_info: 参与协作的代理信息列表
            conversation: 完整对话记录
            task_data: 任务数据
            
        Returns:
            List[AgentUpdate]: 代理更新信息列表
        """
        updates = []
        
        for agent in agents_info:
            agent_id = agent['agent_id']
            current_reputation = agent.get('reputation', 80)
            current_capabilities = agent.get('capabilities', [])
            
            # 评估代理表现
            performance_metrics = self.evaluate_agent_performance(agent_id, conversation, task_data)
            
            # 计算声誉变化
            reputation_change = self.calculate_reputation_change(performance_metrics, current_reputation)
            new_reputation = max(0, min(100, current_reputation + reputation_change))
            
            # 确定能力提升
            capability_improvements = self.determine_capability_improvements(
                performance_metrics, current_capabilities, task_data.get('type', '')
            )
            
            # 创建更新记录
            agent_update = AgentUpdate(
                agent_id=agent_id,
                old_reputation=current_reputation,
                new_reputation=new_reputation,
                reputation_change=reputation_change,
                tasks_completed=agent.get('tasks_completed', 0) + 1,
                performance_metrics=performance_metrics,
                capability_improvements=capability_improvements,
                new_capabilities=list(set(current_capabilities + capability_improvements)),
                timestamp=time.time()
            )
            
            updates.append(agent_update)
            
            # 更新内存缓存
            self.agent_data[agent_id] = {
                'agent_id': agent_id,
                'name': agent.get('name'),
                'reputation': new_reputation,
                'capabilities': agent_update.new_capabilities,
                'tasks_completed': agent_update.tasks_completed,
                'last_updated': agent_update.timestamp
            }
            
            logger.info(f"Updated agent {agent_id}: reputation {current_reputation:.1f} -> {new_reputation:.1f} (change: {reputation_change:+.1f})")
        
        return updates
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """获取代理信息"""
        return self.agent_data.get(agent_id)
    
    def get_all_agents_info(self) -> List[Dict]:
        """获取所有代理信息"""
        return list(self.agent_data.values())

# 创建单例实例
agent_performance_service = AgentPerformanceService()