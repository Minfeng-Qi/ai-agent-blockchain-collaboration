# AI Agent Multi-Agent Collaboration System

🚀 A comprehensive blockchain-based AI agent learning system with real OpenAI GPT API integration for multi-agent collaboration.

## ✨ Features

### Core Capabilities
- **Real OpenAI GPT API Integration**: Multiple AI agents collaborate using actual GPT API calls
- **Decentralized Agent Performance Tracking**: Agent performance stored and managed on blockchain
- **IPFS Storage**: Conversation records and collaboration data stored on IPFS
- **Automatic Performance Evaluation**: Agents automatically updated based on collaboration performance
- **React Frontend**: Modern web interface with Material-UI for task creation and collaboration viewing

### System Architecture
- **FastAPI Backend**: Async/await patterns for high performance
- **Smart Contracts**: Ethereum-based contracts for agent registry, task management, and learning
- **Real-time Collaboration**: Multiple AI agents work together to solve tasks
- **Blockchain Incentives**: Reputation and reward system built on smart contracts

## 🏗️ Technical Stack

### Backend
- **Python**: FastAPI framework with async/await
- **OpenAI API**: Real GPT API integration for agent conversations
- **Web3.py**: Ethereum blockchain interaction
- **IPFS**: Decentralized storage for conversation data

### Frontend
- **React.js**: Modern web application framework
- **Material-UI**: Professional UI component library
- **Axios**: HTTP client for API communication

### Blockchain
- **Ethereum**: Smart contract platform
- **Ganache**: Local blockchain for development
- **Hardhat**: Development environment and testing framework

### AI Integration
- **OpenAI GPT API**: Multi-agent conversation generation
- **Performance Evaluation**: Algorithm-based agent assessment
- **Learning Loop**: Continuous improvement based on collaboration results

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd llm-blockchain-agents
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other configurations
```

3. **Install backend dependencies**
```bash
pip install -r requirements.txt
cd backend && pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend && npm install
```

5. **Start the development environment**
```bash
# Start Ganache (local blockchain)
npx ganache-cli

# Start IPFS daemon
ipfs daemon

# Start backend
python -m uvicorn backend.main:app --reload

# Start frontend
cd frontend && npm start
```

## 📖 Usage

### Creating Tasks
1. Navigate to the web interface at `http://localhost:3000`
2. Go to "Create Task" section
3. Fill in task details including title, description, and requirements
4. Submit the task to initiate agent collaboration

### Viewing Collaborations
1. Go to "Task Collaboration" section
2. Select a task to view agent collaboration
3. Watch real-time GPT API conversations between agents
4. View agent performance updates and blockchain records

### System Monitoring
1. Check "Dashboard" for system statistics
2. View "Blockchain Explorer" for transaction history
3. Monitor agent performance in "Agent Management"

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for GPT integration
- `OPENAI_DEFAULT_MODEL`: Default GPT model (default: gpt-3.5-turbo)
- `AGENT_MOCK_MODE`: Set to False for real API calls
- `BLOCKCHAIN_URL`: Ethereum node URL (default: http://localhost:8545)
- `IPFS_URL`: IPFS node URL (default: http://localhost:5001)

### Smart Contracts
The system includes several smart contracts:
- **AgentRegistry**: Manages agent registration and metadata
- **TaskManager**: Handles task creation and lifecycle
- **Learning**: Implements learning algorithms and performance tracking
- **IncentiveEngine**: Manages rewards and reputation

## 🧪 Testing

### Backend Tests
```bash
cd backend && python -m pytest tests/
```

### Smart Contract Tests
```bash
cd contracts-clean && npm test
```

### Integration Tests
```bash
python test_integration.py
```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── services/           # Business logic
│   ├── routers/            # API endpoints
│   └── models/             # Data models
├── frontend/               # React frontend
│   ├── src/components/     # UI components
│   └── src/services/       # API clients
├── contracts-clean/        # Smart contracts
│   ├── core/              # Contract files
│   └── test/              # Contract tests
├── agents/                 # Agent implementations
└── docs/                  # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- Ethereum and the Web3 ecosystem
- React and Material-UI communities
- IPFS for decentralized storage

## 📞 Support

For questions and support, please open an issue in the GitHub repository.

---

**Built with ❤️ for the decentralized AI future**