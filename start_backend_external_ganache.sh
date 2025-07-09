#!/bin/bash

# LLM区块链项目后端启动脚本 (连接外部Ganache)
echo "🚀 启动LLM区块链后端系统 (连接外部Ganache)..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 检查是否在正确目录
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "contracts-clean" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 停止现有后端服务
echo -e "${YELLOW}🛑 停止现有后端服务...${NC}"
pkill -f "uvicorn.*backend" 2>/dev/null
sleep 2

# 2. 检查外部Ganache连接
echo -e "${BLUE}🔍 检查外部Ganache连接...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8545 > /dev/null 2>&1; then
        # 检查chainId
        CHAIN_ID=$(curl -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://localhost:8545 | jq -r '.result' 2>/dev/null)
        if [ "$CHAIN_ID" = "0x1691" ] || [ "$CHAIN_ID" = "0x539" ]; then
            echo -e "${GREEN}✅ 外部Ganache连接成功 (ChainID: $CHAIN_ID)${NC}"
            break
        else
            echo -e "${YELLOW}⚠️  ChainID不匹配，期望0x1691(5777)或0x539(1337)，实际: $CHAIN_ID${NC}"
        fi
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 无法连接到外部Ganache，请确保:${NC}"
        echo "  1. Ganache正在运行在端口8545"
        echo "  2. ChainID设置为5777或1337"
        echo "  3. 主机绑定允许本地连接"
        exit 1
    fi
    echo -e "${YELLOW}⏳ 等待外部Ganache连接... (${i}/10)${NC}"
    sleep 2
done

# 3. 检查合约依赖
echo -e "${BLUE}📦 检查合约依赖...${NC}"
cd contracts-clean
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 安装合约依赖...${NC}"
    npm install
fi

# 4. 部署智能合约
echo -e "${BLUE}📜 部署智能合约到外部Ganache...${NC}"
DEPLOY_OUTPUT=$(npx hardhat run scripts/deploy.js --network localhost 2>&1)
DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -ne 0 ]; then
    echo -e "${RED}❌ 合约部署失败:${NC}"
    echo "$DEPLOY_OUTPUT"
    echo ""
    echo -e "${YELLOW}💡 可能的解决方案:${NC}"
    echo "  1. 确保Ganache账户有足够余额"
    echo "  2. 检查Ganache网络配置是否正确"
    echo "  3. 尝试重启Ganache"
    exit 1
fi

echo -e "${GREEN}✅ 合约部署成功${NC}"
echo "$DEPLOY_OUTPUT"

# 提取合约地址
AGENT_REGISTRY=$(echo "$DEPLOY_OUTPUT" | grep "AgentRegistry:" | awk '{print $2}')
ACTION_LOGGER=$(echo "$DEPLOY_OUTPUT" | grep "ActionLogger:" | awk '{print $2}')
INCENTIVE_ENGINE=$(echo "$DEPLOY_OUTPUT" | grep "IncentiveEngine:" | awk '{print $2}')
TASK_MANAGER=$(echo "$DEPLOY_OUTPUT" | grep "TaskManager:" | awk '{print $2}')
BID_AUCTION=$(echo "$DEPLOY_OUTPUT" | grep "BidAuction:" | awk '{print $2}')
MESSAGE_HUB=$(echo "$DEPLOY_OUTPUT" | grep "MessageHub:" | awk '{print $2}')
LEARNING=$(echo "$DEPLOY_OUTPUT" | grep "Learning:" | awk '{print $2}')

# 5. 复制ABI文件到后端
echo -e "${BLUE}📁 复制ABI文件...${NC}"
cp -r ../artifacts-clean/core/*.sol/*.json ../backend/contracts/abi/
echo -e "${GREEN}✅ ABI文件复制完成${NC}"

# 6. 更新后端合约地址配置
echo -e "${BLUE}🔧 更新后端合约配置...${NC}"
CONTRACT_SERVICE_FILE="../backend/services/contract_service.py"

# 创建临时文件进行替换
cat > /tmp/contract_addresses.txt << EOF
        # 自动生成的合约地址 (checksum格式)
        contract_addresses = {
            "AgentRegistry": "$AGENT_REGISTRY",
            "ActionLogger": "$ACTION_LOGGER",
            "IncentiveEngine": "$INCENTIVE_ENGINE",
            "TaskManager": "$TASK_MANAGER",
            "BidAuction": "$BID_AUCTION",
            "MessageHub": "$MESSAGE_HUB",
            "Learning": "$LEARNING",
        }
EOF

# 使用python进行精确替换
python3 << EOF
import re

# 读取合约服务文件
with open('$CONTRACT_SERVICE_FILE', 'r') as f:
    content = f.read()

# 读取新的地址配置
with open('/tmp/contract_addresses.txt', 'r') as f:
    new_addresses = f.read()

# 替换合约地址配置
pattern = r'(\s+# .*合约地址.*\n\s+contract_addresses = \{[^}]+\})'
content = re.sub(pattern, new_addresses, content, flags=re.MULTILINE | re.DOTALL)

# 如果没有匹配到，尝试更简单的模式
if "AgentRegistry\": \"$AGENT_REGISTRY" not in content:
    pattern = r'(\s+contract_addresses = \{[^}]+\})'
    content = re.sub(pattern, new_addresses, content, flags=re.MULTILINE | re.DOTALL)

# 写回文件
with open('$CONTRACT_SERVICE_FILE', 'w') as f:
    f.write(content)

print("✅ 合约地址更新完成")
EOF

# 清理临时文件
rm -f /tmp/contract_addresses.txt

# 7. 检查Python虚拟环境
echo -e "${BLUE}🐍 检查Python虚拟环境...${NC}"
cd ../backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 创建Python虚拟环境...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 8. 启动后端API服务
echo -e "${BLUE}🔧 启动后端API服务...${NC}"
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > backend.pid

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端启动...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        echo "查看日志: tail -f backend/backend.log"
        exit 1
    fi
    sleep 2
done

# 9. 验证服务状态
echo -e "${BLUE}🔍 验证服务状态...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8001/health | jq -r '.status' 2>/dev/null)

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${YELLOW}⚠️  服务状态检查失败，但服务可能仍在正常运行${NC}"
fi

# 10. 显示启动完成信息
echo ""
echo -e "${GREEN}🎉 后端系统启动完成！${NC}"
echo "=========================================="
echo -e "${BLUE}📊 服务信息:${NC}"
echo "  🔗 外部Ganache: http://localhost:8545 (由用户管理)"
echo "  🔧 后端API: http://localhost:8001"
echo "  📚 API文档: http://localhost:8001/docs"
echo ""
echo -e "${BLUE}📋 合约地址:${NC}"
echo "  AgentRegistry: $AGENT_REGISTRY"
echo "  ActionLogger: $ACTION_LOGGER"
echo "  IncentiveEngine: $INCENTIVE_ENGINE"
echo "  TaskManager: $TASK_MANAGER"
echo "  BidAuction: $BID_AUCTION"
echo "  MessageHub: $MESSAGE_HUB"
echo "  Learning: $LEARNING"
echo ""
echo -e "${BLUE}🛠️  管理命令:${NC}"
echo "  停止后端: ./stop_backend_only.sh"
echo "  查看日志: tail -f backend/backend.log"
echo "  重启后端: ./start_backend_external_ganache.sh"
echo ""
echo -e "${YELLOW}💡 提示: ${NC}"
echo "  - 后端服务在后台运行"
echo "  - Ganache由用户外部管理，脚本不会启动/停止"
echo "  - 可以通过API文档测试接口"