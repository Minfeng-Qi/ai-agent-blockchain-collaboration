import os
import json
import time
import random
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path so we can import from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv

from agents.agent import LLMAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("simulation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Simulation")

# Load environment variables
load_dotenv()

class MultiAgentSimulation:
    """
    Simulation environment for running multi-agent coordination experiments
    """
    def __init__(
        self, 
        num_agents: int = 5,
        num_rounds: int = 50,
        backend_url: str = "http://localhost:8000",
        web3_provider: str = "http://localhost:8545",
        task_corpus_path: str = "tasks.json"
    ):
        self.num_agents = num_agents
        self.num_rounds = num_rounds
        self.backend_url = backend_url
        self.web3_provider = web3_provider
        self.task_corpus_path = task_corpus_path
        
        self.agents = []
        self.tasks = []
        self.current_round = 0
        self.metrics = {
            "success_rate": [],
            "utility": [],
            "completion_time": [],
            "agent_participation": {}
        }
        
    async def load_task_corpus(self):
        """
        Load task corpus from JSON file
        """
        try:
            task_path = Path(self.task_corpus_path)
            if task_path.exists():
                with open(task_path, "r") as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from corpus")
            else:
                # Create demo tasks if file doesn't exist
                self.tasks = self._create_demo_tasks()
                
                # Save demo tasks for future use
                with open(task_path, "w") as f:
                    json.dump(self.tasks, f, indent=2)
                    
                logger.info(f"Created {len(self.tasks)} demo tasks")
        except Exception as e:
            logger.error(f"Error loading task corpus: {e}")
            self.tasks = self._create_demo_tasks()
            logger.info(f"Created {len(self.tasks)} demo tasks after error")
    
    def _create_demo_tasks(self) -> List[Dict[str, Any]]:
        """
        Create a set of demo tasks based on simplified ALFRED tasks
        """
        capabilities = [
            "text_analysis", "code_generation", "data_processing",
            "language_translation", "summarization", "reasoning",
            "question_answering", "mathematical_reasoning", "problem_solving",
            "creative_writing"
        ]
        
        tasks = []
        
        # Task templates
        templates = [
            {
                "name": "Code Analysis",
                "description": "Analyze the following Python code and identify potential bugs or performance issues: {code}",
                "requirements": ["code_generation", "reasoning"]
            },
            {
                "name": "Data Summarization",
                "description": "Summarize the key insights from this dataset: {data}",
                "requirements": ["data_processing", "summarization"]
            },
            {
                "name": "Language Translation",
                "description": "Translate the following text from {source_lang} to {target_lang}: {text}",
                "requirements": ["language_translation"]
            },
            {
                "name": "Problem Solving",
                "description": "Solve the following problem: {problem}",
                "requirements": ["problem_solving", "mathematical_reasoning"]
            },
            {
                "name": "Creative Content",
                "description": "Write a short story about {topic} with the following elements: {elements}",
                "requirements": ["creative_writing"]
            }
        ]
        
        # Generate 50 tasks based on templates
        for i in range(50):
            template = random.choice(templates)
            
            if template["name"] == "Code Analysis":
                code_samples = [
                    "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
                    "data = [i for i in range(10000)]\nresult = []\nfor i in data:\n    if i % 2 == 0:\n        result.append(i*i)",
                    "def process_items(items):\n    result = {}\n    for item in items:\n        result[item] = len(item)\n    return result"
                ]
                description = template["description"].format(code=random.choice(code_samples))
                
            elif template["name"] == "Data Summarization":
                data_samples = [
                    "Sales data for Q1-Q3 2023: Q1 ($2.3M), Q2 ($1.8M), Q3 ($3.1M) across 5 product categories.",
                    "Customer survey results: 45% very satisfied, 30% satisfied, 15% neutral, 10% dissatisfied with response times.",
                    "Website traffic by source: Direct (30%), Organic Search (40%), Social Media (15%), Referrals (10%), Other (5%)."
                ]
                description = template["description"].format(data=random.choice(data_samples))
                
            elif template["name"] == "Language Translation":
                text_samples = [
                    "The artificial intelligence revolution has transformed how we interact with technology.",
                    "Climate change presents significant challenges that require global cooperation.",
                    "Advances in renewable energy are crucial for sustainable development."
                ]
                lang_pairs = [("English", "French"), ("English", "Spanish"), ("English", "German")]
                source_lang, target_lang = random.choice(lang_pairs)
                description = template["description"].format(
                    source_lang=source_lang, 
                    target_lang=target_lang,
                    text=random.choice(text_samples)
                )
                
            elif template["name"] == "Problem Solving":
                problem_samples = [
                    "A company has 120 employees and needs to form teams of 5 people each. How many teams can they form, and how many employees will be left without a team?",
                    "If a train travels at 60 mph for 2 hours and then at 80 mph for 1 hour, what is the average speed for the entire journey?",
                    "A store is offering a 20% discount on an item. If the discounted price is $240, what was the original price?"
                ]
                description = template["description"].format(problem=random.choice(problem_samples))
                
            else:  # Creative Content
                topics = ["space exploration", "artificial intelligence", "underwater cities", "time travel"]
                elements_list = [
                    "a surprising twist, a character facing a moral dilemma",
                    "a historical setting, a technological discovery",
                    "a journey, an unexpected friendship"
                ]
                description = template["description"].format(
                    topic=random.choice(topics),
                    elements=random.choice(elements_list)
                )
            
            # Select 2-3 random requirements
            if len(template["requirements"]) < 3:
                task_requirements = template["requirements"].copy()
                # Add 1-2 random requirements
                additional_reqs = random.sample([c for c in capabilities if c not in task_requirements], 
                                              random.randint(1, 2))
                task_requirements.extend(additional_reqs)
            else:
                task_requirements = random.sample(template["requirements"], random.randint(2, 3))
            
            tasks.append({
                "name": f"{template['name']} Task {i+1}",
                "description": description,
                "requirements": task_requirements,
                "difficulty": random.randint(1, 5)
            })
        
        return tasks
    
    async def initialize_agents(self):
        """
        Initialize agent population with varying capabilities
        """
        capabilities_pool = [
            "text_analysis", "code_generation", "data_processing",
            "language_translation", "summarization", "reasoning",
            "question_answering", "mathematical_reasoning", "problem_solving",
            "creative_writing"
        ]
        
        # Load contract addresses if available
        contract_addresses = {}
        deployment_path = Path("../deployment/deployment.json")
        if deployment_path.exists():
            with open(deployment_path, "r") as f:
                deployment = json.load(f)
                contract_addresses = {
                    k: v for k, v in deployment.items() if k != "network" and k != "timestamp"
                }
        
        # Create agents with different capability combinations
        for i in range(self.num_agents):
            # Each agent has 4-7 capabilities
            num_capabilities = random.randint(4, 7)
            agent_capabilities = random.sample(capabilities_pool, num_capabilities)
            
            agent = LLMAgent(
                agent_name=f"Agent{i+1:03d}",
                capabilities=agent_capabilities,
                backend_url=self.backend_url,
                web3_provider=self.web3_provider,
                contract_addresses=contract_addresses
            )
            
            self.agents.append(agent)
            self.metrics["agent_participation"][agent.address] = 0
            
            logger.info(f"Initialized {agent.agent_name} with {len(agent_capabilities)} capabilities")
        
        # Register all agents on blockchain
        registration_tasks = [agent.register_on_blockchain() for agent in self.agents]
        await asyncio.gather(*registration_tasks)
        
    async def run_simulation(self):
        """
        Run the multi-agent simulation for the specified number of rounds
        """
        logger.info(f"Starting simulation with {self.num_agents} agents for {self.num_rounds} rounds")
        
        # Load tasks
        await self.load_task_corpus()
        
        # Initialize agents
        await self.initialize_agents()
        
        # Run rounds
        for round_num in range(1, self.num_rounds + 1):
            self.current_round = round_num
            logger.info(f"Starting round {round_num}/{self.num_rounds}")
            
            # Select tasks for this round (1-3 tasks per round)
            num_tasks = random.randint(1, 3)
            round_tasks = random.sample(self.tasks, num_tasks)
            
            # Submit tasks to backend
            submitted_tasks = []
            for task in round_tasks:
                try:
                    response = requests.post(
                        f"{self.backend_url}/tasks",
                        json={
                            "description": task["description"],
                            "requirements": task["requirements"]
                        }
                    )
                    
                    if response.status_code == 200:
                        submitted_task = response.json()
                        submitted_tasks.append(submitted_task)
                        logger.info(f"Submitted task: {submitted_task['task_id']}")
                    else:
                        logger.warning(f"Failed to submit task: {response.text}")
                        
                except Exception as e:
                    logger.error(f"Error submitting task: {e}")
            
            # Wait for bidding period
            logger.info("Waiting for agents to bid on tasks...")
            await asyncio.sleep(5)
            
            # Manually assign tasks to agents with highest bids
            # In a real system, this would be handled by smart contracts
            for task in submitted_tasks:
                try:
                    # Get all bids for this task
                    response = requests.get(f"{self.backend_url}/tasks/{task['task_id']}/bids")
                    
                    if response.status_code == 200:
                        bids = response.json()
                        
                        if bids:
                            # Sort bids by utility (highest first)
                            bids.sort(key=lambda x: x["utility"], reverse=True)
                            winning_bid = bids[0]
                            
                            # Assign task to winning bidder
                            assign_response = requests.post(
                                f"{self.backend_url}/tasks/{task['task_id']}/assign",
                                params={"agent_address": winning_bid["agent_address"]}
                            )
                            
                            if assign_response.status_code == 200:
                                logger.info(f"Task {task['task_id']} assigned to {winning_bid['agent_name']}")
                                
                                # Update participation metrics
                                self.metrics["agent_participation"][winning_bid["agent_address"]] += 1
                            else:
                                logger.warning(f"Failed to assign task: {assign_response.text}")
                        else:
                            logger.warning(f"No bids received for task {task['task_id']}")
                            
                except Exception as e:
                    logger.error(f"Error assigning task: {e}")
            
            # Wait for task execution
            logger.info("Waiting for agents to execute tasks...")
            await asyncio.sleep(10)
            
            # Collect round metrics
            round_success = 0
            round_utility = 0.0
            round_time = 0.0
            
            for task in submitted_tasks:
                try:
                    # Check task results
                    response = requests.get(f"{self.backend_url}/tasks/{task['task_id']}")
                    
                    if response.status_code == 200:
                        task_data = response.json()
                        
                        if task_data["status"] == "completed":
                            round_success += 1
                            
                            # Get task result details
                            result_response = requests.get(
                                f"{self.backend_url}/tasks/{task['task_id']}/result"
                            )
                            
                            if result_response.status_code == 200:
                                result = result_response.json()
                                
                                # Extract metrics
                                if "utility" in result:
                                    round_utility += result["utility"]
                                    
                                if "execution_time" in result:
                                    round_time += result["execution_time"]
                                    
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
            
            # Calculate round metrics
            if submitted_tasks:
                success_rate = round_success / len(submitted_tasks)
                avg_utility = round_utility / max(round_success, 1)
                avg_completion_time = round_time / max(round_success, 1)
                
                self.metrics["success_rate"].append(success_rate)
                self.metrics["utility"].append(avg_utility)
                self.metrics["completion_time"].append(avg_completion_time)
                
                logger.info(f"Round {round_num} metrics:")
                logger.info(f"  Success rate: {success_rate:.2f}")
                logger.info(f"  Average utility: {avg_utility:.2f}")
                logger.info(f"  Average completion time: {avg_completion_time:.2f} seconds")
            
            # Wait before next round
            await asyncio.sleep(5)
        
        # Save final metrics
        self._save_metrics()
    
    def _save_metrics(self):
        """
        Save simulation metrics to file
        """
        try:
            metrics_path = Path("simulation_metrics.json")
            with open(metrics_path, "w") as f:
                json.dump(self.metrics, f, indent=2)
            
            logger.info(f"Saved metrics to {metrics_path}")
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

async def main():
    """
    Main entry point for running a simulation
    """
    simulation = MultiAgentSimulation(
        num_agents=5,
        num_rounds=50,
        backend_url="http://localhost:8000",
        web3_provider="http://localhost:8545"
    )
    
    await simulation.run_simulation()

if __name__ == "__main__":
    asyncio.run(main())