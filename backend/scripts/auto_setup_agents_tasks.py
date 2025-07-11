#!/usr/bin/env python3
"""
自动注册Agents和创建Tasks的脚本
该脚本会自动创建多个不同能力的智能体，并创建匹配的任务

使用方法:
    python scripts/auto_setup_agents_tasks.py

功能:
    1. 自动注册5个不同专业能力的agents
    2. 自动创建6个匹配agents能力的tasks
    3. 包含单agent任务和多agent协作任务
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

# 配置
BACKEND_URL = "http://localhost:8001"
WAIT_TIME = 2  # 请求间隔时间(秒)

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status="INFO"):
    """打印带颜色的状态信息"""
    color = Colors.OKBLUE
    if status == "SUCCESS":
        color = Colors.OKGREEN
    elif status == "ERROR":
        color = Colors.FAIL
    elif status == "WARNING":
        color = Colors.WARNING
    
    print(f"{color}[{status}]{Colors.ENDC} {message}")

def check_backend_health():
    """检查后端服务是否健康"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("status") == "healthy":
                print_status("后端服务健康检查通过", "SUCCESS")
                blockchain_details = health_data.get("blockchain_details", {})
                print_status(f"区块链连接: {blockchain_details.get('connected', False)}", "INFO")
                print_status(f"网络ID: {blockchain_details.get('network_id', 'Unknown')}", "INFO")
                print_status(f"最新区块: {blockchain_details.get('latest_block', 'Unknown')}", "INFO")
                return True
            else:
                print_status("后端服务状态异常", "ERROR")
                return False
        else:
            print_status(f"后端服务响应异常: {response.status_code}", "ERROR")
            return False
    except requests.RequestException as e:
        print_status(f"无法连接到后端服务: {str(e)}", "ERROR")
        return False

def register_agent(agent_data):
    """注册单个agent"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/agents/",
            headers={"Content-Type": "application/json"},
            json=agent_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                agent_id = result.get("agent_id")
                tx_hash = result.get("transaction_hash")
                print_status(f"✅ Agent '{agent_data['name']}' 注册成功", "SUCCESS")
                print_status(f"   Agent ID: {agent_id}", "INFO")
                print_status(f"   交易哈希: {tx_hash}", "INFO")
                return True
            else:
                print_status(f"❌ Agent '{agent_data['name']}' 注册失败: {result.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            print_status(f"❌ Agent '{agent_data['name']}' 注册失败: HTTP {response.status_code}", "ERROR")
            return False
    except requests.RequestException as e:
        print_status(f"❌ Agent '{agent_data['name']}' 注册失败: {str(e)}", "ERROR")
        return False

def create_task(task_data):
    """创建单个task"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/tasks/",
            headers={"Content-Type": "application/json"},
            json=task_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                task_id = result.get("task", {}).get("task_id")
                tx_hash = result.get("transaction_hash")
                reward = result.get("task", {}).get("reward")
                print_status(f"✅ Task '{task_data['title']}' 创建成功", "SUCCESS")
                print_status(f"   Task ID: {task_id}", "INFO")
                print_status(f"   奖励: {reward} ETH", "INFO")
                print_status(f"   交易哈希: {tx_hash}", "INFO")
                return True
            else:
                print_status(f"❌ Task '{task_data['title']}' 创建失败: {result.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            print_status(f"❌ Task '{task_data['title']}' 创建失败: HTTP {response.status_code}", "ERROR")
            return False
    except requests.RequestException as e:
        print_status(f"❌ Task '{task_data['title']}' 创建失败: {str(e)}", "ERROR")
        return False

def get_future_timestamp(days_from_now):
    """获取未来时间戳"""
    future_date = datetime.now() + timedelta(days=days_from_now)
    return int(future_date.timestamp())

def register_all_agents():
    """注册所有预定义的agents"""
    print_status("=" * 50, "INFO")
    print_status("开始注册Agents", "INFO")
    print_status("=" * 50, "INFO")
    
    # 使用与前端CreateAgent.js一致的capabilities
    # 前端定义：['data_analysis', 'text_generation', 'classification', 'translation', 'summarization', 'image_recognition', 'sentiment_analysis', 'code_generation']
    agents = [
        {
            "name": "DataAnalysisExpert",
            "capabilities": ["data_analysis", "classification"],  # 使用前端定义的capabilities
            "agent_type": 1,  # LLM Agent
            "reputation": 85,
            "confidence_factor": 90,
            "capabilityWeights": [90, 85]
        },
        {
            "name": "CodeGenerationMaster",
            "capabilities": ["code_generation", "text_generation"],  # 使用前端定义的capabilities
            "agent_type": 1,  # LLM Agent
            "reputation": 92,
            "confidence_factor": 85,
            "capabilityWeights": [95, 90]
        },
        {
            "name": "NLPSpecialist",
            "capabilities": ["sentiment_analysis", "text_generation", "summarization"],  # 使用前端定义的capabilities
            "agent_type": 1,  # LLM Agent
            "reputation": 88,
            "confidence_factor": 87,
            "capabilityWeights": [92, 88, 85]
        },
        {
            "name": "TranslationExpert",
            "capabilities": ["translation", "text_generation"],  # 新增翻译专家
            "agent_type": 1,  # LLM Agent
            "reputation": 90,
            "confidence_factor": 89,
            "capabilityWeights": [95, 85]
        },
        {
            "name": "ImageAnalysisAgent",
            "capabilities": ["image_recognition", "classification"],  # 新增图像分析专家
            "agent_type": 1,  # LLM Agent
            "reputation": 87,
            "confidence_factor": 88,
            "capabilityWeights": [93, 88]
        },
        {
            "name": "TaskOrchestrator",
            "capabilities": ["text_generation", "summarization"],  # 协调者使用通用能力
            "agent_type": 2,  # Orchestrator Agent
            "reputation": 95,
            "confidence_factor": 93,
            "capabilityWeights": [95, 92]
        },
        {
            "name": "QualityEvaluator",
            "capabilities": ["classification", "sentiment_analysis"],  # 评估者使用分析能力
            "agent_type": 3,  # Evaluator Agent
            "reputation": 90,
            "confidence_factor": 88,
            "capabilityWeights": [90, 87]
        }
    ]
    
    successful_agents = 0
    for i, agent in enumerate(agents, 1):
        print_status(f"注册 Agent {i}/{len(agents)}: {agent['name']}", "INFO")
        if register_agent(agent):
            successful_agents += 1
        
        # 等待一段时间再注册下一个
        if i < len(agents):
            time.sleep(WAIT_TIME)
    
    print_status(f"Agent注册完成: {successful_agents}/{len(agents)} 成功", "SUCCESS" if successful_agents == len(agents) else "WARNING")
    return successful_agents == len(agents)

def create_all_tasks():
    """创建所有预定义的tasks"""
    print_status("=" * 50, "INFO")
    print_status("开始创建Tasks", "INFO")
    print_status("=" * 50, "INFO")
    
    # 使用与前端兼容的capabilities创建任务
    # 前端定义：['data_analysis', 'text_generation', 'classification', 'translation', 'summarization', 'image_recognition', 'sentiment_analysis', 'code_generation']
    tasks = [
        {
            "title": "Analyze Sales Data Patterns",
            "description": "Analyze quarterly sales data to identify trends, patterns, and insights using data analysis and classification techniques",
            "required_capabilities": ["data_analysis", "classification"],  # 使用前端定义的capabilities
            "min_reputation": 80,
            "reward": 1.2,
            "deadline": get_future_timestamp(7)  # 7天后
        },
        {
            "title": "Build REST API Documentation",
            "description": "Generate comprehensive documentation and code examples for a REST API, including usage guides and implementation details",
            "required_capabilities": ["code_generation", "text_generation"],  # 使用前端定义的capabilities
            "min_reputation": 85,
            "reward": 2.5,
            "deadline": get_future_timestamp(14)  # 14天后
        },
        {
            "title": "Sentiment Analysis of Customer Reviews",
            "description": "Perform comprehensive sentiment analysis on customer reviews and generate summary reports about customer satisfaction",
            "required_capabilities": ["sentiment_analysis", "summarization"],  # 使用前端定义的capabilities
            "min_reputation": 85,
            "reward": 1.8,
            "deadline": get_future_timestamp(10)  # 10天后
        },
        {
            "title": "Multi-language Translation Service",
            "description": "Translate product descriptions and user guides into multiple languages and generate localized content",
            "required_capabilities": ["translation", "text_generation"],  # 使用前端定义的capabilities
            "min_reputation": 85,
            "reward": 2.2,
            "deadline": get_future_timestamp(12)  # 12天后
        },
        {
            "title": "Image Classification and Analysis",
            "description": "Classify product images, extract features, and generate descriptive text for e-commerce catalog",
            "required_capabilities": ["image_recognition", "classification", "text_generation"],  # 使用前端定义的capabilities
            "min_reputation": 80,
            "reward": 2.8,
            "deadline": get_future_timestamp(15)  # 15天后
        },
        {
            "title": "Complete Content Generation Pipeline",
            "description": "End-to-end content pipeline: analyze data, generate text, translate content, perform sentiment analysis, and create summaries",
            "required_capabilities": ["data_analysis", "text_generation", "translation", "sentiment_analysis", "summarization"],  # 多agent协作任务
            "min_reputation": 80,
            "reward": 5.0,
            "deadline": get_future_timestamp(30)  # 30天后 (多agent协作任务，时间更长)
        },
        {
            "title": "AI Content Quality Assessment",
            "description": "Evaluate and classify the quality of AI-generated content, analyze sentiment, and provide improvement recommendations",
            "required_capabilities": ["classification", "sentiment_analysis", "summarization"],  # 质量评估任务
            "min_reputation": 85,
            "reward": 3.2,
            "deadline": get_future_timestamp(18)  # 18天后
        }
    ]
    
    successful_tasks = 0
    for i, task in enumerate(tasks, 1):
        print_status(f"创建 Task {i}/{len(tasks)}: {task['title']}", "INFO")
        if create_task(task):
            successful_tasks += 1
        
        # 等待一段时间再创建下一个
        if i < len(tasks):
            time.sleep(WAIT_TIME)
    
    print_status(f"Task创建完成: {successful_tasks}/{len(tasks)} 成功", "SUCCESS" if successful_tasks == len(tasks) else "WARNING")
    return successful_tasks == len(tasks)

def verify_setup():
    """验证setup结果"""
    print_status("=" * 50, "INFO")
    print_status("验证setup结果", "INFO")
    print_status("=" * 50, "INFO")
    
    try:
        # 检查agents
        agents_response = requests.get(f"{BACKEND_URL}/agents/", timeout=10)
        if agents_response.status_code == 200:
            agents_data = agents_response.json()
            agent_count = agents_data.get("total", 0)
            print_status(f"已注册Agents数量: {agent_count}", "SUCCESS" if agent_count > 0 else "WARNING")
        else:
            print_status("无法获取agents信息", "ERROR")
        
        # 检查tasks
        tasks_response = requests.get(f"{BACKEND_URL}/tasks/", timeout=10)
        if tasks_response.status_code == 200:
            tasks_data = tasks_response.json()
            task_count = tasks_data.get("total", 0)
            print_status(f"已创建Tasks数量: {task_count}", "SUCCESS" if task_count > 0 else "WARNING")
        else:
            print_status("无法获取tasks信息", "ERROR")
            
    except requests.RequestException as e:
        print_status(f"验证过程中发生错误: {str(e)}", "ERROR")

def main():
    """主函数"""
    print_status(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print_status(f"{Colors.HEADER}🚀 LLM区块链系统 - Agents & Tasks 自动Setup脚本{Colors.ENDC}")
    print_status(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    
    # 1. 检查后端健康状态
    print_status("步骤 1: 检查后端服务状态", "INFO")
    if not check_backend_health():
        print_status("后端服务不可用，请先启动后端服务", "ERROR")
        print_status("运行命令: ./start_backend.sh", "INFO")
        sys.exit(1)
    
    # 2. 注册agents
    print_status("步骤 2: 注册Agents", "INFO")
    agents_success = register_all_agents()
    
    # 3. 创建tasks
    print_status("步骤 3: 创建Tasks", "INFO")
    tasks_success = create_all_tasks()
    
    # 4. 验证结果
    print_status("步骤 4: 验证Setup结果", "INFO")
    verify_setup()
    
    # 5. 总结
    print_status("=" * 50, "INFO")
    print_status("Setup完成!", "SUCCESS" if agents_success and tasks_success else "WARNING")
    print_status("=" * 50, "INFO")
    
    if agents_success and tasks_success:
        print_status("🎉 所有Agents和Tasks已成功创建到区块链上!", "SUCCESS")
        print_status("💡 现在可以访问前端查看: http://localhost:3000", "INFO")
        print_status("📖 API文档: http://localhost:8001/docs", "INFO")
    else:
        print_status("⚠️  部分创建失败，请检查日志", "WARNING")
        print_status("📝 查看日志: tail -f backend/backend.log", "INFO")

if __name__ == "__main__":
    main()