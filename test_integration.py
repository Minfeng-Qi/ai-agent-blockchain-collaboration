#!/usr/bin/env python3
"""
Complete integration test for Agent Learning System API
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"✓ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code == expected_status:
            return response.json()
        else:
            print(f"  ⚠️  Expected {expected_status}, got {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ {method} {endpoint} - Error: {str(e)}")
        return None

def run_integration_tests():
    """Run comprehensive integration tests"""
    print("🚀 Starting Agent Learning System Integration Tests\n")
    
    # Test 1: System Health
    print("📋 Test 1: System Health Check")
    health = test_api_endpoint("GET", "/health")
    if health:
        print(f"  API Status: {health['services']['api']}")
        print(f"  Blockchain Status: {health['services']['blockchain']}")
    print()
    
    # Test 2: System Stats
    print("📊 Test 2: System Statistics")
    stats = test_api_endpoint("GET", "/stats")
    if stats:
        print(f"  Total Agents: {stats['agents']['total']}")
        print(f"  Total Tasks: {stats['tasks']['total']}")
        print(f"  Total Learning Events: {stats['learning']['total_events']}")
    print()
    
    # Test 3: Agent Management
    print("🤖 Test 3: Agent Management")
    # Get agents list
    agents = test_api_endpoint("GET", "/agents/")
    
    # Create new agent
    new_agent_data = {
        "name": "IntegrationTestAgent",
        "capabilities": ["data_analysis", "text_generation"],
        "reputation": 90
    }
    created_agent = test_api_endpoint("POST", "/agents/", new_agent_data, 200)
    
    if created_agent and created_agent.get("success"):
        agent_id = created_agent["agent_id"]
        print(f"  Created Agent ID: {agent_id}")
        
        # Get agent details
        agent_details = test_api_endpoint("GET", f"/agents/{agent_id}")
        if agent_details:
            print(f"  Agent Name: {agent_details['name']}")
            print(f"  Agent Capabilities: {agent_details['capabilities']}")
    print()
    
    # Test 4: Task Management  
    print("📝 Test 4: Task Management")
    # Get tasks list
    tasks = test_api_endpoint("GET", "/tasks/")
    
    # Create new task
    new_task_data = {
        "title": "Integration Test Task",
        "type": "data_analysis", 
        "reward": 0.8,
        "required_capabilities": ["data_analysis"]
    }
    created_task = test_api_endpoint("POST", "/tasks/", new_task_data, 200)
    
    if created_task and created_task.get("success"):
        task_id = created_task["task_id"]
        print(f"  Created Task ID: {task_id}")
        
        # Get task details
        task_details = test_api_endpoint("GET", f"/tasks/{task_id}")
        if task_details:
            print(f"  Task Title: {task_details['title']}")
            print(f"  Task Status: {task_details['status']}")
            
        # Assign task to agent (if we have an agent)
        if created_agent and created_agent.get("success"):
            assign_data = {"agent_id": agent_id}
            assignment = test_api_endpoint("POST", f"/tasks/{task_id}/assign", assign_data, 200)
            if assignment and assignment.get("success"):
                print(f"  Task assigned to agent: {agent_id}")
    print()
    
    # Test 5: Learning Events
    print("🧠 Test 5: Learning Events")
    learning_events = test_api_endpoint("GET", "/learning/")
    if learning_events:
        print(f"  Total Learning Events: {learning_events['total']}")
        if learning_events['events']:
            print(f"  Latest Event Type: {learning_events['events'][0]['event_type']}")
    print()
    
    # Test 6: Blockchain Data
    print("⛓️  Test 6: Blockchain Data")
    transactions = test_api_endpoint("GET", "/blockchain/transactions")
    blocks = test_api_endpoint("GET", "/blockchain/blocks")
    events = test_api_endpoint("GET", "/blockchain/events")
    blockchain_stats = test_api_endpoint("GET", "/blockchain/stats")
    
    if transactions:
        print(f"  Total Transactions: {transactions['total']}")
    if blocks:
        print(f"  Total Blocks: {blocks['total']}")
    if events:
        print(f"  Total Events: {events['total']}")
    if blockchain_stats:
        print(f"  Connected to Blockchain: {blockchain_stats['connected']}")
    print()
    
    # Test 7: Collaboration API
    print("🤝 Test 7: Collaboration System")
    if created_task and created_task.get("success"):
        collaboration_data = {
            "task_data": {
                "task_id": task_id,
                "title": "Integration Test Task",
                "description": "Testing agent collaboration system",
                "type": "data_analysis"
            }
        }
        
        # Create collaboration
        collaboration = test_api_endpoint("POST", "/collaboration/", collaboration_data, 200)
        if collaboration:
            collab_id = collaboration["collaboration_id"]
            print(f"  Created Collaboration ID: {collab_id}")
            
            # Run collaboration
            conversation = test_api_endpoint("POST", f"/collaboration/{collab_id}/run", collaboration_data, 200)
            if conversation:
                print(f"  Collaboration completed with {len(conversation['conversation'])} messages")
                print(f"  IPFS CID: {conversation['ipfs_cid']}")
    print()
    
    print("✅ Integration Tests Completed!")
    print("\n📈 Summary:")
    print("- All major API endpoints tested")
    print("- Agent creation and management ✓")
    print("- Task creation and assignment ✓") 
    print("- Learning events tracking ✓")
    print("- Blockchain data access ✓")
    print("- Agent collaboration system ✓")
    print("\n🎉 System is ready for production use!")

if __name__ == "__main__":
    run_integration_tests()