# Agent Learning System - Project Structure

This document outlines the reorganized structure of the Agent Learning System project.

## Directory Structure

```
llm-blockchain/code/
├── agents/                  # Agent implementation
│   ├── core/                # Core agent functionality
│   │   ├── agent.py
│   │   └── agent_config.py
│   ├── ai/                  # AI and learning components
│   │   ├── agent_learning.py
│   │   └── openai_integration.py
│   ├── learning/            # Learning algorithms
│   │   ├── adaptive_bidding_strategy.py
│   │   ├── learning_integration.py
│   │   └── reinforcement_learning.py
│   ├── abis/                # Contract ABI files
│   ├── tests/               # Agent tests
│   ├── agent_service.py     # Main agent service entry point
│   ├── run_agents.py        # Agent runner script
│   ├── requirements.txt     # Agent dependencies
│   ├── setup_agents.sh      # Agent setup script
│   └── Dockerfile           # Agent service container
│
├── app/                     # Legacy backend (being phased out)
│   ├── models/              # Data models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   ├── tests/               # Backend tests
│   ├── main.py              # Main API entry point
│   ├── config.py            # Configuration
│   └── requirements.txt     # Backend dependencies
│
├── backend/                 # Main backend API service
│   ├── models/              # Data models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   │   ├── agent_collaboration_service.py
│   │   ├── contract_service.py
│   │   ├── ipfs_service.py
│   │   └── learning_service.py
│   ├── contracts/           # Contract integration
│   │   └── abi/             # Contract ABI files
│   ├── scripts/             # Deployment and utility scripts
│   ├── tests/               # Backend tests
│   ├── main.py              # Main API entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Backend dependencies
│   └── Dockerfile           # Backend container
│
├── contracts-clean/         # Smart contracts (current)
│   ├── core/                # Core contracts
│   │   ├── AgentRegistry.sol
│   │   ├── TaskManager.sol
│   │   ├── TaskMarketplace.sol
│   │   ├── BidAuction.sol
│   │   ├── IncentiveEngine.sol
│   │   ├── MessageHub.sol
│   │   ├── ActionLogger.sol
│   │   └── Learning.sol
│   ├── test/                # Contract tests
│   ├── scripts/             # Deployment scripts
│   ├── mocks/               # Mock contracts for testing
│   ├── hardhat.config.js    # Hardhat configuration
│   ├── package.json         # Contract dependencies
│   └── README.md            # Contracts documentation
│
├── artifacts-clean/         # Compiled contract artifacts
├── cache-clean/             # Build cache
│
├── frontend/                # React frontend
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   │   ├── components/      # React components
│   │   └── services/        # API services
│   ├── build/               # Production build
│   ├── package.json         # Frontend dependencies
│   ├── Dockerfile           # Frontend container
│   └── README.md            # Frontend documentation
│
├── docs/                    # Project documentation
│   ├── architecture/        # Architecture documentation
│   ├── api/                 # API documentation
│   ├── tutorials/           # User tutorials
│   ├── deployment/          # Deployment guides
│   └── README.md            # Documentation index
│
├── utils/                   # Utility modules
│   ├── capability_extractor.py
│   ├── ipfs_client.py
│   └── signature.py
│
├── simulations/             # Simulation scripts
│   └── run_simulation.py
│
├── backup/                  # Backup files
├── test_venv/               # Test virtual environment
├── venv/                    # Python virtual environment
│
├── setup_dev_env.sh         # Development environment setup script
├── setup-node.sh            # Node.js setup script
├── start_dev.sh             # Development environment start script
├── start_frontend.sh        # Frontend start script
├── run_backend.py           # Backend runner script
├── comprehensive_e2e_test.py # End-to-end test script
├── test_backend_simple.py   # Simple backend test
├── package.json             # Root project dependencies
├── requirements.txt         # Root Python dependencies
├── ipfs.log                 # IPFS daemon log file
├── ganache.log              # Ganache blockchain log file
├── E2E_TEST_REPORT.md       # Test report
├── RUNNING.md               # Runtime instructions
└── PROJECT_STRUCTURE.md     # This file
```

## Key Changes Made

1. **Consolidated Backend**:
   - Combined `app` and `backend` directories into a single `backend` directory
   - Organized into models, routers, services, and tests

2. **Structured Agents**:
   - Created subdirectories for core functionality, AI components, and tests
   - Added proper Python package structure with `__init__.py` files
   - Implemented agent service as main entry point

3. **Organized Contracts**:
   - Separated core contracts, tests, and deployment scripts
   - Added documentation for smart contracts

4. **Enhanced Documentation**:
   - Created comprehensive documentation structure
   - Added architecture diagrams, API reference, tutorials, and deployment guides

5. **Added DevOps Configuration**:
   - Created Dockerfiles for each service
   - Added docker-compose.yml for easy deployment
   - Included .gitignore for version control

6. **Frontend Structure**:
   - Maintained existing frontend structure
   - Added Docker configuration for containerization

7. **IPFS Integration**:
   - Added IPFS directory for distributed storage configuration
   - Integrated IPFS setup and management scripts
   - Added IPFS daemon logging and monitoring

8. **Development Scripts**:
   - Added automated setup scripts for development environment
   - Created unified start script with IPFS integration
   - Added Node.js version management script

## Technology Stack

### Core Technologies
- **Frontend**: React.js with Node.js 18.x
- **Backend**: Python FastAPI with uvicorn
- **Blockchain**: Ethereum with Hardhat and Ganache
- **Storage**: IPFS for distributed file storage
- **Containerization**: Docker and Docker Compose

### Development Tools
- **Package Management**: npm (frontend), pip (backend)
- **Testing**: Hardhat (contracts), pytest (backend), Jest (frontend)
- **Development Environment**: Python virtual environment, nvm for Node.js

## IPFS Integration

The system uses IPFS (InterPlanetary File System) for distributed storage:

- **Version**: 0.35.0+ (automatically managed)
- **Web UI**: Available at http://127.0.0.1:5001/webui
- **API Endpoint**: http://127.0.0.1:5001
- **Gateway**: http://127.0.0.1:8081
- **Configuration**: Stored in `~/.ipfs/`

## Next Steps

1. **Testing**: Ensure all tests are updated to work with the new structure
2. **CI/CD**: Set up continuous integration and deployment
3. **Documentation**: Continue expanding documentation with more detailed guides
4. **Dependency Management**: Review and update dependencies in each component
5. **IPFS Storage**: Implement agent data storage and retrieval via IPFS
6. **Monitoring**: Add health checks and monitoring for all services