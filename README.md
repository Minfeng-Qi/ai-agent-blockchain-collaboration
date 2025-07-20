# LLM Blockchain Agent Learning System

A blockchain-based AI agent task management and learning system that supports agent registration, task allocation, collaborative learning, and incentive mechanisms.

## 🚀 Quick Start

### System Requirements
- **Node.js**: 18.x or higher
- **Python**: 3.8 or higher  
- **IPFS**: Kubo 0.35.0 or higher
- **Git**: 2.x or higher

For detailed installation guide, see: [System Requirements](SYSTEM_REQUIREMENTS.md)

### One-Click Launch
```bash
./quick_start.sh
```

### Manual Setup
See [Startup Guide](STARTUP_GUIDE.md) for detailed instructions

## 📋 System Components

- **Frontend** (React): http://localhost:3000
- **Backend** (FastAPI): http://localhost:8001
- **Blockchain** (Ganache): http://localhost:8545
- **IPFS Node**: http://localhost:5001
- **IPFS Gateway**: http://localhost:8080
- **Smart Contracts**: 7 deployed contracts

## 🏗️ Project Structure

```
llm-blockchain/
├── frontend/          # React frontend application
├── backend/           # FastAPI backend services
├── contracts-clean/   # Smart contract source code
├── artifacts-clean/   # Compiled contract ABIs
├── scripts/           # Automation scripts
├── quick_start.sh     # Quick start script
└── STARTUP_GUIDE.md   # Detailed startup guide
```

## 🔧 Core Features

### Smart Contracts
- **AgentRegistry**: Agent registration and management
- **TaskManager**: Task creation and assignment
- **Learning**: Learning event recording
- **IncentiveEngine**: Reward and incentive mechanisms
- **BidAuction**: Bidding and auction system
- **MessageHub**: Inter-agent communication
- **ActionLogger**: Behavior and action logging

### Frontend Interface
- 📊 Real-time data dashboard
- 🔍 Blockchain explorer
- 👥 Agent management
- 📝 Task management
- 📈 Learning visualization
- 💬 Multi-agent collaboration viewer

### Backend API
- RESTful API endpoints
- Blockchain data integration
- Smart contract interactions
- Real-time data retrieval
- IPFS distributed storage

### Storage Systems
- **IPFS**: Distributed storage for collaboration results
- **Blockchain**: Task states and transaction records
- **Local Database**: Collaboration history and caching

## 🤖 Multi-Agent Collaboration

### Key Features
- **Multi-Agent Task Assignment**: Tasks can be assigned to multiple agents for collaborative work
- **Independent LLM API Calls**: Each agent makes independent calls to language models (OpenAI/DeepSeek)
- **Phase-Based Collaboration**: 
  - Phase 1: Initial contributions from all agents
  - Phase 2: Collaborative refinement and integration
- **Real-time Conversation Tracking**: Complete conversation history between agents
- **Agent Performance Analytics**: Detailed metrics on agent participation and success rates

### Collaboration Workflow
1. **Task Creation**: Multi-agent tasks are created with specific capability requirements
2. **Agent Selection**: System selects best-suited agents based on capabilities and reputation
3. **Collaborative Execution**: 
   - All assigned agents participate with independent LLM calls
   - Conversation state tracks each agent's contributions
   - Agents build upon each other's work in refinement phases
4. **Result Integration**: Final results include all agent contributions and conversation history
5. **Learning Events**: All participating agents receive learning events and reputation updates

### Technical Implementation
- **Fixed Multi-Agent Priority Logic**: Ensures multi-agent tasks are correctly identified and processed
- **Collaboration State Preservation**: Prevents loss of agent participation data during execution
- **IPFS Storage**: Complete conversation history stored in distributed system
- **Frontend Visualization**: Rich UI for viewing multi-agent conversations and results

## 🛠️ Development

### Start Development Environment
```bash
# Start blockchain and backend
echo "3" | ./quick_start.sh

# Start frontend development server
cd frontend && npm start
```

### API Documentation
Visit http://localhost:8001/docs for complete API documentation

### Testing Multi-Agent Features
```bash
# Run multi-agent collaboration tests
cd backend
python tests/test_multi_agent_collaboration.py

# Test complete workflow
python tests/test_complete_workflow.py

# Verify agent learning events
python check_agent_learning.py
```

## 📊 Monitoring & Analytics

### Real-time Monitoring
- **Blockchain Status**: Ganache console
- **Backend Logs**: `tail -f backend.log`
- **IPFS Logs**: `tail -f ipfs.log`
- **Frontend**: Browser developer tools
- **IPFS Status**: http://localhost:5001/webui

### Learning Dashboard
- Agent performance metrics
- Task completion statistics
- Learning event timeline
- Reputation history tracking
- Collaboration success rates

### Conversation Analytics
- Multi-agent conversation flows
- Agent contribution analysis
- Task result visualization
- IPFS storage statistics

## 📦 Deployment

### Contract Deployment
```bash
./scripts/auto_deploy.py
```

### Service Management
```bash
./scripts/start_system.sh  # Start all services
./scripts/stop_system.sh   # Stop all services
```

### Production Configuration
- Configure environment variables in `.env` files
- Set up proper IPFS node clustering
- Configure blockchain network parameters
- Set up monitoring and logging

## 🔧 Recent Updates

### Multi-Agent Collaboration Fixes (Latest)
- **Fixed Agent Priority Logic**: Multi-agent tasks now correctly prioritize `assigned_agents` over `assigned_agent`
- **Enhanced Collaboration State**: Prevents loss of agent participation data during task execution
- **Improved IPFS Storage**: All participating agents properly stored in conversation records
- **Better Frontend Display**: Complete multi-agent conversation history in result viewer

### Learning System Improvements
- **Task History Deduplication**: Fixed duplicate evaluation events in task history
- **Learning Event Attribution**: Proper task_id association for all learning events
- **Agent Statistics**: Accurate tracking of agent participation and performance
- **Real-time Updates**: Improved synchronization between blockchain and local database

### UI/UX Enhancements
- **Null Safety**: Fixed JavaScript runtime errors in dashboard components
- **Data Visualization**: Enhanced charts and graphs for learning analytics
- **Agent Details**: Comprehensive learning event display in agent profiles
- **Task Results**: Rich conversation viewer for multi-agent collaborations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation for API changes
- Test multi-agent scenarios thoroughly

## 📄 License

MIT License

## 🔗 Links

- [System Requirements](SYSTEM_REQUIREMENTS.md)
- [Startup Guide](STARTUP_GUIDE.md)
- [API Documentation](http://localhost:8001/docs)
- [IPFS Web UI](http://localhost:5001/webui)

## 📞 Support

For issues and questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include system information and error logs
4. Test with provided examples before reporting

---

**Note**: This system demonstrates advanced blockchain-based AI agent collaboration with real LLM integration. All multi-agent features have been thoroughly tested and validated.