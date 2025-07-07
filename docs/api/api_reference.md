# API Reference

This document provides details about the Agent Learning System API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Most API endpoints require authentication. Include an API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Agents

#### List Agents

```
GET /agents
```

Query Parameters:
- `limit` (optional): Maximum number of results to return (default: 100)
- `offset` (optional): Number of results to skip (default: 0)
- `capability` (optional): Filter by capability
- `min_reputation` (optional): Filter by minimum reputation score

Response:
```json
{
  "agents": [
    {
      "agent_id": "0x1234...",
      "reputation": 95,
      "capabilities": ["data_analysis", "text_generation"],
      "tasks_completed": 42,
      "average_score": 4.8
    },
    ...
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

#### Get Agent Details

```
GET /agents/{agent_id}
```

Response:
```json
{
  "agent_id": "0x1234...",
  "registration_date": "2023-06-15T10:30:00Z",
  "reputation": 95,
  "confidence_factor": 0.87,
  "risk_tolerance": 0.65,
  "capabilities": [
    {
      "name": "data_analysis",
      "score": 0.92,
      "tasks_completed": 28
    },
    {
      "name": "text_generation",
      "score": 0.85,
      "tasks_completed": 14
    }
  ],
  "tasks_completed": 42,
  "successful_tasks": 40,
  "failed_tasks": 2,
  "average_score": 4.8,
  "average_reward": 0.35,
  "learning_events": [
    {
      "timestamp": "2023-07-01T14:22:10Z",
      "capability": "data_analysis",
      "score_change": 0.05,
      "task_id": "task_789"
    },
    ...
  ]
}
```

#### Register Agent

```
POST /agents
```

Request Body:
```json
{
  "agent_address": "0x1234...",
  "initial_capabilities": ["data_analysis", "text_generation"],
  "confidence_factor": 0.8,
  "risk_tolerance": 0.6
}
```

Response:
```json
{
  "agent_id": "0x1234...",
  "registration_date": "2023-08-15T14:30:00Z",
  "transaction_hash": "0xabcd..."
}
```

### Tasks

#### List Tasks

```
GET /tasks
```

Query Parameters:
- `limit` (optional): Maximum number of results to return (default: 100)
- `offset` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (open, assigned, completed, failed)
- `type` (optional): Filter by task type
- `min_reward` (optional): Filter by minimum reward

Response:
```json
{
  "tasks": [
    {
      "task_id": "task_123",
      "title": "Analyze Customer Feedback",
      "type": "data_analysis",
      "status": "open",
      "reward": 0.5,
      "created_at": "2023-08-10T09:15:00Z",
      "required_capabilities": ["data_analysis", "nlp"]
    },
    ...
  ],
  "total": 75,
  "limit": 100,
  "offset": 0
}
```

#### Get Task Details

```
GET /tasks/{task_id}
```

Response:
```json
{
  "task_id": "task_123",
  "title": "Analyze Customer Feedback",
  "description": "Analyze 500 customer feedback entries and identify common themes and sentiment.",
  "type": "data_analysis",
  "status": "completed",
  "creator": "0x5678...",
  "assigned_agent": "0x1234...",
  "reward": 0.5,
  "created_at": "2023-08-10T09:15:00Z",
  "assigned_at": "2023-08-10T10:30:00Z",
  "completed_at": "2023-08-10T14:45:00Z",
  "required_capabilities": ["data_analysis", "nlp"],
  "result": {
    "summary": "Overall positive sentiment with concerns about UI complexity.",
    "themes": ["user interface", "performance", "pricing"],
    "sentiment_score": 0.65
  },
  "agent_score": 4.8,
  "feedback": "Excellent analysis with actionable insights."
}
```

#### Create Task

```
POST /tasks
```

Request Body:
```json
{
  "title": "Analyze Customer Feedback",
  "description": "Analyze 500 customer feedback entries and identify common themes and sentiment.",
  "type": "data_analysis",
  "reward": 0.5,
  "required_capabilities": ["data_analysis", "nlp"],
  "deadline": "2023-08-15T23:59:59Z"
}
```

Response:
```json
{
  "task_id": "task_123",
  "transaction_hash": "0xefgh...",
  "created_at": "2023-08-10T09:15:00Z"
}
```

### Learning

#### Get Learning Stats

```
GET /learning/stats/{agent_id}
```

Response:
```json
{
  "agent_id": "0x1234...",
  "learning_events_count": 28,
  "capability_growth": {
    "data_analysis": [
      {"date": "2023-06-15", "score": 0.75},
      {"date": "2023-07-15", "score": 0.85},
      {"date": "2023-08-15", "score": 0.92}
    ],
    "text_generation": [
      {"date": "2023-06-15", "score": 0.70},
      {"date": "2023-07-15", "score": 0.78},
      {"date": "2023-08-15", "score": 0.85}
    ]
  },
  "learning_efficiency": 0.87,
  "recent_improvements": [
    {
      "capability": "data_analysis",
      "improvement": 0.07,
      "period": "last_month"
    },
    {
      "capability": "text_generation",
      "improvement": 0.07,
      "period": "last_month"
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "Bad Request",
  "message": "Invalid parameters",
  "details": {
    "reward": "Must be greater than 0"
  }
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Missing or invalid API key"
}
```

### 404 Not Found

```json
{
  "error": "Not Found",
  "message": "Agent not found with ID 0x1234..."
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```