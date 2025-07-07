#!/bin/bash

# 智能合约系统启动脚本
# 自动启动Ganache、部署合约、启动backend服务

echo "🚀 启动智能合约AI代理系统"
echo "================================"

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖...${NC}"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python 未安装${NC}"
        exit 1
    fi
    
    # 检查Ganache CLI
    if ! command -v ganache &> /dev/null && ! command -v ganache-cli &> /dev/null; then
        echo -e "${YELLOW}⚠️  Ganache CLI 未安装，正在安装...${NC}"
        npm install -g ganache
    fi
    
    # 检查IPFS
    if ! command -v ipfs &> /dev/null; then
        echo -e "${YELLOW}⚠️  IPFS 未安装，请手动安装${NC}"
        echo -e "${YELLOW}    macOS: brew install ipfs${NC}"
        echo -e "${YELLOW}    Linux: https://docs.ipfs.io/install/command-line/${NC}"
        echo -e "${YELLOW}    注意: IPFS不是必需的，系统将运行在模拟模式${NC}"
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 启动IPFS
start_ipfs() {
    echo -e "${BLUE}📁 启动IPFS服务...${NC}"
    
    # 检查IPFS是否已安装
    if ! command -v ipfs &> /dev/null; then
        echo -e "${YELLOW}⚠️  IPFS未安装，跳过IPFS启动${NC}"
        return 0
    fi
    
    # 检查IPFS是否已经运行
    if curl -s http://localhost:5001/api/v0/version > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  IPFS已在运行${NC}"
        return 0
    fi
    
    # 初始化IPFS仓库 (如果不存在)
    if [ ! -d "$HOME/.ipfs" ]; then
        echo -e "${YELLOW}🔧 初始化IPFS仓库...${NC}"
        ipfs init
    fi
    
    # 启动IPFS daemon (后台运行)
    echo -e "${YELLOW}⏳ 启动IPFS daemon...${NC}"
    nohup ipfs daemon > ipfs.log 2>&1 &
    IPFS_PID=$!
    echo "$IPFS_PID" > ipfs.pid
    
    # 等待IPFS启动
    for i in {1..10}; do
        if curl -s http://localhost:5001/api/v0/version > /dev/null 2>&1; then
            echo -e "${GREEN}✅ IPFS启动成功 (PID: $IPFS_PID)${NC}"
            echo -e "${GREEN}📁 IPFS Gateway: http://localhost:8080${NC}"
            echo -e "${GREEN}🔗 IPFS API: http://localhost:5001${NC}"
            return 0
        fi
        sleep 2
    done
    
    echo -e "${YELLOW}⚠️  IPFS启动超时，系统将运行在模拟模式${NC}"
    return 0  # 不阻止系统启动
}

# 启动Ganache
start_ganache() {
    echo -e "${BLUE}🔗 启动Ganache区块链网络...${NC}"
    
    # 检查是否已经运行
    if curl -s http://localhost:8545 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ganache已在运行${NC}"
        return 0
    fi
    
    # 启动Ganache (后台运行)
    nohup ganache \
        --host 0.0.0.0 \
        --port 8545 \
        --accounts 10 \
        --defaultBalanceEther 1000 \
        --mnemonic "myth like bonus scare over problem client lizard pioneer submit female collect" \
        --networkId 1337 \
        --chain.chainId 1337 \
        > ganache.log 2>&1 &
    
    GANACHE_PID=$!
    echo "$GANACHE_PID" > ganache.pid
    
    # 等待Ganache启动
    echo -e "${YELLOW}⏳ 等待Ganache启动...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8545 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ganache启动成功 (PID: $GANACHE_PID)${NC}"
            return 0
        fi
        sleep 2
    done
    
    echo -e "${RED}❌ Ganache启动失败${NC}"
    return 1
}

# 自动部署合约
deploy_contracts() {
    echo -e "${BLUE}📜 自动部署智能合约...${NC}"
    
    # 确保Python脚本可执行
    chmod +x scripts/auto_deploy.py
    
    # 运行自动部署脚本（使用虚拟环境）
    if [ -f "backend/venv/bin/python3" ]; then
        echo -e "${YELLOW}📦 使用虚拟环境运行部署脚本...${NC}"
        backend/venv/bin/python3 scripts/auto_deploy.py
    else
        echo -e "${YELLOW}📦 使用系统Python运行部署脚本...${NC}"
        python3 scripts/auto_deploy.py
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 合约部署完成${NC}"
        return 0
    else
        echo -e "${RED}❌ 合约部署失败${NC}"
        return 1
    fi
}

# 启动前端 (可选)
start_frontend() {
    if [ "$START_FRONTEND" = "true" ]; then
        echo -e "${BLUE}🌐 启动前端服务...${NC}"
        
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}📦 安装前端依赖...${NC}"
            npm install
        fi
        
        # 启动前端 (后台运行)
        nohup npm start > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "$FRONTEND_PID" > ../frontend.pid
        
        echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
        echo -e "${GREEN}🌐 前端地址: http://localhost:3000${NC}"
        
        cd ..
    fi
}

# 显示状态
show_status() {
    echo ""
    echo -e "${GREEN}🎉 系统启动完成！${NC}"
    echo "================================"
    echo -e "${BLUE}📊 服务状态:${NC}"
    echo "  🔗 Ganache区块链: http://localhost:8545"
    echo "  🔧 Backend API: http://localhost:8001"
    
    # 检查IPFS状态
    if curl -s http://localhost:5001/api/v0/version > /dev/null 2>&1; then
        echo "  📁 IPFS Gateway: http://localhost:8080"
        echo "  🔗 IPFS API: http://localhost:5001"
    else
        echo "  📁 IPFS: 模拟模式 (未启动或不可用)"
    fi
    
    if [ "$START_FRONTEND" = "true" ]; then
        echo "  🌐 前端界面: http://localhost:3000"
    fi
    
    echo ""
    echo -e "${BLUE}📋 管理命令:${NC}"
    echo "  停止系统: ./scripts/stop_system.sh"
    echo "  重新部署: python3 scripts/auto_deploy.py"
    echo "  查看日志: tail -f ganache.log backend.log"
    echo ""
    echo -e "${YELLOW}💡 提示: 每次重启系统会自动重新部署合约并更新地址${NC}"
}

# 清理函数 (信号处理)
cleanup() {
    echo -e "\n${YELLOW}🛑 正在关闭系统...${NC}"
    
    # 杀死所有相关进程
    if [ -f "ganache.pid" ]; then
        kill "$(cat ganache.pid)" 2>/dev/null
        rm -f ganache.pid
    fi
    
    if [ -f "ipfs.pid" ]; then
        kill "$(cat ipfs.pid)" 2>/dev/null
        rm -f ipfs.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        kill "$(cat frontend.pid)" 2>/dev/null
        rm -f frontend.pid
    fi
    
    pkill -f "uvicorn" 2>/dev/null
    pkill -f "python.*backend" 2>/dev/null
    pkill -f "ipfs daemon" 2>/dev/null
    
    echo -e "${GREEN}✅ 系统已关闭${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 解析命令行参数
START_FRONTEND=false
FORCE_RESTART=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend|-f)
            START_FRONTEND=true
            shift
            ;;
        --force|-F)
            FORCE_RESTART=true
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --frontend, -f    同时启动前端服务"
            echo "  --force, -F       强制重启所有服务"
            echo "  --help, -h        显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 主流程
main() {
    # 强制重启时清理现有进程
    if [ "$FORCE_RESTART" = "true" ]; then
        echo -e "${YELLOW}🔄 强制重启模式${NC}"
        cleanup
        sleep 2
    fi
    
    # 执行启动流程
    check_dependencies && \
    start_ipfs && \
    start_ganache && \
    deploy_contracts && \
    start_frontend && \
    show_status
    
    if [ $? -eq 0 ]; then
        echo -e "${BLUE}⏳ 系统运行中... (按 Ctrl+C 停止)${NC}"
        
        # 保持脚本运行
        while true; do
            sleep 10
            
            # 检查服务健康状态
            if ! curl -s http://localhost:8545 > /dev/null 2>&1; then
                echo -e "${RED}❌ Ganache连接丢失${NC}"
                break
            fi
        done
    else
        echo -e "${RED}❌ 系统启动失败${NC}"
        cleanup
        exit 1
    fi
}

# 运行主程序
main