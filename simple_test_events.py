#!/usr/bin/env python3
"""
简化的测试事件创建脚本
使用后端的现有方法来创建测试数据
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services import contract_service

def create_test_events():
    """创建测试事件"""
    print("🚀 Creating test events using backend services...")
    
    # 初始化合约
    success = contract_service.initialize_contracts()
    if not success:
        print("❌ Failed to initialize contracts")
        return
    
    print("✅ Contracts initialized successfully")
    
    # 检查连接状态
    status = contract_service.get_connection_status()
    print(f"📊 Network ID: {status.get('network_id')}")
    print(f"📊 Latest block: {status.get('latest_block')}")
    print(f"📊 Connected: {status.get('connected')}")
    
    # 使用Learning合约创建一些学习事件
    if contract_service.learning_contract:
        try:
            # 使用部署者账户（有资金的账户）
            from web3 import Web3
            w3 = contract_service.w3
            
            # 获取账户（使用第一个账户，通常有足够的ETH）
            accounts = w3.eth.accounts
            if not accounts:
                print("❌ No accounts available")
                return
                
            deployer_account = accounts[0]
            print(f"🔑 Using account: {deployer_account}")
            print(f"💰 Balance: {w3.from_wei(w3.eth.get_balance(deployer_account), 'ether')} ETH")
            
            # 创建一些学习事件
            events_to_create = [
                {
                    "agent_address": deployer_account,
                    "event_type": "skill_assessment",
                    "data": '{"skill": "data_analysis", "score": 85, "timestamp": 1640995200}'
                },
                {
                    "agent_address": deployer_account,
                    "event_type": "task_completion",
                    "data": '{"task_id": "task_001", "quality_score": 92, "completion_time": 3600}'
                },
                {
                    "agent_address": deployer_account,
                    "event_type": "collaboration",
                    "data": '{"partner": "0x742d35Cc6634C0532925a3b8D24B9e2b5f7b4b72", "type": "knowledge_sharing"}'
                },
                {
                    "agent_address": deployer_account,
                    "event_type": "milestone_reached",
                    "data": '{"milestone": "100_tasks_completed", "value": 100}'
                }
            ]
            
            for i, event_data in enumerate(events_to_create):
                try:
                    # 准备交易数据
                    tx_data = {
                        "from": deployer_account,
                        "gas": 3000000,
                        "gasPrice": w3.eth.gas_price,
                        "nonce": w3.eth.get_transaction_count(deployer_account)
                    }
                    
                    # 调用合约方法
                    tx_hash = contract_service.learning_contract.functions.recordEvent(
                        event_data["agent_address"],
                        event_data["event_type"],
                        event_data["data"]
                    ).transact(tx_data)
                    
                    # 等待交易确认
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    if receipt.status == 1:
                        print(f"✅ Created learning event {i+1}: {event_data['event_type']}")
                        
                        # 解析事件日志
                        for log in receipt.logs:
                            try:
                                decoded_log = contract_service.learning_contract.events.LearningEventRecorded().process_log(log)
                                event_id = decoded_log['args']['eventId']
                                print(f"   📋 Event ID: {event_id}")
                            except:
                                continue
                    else:
                        print(f"❌ Failed to create learning event {i+1}")
                        
                except Exception as e:
                    print(f"❌ Error creating event {i+1}: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Error accessing Learning contract: {str(e)}")
    
    print("🎉 Test event creation completed!")

if __name__ == "__main__":
    create_test_events()