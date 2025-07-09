#!/usr/bin/env python3
"""
调试合约问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services import contract_service

def debug_contract():
    """调试合约"""
    print("🔍 调试合约问题...")
    
    # 检查基本连接
    w3 = contract_service.w3
    print(f"📡 Web3连接状态: {w3.is_connected()}")
    print(f"📊 最新区块: {w3.eth.block_number}")
    
    # 检查合约地址处是否有代码
    agent_registry_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    code = w3.eth.get_code(agent_registry_address)
    print(f"🔗 合约地址: {agent_registry_address}")
    print(f"📦 合约代码长度: {len(code)} bytes")
    print(f"📦 合约代码存在: {len(code) > 0}")
    
    if len(code) > 0:
        print("✅ 合约已部署")
        
        # 尝试直接调用合约
        print("\n🔍 尝试直接调用合约...")
        try:
            # 初始化合约
            success = contract_service.initialize_contracts()
            print(f"合约初始化状态: {success}")
            
            if success and contract_service.agent_registry_contract:
                print("✅ 合约实例创建成功")
                
                # 检查ABI中的函数
                print("\n📋 检查ABI中的函数...")
                functions = [name for name in dir(contract_service.agent_registry_contract.functions) if not name.startswith('_')]
                print(f"可用函数: {functions}")
                
                # 尝试调用一个简单的函数
                print("\n🔍 尝试调用简单函数...")
                try:
                    # 尝试调用owner函数
                    if hasattr(contract_service.agent_registry_contract.functions, 'owner'):
                        owner = contract_service.agent_registry_contract.functions.owner().call()
                        print(f"✅ owner(): {owner}")
                    else:
                        print("❌ owner函数不存在")
                        
                    # 尝试调用getAgentCount
                    if hasattr(contract_service.agent_registry_contract.functions, 'getAgentCount'):
                        print("✅ getAgentCount函数存在")
                        try:
                            count = contract_service.agent_registry_contract.functions.getAgentCount().call()
                            print(f"✅ getAgentCount(): {count}")
                        except Exception as e:
                            print(f"❌ getAgentCount()调用失败: {str(e)}")
                    else:
                        print("❌ getAgentCount函数不存在")
                        
                except Exception as e:
                    print(f"❌ 调用函数失败: {str(e)}")
            else:
                print("❌ 合约实例创建失败")
                
        except Exception as e:
            print(f"❌ 合约初始化失败: {str(e)}")
    else:
        print("❌ 合约未部署或地址错误")

if __name__ == "__main__":
    debug_contract()