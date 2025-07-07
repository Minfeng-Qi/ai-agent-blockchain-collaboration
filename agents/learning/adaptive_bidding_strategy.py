import os
import json
import time
import math
import random
import numpy as np
from web3 import Web3
from typing import Dict, List, Tuple, Any, Optional
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdaptiveBiddingStrategy")

# 加载环境变量
load_dotenv()

class AdaptiveBiddingStrategy:
    """
    实现代理的自适应投标策略和能力向量演化
    
    该类负责:
    1. 根据历史任务表现调整代理的能力向量
    2. 根据声誉和任务结果优化投标策略
    3. 提供链上可验证的学习机制
    """
    
    def __init__(
        self,
        agent_address: str,
        agent_private_key: str,
        web3_provider: str,
        agent_registry_address: str,
        incentive_engine_address: str,
        bid_auction_address: str,
        task_manager_address: str,
        agent_registry_abi_path: str,
        incentive_engine_abi_path: str,
        bid_auction_abi_path: str,
        task_manager_abi_path: str
    ):
        """
        初始化自适应投标策略
        
        Args:
            agent_address: 代理的以太坊地址
            agent_private_key: 代理的私钥
            web3_provider: Web3提供者URL
            agent_registry_address: AgentRegistry合约地址
            incentive_engine_address: IncentiveEngine合约地址
            bid_auction_address: BidAuction合约地址
            task_manager_address: TaskManager合约地址
            agent_registry_abi_path: AgentRegistry ABI文件路径
            incentive_engine_abi_path: IncentiveEngine ABI文件路径
            bid_auction_abi_path: BidAuction ABI文件路径
            task_manager_abi_path: TaskManager ABI文件路径
        """
        # 初始化Web3连接
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.agent_address = Web3.to_checksum_address(agent_address)
        self.agent_private_key = agent_private_key
        
        # 加载合约ABIs
        with open(agent_registry_abi_path, 'r') as f:
            agent_registry_abi = json.load(f)
        with open(incentive_engine_abi_path, 'r') as f:
            incentive_engine_abi = json.load(f)
        with open(bid_auction_abi_path, 'r') as f:
            bid_auction_abi = json.load(f)
        with open(task_manager_abi_path, 'r') as f:
            task_manager_abi = json.load(f)
        
        # 初始化合约
        self.agent_registry = self.web3.eth.contract(
            address=Web3.to_checksum_address(agent_registry_address),
            abi=agent_registry_abi
        )
        self.incentive_engine = self.web3.eth.contract(
            address=Web3.to_checksum_address(incentive_engine_address),
            abi=incentive_engine_abi
        )
        self.bid_auction = self.web3.eth.contract(
            address=Web3.to_checksum_address(bid_auction_address),
            abi=bid_auction_abi
        )
        self.task_manager = self.web3.eth.contract(
            address=Web3.to_checksum_address(task_manager_address),
            abi=task_manager_abi
        )
        
        # 代理状态
        self.capabilities = {}  # 能力标签 -> 权重映射
        self.reputation = 50    # 默认声誉值
        self.workload = 0       # 当前工作负载
        self.recent_tasks = []  # 最近任务列表
        self.recent_scores = [] # 最近得分列表
        
        # 投标策略参数
        self.confidence_factor = 80  # 信心因子 (0-100)
        self.risk_tolerance = 50     # 风险承受度 (0-100)
        
        # 学习参数
        self.learning_rate = 0.05    # 学习率
        self.adaptation_factor = 0.5 # 适应因子
        self.exploration_rate = 0.1  # 探索率
        
        # 任务类型偏好 (根据过去表现)
        self.task_type_preferences = {}  # 任务类型组合 -> 偏好分数
        
        # 从区块链同步初始状态
        self.sync_from_blockchain()
        logger.info(f"AdaptiveBiddingStrategy initialized for agent {agent_address}")
    
    def sync_from_blockchain(self) -> None:
        """从区块链同步代理状态"""
        try:
            # 获取学习状态
            learning_state = self.agent_registry.functions.getAgentLearningState(
                self.agent_address
            ).call()
            
            # 解析能力向量
            capability_tags = learning_state[1]  # capabilityTags
            capability_weights = learning_state[2]  # capabilityWeights
            
            # 更新本地状态
            self.capabilities = {
                tag: int(weight) for tag, weight in zip(capability_tags, capability_weights)
            }
            self.reputation = int(learning_state[0])  # reputation
            self.workload = int(learning_state[3])    # workload
            
            # 获取最近任务和分数
            self.recent_tasks = learning_state[4]  # recentTaskIds
            self.recent_scores = [int(score) for score in learning_state[5]]  # recentScores
            
            # 获取投标策略
            bidding_strategy = self.agent_registry.functions.getAgentBiddingStrategy(
                self.agent_address
            ).call()
            
            self.confidence_factor = int(bidding_strategy[0])
            self.risk_tolerance = int(bidding_strategy[1])
            
            # 更新任务类型偏好
            self._update_task_type_preferences()
            
            logger.info(f"Synced agent state from blockchain: {len(capability_tags)} capabilities, "
                       f"reputation: {self.reputation}, workload: {self.workload}")
        except Exception as e:
            logger.error(f"Error syncing from blockchain: {e}")
    
    def _update_task_type_preferences(self) -> None:
        """根据最近任务表现更新任务类型偏好"""
        if not self.recent_tasks:
            return
            
        # 获取最近任务的详细信息
        for i, task_id in enumerate(self.recent_tasks):
            try:
                # 获取任务能力要求
                task_info = self.task_manager.functions.getTaskExecutionInfo(task_id).call()
                task_capabilities = task_info[2]  # capabilities数组
                
                if not task_capabilities:
                    continue
                
                # 为这个能力组合创建一个键
                task_type_key = "_".join(sorted(task_capabilities))
                
                # 获取这个任务的得分
                score = self.recent_scores[i] if i < len(self.recent_scores) else 0
                
                # 更新对这个任务类型的偏好
                if task_type_key in self.task_type_preferences:
                    # 指数移动平均更新
                    old_pref = self.task_type_preferences[task_type_key]
                    new_pref = 0.8 * old_pref + 0.2 * score
                    self.task_type_preferences[task_type_key] = new_pref
                else:
                    # 初始化偏好
                    self.task_type_preferences[task_type_key] = score
                    
            except Exception as e:
                logger.error(f"Error updating task type preferences for task {task_id}: {e}")
    
    def calculate_bid_for_task(self, task_id: str, task_reward: int) -> Tuple[int, int]:
        """
        为特定任务计算投标金额和效用分数
        
        Args:
            task_id: 任务ID
            task_reward: 任务奖励
            
        Returns:
            Tuple[int, int]: (投标金额, 效用分数)
        """
        try:
            # 获取任务信息
            task_info = self.task_manager.functions.getTaskExecutionInfo(
                Web3.to_bytes(hexstr=task_id)
            ).call()
            
            # 解析任务能力要求
            required_capabilities = task_info[2]  # capabilities数组
            
            # 计算区块链上的效用分数
            blockchain_utility = self.incentive_engine.functions.calculateUtility(
                self.agent_address,
                required_capabilities,
                task_reward,
                self.workload
            ).call()
            
            # 计算任务类型偏好加成
            task_type_key = "_".join(sorted(required_capabilities))
            type_preference = self.task_type_preferences.get(task_type_key, 50)  # 默认中等偏好
            
            # 计算最终效用分数 (区块链效用 * 0.7 + 类型偏好 * 0.3)
            utility_score = int(blockchain_utility * 0.7 + type_preference * 0.3)
            
            # 基于效用分数和投标策略计算投标金额
            bid_amount = self._calculate_bid_amount(utility_score, task_reward)
            
            logger.info(f"Calculated bid for task {task_id}: utility={utility_score}, bid={bid_amount}")
            return bid_amount, utility_score
            
        except Exception as e:
            logger.error(f"Error calculating bid for task {task_id}: {e}")
            return 0, 0
    
    def _calculate_bid_amount(self, utility_score: int, task_reward: int) -> int:
        """
        根据效用分数和投标策略计算投标金额
        
        Args:
            utility_score: 效用分数 (0-100)
            task_reward: 任务奖励
            
        Returns:
            int: 投标金额
        """
        # 效用因子 (效用越高，投标越低)
        utility_factor = 1 - (utility_score / 100) * (self.confidence_factor / 100)
        
        # 风险因子 (风险承受度越高，投标越激进)
        risk_factor = 1 - (self.risk_tolerance / 100)
        
        # 基础投标金额 (任务奖励的一部分)
        base_bid = task_reward * 0.7
        
        # 应用效用和风险因子
        adjusted_bid = base_bid * utility_factor * risk_factor
        
        # 添加随机变化以打破平局 (±5%)
        random_factor = 1 + (random.random() * 0.1 - 0.05)
        final_bid = int(adjusted_bid * random_factor)
        
        # 确保投标金额在合理范围内
        final_bid = max(1, min(final_bid, task_reward))
        
        return final_bid
    
    def should_bid_on_task(self, task_id: str) -> bool:
        """
        决定是否对任务进行投标
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否应该投标
        """
        try:
            # 获取任务信息
            task_info = self.task_manager.functions.getTaskExecutionInfo(
                Web3.to_bytes(hexstr=task_id)
            ).call()
            
            # 解析任务能力要求
            required_capabilities = task_info[2]  # capabilities数组
            
            # 检查工作负载容量
            if self.workload >= 10:  # 最大工作负载
                logger.info(f"Not bidding on task {task_id}: workload too high ({self.workload})")
                return False
            
            # 检查声誉要求
            min_reputation = 30  # 最低声誉要求
            if self.reputation < min_reputation:
                logger.info(f"Not bidding on task {task_id}: reputation too low ({self.reputation})")
                return False
            
            # 计算能力匹配度
            capability_match = self._calculate_capability_match(required_capabilities)
            
            # 如果能力匹配度太低，不投标
            if capability_match < 30:  # 最低能力匹配度
                logger.info(f"Not bidding on task {task_id}: capability match too low ({capability_match})")
                return False
            
            # 检查任务类型偏好
            task_type_key = "_".join(sorted(required_capabilities))
            type_preference = self.task_type_preferences.get(task_type_key, 50)
            
            # 如果偏好太低，可能不投标
            if type_preference < 30 and random.random() > 0.3:  # 30%的几率仍然投标
                logger.info(f"Not bidding on task {task_id}: low preference for task type ({type_preference})")
                return False
            
            # 探索机制：有一定几率投标不熟悉的任务类型
            if random.random() < self.exploration_rate:
                logger.info(f"Bidding on task {task_id} for exploration")
                return True
            
            # 默认投标
            return True
            
        except Exception as e:
            logger.error(f"Error deciding whether to bid on task {task_id}: {e}")
            return False
    
    def _calculate_capability_match(self, required_capabilities: List[str]) -> int:
        """
        计算代理能力与任务要求的匹配度
        
        Args:
            required_capabilities: 任务要求的能力列表
            
        Returns:
            int: 匹配度分数 (0-100)
        """
        if not required_capabilities:
            return 100  # 没有要求的能力，完全匹配
            
        if not self.capabilities:
            return 0  # 代理没有能力，完全不匹配
        
        total_match = 0
        for capability in required_capabilities:
            weight = self.capabilities.get(capability, 0)
            total_match += weight
        
        # 计算平均匹配度
        avg_match = total_match / len(required_capabilities)
        return int(avg_match)
    
    def place_bid(self, task_id: str, bid_amount: int, utility_score: int) -> bool:
        """
        在区块链上为任务下投标
        
        Args:
            task_id: 任务ID
            bid_amount: 投标金额
            utility_score: 效用分数
            
        Returns:
            bool: 投标是否成功
        """
        try:
            # 准备交易
            task_id_bytes = Web3.to_bytes(hexstr=task_id)
            
            # 获取交易参数
            nonce = self.web3.eth.get_transaction_count(self.agent_address)
            gas_price = self.web3.eth.gas_price
            
            # 构建交易
            tx = self.bid_auction.functions.placeBid(
                task_id_bytes,
                bid_amount
            ).build_transaction({
                'from': self.agent_address,
                'gas': 2000000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            
            # 签名并发送交易
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.agent_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待交易确认
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully placed bid on task {task_id}: amount={bid_amount}, utility={utility_score}")
                return True
            else:
                logger.error(f"Bid transaction failed for task {task_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error placing bid on task {task_id}: {e}")
            return False
    
    def process_task_feedback(self, task_id: str, quality: int, tag_scores: Dict[str, int]) -> None:
        """
        处理任务完成后的反馈，更新学习状态
        
        Args:
            task_id: 任务ID
            quality: 整体质量分数
            tag_scores: 各能力标签的分数
        """
        logger.info(f"Processing feedback for task {task_id}: quality={quality}, tag_scores={tag_scores}")
        
        # 更新本地能力权重
        for tag, score in tag_scores.items():
            if tag in self.capabilities:
                old_weight = self.capabilities[tag]
                # 应用EMA更新
                mu = 0.7  # 与合约相同
                new_weight = (mu * old_weight + (100 - mu) * score) / 100
                self.capabilities[tag] = int(new_weight)
                logger.info(f"Updated capability {tag}: {old_weight} -> {int(new_weight)}")
        
        # 调整投标策略
        self._adjust_bidding_strategy(quality)
        
        # 从区块链同步最新状态
        self.sync_from_blockchain()
    
    def _adjust_bidding_strategy(self, task_score: int) -> None:
        """
        根据任务表现调整投标策略
        
        Args:
            task_score: 任务得分
        """
        old_confidence = self.confidence_factor
        old_risk_tolerance = self.risk_tolerance
        
        # 调整信心因子
        if task_score >= 70:
            # 表现良好，增加信心
            self.confidence_factor = min(95, self.confidence_factor + int(self.learning_rate * 100))
        elif task_score <= 50:
            # 表现不佳，降低信心
            self.confidence_factor = max(30, self.confidence_factor - int(self.learning_rate * 100))
        
        # 调整风险承受度
        if self.reputation >= 70 and task_score >= 70:
            # 声誉高且表现良好，可以承担更多风险
            self.risk_tolerance = min(80, self.risk_tolerance + int(self.learning_rate * 60))
        elif self.reputation <= 40 or task_score <= 40:
            # 声誉低或表现不佳，降低风险
            self.risk_tolerance = max(20, self.risk_tolerance - int(self.learning_rate * 60))
        
        # 如果策略发生变化，更新到区块链
        if old_confidence != self.confidence_factor or old_risk_tolerance != self.risk_tolerance:
            try:
                self._update_bidding_strategy_on_chain()
            except Exception as e:
                logger.error(f"Failed to update bidding strategy on chain: {e}")
                # 回滚本地更改
                self.confidence_factor = old_confidence
                self.risk_tolerance = old_risk_tolerance
    
    def _update_bidding_strategy_on_chain(self) -> None:
        """将更新后的投标策略提交到区块链"""
        try:
            # 准备交易
            nonce = self.web3.eth.get_transaction_count(self.agent_address)
            gas_price = self.web3.eth.gas_price
            
            # 构建交易
            tx = self.incentive_engine.functions.manuallyUpdateBiddingStrategy(
                self.agent_address,
                self.confidence_factor,
                self.risk_tolerance
            ).build_transaction({
                'from': self.agent_address,
                'gas': 2000000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            
            # 签名并发送交易
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.agent_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待交易确认
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully updated bidding strategy on chain: "
                           f"confidence={self.confidence_factor}, risk_tolerance={self.risk_tolerance}")
            else:
                logger.error("Bidding strategy update transaction failed")
                raise Exception("Transaction failed")
                
        except Exception as e:
            logger.error(f"Error updating bidding strategy on chain: {e}")
            raise
    
    def monitor_and_learn(self, polling_interval: int = 60) -> None:
        """
        持续监控区块链事件并学习
        
        Args:
            polling_interval: 轮询间隔（秒）
        """
        logger.info(f"Starting monitoring and learning loop with interval {polling_interval}s")
        
        try:
            while True:
                # 同步区块链状态
                self.sync_from_blockchain()
                
                # 查找可用任务
                open_tasks = self._get_open_tasks()
                logger.info(f"Found {len(open_tasks)} open tasks")
                
                # 处理每个开放任务
                for task_id in open_tasks:
                    # 检查是否已经投标
                    has_bid = self.bid_auction.functions.hasAgentBid(task_id, self.agent_address).call()
                    if has_bid:
                        continue
                    
                    # 决定是否投标
                    if self.should_bid_on_task(Web3.to_hex(task_id)):
                        # 获取任务奖励
                        task_info = self.task_manager.functions.getTaskExecutionInfo(task_id).call()
                        task_reward = task_info[1]  # reward
                        
                        # 计算投标金额和效用
                        bid_amount, utility_score = self.calculate_bid_for_task(
                            Web3.to_hex(task_id), 
                            task_reward
                        )
                        
                        # 提交投标
                        self.place_bid(Web3.to_hex(task_id), bid_amount, utility_score)
                
                # 等待下一次轮询
                time.sleep(polling_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    def _get_open_tasks(self) -> List[bytes]:
        """获取所有开放投标的任务"""
        try:
            # 从TaskMarketplace获取开放任务
            open_task_ids = self.task_manager.functions.getTasksByStatus(0).call()  # 0 = Open
            
            # 过滤出投标开放的任务
            bidding_open_tasks = []
            for task_id in open_task_ids:
                if self.bid_auction.functions.isBiddingOpen(task_id).call():
                    bidding_open_tasks.append(task_id)
            
            return bidding_open_tasks
        except Exception as e:
            logger.error(f"Error getting open tasks: {e}")
            return []


# 示例使用
if __name__ == "__main__":
    # 从环境变量或配置文件加载参数
    agent_address = os.getenv("AGENT_ADDRESS")
    agent_private_key = os.getenv("AGENT_PRIVATE_KEY")
    web3_provider = os.getenv("WEB3_PROVIDER_URL")
    
    # 合约地址
    agent_registry_address = os.getenv("AGENT_REGISTRY_ADDRESS")
    incentive_engine_address = os.getenv("INCENTIVE_ENGINE_ADDRESS")
    bid_auction_address = os.getenv("BID_AUCTION_ADDRESS")
    task_manager_address = os.getenv("TASK_MANAGER_ADDRESS")
    
    # ABI文件路径
    contract_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts/contracts")
    agent_registry_abi_path = os.path.join(contract_dir, "AgentRegistry.sol/AgentRegistry.json")
    incentive_engine_abi_path = os.path.join(contract_dir, "IncentiveEngine.sol/IncentiveEngine.json")
    bid_auction_abi_path = os.path.join(contract_dir, "BidAuction.sol/BidAuction.json")
    task_manager_abi_path = os.path.join(contract_dir, "TaskManager.sol/TaskManager.json")
    
    # 创建自适应投标策略实例
    strategy = AdaptiveBiddingStrategy(
        agent_address=agent_address,
        agent_private_key=agent_private_key,
        web3_provider=web3_provider,
        agent_registry_address=agent_registry_address,
        incentive_engine_address=incentive_engine_address,
        bid_auction_address=bid_auction_address,
        task_manager_address=task_manager_address,
        agent_registry_abi_path=agent_registry_abi_path,
        incentive_engine_abi_path=incentive_engine_abi_path,
        bid_auction_abi_path=bid_auction_abi_path,
        task_manager_abi_path=task_manager_abi_path
    )
    
    # 启动监控和学习循环
    strategy.monitor_and_learn(polling_interval=60)  # 每60秒轮询一次 