#!/usr/bin/env python3
"""
测试单agent任务的协作结果是否正确
"""
import requests
import json

def test_single_agent_task():
    """测试单agent任务的协作结果"""
    
    base_url = "http://localhost:8001"
    
    # 检查Build REST API Documentation任务
    task_id = "6136fa93ca9c0721cfd6e2b969a04e6c9481937995e477e90b2975e9c54d3848"
    
    print(f"🔍 Testing single agent task: {task_id}")
    
    try:
        # 获取任务详情
        task_response = requests.get(f"{base_url}/tasks/{task_id}")
        if task_response.status_code == 200:
            task_data = task_response.json()
            task = task_data["task"]
            
            print(f"📋 Task: {task['title']}")
            print(f"👤 Assigned agent: {task.get('assigned_agent', 'None')}")
            print(f"👥 Assigned agents: {task.get('assigned_agents', [])}")
            print(f"📊 Status: {task['status']}")
            
            # 检查任务结果
            if task['status'] == 'completed' and task.get('result'):
                result_data = json.loads(task['result'])
                participants = result_data.get('participants', [])
                
                print(f"\n🔍 Result analysis:")
                print(f"   Participants in result: {len(participants)}")
                
                if len(participants) == 1:
                    print("   ✅ Correct: Single agent task has single participant")
                    participant = participants[0]
                    print(f"   Agent ID: {participant.get('agent_id', 'N/A')}")
                    print(f"   Agent name: {participant.get('name', 'N/A')}")
                    print(f"   Capabilities: {participant.get('capabilities', [])}")
                else:
                    print(f"   ❌ Error: Single agent task has {len(participants)} participants!")
                    for i, p in enumerate(participants):
                        print(f"     Participant {i+1}: {p.get('name', 'N/A')} ({p.get('agent_id', 'N/A')})")
                
                # 检查IPFS数据
                ipfs_cid = result_data.get('conversation_ipfs')
                if ipfs_cid:
                    print(f"\n🔗 Checking IPFS data: {ipfs_cid}")
                    ipfs_response = requests.get(f"{base_url}/collaboration/ipfs/{ipfs_cid}")
                    if ipfs_response.status_code == 200:
                        ipfs_data = ipfs_response.json()
                        ipfs_agents = ipfs_data.get('agents', [])
                        
                        print(f"   IPFS agents count: {len(ipfs_agents)}")
                        if len(ipfs_agents) == 1:
                            print("   ✅ IPFS data correctly shows single agent")
                        else:
                            print(f"   ❌ IPFS data shows {len(ipfs_agents)} agents!")
                            for i, agent in enumerate(ipfs_agents):
                                print(f"     IPFS Agent {i+1}: {agent.get('name', 'N/A')}")
                    else:
                        print(f"   ❌ Failed to fetch IPFS data: {ipfs_response.status_code}")
        else:
            print(f"❌ Failed to get task: {task_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

def test_create_new_single_agent_task():
    """创建一个新的单agent任务来测试修复"""
    
    base_url = "http://localhost:8001"
    
    print(f"\n🆕 Creating new single agent task for testing...")
    
    try:
        # 创建新任务
        task_data = {
            "title": "Test Single Agent Task",
            "description": "This is a test task to verify single agent collaboration works correctly",
            "type": "text_generation", 
            "reward": 1.0,
            "required_capabilities": ["text_generation"],
            "min_reputation": 50
        }
        
        create_response = requests.post(f"{base_url}/tasks/", json=task_data)
        print(f"Create response status: {create_response.status_code}")
        print(f"Create response body: {create_response.text}")
        if create_response.status_code == 200:
            result = create_response.json()
            new_task_id = result.get("task", {}).get("task_id")
            print(f"✅ Created task: {new_task_id}")
            
            # 启动协作（这会自动选择agents）
            assign_response = requests.post(f"{base_url}/tasks/{new_task_id}/start-collaboration", json={})
            print(f"Start collaboration response status: {assign_response.status_code}")
            print(f"Start collaboration response body: {assign_response.text}")
            if assign_response.status_code == 200:
                assign_result = assign_response.json()
                selected_agents = assign_result.get("selected_agents", [])
                team_size = len(selected_agents)
                assignment_type = "single_agent" if team_size == 1 else "multi_agent_collaboration"
                print(f"✅ Started collaboration: {assignment_type} with {team_size} agents")
                print(f"   Selected agents: {selected_agents}")
                
                # 等待后台系统自动执行
                print("⏳ Waiting for background execution...")
                import time
                time.sleep(15)
                
                # 检查结果
                task_response = requests.get(f"{base_url}/tasks/{new_task_id}")
                if task_response.status_code == 200:
                    task = task_response.json()["task"]
                    if task["status"] == "completed":
                        print("✅ Task completed, checking collaboration result...")
                        result_data = json.loads(task["result"])
                        participants = result_data.get("participants", [])
                        print(f"   Participants: {len(participants)}")
                        
                        if len(participants) == 1:
                            print("   ✅ SUCCESS: Single agent task correctly has 1 participant!")
                        else:
                            print(f"   ❌ FAILED: Single agent task has {len(participants)} participants")
                    else:
                        print(f"   Task status: {task['status']} (may need more time)")
                        
            else:
                print(f"❌ Failed to assign task: {assign_response.status_code}")
        else:
            print(f"❌ Failed to create task: {create_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during new task test: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing single agent task collaboration...")
    test_single_agent_task()
    test_create_new_single_agent_task()  # 启用创建新任务测试
    print("✅ Test completed!")