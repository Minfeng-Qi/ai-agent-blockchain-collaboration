#!/bin/bash

# LLM区块链项目后端停止脚本
echo "🛑 停止LLM区块链后端系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🔍 检查运行中的服务...${NC}"

# 停止后端服务
if [ -f "backend/backend.pid" ]; then
    BACKEND_PID=$(cat backend/backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}🔧 停止后端服务 (PID: $BACKEND_PID)...${NC}"
        kill "$BACKEND_PID"
        rm -f backend/backend.pid
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务PID文件存在但进程不在运行${NC}"
        rm -f backend/backend.pid
    fi
else
    echo -e "${YELLOW}📝 未找到后端PID文件，尝试通过进程名停止...${NC}"
fi

# 通过进程名停止后端
pkill -f "uvicorn.*backend" 2>/dev/null && echo -e "${GREEN}✅ 通过进程名停止了后端服务${NC}"

# 停止Ganache服务
if [ -f "ganache.pid" ]; then
    GANACHE_PID=$(cat ganache.pid)
    if kill -0 "$GANACHE_PID" 2>/dev/null; then
        echo -e "${YELLOW}🔗 停止Ganache区块链 (PID: $GANACHE_PID)...${NC}"
        kill "$GANACHE_PID"
        rm -f ganache.pid
        echo -e "${GREEN}✅ Ganache区块链已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  Ganache PID文件存在但进程不在运行${NC}"
        rm -f ganache.pid
    fi
else
    echo -e "${YELLOW}📝 未找到Ganache PID文件，尝试通过进程名停止...${NC}"
fi

# 通过进程名停止Ganache
pkill -f "ganache" 2>/dev/null && echo -e "${GREEN}✅ 通过进程名停止了Ganache服务${NC}"

# 清理日志文件（可选）
read -p "是否清理日志文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理日志文件...${NC}"
    rm -f ganache.log backend/backend.log
    echo -e "${GREEN}✅ 日志文件已清理${NC}"
fi

# 验证服务是否已停止
echo -e "${BLUE}🔍 验证服务状态...${NC}"
sleep 2

# 检查端口
if lsof -i :8545 >/dev/null 2>&1; then
    echo -e "${RED}⚠️  端口8545仍被占用${NC}"
    echo "运行 'lsof -i :8545' 查看详情"
else
    echo -e "${GREEN}✅ 端口8545已释放${NC}"
fi

if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}⚠️  端口8001仍被占用${NC}"
    echo "运行 'lsof -i :8001' 查看详情"
else
    echo -e "${GREEN}✅ 端口8001已释放${NC}"
fi

echo ""
echo -e "${GREEN}🎉 后端系统已停止！${NC}"
echo "=========================================="
echo -e "${BLUE}🔄 如需重新启动:${NC}"
echo "  ./start_backend.sh"
echo ""
echo -e "${BLUE}🔍 如需查看进程状态:${NC}"
echo "  ps aux | grep -E '(ganache|uvicorn)'"
echo ""
echo -e "${BLUE}🔧 如需强制清理进程:${NC}"
echo "  pkill -f ganache"
echo "  pkill -f uvicorn"