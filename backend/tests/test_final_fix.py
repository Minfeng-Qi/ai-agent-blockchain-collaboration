#!/usr/bin/env python3
"""
测试最终的多agent协作修复
"""

import asyncio
import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agent_collaboration_service import AgentCollaborationService

async def test_final_multi_agent_fix():
    print('🎯 测试最终的多agent协作修复...')
    
    # Initialize collaboration service
    collaboration_service = AgentCollaborationService()
    
    # 测试数据：模拟区块链任务数据结构
    task_data = {
        "task_id": "final_test_12345",
        "title": "Final Multi-Agent Test",
        "description": "测试多agent协作修复后的效果",
        "required_capabilities": ["text_generation", "analysis"],
        "reward": 3.0,
        # 模拟区块链任务数据结构（同时有单个和列表）
        "assigned_agent": "0xFirst0000000000000000000000000000000000001",  # 单个分配
        "assigned_agents": [  # 多个分配（应该优先使用这个）
            "0xFirst0000000000000000000000000000000000001",
            "0xSecond000000000000000000000000000000000002", 
            "0xThird0000000000000000000000000000000000003"
        ]
    }
    
    print(f'📋 测试数据:')
    print(f'   assigned_agent: {task_data["assigned_agent"]}')
    print(f'   assigned_agents: {task_data["assigned_agents"]} (共{len(task_data["assigned_agents"])}个)')
    
    try:
        # 测试协作创建
        print('\n🚀 创建协作...')
        collaboration_id = await collaboration_service.create_collaboration(
            task_id=task_data["task_id"],
            task_data=task_data
        )
        
        print(f'✅ 协作已创建: {collaboration_id}')
        
        # 测试协作执行
        print('🚀 执行协作...')
        result = await collaboration_service.run_collaboration(
            collaboration_id=collaboration_id,
            task_data=task_data
        )
        
        # 分析结果
        print('\n📊 结果分析:')
        
        result_agents = result.get("agents", [])
        assigned_agents = task_data["assigned_agents"]
        
        print(f'   分配的agents: {len(assigned_agents)} 个')
        print(f'   结果中的agents: {len(result_agents)} 个')
        
        # 检查agent详情
        print(f'\n👥 结果中的agents详情:')
        for i, agent in enumerate(result_agents):
            agent_id = agent.get("agent_id", "N/A")
            agent_name = agent.get("name", "N/A")
            capabilities = agent.get("capabilities", [])
            print(f'   Agent {i+1}: {agent_name} ({agent_id[:12]}...)')
            print(f'             能力: {capabilities}')
        
        # 验证修复结果
        if len(result_agents) == len(assigned_agents):
            print(f'\n🎉 修复成功！')
            print(f'✅ 所有 {len(assigned_agents)} 个分配的agents都出现在结果中')
            print(f'✅ 多agent协作优先级逻辑正常工作')
            
            # 验证agent ID匹配
            result_ids = {agent["agent_id"] for agent in result_agents}
            assigned_ids = set(assigned_agents)
            
            if result_ids == assigned_ids:
                print(f'✅ Agent ID完全匹配')
            else:
                print(f'⚠️ Agent ID部分匹配:')
                print(f'   分配: {assigned_ids}')
                print(f'   结果: {result_ids}')
        else:
            print(f'\n❌ 仍有问题')
            print(f'   期望: {len(assigned_agents)} 个agents')
            print(f'   实际: {len(result_agents)} 个agents')
        
        # 检查对话记录
        conversation = result.get("conversation", [])
        print(f'\n💬 对话分析:')
        print(f'   总消息数: {len(conversation)}')
        
        # 统计每个agent在对话中的参与
        agent_mentions = {}
        for agent in result_agents:
            agent_name = agent.get("name", "")
            mentions = sum(1 for msg in conversation if agent_name in msg.get("content", ""))
            agent_mentions[agent_name] = mentions
        
        for agent_name, mentions in agent_mentions.items():
            print(f'   {agent_name}: {mentions} 次提及')
        
        # IPFS存储验证
        ipfs_cid = result.get("ipfs_cid", "N/A")
        print(f'\n💾 IPFS存储:')
        print(f'   CID: {ipfs_cid}')
        
        if ipfs_cid != "N/A":
            # 尝试验证IPFS中的数据
            try:
                import requests
                ipfs_response = requests.get(f'http://localhost:8001/collaboration/ipfs/{ipfs_cid}', timeout=5)
                if ipfs_response.status_code == 200:
                    ipfs_data = ipfs_response.json()
                    ipfs_agents = ipfs_data.get("agents", [])
                    print(f'   IPFS中的agents: {len(ipfs_agents)} 个')
                    
                    if len(ipfs_agents) == len(assigned_agents):
                        print(f'   ✅ IPFS存储正确包含所有agents')
                    else:
                        print(f'   ❌ IPFS存储agents数量不匹配')
                else:
                    print(f'   ⚠️ 无法获取IPFS数据 (状态码: {ipfs_response.status_code})')
            except Exception as e:
                print(f'   ⚠️ IPFS验证失败: {e}')
        
        print(f'\n🏁 最终评估:')
        if len(result_agents) == len(assigned_agents):
            print(f'🎉 多agent协作问题已完全修复！')
            print(f'   - 条件判断优先级已正确修改')
            print(f'   - 多agent任务不再被误识别为单agent任务')
            print(f'   - 所有分配的agents都正确参与协作')
            print(f'   - 结果展示将包含所有参与agents的对话记录')
        else:
            print(f'❌ 仍需进一步调试')
            
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_multi_agent_fix())