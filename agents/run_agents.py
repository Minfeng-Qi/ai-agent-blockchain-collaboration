#!/usr/bin/env python3
import os
import json
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from eth_account import Account

# 更新导入路径
from agents.core.agent import LLMAgent
from agents.ai.openai_integration import OpenAIIntegration
from agents.core.agent_config import AgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AgentRunner")

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = "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"

# Default contract addresses (these should be updated after deployment)
DEFAULT_CONTRACT_ADDRESSES = {
    "AgentRegistry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ActionLogger": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "IncentiveEngine": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
    "TaskManager": "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9",
    "BidAuction": "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9",
    "TaskMarketplace": "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853",
    "MessageHub": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"
}

# Agent definitions - each with different capabilities
AGENT_DEFINITIONS = [
    {
        "name": "ResearchAgent",
        "capabilities": ["research", "writing", "analysis"],
        "profile": "balanced"
    },
    {
        "name": "DevelopmentAgent",
        "capabilities": ["coding", "testing", "blockchain"],
        "profile": "specialist"
    },
    {
        "name": "AnalyticsAgent",
        "capabilities": ["data analysis", "statistics", "visualization"],
        "profile": "conservative"
    },
    {
        "name": "CreativeAgent",
        "capabilities": ["creative writing", "content creation", "storytelling"],
        "profile": "explorer"
    },
    {
        "name": "BlockchainExpertAgent",
        "capabilities": ["blockchain", "smart contracts", "tokenomics"],
        "profile": "aggressive"
    }
]

# Example tasks to be created in the system
EXAMPLE_TASKS = [
    {
        "description": "Research and write a comprehensive analysis of Layer 2 scaling solutions for Ethereum",
        "requirements": ["research", "writing", "blockchain"],
        "min_reputation": 40,
        "reward": 0.15,
        "deadline_days": 3
    },
    {
        "description": "Develop a simple DeFi yield aggregator smart contract with documentation",
        "requirements": ["coding", "blockchain", "smart contracts"],
        "min_reputation": 60,
        "reward": 0.25,
        "deadline_days": 5
    },
    {
        "description": "Create an engaging article explaining blockchain technology to beginners",
        "requirements": ["creative writing", "blockchain", "content creation"],
        "min_reputation": 30,
        "reward": 0.1,
        "deadline_days": 2
    },
    {
        "description": "Analyze on-chain data to identify patterns in DEX trading volumes",
        "requirements": ["data analysis", "blockchain", "statistics"],
        "min_reputation": 50,
        "reward": 0.2,
        "deadline_days": 4
    }
]

async def create_and_run_agents(
    num_agents: int = 5,
    web3_provider: str = "http://localhost:8545",
    contract_addresses: Dict[str, str] = None
) -> List[LLMAgent]:
    """
    Create and run multiple agents with different capabilities.
    
    Args:
        num_agents: Number of agents to create (max 5)
        web3_provider: URL of the Web3 provider
        contract_addresses: Dictionary of contract addresses
        
    Returns:
        List of created agents
    """
    if contract_addresses is None:
        contract_addresses = DEFAULT_CONTRACT_ADDRESSES
        
    # Limit the number of agents to the available definitions
    num_agents = min(num_agents, len(AGENT_DEFINITIONS))
    
    # Create OpenAI integration
    openai_integration = OpenAIIntegration(api_key=OPENAI_API_KEY)
    
    # Create agents
    agents = []
    for i in range(num_agents):
        agent_def = AGENT_DEFINITIONS[i]
        
        # Generate a deterministic private key for testing
        # In production, these would be securely stored
        private_key = Account.create(f"test_key_{i}").key.hex()
        
        # Get learning profile
        profile = AgentConfig.get_profile(agent_def["profile"])
        
        # Create agent
        agent = LLMAgent(
            agent_name=agent_def["name"],
            capabilities=agent_def["capabilities"],
            private_key=private_key,
            api_key=OPENAI_API_KEY,
            web3_provider=web3_provider,
            contract_addresses=contract_addresses
        )
        
        # Add the agent to our list
        agents.append(agent)
        logger.info(f"Created agent: {agent_def['name']} with capabilities: {agent_def['capabilities']}")
    
    # Register agents on blockchain (in parallel)
    registration_tasks = [agent.register_on_blockchain() for agent in agents]
    registration_results = await asyncio.gather(*registration_tasks)
    
    for agent, result in zip(agents, registration_results):
        if result:
            logger.info(f"Agent {agent.agent_name} registered successfully")
        else:
            logger.warning(f"Agent {agent.agent_name} registration failed")
    
    # Start agent event loops
    agent_tasks = [agent.run() for agent in agents]
    await asyncio.gather(*agent_tasks)
    
    return agents

async def create_example_tasks(
    web3_provider: str = "http://localhost:8545",
    contract_addresses: Dict[str, str] = None
):
    """
    Create example tasks in the system using a task creator agent.
    
    Args:
        web3_provider: URL of the Web3 provider
        contract_addresses: Dictionary of contract addresses
    """
    if contract_addresses is None:
        contract_addresses = DEFAULT_CONTRACT_ADDRESSES
    
    # Create a task creator agent
    private_key = Account.create("task_creator").key.hex()
    
    task_creator = LLMAgent(
        agent_name="TaskCreator",
        capabilities=["task management"],
        private_key=private_key,
        api_key=OPENAI_API_KEY,
        web3_provider=web3_provider,
        contract_addresses=contract_addresses
    )
    
    # Register the task creator
    registered = await task_creator.register_on_blockchain()
    if not registered:
        logger.error("Failed to register task creator agent")
        return
    
    # Create tasks
    for task in EXAMPLE_TASKS:
        # TODO: Implement task creation through the blockchain
        # This would call the TaskMarketplace contract's createTask function
        logger.info(f"Would create task: {task['description']}")
    
    logger.info("Example tasks created")

async def main():
    parser = argparse.ArgumentParser(description="Run multiple LLM agents on the blockchain")
    parser.add_argument("--agents", type=int, default=5, help="Number of agents to run (max 5)")
    parser.add_argument("--provider", type=str, default="http://localhost:8545", help="Web3 provider URL")
    parser.add_argument("--create-tasks", action="store_true", help="Create example tasks")
    
    args = parser.parse_args()
    
    # Load contract addresses from file if available
    contract_addresses = DEFAULT_CONTRACT_ADDRESSES
    if Path("contract_addresses.json").exists():
        with open("contract_addresses.json", "r") as f:
            contract_addresses = json.load(f)
    
    # Create example tasks if requested
    if args.create_tasks:
        await create_example_tasks(args.provider, contract_addresses)
    
    # Create and run agents
    agents = await create_and_run_agents(args.agents, args.provider, contract_addresses)
    
    # Keep the program running
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down agents...")

if __name__ == "__main__":
    asyncio.run(main()) 