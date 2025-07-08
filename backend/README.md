# Agent Learning System Backend API

A FastAPI-based backend for interacting with blockchain smart contracts and managing agent learning systems.

## Features

- **Smart Contract Integration**: Connect and interact with blockchain smart contracts
- **Agent Management**: Register, update, and query agent information
- **Task Management**: Create, assign, and track tasks
- **Learning Integration**: Connect with reinforcement learning models for agent capability improvement
- **RESTful API**: Well-documented endpoints with Swagger UI
- **Blockchain Explorer**: Real-time blockchain data visualization and transaction monitoring
- **Agent Lifecycle Management**: Complete agent activation/deactivation workflow with reactivation support

## API Endpoints

### Agent Endpoints

- `GET /agents`: List all registered agents (only shows active agents)
- `GET /agents/{agent_id}`: Get details for a specific agent
- `POST /agents`: Register a new agent (automatically reactivates if previously deactivated)
- `DELETE /agents/{agent_id}`: Deactivate an agent
- `GET /agents/{agent_id}/capabilities`: Get agent capabilities
- `PUT /agents/{agent_id}/capabilities`: Update agent capabilities
- `GET /agents/capabilities`: Get capability distribution across all agents

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

### Blockchain Endpoints

- `GET /blockchain/stats`: Get blockchain statistics (transaction count, block count, etc.)
- `GET /blockchain/transactions`: List blockchain transactions with pagination
- `GET /blockchain/transactions/{tx_hash}`: Get specific transaction details
- `GET /blockchain/blocks`: List blockchain blocks with pagination
- `GET /blockchain/blocks/{block_number}`: Get specific block details
- `GET /blockchain/events`: List smart contract events

### Analytics Endpoints

- `GET /analytics/agent-performance`: Agent performance analytics
- `GET /analytics/task-completion`: Task completion statistics
- `GET /analytics/system-health`: System health metrics

## Setup

### Prerequisites

- Python 3.8+
- Ganache (local Ethereum development network)
- Node.js and npm (for frontend development)
- Smart contracts deployed to Ganache

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Ganache on port 8545

3. Deploy smart contracts to Ganache (contract addresses are configured in `services/contract_service.py`)

4. Start the backend API server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

5. Start the frontend (in a separate terminal):
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

6. Access the API documentation at `http://localhost:8001/docs`
7. Access the frontend application at `http://localhost:3000`

## Development

### Project Structure

```
backend/
├── main.py                     # FastAPI application entry point
├── routers/              
│   ├── agents.py              # Agent management endpoints
│   ├── tasks.py               # Task management endpoints
│   ├── learning.py            # Learning integration endpoints
│   ├── blockchain.py          # Blockchain explorer endpoints
│   └── analytics.py           # Analytics endpoints
├── services/
│   └── contract_service.py    # Smart contract interaction service
├── contracts/
│   └── abi/                   # Smart contract ABI files
│       ├── AgentRegistry.json
│       ├── TaskManager.json
│       ├── Learning.json
│       └── ...
├── tests/                     # Test files
└── README.md
```

### Recent Updates (2025-01-08)

#### Fixed Transaction Count Statistics
- **Issue**: Frontend displayed 0 total transactions
- **Solution**: Fixed `get_blockchain_stats()` in `contract_service.py` to properly calculate transaction count across all blocks
- **Files Modified**: `services/contract_service.py:get_blockchain_stats()`

#### Enhanced Blocks Display
- **Issue**: Blocks table only showed latest 10 items without pagination
- **Solution**: Increased backend limit to 100 blocks, added frontend pagination support
- **Files Modified**: `frontend/src/components/BlockchainExplorer.js`, `routers/blockchain.py`

#### Optimized Page Refresh Frequency
- **Issue**: Page refreshed every 30 seconds causing poor user experience
- **Solution**: Changed refresh interval to 2 minutes (120 seconds)
- **Files Modified**: `frontend/src/components/BlockchainExplorer.js`

#### Removed Mock Data Dependencies
- **Issue**: Backend was showing mock data instead of real blockchain data
- **Solution**: Removed all mock data fallbacks from get_agents and create_agent endpoints
- **Files Modified**: `routers/agents.py`

#### Fixed Agent Lifecycle Management
- **Issue**: Frontend displayed inactive agents and delete functionality was broken
- **Solution**: 
  - Modified `get_all_agents()` to filter only active agents
  - Fixed delete functionality to handle "Agent already inactive" cases
  - Added proper error handling for deactivation operations
- **Files Modified**: `services/contract_service.py`, `routers/agents.py`

#### Implemented Agent Reactivation System
- **Issue**: Previously deleted agents couldn't be "re-registered"
- **Solution**: 
  - Added `activate_agent()` function in contract service
  - Modified registration logic to attempt reactivation if agent already exists
  - Updated frontend to handle reactivation responses correctly
- **Files Modified**: `services/contract_service.py`, `routers/agents.py`, `frontend/src/components/CreateAgent.js`

#### Fixed Checksum Address Handling
- **Issue**: Web3.py rejecting lowercase addresses
- **Solution**: Added `Web3.to_checksum_address()` conversion throughout the system
- **Files Modified**: `services/contract_service.py`

### Smart Contract Integration

The system integrates with the following smart contracts deployed on Ganache:
- **AgentRegistry** (`0x112F8B6eB083DdC54Fb6296429A57999DF659479`): Agent registration and lifecycle management
- **ActionLogger** (`0x43921546C94D6EdbCe902B4A31238a6d7dC8F692`): Action logging and tracking
- **IncentiveEngine** (`0xdb6F5A1a66Df1094766A99AdA41F5c32e6d6977b`): Incentive management
- **TaskManager** (`0x6531649183f46885B375a1Ce5289edd719d506B5`): Task assignment and completion
- **BidAuction** (`0x081BD1D43c7019A360aEe32781E6Cc608E7C0bD7`): Auction mechanisms
- **MessageHub** (`0xf68f033E3B42D41696016399Cd6D06e3513D2c39`): Inter-agent communication
- **Learning** (`0x2787255B022C2AB332dC58ebA3d95FE2bD83ab84`): Learning event tracking

### Key Features Implemented

1. **Real-time Blockchain Data**: Live transaction and block monitoring with proper statistics
2. **Agent Lifecycle Management**: Complete activate/deactivate/reactivate workflow
3. **Dynamic Address Management**: Automatic Ganache address selection and reuse
4. **Pagination Support**: Efficient data loading for large datasets
5. **Error Handling**: Comprehensive error handling for blockchain operations
6. **Frontend Integration**: Seamless integration between React frontend and FastAPI backend

## Testing

The system has been tested with:
- Agent registration and reactivation workflows
- Transaction and block data retrieval
- Real-time frontend updates
- Error handling for various edge cases

## License

This project is licensed under the MIT License. 