import os
import json
import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from web3 import Web3
from web3.contract import Contract
import numpy as np
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class LLMAgentLearning:
    """
    Implements the learning loop for LLM agents in a blockchain-based multi-agent system.
    This class handles the agent's learning process, including capability updates, reputation tracking,
    and bidding strategy adjustments based on feedback from the blockchain.
    """
    
    def __init__(
        self, 
        agent_address: str,
        agent_private_key: str,
        registry_contract: Contract,
        incentive_engine_contract: Contract,
        bid_auction_contract: Contract,
        task_manager_contract: Contract,
        web3_provider: Web3
    ):
        """
        Initialize the LLM agent learning module.
        
        Args:
            agent_address: The Ethereum address of the agent
            agent_private_key: The private key for signing transactions
            registry_contract: The AgentRegistry contract instance
            incentive_engine_contract: The IncentiveEngine contract instance
            bid_auction_contract: The BidAuction contract instance
            task_manager_contract: The TaskManager contract instance
            web3_provider: Web3 provider instance
        """
        self.agent_address = agent_address
        self.agent_private_key = agent_private_key
        self.registry_contract = registry_contract
        self.incentive_engine_contract = incentive_engine_contract
        self.bid_auction_contract = bid_auction_contract
        self.task_manager_contract = task_manager_contract
        self.web3 = web3_provider
        
        # Learning state
        self.capabilities = {}  # tag -> weight mapping
        self.reputation = 50    # Default starting reputation
        self.workload = 0
        self.recent_tasks = []  # List of recent task IDs
        self.recent_scores = [] # List of recent scores
        
        # Bidding strategy parameters
        self.min_utility_threshold = 30  # Minimum utility to consider bidding
        self.confidence_factor = 0.8     # How confident the agent is in its capabilities
        self.risk_tolerance = 0.5        # How much risk the agent is willing to take (0-1)
        self.workload_sensitivity = 0.2  # How sensitive the agent is to workload
        
        # Learning parameters
        self.learning_rate = 0.05        # How quickly the agent adapts its bidding strategy
        self.exploration_rate = 0.1      # Probability of exploring new tasks
        self.decay_rate = 0.99           # Rate at which exploration decays over time
        self.min_exploration_rate = 0.01 # Minimum exploration rate
        
        # Task type preferences based on past performance
        self.task_type_preferences = {}  # tag combination -> preference score
        
        # Initialize by syncing with blockchain
        self.sync_with_blockchain()
    
    def sync_with_blockchain(self) -> None:
        """
        Synchronize the agent's learning state with the blockchain.
        Fetches the latest reputation, capabilities, workload, and recent task history.
        """
        try:
            # Get learning state from AgentRegistry
            learning_state = self.registry_contract.functions.getAgentLearningState(
                self.agent_address
            ).call()
            
            # Unpack learning state
            self.reputation = learning_state[0]
            capability_tags = learning_state[1]
            capability_weights = learning_state[2]
            self.workload = learning_state[3]
            self.recent_tasks = learning_state[4]
            self.recent_scores = learning_state[5]
            
            # Update capabilities dictionary
            self.capabilities = {}
            for i in range(len(capability_tags)):
                self.capabilities[capability_tags[i]] = capability_weights[i]
            
            print(f"Agent learning state synced: reputation={self.reputation}, "
                  f"capabilities={len(self.capabilities)}, workload={self.workload}")
            
            # Update task type preferences based on recent performance
            self._update_task_type_preferences()
            
        except Exception as e:
            print(f"Error syncing with blockchain: {e}")
    
    def _update_task_type_preferences(self) -> None:
        """
        Update task type preferences based on recent task performance.
        This helps the agent learn which types of tasks it performs well on.
        """
        # Skip if no recent tasks
        if not self.recent_tasks:
            return
            
        # Get task details for recent tasks
        for i, task_id in enumerate(self.recent_tasks):
            try:
                # Get task capabilities
                task_info = self.task_manager_contract.functions.getTaskExecutionInfo(task_id).call()
                task_capabilities = task_info[2]  # capabilities array
                
                # Skip if no capabilities
                if not task_capabilities:
                    continue
                
                # Create a key for this combination of capabilities
                task_type_key = "_".join(sorted(task_capabilities))
                
                # Get the score for this task
                score = self.recent_scores[i]
                
                # Update preference for this task type
                if task_type_key in self.task_type_preferences:
                    # Exponential moving average update
                    old_pref = self.task_type_preferences[task_type_key]
                    new_pref = 0.8 * old_pref + 0.2 * score
                    self.task_type_preferences[task_type_key] = new_pref
                else:
                    # Initialize preference
                    self.task_type_preferences[task_type_key] = score
                    
            except Exception as e:
                print(f"Error updating task type preferences for task {task_id}: {e}")
    
    def calculate_bid_utility(self, task_id: str, task_capabilities: List[str], reward: int) -> int:
        """
        Calculate the utility of a task for bidding purposes.
        This is the agent's internal utility calculation, which may differ from the blockchain's.
        
        Args:
            task_id: The ID of the task
            task_capabilities: List of capabilities required for the task
            reward: The reward offered for the task
            
        Returns:
            The calculated utility score (0-100)
        """
        # Base utility from blockchain
        try:
            blockchain_utility = self.bid_auction_contract.functions.calculateAgentUtility(
                task_id, self.agent_address
            ).call()
        except Exception as e:
            print(f"Error getting blockchain utility: {e}")
            blockchain_utility = 0
        
        # Calculate capability match score
        capability_match = 0
        total_weight = 0
        
        for cap in task_capabilities:
            if cap in self.capabilities:
                capability_match += self.capabilities[cap]
                total_weight += 100
        
        # Normalize capability match score
        if total_weight > 0:
            capability_match = capability_match * 100 / total_weight
        else:
            capability_match = 0
        
        # Calculate workload penalty
        workload_penalty = self.workload * self.workload_sensitivity * 10
        
        # Calculate task type preference boost
        task_type_key = "_".join(sorted(task_capabilities))
        type_preference_boost = 0
        
        if task_type_key in self.task_type_preferences:
            preference_score = self.task_type_preferences[task_type_key]
            # Boost based on past performance on similar tasks
            type_preference_boost = (preference_score - 50) * 0.2  # -10 to +10 boost
        
        # Combine factors for final utility
        adjusted_utility = (
            blockchain_utility * 0.7 +  # 70% weight to blockchain utility
            capability_match * 0.2 +    # 20% weight to capability match
            type_preference_boost       # Boost/penalty based on past performance
        ) - workload_penalty            # Penalty for current workload
        
        # Apply confidence factor
        adjusted_utility = adjusted_utility * self.confidence_factor
        
        # Add exploration factor if exploration rate is triggered
        if random.random() < self.exploration_rate:
            # Add some randomness for exploration
            exploration_boost = random.uniform(-10, 20)  # More bias toward positive exploration
            adjusted_utility += exploration_boost
            print(f"Exploration triggered: {exploration_boost:+.2f} utility adjustment")
        
        # Ensure utility is in valid range
        adjusted_utility = max(0, min(100, adjusted_utility))
        
        print(f"Utility calculation: blockchain={blockchain_utility}, "
              f"capability_match={capability_match:.2f}, workload_penalty={workload_penalty:.2f}, "
              f"type_boost={type_preference_boost:.2f}, final={adjusted_utility:.2f}")
        
        return int(adjusted_utility)
    
    def adjust_bidding_strategy(self) -> None:
        """
        Adjust the agent's bidding strategy based on past performance.
        This function is called periodically to update the agent's bidding parameters.
        """
        # Skip if no recent tasks
        if not self.recent_scores:
            return
            
        # Calculate average recent score
        avg_score = sum(self.recent_scores) / len(self.recent_scores)
        
        # Adjust confidence factor based on recent performance
        if avg_score > 70:
            # Good performance, increase confidence
            self.confidence_factor = min(1.0, self.confidence_factor + self.learning_rate)
        elif avg_score < 50:
            # Poor performance, decrease confidence
            self.confidence_factor = max(0.5, self.confidence_factor - self.learning_rate)
        
        # Adjust risk tolerance based on reputation
        if self.reputation > 70:
            # High reputation, can take more risks
            self.risk_tolerance = min(0.8, self.risk_tolerance + self.learning_rate * 0.5)
        elif self.reputation < 40:
            # Low reputation, be more conservative
            self.risk_tolerance = max(0.2, self.risk_tolerance - self.learning_rate * 0.5)
        
        # Adjust workload sensitivity based on current workload
        if self.workload > 5:
            # High workload, be more sensitive
            self.workload_sensitivity = min(0.5, self.workload_sensitivity + self.learning_rate)
        elif self.workload < 2:
            # Low workload, be less sensitive
            self.workload_sensitivity = max(0.1, self.workload_sensitivity - self.learning_rate)
        
        # Decay exploration rate over time, but maintain minimum
        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate * self.decay_rate
        )
        
        print(f"Adjusted bidding strategy: confidence={self.confidence_factor:.2f}, "
              f"risk_tolerance={self.risk_tolerance:.2f}, "
              f"workload_sensitivity={self.workload_sensitivity:.2f}, "
              f"exploration_rate={self.exploration_rate:.2f}")
    
    def decide_bid_amount(self, task_id: str, utility: int, min_bid: int, max_bid: int) -> int:
        """
        Decide how much to bid for a task based on utility and strategy.
        
        Args:
            task_id: The ID of the task
            utility: The calculated utility of the task
            min_bid: The minimum possible bid
            max_bid: The maximum possible bid
            
        Returns:
            The bid amount
        """
        # Calculate bid range
        bid_range = max_bid - min_bid
        
        # Base bid calculation - higher utility means willing to bid lower
        # (more competitive) to win the task
        utility_factor = 1 - (utility / 100)  # Invert utility (0-1)
        
        # Apply risk tolerance - higher risk tolerance means more aggressive bidding
        risk_factor = 1 - self.risk_tolerance
        
        # Combine factors
        bid_position = utility_factor * risk_factor
        
        # Calculate bid amount within range
        bid_amount = min_bid + int(bid_range * bid_position)
        
        # Add small random variation for tie-breaking
        variation = int(bid_range * 0.05)  # 5% variation
        if variation > 0:
            bid_amount += random.randint(-variation, variation)
        
        # Ensure bid is within valid range
        bid_amount = max(min_bid, min(max_bid, bid_amount))
        
        print(f"Bid decision: utility={utility}, utility_factor={utility_factor:.2f}, "
              f"risk_factor={risk_factor:.2f}, bid_position={bid_position:.2f}, "
              f"bid_amount={bid_amount}")
        
        return bid_amount
    
    def should_bid_on_task(self, task_id: str, task_capabilities: List[str], min_reputation: int) -> bool:
        """
        Decide whether the agent should bid on a task.
        
        Args:
            task_id: The ID of the task
            task_capabilities: List of capabilities required for the task
            min_reputation: Minimum reputation required for the task
            
        Returns:
            True if the agent should bid, False otherwise
        """
        # Check if agent meets minimum reputation requirement
        if self.reputation < min_reputation:
            print(f"Reputation too low: {self.reputation} < {min_reputation}")
            return False
        
        # Calculate utility
        reward = 100  # Default reward for utility calculation
        utility = self.calculate_bid_utility(task_id, task_capabilities, reward)
        
        # Check if utility meets minimum threshold
        if utility < self.min_utility_threshold:
            print(f"Utility too low: {utility} < {self.min_utility_threshold}")
            return False
        
        # Check workload capacity
        if self.workload >= 10:  # Hard cap on workload
            print(f"Workload too high: {self.workload} >= 10")
            return False
        
        # Check task type preferences
        task_type_key = "_".join(sorted(task_capabilities))
        if task_type_key in self.task_type_preferences:
            preference = self.task_type_preferences[task_type_key]
            if preference < 40 and random.random() > self.exploration_rate:
                print(f"Low preference for task type: {preference} < 40")
                return False
        
        # Apply exploration rate
        if random.random() < self.exploration_rate:
            print("Exploration triggered: bidding despite parameters")
            return True
            
        return True
    
    def process_task_feedback(self, task_id: str, quality: int, tag_scores: Dict[str, int]) -> None:
        """
        Process feedback from a completed task to update the agent's learning state.
        
        Args:
            task_id: The ID of the completed task
            quality: The overall quality score
            tag_scores: Dictionary mapping capability tags to scores
        """
        print(f"Processing feedback for task {task_id}: quality={quality}, tag_scores={tag_scores}")
        
        # Update local capabilities based on tag scores
        for tag, score in tag_scores.items():
            if tag in self.capabilities:
                old_weight = self.capabilities[tag]
                # Apply EMA update locally
                mu = 0.7  # Same as contract
                new_weight = (mu * old_weight + (100 - mu) * score) / 100
                self.capabilities[tag] = new_weight
                print(f"Updated capability {tag}: {old_weight} -> {new_weight:.2f}")
        
        # Adjust bidding strategy based on new feedback
        self.adjust_bidding_strategy()
        
        # Sync with blockchain to get latest state
        self.sync_with_blockchain()
    
    def place_bid(self, task_id: str, utility: int, bid_amount: int) -> bool:
        """
        Place a bid on a task.
        
        Args:
            task_id: The ID of the task
            utility: The utility score to report
            bid_amount: The amount to bid
            
        Returns:
            True if bid was placed successfully, False otherwise
        """
        try:
            # Create transaction
            nonce = self.web3.eth.get_transaction_count(self.agent_address)
            
            # Simple signature for demo purposes
            signature = "0x"  # In production, would sign the bid data
            
            # Build transaction
            tx = self.bid_auction_contract.functions.placeBid(
                task_id,
                utility,
                bid_amount,
                signature,
                nonce
            ).build_transaction({
                'from': self.agent_address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.agent_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"Bid placed successfully: task={task_id}, utility={utility}, amount={bid_amount}")
                return True
            else:
                print(f"Bid failed: transaction reverted")
                return False
                
        except Exception as e:
            print(f"Error placing bid: {e}")
            return False
    
    def monitor_and_learn(self, polling_interval: int = 60) -> None:
        """
        Continuously monitor the blockchain for new tasks and learning opportunities.
        
        Args:
            polling_interval: Time between polling cycles in seconds
        """
        print(f"Starting monitoring and learning loop with interval {polling_interval}s")
        
        last_sync_time = 0
        
        while True:
            try:
                # Sync with blockchain periodically
                current_time = time.time()
                if current_time - last_sync_time > 300:  # Every 5 minutes
                    self.sync_with_blockchain()
                    last_sync_time = current_time
                
                # Look for open tasks
                open_task_ids = self.task_manager_contract.functions.getTasksByStatus(1).call()  # Open status
                
                for task_id in open_task_ids:
                    # Check if bidding is open
                    bidding_deadline = self.bid_auction_contract.functions.biddingDeadlines(task_id).call()
                    
                    if bidding_deadline > 0 and bidding_deadline > current_time:
                        # Check if we've already bid
                        already_bid = self.bid_auction_contract.functions.hasAgentBid(task_id, self.agent_address).call()
                        
                        if not already_bid:
                            # Get task details
                            task_info = self.task_manager_contract.functions.getTaskExecutionInfo(task_id).call()
                            task_capabilities = task_info[2]  # capabilities array
                            min_reputation = self.task_manager_contract.functions.tasks(task_id).call()[4]  # minReputation
                            reward = task_info[1]  # reward
                            
                            # Decide whether to bid
                            if self.should_bid_on_task(task_id, task_capabilities, min_reputation):
                                # Calculate utility
                                utility = self.calculate_bid_utility(task_id, task_capabilities, reward)
                                
                                # Decide bid amount
                                min_bid = 10  # Minimum bid amount
                                max_bid = 100  # Maximum bid amount
                                bid_amount = self.decide_bid_amount(task_id, utility, min_bid, max_bid)
                                
                                # Place bid
                                self.place_bid(task_id, utility, bid_amount)
                
                # Check for completed tasks to learn from
                agent_tasks = self.task_manager_contract.functions.getAgentTasks(self.agent_address).call()
                
                for task_id in agent_tasks:
                    task = self.task_manager_contract.functions.tasks(task_id).call()
                    
                    # Check if task is completed and evaluated
                    if task[7] == 4 and task[12]:  # Completed status and isEvaluated
                        # Get evaluation details
                        eval_data = self.incentive_engine_contract.functions.getTaskEvaluation(task_id).call()
                        quality = eval_data[0]
                        tags = eval_data[3]
                        tag_scores = eval_data[4]
                        
                        # Process feedback
                        tag_score_dict = {tags[i]: tag_scores[i] for i in range(len(tags))}
                        self.process_task_feedback(task_id, quality, tag_score_dict)
                
                # Adjust bidding strategy periodically
                self.adjust_bidding_strategy()
                
                # Sleep before next cycle
                time.sleep(polling_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(polling_interval)


# Example usage
if __name__ == "__main__":
    # Load configuration
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    
    # Connect to blockchain
    web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Load contract ABIs
    def load_abi(contract_name):
        with open(f"../artifacts/contracts/{contract_name}.sol/{contract_name}.json") as f:
            contract_json = json.load(f)
            return contract_json["abi"]
    
    registry_abi = load_abi("AgentRegistry")
    incentive_engine_abi = load_abi("IncentiveEngine")
    bid_auction_abi = load_abi("BidAuction")
    task_manager_abi = load_abi("TaskManager")
    
    # Contract addresses (replace with actual deployed addresses)
    registry_address = os.getenv("REGISTRY_ADDRESS")
    incentive_engine_address = os.getenv("INCENTIVE_ENGINE_ADDRESS")
    bid_auction_address = os.getenv("BID_AUCTION_ADDRESS")
    task_manager_address = os.getenv("TASK_MANAGER_ADDRESS")
    
    # Create contract instances
    registry_contract = web3.eth.contract(address=registry_address, abi=registry_abi)
    incentive_engine_contract = web3.eth.contract(address=incentive_engine_address, abi=incentive_engine_abi)
    bid_auction_contract = web3.eth.contract(address=bid_auction_address, abi=bid_auction_abi)
    task_manager_contract = web3.eth.contract(address=task_manager_address, abi=task_manager_abi)
    
    # Agent configuration
    agent_address = os.getenv("AGENT_ADDRESS")
    agent_private_key = os.getenv("AGENT_PRIVATE_KEY")
    
    # Create agent learning module
    agent_learning = LLMAgentLearning(
        agent_address=agent_address,
        agent_private_key=agent_private_key,
        registry_contract=registry_contract,
        incentive_engine_contract=incentive_engine_contract,
        bid_auction_contract=bid_auction_contract,
        task_manager_contract=task_manager_contract,
        web3_provider=web3
    )
    
    # Start monitoring and learning
    agent_learning.monitor_and_learn(polling_interval=30) 