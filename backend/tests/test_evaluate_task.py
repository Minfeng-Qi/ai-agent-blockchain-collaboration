#!/usr/bin/env python3
"""
测试任务评估功能的脚本
"""
import asyncio
import sys
import os
import requests
import json

# 添加backend目录到路径
sys.path.append('/Users/minfeng/Desktop/llm-blockchain/code/backend')

async def test_evaluate_task():
    """测试任务评估API"""
    
    # API基础URL
    base_url = "http://localhost:8001"
    
    # 首先获取一个已完成的任务
    try:
        tasks_response = requests.get(f"{base_url}/tasks/")
        if tasks_response.status_code != 200:
            print(f"❌ Failed to get tasks: {tasks_response.status_code}")
            return
            
        tasks_data = tasks_response.json()
        completed_tasks = [task for task in tasks_data.get("tasks", []) if task.get("status") == "completed"]
        
        if not completed_tasks:
            print("❌ No completed tasks found to evaluate")
            return
            
        task = completed_tasks[0]
        task_id = task["task_id"]
        
        print(f"🎯 Testing evaluation for task: {task_id}")
        print(f"📋 Task title: {task.get('title', 'Unknown')}")
        print(f"👤 Assigned agent: {task.get('assigned_agent', 'None')}")
        
        # 评估数据
        evaluation_data = {
            "success": True,
            "rating": 4,
            "evaluator": "test_script",
            "notes": "Test evaluation for blockchain events"
        }
        
        # 调用评估API
        evaluate_response = requests.post(
            f"{base_url}/tasks/{task_id}/evaluate",
            json=evaluation_data
        )
        
        print(f"\n📊 Evaluation response status: {evaluate_response.status_code}")
        
        if evaluate_response.status_code == 200:
            result = evaluate_response.json()
            print(f"✅ Evaluation successful!")
            print(f"📈 Agents updated: {result.get('data', {}).get('total_agents_updated', 0)}")
            print(f"🎉 Message: {result.get('message', 'No message')}")
            
            # 打印学习事件详情
            learning_events = result.get('data', {}).get('learning_events', [])
            for event in learning_events:
                print(f"🧠 Agent: {event['agent_id']}")
                print(f"   Reputation change: {event['reputation_change']:+d}")
                print(f"   Reward: {event['reward']}")
                print(f"   Blockchain recorded: {event['learning_event'].get('blockchain_recorded', False)}")
                if event['learning_event'].get('transaction_hash'):
                    print(f"   Transaction: {event['learning_event']['transaction_hash']}")
        else:
            print(f"❌ Evaluation failed: {evaluate_response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting task evaluation test...")
    asyncio.run(test_evaluate_task())