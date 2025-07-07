"""
区块链合约交互服务
"""
import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 区块链连接配置
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

# 合约ABI和地址
CONTRACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "build")

# 尝试连接到区块链
try:
    w3 = Web3(HTTPProvider(BLOCKCHAIN_RPC_URL))
    # 对于一些测试网络，如Ganache，需要添加POA中间件
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    logger.info(f"Connected to blockchain: {w3.is_connected()}")
except Exception as e:
    logger.error(f"Failed to connect to blockchain: {str(e)}")
    w3 = None

# 合约实例
agent_registry_contract = None
task_manager_contract = None
learning_contract = None

def load_contract(contract_name: str):
    """
    加载合约实例
    """
    try:
        # 加载合约ABI
        abi_path = os.path.join(CONTRACT_DIR, f"{contract_name}.json")
        if not os.path.exists(abi_path):
            logger.warning(f"Contract ABI file not found: {abi_path}")
            return None
            
        with open(abi_path, 'r') as f:
            contract_data = json.load(f)
        
        # 获取合约地址
        address_path = os.path.join(CONTRACT_DIR, f"{contract_name}_address.json")
        if not os.path.exists(address_path):
            logger.warning(f"Contract address file not found: {address_path}")
            return None
            
        with open(address_path, 'r') as f:
            address_data = json.load(f)
            
        contract_address = address_data.get("address")
        if not contract_address:
            logger.warning(f"Contract address not found for {contract_name}")
            return None
        
        # 创建合约实例
        contract = w3.eth.contract(address=contract_address, abi=contract_data["abi"])
        logger.info(f"Loaded contract {contract_name} at {contract_address}")
        return contract
    except Exception as e:
        logger.error(f"Error loading contract {contract_name}: {str(e)}")
        return None

def initialize_contracts():
    """
    初始化所有合约
    """
    global agent_registry_contract, task_manager_contract, learning_contract
    
    if not w3 or not w3.is_connected():
        logger.warning("Web3 not connected, cannot initialize contracts")
        return False
    
    agent_registry_contract = load_contract("AgentRegistry")
    task_manager_contract = load_contract("TaskManager")
    learning_contract = load_contract("Learning")
    
    return all([agent_registry_contract, task_manager_contract, learning_contract])

def get_connection_status() -> Dict[str, Any]:
    """
    获取区块链连接状态
    """
    status = {
        "connected": False,
        "network_id": None,
        "latest_block": None,
        "contracts": {
            "agent_registry": agent_registry_contract is not None,
            "task_manager": task_manager_contract is not None,
            "learning": learning_contract is not None
        }
    }
    
    if w3 and w3.is_connected():
        status["connected"] = True
        try:
            status["network_id"] = w3.eth.chain_id
            status["latest_block"] = w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting blockchain status: {str(e)}")
    
    return status

# 代理相关方法
def register_agent(agent_data: Dict[str, Any], sender_address: str) -> Dict[str, Any]:
    """
    注册新代理
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = agent_registry_contract.functions.registerAgent(
            agent_data["name"],
            agent_data["capabilities"],
            agent_data["reputation"] if "reputation" in agent_data else 0,
            agent_data["confidence_factor"] if "confidence_factor" in agent_data else 0
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取代理ID
        agent_id = None
        for log in receipt["logs"]:
            try:
                event = agent_registry_contract.events.AgentRegistered().process_log(log)
                agent_id = event["args"]["agentId"]
                break
            except:
                continue
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "agent_id": agent_id,
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        return {"success": False, "error": str(e)}

def get_agent(agent_id: str) -> Dict[str, Any]:
    """
    获取代理信息
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        agent_data = agent_registry_contract.functions.getAgent(agent_id).call()
        return {
            "success": True,
            "agent_id": agent_id,
            "name": agent_data[0],
            "capabilities": agent_data[1],
            "reputation": agent_data[2],
            "confidence_factor": agent_data[3],
            "registration_date": agent_data[4],
            "active": agent_data[5]
        }
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_all_agents() -> List[Dict[str, Any]]:
    """
    获取所有代理
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        agent_count = agent_registry_contract.functions.getAgentCount().call()
        agents = []
        
        for i in range(agent_count):
            agent_id = agent_registry_contract.functions.agentIds(i).call()
            agent_data = get_agent(agent_id)
            if agent_data["success"]:
                agents.append(agent_data)
        
        return {"success": True, "agents": agents}
    except Exception as e:
        logger.error(f"Error getting all agents: {str(e)}")
        return {"success": False, "error": str(e)}

# 任务相关方法
def create_task(task_data: Dict[str, Any], sender_address: str) -> Dict[str, Any]:
    """
    创建新任务
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "value": w3.to_wei(task_data.get("reward", 0), "ether"),
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.createTask(
            task_data["title"],
            task_data["description"],
            task_data.get("required_capabilities", []),
            task_data.get("deadline", 0),
            task_data.get("complexity", 1)
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取任务ID
        task_id = None
        for log in receipt["logs"]:
            try:
                event = task_manager_contract.events.TaskCreated().process_log(log)
                task_id = event["args"]["taskId"]
                break
            except:
                continue
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "task_id": task_id,
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {"success": False, "error": str(e)}

def get_task(task_id: str) -> Dict[str, Any]:
    """
    获取任务信息
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        task_data = task_manager_contract.functions.getTask(task_id).call()
        return {
            "success": True,
            "task_id": task_id,
            "title": task_data[0],
            "description": task_data[1],
            "creator": task_data[2],
            "assigned_to": task_data[3],
            "status": task_data[4],
            "reward": w3.from_wei(task_data[5], "ether"),
            "created_at": task_data[6],
            "deadline": task_data[7],
            "required_capabilities": task_data[8],
            "complexity": task_data[9]
        }
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_all_tasks() -> List[Dict[str, Any]]:
    """
    获取所有任务
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        task_count = task_manager_contract.functions.getTaskCount().call()
        tasks = []
        
        for i in range(task_count):
            task_id = task_manager_contract.functions.taskIds(i).call()
            task_data = get_task(task_id)
            if task_data["success"]:
                tasks.append(task_data)
        
        return {"success": True, "tasks": tasks}
    except Exception as e:
        logger.error(f"Error getting all tasks: {str(e)}")
        return {"success": False, "error": str(e)}

def assign_task(task_id: str, agent_id: str, sender_address: str) -> Dict[str, Any]:
    """
    分配任务给代理
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.assignTask(task_id, agent_id).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error assigning task {task_id} to agent {agent_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def complete_task(task_id: str, result: str, sender_address: str) -> Dict[str, Any]:
    """
    完成任务
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.completeTask(task_id, result).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {str(e)}")
        return {"success": False, "error": str(e)}

# 学习相关方法
def record_learning_event(agent_id: str, event_type: str, data: str, sender_address: str) -> Dict[str, Any]:
    """
    记录学习事件
    """
    if not learning_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = learning_contract.functions.recordLearningEvent(agent_id, event_type, data).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取事件ID
        event_id = None
        for log in receipt["logs"]:
            try:
                event = learning_contract.events.LearningEventRecorded().process_log(log)
                event_id = event["args"]["eventId"]
                break
            except:
                continue
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "event_id": event_id,
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error recording learning event for agent {agent_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_learning_events(agent_id: str) -> List[Dict[str, Any]]:
    """
    获取代理的学习事件
    """
    if not learning_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        event_count = learning_contract.functions.getAgentEventCount(agent_id).call()
        events = []
        
        for i in range(event_count):
            event_id = learning_contract.functions.getAgentEventIdAtIndex(agent_id, i).call()
            event_data = learning_contract.functions.getLearningEvent(event_id).call()
            
            events.append({
                "event_id": event_id,
                "agent_id": event_data[0],
                "event_type": event_data[1],
                "data": event_data[2],
                "timestamp": event_data[3]
            })
        
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Error getting learning events for agent {agent_id}: {str(e)}")
        return {"success": False, "error": str(e)}

# 区块链数据相关方法
def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    获取交易详情
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    try:
        # 获取交易信息
        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        block = w3.eth.get_block(tx.blockNumber)
        
        # 解析事件类型
        event_type = "Unknown"
        event_data = {}
        
        # 检查是否是已知合约的事件
        contracts = [
            (agent_registry_contract, "AgentRegistered", "AgentUpdated"),
            (task_manager_contract, "TaskCreated", "TaskAssigned", "TaskCompleted"),
            (learning_contract, "LearningEventRecorded")
        ]
        
        for contract, *events in contracts:
            if contract and receipt and receipt.get("logs"):
                for log in receipt["logs"]:
                    for event_name in events:
                        try:
                            event_obj = getattr(contract.events, event_name)()
                            parsed_log = event_obj.process_log(log)
                            event_type = event_name
                            event_data = parsed_log["args"]
                            break
                        except:
                            continue
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block_number": tx.blockNumber,
            "timestamp": block.timestamp,
            "from_address": tx["from"],
            "to_address": tx["to"],
            "value": w3.from_wei(tx.value, "ether"),
            "gas_used": receipt.gasUsed,
            "gas_price": w3.from_wei(tx.gasPrice, "gwei"),
            "total_fee": w3.from_wei(tx.gasPrice * receipt.gasUsed, "ether"),
            "status": "confirmed" if receipt.status == 1 else "failed",
            "event_type": event_type,
            "event_data": event_data,
            "input_data": tx.input,
            "confirmations": w3.eth.block_number - tx.blockNumber
        }
    except Exception as e:
        logger.error(f"Error getting transaction {tx_hash}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_block(block_number: int) -> Dict[str, Any]:
    """
    获取区块详情
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    try:
        # 获取区块信息
        block = w3.eth.get_block(block_number, full_transactions=False)
        
        return {
            "success": True,
            "number": block.number,
            "hash": block.hash.hex(),
            "parent_hash": block.parentHash.hex(),
            "timestamp": block.timestamp,
            "transactions": len(block.transactions),
            "miner": block.miner,
            "gas_used": block.gasUsed,
            "gas_limit": block.gasLimit,
            "difficulty": block.difficulty,
            "total_difficulty": block.totalDifficulty,
            "size": block.size,
            "extra_data": block.extraData.hex(),
            "nonce": block.nonce.hex()
        }
    except Exception as e:
        logger.error(f"Error getting block {block_number}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_transactions(filters: Dict[str, Any] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    获取交易列表
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    filters = filters or {}
    transactions = []
    
    try:
        # 获取最新区块号
        latest_block = w3.eth.block_number
        
        # 确定起始区块
        start_block = max(0, latest_block - 100)  # 默认只查询最近100个区块
        if "block_number" in filters:
            start_block = filters["block_number"]
            end_block = start_block + 1
        else:
            end_block = latest_block + 1
        
        # 收集交易
        tx_count = 0
        for block_num in range(end_block - 1, start_block - 1, -1):
            block = w3.eth.get_block(block_num, full_transactions=False)
            
            for tx_hash in block.transactions:
                if tx_count < offset:
                    tx_count += 1
                    continue
                    
                if len(transactions) >= limit:
                    break
                
                tx_data = get_transaction(tx_hash.hex())
                if tx_data["success"]:
                    # 应用过滤器
                    if "event_type" in filters and tx_data["event_type"] != filters["event_type"]:
                        continue
                    if "from_address" in filters and tx_data["from_address"].lower() != filters["from_address"].lower():
                        continue
                    if "to_address" in filters and tx_data["to_address"].lower() != filters["to_address"].lower():
                        continue
                    
                    transactions.append(tx_data)
                    tx_count += 1
            
            if len(transactions) >= limit:
                break
        
        return {"success": True, "transactions": transactions, "total": tx_count}
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return {"success": False, "error": str(e)}

def get_contract_events(contract_address: str, event_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    获取合约事件
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    filters = filters or {}
    events = []
    
    try:
        # 确定要查询的合约
        contract = None
        if agent_registry_contract and agent_registry_contract.address.lower() == contract_address.lower():
            contract = agent_registry_contract
        elif task_manager_contract and task_manager_contract.address.lower() == contract_address.lower():
            contract = task_manager_contract
        elif learning_contract and learning_contract.address.lower() == contract_address.lower():
            contract = learning_contract
        
        if not contract:
            return {"success": False, "error": f"Contract not found at address {contract_address}"}
        
        # 确定事件过滤器
        from_block = filters.get("from_block", 0)
        to_block = filters.get("to_block", "latest")
        
        # 获取事件
        event_filter = getattr(contract.events, event_name).createFilter(
            fromBlock=from_block,
            toBlock=to_block
        )
        
        # 处理事件
        for event in event_filter.get_all_entries():
            block = w3.eth.get_block(event.blockNumber)
            
            events.append({
                "event_name": event_name,
                "block_number": event.blockNumber,
                "tx_hash": event.transactionHash.hex(),
                "timestamp": block.timestamp,
                "contract_address": contract_address,
                "parameters": event.args
            })
        
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Error getting events for contract {contract_address}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_blockchain_stats() -> Dict[str, Any]:
    """
    获取区块链统计数据
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    try:
        latest_block = w3.eth.block_number
        
        # 计算平均区块时间
        if latest_block > 1:
            latest_block_data = w3.eth.get_block(latest_block)
            prev_block_data = w3.eth.get_block(latest_block - 1)
            avg_block_time = (latest_block_data.timestamp - prev_block_data.timestamp)
        else:
            avg_block_time = 0
        
        # 计算平均每个区块的交易数
        if latest_block > 0:
            recent_blocks = min(10, latest_block + 1)  # 最多取10个区块
            total_tx = 0
            
            for i in range(latest_block, latest_block - recent_blocks, -1):
                block = w3.eth.get_block(i)
                total_tx += len(block.transactions)
            
            avg_tx_per_block = total_tx / recent_blocks
        else:
            avg_tx_per_block = 0
        
        # 获取合约统计数据
        agent_count = 0
        task_count = 0
        learning_event_count = 0
        
        if agent_registry_contract:
            try:
                agent_count = agent_registry_contract.functions.getAgentCount().call()
            except:
                pass
        
        if task_manager_contract:
            try:
                task_count = task_manager_contract.functions.getTaskCount().call()
            except:
                pass
        
        if learning_contract:
            try:
                learning_event_count = learning_contract.functions.getTotalEventCount().call()
            except:
                pass
        
        return {
            "success": True,
            "latest_block": latest_block,
            "avg_block_time": avg_block_time,
            "avg_transactions_per_block": avg_tx_per_block,
            "agent_count": agent_count,
            "task_count": task_count,
            "learning_event_count": learning_event_count,
            "connected": True
        }
    except Exception as e:
        logger.error(f"Error getting blockchain stats: {str(e)}")
        return {"success": False, "error": str(e)}

def record_collaboration_ipfs(collaboration_id: str, ipfs_cid: str, task_id: str, sender_address: str) -> Dict[str, Any]:
    """
    记录协作IPFS哈希到区块链
    """
    if not learning_contract:
        return {"success": False, "error": "Learning contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法记录协作数据
        collaboration_data = json.dumps({
            "collaboration_id": collaboration_id,
            "task_id": task_id,
            "ipfs_cid": ipfs_cid,
            "timestamp": int(time.time())
        })
        
        tx_hash = learning_contract.functions.recordLearningEvent(
            collaboration_id,
            "collaboration",
            collaboration_data
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取事件ID
        event_id = None
        for log in receipt["logs"]:
            try:
                event = learning_contract.events.LearningEventRecorded().process_log(log)
                event_id = event["args"]["eventId"]
                break
            except:
                continue
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "event_id": event_id,
            "block_number": receipt["blockNumber"],
            "ipfs_cid": ipfs_cid
        }
    except Exception as e:
        logger.error(f"Error recording collaboration IPFS: {str(e)}")
        return {"success": False, "error": str(e)}

def get_collaboration_record(collaboration_id: str) -> Dict[str, Any]:
    """
    获取协作记录
    """
    if not learning_contract:
        return {"success": False, "error": "Learning contract not initialized"}
    
    try:
        # 获取协作相关的学习事件
        events = get_learning_events(collaboration_id)
        if not events["success"]:
            return events
        
        # 过滤出协作事件
        collaboration_events = [
            event for event in events["events"]
            if event["event_type"] == "collaboration"
        ]
        
        if not collaboration_events:
            return {"success": False, "error": "No collaboration records found"}
        
        # 解析最新的协作记录
        latest_event = collaboration_events[-1]
        collaboration_data = json.loads(latest_event["data"])
        
        return {
            "success": True,
            "collaboration_id": collaboration_id,
            "task_id": collaboration_data.get("task_id"),
            "ipfs_cid": collaboration_data.get("ipfs_cid"),
            "timestamp": collaboration_data.get("timestamp"),
            "block_number": latest_event.get("block_number"),
            "transaction_hash": latest_event.get("transaction_hash")
        }
    except Exception as e:
        logger.error(f"Error getting collaboration record: {str(e)}")
        return {"success": False, "error": str(e)}

# 初始化合约
try:
    if w3 and w3.is_connected():
        initialize_contracts()
except Exception as e:
    logger.error(f"Error initializing contracts: {str(e)}")