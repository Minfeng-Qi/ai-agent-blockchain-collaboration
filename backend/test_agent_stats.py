#!/usr/bin/env python3
"""
测试agent统计信息更新的脚本
"""
import requests
import json

def test_agent_statistics():
    """测试agent统计信息"""
    
    base_url = "http://localhost:8001"
    
    # 获取一个测试agent的ID
    test_agent_id = "0x00d2c630b8Bb8EEC21e5C11B1b91dfBBc2C4a3D5"
    
    print(f"🔍 Checking statistics for agent: {test_agent_id}")
    
    try:
        # 获取agent信息
        agent_response = requests.get(f"{base_url}/agents/{test_agent_id}")
        if agent_response.status_code == 200:
            agent_data = agent_response.json()
            print(f"📊 Current agent statistics:")
            print(f"   Reputation: {agent_data.get('reputation', 'N/A')}")
            print(f"   Tasks completed: {agent_data.get('tasks_completed', 'N/A')}")
            print(f"   Average score: {agent_data.get('average_score', 'N/A')}")
            print(f"   Capabilities: {agent_data.get('capabilities', [])}")
        else:
            print(f"❌ Failed to get agent info: {agent_response.status_code}")
            
        # 获取agent学习历史
        learning_response = requests.get(f"{base_url}/agents/{test_agent_id}/learning")
        if learning_response.status_code == 200:
            learning_data = learning_response.json()
            events = learning_data.get('events', [])
            print(f"\n📚 Learning events: {len(events)} events")
            
            # 显示最近的几个学习事件
            for i, event in enumerate(events[:3]):
                print(f"   Event {i+1}:")
                print(f"     Type: {event.get('event_type', 'N/A')}")
                print(f"     Timestamp: {event.get('timestamp', 'N/A')}")
                print(f"     Transaction: {event.get('transaction_hash', 'N/A')}")
                if event.get('data'):
                    data = event['data']
                    print(f"     Success: {data.get('success', 'N/A')}")
                    print(f"     Rating: {data.get('rating', 'N/A')}")
                    print(f"     Reputation change: {data.get('reputation_change', 'N/A')}")
        else:
            print(f"❌ Failed to get learning events: {learning_response.status_code}")
            
        # 检查区块链事件
        events_response = requests.get(f"{base_url}/blockchain/events", params={"event_type": "LearningEventRecorded"})
        if events_response.status_code == 200:
            events_data = events_response.json()
            print(f"\n🔗 Blockchain learning events: {len(events_data.get('events', []))} total")
            
            # 查找这个agent的事件
            agent_events = [e for e in events_data.get('events', []) if e.get('data', {}).get('agentAddress') == test_agent_id]
            print(f"   Agent-specific events: {len(agent_events)}")
            
        else:
            print(f"❌ Failed to get blockchain events: {events_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing agent statistics and learning events...")
    test_agent_statistics()
    print("✅ Test completed!")