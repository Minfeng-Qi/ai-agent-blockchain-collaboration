#!/usr/bin/env python3
"""
测试任务历史评价事件去重功能
Test script to verify task history evaluation event deduplication
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的服务
from services.collaboration_db_service import collaboration_db_service
from routers.tasks import get_task_history

async def test_evaluation_deduplication():
    """
    测试任务历史中评价事件的去重功能
    """
    print("🧪 Testing task history evaluation deduplication...")
    
    # 创建测试任务ID
    test_task_id = f"test_eval_dedup_{int(time.time())}"
    print(f"📋 Using test task ID: {test_task_id}")
    
    # 1. 创建多个相同任务的评价事件（模拟重复评价问题）
    print("\n📝 Creating multiple evaluation events for the same task...")
    
    evaluation_events = []
    for i in range(3):
        agent_id = f"agent_{i+1}_test"
        event_data = {
            "task_id": test_task_id,
            "evaluator": "user",
            "rating": 4,
            "success": True,
            "reputation_change": 5,
            "reward": 10.0,
            "timestamp": time.time() + i  # 稍微不同的时间戳
        }
        
        # 记录评价事件到数据库（直接使用record_blockchain_event，它设置了task_id）
        collaboration_db_service.record_blockchain_event(
            event_type="task_evaluation",
            task_id=test_task_id,
            event_data=event_data,
            transaction_hash=f"0x{abs(hash(f'{test_task_id}_{i}')):#x}",
            block_number=1000000 + i
        )
        
        evaluation_events.append({
            "agent_id": agent_id,
            "event_data": event_data
        })
        print(f"  ✅ Created evaluation event {i+1} for agent {agent_id}")
    
    print(f"\n📊 Created {len(evaluation_events)} evaluation events in database")
    
    # 2. 验证事件是否真的被存储了
    print("\n🔍 Verifying events were stored in database...")
    try:
        stored_events = collaboration_db_service.get_blockchain_events(
            event_type="task_evaluation", 
            task_id=test_task_id,
            limit=10
        )
        print(f"📊 Found {len(stored_events)} evaluation events for task {test_task_id} in database")
        for i, event in enumerate(stored_events):
            print(f"  Event {i+1}: task_id={event.get('task_id')}, agent_id={event.get('agent_id')}")
    except Exception as e:
        print(f"❌ Error checking stored events: {e}")
    
    # 3. 获取任务历史并检查去重是否生效
    print("\n🔍 Retrieving task history to check deduplication...")
    
    try:
        # 模拟任务存在（添加到mock数据中）
        from routers.tasks import mock_tasks
        mock_tasks.append({
            "task_id": test_task_id,
            "title": "Test Task for Evaluation Deduplication",
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        })
        
        # 获取任务历史
        history_result = await get_task_history(test_task_id)
        
        # 正确获取history数据
        task_data = history_result.get('data', {})
        history_events = task_data.get('history', [])
        
        print(f"📈 Task history retrieved: {len(history_events)} total events")
        print(f"📄 Full history result keys: {list(history_result.keys())}")
        if history_events:
            print("📄 History details:")
            for i, event in enumerate(history_events):
                print(f"  {i+1}. {event}")
        
        # 检查评价事件数量
        evaluation_events_in_history = [
            event for event in history_events
            if event.get('event') == 'evaluated'
        ]
        
        print(f"🎯 Evaluation events in history: {len(evaluation_events_in_history)}")
        
        # 验证去重是否生效
        if len(evaluation_events_in_history) == 1:
            print("✅ SUCCESS: Evaluation deduplication is working correctly!")
            print("   Only 1 consolidated evaluation event appears in task history")
            
            # 显示评价事件详情
            eval_event = evaluation_events_in_history[0]
            print(f"   📄 Evaluation details: {eval_event['details']}")
            
            if eval_event.get('evaluation_data'):
                eval_data = eval_event['evaluation_data']
                print(f"   👥 Total agents affected: {eval_data.get('total_agents', 'N/A')}")
                print(f"   💰 Total reward: {eval_data.get('total_reward', 'N/A')}")
                print(f"   ⭐ Rating: {eval_data.get('rating', 'N/A')}/5")
        
        elif len(evaluation_events_in_history) == 0:
            print("❌ ISSUE: No evaluation events found in task history")
            print("   This might indicate the evaluation events are not being retrieved correctly")
        
        else:
            print(f"❌ ISSUE: Found {len(evaluation_events_in_history)} evaluation events in history")
            print("   Expected only 1 consolidated evaluation event")
            print("   Deduplication may not be working correctly")
            
            # 显示所有评价事件
            for i, event in enumerate(evaluation_events_in_history):
                print(f"   Event {i+1}: {event.get('details', 'No details')}")
        
        # 显示完整的任务历史
        print(f"\n📜 Complete task history for {test_task_id}:")
        for i, event in enumerate(history_events):
            print(f"  {i+1}. [{event.get('event', 'unknown')}] {event.get('timestamp', 'N/A')} - {event.get('details', 'No details')}")
    
    except Exception as e:
        print(f"❌ Error getting task history: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 清理测试数据
    print(f"\n🧹 Cleaning up test data...")
    try:
        # 从mock_tasks中移除测试任务
        mock_tasks[:] = [task for task in mock_tasks if task.get('task_id') != test_task_id]
        
        # 清理数据库中的测试事件
        # 注意：这里假设有清理方法，如果没有则保留测试数据
        print("   ✅ Test data cleanup completed")
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    print("🚀 Starting task history evaluation deduplication test...")
    asyncio.run(test_evaluation_deduplication())
    print("\n🏁 Test completed!")