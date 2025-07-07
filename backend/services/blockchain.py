"""
Blockchain service for interacting with smart contracts.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("backend")

# Load environment variables
load_dotenv()

# Constants
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
AGENT_CONTRACT_ADDRESS = os.getenv("AGENT_CONTRACT_ADDRESS")
TASK_CONTRACT_ADDRESS = os.getenv("TASK_CONTRACT_ADDRESS")
LEARNING_CONTRACT_ADDRESS = os.getenv("LEARNING_CONTRACT_ADDRESS")
AGENT_REGISTRY_ADDRESS = os.getenv("AGENT_REGISTRY_ADDRESS")
TASK_MANAGER_ADDRESS = os.getenv("TASK_MANAGER_ADDRESS")
TASK_MARKETPLACE_ADDRESS = os.getenv("TASK_MARKETPLACE_ADDRESS")
BID_AUCTION_ADDRESS = os.getenv("BID_AUCTION_ADDRESS")
INCENTIVE_ENGINE_ADDRESS = os.getenv("INCENTIVE_ENGINE_ADDRESS")
MESSAGE_HUB_ADDRESS = os.getenv("MESSAGE_HUB_ADDRESS")
ACTION_LOGGER_ADDRESS = os.getenv("ACTION_LOGGER_ADDRESS")

# Check for missing contract addresses
missing_addresses = []
for name, address in [
    ("AGENT_REGISTRY_ADDRESS", AGENT_REGISTRY_ADDRESS),
    ("TASK_MANAGER_ADDRESS", TASK_MANAGER_ADDRESS),
    ("TASK_MARKETPLACE_ADDRESS", TASK_MARKETPLACE_ADDRESS),
    ("BID_AUCTION_ADDRESS", BID_AUCTION_ADDRESS),
    ("INCENTIVE_ENGINE_ADDRESS", INCENTIVE_ENGINE_ADDRESS),
    ("MESSAGE_HUB_ADDRESS", MESSAGE_HUB_ADDRESS),
    ("ACTION_LOGGER_ADDRESS", ACTION_LOGGER_ADDRESS),
]:
    if not address:
        missing_addresses.append(name)

if missing_addresses:
    logger.warning(f"Missing contract addresses: {', '.join(missing_addresses)}")

# Initialize Web3
try:
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
    # Apply middleware for compatibility with some networks
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    if w3.is_connected():
        logger.info(f"Connected to blockchain. Chain ID: {w3.eth.chain_id}")
    else:
        logger.error("Failed to connect to blockchain")
except Exception as e:
    logger.error(f"Error initializing Web3: {str(e)}")
    w3 = None

# Load contract ABIs
def load_contract_abi(contract_name: str) -> List[Dict[str, Any]]:
    """Load contract ABI from JSON file."""
    try:
        abi_path = f"contracts/abi/{contract_name}.json"
        with open(abi_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading ABI for {contract_name}: {str(e)}")
        # Return a minimal ABI for development
        return []

# Initialize contracts
contracts = {}
try:
    if w3 and w3.is_connected():
        # Agent contract
        if AGENT_REGISTRY_ADDRESS:
            agent_abi = load_contract_abi("AgentRegistry")
            contracts["agent"] = w3.eth.contract(address=AGENT_REGISTRY_ADDRESS, abi=agent_abi)
        
        # Task contract
        if TASK_MANAGER_ADDRESS:
            task_abi = load_contract_abi("TaskManager")
            contracts["task"] = w3.eth.contract(address=TASK_MANAGER_ADDRESS, abi=task_abi)
        
        # Learning contract
        if LEARNING_CONTRACT_ADDRESS:
            learning_abi = load_contract_abi("Learning")
            contracts["learning"] = w3.eth.contract(address=LEARNING_CONTRACT_ADDRESS, abi=learning_abi)
except Exception as e:
    logger.error(f"Error initializing contracts: {str(e)}")

def get_connection_status() -> Dict[str, Any]:
    """Get blockchain connection status."""
    if not w3:
        return {
            "connected": False,
            "chain_id": None,
            "provider": BLOCKCHAIN_RPC_URL,
            "contracts_configured": False
        }
    
    return {
        "connected": w3.is_connected(),
        "chain_id": w3.eth.chain_id if w3.is_connected() else None,
        "provider": BLOCKCHAIN_RPC_URL,
        "contracts_configured": bool(contracts)
    }

def register_agent(agent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new agent on the blockchain."""
    try:
        if "agent" not in contracts:
            # For development, return mock data
            return {
                "agent_id": "0x1234567890123456789012345678901234567890",
                "registration_date": "2023-08-15T14:30:00Z",
                "transaction_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"
            }
        
        # In production, we would interact with the blockchain
        # contract_call = contracts["agent"].functions.registerAgent(...)
        # tx_hash = contract_call.transact({"from": account})
        # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # For now, return mock data
        return {
            "agent_id": "0x1234567890123456789012345678901234567890",
            "registration_date": "2023-08-15T14:30:00Z",
            "transaction_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"
        }
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise

def create_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new task on the blockchain."""
    try:
        if "task" not in contracts:
            # For development, return mock data
            return {
                "task_id": "task_new",
                "transaction_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678",
                "created_at": "2023-08-15T09:15:00Z"
            }
        
        # In production, we would interact with the blockchain
        # contract_call = contracts["task"].functions.createTask(...)
        # tx_hash = contract_call.transact({"from": account})
        # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # For now, return mock data
        return {
            "task_id": "task_new",
            "transaction_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678",
            "created_at": "2023-08-15T09:15:00Z"
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise

def record_learning_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Record a learning event on the blockchain."""
    try:
        if "learning" not in contracts:
            # For development, return mock data
            return {
                "event_id": "event_new",
                "transaction_hash": "0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012",
                "timestamp": "2023-08-15T10:30:00Z"
            }
        
        # In production, we would interact with the blockchain
        # contract_call = contracts["learning"].functions.recordEvent(...)
        # tx_hash = contract_call.transact({"from": account})
        # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # For now, return mock data
        return {
            "event_id": "event_new",
            "transaction_hash": "0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012",
            "timestamp": "2023-08-15T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error recording learning event: {str(e)}")
        raise