#!/bin/bash

# LLM区块链项目快速启动脚本
echo "🚀 LLM区块链系统启动中..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在正确目录
if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 停止可能已经运行的服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"
pkill -f "ganache" 2>/dev/null
pkill -f "uvicorn.*backend" 2>/dev/null
rm -f *.pid *.log 2>/dev/null

echo -e "${BLUE}📋 启动选项:${NC}"
echo "1. 完整启动 (区块链 + 后端 + 前端)"
echo "2. 仅启动前端 (使用模拟数据)"
echo "3. 区块链 + 后端 (不启动前端)"
echo "4. 查看服务状态"
echo "5. 停止所有服务"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}🔗 启动完整系统...${NC}"
        
        # 1. 启动Ganache
        echo -e "${BLUE}📦 启动Ganache区块链...${NC}"
        npx ganache --host 0.0.0.0 --port 8545 --chain.chainId 1337 --accounts 10 --deterministic > ganache.log 2>&1 &
        GANACHE_PID=$!
        echo $GANACHE_PID > ganache.pid
        sleep 3
        
        # 2. 部署合约
        echo -e "${BLUE}📜 部署智能合约...${NC}"
        python3 scripts/auto_deploy.py
        
        # 3. 启动后端
        echo -e "${BLUE}🔧 启动后端API...${NC}"
        backend/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        sleep 3
        
        # 4. 启动前端
        echo -e "${BLUE}🌐 启动前端...${NC}"
        cd frontend
        npm start &
        cd ..
        
        echo -e "${GREEN}✅ 系统启动完成!${NC}"
        echo -e "${GREEN}📱 前端: http://localhost:3000${NC}"
        echo -e "${GREEN}🔧 后端: http://localhost:8001${NC}"
        echo -e "${GREEN}⛓️  区块链: http://localhost:8545${NC}"
        ;;
        
    2)
        echo -e "${GREEN}🌐 仅启动前端 (模拟数据模式)...${NC}"
        cd frontend
        npm start
        cd ..
        ;;
        
    3)
        echo -e "${GREEN}🔗 启动区块链和后端...${NC}"
        
        # 启动Ganache
        echo -e "${BLUE}📦 启动Ganache区块链...${NC}"
        npx ganache --host 0.0.0.0 --port 8545 --chain.chainId 1337 --accounts 10 --deterministic > ganache.log 2>&1 &
        GANACHE_PID=$!
        echo $GANACHE_PID > ganache.pid
        sleep 3
        
        # 部署合约
        echo -e "${BLUE}📜 部署智能合约...${NC}"
        python3 scripts/auto_deploy.py
        
        # 启动后端
        echo -e "${BLUE}🔧 启动后端API...${NC}"
        backend/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        
        echo -e "${GREEN}✅ 后端服务启动完成!${NC}"
        echo -e "${GREEN}🔧 后端API: http://localhost:8001/docs${NC}"
        echo -e "${GREEN}⛓️  区块链: http://localhost:8545${NC}"
        ;;
        
    4)
        echo -e "${BLUE}📊 检查服务状态...${NC}"
        
        # 检查Ganache
        if pgrep -f "ganache" > /dev/null; then
            echo -e "${GREEN}✅ Ganache正在运行${NC}"
        else
            echo -e "${RED}❌ Ganache未运行${NC}"
        fi
        
        # 检查后端
        if pgrep -f "uvicorn.*backend" > /dev/null; then
            echo -e "${GREEN}✅ 后端正在运行${NC}"
        else
            echo -e "${RED}❌ 后端未运行${NC}"
        fi
        
        # 检查前端
        if pgrep -f "react-scripts" > /dev/null; then
            echo -e "${GREEN}✅ 前端正在运行${NC}"
        else
            echo -e "${RED}❌ 前端未运行${NC}"
        fi
        
        # 检查端口
        echo -e "${BLUE}📡 端口状态:${NC}"
        lsof -i :3000 >/dev/null 2>&1 && echo -e "${GREEN}✅ 3000 (前端)${NC}" || echo -e "${RED}❌ 3000 (前端)${NC}"
        lsof -i :8001 >/dev/null 2>&1 && echo -e "${GREEN}✅ 8001 (后端)${NC}" || echo -e "${RED}❌ 8001 (后端)${NC}"
        lsof -i :8545 >/dev/null 2>&1 && echo -e "${GREEN}✅ 8545 (区块链)${NC}" || echo -e "${RED}❌ 8545 (区块链)${NC}"
        ;;
        
    5)
        echo -e "${YELLOW}🛑 停止所有服务...${NC}"
        
        # 停止前端
        pkill -f "react-scripts" 2>/dev/null && echo -e "${GREEN}✅ 前端已停止${NC}"
        
        # 停止后端
        if [ -f backend.pid ]; then
            BACKEND_PID=$(cat backend.pid)
            kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ 后端已停止${NC}"
            rm -f backend.pid
        fi
        
        # 停止Ganache
        if [ -f ganache.pid ]; then
            GANACHE_PID=$(cat ganache.pid)
            kill $GANACHE_PID 2>/dev/null && echo -e "${GREEN}✅ Ganache已停止${NC}"
            rm -f ganache.pid
        fi
        
        # 清理日志文件
        rm -f *.log 2>/dev/null
        echo -e "${GREEN}✅ 所有服务已停止${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac