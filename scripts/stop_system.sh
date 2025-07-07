#!/bin/bash

# 系统停止脚本
# 停止所有相关服务

echo "🛑 停止智能合约AI代理系统"
echo "=========================="

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 查找运行中的服务...${NC}"

# 停止IPFS
if [ -f "ipfs.pid" ]; then
    IPFS_PID=$(cat ipfs.pid)
    if kill -0 "$IPFS_PID" 2>/dev/null; then
        echo -e "${YELLOW}⏹️  停止IPFS (PID: $IPFS_PID)${NC}"
        kill "$IPFS_PID"
        rm -f ipfs.pid
    else
        echo -e "${YELLOW}⚠️  IPFS进程不存在${NC}"
        rm -f ipfs.pid
    fi
else
    echo -e "${YELLOW}⏹️  尝试停止IPFS进程...${NC}"
    pkill -f "ipfs daemon" 2>/dev/null
fi

# 停止Ganache
if [ -f "ganache.pid" ]; then
    GANACHE_PID=$(cat ganache.pid)
    if kill -0 "$GANACHE_PID" 2>/dev/null; then
        echo -e "${YELLOW}⏹️  停止Ganache (PID: $GANACHE_PID)${NC}"
        kill "$GANACHE_PID"
        rm -f ganache.pid
    else
        echo -e "${YELLOW}⚠️  Ganache进程不存在${NC}"
        rm -f ganache.pid
    fi
else
    echo -e "${YELLOW}⏹️  尝试停止Ganache进程...${NC}"
    pkill -f "ganache" 2>/dev/null
fi

# 停止Backend
echo -e "${YELLOW}⏹️  停止Backend服务...${NC}"
pkill -f "uvicorn" 2>/dev/null
pkill -f "python.*backend" 2>/dev/null

# 停止Frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}⏹️  停止Frontend (PID: $FRONTEND_PID)${NC}"
        kill "$FRONTEND_PID"
        rm -f frontend.pid
    else
        echo -e "${YELLOW}⚠️  Frontend进程不存在${NC}"
        rm -f frontend.pid
    fi
else
    echo -e "${YELLOW}⏹️  尝试停止Frontend进程...${NC}"
    pkill -f "npm start" 2>/dev/null
    pkill -f "react-scripts" 2>/dev/null
fi

# 等待进程完全退出
sleep 2

# 检查是否还有遗留进程
echo -e "${BLUE}🔍 检查遗留进程...${NC}"

REMAINING_PROCESSES=$(ps aux | grep -E "(ipfs daemon|ganache|uvicorn|react-scripts)" | grep -v grep)
if [ -n "$REMAINING_PROCESSES" ]; then
    echo -e "${YELLOW}⚠️  发现遗留进程:${NC}"
    echo "$REMAINING_PROCESSES"
    echo ""
    echo -e "${YELLOW}尝试强制终止...${NC}"
    pkill -9 -f "ipfs daemon"
    pkill -9 -f "ganache"
    pkill -9 -f "uvicorn"
    pkill -9 -f "react-scripts"
fi

# 清理临时文件
echo -e "${BLUE}🧹 清理临时文件...${NC}"
rm -f ipfs.pid ganache.pid frontend.pid

echo ""
echo -e "${GREEN}✅ 系统已完全停止${NC}"
echo ""
echo -e "${BLUE}📋 可用命令:${NC}"
echo "  重新启动: ./scripts/start_system.sh"
echo "  仅重新部署合约: python3 scripts/auto_deploy.py"