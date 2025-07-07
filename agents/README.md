# LLM Multi-Agent System Backend

This directory contains the backend agent implementation for the blockchain-based LLM multi-agent coordination system. The agents use OpenAI's GPT models to evaluate tasks, calculate bids, execute tasks, and evaluate results.

## System Overview

The agent system consists of several key components:

1. **LLMAgent** (`agent.py`) - The main agent class that handles blockchain interactions, task bidding, and execution
2. **OpenAIIntegration** (`openai_integration.py`) - Handles all interactions with the OpenAI API
3. **AgentLearningConfig** (`agent_config.py`) - Provides configuration profiles for different agent learning strategies
4. **run_agents.py** - Main entry point for running multiple agents with different capabilities

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js v18+ (for the blockchain contracts)
- Hardhat (for local blockchain)
- OpenAI API key

### Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Make sure the blockchain contracts are deployed:

```bash
cd ..
npx hardhat compile
npx hardhat run scripts/deploy-all.js --network localhost
```

3. Run the setup script to configure the environment:

```bash
./setup_agents.sh
```

## Running the Agents

### Start Multiple Agents

To start multiple agents with different capabilities:

```bash
python run_agents.py --agents 5 --provider http://localhost:8545
```

This will:
1. Create 5 agents with different capabilities
2. Register them on the blockchain
3. Start their main loops to monitor for tasks, bid, and execute

### Create Example Tasks

To create example tasks in the system:

```bash
python run_agents.py --create-tasks --provider http://localhost:8545
```

### Run a Single Agent

You can also run a single agent with specific capabilities:

```bash
python agent.py
```

### Test the OpenAI Integration

To test the OpenAI integration separately:

```bash
python test_openai_integration.py
```

## Agent Capabilities

The system includes several pre-defined agent types with different capabilities:

1. **ResearchAgent** - Specialized in research, writing, and analysis
2. **DevelopmentAgent** - Specialized in coding, testing, and blockchain
3. **AnalyticsAgent** - Specialized in data analysis, statistics, and visualization
4. **CreativeAgent** - Specialized in creative writing, content creation, and storytelling
5. **BlockchainExpertAgent** - Specialized in blockchain, smart contracts, and tokenomics

## Learning Profiles

Agents can use different learning profiles that affect their bidding behavior and task selection:

1. **balanced** - Default balanced approach
2. **aggressive** - Takes more risks, bids more aggressively
3. **conservative** - Takes fewer risks, bids more conservatively
4. **explorer** - Prioritizes exploring new tasks and capabilities
5. **specialist** - Focuses on tasks that match its core capabilities
6. **workload_sensitive** - Prioritizes workload management

## OpenAI Integration

The OpenAI integration handles all interactions with the GPT models:

1. **evaluate_task_fit** - Evaluates how well an agent's capabilities match a task's requirements
2. **calculate_bid_amount** - Calculates a bid amount based on capabilities, reputation, and workload
3. **execute_task** - Executes a task using the agent's capabilities
4. **evaluate_task_result** - Evaluates the quality of a task result

## Agent Learning

The agent learning system allows agents to improve their capabilities over time based on task performance. The learning process includes:

1. **Reputation updates** - Agents gain or lose reputation based on task performance
2. **Capability weight adjustments** - Agents adjust their capability weights based on task feedback
3. **Bidding strategy adaptation** - Agents learn to bid more effectively based on past successes and failures

## Blockchain Integration

The agents interact with the following smart contracts:

1. **AgentRegistry** - For agent registration and capability management
2. **TaskManager** - For task creation, assignment, and completion
3. **BidAuction** - For bidding on tasks and winner selection
4. **TaskMarketplace** - For browsing and filtering available tasks
5. **MessageHub** - For secure communication between agents
6. **ActionLogger** - For logging agent actions
7. **IncentiveEngine** - For reputation and capability weight updates

## File Structure

- `agent.py` - Main agent implementation
- `openai_integration.py` - OpenAI API integration
- `agent_config.py` - Agent learning configuration
- `agent_learning.py` - Agent learning implementation
- `agent_learning_utils.py` - Utility functions for agent learning
- `agent_learning_example.py` - Example of agent learning
- `run_agents.py` - Main entry point for running multiple agents
- `test_openai_integration.py` - Test script for OpenAI integration
- `setup_agents.sh` - Setup script for agent environment
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Configuration

The agent system can be configured through:

1. `.env` file - For API keys and other sensitive information
2. `contract_addresses.json` - For blockchain contract addresses
3. `agent_config.py` - For agent learning parameters

## Advanced Usage

### Custom Agent Profiles

You can create custom agent profiles by modifying the `AGENT_DEFINITIONS` in `run_agents.py`:

```python
AGENT_DEFINITIONS = [
    {
        "name": "CustomAgent",
        "capabilities": ["custom_capability_1", "custom_capability_2"],
        "profile": "balanced"
    }
]
```

### Custom Learning Profiles

You can create custom learning profiles using the `AgentLearningConfig` class:

```python
custom_config = AgentLearningConfig.create_custom_profile(
    base_profile="conservative",
    learning_rate=0.1,
    exploration_rate=0.15
)
```

# Agent Learning System

This module implements a reinforcement learning system for blockchain-based AI agents, enabling them to improve their capabilities and bidding strategies over time.

## Components

### LearningIntegration

The main integration class that connects the agent's on-chain identity with the learning system. It handles:

- Loading and saving agent state
- Processing task results and feedback
- Updating agent capabilities
- Managing the reinforcement learning model
- Generating learning reports

### ReinforcementLearning

The core learning model that uses reinforcement learning to improve agent decision-making. Features:

- State representation of agent capabilities and task requirements
- Action space for bidding decisions
- Reward function based on task success and rewards
- Experience replay for improved learning
- Model persistence for continuous improvement

### AdaptiveBiddingStrategy

A strategy class that determines optimal bidding behavior based on:

- Agent capabilities
- Task requirements
- Current workload
- Reputation
- Confidence factor
- Risk tolerance

## Usage

### Initializing the Learning System

```python
from agents.learning_integration import LearningIntegration
from agents.reinforcement_learning import ReinforcementLearning

# Initialize the learning model
rl_model = ReinforcementLearning(
    agent_address="0x123...",
    learning_rate=0.001,
    discount_factor=0.95,
    exploration_rate=0.1
)

# Create the integration
learning = LearningIntegration(
    agent_address="0x123...",
    initial_capabilities={
        "analysis": 60,
        "generation": 70,
        "classification": 50,
        "translation": 40,
        "summarization": 55
    },
    rl_model=rl_model,
    reputation=50,
    confidence_factor=80,
    risk_tolerance=60
)
```

### Processing Task Results

```python
# After completing a task
learning.process_task_result(
    task_id="task_123",
    task_type="analysis",
    score=85,
    reward=200,
    tags={
        "analysis": 85,
        "research": 80,
        "finance": 90
    }
)
```

### Updating Agent Capabilities

```python
# Get updated capabilities
updated_capabilities = learning.get_capabilities()

# Update capabilities on-chain
# (implementation depends on your blockchain integration)
```

### Saving and Loading State

```python
# Save the learning state
learning.save_state()

# Load the learning state
learning = LearningIntegration.load_state(agent_address="0x123...")
```

### Generating Learning Reports

```python
# Get a learning report
report = learning.generate_report()
print(report)
```

## Integration Tests

The `test_integration.py` file provides comprehensive tests for the learning system:

```bash
# Run integration tests
python agents/test_integration.py
```

## Model Persistence

Learning models are saved in the `models/` directory with the following naming convention:

```
models/{agent_address}_rl_model.pt  # PyTorch model
models/{agent_address}_state.json   # Agent state
```

## Configuration

The learning system can be configured with the following parameters:

- `learning_rate`: Controls how quickly the model adapts (default: 0.001)
- `discount_factor`: Balances immediate vs. future rewards (default: 0.95)
- `exploration_rate`: Controls exploration vs. exploitation (default: 0.1)
- `batch_size`: Number of experiences to learn from at once (default: 64)
- `memory_size`: Size of experience replay buffer (default: 10000)

## License

This project is licensed under the MIT License. 