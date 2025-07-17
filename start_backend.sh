#!/bin/bash

# 改进的LLM区块链项目后端启动脚本
echo "🚀 启动LLM区块链后端系统 (改进版)..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 错误处理函数
error_exit() {
    echo -e "${RED}❌ 错误: $1${NC}"
    exit 1
}

# 成功消息函数
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 警告消息函数
warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 信息消息函数
info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        error_exit "命令 $1 未找到，请先安装"
    fi
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local max_attempts=$2
    local service_name=$3
    
    for i in $(seq 1 $max_attempts); do
        if curl -s "$url" > /dev/null 2>&1; then
            success_msg "$service_name 服务已启动"
            return 0
        fi
        if [ $i -eq $max_attempts ]; then
            error_exit "$service_name 服务启动失败"
        fi
        echo -e "${YELLOW}⏳ 等待 $service_name 启动... ($i/$max_attempts)${NC}"
        sleep 2
    done
}

# 检查是否在正确目录
echo -e "${BLUE}📁 检查项目目录...${NC}"
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "contracts-clean" ]; then
    error_exit "请在项目根目录运行此脚本"
fi
success_msg "项目目录检查通过"

# 检查必要的命令
echo -e "${BLUE}🔧 检查必要的工具...${NC}"
check_command "curl"
check_command "jq"
check_command "python3"
check_command "npm"
check_command "ipfs"
success_msg "工具检查通过"

# 1. 停止现有后端服务
echo -e "${BLUE}🛑 停止现有后端服务...${NC}"
pkill -f "uvicorn.*backend" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "ipfs daemon" 2>/dev/null || true
sleep 2
success_msg "现有服务已停止"

# 2. 检查外部Ganache连接
echo -e "${BLUE}🔍 检查外部Ganache连接...${NC}"
if ! curl -s http://localhost:8545 > /dev/null 2>&1; then
    error_exit "无法连接到Ganache，请确保Ganache正在运行在端口8545"
fi

# 检查chainId
CHAIN_ID=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
    http://localhost:8545 | jq -r '.result' 2>/dev/null)

if [ "$CHAIN_ID" != "0x1691" ] && [ "$CHAIN_ID" != "0x539" ]; then
    warning_msg "ChainID可能不匹配，期望0x1691(5777)或0x539(1337)，实际: $CHAIN_ID"
    warning_msg "如果遇到问题，请检查Ganache配置"
else
    success_msg "外部Ganache连接成功 (ChainID: $CHAIN_ID)"
fi

# 3. 检查合约依赖
echo -e "${BLUE}📦 检查合约依赖...${NC}"
cd contracts-clean
if [ ! -d "node_modules" ]; then
    info_msg "安装合约依赖..."
    npm install || error_exit "合约依赖安装失败"
fi
success_msg "合约依赖检查通过"

# 4. 部署智能合约
echo -e "${BLUE}📜 部署智能合约到外部Ganache...${NC}"
# 使用timeout防止卡死
timeout 60 npx hardhat run scripts/deploy.js --network localhost > /tmp/deploy_output.txt 2>&1
DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -ne 0 ]; then
    echo -e "${RED}❌ 合约部署失败:${NC}"
    cat /tmp/deploy_output.txt
    error_exit "合约部署失败"
fi

DEPLOY_OUTPUT=$(cat /tmp/deploy_output.txt)
success_msg "合约部署成功"

# 提取合约地址
AGENT_REGISTRY=$(echo "$DEPLOY_OUTPUT" | grep "AgentRegistry:" | awk '{print $2}')
ACTION_LOGGER=$(echo "$DEPLOY_OUTPUT" | grep "ActionLogger:" | awk '{print $2}')
INCENTIVE_ENGINE=$(echo "$DEPLOY_OUTPUT" | grep "IncentiveEngine:" | awk '{print $2}')
TASK_MANAGER=$(echo "$DEPLOY_OUTPUT" | grep "TaskManager:" | awk '{print $2}')
BID_AUCTION=$(echo "$DEPLOY_OUTPUT" | grep "BidAuction:" | awk '{print $2}')
MESSAGE_HUB=$(echo "$DEPLOY_OUTPUT" | grep "MessageHub:" | awk '{print $2}')
LEARNING=$(echo "$DEPLOY_OUTPUT" | grep "Learning:" | awk '{print $2}')

# 验证合约地址
if [ -z "$AGENT_REGISTRY" ] || [ -z "$TASK_MANAGER" ] || [ -z "$LEARNING" ]; then
    error_exit "无法提取合约地址，请检查部署输出"
fi

# 5. 复制ABI文件到后端
echo -e "${BLUE}📁 复制ABI文件...${NC}"
cp -r ../artifacts-clean/core/*.sol/*.json ../backend/contracts/abi/ || error_exit "ABI文件复制失败"
success_msg "ABI文件复制完成"

# 6. 更新后端合约地址配置
echo -e "${BLUE}🔧 更新后端合约配置...${NC}"
CONTRACT_SERVICE_FILE="../backend/services/contract_service.py"

# 使用Python脚本安全地更新合约地址
python3 << EOF
import re

# 读取合约服务文件
with open('$CONTRACT_SERVICE_FILE', 'r') as f:
    content = f.read()

# 定义新的合约地址
new_addresses = '''# 自动生成的合约地址 (checksum格式)
contract_addresses = {
    "AgentRegistry": "$AGENT_REGISTRY",
    "ActionLogger": "$ACTION_LOGGER",
    "IncentiveEngine": "$INCENTIVE_ENGINE",
    "TaskManager": "$TASK_MANAGER",
    "BidAuction": "$BID_AUCTION",
    "MessageHub": "$MESSAGE_HUB",
    "Learning": "$LEARNING",
}'''

# 使用正则表达式替换合约地址配置
pattern = r'# 自动生成的合约地址.*?^}'
content = re.sub(pattern, new_addresses, content, flags=re.MULTILINE | re.DOTALL)

# 写回文件
with open('$CONTRACT_SERVICE_FILE', 'w') as f:
    f.write(content)

print("✅ 合约地址更新完成")
EOF

if [ $? -ne 0 ]; then
    error_exit "合约地址更新失败"
fi

# 7. 检查Python虚拟环境
echo -e "${BLUE}🐍 检查Python虚拟环境...${NC}"
cd ../backend

if [ ! -d "venv" ]; then
    info_msg "创建Python虚拟环境..."
    python3 -m venv venv || error_exit "虚拟环境创建失败"
    source venv/bin/activate
    pip install -r requirements.txt || error_exit "Python依赖安装失败"
else
    source venv/bin/activate
fi
success_msg "Python虚拟环境检查通过"

# 8. 验证Python文件语法
echo -e "${BLUE}🔍 验证Python文件语法...${NC}"
python -m py_compile services/contract_service.py || error_exit "contract_service.py语法错误"
python -m py_compile main.py || error_exit "main.py语法错误"
success_msg "Python文件语法验证通过"

# 9. 启动IPFS守护进程
echo -e "${BLUE}🗂️  启动IPFS守护进程...${NC}"

# 检查IPFS是否已初始化
if [ ! -d "$HOME/.ipfs" ]; then
    info_msg "初始化IPFS..."
    ipfs init || error_exit "IPFS初始化失败"
fi

# 启动IPFS守护进程
nohup ipfs daemon > ipfs.log 2>&1 &
IPFS_PID=$!
echo "$IPFS_PID" > ipfs.pid
success_msg "IPFS守护进程已启动 (PID: $IPFS_PID)"

# 等待IPFS启动
wait_for_service "http://localhost:5001/api/v0/version" 10 "IPFS"

# 10. 启动后端API服务
echo -e "${BLUE}🔧 启动后端API服务...${NC}"
nohup python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > backend.pid
success_msg "后端服务已启动 (PID: $BACKEND_PID)"

# 11. 等待后端启动并验证
wait_for_service "http://localhost:8001/health" 15 "后端"

# 12. 验证区块链连接
echo -e "${BLUE}🔍 验证区块链连接...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8001/health)
BLOCKCHAIN_STATUS=$(echo "$HEALTH_STATUS" | jq -r '.services.blockchain' 2>/dev/null)

if [ "$BLOCKCHAIN_STATUS" = "up" ]; then
    success_msg "区块链连接正常"
else
    warning_msg "区块链连接可能有问题，请检查日志"
    echo "健康状态: $HEALTH_STATUS"
fi

# 13. 显示启动完成信息
echo ""
echo -e "${GREEN}🎉 后端系统启动完成！${NC}"
echo "=========================================="
echo -e "${BLUE}📊 服务信息:${NC}"
echo "  🔗 外部Ganache: http://localhost:8545"
echo "  🔧 后端API: http://localhost:8001"
echo "  🗂️  IPFS节点: http://localhost:5001"
echo "  🌐 IPFS网关: http://localhost:8080"
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
echo "  停止后端: pkill -f 'uvicorn.*main:app'"
echo "  停止IPFS: pkill -f 'ipfs daemon'"
echo "  查看后端日志: tail -f backend/backend.log"
echo "  查看IPFS日志: tail -f ipfs.log"
echo "  重启系统: $0"
echo ""
echo -e "${BLUE}🔍 健康检查:${NC}"
echo "  后端健康: curl -s http://localhost:8001/health | jq"
echo "  IPFS版本: ipfs version"
echo "  IPFS节点: curl -s http://localhost:5001/api/v0/version | jq"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo "  - 后端服务和IPFS守护进程在后台运行"
echo "  - 如有问题，请查看完整启动指南: STARTUP_COMPLETE_GUIDE.md"
echo "  - 服务日志: backend/backend.log, ipfs.log"

# 清理临时文件
rm -f /tmp/deploy_output.txt

success_msg "启动脚本执行完成"