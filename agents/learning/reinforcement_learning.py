import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from typing import Dict, List, Tuple, Any, Optional
import logging
from collections import deque
import random
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ReinforcementLearning")

class CapabilityNetwork(nn.Module):
    """
    用于代理能力向量演化的神经网络模型
    """
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        """
        初始化能力网络
        
        Args:
            input_dim: 输入维度（任务特征）
            hidden_dim: 隐藏层维度
            output_dim: 输出维度（能力权重调整）
        """
        super(CapabilityNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # 价值网络（估计状态价值）
        self.value_network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播
        
        Args:
            x: 输入张量
            
        Returns:
            Tuple[torch.Tensor, torch.Tensor]: (策略输出, 价值估计)
        """
        policy_output = self.network(x)
        value = self.value_network(x)
        return policy_output, value

class ReinforcementLearning:
    """
    实现基于强化学习的代理能力向量自适应演化
    
    该类负责:
    1. 通过强化学习优化代理的能力权重
    2. 学习任务特征与最优能力配置的关系
    3. 提供可解释的学习过程
    """
    
    def __init__(
        self,
        capability_tags: List[str],
        initial_weights: List[int],
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        eps_clip: float = 0.2,
        k_epochs: int = 4,
        update_timestep: int = 20,
        max_memory_size: int = 1000,
        batch_size: int = 32,
        model_path: str = None
    ):
        """
        初始化强化学习模块
        
        Args:
            capability_tags: 能力标签列表
            initial_weights: 初始能力权重列表
            learning_rate: 学习率
            gamma: 折扣因子
            eps_clip: PPO裁剪参数
            k_epochs: 每次更新的训练轮数
            update_timestep: 更新策略的时间步长
            max_memory_size: 经验回放缓冲区大小
            batch_size: 批处理大小
            model_path: 模型保存路径
        """
        self.capability_tags = capability_tags
        self.num_capabilities = len(capability_tags)
        
        # 创建能力权重字典
        self.capability_weights = {
            tag: weight for tag, weight in zip(capability_tags, initial_weights)
        }
        
        # 学习参数
        self.lr = learning_rate
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        self.update_timestep = update_timestep
        
        # 任务特征维度（示例：任务类型、复杂度、紧急程度、奖励等）
        self.task_feature_dim = 10
        
        # 初始化神经网络
        self.policy = CapabilityNetwork(
            input_dim=self.task_feature_dim,
            hidden_dim=128,
            output_dim=self.num_capabilities
        )
        
        # 优化器
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.lr)
        
        # 经验回放缓冲区
        self.memory = deque(maxlen=max_memory_size)
        self.batch_size = batch_size
        
        # 训练计数器
        self.timestep = 0
        
        # 加载预训练模型（如果存在）
        self.model_path = model_path
        if model_path and os.path.exists(model_path):
            self._load_model()
            logger.info(f"Loaded pre-trained model from {model_path}")
        
        # 学习历史记录
        self.training_history = {
            'rewards': [],
            'losses': [],
            'value_losses': [],
            'policy_losses': [],
            'entropy': []
        }
        
        logger.info(f"ReinforcementLearning initialized with {self.num_capabilities} capabilities")
    
    def extract_task_features(self, task_data: Dict[str, Any]) -> np.ndarray:
        """
        从任务数据中提取特征向量
        
        Args:
            task_data: 任务数据字典
            
        Returns:
            np.ndarray: 任务特征向量
        """
        # 初始化特征向量
        features = np.zeros(self.task_feature_dim)
        
        try:
            # 1. 任务类型编码（假设有预定义的任务类型列表）
            task_types = ["analysis", "generation", "classification", "translation", "summarization"]
            if "task_type" in task_data and task_data["task_type"] in task_types:
                type_idx = task_types.index(task_data["task_type"])
                features[type_idx] = 1  # One-hot编码
            
            # 2. 任务复杂度 (0-1)
            if "complexity" in task_data:
                features[5] = task_data["complexity"] / 100
            
            # 3. 任务紧急程度 (0-1)
            if "urgency" in task_data:
                features[6] = task_data["urgency"] / 100
            
            # 4. 归一化任务奖励
            if "reward" in task_data:
                features[7] = min(task_data["reward"] / 1000, 1.0)  # 假设最大奖励为1000
            
            # 5. 任务预计持续时间
            if "estimated_duration" in task_data:
                features[8] = min(task_data["estimated_duration"] / 86400, 1.0)  # 最多1天，归一化
            
            # 6. 是否有特殊要求
            if "special_requirements" in task_data and task_data["special_requirements"]:
                features[9] = 1
        
        except Exception as e:
            logger.error(f"Error extracting task features: {e}")
        
        return features
    
    def recommend_capability_adjustments(self, task_data: Dict[str, Any]) -> Dict[str, int]:
        """
        根据任务特征推荐能力权重调整
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict[str, int]: 推荐的能力权重调整（正值表示增加，负值表示减少）
        """
        # 提取任务特征
        task_features = self.extract_task_features(task_data)
        task_tensor = torch.FloatTensor(task_features).unsqueeze(0)  # 添加批处理维度
        
        # 使用策略网络预测调整
        with torch.no_grad():
            adjustment_logits, _ = self.policy(task_tensor)
            
            # 将logits转换为实际调整值（范围：-10到+10）
            adjustments = torch.tanh(adjustment_logits) * 10
        
        # 转换为字典
        adjustment_dict = {
            tag: int(adjustments[0, i].item())
            for i, tag in enumerate(self.capability_tags)
        }
        
        logger.info(f"Recommended capability adjustments: {adjustment_dict}")
        return adjustment_dict
    
    def apply_adjustments(self, adjustments: Dict[str, int]) -> Dict[str, int]:
        """
        应用能力权重调整
        
        Args:
            adjustments: 能力权重调整
            
        Returns:
            Dict[str, int]: 更新后的能力权重
        """
        for tag, adjustment in adjustments.items():
            if tag in self.capability_weights:
                # 应用调整并确保在0-100范围内
                self.capability_weights[tag] = max(0, min(100, self.capability_weights[tag] + adjustment))
        
        logger.info(f"Updated capability weights: {self.capability_weights}")
        return self.capability_weights
    
    def store_experience(
        self,
        task_features: np.ndarray,
        adjustments: Dict[str, int],
        reward: float,
        next_task_features: np.ndarray,
        done: bool
    ) -> None:
        """
        存储经验到回放缓冲区
        
        Args:
            task_features: 任务特征
            adjustments: 应用的能力调整
            reward: 获得的奖励
            next_task_features: 下一个任务的特征
            done: 是否完成
        """
        # 转换调整为向量
        adjustment_vector = np.array([adjustments.get(tag, 0) for tag in self.capability_tags])
        
        # 存储经验
        self.memory.append((
            task_features,
            adjustment_vector,
            reward,
            next_task_features,
            done
        ))
        
        # 更新时间步
        self.timestep += 1
        
        # 如果达到更新时间，执行策略更新
        if self.timestep % self.update_timestep == 0 and len(self.memory) >= self.batch_size:
            self.update_policy()
    
    def calculate_reward(self, task_score: int, task_data: Dict[str, Any]) -> float:
        """
        计算强化学习奖励
        
        Args:
            task_score: 任务得分 (0-100)
            task_data: 任务数据
            
        Returns:
            float: 计算的奖励
        """
        # 基础奖励基于任务得分
        base_reward = task_score / 20.0  # 将0-100映射到0-5
        
        # 任务难度调整（难任务有更高奖励）
        difficulty_multiplier = 1.0
        if "complexity" in task_data:
            difficulty_multiplier += task_data["complexity"] / 100.0
        
        # 紧急程度加成
        urgency_bonus = 0.0
        if "urgency" in task_data and task_data["urgency"] > 70:
            urgency_bonus = 1.0
        
        # 计算最终奖励
        final_reward = base_reward * difficulty_multiplier + urgency_bonus
        
        logger.info(f"Calculated reward: {final_reward} (base: {base_reward}, "
                   f"difficulty: {difficulty_multiplier}, urgency bonus: {urgency_bonus})")
        
        return final_reward
    
    def update_policy(self) -> None:
        """更新策略网络"""
        # 检查内存中的样本数量
        if len(self.memory) < self.batch_size:
            return
        
        # 记录训练开始时间
        start_time = time.time()
        
        # 从经验回放缓冲区中采样
        batch = random.sample(self.memory, self.batch_size)
        
        # 解包批次数据
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # 转换为张量
        states = torch.FloatTensor(np.vstack(states))
        actions = torch.FloatTensor(np.vstack(actions))
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.FloatTensor(np.vstack(next_states))
        dones = torch.FloatTensor(dones).unsqueeze(1)
        
        # 计算目标值（TD目标）
        with torch.no_grad():
            _, next_values = self.policy(next_states)
            target_values = rewards + self.gamma * next_values * (1 - dones)
        
        # PPO更新
        for _ in range(self.k_epochs):
            # 获取当前策略的动作概率和状态值
            logits, values = self.policy(states)
            
            # 计算优势函数
            advantages = target_values - values
            
            # 计算策略损失
            # 这里我们使用MSE损失来近似策略梯度，因为我们的动作是连续的
            policy_loss = ((logits - actions) ** 2).mean()
            
            # 计算价值损失
            value_loss = ((target_values - values) ** 2).mean()
            
            # 计算熵（用于鼓励探索）
            entropy = -torch.sum(torch.softmax(logits, dim=1) * torch.log_softmax(logits, dim=1), dim=1).mean()
            
            # 总损失
            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
            
            # 梯度更新
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # 记录损失
            self.training_history['losses'].append(loss.item())
            self.training_history['policy_losses'].append(policy_loss.item())
            self.training_history['value_losses'].append(value_loss.item())
            self.training_history['entropy'].append(entropy.item())
        
        # 记录平均奖励
        self.training_history['rewards'].append(rewards.mean().item())
        
        # 定期保存模型
        if self.model_path and self.timestep % (self.update_timestep * 5) == 0:
            self._save_model()
        
        logger.info(f"Policy updated at timestep {self.timestep} "
                   f"(time: {time.time() - start_time:.2f}s, "
                   f"loss: {loss.item():.4f})")
    
    def _save_model(self) -> None:
        """保存模型"""
        if not self.model_path:
            return
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # 保存模型状态
        model_state = {
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'capability_tags': self.capability_tags,
            'capability_weights': self.capability_weights,
            'timestep': self.timestep,
            'training_history': self.training_history
        }
        
        torch.save(model_state, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def _load_model(self) -> None:
        """加载模型"""
        if not os.path.exists(self.model_path):
            return
        
        try:
            # 加载模型状态
            model_state = torch.load(self.model_path)
            
            # 恢复模型参数
            self.policy.load_state_dict(model_state['policy_state_dict'])
            self.optimizer.load_state_dict(model_state['optimizer_state_dict'])
            
            # 恢复其他状态
            self.capability_tags = model_state['capability_tags']
            self.capability_weights = model_state['capability_weights']
            self.timestep = model_state['timestep']
            self.training_history = model_state['training_history']
            
            logger.info(f"Model loaded from {self.model_path} (timestep: {self.timestep})")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """
        生成学习报告
        
        Returns:
            Dict[str, Any]: 学习报告
        """
        # 计算平均奖励
        avg_reward = np.mean(self.training_history['rewards'][-100:]) if self.training_history['rewards'] else 0
        
        # 计算平均损失
        avg_loss = np.mean(self.training_history['losses'][-100:]) if self.training_history['losses'] else 0
        
        # 计算能力权重变化
        capability_changes = {}
        
        # 生成报告
        report = {
            'timesteps': self.timestep,
            'avg_reward': avg_reward,
            'avg_loss': avg_loss,
            'current_weights': self.capability_weights,
            'capability_changes': capability_changes,
            'learning_progress': {
                'rewards': self.training_history['rewards'][-100:],
                'losses': self.training_history['losses'][-100:]
            }
        }
        
        return report


class AgentLearningSystem:
    """
    Agent learning system that integrates reinforcement learning for capability evolution
    """
    
    def __init__(
        self,
        agent_id: str,
        capability_tags: List[str],
        initial_weights: Optional[List[int]] = None,
        model_dir: str = "./models"
    ):
        """
        Initialize the agent learning system
        
        Args:
            agent_id: Unique identifier for the agent
            capability_tags: List of capability tags
            initial_weights: Initial capability weights (optional, defaults to 50 for each capability)
            model_dir: Directory to store model files
        """
        self.agent_id = agent_id
        self.capability_tags = capability_tags
        
        # Create model directory if it doesn't exist
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize with default weights if not provided
        if initial_weights is None:
            initial_weights = [50] * len(capability_tags)
        
        # Initialize reinforcement learning module
        self.rl_module = ReinforcementLearning(
            capability_tags=capability_tags,
            initial_weights=initial_weights,
            model_path=os.path.join(self.model_dir, f"{agent_id}_rl_model.pt")
        )
        
        # Task history
        self.task_history = []
        self.total_tasks = 0
        self.total_score = 0
        
        logger.info(f"AgentLearningSystem initialized for agent {agent_id}")
    
    def process_task(
        self,
        task_id: str,
        task_type: str = "",
        task_complexity: float = 1.0,
        score: int = 0,
        is_urgent: bool = False
    ) -> Dict[str, Any]:
        """
        Process a completed task and update the learning system
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of the task
            task_complexity: Complexity level of the task (0.1-5.0)
            score: Task execution score (0-100)
            is_urgent: Whether the task was urgent
            
        Returns:
            Dict[str, Any]: Processing results
        """
        # Convert parameters to task data dictionary
        task_data = {
            "task_id": task_id,
            "task_type": task_type,
            "complexity": task_complexity * 20,  # Scale to 0-100
            "urgency": 100 if is_urgent else 0,
            "timestamp": time.time()
        }
        
        # Extract task features
        task_features = self.rl_module.extract_task_features(task_data)
        
        # Calculate reward based on score and task data
        reward = self.rl_module.calculate_reward(score, task_data)
        
        # Get recommended capability adjustments
        adjustments = self.rl_module.recommend_capability_adjustments(task_data)
        
        # Apply the adjustments
        updated_weights = self.rl_module.apply_adjustments(adjustments)
        
        # Store the experience for future learning
        # For simplicity, we're using the same task features as "next state"
        self.rl_module.store_experience(
            task_features,
            adjustments,
            reward,
            task_features,  # Next state (simplified)
            True  # Done
        )
        
        # Update policy if enough experiences have been collected
        if self.rl_module.timestep >= self.rl_module.update_timestep:
            self.rl_module.update_policy()
        
        # Update task history
        task_record = {
            "task_id": task_id,
            "task_type": task_type,
            "complexity": task_complexity,
            "score": score,
            "is_urgent": is_urgent,
            "reward": reward,
            "adjustments": adjustments,
            "timestamp": time.time()
        }
        self.task_history.append(task_record)
        
        # Update totals
        self.total_tasks += 1
        self.total_score += score
        
        logger.info(f"Processed task {task_id} with score {score}, reward {reward:.2f}")
        
        return {
            "task_id": task_id,
            "reward": reward,
            "adjustments": adjustments,
            "updated_weights": updated_weights
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive learning report
        
        Returns:
            Dict[str, Any]: Learning report
        """
        # Calculate average score
        avg_score = self.total_score / max(1, self.total_tasks)
        
        # Get current capability weights
        current_weights = self.rl_module.capability_weights
        
        # Calculate task type distribution
        task_types = {}
        for task in self.task_history:
            task_type = task.get("task_type", "unknown")
            if task_type in task_types:
                task_types[task_type] += 1
            else:
                task_types[task_type] = 1
        
        # Calculate average reward
        avg_reward = sum(task.get("reward", 0) for task in self.task_history) / max(1, len(self.task_history))
        
        # Calculate capability evolution
        capability_evolution = {}
        if len(self.task_history) > 0:
            # Track capability changes over time
            for capability in self.capability_tags:
                capability_evolution[capability] = [
                    {
                        "task_id": task.get("task_id", "unknown"),
                        "timestamp": task.get("timestamp", 0),
                        "adjustment": task.get("adjustments", {}).get(capability, 0)
                    }
                    for task in self.task_history
                    if capability in task.get("adjustments", {})
                ]
        
        # Generate report
        report = {
            "agent_id": self.agent_id,
            "total_tasks": self.total_tasks,
            "average_score": avg_score,
            "average_reward": avg_reward,
            "current_weights": current_weights,
            "task_type_distribution": task_types,
            "capability_evolution": capability_evolution,
            "learning_progress": len(self.task_history),
            "timestamp": time.time()
        }
        
        logger.info(f"Generated learning report for agent {self.agent_id}")
        return report
    
    def save_state(self) -> None:
        """保存学习系统状态"""
        self.rl_module._save_model()
        
        # 保存任务历史
        history_path = os.path.join(os.path.dirname(self.rl_module.model_path), f"agent_{self.agent_id}_history.json")
        with open(history_path, 'w') as f:
            json.dump(self.task_history, f)
        
        logger.info(f"Agent learning system state saved for agent {self.agent_id}")
    
    def load_state(self) -> None:
        """加载学习系统状态"""
        self.rl_module._load_model()
        
        # 加载任务历史
        history_path = os.path.join(os.path.dirname(self.rl_module.model_path), f"agent_{self.agent_id}_history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                self.task_history = json.load(f)
        
        logger.info(f"Agent learning system state loaded for agent {self.agent_id}")


# 示例使用
if __name__ == "__main__":
    # 示例能力标签和初始权重
    capability_tags = ["analysis", "generation", "classification", "translation", "summarization"]
    initial_weights = [50, 50, 50, 50, 50]  # 初始权重均为50
    
    # 创建代理学习系统
    learning_system = AgentLearningSystem(
        agent_id="agent_001",
        capability_tags=capability_tags,
        initial_weights=initial_weights
    )
    
    # 模拟任务处理
    for i in range(10):
        # 模拟任务数据
        task_data = {
            'task_id': f"task_{i}",
            'task_type': random.choice(capability_tags),
            'complexity': random.randint(30, 90),
            'urgency': random.randint(20, 80),
            'reward': random.randint(100, 500),
            'estimated_duration': random.randint(300, 7200)  # 5分钟到2小时
        }
        
        # 模拟任务得分
        task_score = random.randint(60, 95)
        
        # 处理任务
        result = learning_system.process_task(task_data, task_score)
        print(f"Task {i} processed: score={task_score}, reward={result['reward']:.2f}")
        
        # 每3个任务保存一次状态
        if (i + 1) % 3 == 0:
            learning_system.save_state()
    
    # 生成并打印学习报告
    report = learning_system.generate_report()
    print("\nLearning Report:")
    print(f"Agent ID: {report['agent_id']}")
    print(f"Total Tasks: {report['total_tasks']}")
    print(f"Average Score: {report['average_score']:.2f}")
    print(f"Current Capability Weights: {report['current_weights']}") 