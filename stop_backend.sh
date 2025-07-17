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

# 函数：强制停止进程
force_kill_process() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}🔧 发现 $process_name 进程: $pids${NC}"
        
        # 先尝试温和停止
        echo "$pids" | xargs -r kill -TERM 2>/dev/null
        sleep 2
        
        # 检查是否还有进程存在
        local remaining_pids=$(pgrep -f "$process_name" 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo -e "${RED}⚠️  强制停止 $process_name 进程: $remaining_pids${NC}"
            echo "$remaining_pids" | xargs -r kill -KILL 2>/dev/null
        fi
        
        # 最终验证
        sleep 1
        local final_pids=$(pgrep -f "$process_name" 2>/dev/null)
        if [ -z "$final_pids" ]; then
            echo -e "${GREEN}✅ $process_name 进程已停止${NC}"
        else
            echo -e "${RED}❌ $process_name 进程仍在运行: $final_pids${NC}"
        fi
    else
        echo -e "${GREEN}✅ 未发现 $process_name 进程${NC}"
    fi
}

# 函数：强制释放端口
force_free_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}🔧 端口 $port 被占用，PID: $pids${NC}"
        
        # 先尝试温和停止
        echo "$pids" | xargs -r kill -TERM 2>/dev/null
        sleep 2
        
        # 检查端口是否还被占用
        local remaining_pids=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo -e "${RED}⚠️  强制释放端口 $port，PID: $remaining_pids${NC}"
            echo "$remaining_pids" | xargs -r kill -KILL 2>/dev/null
        fi
        
        # 最终验证
        sleep 1
        if ! lsof -i :$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 端口 $port 已释放${NC}"
        else
            echo -e "${RED}❌ 端口 $port 仍被占用${NC}"
        fi
    else
        echo -e "${GREEN}✅ 端口 $port 未被占用${NC}"
    fi
}

# 1. 停止后端服务
echo -e "${BLUE}📱 停止后端服务...${NC}"

# 通过PID文件停止
if [ -f "backend/backend.pid" ]; then
    BACKEND_PID=$(cat backend/backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}🔧 停止后端服务 (PID: $BACKEND_PID)...${NC}"
        kill -TERM "$BACKEND_PID" 2>/dev/null
        sleep 2
        
        # 检查是否还在运行
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${RED}⚠️  强制停止后端服务 (PID: $BACKEND_PID)${NC}"
            kill -KILL "$BACKEND_PID" 2>/dev/null
        fi
        
        if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ 后端服务已停止${NC}"
        fi
    fi
    rm -f backend/backend.pid
fi

# 通过进程名强制停止所有相关进程
force_kill_process "uvicorn.*backend"
force_kill_process "python.*backend"
force_kill_process "fastapi"

# 2. 停止IPFS服务
echo -e "${BLUE}🗂️  停止IPFS服务...${NC}"

# 通过PID文件停止
if [ -f "ipfs.pid" ]; then
    IPFS_PID=$(cat ipfs.pid)
    if kill -0 "$IPFS_PID" 2>/dev/null; then
        echo -e "${YELLOW}🔧 停止IPFS守护进程 (PID: $IPFS_PID)...${NC}"
        kill -TERM "$IPFS_PID" 2>/dev/null
        sleep 2
        
        # 检查是否还在运行
        if kill -0 "$IPFS_PID" 2>/dev/null; then
            echo -e "${RED}⚠️  强制停止IPFS守护进程 (PID: $IPFS_PID)${NC}"
            kill -KILL "$IPFS_PID" 2>/dev/null
        fi
        
        if ! kill -0 "$IPFS_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ IPFS守护进程已停止${NC}"
        fi
    fi
    rm -f ipfs.pid
fi

# 通过进程名强制停止所有相关进程
force_kill_process "ipfs daemon"
force_kill_process "ipfs"

# 3. 停止Ganache服务
echo -e "${BLUE}🔗 停止Ganache区块链...${NC}"

# 通过PID文件停止
if [ -f "ganache.pid" ]; then
    GANACHE_PID=$(cat ganache.pid)
    if kill -0 "$GANACHE_PID" 2>/dev/null; then
        echo -e "${YELLOW}🔧 停止Ganache区块链 (PID: $GANACHE_PID)...${NC}"
        kill -TERM "$GANACHE_PID" 2>/dev/null
        sleep 2
        
        # 检查是否还在运行
        if kill -0 "$GANACHE_PID" 2>/dev/null; then
            echo -e "${RED}⚠️  强制停止Ganache区块链 (PID: $GANACHE_PID)${NC}"
            kill -KILL "$GANACHE_PID" 2>/dev/null
        fi
        
        if ! kill -0 "$GANACHE_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Ganache区块链已停止${NC}"
        fi
    fi
    rm -f ganache.pid
fi

# 通过进程名强制停止所有相关进程
force_kill_process "ganache"
force_kill_process "node.*ganache"

# 4. 强制释放端口
echo -e "${BLUE}🔧 检查和释放端口...${NC}"
force_free_port 8545
force_free_port 8001
force_free_port 5001
force_free_port 8080
force_free_port 4001

# 5. 停止其他可能的相关进程
echo -e "${BLUE}🧹 清理其他相关进程...${NC}"
force_kill_process "python.*main.py"
force_kill_process "hypercorn"
force_kill_process "gunicorn"

# 6. 清理临时文件
echo -e "${BLUE}🧹 清理临时文件...${NC}"
rm -f backend/backend.pid ganache.pid ipfs.pid
rm -f backend/*.pid ganache*.pid ipfs*.pid

# 7. 清理日志文件（可选）
read -p "是否清理日志文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理日志文件...${NC}"
    rm -f ganache.log backend/backend.log ipfs.log
    rm -f *.log backend/*.log
    echo -e "${GREEN}✅ 日志文件已清理${NC}"
fi

# 8. 最终验证
echo -e "${BLUE}🔍 最终验证服务状态...${NC}"
sleep 3

# 检查端口状态
echo -e "${BLUE}检查端口状态:${NC}"
if lsof -i :8545 >/dev/null 2>&1; then
    echo -e "${RED}❌ 端口8545仍被占用${NC}"
    echo "占用详情:"
    lsof -i :8545
else
    echo -e "${GREEN}✅ 端口8545已释放${NC}"
fi

if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}❌ 端口8001仍被占用${NC}"
    echo "占用详情:"
    lsof -i :8001
else
    echo -e "${GREEN}✅ 端口8001已释放${NC}"
fi

if lsof -i :5001 >/dev/null 2>&1; then
    echo -e "${RED}❌ 端口5001仍被占用${NC}"
    echo "占用详情:"
    lsof -i :5001
else
    echo -e "${GREEN}✅ 端口5001已释放${NC}"
fi

if lsof -i :8080 >/dev/null 2>&1; then
    echo -e "${RED}❌ 端口8080仍被占用${NC}"
    echo "占用详情:"
    lsof -i :8080
else
    echo -e "${GREEN}✅ 端口8080已释放${NC}"
fi

# 检查进程状态
echo -e "${BLUE}检查进程状态:${NC}"
remaining_processes=$(pgrep -f "ganache|uvicorn|fastapi|ipfs" 2>/dev/null)
if [ -n "$remaining_processes" ]; then
    echo -e "${RED}❌ 发现残留进程:${NC}"
    ps aux | grep -E "(ganache|uvicorn|fastapi|ipfs)" | grep -v grep
else
    echo -e "${GREEN}✅ 所有相关进程已停止${NC}"
fi

echo ""
echo -e "${GREEN}🎉 后端系统已完全停止！${NC}"
echo "=========================================="
echo -e "${BLUE}🔄 如需重新启动:${NC}"
echo "  ./start_backend.sh"
echo ""
echo -e "${BLUE}🔍 如需查看进程状态:${NC}"
echo "  ps aux | grep -E '(ganache|uvicorn|ipfs)'"
echo ""
echo -e "${BLUE}🔧 如需手动清理:${NC}"
echo "  pkill -f ganache"
echo "  pkill -f uvicorn"
echo "  pkill -f 'ipfs daemon'"
echo "  lsof -ti :8545 | xargs kill -9"
echo "  lsof -ti :8001 | xargs kill -9"
echo "  lsof -ti :5001 | xargs kill -9"
echo "  lsof -ti :8080 | xargs kill -9"