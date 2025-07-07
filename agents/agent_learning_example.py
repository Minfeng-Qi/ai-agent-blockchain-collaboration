"""
Example script demonstrating the agent learning loop.
This script shows how to set up and run the agent learning module.
"""

import os
import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# Import our agent learning module
from agent_learning import LLMAgentLearning
from agent_config import AgentLearningConfig

# Load environment variables
load_dotenv()

def main():
    """
    Main function to demonstrate the agent learning loop.
    """
    print("Starting LLM Agent Learning Example")
    
    # Connect to blockchain
    web3_provider_uri = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
    print(f"Connecting to blockchain at {web3_provider_uri}")
    
    web3 = Web3(Web3.HTTPProvider(web3_provider_uri))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    if not web3.is_connected():
        print("Failed to connect to Web3 provider")
        return
    
    print(f"Connected to blockchain. Network ID: {web3.eth.chain_id}")
    
    # Load contract addresses
    registry_address = os.getenv("REGISTRY_ADDRESS")
    incentive_engine_address = os.getenv("INCENTIVE_ENGINE_ADDRESS")
    bid_auction_address = os.getenv("BID_AUCTION_ADDRESS")
    task_manager_address = os.getenv("TASK_MANAGER_ADDRESS")
    
    if not all([registry_address, incentive_engine_address, bid_auction_address, task_manager_address]):
        print("Missing contract addresses in environment variables")
        return
    
    # Load contract ABIs
    try:
        def load_abi(contract_name):
            abi_path = f"../artifacts/contracts/{contract_name}.sol/{contract_name}.json"
            if not os.path.exists(abi_path):
                print(f"ABI file not found: {abi_path}")
                return None
                
            with open(abi_path) as f:
                contract_json = json.load(f)
                return contract_json["abi"]
        
        registry_abi = load_abi("AgentRegistry")
        incentive_engine_abi = load_abi("IncentiveEngine")
        bid_auction_abi = load_abi("BidAuction")
        task_manager_abi = load_abi("TaskManager")
        
        if not all([registry_abi, incentive_engine_abi, bid_auction_abi, task_manager_abi]):
            print("Failed to load one or more contract ABIs")
            return
            
    except Exception as e:
        print(f"Error loading contract ABIs: {e}")
        return
    
    # Create contract instances
    registry_contract = web3.eth.contract(address=registry_address, abi=registry_abi)
    incentive_engine_contract = web3.eth.contract(address=incentive_engine_address, abi=incentive_engine_abi)
    bid_auction_contract = web3.eth.contract(address=bid_auction_address, abi=bid_auction_abi)
    task_manager_contract = web3.eth.contract(address=task_manager_address, abi=task_manager_abi)
    
    # Agent configuration
    agent_address = os.getenv("AGENT_ADDRESS")
    agent_private_key = os.getenv("AGENT_PRIVATE_KEY")
    
    if not agent_address or not agent_private_key:
        print("Agent address or private key not set in environment variables")
        return
    
    print(f"Setting up agent with address: {agent_address}")
    
    # Choose an agent profile
    agent_profile = os.getenv("AGENT_PROFILE", "balanced")
    config = AgentLearningConfig.get_profile(agent_profile)
    print(f"Using agent profile: {agent_profile}")
    
    # Create agent learning module with the selected profile
    agent_learning = LLMAgentLearning(
        agent_address=agent_address,
        agent_private_key=agent_private_key,
        registry_contract=registry_contract,
        incentive_engine_contract=incentive_engine_contract,
        bid_auction_contract=bid_auction_contract,
        task_manager_contract=task_manager_contract,
        web3_provider=web3
    )
    
    # Apply configuration from profile
    agent_learning.learning_rate = config["learning_rate"]
    agent_learning.exploration_rate = config["exploration_rate"]
    agent_learning.decay_rate = config["decay_rate"]
    agent_learning.min_exploration_rate = config["min_exploration_rate"]
    agent_learning.min_utility_threshold = config["min_utility_threshold"]
    agent_learning.confidence_factor = config["confidence_factor"]
    agent_learning.risk_tolerance = config["risk_tolerance"]
    agent_learning.workload_sensitivity = config["workload_sensitivity"]
    
    # Print initial agent state
    print("\nInitial agent state:")
    print(f"Reputation: {agent_learning.reputation}")
    print(f"Workload: {agent_learning.workload}")
    print(f"Capabilities: {len(agent_learning.capabilities)}")
    print(f"Learning rate: {agent_learning.learning_rate}")
    print(f"Exploration rate: {agent_learning.exploration_rate}")
    print(f"Risk tolerance: {agent_learning.risk_tolerance}")
    
    # Sync with blockchain to get latest state
    print("\nSyncing with blockchain...")
    agent_learning.sync_with_blockchain()
    
    # Print updated agent state
    print("\nUpdated agent state after sync:")
    print(f"Reputation: {agent_learning.reputation}")
    print(f"Workload: {agent_learning.workload}")
    print(f"Capabilities: {len(agent_learning.capabilities)}")
    if agent_learning.capabilities:
        print("Top capabilities:")
        sorted_caps = sorted(agent_learning.capabilities.items(), key=lambda x: x[1], reverse=True)
        for cap, weight in sorted_caps[:5]:
            print(f"  - {cap}: {weight}")
    
    # Demonstrate utility calculation for a sample task
    print("\nDemonstrating utility calculation for a sample task:")
    sample_task_id = "0"  # Sample task ID
    sample_capabilities = ["coding", "writing", "research"]
    sample_reward = 100
    
    utility = agent_learning.calculate_bid_utility(
        sample_task_id, 
        sample_capabilities, 
        sample_reward
    )
    
    print(f"Calculated utility for sample task: {utility}")
    
    # Demonstrate bid decision
    should_bid = agent_learning.should_bid_on_task(
        sample_task_id,
        sample_capabilities,
        50  # min reputation
    )
    
    print(f"Should bid on sample task: {should_bid}")
    
    if should_bid:
        min_bid = 10
        max_bid = 100
        bid_amount = agent_learning.decide_bid_amount(
            sample_task_id,
            utility,
            min_bid,
            max_bid
        )
        print(f"Decided bid amount: {bid_amount}")
    
    # Demonstrate learning from task feedback
    print("\nDemonstrating learning from task feedback:")
    sample_quality = 75
    sample_tag_scores = {
        "coding": 80,
        "writing": 70,
        "research": 75
    }
    
    print(f"Before learning update:")
    for tag in sample_tag_scores:
        if tag in agent_learning.capabilities:
            print(f"  - {tag}: {agent_learning.capabilities[tag]}")
    
    # Process feedback
    agent_learning.process_task_feedback(
        sample_task_id,
        sample_quality,
        sample_tag_scores
    )
    
    print(f"After learning update:")
    for tag in sample_tag_scores:
        if tag in agent_learning.capabilities:
            print(f"  - {tag}: {agent_learning.capabilities[tag]}")
    
    # Start monitoring and learning (with short timeout for demo)
    print("\nStarting monitoring and learning loop...")
    print("Press Ctrl+C to stop after a few cycles")
    
    try:
        # For demonstration, we'll just run a few cycles
        demo_cycles = 3
        for i in range(demo_cycles):
            print(f"\nDemo cycle {i+1}/{demo_cycles}:")
            
            # Look for open tasks
            try:
                open_task_ids = task_manager_contract.functions.getTasksByStatus(1).call()  # Open status
                print(f"Found {len(open_task_ids)} open tasks")
                
                # Process first open task if available
                if open_task_ids:
                    task_id = open_task_ids[0]
                    print(f"Processing task {task_id}")
                    
                    # Get task details
                    task_info = task_manager_contract.functions.getTaskExecutionInfo(task_id).call()
                    task_capabilities = task_info[2]  # capabilities array
                    
                    print(f"Task capabilities: {task_capabilities}")
                    
                    # Calculate utility
                    utility = agent_learning.calculate_bid_utility(task_id, task_capabilities, 100)
                    print(f"Calculated utility: {utility}")
                    
                    # Adjust bidding strategy
                    agent_learning.adjust_bidding_strategy()
                    print(f"Adjusted bidding strategy:")
                    print(f"  - Confidence: {agent_learning.confidence_factor:.2f}")
                    print(f"  - Risk tolerance: {agent_learning.risk_tolerance:.2f}")
                    print(f"  - Workload sensitivity: {agent_learning.workload_sensitivity:.2f}")
            except Exception as e:
                print(f"Error processing tasks: {e}")
            
            # Wait between cycles
            time.sleep(2)
            
        print("\nDemo completed")
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    
    print("\nLLM Agent Learning Example completed")


if __name__ == "__main__":
    main() 