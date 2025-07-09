#!/bin/bash

# LLM区块链项目后端停止脚本 (仅停止后端，不影响外部Ganache)
echo "🛑 停止LLM区块链后端服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🔍 检查运行中的后端服务...${NC}"

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

# 验证服务是否已停止
echo -e "${BLUE}🔍 验证后端服务状态...${NC}"
sleep 2

# 检查后端端口
if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}⚠️  端口8001仍被占用${NC}"
    echo "运行 'lsof -i :8001' 查看详情"
    echo "或运行 'pkill -f uvicorn' 强制停止"
else
    echo -e "${GREEN}✅ 后端端口8001已释放${NC}"
fi

# 检查外部Ganache状态 (仅显示，不操作)
echo -e "${BLUE}🔍 检查外部Ganache状态...${NC}"
if lsof -i :8545 >/dev/null 2>&1; then
    if curl -s http://localhost:8545 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 外部Ganache仍在运行 (正常，由用户管理)${NC}"
    else
        echo -e "${YELLOW}⚠️  端口8545被占用但无法连接${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  端口8545未被占用，外部Ganache可能未启动${NC}"
fi

# 清理日志文件（可选）
read -p "是否清理后端日志文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理后端日志文件...${NC}"
    rm -f backend/backend.log
    echo -e "${GREEN}✅ 后端日志文件已清理${NC}"
fi

echo ""
echo -e "${GREEN}🎉 后端服务已停止！${NC}"
echo "=========================================="
echo -e "${BLUE}📊 状态信息:${NC}"
echo "  🔧 后端服务: 已停止"
echo "  🔗 外部Ganache: 由用户管理 (未受影响)"
echo ""
echo -e "${BLUE}🔄 如需重新启动后端:${NC}"
echo "  ./start_backend_external_ganache.sh"
echo ""
echo -e "${BLUE}🔍 如需查看后端进程状态:${NC}"
echo "  ps aux | grep uvicorn"
echo ""
echo -e "${BLUE}🔧 如需强制清理后端进程:${NC}"
echo "  pkill -f uvicorn"
echo ""
echo -e "${YELLOW}💡 注意: 此脚本不会影响外部Ganache服务${NC}"