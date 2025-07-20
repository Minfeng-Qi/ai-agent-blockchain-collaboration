#!/usr/bin/env python3
"""
使用真实区块链任务测试评价功能
Test evaluation functionality with real blockchain task
"""

import asyncio
import sys
import os
import requests
import time
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import contract_service
from services.collaboration_db_service import collaboration_db_service

async def test_real_task_workflow():
    print('🧪 使用真实任务测试完整工作流...')
    
    # 使用有分配agents的真实任务
    task_id = 'df9c4038d7d0b174145f541f14b95ed4daa6d04ac0f77081fcd262f0d086247a'
    
    try:
        # 1. 获取任务详情
        print(f'\n📋 获取任务详情: {task_id[:16]}...')
        contract_service.init_web3()
        contract_service.initialize_contracts()
        
        task_result = contract_service.get_task(task_id)
        if task_result.get('success'):
            task_data = task_result
            print(f'✅ 任务: {task_data.get("title", "Unknown")}')
            print(f'   状态: {task_data.get("status", "unknown")}')
            print(f'   分配的agents: {len(task_data.get("assigned_agents", []))} 个')
            
            assigned_agents = task_data.get('assigned_agents', [])
            for i, agent in enumerate(assigned_agents):
                print(f'     Agent {i+1}: {agent}')
            
            # 2. 如果任务还未完成，先完成它
            if task_data.get('status') != 'completed':
                print(f'\n🏁 完成任务 {task_id[:16]}...')
                
                sender_address = contract_service.w3.eth.accounts[0]
                completion_result = {
                    'task_analysis': 'AI内容质量评估任务已完成',
                    'quality_metrics': {
                        'accuracy': 95,
                        'relevance': 92,
                        'completeness': 88
                    },
                    'recommendations': [
                        '内容质量整体良好',
                        '建议加强细节描述',
                        '保持现有标准'
                    ],
                    'completion_time': time.time()
                }
                
                complete_result = contract_service.complete_task(
                    task_id,
                    json.dumps(completion_result),
                    sender_address
                )
                
                if complete_result.get('success'):
                    print('✅ 任务完成成功')
                    time.sleep(3)  # 等待区块链状态更新
                else:
                    print(f'❌ 任务完成失败: {complete_result}')
                    return
            else:
                print('✅ 任务已完成，可以直接评价')
            
            # 3. 评价任务
            print(f'\n📊 评价任务 {task_id[:16]}...')
            
            evaluation_data = {
                'success': True,
                'rating': 5,
                'evaluator': 'real_data_test',
                'notes': '使用真实数据测试task_id修复功能 - AI内容质量评估任务评价',
                'assigned_agents': assigned_agents  # 使用真实的分配agents
            }
            
            eval_response = requests.post(
                f'http://localhost:8001/tasks/{task_id}/evaluate',
                json=evaluation_data,
                timeout=30
            )
            
            print(f'评价响应状态: {eval_response.status_code}')
            
            if eval_response.status_code == 200:
                eval_result = eval_response.json()
                print('✅ 评价成功!')
                
                data = eval_result.get('data', {})
                print(f'   影响的agent数量: {data.get("total_agents_updated", "unknown")}')
                print(f'   学习事件数量: {len(data.get("learning_events", []))}')
                
                # 显示每个agent的学习事件
                learning_events = data.get('learning_events', [])
                for i, event in enumerate(learning_events):
                    agent_id = event.get('agent_id', 'unknown')
                    reputation_change = event.get('reputation_change', 0)
                    reward = event.get('reward', 0)
                    print(f'     Agent {i+1} ({agent_id[:10]}...): 声誉 {reputation_change:+d}, 奖励 {reward}')
                
                # 4. 等待事件处理
                print('\n⏳ 等待评价事件处理...')
                time.sleep(5)
                
                # 5. 验证数据库中的评价事件
                print(f'\n🔍 验证数据库中的评价事件...')
                
                stored_events = collaboration_db_service.get_blockchain_events(
                    event_type='task_evaluation',
                    task_id=task_id,
                    limit=10
                )
                
                print(f'找到 {len(stored_events)} 个该任务的评价事件')
                
                if stored_events:
                    print('🎉 修复验证成功! 评价事件现在包含正确的task_id!')
                    
                    correct_events = 0
                    for i, event in enumerate(stored_events):
                        task_id_db = event.get('task_id')
                        agent_id = event.get('agent_id', 'N/A')
                        timestamp = event.get('timestamp', 'N/A')
                        
                        print(f'  事件 {i+1}:')
                        print(f'    Task ID: {task_id_db[:16] if task_id_db else "None"}...')
                        print(f'    Agent ID: {agent_id[:10] if agent_id else "None"}...')
                        print(f'    时间: {timestamp}')
                        
                        if task_id_db == task_id:
                            print(f'    状态: ✅ task_id修复成功')
                            correct_events += 1
                        else:
                            print(f'    状态: ❌ task_id不正确')
                        print()
                    
                    print(f'📊 修复统计: {correct_events}/{len(stored_events)} 个事件有正确的task_id')
                
                # 6. 测试任务历史API
                print(f'\n📈 测试任务历史 {task_id[:16]}...')
                
                history_response = requests.get(f'http://localhost:8001/tasks/{task_id}/history')
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    history_events = history_data.get('data', {}).get('history', [])
                    eval_events = [e for e in history_events if e.get('event') == 'evaluated']
                    
                    print(f'任务历史事件总数: {len(history_events)}')
                    print(f'评价事件数量: {len(eval_events)}')
                    
                    if eval_events:
                        print('🎉 最终验证成功! 评价事件正确出现在任务历史中!')
                        
                        for i, eval_event in enumerate(eval_events):
                            details = eval_event.get('details', 'No details')
                            eval_data = eval_event.get('evaluation_data', {})
                            total_agents = eval_data.get('total_agents', 'N/A')
                            rating = eval_data.get('rating', 'N/A')
                            
                            print(f'  评价事件 {i+1}: {details}')
                            print(f'                评分: {rating}/5, 影响: {total_agents} 个agent')
                        
                        # 验证去重功能
                        if len(eval_events) == 1:
                            print('✅ 评价事件去重功能正常工作!')
                            print(f'   原本 {len(assigned_agents)} 个agents的评价被合并为1个事件')
                        else:
                            print(f'⚠️ 发现 {len(eval_events)} 个评价事件，去重功能可能需要检查')
                    
                    else:
                        print('❌ 评价事件仍未出现在任务历史中')
                    
                    print(f'\n📜 完整任务历史:')
                    for i, event in enumerate(history_events):
                        event_type = event.get('event', 'unknown')
                        timestamp = event.get('timestamp', 'N/A')
                        details = event.get('details', 'No details')
                        print(f'  {i+1}. [{event_type}] {timestamp} - {details}')
                else:
                    print(f'❌ 获取任务历史失败: {history_response.status_code}')
                    
            elif eval_response.status_code == 400 and 'already been evaluated' in eval_response.text:
                print('⚠️ 任务已被评价过')
                print('这说明防重复评价机制正常工作')
                
                # 检查现有的评价事件
                print(f'\n📈 检查已评价任务的历史...')
                history_response = requests.get(f'http://localhost:8001/tasks/{task_id}/history')
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    history_events = history_data.get('data', {}).get('history', [])
                    eval_events = [e for e in history_events if e.get('event') == 'evaluated']
                    
                    print(f'任务历史中的评价事件: {len(eval_events)} 个')
                    
                    if eval_events:
                        print('✅ 任务历史中存在评价事件!')
                        for eval_event in eval_events:
                            print(f'  评价详情: {eval_event.get("details", "No details")}')
                    else:
                        print('❌ 任务历史中没有评价事件')
            else:
                print(f'❌ 评价失败: {eval_response.status_code}')
                print(f'   响应: {eval_response.text}')
                
        else:
            print(f'❌ 获取任务失败: {task_result}')
            
    except Exception as e:
        print(f'❌ 测试过程中出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始真实任务测试...")
    asyncio.run(test_real_task_workflow())
    print("\n🏁 测试完成!")