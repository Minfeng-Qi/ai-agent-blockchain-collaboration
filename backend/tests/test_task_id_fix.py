#!/usr/bin/env python3
"""
测试任务ID修复功能
Test task_id fix for evaluation events
"""

import asyncio
import sys
import os
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import contract_service
from services.collaboration_db_service import collaboration_db_service

async def test_evaluation_task_id_fix():
    print('🧪 测试评价事件task_id修复...')
    
    try:
        # 1. 初始化区块链连接
        contract_service.init_web3()
        contract_service.initialize_contracts()
        
        # 2. 获取已完成的任务
        tasks_result = contract_service.get_all_tasks()
        if not tasks_result.get('success'):
            print('❌ 无法获取任务列表')
            return
            
        tasks = tasks_result.get('tasks', [])
        completed_tasks = [t for t in tasks if t.get('status') == 'completed']
        
        if not completed_tasks:
            print('❌ 没有找到已完成的任务')
            return
            
        # 3. 选择测试任务
        test_task = completed_tasks[0]
        task_id = test_task.get('task_id')
        
        print(f'\n📋 选择测试任务: {task_id}')
        print(f'   标题: {test_task.get("title", "Unknown")}')
        
        # 4. 检查当前的评价事件
        print('\n🔍 检查数据库中的评价事件...')
        
        # 检查特定任务的评价事件
        task_events = collaboration_db_service.get_blockchain_events(
            event_type='task_evaluation',
            task_id=task_id,
            limit=10
        )
        
        print(f'任务 {task_id} 的评价事件: {len(task_events)} 个')
        
        # 检查最近的所有评价事件
        recent_events = collaboration_db_service.get_blockchain_events(
            event_type='task_evaluation',
            limit=5
        )
        
        print(f'\n最近的 {len(recent_events)} 个评价事件:')
        for i, event in enumerate(recent_events):
            task_id_db = event.get('task_id')
            agent_id = event.get('agent_id', 'N/A')
            timestamp = event.get('timestamp', 'N/A')
            
            print(f'  {i+1}. Task ID: {task_id_db}')
            print(f'      Agent ID: {agent_id}')
            print(f'      时间: {timestamp}')
            
            if task_id_db and task_id_db != 'None':
                print(f'      修复状态: 已修复 ✅')
            else:
                print(f'      修复状态: 未修复 ❌')
            print()
        
        # 5. 测试任务历史API
        print(f'\n📈 测试任务历史 {task_id}...')
        try:
            history_response = requests.get(f'http://localhost:8001/tasks/{task_id}/history', timeout=10)
            if history_response.status_code == 200:
                history_data = history_response.json()
                history_events = history_data.get('data', {}).get('history', [])
                eval_events = [e for e in history_events if e.get('event') == 'evaluated']
                
                print(f'任务历史中的评价事件数量: {len(eval_events)}')
                
                if eval_events:
                    print('✅ 评价事件出现在任务历史中!')
                    for i, eval_event in enumerate(eval_events):
                        details = eval_event.get('details', 'No details')
                        eval_data = eval_event.get('evaluation_data', {})
                        total_agents = eval_data.get('total_agents', 'N/A')
                        rating = eval_data.get('rating', 'N/A')
                        
                        print(f'  评价 {i+1}: {details}')
                        print(f'            评分: {rating}/5, 影响: {total_agents} 个agent')
                else:
                    print('❌ 评价事件没有出现在任务历史中')
                    print('   可能原因:')
                    print('   1. 旧的评价数据没有正确的task_id')
                    print('   2. 需要进行新的评价来测试修复效果')
                    
                print(f'\n📜 完整任务历史 ({len(history_events)} 个事件):')
                for i, event in enumerate(history_events):
                    event_type = event.get('event', 'unknown')
                    timestamp = event.get('timestamp', 'N/A')
                    details = event.get('details', 'No details')
                    print(f'  {i+1}. [{event_type}] {timestamp} - {details}')
                    
            else:
                print(f'❌ 获取任务历史失败: {history_response.status_code}')
                print(f'   响应: {history_response.text}')
                
        except Exception as e:
            print(f'❌ 任务历史API请求失败: {e}')
        
        # 6. 总结
        print('\n📊 修复状态总结:')
        
        # 检查是否有带正确task_id的新评价事件
        events_with_task_id = [e for e in recent_events if e.get('task_id') and e.get('task_id') != 'None']
        
        if events_with_task_id:
            print('✅ 修复成功: 新的评价事件现在包含正确的task_id')
            print(f'   有效事件数量: {len(events_with_task_id)}')
        else:
            print('⚠️  修复已应用，但需要新的评价事件来验证效果')
            print('   建议: 对一个已完成任务进行评价以验证修复')
        
        if task_events:
            print('✅ 任务历史功能正常: 能够正确检索特定任务的评价事件')
        else:
            print('❌ 任务历史功能需要改进: 无法检索到该任务的评价事件')
            
    except Exception as e:
        print(f'❌ 测试过程中出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试task_id修复功能...")
    asyncio.run(test_evaluation_task_id_fix())
    print("\n🏁 测试完成!")