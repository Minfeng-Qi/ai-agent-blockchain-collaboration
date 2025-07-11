#!/bin/bash
# 一键Setup脚本 - 自动注册Agents和创建Tasks

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    print_message $PURPLE "=================================="
    print_message $PURPLE "$1"
    print_message $PURPLE "=================================="
}

print_success() {
    print_message $GREEN "✅ $1"
}

print_error() {
    print_message $RED "❌ $1"
}

print_warning() {
    print_message $YELLOW "⚠️  $1"
}

print_info() {
    print_message $BLUE "ℹ️  $1"
}

# 检查依赖
check_dependencies() {
    print_header "检查依赖环境"
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        print_success "Python3 已安装"
    else
        print_error "Python3 未安装"
        exit 1
    fi
    
    # 检查curl
    if command -v curl &> /dev/null; then
        print_success "curl 已安装"
    else
        print_error "curl 未安装"
        exit 1
    fi
    
    # 检查jq (可选)
    if command -v jq &> /dev/null; then
        print_success "jq 已安装"
    else
        print_warning "jq 未安装 (可选，用于JSON格式化)"
    fi
    
    # 检查和安装Python依赖
    print_info "检查Python依赖..."
    
    # 只安装必要的requests包
    print_info "安装requests库..."
    python3 -m pip install requests --quiet --disable-pip-version-check 2>/dev/null || {
        print_warning "requests安装失败，尝试其他方式..."
        python3 -c "import requests" 2>/dev/null && print_success "requests已可用" || print_warning "requests不可用，脚本可能失败"
    }
}

# 检查后端服务
check_backend() {
    print_header "检查后端服务状态"
    
    local backend_url="http://localhost:8001"
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$backend_url/health" | grep -q "200"; then
            print_success "后端服务运行正常"
            
            # 显示区块链状态
            if command -v jq &> /dev/null; then
                local blockchain_status=$(curl -s "$backend_url/health" | jq -r '.blockchain_details.connected')
                if [ "$blockchain_status" = "true" ]; then
                    print_success "区块链连接正常"
                else
                    print_warning "区块链连接异常"
                fi
            fi
            return 0
        else
            ((retry_count++))
            print_warning "后端服务检查失败，重试 $retry_count/$max_retries"
            sleep 2
        fi
    done
    
    print_error "后端服务不可用"
    print_info "请运行: ./start_backend.sh"
    exit 1
}

# 运行Python setup脚本
run_setup_script() {
    print_header "运行自动Setup脚本"
    
    local script_path="backend/scripts/auto_setup_agents_tasks.py"
    
    if [ -f "$script_path" ]; then
        print_info "执行 $script_path"
        cd backend
        python3 scripts/auto_setup_agents_tasks.py
        cd ..
    else
        print_error "Setup脚本不存在: $script_path"
        exit 1
    fi
}

# 显示最终状态
show_final_status() {
    print_header "最终状态检查"
    
    local backend_url="http://localhost:8001"
    
    # 检查agents数量
    if command -v jq &> /dev/null; then
        local agents_count=$(curl -s "$backend_url/agents/" | jq '.total // 0')
        print_info "已注册Agents: $agents_count"
    else
        local agents_response=$(curl -s "$backend_url/agents/")
        print_info "Agents状态: $(echo $agents_response | grep -o '"total":[0-9]*' | cut -d':' -f2 || echo "未知")"
    fi
    
    # 检查tasks数量
    if command -v jq &> /dev/null; then
        local tasks_count=$(curl -s "$backend_url/tasks/" | jq '.total // 0')
        print_info "已创建Tasks: $tasks_count"
    else
        local tasks_response=$(curl -s "$backend_url/tasks/")
        print_info "Tasks状态: $(echo $tasks_response | grep -o '"total":[0-9]*' | cut -d':' -f2 || echo "未知")"
    fi
}

# 主函数
main() {
    print_header "🚀 LLM区块链系统 - 一键Setup脚本"
    
    # 步骤1: 检查依赖
    check_dependencies
    
    # 步骤2: 检查后端服务
    check_backend
    
    # 步骤3: 运行setup脚本
    run_setup_script
    
    # 步骤4: 显示最终状态
    show_final_status
    
    print_header "🎉 Setup完成!"
    print_success "系统已准备就绪"
    print_info "前端访问: http://localhost:3000"
    print_info "API文档: http://localhost:8001/docs"
    print_info "查看日志: tail -f backend/backend.log"
}

# 执行主函数
main "$@"