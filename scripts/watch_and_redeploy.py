#!/usr/bin/env python3
"""
智能合约监控和自动重部署脚本
监控Ganache状态，检测到重启时自动重新部署合约
"""

import time
import json
import requests
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def check_ganache_connection():
    """检查Ganache连接状态"""
    try:
        response = requests.post(
            "http://localhost:8545",
            json={"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1},
            timeout=3
        )
        return response.status_code == 200
    except:
        return False

def get_block_number():
    """获取当前区块号"""
    try:
        response = requests.post(
            "http://localhost:8545",
            json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
            timeout=3
        )
        if response.status_code == 200:
            result = response.json()
            return int(result.get("result", "0x0"), 16)
        return None
    except:
        return None

def get_deployed_contracts():
    """获取已部署的合约列表"""
    try:
        response = requests.post(
            "http://localhost:8545",
            json={"jsonrpc": "2.0", "method": "eth_getCode", "params": ["0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab", "latest"], "id": 1},
            timeout=3
        )
        if response.status_code == 200:
            result = response.json()
            code = result.get("result", "0x")
            return len(code) > 2  # 有代码表示合约存在
        return False
    except:
        return False

def auto_redeploy():
    """自动重新部署合约"""
    print("🔄 检测到Ganache重启，开始自动重新部署...")
    
    try:
        # 运行自动部署脚本
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "auto_deploy.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ 自动重新部署成功！")
            return True
        else:
            print(f"❌ 自动重新部署失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重新部署过程出错: {str(e)}")
        return False

def main():
    """主监控循环"""
    print("👁️  启动智能合约监控服务")
    print("监控Ganache状态，自动处理重启和重新部署")
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    
    last_block = None
    contracts_deployed = False
    ganache_was_down = False
    
    while True:
        try:
            # 检查Ganache连接
            if not check_ganache_connection():
                if not ganache_was_down:
                    print("⚠️  Ganache连接丢失")
                    ganache_was_down = True
                    contracts_deployed = False
                time.sleep(5)
                continue
            
            # Ganache重新连接
            if ganache_was_down:
                print("✅ Ganache重新连接")
                ganache_was_down = False
                time.sleep(2)  # 等待Ganache完全启动
            
            # 获取当前区块号
            current_block = get_block_number()
            
            # 检测是否为新的Ganache实例 (区块号重置)
            if last_block is not None and current_block is not None:
                if current_block < last_block:
                    print(f"🔄 检测到Ganache重启 (区块号: {last_block} -> {current_block})")
                    contracts_deployed = False
            
            last_block = current_block
            
            # 检查合约是否部署
            if not contracts_deployed:
                if not get_deployed_contracts():
                    print("📜 检测到需要部署合约")
                    if auto_redeploy():
                        contracts_deployed = True
                        print("🎉 系统恢复正常运行")
                    else:
                        print("⏰ 30秒后重试...")
                        time.sleep(30)
                        continue
                else:
                    contracts_deployed = True
                    print("✅ 合约已存在，系统正常运行")
            
            # 正常监控状态
            if current_block is not None:
                print(f"📊 监控中... (区块: {current_block})", end='\r')
            
            time.sleep(10)  # 每10秒检查一次
            
        except KeyboardInterrupt:
            print("\n\n🛑 监控服务已停止")
            break
        except Exception as e:
            print(f"\n❌ 监控过程出错: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()