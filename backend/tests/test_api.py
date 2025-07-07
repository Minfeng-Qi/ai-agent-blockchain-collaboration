"""
API integration tests for the Agent Learning System.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint returns correct status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "services" in data
    assert "api" in data["services"]
    assert "blockchain" in data["services"]

def test_get_agents():
    """Test retrieving the list of agents."""
    response = client.get("/agents/")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert isinstance(data["agents"], list)
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

def test_create_agent():
    """Test creating a new agent."""
    agent_data = {
        "name": "TestAgent",
        "description": "A test agent for API testing",
        "capabilities": ["data_analysis", "text_generation"],
        "confidence_factor": 0.85,
        "risk_tolerance": 0.6
    }
    response = client.post("/agents/", json=agent_data)
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "transaction_hash" in data
    assert "registration_date" in data

def test_get_tasks():
    """Test retrieving the list of tasks."""
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

def test_create_task():
    """Test creating a new task."""
    task_data = {
        "title": "Test Task",
        "description": "A test task for API testing",
        "reward": 0.5,
        "required_capabilities": ["data_analysis"],
        "deadline": "2023-09-15T00:00:00Z",
        "complexity": "medium"
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "transaction_hash" in data
    assert "created_at" in data

def test_get_learning_events():
    """Test retrieving learning events."""
    response = client.get("/learning/")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert isinstance(data["events"], list)
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

def test_create_learning_event():
    """Test creating a new learning event."""
    event_data = {
        "agent_id": "0x1234567890123456789012345678901234567890",
        "event_type": "task_completion",
        "data": {
            "task_id": "task_123",
            "performance_score": 4.8,
            "insights_gained": ["market trend analysis improved"]
        }
    }
    response = client.post("/learning/", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert "event_id" in data
    assert "transaction_hash" in data
    assert "timestamp" in data

def test_get_agent_by_id():
    """Test retrieving a specific agent by ID."""
    # First, create an agent
    agent_data = {
        "name": "SpecificAgent",
        "description": "A specific agent for testing",
        "capabilities": ["data_analysis"],
        "confidence_factor": 0.8,
        "risk_tolerance": 0.5
    }
    create_response = client.post("/agents/", json=agent_data)
    agent_id = create_response.json()["agent_id"]
    
    # Then, retrieve the agent
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert data["agent_id"] == agent_id
    assert "name" in data
    assert "capabilities" in data
    assert isinstance(data["capabilities"], list)

def test_get_task_by_id():
    """Test retrieving a specific task by ID."""
    # First, create a task
    task_data = {
        "title": "Specific Task",
        "description": "A specific task for testing",
        "reward": 0.7,
        "required_capabilities": ["text_generation"],
        "deadline": "2023-09-20T00:00:00Z",
        "complexity": "high"
    }
    create_response = client.post("/tasks/", json=task_data)
    task_id = create_response.json()["task_id"]
    
    # Then, retrieve the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["task_id"] == task_id
    assert "title" in data
    assert "status" in data
    assert "reward" in data

def test_assign_task():
    """Test assigning a task to an agent."""
    # Create an agent
    agent_data = {
        "name": "AssignmentAgent",
        "description": "An agent for task assignment testing",
        "capabilities": ["data_analysis"],
        "confidence_factor": 0.9,
        "risk_tolerance": 0.4
    }
    agent_response = client.post("/agents/", json=agent_data)
    agent_id = agent_response.json()["agent_id"]
    
    # Create a task
    task_data = {
        "title": "Assignment Task",
        "description": "A task for assignment testing",
        "reward": 0.6,
        "required_capabilities": ["data_analysis"],
        "deadline": "2023-09-18T00:00:00Z",
        "complexity": "medium"
    }
    task_response = client.post("/tasks/", json=task_data)
    task_id = task_response.json()["task_id"]
    
    # Assign the task
    assignment_data = {
        "agent_id": agent_id
    }
    response = client.post(f"/tasks/{task_id}/assign", json=assignment_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "agent_id" in data
    assert data["task_id"] == task_id
    assert data["agent_id"] == agent_id
    assert "transaction_hash" in data
    
    # Verify the task is assigned
    task_response = client.get(f"/tasks/{task_id}")
    task_data = task_response.json()
    assert task_data["status"] == "assigned"
    assert "assigned_agent" in task_data
    assert task_data["assigned_agent"] == agent_id

def test_complete_task():
    """Test marking a task as completed."""
    # Create an agent
    agent_data = {
        "name": "CompletionAgent",
        "description": "An agent for task completion testing",
        "capabilities": ["data_analysis"],
        "confidence_factor": 0.85,
        "risk_tolerance": 0.5
    }
    agent_response = client.post("/agents/", json=agent_data)
    agent_id = agent_response.json()["agent_id"]
    
    # Create a task
    task_data = {
        "title": "Completion Task",
        "description": "A task for completion testing",
        "reward": 0.8,
        "required_capabilities": ["data_analysis"],
        "deadline": "2023-09-19T00:00:00Z",
        "complexity": "medium"
    }
    task_response = client.post("/tasks/", json=task_data)
    task_id = task_response.json()["task_id"]
    
    # Assign the task
    assignment_data = {
        "agent_id": agent_id
    }
    client.post(f"/tasks/{task_id}/assign", json=assignment_data)
    
    # Complete the task
    completion_data = {
        "status": "completed",
        "result": "Task completed successfully with all requirements met."
    }
    response = client.post(f"/tasks/{task_id}/complete", json=completion_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["task_id"] == task_id
    assert "status" in data
    assert data["status"] == "completed"
    assert "transaction_hash" in data
    
    # Verify the task is completed
    task_response = client.get(f"/tasks/{task_id}")
    task_data = task_response.json()
    assert task_data["status"] == "completed"