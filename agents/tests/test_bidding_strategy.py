#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import random
from dotenv import load_dotenv
from web3 import Web3
from adaptive_bidding_strategy import AdaptiveBiddingStrategy

# 加载环境变量
load_dotenv()

def mock_contract_functions(strategy):
    """
    模拟合约函数，用于测试不需要实际区块链连接的情况
    
    Args:
        strategy: AdaptiveBiddingStrategy实例
    """
    # 模拟getAgentLearningState函数
    def mock_get_agent_learning_state(agent_address):
        return [
            50,  # reputation
            ["analysis", "generation", "classification"],  # capabilityTags
            [60, 50, 40],  # capabilityWeights
            2,  # workload
            [Web3.to_bytes(hexstr="0x1234"), Web3.to_bytes(hexstr="0x5678")],  # recentTaskIds
            [75, 80]  # recentScores
        ]
    
    # 模拟getAgentBiddingStrategy函数
    def mock_get_agent_bidding_strategy(agent_address):
        return [80, 50]  # [confidence_factor, risk_tolerance]
    
    # 模拟getTaskExecutionInfo函数
    def mock_get_task_execution_info(task_id):
        return [
            0,  # status
            200,  # reward
            ["analysis", "generation"],  # capabilities
            0,  # deadline
            "0x0000000000000000000000000000000000000000"  # assignedAgent
        ]
    
    # 模拟calculateUtility函数
    def mock_calculate_utility(agent_address, capabilities, reward, workload):
        return 75  # 效用分数
    
    # 模拟hasAgentBid函数
    def mock_has_agent_bid(task_id, agent_address):
        return False
    
    # 模拟isBiddingOpen函数
    def mock_is_bidding_open(task_id):
        return True
    
    # 模拟getTasksByStatus函数
    def mock_get_tasks_by_status(status):
        return [
            Web3.to_bytes(hexstr="0xabcd"),
            Web3.to_bytes(hexstr="0xef12"),
            Web3.to_bytes(hexstr="0x3456")
        ]
    
    # 替换合约函数
    strategy.agent_registry.functions.getAgentLearningState = lambda addr: mock_get_agent_learning_state(addr)
    strategy.agent_registry.functions.getAgentBiddingStrategy = lambda addr: mock_get_agent_bidding_strategy(addr)
    strategy.task_manager.functions.getTaskExecutionInfo = lambda task_id: mock_get_task_execution_info(task_id)
    strategy.incentive_engine.functions.calculateUtility = lambda addr, caps, reward, workload: mock_calculate_utility(addr, caps, reward, workload)
    strategy.bid_auction.functions.hasAgentBid = lambda task_id, addr: mock_has_agent_bid(task_id, addr)
    strategy.bid_auction.functions.isBiddingOpen = lambda task_id: mock_is_bidding_open(task_id)
    strategy.task_manager.functions.getTasksByStatus = lambda status: mock_get_tasks_by_status(status)
    
    # 模拟交易发送
    strategy.place_bid = lambda task_id, bid_amount, utility_score: print(f"模拟投标: 任务={task_id}, 金额={bid_amount}, 效用={utility_score}")
    strategy._update_bidding_strategy_on_chain = lambda: print("模拟更新投标策略")

def test_bidding_strategy():
    """测试自适应投标策略的基本功能"""
    print("\n=== 测试自适应投标策略 ===\n")
    
    # 从环境变量获取配置
    agent_address = os.getenv("AGENT_ADDRESS")
    agent_private_key = os.getenv("AGENT_PRIVATE_KEY")
    web3_provider = os.getenv("WEB3_PROVIDER_URL", "http://localhost:8545")
    
    # 合约地址
    agent_registry_address = os.getenv("AGENT_REGISTRY_ADDRESS")
    incentive_engine_address = os.getenv("INCENTIVE_ENGINE_ADDRESS")
    bid_auction_address = os.getenv("BID_AUCTION_ADDRESS")
    task_manager_address = os.getenv("TASK_MANAGER_ADDRESS")
    
    # 创建临时ABI文件
    os.makedirs("temp_abis", exist_ok=True)
    
    # 创建简单的模拟ABI文件
    mock_abi = [{"type": "function", "name": "test", "inputs": [], "outputs": []}]
    
    for contract_name in ["AgentRegistry", "IncentiveEngine", "BidAuction", "TaskManager"]:
        abi_path = f"temp_abis/{contract_name}.json"
        with open(abi_path, "w") as f:
            json.dump(mock_abi, f)
    
    try:
        # 创建自适应投标策略实例
        strategy = AdaptiveBiddingStrategy(
            agent_address=agent_address,
            agent_private_key=agent_private_key,
            web3_provider=web3_provider,
            agent_registry_address=agent_registry_address,
            incentive_engine_address=incentive_engine_address,
            bid_auction_address=bid_auction_address,
            task_manager_address=task_manager_address,
            agent_registry_abi_path="temp_abis/AgentRegistry.json",
            incentive_engine_abi_path="temp_abis/IncentiveEngine.json",
            bid_auction_abi_path="temp_abis/BidAuction.json",
            task_manager_abi_path="temp_abis/TaskManager.json"
        )
        
        # 替换合约函数为模拟实现
        mock_contract_functions(strategy)
        
        # 测试同步函数
        print("测试同步区块链状态...")
        strategy.sync_from_blockchain()
        
        print(f"能力: {strategy.capabilities}")
        print(f"声誉: {strategy.reputation}")
        print(f"工作负载: {strategy.workload}")
        print(f"信心因子: {strategy.confidence_factor}")
        print(f"风险承受度: {strategy.risk_tolerance}")
        
        # 测试投标计算
        print("\n测试投标计算...")
        task_id = "0xabcd"
        task_reward = 200
        bid_amount, utility_score = strategy.calculate_bid_for_task(task_id, task_reward)
        
        print(f"任务ID: {task_id}")
        print(f"任务奖励: {task_reward}")
        print(f"计算的投标金额: {bid_amount}")
        print(f"效用分数: {utility_score}")
        
        # 测试投标决策
        print("\n测试投标决策...")
        should_bid = strategy.should_bid_on_task(task_id)
        print(f"是否应该投标: {should_bid}")
        
        # 测试能力匹配度计算
        print("\n测试能力匹配度计算...")
        required_capabilities = ["analysis", "generation"]
        match_score = strategy._calculate_capability_match(required_capabilities)
        print(f"能力匹配度: {match_score}")
        
        # 测试任务反馈处理
        print("\n测试任务反馈处理...")
        task_id = "0x1234"
        quality = 85
        tag_scores = {"analysis": 85, "generation": 80}
        strategy.process_task_feedback(task_id, quality, tag_scores)
        
        print(f"处理后的能力: {strategy.capabilities}")
        print(f"处理后的信心因子: {strategy.confidence_factor}")
        print(f"处理后的风险承受度: {strategy.risk_tolerance}")
        
        # 测试获取开放任务
        print("\n测试获取开放任务...")
        open_tasks = strategy._get_open_tasks()
        print(f"开放任务: {[Web3.to_hex(task_id) for task_id in open_tasks]}")
        
        return strategy
        
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree("temp_abis", ignore_errors=True)

def test_bidding_simulation():
    """模拟一系列投标场景"""
    print("\n=== 测试投标模拟 ===\n")
    
    # 创建临时ABI文件
    os.makedirs("temp_abis", exist_ok=True)
    
    # 创建简单的模拟ABI文件
    mock_abi = [{"type": "function", "name": "test", "inputs": [], "outputs": []}]
    
    for contract_name in ["AgentRegistry", "IncentiveEngine", "BidAuction", "TaskManager"]:
        abi_path = f"temp_abis/{contract_name}.json"
        with open(abi_path, "w") as f:
            json.dump(mock_abi, f)
    
    try:
        # 创建自适应投标策略实例
        strategy = AdaptiveBiddingStrategy(
            agent_address=os.getenv("AGENT_ADDRESS"),
            agent_private_key=os.getenv("AGENT_PRIVATE_KEY"),
            web3_provider=os.getenv("WEB3_PROVIDER_URL", "http://localhost:8545"),
            agent_registry_address=os.getenv("AGENT_REGISTRY_ADDRESS"),
            incentive_engine_address=os.getenv("INCENTIVE_ENGINE_ADDRESS"),
            bid_auction_address=os.getenv("BID_AUCTION_ADDRESS"),
            task_manager_address=os.getenv("TASK_MANAGER_ADDRESS"),
            agent_registry_abi_path="temp_abis/AgentRegistry.json",
            incentive_engine_abi_path="temp_abis/IncentiveEngine.json",
            bid_auction_abi_path="temp_abis/BidAuction.json",
            task_manager_abi_path="temp_abis/TaskManager.json"
        )
        
        # 自定义初始状态
        strategy.capabilities = {
            "analysis": 70,
            "generation": 60,
            "classification": 50,
            "translation": 40,
            "summarization": 30
        }
        strategy.reputation = 60
        strategy.workload = 2
        strategy.confidence_factor = 70
        strategy.risk_tolerance = 50
        
        # 模拟不同类型的任务
        task_types = [
            {
                "id": "0x1001",
                "capabilities": ["analysis", "classification"],
                "reward": 300,
                "complexity": "高"
            },
            {
                "id": "0x1002",
                "capabilities": ["generation", "translation"],
                "reward": 200,
                "complexity": "中"
            },
            {
                "id": "0x1003",
                "capabilities": ["summarization", "analysis"],
                "reward": 150,
                "complexity": "低"
            },
            {
                "id": "0x1004",
                "capabilities": ["translation", "summarization"],
                "reward": 250,
                "complexity": "中"
            },
            {
                "id": "0x1005",
                "capabilities": ["classification", "generation"],
                "reward": 350,
                "complexity": "高"
            }
        ]
        
        print("初始状态:")
        print(f"能力: {strategy.capabilities}")
        print(f"声誉: {strategy.reputation}")
        print(f"工作负载: {strategy.workload}")
        print(f"信心因子: {strategy.confidence_factor}")
        print(f"风险承受度: {strategy.risk_tolerance}")
        
        # 模拟投标计算
        print("\n模拟投标计算:")
        for task in task_types:
            # 模拟合约函数
            strategy.task_manager.functions.getTaskExecutionInfo = lambda _: [0, task["reward"], task["capabilities"], 0, "0x0"]
            strategy.incentive_engine.functions.calculateUtility = lambda _, caps, reward, workload: 80 if "analysis" in caps else 60
            
            # 计算投标
            bid_amount, utility_score = strategy.calculate_bid_for_task(task["id"], task["reward"])
            
            # 计算能力匹配度
            match_score = strategy._calculate_capability_match(task["capabilities"])
            
            # 决定是否投标
            should_bid = strategy.should_bid_on_task(task["id"])
            
            print(f"\n任务 {task['id']} ({', '.join(task['capabilities'])}):")
            print(f"  复杂度: {task['complexity']}")
            print(f"  奖励: {task['reward']}")
            print(f"  能力匹配度: {match_score}")
            print(f"  效用分数: {utility_score}")
            print(f"  投标金额: {bid_amount}")
            print(f"  是否投标: {should_bid}")
        
        # 模拟任务反馈循环
        print("\n模拟任务反馈循环:")
        
        for i in range(3):
            print(f"\n第 {i+1} 轮反馈:")
            
            # 选择一个任务类型
            task = random.choice(task_types)
            
            # 根据能力匹配度生成任务得分
            match_score = strategy._calculate_capability_match(task["capabilities"])
            base_score = 60 + match_score * 0.3  # 基础分数与匹配度相关
            random_factor = random.uniform(-5, 5)  # 随机因素
            quality = min(95, max(60, base_score + random_factor))  # 限制在60-95之间
            
            # 创建标签得分
            tag_scores = {tag: quality for tag in task["capabilities"]}
            
            print(f"任务: {task['id']} ({', '.join(task['capabilities'])})")
            print(f"得分: {quality:.1f}")
            
            # 记录旧状态
            old_confidence = strategy.confidence_factor
            old_risk = strategy.risk_tolerance
            old_capabilities = strategy.capabilities.copy()
            
            # 处理反馈
            strategy.process_task_feedback(task["id"], quality, tag_scores)
            
            # 打印变化
            print("变化:")
            print(f"  信心因子: {old_confidence} -> {strategy.confidence_factor}")
            print(f"  风险承受度: {old_risk} -> {strategy.risk_tolerance}")
            print("  能力权重变化:")
            for tag in task["capabilities"]:
                if tag in old_capabilities:
                    print(f"    {tag}: {old_capabilities[tag]} -> {strategy.capabilities[tag]}")
            
            # 暂停一下
            time.sleep(0.5)
        
        # 最终状态
        print("\n最终状态:")
        print(f"能力: {strategy.capabilities}")
        print(f"声誉: {strategy.reputation}")
        print(f"工作负载: {strategy.workload}")
        print(f"信心因子: {strategy.confidence_factor}")
        print(f"风险承受度: {strategy.risk_tolerance}")
        
        return strategy
        
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree("temp_abis", ignore_errors=True)

if __name__ == "__main__":
    # 设置随机种子，使结果可重现
    random.seed(42)
    
    # 运行测试
    strategy = test_bidding_strategy()
    simulation = test_bidding_simulation() 