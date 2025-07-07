#!/usr/bin/env python3
import asyncio
import logging
import json
from typing import List, Dict, Any

from openai_integration import OpenAIIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("TestOpenAIIntegration")

# OpenAI API key
OPENAI_API_KEY = "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"

# Test agents with different capabilities
TEST_AGENTS = [
    {
        "name": "ResearchAgent",
        "capabilities": ["research", "writing", "analysis"]
    },
    {
        "name": "DevelopmentAgent",
        "capabilities": ["coding", "testing", "blockchain"]
    },
    {
        "name": "AnalyticsAgent",
        "capabilities": ["data analysis", "statistics", "visualization"]
    }
]

# Test tasks with different requirements
TEST_TASKS = [
    {
        "id": "task-001",
        "description": "Research and write a comprehensive analysis of Layer 2 scaling solutions for Ethereum",
        "requirements": ["research", "writing", "blockchain"],
        "max_reward": 0.15,
        "min_reputation": 40
    },
    {
        "id": "task-002",
        "description": "Develop a simple DeFi yield aggregator smart contract with documentation",
        "requirements": ["coding", "blockchain", "smart contracts"],
        "max_reward": 0.25,
        "min_reputation": 60
    },
    {
        "id": "task-003",
        "description": "Analyze on-chain data to identify patterns in DEX trading volumes",
        "requirements": ["data analysis", "blockchain", "statistics"],
        "max_reward": 0.2,
        "min_reputation": 50
    }
]

async def test_task_evaluation(openai_integration: OpenAIIntegration):
    """
    Test task evaluation for different agents and tasks.
    """
    logger.info("=== Testing Task Evaluation ===")
    
    results = []
    
    for agent in TEST_AGENTS:
        agent_results = []
        
        for task in TEST_TASKS:
            score = await openai_integration.evaluate_task_fit(
                agent_capabilities=agent["capabilities"],
                task_description=task["description"],
                task_requirements=task["requirements"]
            )
            
            agent_results.append({
                "task_id": task["id"],
                "score": score
            })
            
            logger.info(f"Agent: {agent['name']}, Task: {task['id']}, Score: {score}")
        
        results.append({
            "agent_name": agent["name"],
            "task_scores": agent_results
        })
    
    # Find the best agent for each task
    for task in TEST_TASKS:
        best_score = -1
        best_agent = None
        
        for agent in TEST_AGENTS:
            for result in next(r for r in results if r["agent_name"] == agent["name"])["task_scores"]:
                if result["task_id"] == task["id"] and result["score"] > best_score:
                    best_score = result["score"]
                    best_agent = agent["name"]
        
        logger.info(f"Best agent for task {task['id']}: {best_agent} (score: {best_score})")
    
    return results

async def test_bid_calculation(openai_integration: OpenAIIntegration):
    """
    Test bid calculation for different agents and tasks.
    """
    logger.info("\n=== Testing Bid Calculation ===")
    
    results = []
    
    for agent in TEST_AGENTS:
        agent_results = []
        
        # Simulate different agent reputations and workloads
        agent_reputation = {
            "ResearchAgent": 70,
            "DevelopmentAgent": 85,
            "AnalyticsAgent": 60
        }.get(agent["name"], 50)
        
        agent_workload = {
            "ResearchAgent": 2,
            "DevelopmentAgent": 1,
            "AnalyticsAgent": 3
        }.get(agent["name"], 0)
        
        for task in TEST_TASKS:
            bid_amount, reasoning = await openai_integration.calculate_bid_amount(
                agent_capabilities=agent["capabilities"],
                task_description=task["description"],
                task_requirements=task["requirements"],
                max_reward=task["max_reward"],
                agent_reputation=agent_reputation,
                min_reputation=task["min_reputation"],
                current_workload=agent_workload
            )
            
            agent_results.append({
                "task_id": task["id"],
                "bid_amount": bid_amount,
                "reasoning": reasoning
            })
            
            logger.info(f"Agent: {agent['name']}, Task: {task['id']}, Bid: {bid_amount} ETH")
            logger.info(f"Reasoning: {reasoning[:100]}...")
        
        results.append({
            "agent_name": agent["name"],
            "reputation": agent_reputation,
            "workload": agent_workload,
            "bids": agent_results
        })
    
    return results

async def test_task_execution(openai_integration: OpenAIIntegration):
    """
    Test task execution for a specific agent and task.
    """
    logger.info("\n=== Testing Task Execution ===")
    
    # Select the first task and the most suitable agent
    task = TEST_TASKS[0]
    agent = TEST_AGENTS[0]  # ResearchAgent is good for the first task
    
    logger.info(f"Executing task {task['id']} with agent {agent['name']}")
    
    result = await openai_integration.execute_task(
        agent_capabilities=agent["capabilities"],
        agent_name=agent["name"],
        task_description=task["description"],
        task_requirements=task["requirements"]
    )
    
    logger.info(f"Task execution status: {result['status']}")
    logger.info(f"Result preview: {result['result'][:200]}...")
    
    if "metadata" in result:
        logger.info(f"Tokens used: {result['metadata']['total_tokens']}")
    
    return result

async def test_result_evaluation(openai_integration: OpenAIIntegration, task_result: Dict[str, Any]):
    """
    Test result evaluation for a completed task.
    """
    logger.info("\n=== Testing Result Evaluation ===")
    
    task = TEST_TASKS[0]
    
    evaluation = await openai_integration.evaluate_task_result(
        task_description=task["description"],
        task_requirements=task["requirements"],
        task_result=task_result["result"]
    )
    
    logger.info(f"Evaluation scores: {json.dumps(evaluation['scores'], indent=2)}")
    logger.info("Strengths:")
    for strength in evaluation["feedback"]["strengths"]:
        logger.info(f"- {strength}")
    
    logger.info("Areas for improvement:")
    for improvement in evaluation["feedback"]["improvements"]:
        logger.info(f"- {improvement}")
    
    return evaluation

async def main():
    """
    Run all tests for the OpenAI integration.
    """
    logger.info("Starting OpenAI integration tests")
    
    # Initialize OpenAI integration
    openai_integration = OpenAIIntegration(api_key=OPENAI_API_KEY)
    
    # Test task evaluation
    evaluation_results = await test_task_evaluation(openai_integration)
    
    # Test bid calculation
    bid_results = await test_bid_calculation(openai_integration)
    
    # Test task execution
    execution_result = await test_task_execution(openai_integration)
    
    # Test result evaluation
    evaluation = await test_result_evaluation(openai_integration, execution_result)
    
    logger.info("All tests completed successfully")
    
    # Save results to file
    with open("openai_test_results.json", "w") as f:
        json.dump({
            "evaluation_results": evaluation_results,
            "bid_results": bid_results,
            "execution_result": {
                "status": execution_result["status"],
                "result_preview": execution_result["result"][:500] + "..."
            },
            "result_evaluation": evaluation
        }, f, indent=2)
    
    logger.info("Results saved to openai_test_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 