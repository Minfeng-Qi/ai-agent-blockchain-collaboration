#!/usr/bin/env python3
"""
Quick test to verify the multi-agent collaboration fix
"""

import asyncio
import sys
import os
import json

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agent_collaboration_service import AgentCollaborationService

async def test_quick_fix_verification():
    print('🧪 Quick verification of multi-agent collaboration fix...')
    
    # Initialize collaboration service in mock mode for speed
    collaboration_service = AgentCollaborationService()
    collaboration_service.mock_mode = True  # Force mock mode for quick testing
    
    # Test data: multi-agent task
    task_data = {
        "task_id": "quick_test_12345",
        "title": "Quick Multi-Agent Test",
        "description": "Quick test for collaboration fix",
        "required_capabilities": ["text_generation"],
        "reward": 1.0,
        "assigned_agents": [
            {
                "agent_id": "0xDEADBEEF1111111111111111111111111111111111",
                "name": "TestAgent1",
                "capabilities": ["text_generation"],
                "reputation": 80
            },
            {
                "agent_id": "0xDEADBEEF2222222222222222222222222222222222",
                "name": "TestAgent2", 
                "capabilities": ["text_generation"],
                "reputation": 85
            }
        ]
    }
    
    print(f'📋 Testing with {len(task_data["assigned_agents"])} agents')
    
    try:
        # Create and run collaboration
        collaboration_id = await collaboration_service.create_collaboration(
            task_id=task_data["task_id"],
            task_data=task_data
        )
        
        result = await collaboration_service.run_collaboration(
            collaboration_id=collaboration_id,
            task_data=task_data
        )
        
        # Check results
        result_agents = result.get("agents", [])
        assigned_agents = task_data["assigned_agents"]
        
        print(f'\n📊 Results:')
        print(f'   Assigned agents: {len(assigned_agents)}')
        print(f'   Result agents: {len(result_agents)}')
        
        # Check if all assigned agents are in result
        assigned_ids = {agent["agent_id"] for agent in assigned_agents}
        result_ids = {agent["agent_id"] for agent in result_agents}
        
        if assigned_ids == result_ids:
            print('🎉 SUCCESS: All assigned agents are preserved in result!')
            print('✅ Multi-agent collaboration fix is working correctly!')
        else:
            print('❌ ISSUE: Agent mismatch')
            print(f'   Assigned IDs: {assigned_ids}')
            print(f'   Result IDs: {result_ids}')
        
        # Check conversation for agent participation
        conversation = result.get("conversation", [])
        conversation_text = json.dumps(conversation)
        
        print(f'\n💬 Conversation analysis:')
        print(f'   Total messages: {len(conversation)}')
        
        for agent in assigned_agents:
            mentions = conversation_text.count(agent["name"])
            print(f'   {agent["name"]}: {mentions} mentions')
        
        print('\n🔍 Final Assessment:')
        if len(result_agents) == len(assigned_agents):
            print('✅ FIXED: Multi-agent participant tracking works correctly')
        else:
            print('❌ STILL BROKEN: Participant tracking has issues')
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quick_fix_verification())