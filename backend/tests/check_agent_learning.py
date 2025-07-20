#!/usr/bin/env python3
"""
检查agents的学习事件分配情况
Check learning event distribution among agents
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.collaboration_db_service import collaboration_db_service

def check_agent_learning_events():
    print('🔍 检查agents的学习事件分配情况...')
    
    # 使用刚才测试的真实任务
    task_id = 'df9c4038d7d0b174145f541f14b95ed4daa6d04ac0f77081fcd262f0d086247a'
    agents = [
        '0xa5A1E9Bd425AEec01428f871D8a9BDD78bCD7b01',
        '0xDE36D579646B6F567686b03Eb0C964dE6C7DE2F2'
    ]
    
    print(f'\n📋 任务ID: {task_id[:16]}...')
    print(f'参与agents: {len(agents)} 个')
    
    # 1. 检查该任务的所有评价事件
    print(f'\n📊 检查任务的评价事件分布...')
    
    all_task_events = collaboration_db_service.get_blockchain_events(
        event_type='task_evaluation',
        task_id=task_id,
        limit=10
    )
    
    print(f'该任务的评价事件总数: {len(all_task_events)}')
    
    agent_events = {}
    for event in all_task_events:
        agent_id = event.get('agent_id')
        if agent_id:
            if agent_id not in agent_events:
                agent_events[agent_id] = []
            agent_events[agent_id].append(event)
    
    print(f'涉及的agents数量: {len(agent_events)}')
    
    # 2. 检查每个agent的学习事件详情
    print(f'\n📖 每个agent的学习事件详情:')
    
    for i, agent_id in enumerate(agents):
        print(f'\n  Agent {i+1}: {agent_id}')
        
        # 检查该agent在这个任务中的学习事件
        agent_task_events = [e for e in all_task_events if e.get('agent_id') == agent_id]
        
        print(f'    该任务的学习事件数量: {len(agent_task_events)}')
        
        if agent_task_events:
            for j, event in enumerate(agent_task_events):
                timestamp = event.get('timestamp', 'N/A')
                event_data = event.get('event_data') or event.get('data')
                
                if isinstance(event_data, str):
                    try:
                        event_data = json.loads(event_data)
                    except:
                        event_data = {}
                
                rating = event_data.get('rating', 'N/A')
                reputation_change = event_data.get('reputation_change', 'N/A')
                reward = event_data.get('reward', 'N/A')
                success = event_data.get('success', 'N/A')
                
                print(f'      事件 {j+1}:')
                print(f'        时间: {timestamp}')
                print(f'        评分: {rating}/5')
                print(f'        声誉变化: {reputation_change}')
                print(f'        奖励: {reward}')
                print(f'        成功: {success}')
        else:
            print(f'    ❌ 该agent没有学习事件')
    
    # 3. 检查agents的总体学习历史
    print(f'\n📚 检查agents的总体学习历史（最近5个事件）:')
    
    for i, agent_id in enumerate(agents):
        print(f'\n  Agent {i+1}: {agent_id[:10]}...')
        
        agent_learning_events = collaboration_db_service.get_agent_learning_events(agent_id, limit=5)
        
        print(f'    总学习事件数量: {len(agent_learning_events)}')
        
        if agent_learning_events:
            for j, event in enumerate(agent_learning_events):
                event_type = event.get('event_type', 'unknown')
                timestamp = event.get('timestamp', 'N/A')
                task_id_event = event.get('task_id', 'N/A')
                
                data = event.get('data', {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        data = {}
                
                rating = data.get('rating', 'N/A')
                reward = data.get('reward', 'N/A')
                
                print(f'      事件 {j+1}: [{event_type}] {timestamp}')
                
                if task_id_event != 'N/A':
                    task_display = task_id_event[:16] + '...'
                else:
                    task_display = 'N/A'
                print(f'               任务: {task_display}')
                print(f'               评分: {rating}, 奖励: {reward}')
        else:
            print(f'    ❌ 该agent没有学习历史')
    
    # 4. 总结
    print(f'\n📊 学习事件分配总结:')
    print(f'✅ 参与任务的agents总数: {len(agents)}')
    print(f'✅ 获得学习事件的agents数: {len(agent_events)}')
    
    if len(agent_events) == len(agents):
        print(f'🎉 确认: 所有参与agents都获得了学习事件!')
        print(f'   每个agent都会从任务评价中学习和获得奖励')
    else:
        print(f'⚠️ 注意: 有 {len(agents) - len(agent_events)} 个agents没有获得学习事件')
    
    # 验证学习事件的一致性
    if agent_events:
        consistent_data = True
        base_rating = None
        base_success = None
        
        for agent_id, events in agent_events.items():
            for event in events:
                event_data = event.get('event_data') or event.get('data', {})
                if isinstance(event_data, str):
                    try:
                        event_data = json.loads(event_data)
                    except:
                        event_data = {}
                
                rating = event_data.get('rating')
                success = event_data.get('success')
                
                if base_rating is None:
                    base_rating = rating
                    base_success = success
                elif rating != base_rating or success != base_success:
                    consistent_data = False
                    break
        
        if consistent_data:
            print(f'✅ 学习事件数据一致: 所有agents获得相同的评分 ({base_rating}/5) 和成功状态 ({base_success})')
        else:
            print(f'⚠️ 学习事件数据不一致: agents获得了不同的评分或成功状态')
    
    # 5. 检查奖励分配
    print(f'\n💰 奖励分配详情:')
    total_rewards = 0
    for agent_id, events in agent_events.items():
        agent_total_reward = 0
        for event in events:
            event_data = event.get('event_data') or event.get('data', {})
            if isinstance(event_data, str):
                try:
                    event_data = json.loads(event_data)
                except:
                    event_data = {}
            
            reward = event_data.get('reward', 0)
            agent_total_reward += reward
            total_rewards += reward
        
        print(f'  {agent_id[:10]}... 获得奖励: {agent_total_reward}')
    
    print(f'  总奖励分配: {total_rewards}')
    if len(agent_events) > 0:
        avg_reward = total_rewards / len(agent_events)
        print(f'  平均每agent奖励: {avg_reward}')

if __name__ == "__main__":
    check_agent_learning_events()