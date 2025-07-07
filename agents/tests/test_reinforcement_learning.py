#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import random
import numpy as np
from dotenv import load_dotenv
from reinforcement_learning import AgentLearningSystem, ReinforcementLearning

# 加载环境变量
load_dotenv()

def test_reinforcement_learning():
    """测试强化学习模块的基本功能"""
    print("\n=== 测试强化学习模块 ===\n")
    
    # 创建一个简单的强化学习模块
    capability_tags = ["analysis", "generation", "classification", "translation", "summarization"]
    initial_weights = [50, 50, 50, 50, 50]  # 初始权重均为50
    
    # 创建强化学习模块
    rl_module = ReinforcementLearning(
        capability_tags=capability_tags,
        initial_weights=initial_weights,
        model_path="models/test_rl_model.pt"
    )
    
    print(f"初始能力权重: {rl_module.capability_weights}")
    
    # 测试特征提取
    test_task = {
        'task_id': "task_test",
        'task_type': "analysis",
        'complexity': 70,
        'urgency': 50,
        'reward': 200,
        'estimated_duration': 3600  # 1小时
    }
    
    features = rl_module.extract_task_features(test_task)
    print(f"任务特征向量: {features}")
    
    # 测试能力调整推荐
    adjustments = rl_module.recommend_capability_adjustments(test_task)
    print(f"推荐的能力调整: {adjustments}")
    
    # 应用调整
    updated_weights = rl_module.apply_adjustments(adjustments)
    print(f"更新后的能力权重: {updated_weights}")
    
    # 计算奖励
    reward = rl_module.calculate_reward(85, test_task)
    print(f"计算的奖励: {reward}")
    
    # 存储经验
    rl_module.store_experience(
        task_features=features,
        adjustments=adjustments,
        reward=reward,
        next_task_features=features,
        done=True
    )
    
    print(f"经验缓冲区大小: {len(rl_module.memory)}")
    
    # 生成学习报告
    report = rl_module.generate_learning_report()
    print(f"学习报告: {report}")
    
    # 保存模型
    rl_module._save_model()
    print("模型已保存")
    
    return rl_module

def test_agent_learning_system():
    """测试代理学习系统的基本功能"""
    print("\n=== 测试代理学习系统 ===\n")
    
    # 创建代理学习系统
    capability_tags = ["analysis", "generation", "classification", "translation", "summarization"]
    initial_weights = [50, 50, 50, 50, 50]  # 初始权重均为50
    
    learning_system = AgentLearningSystem(
        agent_id="test_agent",
        capability_tags=capability_tags,
        initial_weights=initial_weights,
        model_dir="models"
    )
    
    print(f"初始能力权重: {learning_system.rl_module.capability_weights}")
    
    # 处理一系列任务
    task_types = capability_tags
    
    for i in range(5):
        # 创建任务数据
        task_data = {
            'task_id': f"task_{i}",
            'task_type': random.choice(task_types),
            'complexity': random.randint(30, 90),
            'urgency': random.randint(20, 80),
            'reward': random.randint(100, 500),
            'estimated_duration': random.randint(300, 7200)  # 5分钟到2小时
        }
        
        # 模拟任务得分
        task_score = random.randint(60, 95)
        
        # 处理任务
        result = learning_system.process_task(task_data, task_score)
        print(f"任务 {i} 处理结果: 得分={task_score}, 奖励={result['reward']:.2f}")
        print(f"能力调整: {result['adjustments']}")
        print(f"更新后的权重: {result['updated_weights']}")
        print("---")
        
        # 暂停一下，模拟时间间隔
        time.sleep(0.5)
    
    # 获取学习报告
    report = learning_system.get_learning_report()
    print("\n学习报告:")
    print(f"代理ID: {report['agent_id']}")
    print(f"总任务数: {report['task_stats']['total_tasks']}")
    print(f"平均得分: {report['task_stats']['avg_score']:.2f}")
    print(f"当前能力权重: {report['capability_weights']}")
    
    # 保存学习系统状态
    learning_system.save_state()
    print("学习系统状态已保存")
    
    # 尝试加载学习系统状态
    new_system = AgentLearningSystem(
        agent_id="test_agent",
        capability_tags=capability_tags,
        initial_weights=initial_weights,
        model_dir="models"
    )
    new_system.load_state()
    
    # 验证加载是否成功
    new_report = new_system.get_learning_report()
    print("\n加载后的学习报告:")
    print(f"总任务数: {new_report['task_stats']['total_tasks']}")
    print(f"平均得分: {new_report['task_stats']['avg_score']:.2f}")
    print(f"当前能力权重: {new_report['capability_weights']}")
    
    return learning_system

def test_learning_cycle():
    """测试完整的学习循环"""
    print("\n=== 测试完整学习循环 ===\n")
    
    # 创建代理学习系统
    capability_tags = ["analysis", "generation", "classification", "translation", "summarization"]
    initial_weights = [50, 50, 50, 50, 50]  # 初始权重均为50
    
    learning_system = AgentLearningSystem(
        agent_id="cycle_test_agent",
        capability_tags=capability_tags,
        initial_weights=initial_weights,
        model_dir="models"
    )
    
    # 模拟多轮任务处理
    rounds = 3
    tasks_per_round = 10
    
    for round_num in range(rounds):
        print(f"\n开始第 {round_num+1} 轮学习")
        print(f"当前能力权重: {learning_system.rl_module.capability_weights}")
        
        # 每轮处理多个任务
        for i in range(tasks_per_round):
            # 偏向特定任务类型，测试学习效果
            if round_num == 0:
                # 第一轮偏向分析任务
                task_type = "analysis" if random.random() < 0.7 else random.choice(capability_tags)
                complexity = random.randint(60, 90)  # 较高复杂度
            elif round_num == 1:
                # 第二轮偏向生成任务
                task_type = "generation" if random.random() < 0.7 else random.choice(capability_tags)
                complexity = random.randint(40, 70)  # 中等复杂度
            else:
                # 第三轮偏向翻译任务
                task_type = "translation" if random.random() < 0.7 else random.choice(capability_tags)
                complexity = random.randint(20, 50)  # 较低复杂度
            
            # 创建任务数据
            task_data = {
                'task_id': f"round{round_num}_task_{i}",
                'task_type': task_type,
                'complexity': complexity,
                'urgency': random.randint(20, 80),
                'reward': random.randint(100, 500),
                'estimated_duration': random.randint(300, 7200)
            }
            
            # 模拟任务得分 - 根据任务类型和轮次调整
            base_score = random.randint(60, 85)
            
            # 模拟学习效果 - 随着轮次增加，特定类型的任务得分提高
            if (round_num == 0 and task_type == "analysis") or \
               (round_num == 1 and task_type == "generation") or \
               (round_num == 2 and task_type == "translation"):
                score_boost = min(10 * (i / tasks_per_round), 10)  # 最多提升10分
                task_score = min(95, base_score + score_boost)
            else:
                task_score = base_score
            
            # 处理任务
            result = learning_system.process_task(task_data, task_score)
            
            # 只打印部分任务的详细信息，避免输出过多
            if i % 3 == 0:
                print(f"任务 {task_data['task_id']} ({task_type}): 得分={task_score:.1f}, 奖励={result['reward']:.2f}")
        
        # 每轮结束后生成报告
        report = learning_system.get_learning_report()
        print(f"\n第 {round_num+1} 轮结束:")
        print(f"总任务数: {report['task_stats']['total_tasks']}")
        print(f"平均得分: {report['task_stats']['avg_score']:.2f}")
        print(f"当前能力权重: {report['capability_weights']}")
        
        # 保存状态
        learning_system.save_state()
    
    # 最终报告
    print("\n学习循环完成")
    print("最终能力权重:")
    for tag, weight in learning_system.rl_module.capability_weights.items():
        print(f"  {tag}: {weight}")
    
    return learning_system

if __name__ == "__main__":
    # 设置随机种子，使结果可重现
    random.seed(42)
    np.random.seed(42)
    
    # 运行测试
    rl_module = test_reinforcement_learning()
    learning_system = test_agent_learning_system()
    cycle_system = test_learning_cycle() 