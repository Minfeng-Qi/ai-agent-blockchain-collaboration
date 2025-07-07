# Agent Learning System Backend API

A FastAPI-based backend for interacting with blockchain smart contracts and managing agent learning systems.

## Features

- **Smart Contract Integration**: Connect and interact with blockchain smart contracts
- **Agent Management**: Register, update, and query agent information
- **Task Management**: Create, assign, and track tasks
- **Learning Integration**: Connect with reinforcement learning models for agent capability improvement
- **RESTful API**: Well-documented endpoints with Swagger UI

## API Endpoints

### Agent Endpoints

- `GET /agents`: List all registered agents
- `GET /agents/{agent_id}`: Get details for a specific agent
- `POST /agents`: Register a new agent
- `PUT /agents/{agent_id}`: Update agent information
- `GET /agents/{agent_id}/capabilities`: Get agent capabilities
- `PUT /agents/{agent_id}/capabilities`: Update agent capabilities

### Task Endpoints

- `GET /tasks`: List all tasks
- `GET /tasks/available`: List available tasks
- `GET /tasks/assigned`: List assigned tasks
- `GET /tasks/{task_id}`: Get details for a specific task
- `POST /tasks`: Create a new task
- `PUT /tasks/{task_id}/assign`: Assign a task to an agent
- `PUT /tasks/{task_id}/complete`: Mark a task as completed
- `GET /task_stats`: Get task statistics

### Learning Endpoints

- `GET /learning/{agent_id}`: Get learning metrics for an agent
- `POST /learning/{agent_id}/update`: Update agent learning model
- `GET /learning/{agent_id}/report`: Generate learning report for an agent

## Setup

### Prerequisites

- Python 3.8+
- Access to an Ethereum node (local or remote)
- Smart contracts deployed to the blockchain

### Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   cp .env.example .env
   ```
   
   Edit `.env` to include:
   ```
   WEB3_PROVIDER_URI=http://localhost:8545
   PRIVATE_KEY=your_private_key
   CONTRACT_REGISTRY_ADDRESS=0x...
   ```

3. Start the API server:
   ```
   uvicorn app.main:app --reload
   ```

4. Access the API documentation at `http://localhost:8000/docs`

## Development

### Project Structure

```
app/
├── __init__.py
├── main.py                # FastAPI application entry point
├── routers/              
│   ├── agents.py          # Agent endpoints
│   ├── tasks.py           # Task endpoints
│   └── learning.py        # Learning endpoints
├── services/
│   ├── blockchain.py      # Blockchain connection service
│   ├── agent_service.py   # Agent business logic
│   └── learning_service.py # Learning integration
├── models/
│   ├── agent.py           # Agent data models
│   └── task.py            # Task data models
└── config.py              # Application configuration
```

### Adding New Endpoints

To add new endpoints:

1. Create or modify a router in the `app/routers/` directory
2. Implement business logic in the `app/services/` directory
3. Define data models in the `app/models/` directory
4. Register the router in `app/main.py`

## Testing

Run the API tests:

```
pytest app/tests/
```

## License

This project is licensed under the MIT License. 