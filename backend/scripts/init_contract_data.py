#!/usr/bin/env python3
"""
合约数据初始化脚本
用于为部署的合约添加样本数据，以便前端dashboard能够正确显示数据
"""

import os
import sys
import json
import time
from web3 import Web3, HTTPProvider
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 区块链连接配置
BLOCKCHAIN_RPC_URL = "http://localhost:8545"
CHAIN_ID = 1337

# 使用Ganache的第一个账户作为交易发送者
PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
ACCOUNT_ADDRESS = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

# 合约地址 - 使用最新部署的地址
CONTRACT_ADDRESSES = {
    "AgentRegistry": "0xFC628dd79137395F3C9744e33b1c5DE554D94882",
    "TaskManager": "0x4bf749ec68270027C5910220CEAB30Cc284c7BA2",
    "Learning": "0xA586074FA4Fe3E546A132a16238abe37951D41fE"
}

def load_contract_abi(contract_name):
    """加载合约ABI"""
    abi_path = os.path.join(os.path.dirname(__file__), '..', 'contracts', 'abi', f'{contract_name}.json')
    with open(abi_path, 'r') as f:
        contract_data = json.load(f)
    return contract_data['abi']

def initialize_web3():
    """初始化Web3连接"""
    w3 = Web3(HTTPProvider(BLOCKCHAIN_RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    if not w3.is_connected():
        raise Exception("无法连接到区块链网络")
    
    print(f"✅ 已连接到区块链网络: {BLOCKCHAIN_RPC_URL}")
    return w3

def get_contract_instance(w3, contract_name):
    """获取合约实例"""
    abi = load_contract_abi(contract_name)
    address = CONTRACT_ADDRESSES[contract_name]
    return w3.eth.contract(address=address, abi=abi)

def register_agents(w3, agent_registry):
    """注册示例代理"""
    print("\n🤖 开始注册代理...")
    
    # 示例代理数据
    agents = [
        {
            "name": "AI Data Analyst",
            "metadataURI": "https://example.com/agents/data-analyst",
            "agentType": 0,  # 假设0代表分析类型
            "capabilities": ["data_analysis", "visualization", "reporting"]
        },
        {
            "name": "AI Code Generator",
            "metadataURI": "https://example.com/agents/code-generator", 
            "agentType": 1,  # 假设1代表开发类型
            "capabilities": ["code_generation", "debugging", "optimization"]
        },
        {
            "name": "AI Content Creator",
            "metadataURI": "https://example.com/agents/content-creator",
            "agentType": 2,  # 假设2代表创作类型
            "capabilities": ["content_writing", "translation", "summarization"]
        },
        {
            "name": "AI Research Assistant",
            "metadataURI": "https://example.com/agents/research-assistant",
            "agentType": 0,
            "capabilities": ["research", "analysis", "documentation"]
        },
        {
            "name": "AI QA Tester",
            "metadataURI": "https://example.com/agents/qa-tester",
            "agentType": 1,
            "capabilities": ["testing", "quality_assurance", "bug_detection"]
        }
    ]
    
    registered_agents = []
    
    for agent in agents:
        try:
            # 构建交易
            tx = agent_registry.functions.registerAgent(
                agent["name"],
                agent["metadataURI"],
                agent["agentType"]
            ).build_transaction({
                'from': ACCOUNT_ADDRESS,
                'gas': 2000000,
                'gasPrice': w3.to_wei('20', 'gwei'),
                'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
            })
            
            # 签名并发送交易
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # 等待交易确认
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ 已注册代理: {agent['name']}")
                registered_agents.append(agent)
            else:
                print(f"❌ 注册代理失败: {agent['name']}")
                
        except Exception as e:
            print(f"❌ 注册代理出错 {agent['name']}: {str(e)}")
    
    print(f"📊 共注册了 {len(registered_agents)} 个代理")
    return registered_agents

def create_tasks(w3, task_manager):
    """创建示例任务"""
    print("\n📋 开始创建任务...")
    
    # 示例任务数据
    tasks = [
        {
            "metadataURI": "https://example.com/tasks/data-analysis-project",
            "capabilities": ["data_analysis", "visualization"],
            "minReputation": 100,
            "reward": w3.to_wei('1', 'ether'),
            "deadline": int(time.time()) + 86400 * 7  # 7天后
        },
        {
            "metadataURI": "https://example.com/tasks/website-development",
            "capabilities": ["code_generation", "debugging"],
            "minReputation": 200,
            "reward": w3.to_wei('2', 'ether'),
            "deadline": int(time.time()) + 86400 * 14  # 14天后
        },
        {
            "metadataURI": "https://example.com/tasks/content-writing",
            "capabilities": ["content_writing", "translation"],
            "minReputation": 50,
            "reward": w3.to_wei('0.5', 'ether'),
            "deadline": int(time.time()) + 86400 * 3  # 3天后
        },
        {
            "metadataURI": "https://example.com/tasks/research-report",
            "capabilities": ["research", "analysis"],
            "minReputation": 150,
            "reward": w3.to_wei('1.5', 'ether'),
            "deadline": int(time.time()) + 86400 * 10  # 10天后
        },
        {
            "metadataURI": "https://example.com/tasks/quality-testing",
            "capabilities": ["testing", "quality_assurance"],
            "minReputation": 80,
            "reward": w3.to_wei('0.8', 'ether'),
            "deadline": int(time.time()) + 86400 * 5  # 5天后
        }
    ]
    
    created_tasks = []
    
    for task in tasks:
        try:
            # 构建交易
            tx = task_manager.functions.createTask(
                task["metadataURI"],
                task["capabilities"],
                task["minReputation"],
                task["reward"],
                task["deadline"]
            ).build_transaction({
                'from': ACCOUNT_ADDRESS,
                'gas': 2000000,
                'gasPrice': w3.to_wei('20', 'gwei'),
                'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
            })
            
            # 签名并发送交易
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # 等待交易确认
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ 已创建任务: {task['metadataURI']}")
                created_tasks.append(task)
            else:
                print(f"❌ 创建任务失败: {task['metadataURI']}")
                
        except Exception as e:
            print(f"❌ 创建任务出错 {task['metadataURI']}: {str(e)}")
    
    print(f"📊 共创建了 {len(created_tasks)} 个任务")
    return created_tasks

def main():
    """主函数"""
    print("🚀 开始初始化合约数据...")
    
    try:
        # 初始化Web3
        w3 = initialize_web3()
        
        # 获取合约实例
        agent_registry = get_contract_instance(w3, "AgentRegistry")
        task_manager = get_contract_instance(w3, "TaskManager")
        learning = get_contract_instance(w3, "Learning")
        
        print(f"📋 合约地址:")
        for name, address in CONTRACT_ADDRESSES.items():
            print(f"  {name}: {address}")
        
        # 注册代理
        registered_agents = register_agents(w3, agent_registry)
        
        # 创建任务
        created_tasks = create_tasks(w3, task_manager)
        
        print(f"\n🎉 数据初始化完成!")
        print(f"   代理数量: {len(registered_agents)}")
        print(f"   任务数量: {len(created_tasks)}")
        print(f"   区块链网络: {BLOCKCHAIN_RPC_URL}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()