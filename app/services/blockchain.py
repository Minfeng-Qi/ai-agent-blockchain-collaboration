"""
Service for interacting with blockchain contracts.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from app.config import WEB3_PROVIDER_URI, PRIVATE_KEY, CONTRACT_ADDRESSES, ABI_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service for interacting with blockchain contracts.
    """

    def __init__(self):
        """
        Initialize the blockchain service with Web3 provider and contracts.
        """
        # Connect to Web3 provider
        self.w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
        
        if not self.w3.is_connected():
            logger.warning(f"Failed to connect to Web3 provider at {WEB3_PROVIDER_URI}")
            self.connected = False
            return
            
        self.connected = True
        logger.info(f"Connected to blockchain at {WEB3_PROVIDER_URI}")
        
        # Set up account from private key
        if PRIVATE_KEY:
            self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
            self.address = self.account.address
            logger.info(f"Using account: {self.address}")
        else:
            self.account = None
            self.address = None
            logger.warning("No private key provided. Read-only mode enabled.")
        
        # Load contracts
        self.contracts = {}
        self._load_contracts()
    
    def _load_contracts(self) -> None:
        """
        Load contract ABIs and create contract instances.
        """
        for contract_name, contract_address in CONTRACT_ADDRESSES.items():
            if not contract_address:
                logger.warning(f"No address provided for {contract_name}")
                continue
                
            # Check if address is valid
            if not self.w3.is_address(contract_address):
                logger.warning(f"Invalid address for {contract_name}: {contract_address}")
                continue
                
            # Load ABI
            abi_path = ABI_DIR / f"{contract_name}.json"
            if not abi_path.exists():
                logger.warning(f"ABI file not found for {contract_name}: {abi_path}")
                continue
                
            try:
                with open(abi_path, 'r') as f:
                    contract_data = json.load(f)
                    
                # Get ABI from the contract data
                if isinstance(contract_data, dict) and 'abi' in contract_data:
                    abi = contract_data['abi']
                else:
                    abi = contract_data
                    
                # Create contract instance
                self.contracts[contract_name] = self.w3.eth.contract(
                    address=contract_address,
                    abi=abi
                )
                logger.info(f"Loaded contract {contract_name} at {contract_address}")
            except Exception as e:
                logger.error(f"Failed to load contract {contract_name}: {e}")
    
    def get_contract(self, name: str) -> Optional[Contract]:
        """
        Get a contract instance by name.
        
        Args:
            name: The name of the contract.
            
        Returns:
            The contract instance or None if not found.
        """
        return self.contracts.get(name)
    
    async def call_contract(
        self, 
        contract_name: str, 
        method_name: str, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Call a read-only contract method.
        
        Args:
            contract_name: The name of the contract.
            method_name: The name of the method to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.
            
        Returns:
            The result of the contract method call.
            
        Raises:
            ValueError: If the contract or method is not found.
            ContractLogicError: If the contract call fails.
        """
        contract = self.get_contract(contract_name)
        if not contract:
            raise ValueError(f"Contract not found: {contract_name}")
            
        try:
            method = getattr(contract.functions, method_name)
            if not method:
                raise ValueError(f"Method not found: {method_name}")
                
            result = method(*args).call(**kwargs)
            return result
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling contract {contract_name}.{method_name}: {e}")
            raise
    
    async def send_transaction(
        self, 
        contract_name: str, 
        method_name: str, 
        *args, 
        gas_limit: int = 2000000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a transaction to a contract method.
        
        Args:
            contract_name: The name of the contract.
            method_name: The name of the method to call.
            *args: Positional arguments for the method.
            gas_limit: Gas limit for the transaction.
            **kwargs: Keyword arguments for the method.
            
        Returns:
            Transaction receipt.
            
        Raises:
            ValueError: If the contract or method is not found, or no private key is provided.
            ContractLogicError: If the transaction fails.
        """
        if not self.account:
            raise ValueError("No private key provided. Cannot send transactions.")
            
        contract = self.get_contract(contract_name)
        if not contract:
            raise ValueError(f"Contract not found: {contract_name}")
            
        try:
            method = getattr(contract.functions, method_name)
            if not method:
                raise ValueError(f"Method not found: {method_name}")
                
            # Build transaction
            tx = method(*args).build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Transaction mined: {receipt['transactionHash'].hex()}")
            
            return {
                'transaction_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': receipt['status']
            }
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending transaction to {contract_name}.{method_name}: {e}")
            raise
    
    async def get_agent_info(self, agent_address: str) -> Dict[str, Any]:
        """
        Get information about an agent from the AgentRegistry contract.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Agent information.
        """
        try:
            agent_info = await self.call_contract(
                'AgentRegistry', 
                'getAgent', 
                agent_address
            )
            
            capabilities = await self.call_contract(
                'AgentRegistry',
                'getCapabilities',
                agent_address
            )
            
            reputation = await self.call_contract(
                'IncentiveEngine',
                'getReputation',
                agent_address
            )
            
            workload = await self.call_contract(
                'AgentRegistry',
                'getWorkload',
                agent_address
            )
            
            return {
                'address': agent_address,
                'public_key': agent_info[0],
                'capabilities': self._parse_capabilities(capabilities),
                'reputation': reputation,
                'workload': workload
            }
        except Exception as e:
            logger.error(f"Error getting agent info for {agent_address}: {e}")
            return {
                'address': agent_address,
                'error': str(e)
            }
    
    def _parse_capabilities(self, capabilities_data: tuple) -> Dict[str, int]:
        """
        Parse capabilities data from contract response.
        
        Args:
            capabilities_data: Tuple of capabilities data from contract.
            
        Returns:
            Dictionary mapping capability names to weights.
        """
        tags, weights = capabilities_data
        return {tag: weight for tag, weight in zip(tags, weights)}
    
    async def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """
        Get information about a task from the TaskManager contract.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            Task information.
        """
        try:
            task_info = await self.call_contract(
                'TaskManager',
                'getTask',
                task_id
            )
            
            return {
                'task_id': task_id,
                'creator_address': task_info[0],
                'title': task_info[1],
                'description': task_info[2],
                'status': self._parse_task_status(task_info[3]),
                'assigned_agent': task_info[4] if task_info[4] != '0x0000000000000000000000000000000000000000' else None,
                'created_at': task_info[5],
                'tags': self._parse_tags(task_info[6], task_info[7]),
                'complexity': task_info[8],
                'reward': task_info[9]
            }
        except Exception as e:
            logger.error(f"Error getting task info for {task_id}: {e}")
            return {
                'task_id': task_id,
                'error': str(e)
            }
    
    def _parse_task_status(self, status_code: int) -> str:
        """
        Parse task status code to string.
        
        Args:
            status_code: Status code from contract.
            
        Returns:
            Status string.
        """
        status_map = {
            0: 'available',
            1: 'assigned',
            2: 'completed',
            3: 'failed',
            4: 'cancelled'
        }
        return status_map.get(status_code, 'unknown')
    
    def _parse_tags(self, tags: List[str], weights: List[int]) -> Dict[str, int]:
        """
        Parse tags and weights from contract response.
        
        Args:
            tags: List of tag names.
            weights: List of tag weights.
            
        Returns:
            Dictionary mapping tag names to weights.
        """
        return {tag: weight for tag, weight in zip(tags, weights)}


# Create a singleton instance
blockchain_service = BlockchainService()