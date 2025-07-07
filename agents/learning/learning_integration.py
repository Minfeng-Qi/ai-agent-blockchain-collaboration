import os
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional
from web3 import Web3
from dotenv import load_dotenv

# 导入自定义模块
from .adaptive_bidding_strategy import AdaptiveBiddingStrategy
from .reinforcement_learning import AgentLearningSystem, ReinforcementLearning

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LearningIntegration")

# 加载环境变量
load_dotenv()

class LearningIntegration:
    """
    将自适应投标策略和强化学习模块集成到区块链系统中
    
    该类负责:
    1. 协调自适应投标和强化学习模块
    2. 与区块链系统交互，同步状态和提交更新
    3. 提供统一的学习接口和监控功能
    """
    
    def __init__(self, agent_address=None, agent_private_key=None, models_dir="./models"):
        """
        Initialize the learning integration system.
        
        Args:
            agent_address (str): The agent's Ethereum address
            agent_private_key (str): The agent's private key for signing transactions
            models_dir (str): Directory to store model files
        """
        # Load environment variables
        load_dotenv()
        
        # Set models directory
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))
        
        # Set agent details
        self.agent_address = agent_address or os.getenv('AGENT_ADDRESS')
        self.agent_private_key = agent_private_key or os.getenv('AGENT_PRIVATE_KEY')
        
        # Load contract ABIs
        self.contract_abis = self._load_contract_abis()
        
        # Initialize contracts
        self.contracts = self._initialize_contracts()
        
        try:
            # Initialize adaptive bidding strategy
            self.bidding_strategy = self._initialize_bidding_strategy()
            
            # Initialize reinforcement learning system
            capability_tags = self._get_capability_tags()
            self.learning_system = AgentLearningSystem(
                agent_id=self.agent_address,
                capability_tags=capability_tags
            )
            
            logger.info(f"LearningIntegration initialized for agent {self.agent_address}")
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            # Still create the instance but with default/mock objects
            if not hasattr(self, 'bidding_strategy'):
                self.bidding_strategy = self._create_mock_bidding_strategy()
            if not hasattr(self, 'learning_system'):
                self.learning_system = self._create_mock_learning_system()
        
        # Threading control
        self.running = False
        self.threads = []
    
    def _create_mock_bidding_strategy(self):
        """Create a mock bidding strategy when the real one can't be initialized"""
        logger.warning("Creating mock bidding strategy")
        
        class MockBiddingStrategy:
            def __init__(self, agent_address):
                self.agent_address = agent_address
                self.reputation = 50
                self.workload = 0
                self.confidence_factor = 80
                self.risk_tolerance = 50
                self.capabilities = {
                    'analysis': 50,
                    'generation': 50,
                    'classification': 50,
                    'translation': 50,
                    'summarization': 50
                }
            
            def sync_from_blockchain(self):
                return True
            
            def get_open_tasks(self):
                return []
            
            def calculate_bid_for_task(self, task_id):
                return 100
            
            def should_bid_on_task(self, task_id, bid_amount):
                return False
            
            def place_bid(self, task_id, bid_amount):
                return True
            
            def process_task_feedback(self, task_id, score, tag_scores=None):
                """Process task feedback with score parameter instead of quality_score"""
                # Update capabilities based on tag scores
                if tag_scores:
                    for tag, tag_score in tag_scores.items():
                        if tag in self.capabilities:
                            # Simple adjustment: move slightly toward the score
                            current = self.capabilities[tag]
                            adjustment = (tag_score - current) // 5  # 20% adjustment toward score
                            self.capabilities[tag] = max(0, min(100, current + adjustment))
                
                # Update reputation based on overall score
                self.reputation = max(0, min(100, self.reputation + (score - 50) // 10))
                
                return True
            
            def _update_bidding_strategy_on_chain(self):
                return True
        
        return MockBiddingStrategy(self.agent_address)
    
    def _create_mock_learning_system(self):
        """Create a mock learning system when the real one can't be initialized"""
        logger.warning("Creating mock learning system")
        
        return AgentLearningSystem(
            agent_id=self.agent_address,
            capability_tags=['analysis', 'generation', 'classification', 'translation', 'summarization']
            # initial_weights parameter is now optional with default values
        )
    
    def _load_contract_abis(self):
        """Load contract ABIs from files"""
        contract_abis = {}
        
        try:
            # Try to load ABIs from the artifacts directory
            contract_names = [
                'AgentRegistry', 'IncentiveEngine', 'BidAuction', 
                'TaskManager', 'TaskMarketplace', 'MessageHub'
            ]
            
            for contract_name in contract_names:
                try:
                    # First try to load from abis directory
                    abi_path = os.path.join(os.path.dirname(__file__), f'abis/{contract_name.lower()}_abi.json')
                    if os.path.exists(abi_path):
                        with open(abi_path, 'r') as f:
                            contract_abis[contract_name] = json.load(f)
                    else:
                        logger.warning(f"ABI file not found: {abi_path}")
                except Exception as e:
                    logger.warning(f"Could not load ABI for {contract_name}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error loading contract ABIs: {str(e)}")
            
        return contract_abis
    
    def _initialize_contracts(self):
        """Initialize contract instances"""
        contracts = {}
        
        try:
            # Get contract addresses from environment variables
            contract_addresses = {
                'AgentRegistry': os.getenv('AGENT_REGISTRY_ADDRESS'),
                'IncentiveEngine': os.getenv('INCENTIVE_ENGINE_ADDRESS'),
                'BidAuction': os.getenv('BID_AUCTION_ADDRESS'),
                'TaskManager': os.getenv('TASK_MANAGER_ADDRESS'),
                'TaskMarketplace': os.getenv('TASK_MARKETPLACE_ADDRESS'),
                'MessageHub': os.getenv('MESSAGE_HUB_ADDRESS')
            }
            
            # Initialize contract instances
            for contract_name, address in contract_addresses.items():
                if address and contract_name in self.contract_abis:
                    contracts[contract_name] = self.w3.eth.contract(
                        address=address,
                        abi=self.contract_abis[contract_name]
                    )
                    logger.info(f"Initialized {contract_name} contract at {address}")
        
        except Exception as e:
            logger.error(f"Error initializing contracts: {str(e)}")
            
        return contracts
    
    def _initialize_bidding_strategy(self):
        """Initialize the adaptive bidding strategy"""
        try:
            return AdaptiveBiddingStrategy(
                agent_address=self.agent_address,
                agent_private_key=self.agent_private_key,
                web3_provider=os.getenv('WEB3_PROVIDER_URL'),
                agent_registry_address=os.getenv('AGENT_REGISTRY_ADDRESS'),
                incentive_engine_address=os.getenv('INCENTIVE_ENGINE_ADDRESS'),
                bid_auction_address=os.getenv('BID_AUCTION_ADDRESS'),
                task_manager_address=os.getenv('TASK_MANAGER_ADDRESS'),
                agent_registry_abi_path=os.path.join(os.path.dirname(__file__), 'abis/agentregistry_abi.json'),
                incentive_engine_abi_path=os.path.join(os.path.dirname(__file__), 'abis/incentiveengine_abi.json'),
                bid_auction_abi_path=os.path.join(os.path.dirname(__file__), 'abis/bidauction_abi.json'),
                task_manager_abi_path=os.path.join(os.path.dirname(__file__), 'abis/taskmanager_abi.json')
            )
        except Exception as e:
            logger.error(f"Error initializing bidding strategy: {str(e)}")
            raise
    
    def _get_capability_tags(self):
        """Get capability tags from the blockchain or use defaults"""
        default_tags = ['analysis', 'generation', 'classification', 'translation', 'summarization']
        
        try:
            # Try to get capability tags from the blockchain
            if 'AgentRegistry' in self.contracts:
                # This is a placeholder - actual implementation would depend on the contract method
                # that returns the capability tags
                pass
            else:
                logger.warning("Using default capabilities")
            
            return default_tags
        
        except Exception as e:
            logger.warning(f"Could not get capability tags from blockchain: {str(e)}")
            return default_tags
    
    def start(self):
        """Start the learning integration system"""
        if self.running:
            logger.warning("Learning integration system is already running")
            return
        
        self.running = True
        
        # Start bidding monitoring thread
        bidding_thread = threading.Thread(target=self._run_bidding_loop)
        bidding_thread.daemon = True
        bidding_thread.start()
        self.threads.append(bidding_thread)
        
        # Start task completion monitoring thread
        task_thread = threading.Thread(target=self._run_task_completion_loop)
        task_thread.daemon = True
        task_thread.start()
        self.threads.append(task_thread)
        
        logger.info("Learning integration system started")
    
    def stop(self):
        """Stop the learning integration system"""
        self.running = False
        
        # Wait for threads to complete
        for thread in self.threads:
            thread.join(timeout=2.0)
        
        self.threads = []
        logger.info("Learning integration system stopped")
    
    def _run_bidding_loop(self):
        """Monitor for open tasks and place bids"""
        while self.running:
            try:
                # Sync agent state from blockchain
                self.bidding_strategy.sync_from_blockchain()
                
                # Get open tasks
                open_tasks = self.bidding_strategy.get_open_tasks()
                
                # Evaluate each task and place bids
                for task_id in open_tasks:
                    # Calculate bid amount
                    bid_amount = self.bidding_strategy.calculate_bid_for_task(task_id)
                    
                    # Decide whether to bid
                    if self.bidding_strategy.should_bid_on_task(task_id, bid_amount):
                        # Place bid
                        self.bidding_strategy.place_bid(task_id, bid_amount)
                
                # Sleep to prevent high CPU usage
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"Error in bidding loop: {str(e)}")
                time.sleep(10)  # Longer sleep on error
    
    def _run_task_completion_loop(self):
        """Monitor for completed tasks and process feedback"""
        while self.running:
            try:
                # Get completed tasks for this agent
                completed_tasks = self._get_completed_tasks()
                
                # Process feedback for each completed task
                for task_id, task_data in completed_tasks.items():
                    # Extract task score and feedback
                    score = task_data.get('score', 0)
                    tag_scores = task_data.get('tag_scores', {})
                    
                    # Process feedback with the bidding strategy
                    self.bidding_strategy.process_task_feedback(
                        task_id, 
                        score=score,
                        tag_scores=tag_scores
                    )
                    
                    # Process feedback with the learning system
                    task_type = task_data.get('task_type', '')
                    complexity = task_data.get('complexity', 1.0)
                    urgency = task_data.get('urgency', False)
                    
                    self.learning_system.process_task(
                        task_id=task_id,
                        task_type=task_type,
                        task_complexity=complexity,
                        score=score,
                        is_urgent=urgency
                    )
                
                # Sleep to prevent high CPU usage
                time.sleep(10)
            
            except Exception as e:
                logger.error(f"Error in task completion loop: {str(e)}")
                time.sleep(20)  # Longer sleep on error
    
    def _get_completed_tasks(self):
        """Get completed tasks from the blockchain"""
        completed_tasks = {}
        
        try:
            # This is a placeholder - actual implementation would depend on the contract method
            # that returns the completed tasks for an agent
            # Example: completed_tasks = self.contracts['TaskManager'].functions.getCompletedTasksForAgent(self.agent_address).call()
            
            # For testing purposes, we'll return an empty dict
            return completed_tasks
        
        except Exception as e:
            logger.error(f"Error getting completed tasks: {str(e)}")
            return {}
    
    def update_capability_weights(self, capability_weights):
        """
        Manually update capability weights
        
        Args:
            capability_weights (dict): Dictionary of capability weights to update
        """
        try:
            # Update in the learning system
            # Calculate adjustments based on current weights
            current_weights = self.learning_system.rl_module.capability_weights
            adjustments = {}
            
            for capability, weight in capability_weights.items():
                if capability in current_weights:
                    # Calculate the adjustment needed
                    adjustments[capability] = weight - current_weights[capability]
            
            # Apply adjustments to the learning system
            if adjustments:
                self.learning_system.rl_module.apply_adjustments(adjustments)
            
            # Update on the blockchain
            try:
                self.bidding_strategy._update_bidding_strategy_on_chain()
            except Exception as e:
                logger.warning(f"Could not update blockchain: {str(e)}")
            
            logger.info(f"Manually updated capability weights: {capability_weights}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating capability weights: {str(e)}")
            return False
    
    def generate_learning_report(self):
        """Generate a learning report"""
        try:
            # Get learning report from the learning system
            report = self.learning_system.generate_report()
            
            # Get current state from the bidding strategy
            bidding_state = {
                'agent_address': self.agent_address,
                'reputation': self.bidding_strategy.reputation,
                'workload': self.bidding_strategy.workload,
                'confidence_factor': self.bidding_strategy.confidence_factor,
                'risk_tolerance': self.bidding_strategy.risk_tolerance,
                'capabilities': self.bidding_strategy.capabilities
            }
            
            # Combine reports
            combined_report = {
                'bidding_strategy': bidding_state,
                'learning_system': report
            }
            
            return combined_report
        
        except Exception as e:
            logger.error(f"Error generating learning report: {str(e)}")
            return {'error': str(e)}
    
    def save_state(self):
        """Save the current state of the learning system"""
        try:
            # Save learning system state
            self.learning_system.save_state()
            
            logger.info("Learning integration state saved")
            return True
        
        except Exception as e:
            logger.error(f"Error saving learning integration state: {str(e)}")
            return False
    
    def load_state(self):
        """Load the saved state of the learning system"""
        try:
            # Load learning system state
            self.learning_system.load_state()
            
            logger.info("Learning integration state loaded")
            return True
        
        except Exception as e:
            logger.error(f"Error loading learning integration state: {str(e)}")
            return False

# Add a main function to demonstrate usage
def main():
    """
    Main function to demonstrate the usage of the LearningIntegration class
    """
    # Initialize the learning integration system
    integration = LearningIntegration()
    
    try:
        # Start the system
        print("Starting learning integration system...")
        integration.start()
        
        # Run for a short time
        print("System running. Press Ctrl+C to stop...")
        
        # Example of manual capability update
        print("\nUpdating capability weights...")
        integration.update_capability_weights({
            'analysis': 60,
            'generation': 55
        })
        
        # Generate and print a learning report
        print("\nGenerating learning report...")
        report = integration.generate_learning_report()
        print(json.dumps(report, indent=2))
        
        # Save the current state
        print("\nSaving system state...")
        integration.save_state()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping learning integration system...")
        integration.stop()
        print("System stopped.")
    
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        integration.stop()

if __name__ == "__main__":
    main() 