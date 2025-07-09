#!/usr/bin/env python3
"""
创建测试事件脚本
用于在智能合约中生成测试数据，触发各种事件
"""

import os
import sys
import json
import time
from web3 import Web3
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware

# 配置
GANACHE_URL = "http://127.0.0.1:8545"
MNEMONIC = "myth like bonus scare over problem client lizard pioneer submit female collect"

# 合约地址
CONTRACT_ADDRESSES = {
    "AgentRegistry": "0x884dd07b864c7e3Ecef01BEfFEB07731a92B9d53",
    "ActionLogger": "0x56F52B666D53a6555182F5Cc56d73c0c08b36a98",
    "IncentiveEngine": "0x320ffb6049caE8C0A30F07773fd01E615E123fa8",
    "TaskManager": "0x9bf9F7F340C7310f32d33B57E4AccDb44c27E4a4",
    "BidAuction": "0xA28A1DB2D920Ad8E1Db8B72a87628f1bE0B400A1",
    "MessageHub": "0xDE87D8becB4df477415Cbe74815BF7D2483120E9",
    "Learning": "0x5d862DB17aAb6e906ddb1234f3e01db2D835F265"
}

def setup_web3():
    """设置Web3连接"""
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if w3.is_connected():
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        print("✅ Connected to Ganache")
        return w3
    else:
        print("❌ Failed to connect to Ganache")
        return None

def load_contract_abi(contract_name):
    """加载合约ABI"""
    # 尝试不同的路径
    possible_paths = [
        f"backend/contracts/abi/{contract_name}.json",
        f"contracts/abi/{contract_name}.json",
        f"../backend/contracts/abi/{contract_name}.json"
    ]
    
    for abi_path in possible_paths:
        if os.path.exists(abi_path):
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
            return contract_data.get("abi")
    
    print(f"❌ ABI file not found for {contract_name} in any of: {possible_paths}")
    return None

def get_account_from_mnemonic(w3, index=0):
    """从助记词获取账户"""
    from eth_account import Account
    Account.enable_unaudited_hdwallet_features()
    
    # 生成账户
    account = Account.from_mnemonic(MNEMONIC, account_path=f"m/44'/60'/0'/0/{index}")
    return account

def create_test_agents(w3):
    """创建测试智能体"""
    print("🤖 Creating test agents...")
    
    # 加载AgentRegistry合约
    abi = load_contract_abi("AgentRegistry")
    if not abi:
        return []
    
    contract_address = CONTRACT_ADDRESSES["AgentRegistry"]
    agent_registry = w3.eth.contract(address=contract_address, abi=abi)
    
    agents = []
    agent_data = [
        {
            "name": "DataAnalysisAgent",
            "metadataURI": "ipfs://QmDataAnalysisAgent123",
            "agentType": 1  # LLM type
        },
        {
            "name": "TextGenerationAgent", 
            "metadataURI": "ipfs://QmTextGenerationAgent456",
            "agentType": 1  # LLM type
        },
        {
            "name": "ClassificationAgent",
            "metadataURI": "ipfs://QmClassificationAgent789",
            "agentType": 1  # LLM type
        }
    ]
    
    for i, data in enumerate(agent_data):
        try:
            # 获取账户
            account = get_account_from_mnemonic(w3, i + 1)
            agents.append(account)
            
            # 准备交易
            nonce = w3.eth.get_transaction_count(account.address)
            
            # 构建交易
            transaction = agent_registry.functions.registerAgent(
                data["name"],
                data["metadataURI"],
                data["agentType"]
            ).build_transaction({
                'from': account.address,
                'gas': 3000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            # 签名交易
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)
            
            # 发送交易
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # 等待确认
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Registered agent: {data['name']} at {account.address}")
            else:
                print(f"❌ Failed to register agent: {data['name']}")
                
        except Exception as e:
            print(f"❌ Error registering agent {data['name']}: {str(e)}")
    
    return agents

def create_test_tasks(w3, agents):
    """创建测试任务"""
    print("📋 Creating test tasks...")
    
    # 加载TaskManager合约
    abi = load_contract_abi("TaskManager")
    if not abi:
        return []
    
    contract_address = CONTRACT_ADDRESSES["TaskManager"]
    task_manager = w3.eth.contract(address=contract_address, abi=abi)
    
    # 使用第一个账户作为任务创建者
    creator_account = get_account_from_mnemonic(w3, 0)
    
    task_data = [
        {
            "metadataURI": "ipfs://QmTask1DataAnalysis",
            "capabilities": ["data_analysis", "statistics"],
            "minReputation": 30,
            "reward": w3.to_wei(0.1, 'ether'),
            "deadline": int(time.time()) + 86400  # 24 hours
        },
        {
            "metadataURI": "ipfs://QmTask2TextGeneration", 
            "capabilities": ["text_generation", "nlp"],
            "minReputation": 40,
            "reward": w3.to_wei(0.15, 'ether'),
            "deadline": int(time.time()) + 172800  # 48 hours
        },
        {
            "metadataURI": "ipfs://QmTask3Classification",
            "capabilities": ["classification", "machine_learning"],
            "minReputation": 35,
            "reward": w3.to_wei(0.12, 'ether'),
            "deadline": int(time.time()) + 259200  # 72 hours
        }
    ]
    
    task_ids = []
    for data in task_data:
        try:
            # 准备交易
            nonce = w3.eth.get_transaction_count(creator_account.address)
            
            # 构建交易
            transaction = task_manager.functions.createTask(
                data["metadataURI"],
                data["capabilities"],
                data["minReputation"],
                data["reward"],
                data["deadline"]
            ).build_transaction({
                'from': creator_account.address,
                'gas': 3000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            # 签名交易
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=creator_account.key)
            
            # 发送交易
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # 等待确认
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Created task: {data['metadataURI']}")
                # 从事件日志中获取任务ID
                for log in receipt.logs:
                    try:
                        decoded_log = task_manager.events.TaskCreated().process_log(log)
                        task_id = decoded_log['args']['taskId']
                        task_ids.append(task_id)
                        print(f"   Task ID: {task_id.hex()}")
                        break
                    except:
                        continue
            else:
                print(f"❌ Failed to create task: {data['metadataURI']}")
                
        except Exception as e:
            print(f"❌ Error creating task {data['metadataURI']}: {str(e)}")
    
    return task_ids

def create_learning_events(w3, agents):
    """创建学习事件"""
    print("🧠 Creating learning events...")
    
    # 加载Learning合约
    abi = load_contract_abi("Learning")
    if not abi:
        return
    
    contract_address = CONTRACT_ADDRESSES["Learning"]
    learning = w3.eth.contract(address=contract_address, abi=abi)
    
    # 创建各种类型的学习事件
    events = [
        {
            "agent_index": 0,
            "type": "skill_improvement",
            "params": ["data_analysis", 65, 85]
        },
        {
            "agent_index": 1,
            "type": "skill_improvement", 
            "params": ["text_generation", 70, 90]
        },
        {
            "agent_index": 2,
            "type": "skill_improvement",
            "params": ["classification", 60, 80]
        },
        {
            "agent_index": 0,
            "type": "task_completion",
            "params": [w3.keccak(text="task123"), 85, 3600]  # taskId, qualityScore, timeSpent
        },
        {
            "agent_index": 1,
            "type": "learning_milestone",
            "params": ["tasks_completed", 10]
        }
    ]
    
    for event in events:
        try:
            agent = agents[event["agent_index"]]
            nonce = w3.eth.get_transaction_count(agent.address)
            
            if event["type"] == "skill_improvement":
                skill_tag, old_score, new_score = event["params"]
                transaction = learning.functions.recordSkillImprovement(
                    agent.address, skill_tag, old_score, new_score
                ).build_transaction({
                    'from': agent.address,
                    'gas': 3000000,
                    'gasPrice': w3.eth.gas_price,
                    'nonce': nonce
                })
                
            elif event["type"] == "task_completion":
                task_id, quality_score, time_spent = event["params"]
                transaction = learning.functions.recordTaskCompletion(
                    agent.address, task_id, quality_score, time_spent
                ).build_transaction({
                    'from': agent.address,
                    'gas': 3000000,
                    'gasPrice': w3.eth.gas_price,
                    'nonce': nonce
                })
                
            elif event["type"] == "learning_milestone":
                milestone_type, value = event["params"]
                transaction = learning.functions.recordLearningMilestone(
                    agent.address, milestone_type, value
                ).build_transaction({
                    'from': agent.address,
                    'gas': 3000000,
                    'gasPrice': w3.eth.gas_price,
                    'nonce': nonce
                })
            
            # 签名并发送交易
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=agent.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Created {event['type']} event for agent {agent.address}")
            else:
                print(f"❌ Failed to create {event['type']} event")
                
        except Exception as e:
            print(f"❌ Error creating learning event: {str(e)}")

def main():
    """主函数"""
    print("🚀 Starting test event creation script...")
    
    # 设置Web3连接
    w3 = setup_web3()
    if not w3:
        return
    
    print(f"📊 Network ID: {w3.eth.chain_id}")
    print(f"📊 Latest block: {w3.eth.block_number}")
    
    # 创建测试智能体
    agents = create_test_agents(w3)
    if not agents:
        print("❌ No agents created, stopping...")
        return
    
    # 等待一下让区块确认
    print("⏳ Waiting for block confirmations...")
    time.sleep(5)
    
    # 创建测试任务
    task_ids = create_test_tasks(w3, agents)
    
    # 等待一下
    time.sleep(5)
    
    # 创建学习事件
    create_learning_events(w3, agents)
    
    print("🎉 Test event creation completed!")
    print(f"📊 Created {len(agents)} agents")
    print(f"📊 Created {len(task_ids)} tasks")
    print("📊 Created multiple learning events")
    
    # 显示一些统计信息
    print("\n📊 Current blockchain stats:")
    print(f"   Latest block: {w3.eth.block_number}")
    
    # 检查最新几个区块的交易
    latest_block = w3.eth.get_block(w3.eth.block_number, full_transactions=True)
    print(f"   Latest block transactions: {len(latest_block.transactions)}")

if __name__ == "__main__":
    main()