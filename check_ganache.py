#!/usr/bin/env python3
"""
检查Ganache状态
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services import contract_service

def check_ganache():
    """检查Ganache状态"""
    print("🔍 检查Ganache状态...")
    
    w3 = contract_service.w3
    print(f"📡 Web3连接状态: {w3.is_connected()}")
    
    if w3.is_connected():
        print(f"📊 最新区块: {w3.eth.block_number}")
        print(f"🔗 网络ID: {w3.eth.chain_id}")
        
        # 获取最近几个区块的信息
        latest_block = w3.eth.block_number
        print(f"\n📋 最近5个区块:")
        for i in range(max(0, latest_block - 4), latest_block + 1):
            try:
                block = w3.eth.get_block(i)
                print(f"   区块 {i}: {len(block.transactions)} 笔交易")
                
                # 检查交易
                for tx_hash in block.transactions:
                    tx = w3.eth.get_transaction(tx_hash)
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    if receipt.contractAddress:
                        print(f"      📦 合约部署: {receipt.contractAddress}")
                        
            except Exception as e:
                print(f"   区块 {i}: 错误 - {str(e)}")
        
        # 检查指定地址的代码
        addresses = [
            "0x5FbDB2315678afecb367f032d93F642f64180aa3",  # AgentRegistry
            "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",  # ActionLogger
        ]
        
        print(f"\n📦 检查合约地址:")
        for addr in addresses:
            code = w3.eth.get_code(addr)
            print(f"   {addr}: {len(code)} bytes")
            
    else:
        print("❌ Web3连接失败")

if __name__ == "__main__":
    check_ganache()