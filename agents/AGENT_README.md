# LLM Multi-Agent System with OpenAI Integration

This directory contains the agent implementation for the blockchain-based LLM multi-agent coordination system. The agents use OpenAI's GPT models to evaluate tasks, calculate bids, execute tasks, and evaluate results.

## System Overview

The agent system consists of several key components:

1. **LLMAgent** - The main agent class that handles blockchain interactions, task bidding, and execution
2. **OpenAIIntegration** - Handles all interactions with the OpenAI API
3. **AgentLearningConfig** - Provides configuration profiles for different agent learning strategies
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

3. Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=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
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

This will create a test agent and register it on the blockchain.

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

## System Architecture

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────┐
│                 │     │                   │     │                 │
│   Blockchain    │◄────┤    LLM Agents     │────►│   OpenAI API    │
│   Contracts     │     │                   │     │                 │
│                 │     └───────────────────┘     └─────────────────┘
└─────────────────┘              ▲
        ▲                        │
        │                        │
        │                        │
        │                        │
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌───────────────────┐
│                 │     │                   │
│  Task Creation  │     │  Agent Learning   │
│                 │     │                   │
└─────────────────┘     └───────────────────┘
```

## Customizing Agents

You can create custom agents by modifying the `AGENT_DEFINITIONS` in `run_agents.py`. Each agent definition includes:

- **name** - The name of the agent
- **capabilities** - List of capabilities the agent has
- **profile** - The learning profile to use

## Contract Addresses

The system uses the following contract addresses by default:

```python
DEFAULT_CONTRACT_ADDRESSES = {
    "AgentRegistry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ActionLogger": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "IncentiveEngine": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
    "TaskManager": "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9",
    "BidAuction": "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9",
    "TaskMarketplace": "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853",
    "MessageHub": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"
}
```

If your contracts are deployed to different addresses, you can create a `contract_addresses.json` file with the correct addresses.

## Testing the OpenAI Integration

You can test the OpenAI integration separately:

```bash
python openai_integration.py
```

This will run a test function that evaluates tasks, calculates bids, executes tasks, and evaluates results. 