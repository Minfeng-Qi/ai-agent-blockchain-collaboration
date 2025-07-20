#!/usr/bin/env python3
"""
简化的多agent测试：直接修改现有任务的assigned_agents字段进行测试
"""

import requests
import json

def test_simple_multi_agent():
    """简化测试：手动设置多个agents并测试执行"""
    
    # 1. 获取一个assigned状态的任务
    print("1. 获取已分配的任务...")
    response = requests.get("http://localhost:8001/tasks/", params={"status": "assigned"})
    
    if response.status_code != 200:
        print(f"❌ 获取任务失败: {response.status_code}")
        return
    
    tasks = response.json().get("tasks", [])
    if not tasks:
        print("❌ 没有找到assigned状态的任务")
        return
    
    task = tasks[0]
    task_id = task["task_id"]
    print(f"✅ 找到任务: {task['title']} (ID: {task_id})")
    print(f"   当前状态: {task['status']}")
    print(f"   已分配agent: {task.get('assigned_agent', 'None')}")
    print(f"   已分配agents: {task.get('assigned_agents', [])}")
    
    # 2. 获取所有可用agents
    print("\n2. 获取可用agents...")
    agents_response = requests.get("http://localhost:8001/agents/")
    
    if agents_response.status_code != 200:
        print(f"❌ 获取agents失败: {agents_response.status_code}")
        return
    
    agents_data = agents_response.json()
    available_agents = agents_data.get("agents", [])
    
    if len(available_agents) < 3:
        print(f"❌ 需要至少3个agents，当前只有{len(available_agents)}个")
        return
    
    print(f"✅ 找到 {len(available_agents)} 个agents")
    selected_agents = available_agents[:4]  # 选择前4个agents
    
    for i, agent in enumerate(selected_agents):
        print(f"   {i+1}. {agent['name']} ({agent['agent_id'][:10]}...)")
    
    # 3. 手动调用start_agent_collaboration来设置多个agents
    print(f"\n3. 为任务设置多个agents...")
    
    # 由于我们需要直接操作区块链或者模拟数据，让我们用一个不同的方法
    # 直接测试execute-collaboration是否能处理手动设置的agents
    
    # 先检查当前任务详情
    task_detail_response = requests.get(f"http://localhost:8001/tasks/{task_id}")
    if task_detail_response.status_code == 200:
        task_detail = task_detail_response.json()
        print(f"任务详情: assigned_agents = {task_detail.get('assigned_agents', [])}")
        
        # 如果assigned_agents为空，我们需要想办法设置它
        if not task_detail.get('assigned_agents', []):
            print("⚠️  assigned_agents为空，需要设置多个agents")
            
            # 作为测试，我们可以通过重新分配来设置多个agents
            print("   尝试重新分配任务为协作模式...")
            
            # 先将任务状态改回open（如果可能的话）
            # 由于这比较复杂，我们先直接测试execute-collaboration的错误处理
            
    # 4. 直接测试execute-collaboration
    print(f"\n4. 测试协作执行...")
    execute_response = requests.post(f"http://localhost:8001/tasks/{task_id}/execute-collaboration")
    
    print(f"执行状态码: {execute_response.status_code}")
    print(f"响应内容: {execute_response.text}")
    
    if execute_response.status_code == 400:
        response_data = execute_response.json()
        if "No agents assigned" in response_data.get("detail", ""):
            print("✅ 确认问题：任务没有assigned_agents，需要修复分配逻辑")
            
            # 让我们测试一个fresh的协作分配
            print("\n5. 测试新的协作分配...")
            
            # 获取一个open状态的任务
            open_tasks_response = requests.get("http://localhost:8001/tasks/", params={"status": "open"})
            if open_tasks_response.status_code == 200:
                open_tasks = open_tasks_response.json().get("tasks", [])
                if open_tasks:
                    open_task = open_tasks[0]
                    open_task_id = open_task["task_id"]
                    
                    print(f"找到open任务: {open_task['title']}")
                    
                    # 使用协作模式分配
                    collab_assign_response = requests.post(
                        f"http://localhost:8001/tasks/{open_task_id}/smart-assign",
                        params={"collaborative": True, "max_agents": 4}
                    )
                    
                    print(f"协作分配状态码: {collab_assign_response.status_code}")
                    if collab_assign_response.status_code == 200:
                        assign_data = collab_assign_response.json()
                        print(f"分配结果: {json.dumps(assign_data, indent=2)}")
                        
                        # 检查分配后的任务状态
                        updated_task_response = requests.get(f"http://localhost:8001/tasks/{open_task_id}")
                        if updated_task_response.status_code == 200:
                            updated_task = updated_task_response.json()
                            print(f"分配后的assigned_agents: {updated_task.get('assigned_agents', [])}")
                            
                            # 如果有agents，测试执行
                            if updated_task.get('assigned_agents', []):
                                print("✅ 成功设置多个agents，现在测试执行...")
                                final_execute_response = requests.post(f"http://localhost:8001/tasks/{open_task_id}/execute-collaboration")
                                print(f"最终执行状态码: {final_execute_response.status_code}")
                                print(f"最终执行响应: {final_execute_response.text[:500]}...")
                            else:
                                print("❌ 分配后仍然没有assigned_agents")
                    else:
                        print(f"协作分配失败: {collab_assign_response.text}")
                else:
                    print("❌ 没有找到open状态的任务")
            else:
                print("❌ 获取open任务失败")
        else:
            print(f"其他错误: {response_data.get('detail', 'Unknown error')}")
    else:
        print(f"意外的响应: {execute_response.text}")

if __name__ == "__main__":
    print("🧪 简化多Agent测试")
    print("=" * 50)
    
    test_simple_multi_agent()
    
    print("\n" + "=" * 50)
    print("测试完成")