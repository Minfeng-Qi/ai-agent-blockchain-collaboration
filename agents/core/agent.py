import os
import json
import time
import random
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import openai
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

from openai_integration import OpenAIIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Agent")

# Load environment variables
load_dotenv()

class LLMAgent:
    """
    Autonomous agent using LLM (GPT-4) for task evaluation, bidding, and execution.
    Interacts with blockchain for registration, authentication, and task management.
    """
    def __init__(
        self,
        agent_name: str,
        capabilities: List[str],
        private_key: Optional[str] = None,
        api_key: Optional[str] = None,
        backend_url: str = "http://localhost:8000",
        web3_provider: str = "http://localhost:8545",
        contract_addresses: Optional[Dict[str, str]] = None
    ):
        # Agent identity
        self.agent_name = agent_name
        self.capabilities = capabilities
        
        # Generate new key if not provided
        if private_key is None:
            self.account = Account.create()
            self.private_key = self.account.key.hex()
        else:
            self.private_key = private_key
            self.account = Account.from_key(private_key)
        
        self.address = self.account.address
        
        # API keys and endpoints
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI integration
        self.openai_integration = OpenAIIntegration(api_key=self.openai_api_key)
        self.backend_url = backend_url
        
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABIs and addresses
        self.contract_addresses = contract_addresses or {}
        self.load_contracts()
        
        # Agent state
        self.registered = False
        self.current_tasks = []
        self.task_history = []
        self.nonce = 0  # For signature uniqueness
        self.reputation = 50  # Default starting reputation
        self.workload = 0  # Current workload
        
        logger.info(f"Agent {self.agent_name} initialized with address {self.address}")

    def load_contracts(self):
        """
        Load contract ABIs and create contract instances
        """
        # Check if contracts directory exists
        if not Path("../artifacts/contracts").exists():
            logger.warning("Contracts not compiled yet. Please run 'npx hardhat compile'")
            return
        
        try:
            # Load AgentRegistry contract
            with open("../artifacts/contracts/AgentRegistry.sol/AgentRegistry.json", "r") as f:
                agent_registry_json = json.load(f)
                
            registry_address = self.contract_addresses.get("AgentRegistry")
            if registry_address:
                self.agent_registry = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(registry_address),
                    abi=agent_registry_json["abi"]
                )
                logger.info(f"Loaded AgentRegistry contract at {registry_address}")
            else:
                logger.warning("AgentRegistry address not provided")
                self.agent_registry = None
            
            # Load TaskManager contract
            with open("../artifacts/contracts/TaskManager.sol/TaskManager.json", "r") as f:
                task_manager_json = json.load(f)
                
            task_manager_address = self.contract_addresses.get("TaskManager")
            if task_manager_address:
                self.task_manager = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(task_manager_address),
                    abi=task_manager_json["abi"]
                )
                logger.info(f"Loaded TaskManager contract at {task_manager_address}")
            else:
                logger.warning("TaskManager address not provided")
                self.task_manager = None
            
            # Load BidAuction contract
            with open("../artifacts/contracts/BidAuction.sol/BidAuction.json", "r") as f:
                bid_auction_json = json.load(f)
                
            bid_auction_address = self.contract_addresses.get("BidAuction")
            if bid_auction_address:
                self.bid_auction = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(bid_auction_address),
                    abi=bid_auction_json["abi"]
                )
                logger.info(f"Loaded BidAuction contract at {bid_auction_address}")
            else:
                logger.warning("BidAuction address not provided")
                self.bid_auction = None
            
            # Load TaskMarketplace contract
            with open("../artifacts/contracts/TaskMarketplace.sol/TaskMarketplace.json", "r") as f:
                task_marketplace_json = json.load(f)
                
            marketplace_address = self.contract_addresses.get("TaskMarketplace")
            if marketplace_address:
                self.task_marketplace = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(marketplace_address),
                    abi=task_marketplace_json["abi"]
                )
                logger.info(f"Loaded TaskMarketplace contract at {marketplace_address}")
            else:
                logger.warning("TaskMarketplace address not provided")
                self.task_marketplace = None
                
        except Exception as e:
            logger.error(f"Error loading contracts: {e}")
            self.agent_registry = None
            self.task_manager = None
            self.bid_auction = None
            self.task_marketplace = None

    async def register_on_blockchain(self):
        """
        Register the agent on the blockchain via the AgentRegistry contract
        """
        if not self.agent_registry:
            logger.error("AgentRegistry contract not loaded")
            return False
            
        try:
            # Create agent metadata and upload to IPFS
            metadata = {
                "name": self.agent_name,
                "address": self.address,
                "capabilities": self.capabilities,
                "api_version": "1.0",
                "created_at": datetime.now().isoformat()
            }
            
            # For now, we'll use a placeholder URI - in production this would be an IPFS hash
            metadata_uri = f"ipfs://placeholder/{self.address}"
            
            # Check if agent is already registered
            agent_data = await self.get_agent_data()
            if agent_data and agent_data[0] != "":  # Name is not empty
                logger.info(f"Agent {self.agent_name} already registered")
                self.registered = True
                return True
            
            # Call the registerAgent function
            tx = self.agent_registry.functions.registerAgent(
                self.address,
                self.agent_name,
                metadata_uri,
                "https://agent-api.example.com",
                1  # Agent type (1 = LLM agent)
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                self.registered = True
                logger.info(f"Agent {self.agent_name} successfully registered on blockchain")
                
                # Set agent capabilities
                await self.set_agent_capabilities()
                
                return True
            else:
                logger.error("Registration failed")
                return False
                
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return False
    
    async def set_agent_capabilities(self):
        """
        Set the agent's capabilities on the blockchain
        """
        if not self.agent_registry or not self.registered:
            logger.error("Cannot set capabilities: Agent not registered or contract not loaded")
            return False
        
        try:
            # Default weights - all 50
            weights = [50] * len(self.capabilities)
            
            # Call the setCapabilities function
            tx = self.agent_registry.functions.setCapabilities(
                self.address,
                self.capabilities,
                weights
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Agent capabilities set successfully: {self.capabilities}")
                return True
            else:
                logger.error("Setting capabilities failed")
                return False
                
        except Exception as e:
            logger.error(f"Error setting capabilities: {e}")
            return False
    
    async def get_agent_data(self):
        """
        Get agent data from the blockchain
        """
        if not self.agent_registry:
            logger.error("AgentRegistry contract not loaded")
            return None
            
        try:
            # Call the agents mapping
            agent_data = await self.agent_registry.functions.agents(self.address).call()
            return agent_data
        except Exception as e:
            logger.error(f"Error getting agent data: {e}")
            return None

    def sign_message(self, message: str) -> Tuple[bytes, int]:
        """
        Sign a message using the agent's private key
        
        Args:
            message: Message to sign
            
        Returns:
            Tuple of (signature, nonce)
        """
        # Increment nonce to ensure uniqueness
        self.nonce += 1
        
        # Add nonce to message
        message_with_nonce = f"{message}|nonce:{self.nonce}"
        
        # Sign the message
        message_hash = encode_defunct(text=message_with_nonce)
        signed_message = self.w3.eth.account.sign_message(message_hash, private_key=self.private_key)
        
        return signed_message.signature, self.nonce

    async def evaluate_task(self, task_description: str, requirements: List[str]) -> float:
        """
        Evaluate agent's fit for a task using the LLM
        
        Args:
            task_description: Description of the task
            requirements: List of required capabilities
            
        Returns:
            Utility score between 0.0 and 1.0
        """
        # Use the OpenAI integration to evaluate the task fit
        score = await self.openai_integration.evaluate_task_fit(
            agent_capabilities=self.capabilities,
            task_description=task_description,
            task_requirements=requirements
        )
        
        logger.info(f"Agent {self.agent_name} evaluated task with score {score}")
        return score

    async def bid_for_task(
        self, 
        task_id: str, 
        task_description: str, 
        requirements: List[str],
        max_reward: float,
        min_reputation: int
    ) -> Dict:
        """
        Calculate and submit a bid for a task
        
        Args:
            task_id: ID of the task
            task_description: Description of the task
            requirements: List of required capabilities
            max_reward: Maximum reward for the task
            min_reputation: Minimum reputation required
            
        Returns:
            Dictionary with bid details
        """
        # First check if we meet the minimum reputation requirement
        if self.reputation < min_reputation:
            logger.info(f"Agent {self.agent_name} does not meet minimum reputation requirement ({self.reputation} < {min_reputation})")
            return {"success": False, "reason": "Insufficient reputation"}
        
        # Use the OpenAI integration to calculate a bid amount
        bid_amount, reasoning = await self.openai_integration.calculate_bid_amount(
            agent_capabilities=self.capabilities,
            task_description=task_description,
            task_requirements=requirements,
            max_reward=max_reward,
            agent_reputation=self.reputation,
            min_reputation=min_reputation,
            current_workload=self.workload
        )
        
        logger.info(f"Agent {self.agent_name} calculated bid: {bid_amount} ETH for task {task_id}")
        logger.info(f"Bid reasoning: {reasoning}")
        
        # Submit bid to the blockchain
        if self.bid_auction:
            try:
                # Convert task_id to bytes32 if needed
                task_id_bytes32 = Web3.to_bytes(hexstr=task_id) if task_id.startswith('0x') else Web3.to_bytes(text=task_id)
                
                # Convert bid amount to wei
                bid_amount_wei = self.w3.to_wei(bid_amount, 'ether')
                
                # Call the placeBid function
                tx = self.bid_auction.functions.placeBid(
                    task_id_bytes32,
                    bid_amount_wei
                ).build_transaction({
                    'from': self.address,
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                    'gas': 2000000,
                    'gasPrice': self.w3.eth.gas_price
                })
                
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                if receipt.status == 1:
                    logger.info(f"Bid placed successfully for task {task_id}")
                    return {
                        "success": True, 
                        "bid_amount": bid_amount, 
                        "reasoning": reasoning,
                        "tx_hash": tx_hash.hex()
                    }
                else:
                    logger.error(f"Bid placement failed for task {task_id}")
                    return {"success": False, "reason": "Transaction failed"}
                    
            except Exception as e:
                logger.error(f"Error placing bid: {e}")
                return {"success": False, "reason": str(e)}
        else:
            logger.error("BidAuction contract not loaded")
            return {"success": False, "reason": "Contract not loaded"}

    async def execute_task(self, task_id: str, task_description: str, requirements: List[str]) -> Dict:
        """
        Execute a task using the LLM
        
        Args:
            task_id: ID of the task
            task_description: Description of the task
            requirements: List of required capabilities
            
        Returns:
            Dictionary with task results
        """
        logger.info(f"Agent {self.agent_name} executing task {task_id}")
        
        # Update workload
        self.workload += 1
        
        # Use the OpenAI integration to execute the task
        result = await self.openai_integration.execute_task(
            agent_capabilities=self.capabilities,
            agent_name=self.agent_name,
            task_description=task_description,
            task_requirements=requirements
        )
        
        if result["status"] == "completed":
            logger.info(f"Task {task_id} executed successfully")
            
            # In a real implementation, we would upload the result to IPFS
            # and submit the IPFS hash to the blockchain
            result_uri = f"ipfs://placeholder/{task_id}"
            
            # Submit completion to the blockchain
            if self.task_manager:
                try:
                    # Convert task_id to bytes32 if needed
                    task_id_bytes32 = Web3.to_bytes(hexstr=task_id) if task_id.startswith('0x') else Web3.to_bytes(text=task_id)
                    
                    # Call the completeTask function
                    tx = self.task_manager.functions.completeTask(
                        task_id_bytes32,
                        result_uri
                    ).build_transaction({
                        'from': self.address,
                        'nonce': self.w3.eth.get_transaction_count(self.address),
                        'gas': 2000000,
                        'gasPrice': self.w3.eth.gas_price
                    })
                    
                    signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    if receipt.status == 1:
                        logger.info(f"Task {task_id} completion submitted to blockchain")
                        # Update workload
                        self.workload -= 1
                    else:
                        logger.error(f"Task {task_id} completion submission failed")
                        
                except Exception as e:
                    logger.error(f"Error submitting task completion: {e}")
            else:
                logger.error("TaskManager contract not loaded")
        
        # Add task to history
        self.task_history.append({
            "task_id": task_id,
            "description": task_description,
            "requirements": requirements,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result

    async def monitor_open_tasks(self):
        """
        Monitor the blockchain for open tasks that match the agent's capabilities
        """
        if not self.task_marketplace:
            logger.error("TaskMarketplace contract not loaded")
            return []
        
        try:
            # Get open tasks from the marketplace
            open_tasks = await self.task_marketplace.functions.getOpenTasks().call()
            
            # Filter tasks that match the agent's capabilities
            matching_tasks = []
            for task_id in open_tasks:
                # Get task details
                task = await self.task_manager.functions.tasks(task_id).call()
                
                # Check if bidding is open
                is_bidding_open = await self.bid_auction.functions.isBiddingOpen(task_id).call()
                if not is_bidding_open:
                    continue
                
                # Get task requirements
                task_requirements = task[2]  # Assuming index 2 contains tags/requirements
                
                # Check if agent meets minimum reputation
                if self.reputation < task[4]:  # Assuming index 4 contains minReputation
                    continue
                
                # Calculate match score
                match_score = await self.evaluate_task(task[1], task_requirements)  # Assuming index 1 contains description
                
                if match_score > 0.6:  # Only consider tasks with good match
                    matching_tasks.append({
                        "task_id": task_id,
                        "description": task[1],
                        "requirements": task_requirements,
                        "reward": self.w3.from_wei(task[3], 'ether'),  # Assuming index 3 contains reward
                        "min_reputation": task[4],
                        "match_score": match_score
                    })
            
            return matching_tasks
            
        except Exception as e:
            logger.error(f"Error monitoring open tasks: {e}")
            return []

    async def run(self):
        """
        Main agent loop - monitor tasks, bid, execute, and learn
        """
        if not self.registered:
            logger.error("Agent not registered. Please register first.")
            return
        
        logger.info(f"Agent {self.agent_name} starting main loop")
        
        while True:
            try:
                # Monitor open tasks
                matching_tasks = await self.monitor_open_tasks()
                
                if matching_tasks:
                    logger.info(f"Found {len(matching_tasks)} matching tasks")
                    
                    # Sort by match score
                    matching_tasks.sort(key=lambda x: x["match_score"], reverse=True)
                    
                    # Bid on the best matching task
                    best_task = matching_tasks[0]
                    bid_result = await self.bid_for_task(
                        best_task["task_id"],
                        best_task["description"],
                        best_task["requirements"],
                        best_task["reward"],
                        best_task["min_reputation"]
                    )
                    
                    if bid_result["success"]:
                        logger.info(f"Bid placed for task {best_task['task_id']}")
                    else:
                        logger.warning(f"Failed to place bid: {bid_result['reason']}")
                
                # Check for assigned tasks
                # In a real implementation, we would listen for TaskAssigned events
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in agent loop: {e}")
                await asyncio.sleep(60)  # Wait longer after an error

async def main():
    # Example usage
    agent = LLMAgent(
        agent_name="TestAgent",
        capabilities=["research", "writing", "analysis"],
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Register on blockchain
    registered = await agent.register_on_blockchain()
    
    if registered:
        # Start agent loop
        await agent.run()
    else:
        logger.error("Failed to register agent")

if __name__ == "__main__":
    asyncio.run(main())