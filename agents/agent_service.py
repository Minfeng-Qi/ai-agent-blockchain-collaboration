#!/usr/bin/env python3
"""
Agent Service - Main entry point for running agent processes
"""

import os
import time
import json
import logging
import asyncio
import signal
import sys
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
from loguru import logger
from web3 import Web3

# Import local modules
from core.agent import Agent
from core.agent_config import AgentConfig
from ai.agent_learning import AgentLearning

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/agent_service.log", rotation="10 MB", level="DEBUG")

# Constants
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
AGENT_REGISTRY_ADDRESS = os.getenv("AGENT_REGISTRY_ADDRESS")
TASK_MANAGER_ADDRESS = os.getenv("TASK_MANAGER_ADDRESS")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))  # seconds

# Global variables
running = True
agents: Dict[str, Agent] = {}
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))


async def initialize_agents():
    """Initialize agents from the registry"""
    try:
        logger.info("Initializing agents from registry")
        response = requests.get(f"{BACKEND_API_URL}/agents")
        if response.status_code == 200:
            agent_data = response.json().get("agents", [])
            for agent_info in agent_data:
                agent_id = agent_info.get("agent_id")
                if agent_id and agent_id not in agents:
                    logger.info(f"Initializing agent {agent_id}")
                    
                    # Create agent config
                    config = AgentConfig(
                        agent_id=agent_id,
                        capabilities=agent_info.get("capabilities", []),
                        confidence_factor=agent_info.get("confidence_factor", 0.8),
                        risk_tolerance=agent_info.get("risk_tolerance", 0.5)
                    )
                    
                    # Create agent instance
                    agent = Agent(config)
                    
                    # Add learning module
                    agent.learning = AgentLearning(agent)
                    
                    # Store agent
                    agents[agent_id] = agent
                    logger.info(f"Agent {agent_id} initialized with {len(agent.config.capabilities)} capabilities")
        else:
            logger.error(f"Failed to fetch agents: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Error initializing agents: {e}")


async def poll_for_tasks():
    """Poll for available tasks and bid on suitable ones"""
    try:
        logger.info("Polling for available tasks")
        response = requests.get(f"{BACKEND_API_URL}/tasks?status=open")
        if response.status_code == 200:
            tasks = response.json().get("tasks", [])
            logger.info(f"Found {len(tasks)} open tasks")
            
            for task in tasks:
                task_id = task.get("task_id")
                required_capabilities = task.get("required_capabilities", [])
                reward = task.get("reward", 0)
                
                # Find suitable agents for this task
                for agent_id, agent in agents.items():
                    if agent.can_perform_task(required_capabilities):
                        bid_amount = agent.calculate_bid(task)
                        if bid_amount > 0:
                            logger.info(f"Agent {agent_id} bidding {bid_amount} on task {task_id}")
                            try:
                                bid_response = requests.post(
                                    f"{BACKEND_API_URL}/tasks/{task_id}/bids",
                                    json={
                                        "agent_id": agent_id,
                                        "bid_amount": bid_amount,
                                        "estimated_time": agent.estimate_completion_time(task)
                                    }
                                )
                                if bid_response.status_code == 200:
                                    logger.info(f"Bid placed successfully for task {task_id}")
                                else:
                                    logger.error(f"Failed to place bid: {bid_response.status_code} - {bid_response.text}")
                            except Exception as e:
                                logger.error(f"Error placing bid: {e}")
        else:
            logger.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Error polling for tasks: {e}")


async def check_assigned_tasks():
    """Check for tasks assigned to our agents and process them"""
    try:
        for agent_id, agent in agents.items():
            response = requests.get(f"{BACKEND_API_URL}/agents/{agent_id}/tasks?status=assigned")
            if response.status_code == 200:
                assigned_tasks = response.json().get("tasks", [])
                for task in assigned_tasks:
                    task_id = task.get("task_id")
                    logger.info(f"Agent {agent_id} processing task {task_id}")
                    
                    # Process the task
                    try:
                        result = await agent.process_task(task)
                        
                        # Submit result
                        submit_response = requests.post(
                            f"{BACKEND_API_URL}/tasks/{task_id}/complete",
                            json={
                                "agent_id": agent_id,
                                "result": result
                            }
                        )
                        
                        if submit_response.status_code == 200:
                            logger.info(f"Task {task_id} completed successfully")
                            
                            # Update agent learning
                            await agent.learning.update_from_task(task, result)
                        else:
                            logger.error(f"Failed to submit task result: {submit_response.status_code} - {submit_response.text}")
                    except Exception as e:
                        logger.error(f"Error processing task {task_id}: {e}")
                        
                        # Report failure
                        requests.post(
                            f"{BACKEND_API_URL}/tasks/{task_id}/fail",
                            json={
                                "agent_id": agent_id,
                                "reason": str(e)
                            }
                        )
    except Exception as e:
        logger.exception(f"Error checking assigned tasks: {e}")


async def main_loop():
    """Main service loop"""
    await initialize_agents()
    
    while running:
        try:
            await poll_for_tasks()
            await check_assigned_tasks()
            await asyncio.sleep(POLL_INTERVAL)
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")
            await asyncio.sleep(POLL_INTERVAL)


def signal_handler(sig, frame):
    """Handle termination signals"""
    global running
    logger.info("Shutdown signal received, stopping service...")
    running = False


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Agent Service")
    
    # Check connections
    try:
        # Check backend API
        response = requests.get(f"{BACKEND_API_URL}/health")
        if response.status_code == 200:
            logger.info("Successfully connected to backend API")
        else:
            logger.error(f"Backend API connection failed: {response.status_code}")
        
        # Check Web3 connection
        if web3.is_connected():
            chain_id = web3.eth.chain_id
            logger.info(f"Successfully connected to blockchain (Chain ID: {chain_id})")
        else:
            logger.error("Web3 connection failed")
    except Exception as e:
        logger.error(f"Error checking connections: {e}")
    
    # Run the main loop
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.exception(f"Service error: {e}")
    
    logger.info("Agent Service stopped")