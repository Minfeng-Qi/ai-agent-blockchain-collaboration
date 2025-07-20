#!/usr/bin/env python3
"""
Test the multi-agent collaboration fix
"""

import asyncio
import sys
import os
import json

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agent_collaboration_service import AgentCollaborationService

async def test_multi_agent_collaboration_fix():
    print('🧪 Testing multi-agent collaboration fix...')
    
    # Initialize collaboration service
    collaboration_service = AgentCollaborationService()
    
    # Test data: multi-agent task
    task_data = {
        "task_id": "test_multi_agent_collaboration_fix_12345",
        "title": "Multi-Agent Collaboration Fix Test",
        "description": "This task tests whether both assigned agents participate in task execution with independent LLM API calls",
        "required_capabilities": ["text_generation", "summarization"],
        "reward": 2.5,
        "assigned_agents": []  # Will be set below
    }
    
    # Test with 3 agents (similar to the real task)
    agents_info = [
        {
            "agent_id": "0xDE36D579646B6F567686b03Eb0C964dE6C7DE2F2",
            "name": "Agent_7DE2F2",
            "capabilities": ["text_generation", "data_analysis"],
            "reputation": 85
        },
        {
            "agent_id": "0xb026DD162B2Cb197A91cBb091A9E794Dbbd8eFC7",
            "name": "Agent_8eFC7",
            "capabilities": ["summarization", "sentiment_analysis"],
            "reputation": 90
        },
        {
            "agent_id": "0x9b7f0892faC0fD78098Dc23E69901BF83442334A",
            "name": "Agent_334A",
            "capabilities": ["translation", "text_generation"],
            "reputation": 88
        }
    ]
    
    # Set the assigned agents in task_data
    task_data["assigned_agents"] = agents_info
    
    print(f'📋 Testing with {len(agents_info)} agents:')
    for i, agent in enumerate(agents_info):
        print(f'   Agent {i+1}: {agent["name"]} ({agent["agent_id"][:10]}...)')
    
    try:
        # First create collaboration, then run it
        print('\n🚀 Creating collaboration...')
        collaboration_id = await collaboration_service.create_collaboration(
            task_id=task_data["task_id"],
            task_data=task_data
        )
        
        print(f'✅ Collaboration created: {collaboration_id}')
        
        # Now run the collaboration to get the full result
        print('🚀 Running collaboration...')
        result = await collaboration_service.run_collaboration(
            collaboration_id=collaboration_id,
            task_data=task_data
        )
        
        print('✅ Collaboration completed!')
        print(f'   Collaboration ID: {result.get("collaboration_id", "N/A")}')
        print(f'   Status: {result.get("status", "N/A")}')
        
        # Check the result agents
        result_agents = result.get("agents", [])
        print(f'\n📊 Result Analysis:')
        print(f'   Assigned agents: {len(agents_info)}')
        print(f'   Participating agents in result: {len(result_agents)}')
        
        if len(result_agents) == len(agents_info):
            print('🎉 SUCCESS: All assigned agents are in the result!')
            print('   The multi-agent collaboration fix is working correctly!')
        else:
            print('❌ ISSUE: Not all assigned agents are in the result')
            print(f'   Expected {len(agents_info)} agents, got {len(result_agents)}')
        
        # Show participating agents
        print(f'\n👥 Participating agents:')
        for i, agent in enumerate(result_agents):
            agent_id = agent.get("agent_id", "N/A")
            agent_name = agent.get("name", "N/A")
            print(f'   {i+1}. {agent_name} ({agent_id[:10]}...)')
        
        # Check agent updates (which contain participation info)
        agent_updates = result.get("agent_updates", {})
        if agent_updates:
            print(f'\n📈 Agent Updates:')
            for agent_id, update_info in agent_updates.items():
                print(f'   {agent_id[:10]}...: {update_info}')
        
        # Check conversation length as indicator of participation
        conversation = result.get("conversation", [])
        print(f'\n💬 Conversation:')
        print(f'   Total messages: {len(conversation)}')
        
        # Count mentions of each agent in conversation
        conversation_text = json.dumps(conversation).lower()
        agent_mentions = {}
        for agent in agents_info:
            agent_name = agent["name"].lower()
            mentions = conversation_text.count(agent_name.lower())
            agent_mentions[agent["name"]] = mentions
            print(f'   {agent["name"]} mentioned {mentions} times')
        
        # Final assessment
        print(f'\n🔍 Final Assessment:')
        if len(result_agents) == len(agents_info):
            print('✅ Multi-agent result tracking: FIXED')
        else:
            print('❌ Multi-agent result tracking: STILL HAS ISSUES')
            
        participating_count = sum(1 for count in agent_mentions.values() if count > 0)
        if participating_count == len(agents_info):
            print('✅ Multi-agent conversation participation: ALL AGENTS PARTICIPATED')
        else:
            print(f'⚠️ Multi-agent conversation participation: {participating_count}/{len(agents_info)} AGENTS PARTICIPATED')
            
    except Exception as e:
        print(f'❌ Test failed with error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting multi-agent collaboration fix test...")
    asyncio.run(test_multi_agent_collaboration_fix())
    print("\n🏁 Test completed!")