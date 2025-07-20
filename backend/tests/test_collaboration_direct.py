#!/usr/bin/env python3
"""
直接测试协作功能，跳过复杂的API调用
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append('/Users/minfeng/Desktop/llm-blockchain/code/backend')

from services.agent_collaboration_service import AgentCollaborationService

async def test_direct_collaboration():
    """直接测试协作服务"""
    print("🧪 直接测试Agent协作服务")
    
    # 创建协作服务实例
    collaboration_service = AgentCollaborationService()
    
    # 模拟任务数据
    task_data = {
        "task_id": "test_task_123",
        "title": "Complete Content Generation Pipeline",
        "description": "Create a comprehensive content generation system that includes research, writing, editing, and review phases. The system should support multiple content types and ensure quality output.",
        "type": "content_generation",
        "required_capabilities": ["text_generation", "data_analysis", "classification"]
    }
    
    # 模拟多个agents
    agents_info = [
        {
            "agent_id": "0x1111111111111111111111111111111111111111",
            "name": "DataAnalysisExpert",
            "capabilities": ["data_analysis", "classification"],
            "reputation": 85
        },
        {
            "agent_id": "0x2222222222222222222222222222222222222222", 
            "name": "CodeGenerationMaster",
            "capabilities": ["code_generation", "text_generation"],
            "reputation": 92
        },
        {
            "agent_id": "0x3333333333333333333333333333333333333333",
            "name": "NLPSpecialist", 
            "capabilities": ["sentiment_analysis", "text_generation", "summarization"],
            "reputation": 88
        },
        {
            "agent_id": "0x4444444444444444444444444444444444444444",
            "name": "TranslationExpert",
            "capabilities": ["translation", "text_generation"],
            "reputation": 90
        }
    ]
    
    # 设置assigned_agents到task_data中
    task_data["assigned_agents"] = agents_info
    
    print(f"📋 测试任务: {task_data['title']}")
    print(f"🤖 参与Agents: {len(agents_info)}个")
    for agent in agents_info:
        print(f"   - {agent['name']} ({agent['capabilities']})")
    
    try:
        # 运行协作
        print("\n🚀 开始协作...")
        collaboration_id = "test_collab_123"
        
        result = await collaboration_service.run_collaboration(collaboration_id, task_data)
        
        print(f"\n✅ 协作完成!")
        print(f"状态: {result.get('status', 'unknown')}")
        print(f"对话消息数: {len(result.get('conversation', []))}")
        print(f"参与agents: {len(result.get('agents', []))}")
        
        # 显示协作对话的前几条
        conversation = result.get('conversation', [])
        if conversation:
            print(f"\n💬 协作对话片段:")
            for i, msg in enumerate(conversation[:6]):  # 显示前6条消息
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:150]  # 截断长消息
                print(f"   {i+1}. [{role}] {content}...")
        
        # 显示agent更新
        agent_updates = result.get('agent_updates', [])
        if agent_updates:
            print(f"\n📊 Agent表现:")
            for update in agent_updates:
                agent_id = update.get('agent_id', 'unknown')
                score = update.get('performance_score', 0)
                status = update.get('metrics', {}).get('status', 'unknown')
                print(f"   - {agent_id[:10]}...: Score={score:.1f}, Status={status}")
        
        return result
        
    except Exception as e:
        print(f"❌ 协作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎯 直接测试多Agent协作功能")
    print("=" * 60)
    
    result = asyncio.run(test_direct_collaboration())
    
    print("\n" + "=" * 60)
    if result:
        print("✅ 测试成功!")
        print("多Agent协作功能已验证正常工作")
    else:
        print("❌ 测试失败!")
        print("需要进一步调试协作功能")