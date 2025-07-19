#!/usr/bin/env python3
"""
测试多agent协作功能
验证所有分配的agents都能参与任务执行
"""

import asyncio
import requests
import json
import time
from typing import Dict, List

# API基础URL
BASE_URL = "http://localhost:8001"

async def test_multi_agent_collaboration():
    """测试多agent协作功能"""
    print("🚀 开始测试多agent协作功能")
    
    try:
        # 1. 获取所有agents
        print("\n1. 获取可用agents...")
        agents_response = requests.get(f"{BASE_URL}/agents/")
        if agents_response.status_code != 200:
            print(f"❌ 获取agents失败: {agents_response.status_code}")
            return
        
        agents_data = agents_response.json()
        available_agents = agents_data.get("agents", [])
        
        if len(available_agents) < 2:
            print(f"❌ 需要至少2个agents进行测试，当前只有{len(available_agents)}个")
            return
        
        print(f"✅ 找到 {len(available_agents)} 个agents:")
        for agent in available_agents[:4]:  # 最多显示4个
            print(f"   - {agent['name']} ({agent['agent_id'][:10]}...)")
        
        # 2. 获取或创建一个合适的任务
        print("\n2. 获取测试任务...")
        tasks_response = requests.get(f"{BASE_URL}/tasks/", params={"status": "open", "limit": 10})
        
        if tasks_response.status_code != 200:
            print(f"❌ 获取任务失败: {tasks_response.status_code}")
            return
        
        tasks_data = tasks_response.json()
        available_tasks = tasks_data.get("tasks", [])
        
        if not available_tasks:
            print("❌ 没有找到open状态的任务")
            return
        
        # 选择第一个任务进行测试
        test_task = None
        for task in available_tasks:
            if task.get("title") == "Complete Content Generation Pipeline":
                test_task = task
                break
        
        if not test_task:
            test_task = available_tasks[0]
        
        task_id = test_task["task_id"]
        print(f"✅ 选择测试任务: {test_task['title']} (ID: {task_id})")
        
        # 3. 使用智能分配功能分配多个agents
        print(f"\n3. 智能分配多个agents到任务...")
        assign_response = requests.post(
            f"{BASE_URL}/tasks/{task_id}/smart-assign",
            params={
                "collaborative": True,
                "max_agents": 4  # 分配4个agents
            }
        )
        
        if assign_response.status_code != 200:
            print(f"❌ 分配任务失败: {assign_response.status_code}")
            print(f"响应: {assign_response.text}")
            return
        
        assign_data = assign_response.json()
        if not assign_data.get("success"):
            print(f"❌ 智能分配失败: {assign_data.get('error')}")
            return
        
        assigned_agents = assign_data.get("selected_agents", [])
        print(f"✅ 成功分配 {len(assigned_agents)} 个agents:")
        for agent in assigned_agents:
            print(f"   - {agent.get('name', 'Unknown')} ({agent.get('agent_id', 'Unknown')[:10]}...)")
        
        # 4. 执行多agent协作
        print(f"\n4. 执行多agent协作...")
        print("⏳ 这可能需要一些时间，请等待...")
        
        start_time = time.time()
        execute_response = requests.post(f"{BASE_URL}/tasks/{task_id}/execute-collaboration")
        
        if execute_response.status_code != 200:
            print(f"❌ 执行协作失败: {execute_response.status_code}")
            print(f"响应: {execute_response.text}")
            return
        
        execute_data = execute_response.json()
        execution_time = time.time() - start_time
        
        if not execute_data.get("success"):
            print(f"❌ 协作执行失败: {execute_data.get('error')}")
            return
        
        print(f"✅ 协作执行成功! 耗时: {execution_time:.1f}秒")
        
        # 5. 分析协作结果
        print(f"\n5. 分析协作结果...")
        
        # 获取协作结果数据
        collaboration_result = execute_data.get("collaboration_result", {})
        conversation = collaboration_result.get("conversation", [])
        agent_updates = collaboration_result.get("agent_updates", [])
        
        print(f"📝 对话消息数量: {len(conversation)}")
        print(f"🤖 agent更新数量: {len(agent_updates)}")
        
        # 统计每个agent的参与情况
        agent_participation = {}
        for msg in conversation:
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                # 提取agent名称
                for agent in assigned_agents:
                    agent_name = agent.get("name", "")
                    if agent_name and agent_name in content:
                        if agent_name not in agent_participation:
                            agent_participation[agent_name] = 0
                        agent_participation[agent_name] += 1
        
        print(f"\n📊 Agent参与统计:")
        for agent_name, count in agent_participation.items():
            print(f"   - {agent_name}: {count} 条消息")
        
        # 检查是否所有agents都参与了
        expected_agents = {agent.get("name") for agent in assigned_agents if agent.get("name")}
        participating_agents = set(agent_participation.keys())
        
        if expected_agents.issubset(participating_agents):
            print(f"✅ 所有分配的agents都参与了协作!")
        else:
            missing_agents = expected_agents - participating_agents
            print(f"⚠️  以下agents没有参与: {', '.join(missing_agents)}")
        
        # 显示agent更新信息
        if agent_updates:
            print(f"\n🔄 Agent更新信息:")
            for update in agent_updates:
                agent_id = update.get("agent_id", "Unknown")
                score = update.get("performance_score", 0)
                status = update.get("metrics", {}).get("status", "unknown")
                print(f"   - {agent_id[:10]}...: Score={score:.1f}, Status={status}")
        
        print(f"\n🎉 多agent协作测试完成!")
        
        return {
            "success": True,
            "assigned_agents": len(assigned_agents),
            "participating_agents": len(participating_agents),
            "all_participated": expected_agents.issubset(participating_agents),
            "execution_time": execution_time,
            "conversation_messages": len(conversation),
            "agent_updates": len(agent_updates)
        }
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🧪 多Agent协作功能测试")
    print("=" * 50)
    
    result = asyncio.run(test_multi_agent_collaboration())
    
    print("\n" + "=" * 50)
    if result.get("success"):
        print("✅ 测试成功完成!")
        print(f"分配Agents: {result['assigned_agents']}")
        print(f"参与Agents: {result['participating_agents']}")
        print(f"全员参与: {'是' if result['all_participated'] else '否'}")
        print(f"执行时间: {result['execution_time']:.1f}秒")
    else:
        print("❌ 测试失败!")
        print(f"错误: {result.get('error', 'Unknown error')}")