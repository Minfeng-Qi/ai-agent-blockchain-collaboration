#!/usr/bin/env python3
"""
自动化合约部署和配置脚本
每次Ganache重启后自动部署合约并更新backend配置
"""

import os
import json
import sys
import subprocess
import time
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "contracts-clean"
BACKEND_DIR = PROJECT_ROOT / "backend"
ABI_DIR = BACKEND_DIR / "contracts" / "abi"

def check_ganache_running():
    """检查Ganache是否运行"""
    try:
        import subprocess
        # 使用curl检查Ganache是否响应
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json", 
             "--data", '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}',
             "http://localhost:8545"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and "result" in result.stdout
    except:
        return False

def deploy_contracts():
    """部署所有合约并返回地址映射"""
    print("🚀 开始部署智能合约...")
    
    # 切换到contracts目录
    os.chdir(CONTRACTS_DIR)
    
    try:
        # 运行部署脚本
        result = subprocess.run(
            ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "ganache"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ 合约部署失败: {result.stderr}")
            return None
        
        # 解析部署输出获取合约地址
        output = result.stdout
        print(f"✅ 部署输出:\n{output}")
        
        # 提取合约地址
        addresses = {}
        lines = output.split('\n')
        
        for line in lines:
            if "已部署到:" in line or "deployed to:" in line.lower():
                # 匹配格式如: "AgentRegistry 已部署到: 0x..."
                parts = line.strip().split()
                if len(parts) >= 3:
                    contract_name = parts[0].rstrip(':：')
                    address = parts[-1]
                    if address.startswith('0x') and len(address) == 42:
                        addresses[contract_name] = address
        
        if not addresses:
            print("⚠️  未能从输出中解析到合约地址，尝试备用方法...")
            # 备用方法：从日志文件解析
            return parse_addresses_from_logs()
        
        print(f"📋 解析到的合约地址: {addresses}")
        return addresses
        
    except subprocess.TimeoutExpired:
        print("❌ 部署超时")
        return None
    except Exception as e:
        print(f"❌ 部署过程出错: {str(e)}")
        return None

def parse_addresses_from_logs():
    """从Ganache日志解析合约地址"""
    try:
        ganache_log = PROJECT_ROOT / "ganache.log"
        if not ganache_log.exists():
            return None
        
        with open(ganache_log, 'r') as f:
            content = f.read()
        
        # 查找最近的合约创建记录
        contract_pattern = r'Contract created: (0x[a-fA-F0-9]{40})'
        matches = re.findall(contract_pattern, content)
        
        if len(matches) >= 7:
            # 按部署顺序分配地址
            contract_names = ["AgentRegistry", "ActionLogger", "IncentiveEngine", 
                            "TaskManager", "BidAuction", "MessageHub", "Learning"]
            recent_addresses = matches[-7:]  # 取最近的7个地址
            
            addresses = {}
            for name, addr in zip(contract_names, recent_addresses):
                addresses[name] = addr
            
            return addresses
        
        return None
    except Exception as e:
        print(f"❌ 从日志解析地址失败: {str(e)}")
        return None

def update_contract_service(addresses):
    """更新contract_service.py中的合约地址"""
    try:
        # 尝试导入web3生成checksum地址
        try:
            sys.path.insert(0, str(BACKEND_DIR / "venv" / "lib" / "python3.13" / "site-packages"))
            from web3 import Web3
            # 生成checksum地址
            checksum_addresses = {}
            for name, addr in addresses.items():
                checksum_addresses[name] = Web3.to_checksum_address(addr)
        except ImportError:
            # 回退到直接使用地址（大小写混合格式）
            print("⚠️  Web3未找到，使用原始地址格式")
            checksum_addresses = addresses
        
        contract_service_path = BACKEND_DIR / "services" / "contract_service.py"
        
        with open(contract_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建新的地址字典字符串
        addresses_str = "        # 自动生成的合约地址 (checksum格式)\n        contract_addresses = {\n"
        for name, addr in checksum_addresses.items():
            addresses_str += f'            "{name}": "{addr}",\n'
        addresses_str += "        }"
        
        # 替换地址配置
        pattern = r'(\s+# .*合约地址.*\n\s+contract_addresses = \{[^}]+\})'
        new_content = re.sub(pattern, addresses_str, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content == content:
            # 如果没有匹配到，尝试更宽泛的匹配
            pattern = r'(\s+contract_addresses = \{[^}]+\})'
            new_content = re.sub(pattern, addresses_str, content, flags=re.MULTILINE | re.DOTALL)
        
        with open(contract_service_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 已更新 contract_service.py")
        return True
        
    except Exception as e:
        print(f"❌ 更新contract_service失败: {str(e)}")
        return False

def copy_abi_files():
    """复制ABI文件到backend目录"""
    try:
        artifacts_dir = PROJECT_ROOT / "artifacts-clean" / "core"
        
        # 确保ABI目录存在
        ABI_DIR.mkdir(parents=True, exist_ok=True)
        
        # 需要复制的合约
        contracts = ["AgentRegistry", "ActionLogger", "IncentiveEngine", 
                    "TaskManager", "BidAuction", "MessageHub", "Learning"]
        
        for contract in contracts:
            src_file = artifacts_dir / f"{contract}.sol" / f"{contract}.json"
            dst_file = ABI_DIR / f"{contract}.json"
            
            if src_file.exists():
                import shutil
                shutil.copy2(src_file, dst_file)
                print(f"✅ 复制 {contract}.json")
            else:
                print(f"⚠️  {contract}.json 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 复制ABI文件失败: {str(e)}")
        return False

def init_contract_data():
    """初始化合约数据"""
    try:
        print("📊 开始初始化合约数据...")
        
        # 切换到backend目录
        os.chdir(BACKEND_DIR)
        
        # 运行数据初始化脚本
        result = subprocess.run(
            [sys.executable, "scripts/init_contract_data.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ 合约数据初始化成功")
            print(result.stdout)
            return True
        else:
            print(f"⚠️  合约数据初始化失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 初始化合约数据出错: {str(e)}")
        return False

def restart_backend():
    """重启backend服务"""
    try:
        print("🔄 重启backend服务...")
        
        # 杀死现有进程
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        subprocess.run(["pkill", "-f", "python.*backend"], capture_output=True)
        
        time.sleep(2)
        
        # 启动新的backend服务
        os.chdir(PROJECT_ROOT)
        subprocess.Popen([
            sys.executable, "-c", 
            "import sys; sys.path.append('.'); from backend.main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001)"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        print("✅ Backend服务已重启")
        return True
        
    except Exception as e:
        print(f"❌ 重启backend失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🔧 智能合约自动化部署工具")
    print("=" * 50)
    
    # 检查Ganache是否运行
    if not check_ganache_running():
        print("❌ Ganache未运行，请先启动Ganache")
        sys.exit(1)
    
    print("✅ Ganache正在运行")
    
    # 1. 部署合约
    addresses = deploy_contracts()
    if not addresses:
        print("❌ 合约部署失败")
        sys.exit(1)
    
    # 2. 复制ABI文件
    if not copy_abi_files():
        print("❌ ABI文件复制失败")
        sys.exit(1)
    
    # 3. 更新contract_service配置
    if not update_contract_service(addresses):
        print("❌ 更新合约服务配置失败")
        sys.exit(1)
    
    # 4. 初始化合约数据
    if not init_contract_data():
        print("⚠️  合约数据初始化失败，但继续执行...")
    
    # 5. 重启backend服务
    if not restart_backend():
        print("❌ Backend重启失败")
        sys.exit(1)
    
    print("\n🎉 自动化部署完成！")
    print("📋 合约地址:")
    for name, addr in addresses.items():
        print(f"   {name}: {addr}")
    
    print(f"\n🌐 Backend服务: http://localhost:8001")
    print("🔗 可以开始使用区块链数据了！")

if __name__ == "__main__":
    main()