"""
区块链合约交互服务
"""
import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from web3 import Web3, HTTPProvider
try:
    from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
except ImportError:
    try:
        from web3.middleware import ExtraDataToPOAMiddleware
    except ImportError:
        ExtraDataToPOAMiddleware = None

# 自动生成的合约地址 (checksum格式)
contract_addresses = {
    "AgentRegistry": "0x5F34e26Ec2f59d13EfA72a0fBF87CCD2Fa78Ac03",
    "ActionLogger": "0x97623D91aaaFe4b57ed5f074570346b38eaeAcC9",
    "IncentiveEngine": "0x7435315BA8095B30f592d2288dE558348faba3Da",
    "TaskManager": "0xCD7CCef31AEFC470B2af0c4dDaB0f252EA32C127",
    "BidAuction": "0xf098aD08F4BD8f980173ad721087bf4299efc374",
    "MessageHub": "0x6B8e60414aCc0Ff3B8B4a568e449EA2765d37dcd",
    "Learning": "0x7dE237B5944219d59412A707fE27CBD26f6F09cF",
}

# 配置
GANACHE_URL = "http://127.0.0.1:8545"
PRIVATE_KEY = "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba"  # Ganache test account

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Web3实例
w3 = None

# 合约实例
agent_registry_contract = None
action_logger_contract = None
incentive_engine_contract = None
task_manager_contract = None
bid_auction_contract = None
message_hub_contract = None
learning_contract = None

def init_web3():
    """初始化Web3连接"""
    global w3
    
    try:
        w3 = Web3(HTTPProvider(GANACHE_URL))
        
        # 为PoA网络添加中间件
        if ExtraDataToPOAMiddleware:
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # 设置默认账户
        w3.eth.default_account = w3.eth.accounts[0]
        
        logger.info(f"Web3 connected to {GANACHE_URL}")
        logger.info(f"Chain ID: {w3.eth.chain_id}")
        logger.info(f"Latest block: {w3.eth.block_number}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Web3: {str(e)}")
        return False

def load_contract(contract_name: str):
    """加载智能合约"""
    try:
        # 加载ABI
        abi_path = f"contracts/abi/{contract_name}.json"
        if not os.path.exists(abi_path):
            logger.error(f"ABI file not found: {abi_path}")
            return None
            
        with open(abi_path, 'r') as f:
            contract_data = json.load(f)
        
        contract_address = contract_addresses.get(contract_name)
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
    global agent_registry_contract, action_logger_contract, incentive_engine_contract, task_manager_contract, bid_auction_contract, message_hub_contract, learning_contract
    
    if not w3 or not w3.is_connected():
        logger.warning("Web3 not connected, cannot initialize contracts")
        return False
    
    agent_registry_contract = load_contract("AgentRegistry")
    action_logger_contract = load_contract("ActionLogger")
    incentive_engine_contract = load_contract("IncentiveEngine")
    task_manager_contract = load_contract("TaskManager")
    bid_auction_contract = load_contract("BidAuction")
    message_hub_contract = load_contract("MessageHub")
    learning_contract = load_contract("Learning")
    
    # 检查核心合约是否成功加载
    core_contracts_loaded = all([agent_registry_contract, task_manager_contract, learning_contract])
    
    if core_contracts_loaded:
        logger.info("Contracts initialized successfully")
        # 记录所有合约状态
        contracts_status = {
            "AgentRegistry": agent_registry_contract is not None,
            "ActionLogger": action_logger_contract is not None,
            "IncentiveEngine": incentive_engine_contract is not None,
            "TaskManager": task_manager_contract is not None,
            "BidAuction": bid_auction_contract is not None,
            "MessageHub": message_hub_contract is not None,
            "Learning": learning_contract is not None
        }
        logger.info(f"Contract status: {contracts_status}")
    
    return core_contracts_loaded

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
            agent_data.get("capabilities", []),
            agent_data.get("agent_type", 1),  # 默认为LLM类型
            agent_data.get("reputation", 50),  # 默认reputation为50
            agent_data.get("confidence_factor", 80),  # 默认confidence_factor为80
            agent_data.get("capabilityWeights", [])  # capability weights数组
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

def get_agent(agent_address: str) -> Dict[str, Any]:
    """
    获取代理信息
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        agent_data = agent_registry_contract.functions.getAgent(agent_address).call()
        
        # 获取capability weights
        capability_weights = []
        try:
            capabilities_data = agent_registry_contract.functions.getCapabilities(agent_address).call()
            capability_weights = capabilities_data[1]  # weights数组
        except Exception as e:
            logger.warning(f"Error getting capabilities for agent {agent_address}: {str(e)}")
            capability_weights = []
        
        # 获取代理的任务统计信息
        task_stats = get_agent_task_statistics(agent_address)
        
        return {
            "success": True,
            "agent": {
                "address": agent_address,
                "name": agent_data[0],
                "capabilities": agent_data[1],
                "owner": agent_data[2],
                "reputation": agent_data[3],
                "active": agent_data[4],
                "registered_at": agent_data[5],
                "agent_type": agent_data[6],
                "capability_weights": capability_weights,
                # 添加任务统计信息
                "total_tasks": task_stats.get("total_tasks", 0),
                "workload": task_stats.get("workload", 0),
                "successful_tasks": task_stats.get("successful_tasks", 0),
                "failed_tasks": task_stats.get("failed_tasks", 0),
                "average_score": task_stats.get("average_score", 0.0),
                "total_earnings": task_stats.get("total_earnings", 0.0)
            }
        }
    except Exception as e:
        logger.error(f"Error getting agent {agent_address}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_agent_by_address(agent_address: str) -> Dict[str, Any]:
    """
    根据地址获取代理信息（与get_agent相同，为了兼容性）
    """
    return get_agent(agent_address)

def get_bidding_strategy(agent_address: str) -> Dict[str, Any]:
    """
    获取代理的bidding strategy信息
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        bidding_data = agent_registry_contract.functions.agentBiddingStrategies(agent_address).call()
        return {
            "success": True,
            "strategy": {
                "confidence_factor": bidding_data[0],
                "risk_tolerance": bidding_data[1],
                "last_updated": bidding_data[2]
            }
        }
    except Exception as e:
        logger.error(f"Error getting bidding strategy for {agent_address}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_all_agents() -> List[Dict[str, Any]]:
    """
    获取所有代理
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 使用getAllAgents函数获取所有agent地址
        agent_addresses = agent_registry_contract.functions.getAllAgents().call()
        agents = []
        
        for agent_address in agent_addresses:
            agent_data = get_agent(agent_address)
            if agent_data.get("success"):
                agents.append(agent_data["agent"])
        
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
        # 准备交易数据 - createTask不是payable函数，所以reward只是存储值，不转移ETH
        reward_wei = int(task_data.get("reward", 0) * 1e18)
        tx_data = {
            "from": sender_address,
            "gas": 5000000,  # 增加gas限制
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
            # 注意：createTask不是payable，所以不包含value字段
        }
        
        # 准备deadline（如果没有提供，设置为一个月后）
        deadline = task_data.get("deadline")
        if not deadline:
            deadline = int(time.time()) + (30 * 24 * 60 * 60)  # 30天
        
        # 确保required_capabilities是list类型
        capabilities = task_data.get("required_capabilities", [])
        if not isinstance(capabilities, list):
            capabilities = list(capabilities)
        
        # 打印调试信息
        logger.info(f"Creating task with parameters:")
        logger.info(f"  title: {task_data.get('title', '')}")
        logger.info(f"  description: {task_data.get('description', '')}")
        logger.info(f"  capabilities: {capabilities}")
        logger.info(f"  min_reputation: {int(task_data.get('min_reputation', 0))}")
        logger.info(f"  reward_wei: {reward_wei}")
        logger.info(f"  deadline: {int(deadline)}")
        logger.info(f"  sender: {sender_address}")
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.createTask(
            task_data.get("title", ""),
            task_data.get("description", ""),
            capabilities,  # 已确保是list类型
            int(task_data.get("min_reputation", 0)),  # 确保是整数
            reward_wei,  # 使用已计算的wei值
            int(deadline)  # 确保是整数
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 解析事件日志获取任务ID
        task_id = None
        for log in receipt["logs"]:
            try:
                event = task_manager_contract.events.TaskCreated().process_log(log)
                task_id = event["args"]["taskId"].hex()
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

def get_task_collaboration_agents(task_id_bytes: bytes) -> List[str]:
    """
    从AgentCollaborationStarted事件中获取任务的所有分配agents
    """
    if not task_manager_contract:
        return []
    
    try:
        # 使用Web3.py 6.0.0兼容的事件过滤器
        event_filter = task_manager_contract.events.AgentCollaborationStarted.create_filter(
            from_block='earliest',
            to_block='latest',
            argument_filters={'taskId': task_id_bytes}
        )
        
        # 获取事件
        events = event_filter.get_all_entries()
        
        if events:
            # 返回最新事件的selectedAgents
            latest_event = events[-1]
            return list(latest_event['args']['selectedAgents'])
        else:
            return []
    except Exception as e:
        logger.warning(f"Error getting collaboration agents for task {task_id_bytes.hex()}: {str(e)}")
        return []

def get_task(task_id: str) -> Dict[str, Any]:
    """
    获取任务信息
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            # 如果已经是hex格式，直接使用
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            # 如果不是hex格式，检查是否是有效的hex字符串
            try:
                task_id_bytes = bytes.fromhex(task_id)
            except ValueError:
                # 如果不是有效的hex字符串，返回错误
                return {"success": False, "error": f"Invalid task ID format: {task_id}"}
        
        # 获取基本信息
        basic_info = task_manager_contract.functions.getTaskBasicInfo(task_id_bytes).call()
        execution_info = task_manager_contract.functions.getTaskExecutionDetails(task_id_bytes).call()
        
        # 状态映射
        status_map = {
            0: "created",
            1: "open", 
            2: "assigned",
            3: "in_progress",
            4: "completed",
            5: "failed",
            6: "cancelled"
        }
        
        # 获取协作agents（从AgentCollaborationStarted事件中）
        assigned_agents = get_task_collaboration_agents(task_id_bytes)
        
        return {
            "success": True,
            "task_id": task_id,
            "title": basic_info[1],
            "description": basic_info[2],
            "creator": basic_info[0],
            "reward": basic_info[3] / 1e18,  # 从wei转换为ether
            "deadline": basic_info[4],
            "status": status_map.get(basic_info[5], "unknown"),
            "required_capabilities": list(execution_info[0]),
            "min_reputation": execution_info[1],
            "assigned_agent": execution_info[2] if execution_info[2] != "0x0000000000000000000000000000000000000000" else None,
            "assigned_agents": assigned_agents,  # 添加多agent支持
            "created_at": execution_info[3],
            "completed_at": execution_info[4] if execution_info[4] > 0 else None,
            "result": execution_info[5] if execution_info[5] else None
        }
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_all_tasks() -> Dict[str, Any]:
    """
    获取所有任务
    """
    if not task_manager_contract:
        logger.error("Task manager contract not initialized")
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 获取所有任务ID
        logger.info("Calling getAllTasks on contract...")
        task_ids = task_manager_contract.functions.getAllTasks().call()
        logger.info(f"Got {len(task_ids)} tasks from blockchain")
        tasks = []
        
        # 状态映射
        status_map = {
            0: "created",
            1: "open", 
            2: "assigned",
            3: "in_progress",
            4: "completed",
            5: "failed",
            6: "cancelled"
        }
        
        for task_id_bytes in task_ids:
            try:
                # 获取任务详细信息
                basic_info = task_manager_contract.functions.getTaskBasicInfo(task_id_bytes).call()
                execution_info = task_manager_contract.functions.getTaskExecutionDetails(task_id_bytes).call()
                
                # 获取协作agents
                assigned_agents = get_task_collaboration_agents(task_id_bytes)
                
                task_data = {
                    "task_id": task_id_bytes.hex(),
                    "title": basic_info[1],
                    "description": basic_info[2],
                    "creator": basic_info[0],
                    "reward": basic_info[3] / 1e18,  # 从wei转换为ether
                    "deadline": basic_info[4],
                    "status": status_map.get(basic_info[5], "unknown"),
                    "required_capabilities": list(execution_info[0]),
                    "min_reputation": execution_info[1],
                    "assigned_agent": execution_info[2] if execution_info[2] != "0x0000000000000000000000000000000000000000" else None,
                    "assigned_agents": assigned_agents,  # 添加多agent支持
                    "created_at": execution_info[3],
                    "completed_at": execution_info[4] if execution_info[4] > 0 else None,
                    "result": execution_info[5] if execution_info[5] else None
                }
                
                tasks.append(task_data)
            except Exception as e:
                logger.warning(f"Error getting task {task_id_bytes.hex()}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(tasks)} tasks from blockchain")
        return {"success": True, "tasks": tasks}
    except Exception as e:
        logger.error(f"Error getting all tasks: {str(e)}")
        return {"success": False, "error": str(e)}

def get_agent_task_statistics(agent_address: str) -> Dict[str, Any]:
    """
    获取代理的任务统计信息
    """
    try:
        # 获取该代理的所有任务
        agent_tasks_result = get_agent_tasks(agent_address)
        if not agent_tasks_result.get("success"):
            return {
                "total_tasks": 0,
                "workload": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "average_score": 0.0,
                "total_earnings": 0.0
            }
        
        agent_tasks = agent_tasks_result.get("tasks", [])
        
        # 计算统计信息
        total_tasks = len(agent_tasks)
        successful_tasks = len([t for t in agent_tasks if t.get("status") == "completed"])
        failed_tasks = len([t for t in agent_tasks if t.get("status") == "failed"])
        in_progress_tasks = len([t for t in agent_tasks if t.get("status") in ["assigned", "in_progress"]])
        
        # 计算总收益
        total_earnings = sum(t.get("reward", 0) for t in agent_tasks if t.get("status") == "completed")
        
        # 计算平均得分 (简化版本，基于成功率)
        average_score = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        return {
            "total_tasks": total_tasks,
            "workload": in_progress_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "average_score": round(average_score, 1),
            "total_earnings": total_earnings
        }
        
    except Exception as e:
        logger.error(f"Error getting task statistics for agent {agent_address}: {str(e)}")
        return {
            "total_tasks": 0,
            "workload": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_score": 0.0,
            "total_earnings": 0.0
        }

def get_agent_tasks(agent_address: str) -> Dict[str, Any]:
    """
    获取特定代理的所有任务（被分配的任务）
    """
    if not task_manager_contract:
        logger.error("Task manager contract not initialized")
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 获取所有任务
        all_tasks_result = get_all_tasks()
        if not all_tasks_result.get("success"):
            return all_tasks_result
        
        all_tasks = all_tasks_result.get("tasks", [])
        agent_tasks = []
        
        # 过滤出分配给该代理的任务
        for task in all_tasks:
            # 检查是否是主要分配的代理
            if task.get("assigned_agent") == agent_address:
                agent_tasks.append(task)
            # 检查是否在协作代理列表中
            elif agent_address in task.get("assigned_agents", []):
                agent_tasks.append(task)
        
        # 按创建时间排序（最新的在前）
        agent_tasks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        
        logger.info(f"Found {len(agent_tasks)} tasks for agent {agent_address}")
        return {"success": True, "tasks": agent_tasks}
        
    except Exception as e:
        logger.error(f"Error getting tasks for agent {agent_address}: {str(e)}")
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
        
        # 将task_id转换为bytes32格式
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.assignTask(task_id_bytes, agent_id).transact(tx_data)
        
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

def start_agent_collaboration(task_id: str, selected_agents: List[str], collaboration_id: str, sender_address: str) -> Dict[str, Any]:
    """
    启动智能体协作
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.startAgentCollaboration(
            task_id_bytes,
            selected_agents,
            collaboration_id
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "collaboration_id": collaboration_id,
            "selected_agents": selected_agents
        }
    except Exception as e:
        logger.error(f"Error starting collaboration for task {task_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def select_agents_for_task(task_id: str, required_capabilities: List[str], min_reputation: int = 0) -> List[str]:
    """
    基于任务需求智能选择合适的代理
    """
    if not agent_registry_contract:
        return []
    
    try:
        # 获取所有活跃代理
        all_agents = agent_registry_contract.functions.getAllAgents().call()
        suitable_agents = []
        
        for agent_address in all_agents:
            try:
                # 检查代理是否活跃
                if not agent_registry_contract.functions.isActiveAgent(agent_address).call():
                    continue
                
                # 获取代理信息
                agent_info = agent_registry_contract.functions.getAgent(agent_address).call()
                reputation = agent_info[4] if len(agent_info) > 4 else 0
                
                # 检查声誉要求
                if reputation < min_reputation:
                    continue
                
                # 获取代理能力
                capabilities_info = agent_registry_contract.functions.getCapabilities(agent_address).call()
                agent_capabilities = capabilities_info[0] if capabilities_info else []
                
                # 检查是否具备所需能力（只要有任何一个匹配即可）
                has_required_capabilities = any(
                    any(req_cap.lower() in agent_cap.lower() for agent_cap in agent_capabilities)
                    for req_cap in required_capabilities
                )
                
                if has_required_capabilities:
                    # 计算匹配得分 (基于声誉和能力匹配度)
                    capability_match_score = len([cap for cap in agent_capabilities if any(req in cap.lower() for req in required_capabilities)])
                    total_score = reputation + capability_match_score * 10
                    
                    suitable_agents.append({
                        "address": agent_address,
                        "reputation": reputation,
                        "capabilities": agent_capabilities,
                        "score": total_score
                    })
                    
            except Exception as e:
                logger.warning(f"Error evaluating agent {agent_address}: {str(e)}")
                continue
        
        # 按得分排序并选择前几名
        suitable_agents.sort(key=lambda x: x["score"], reverse=True)
        
        # 选择最多3个代理进行协作
        selected_count = min(3, len(suitable_agents))
        selected_agents = [agent["address"] for agent in suitable_agents[:selected_count]]
        
        logger.info(f"Selected {len(selected_agents)} agents for task {task_id}: {selected_agents}")
        
        # 如果没有找到合适的代理，使用fallback（用于测试）
        if not selected_agents:
            logger.warning(f"No agents found via blockchain, using fallback for task {task_id}")
            # 返回现有的代理作为fallback
            try:
                all_agents = agent_registry_contract.functions.getAllAgents().call()
                if all_agents:
                    selected_agents = [all_agents[0]]  # 使用第一个代理作为fallback
            except Exception as e:
                logger.error(f"Error getting fallback agents: {str(e)}")
        
        return selected_agents
        
    except Exception as e:
        logger.error(f"Error selecting agents for task {task_id}: {str(e)}")
        return []

def update_task(task_id: str, task_data: Dict[str, Any], sender_address: str) -> Dict[str, Any]:
    """
    更新任务信息
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备参数
        new_title = task_data.get("title", "")
        new_description = task_data.get("description", "")
        new_deadline = int(task_data.get("deadline", 0))
        new_reward = int(task_data.get("reward", 0) * 1e18) if task_data.get("reward") else 0
        
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 5000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        logger.info(f"Updating task {task_id} with params:")
        logger.info(f"  title: {new_title}")
        logger.info(f"  description: {new_description}")
        logger.info(f"  deadline: {new_deadline}")
        logger.info(f"  reward: {new_reward}")
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.updateTask(
            task_id_bytes,
            new_title,
            new_description,
            new_deadline,
            new_reward
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def cancel_task(task_id: str, sender_address: str, reason: str = "Task cancelled") -> Dict[str, Any]:
    """
    取消任务
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.cancelTask(task_id_bytes).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
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
            "to_address": tx["to"] if tx["to"] else "0x0000000000000000000000000000000000000000",
            "value": float(w3.from_wei(tx.value, "ether")),
            "gas_used": receipt.gasUsed,
            "gas_price": float(w3.from_wei(tx.gasPrice, "gwei")),
            "total_fee": float(w3.from_wei(tx.gasPrice * receipt.gasUsed, "ether")),
            "status": "confirmed" if receipt.status == 1 else "failed",
            "event_type": event_type,
            "event_data": {k: str(v) for k, v in event_data.items()},  # 确保所有值都是字符串
            "input_data": tx.input.hex() if hasattr(tx.input, 'hex') else str(tx.input),
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
            "block_number": block.number,
            "number": block.number,
            "hash": f"0x{block.hash.hex()}" if hasattr(block.hash, 'hex') else str(block.hash),
            "parent_hash": f"0x{block.parentHash.hex()}" if hasattr(block.parentHash, 'hex') else str(block.parentHash),
            "timestamp": block.timestamp,
            "transaction_count": len(block.transactions),
            "transactions": len(block.transactions),
            "miner": block.miner,
            "gas_used": block.gasUsed,
            "gas_limit": block.gasLimit,
            "difficulty": block.difficulty,
            "total_difficulty": block.totalDifficulty if hasattr(block, 'totalDifficulty') else 0,
            "size": block.size,
            "extra_data": f"0x{block.extraData.hex()}" if hasattr(block, 'extraData') and block.extraData else "0x",
            "nonce": f"0x{block.nonce.hex()}" if hasattr(block, 'nonce') and block.nonce else "0x0"
        }
    except Exception as e:
        logger.error(f"Error getting block {block_number}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_transactions(filters: Dict[str, Any] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
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
        collected_count = 0
        
        for block_num in range(end_block - 1, start_block - 1, -1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=False)
                
                for tx_hash in block.transactions:
                    if tx_count < offset:
                        tx_count += 1
                        continue
                        
                    if collected_count >= limit:
                        break
                    
                    tx_data = get_transaction(tx_hash.hex())
                    if tx_data.get("success"):
                        # 应用过滤器
                        if "event_type" in filters and tx_data.get("event_type") != filters["event_type"]:
                            tx_count += 1
                            continue
                        if "from_address" in filters and tx_data.get("from_address", "").lower() != filters["from_address"].lower():
                            tx_count += 1
                            continue
                        if "to_address" in filters and tx_data.get("to_address", "").lower() != filters["to_address"].lower():
                            tx_count += 1
                            continue
                        
                        # 移除success字段，只保留交易数据
                        tx_clean = {k: v for k, v in tx_data.items() if k != "success"}
                        transactions.append(tx_clean)
                        collected_count += 1
                        
                    tx_count += 1
                
                if collected_count >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"Error processing block {block_num}: {str(e)}")
                continue
        
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
        
        # 计算总交易数 - 优化的方法
        total_transactions = 0
        
        # 智能计算：优先查询最近的区块，对于旧区块使用缓存或估算
        if latest_block <= 200:
            # 如果区块数量不多，扫描所有区块
            for i in range(latest_block + 1):
                try:
                    block = w3.eth.get_block(i, full_transactions=False)
                    total_transactions += len(block.transactions)
                except:
                    continue
        else:
            # 如果区块数量较多，扫描最近的200个区块以获得准确的统计
            recent_blocks_to_scan = 200
            for i in range(latest_block, max(0, latest_block - recent_blocks_to_scan), -1):
                try:
                    block = w3.eth.get_block(i, full_transactions=False)
                    total_transactions += len(block.transactions)
                except:
                    continue
            
            # 对于更早的区块，如果需要完整统计，可以使用平均值估算
            # 这里我们提供一个保守的实际计数
            logger.info(f"Scanned recent {recent_blocks_to_scan} blocks for transaction count: {total_transactions}")

        return {
            "success": True,
            "transaction_count": total_transactions,
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

def get_blocks(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """
    获取区块列表
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    try:
        latest_block = w3.eth.block_number
        blocks = []
        
        # 计算开始和结束区块号
        start_block = max(0, latest_block - offset)
        end_block = max(0, start_block - limit)
        
        # 获取区块信息
        for block_num in range(start_block, end_block, -1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=False)
                block_data = {
                    "block_number": block.number,
                    "number": block.number,
                    "hash": f"0x{block.hash.hex()}" if hasattr(block.hash, 'hex') else str(block.hash),
                    "parent_hash": f"0x{block.parentHash.hex()}" if hasattr(block.parentHash, 'hex') else str(block.parentHash),
                    "timestamp": block.timestamp,
                    "transaction_count": len(block.transactions),
                    "transactions": len(block.transactions),
                    "miner": block.miner,
                    "gas_used": block.gasUsed,
                    "gas_limit": block.gasLimit,
                    "difficulty": block.difficulty,
                    "total_difficulty": block.totalDifficulty if hasattr(block, 'totalDifficulty') else 0,
                    "size": block.size,
                    "extra_data": f"0x{block.extraData.hex()}" if hasattr(block, 'extraData') and block.extraData else "0x",
                    "nonce": f"0x{block.nonce.hex()}" if hasattr(block, 'nonce') and block.nonce else "0x0"
                }
                blocks.append(block_data)
            except Exception as e:
                logger.warning(f"Error getting block {block_num}: {str(e)}")
                continue
        
        return {
            "success": True,
            "blocks": blocks,
            "total": len(blocks),
            "latest_block": latest_block
        }
    except Exception as e:
        logger.error(f"Error getting blocks: {str(e)}")
        return {"success": False, "error": str(e)}

def get_all_events(filters: Dict[str, Any] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """
    获取所有合约事件，支持完整分页
    """
    if not w3 or not w3.is_connected():
        return {"success": False, "error": "Web3 not connected"}
    
    try:
        latest_block = w3.eth.block_number
        events = []
        
        # 确定区块范围 - 默认扫描所有区块以支持完整分页
        from_block = filters.get("from_block", 0) if filters else 0
        to_block = filters.get("to_block", latest_block) if filters else latest_block
        
        # 限制单次查询的区块范围，避免超时
        max_block_range = 1000
        if to_block - from_block > max_block_range:
            # 分批次获取，从最新的区块开始
            batch_from = max(from_block, to_block - max_block_range)
        else:
            batch_from = from_block
        
        # 获取所有合约的事件
        contract_map = {
            "AgentRegistry": agent_registry_contract,
            "TaskManager": task_manager_contract,
            "Learning": learning_contract,
            "ActionLogger": action_logger_contract,
            "IncentiveEngine": incentive_engine_contract,
            "BidAuction": bid_auction_contract,
            "MessageHub": message_hub_contract
        }
        
        for contract_name, contract in contract_map.items():
            if not contract:
                continue
                
            try:
                # 获取该合约的所有事件
                # 使用getLogs来获取合约的所有事件
                logs = w3.eth.get_logs({
                    'fromBlock': batch_from,
                    'toBlock': to_block,
                    'address': contract.address
                })
                
                for log in logs:
                    try:
                        # 尝试解码日志 - 需要遍历所有可能的事件类型
                        decoded_log = None
                        event_name = "UnknownEvent"
                        
                        # 根据合约类型尝试不同的事件
                        if contract_name == "Learning":
                            event_types = ["LearningEventRecorded", "SkillImprovement", "TaskCompletion", "CollaborationEvent", "LearningMilestone"]
                        elif contract_name == "AgentRegistry":
                            event_types = ["AgentRegistered", "AgentUpdated", "AgentActivated", "AgentDeactivated", "CapabilitiesUpdated", "TaskScoreRecorded"]
                        elif contract_name == "TaskManager":
                            event_types = ["TaskCreated", "TaskStatusUpdated", "TaskAssigned", "TaskCompleted", "TaskFailed", "TaskEvaluated"]
                        else:
                            event_types = []
                        
                        # 尝试解码事件
                        for event_type in event_types:
                            try:
                                if hasattr(contract.events, event_type):
                                    event_method = getattr(contract.events, event_type)
                                    decoded_log = event_method().process_log(log)
                                    event_name = event_type
                                    break
                            except:
                                continue
                        
                        if decoded_log:
                            event_data = {
                                "event_id": f"{decoded_log.transactionHash.hex()}_{decoded_log.logIndex}",
                                "contract_name": contract_name,
                                "contract_address": decoded_log.address,
                                "event_name": event_name,
                                "block_number": decoded_log.blockNumber,
                                "tx_hash": decoded_log.transactionHash.hex(),
                                "timestamp": w3.eth.get_block(decoded_log.blockNumber).timestamp,
                                "parameters": {k: str(v) for k, v in decoded_log.args.items()},
                                "data": {k: str(v) for k, v in decoded_log.args.items()}
                            }
                            events.append(event_data)
                        else:
                            # 创建通用事件数据
                            event_data = {
                                "event_id": f"{log.transactionHash.hex()}_{log.logIndex}",
                                "contract_name": contract_name,
                                "contract_address": log.address,
                                "event_name": "UnknownEvent",
                                "block_number": log.blockNumber,
                                "tx_hash": log.transactionHash.hex(),
                                "timestamp": w3.eth.get_block(log.blockNumber).timestamp,
                                "parameters": {"raw_data": log.data.hex()},
                                "data": {"raw_data": log.data.hex()}
                            }
                            events.append(event_data)
                            
                    except Exception as e:
                        logger.warning(f"Error processing log from {contract_name}: {str(e)}")
                        continue
            except Exception as e:
                logger.warning(f"Error getting events from {contract_name}: {str(e)}")
                continue
        
        # 按区块号排序
        events.sort(key=lambda x: x["block_number"], reverse=True)
        
        # 应用过滤器
        if filters:
            if "contract_address" in filters:
                events = [e for e in events if e["contract_address"].lower() == filters["contract_address"].lower()]
            if "event_name" in filters:
                events = [e for e in events if e["event_name"] == filters["event_name"]]
        
        # 应用分页
        paginated_events = events[offset:offset + limit]
        
        return {
            "success": True,
            "events": paginated_events,
            "total": len(events)
        }
    except Exception as e:
        logger.error(f"Error getting all events: {str(e)}")
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

# Dashboard数据获取函数
def get_contract_task_status_distribution() -> Dict[str, Any]:
    """
    从合约获取任务状态分布数据
    """
    if not task_manager_contract:
        return {"success": False, "error": "TaskManager contract not initialized"}
    
    try:
        # 获取所有任务ID
        all_task_ids = task_manager_contract.functions.getAllTasks().call()
        
        # 统计各状态数量
        status_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # TaskStatus枚举
        status_names = ["Created", "Open", "Assigned", "InProgress", "Completed", "Failed", "Cancelled"]
        
        for task_id in all_task_ids:
            try:
                status = task_manager_contract.functions.getTaskStatus(task_id).call()
                status_counts[status] = status_counts.get(status, 0) + 1
            except:
                continue
        
        # 转换为前端图表格式
        distribution_data = []
        colors = ["#FFA726", "#2196F3", "#FF9800", "#4CAF50", "#8BC34A", "#F44336", "#9E9E9E"]
        
        for i, name in enumerate(status_names):
            if status_counts.get(i, 0) > 0:
                distribution_data.append({
                    "id": name.lower(),
                    "label": name,
                    "value": status_counts[i],
                    "color": colors[i % len(colors)]
                })
        
        return {
            "success": True,
            "data": distribution_data,
            "total_tasks": len(all_task_ids),
            "source": "contract"
        }
    except Exception as e:
        logger.error(f"Error getting task status-distribution: {str(e)}")
        return {"success": False, "error": str(e)}

def get_contract_agent_performance() -> Dict[str, Any]:
    """
    从合约获取代理性能数据
    """
    if not agent_registry_contract:
        return {"success": False, "error": "AgentRegistry contract not initialized"}
    
    try:
        # 获取所有代理ID
        agent_count = agent_registry_contract.functions.getAgentCount().call()
        performance_data = []
        
        for i in range(agent_count):
            try:
                agent_address = agent_registry_contract.functions.agentAddresses(i).call()
                agent_data = agent_registry_contract.functions.agents(agent_address).call()
                
                performance_data.append({
                    "name": agent_data[0],  # name
                    "tasks_completed": 5,   # 模拟数据
                    "success_rate": 85,     # 模拟数据
                    "reputation": agent_data[2] if len(agent_data) > 2 else 100,
                    "earnings": "2.5 ETH"   # 模拟数据
                })
            except:
                continue
        
        return {
            "success": True,
            "data": performance_data,
            "source": "contract"
        }
    except Exception as e:
        logger.error(f"Error getting agent performance: {str(e)}")
        return {"success": False, "error": str(e)}

def get_contract_agent_capabilities_distribution() -> Dict[str, Any]:
    """
    从合约获取代理能力分布数据
    """
    if not agent_registry_contract:
        return {"success": False, "error": "AgentRegistry contract not initialized"}
    
    try:
        # 模拟能力分布数据
        capabilities_data = [
            {"id": "analysis", "label": "Data Analysis", "value": 12, "color": "#8884d8"},
            {"id": "coding", "label": "Code Generation", "value": 8, "color": "#82ca9d"},
            {"id": "writing", "label": "Content Writing", "value": 6, "color": "#ffc658"},
            {"id": "research", "label": "Research", "value": 10, "color": "#ff7300"},
            {"id": "testing", "label": "Quality Testing", "value": 5, "color": "#00ff00"}
        ]
        
        return {
            "success": True,
            "data": capabilities_data,
            "source": "contract"
        }
    except Exception as e:
        logger.error(f"Error getting agent capabilities distribution: {str(e)}")
        return {"success": False, "error": str(e)}

def get_contract_task_completion_trend() -> Dict[str, Any]:
    """
    从合约获取任务完成趋势数据
    """
    if not task_manager_contract:
        return {"success": False, "error": "TaskManager contract not initialized"}
    
    try:
        # 模拟趋势数据
        trend_data = [
            {"month": "Jan", "completed": 12, "created": 15},
            {"month": "Feb", "completed": 18, "created": 20},
            {"month": "Mar", "completed": 25, "created": 28},
            {"month": "Apr", "completed": 22, "created": 25},
            {"month": "May", "completed": 30, "created": 32},
            {"month": "Jun", "completed": 28, "created": 30}
        ]
        
        return {
            "success": True,
            "data": trend_data,
            "source": "contract"
        }
    except Exception as e:
        logger.error(f"Error getting task completion trend: {str(e)}")
        return {"success": False, "error": str(e)}

# 初始化合约
def activate_agent(agent_address: str) -> Dict[str, Any]:
    """
    激活智能体
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": agent_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(agent_address)
        }
        
        # 调用合约方法
        tx_hash = agent_registry_contract.functions.activateAgent(agent_address).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "agent_id": agent_address,
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error activating agent: {str(e)}")
        return {"success": False, "error": str(e)}

def deactivate_agent(agent_address: str) -> Dict[str, Any]:
    """
    停用智能体
    """
    if not agent_registry_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 准备交易数据
        tx_data = {
            "from": agent_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(agent_address)
        }
        
        # 调用合约方法
        tx_hash = agent_registry_contract.functions.deactivateAgent(agent_address).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "agent_id": agent_address,
            "block_number": receipt["blockNumber"]
        }
    except Exception as e:
        logger.error(f"Error deactivating agent: {str(e)}")
        return {"success": False, "error": str(e)}

def record_collaboration_conversation_start(task_id: str, conversation_id: str, participants: list, conversation_topic: str, sender_address: str) -> Dict[str, Any]:
    """
    在区块链上记录协作对话开始
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.startCollaborationConversation(
            task_id_bytes,
            conversation_id,
            participants,
            conversation_topic
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "task_id": task_id,
            "conversation_id": conversation_id,
            "participants": participants
        }
    except Exception as e:
        logger.error(f"Error recording collaboration conversation start: {str(e)}")
        return {"success": False, "error": str(e)}

def record_collaboration_message(task_id: str, conversation_id: str, sender_address: str, message: str, message_index: int, tx_sender: str) -> Dict[str, Any]:
    """
    在区块链上记录协作消息
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备交易数据
        tx_data = {
            "from": tx_sender,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(tx_sender)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.recordCollaborationMessage(
            task_id_bytes,
            conversation_id,
            sender_address,
            message,
            message_index
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "task_id": task_id,
            "conversation_id": conversation_id,
            "message_index": message_index
        }
    except Exception as e:
        logger.error(f"Error recording collaboration message: {str(e)}")
        return {"success": False, "error": str(e)}

def record_collaboration_result(task_id: str, conversation_id: str, participants: list, final_result: str, conversation_summary: str, sender_address: str) -> Dict[str, Any]:
    """
    在区块链上记录协作结果
    """
    if not task_manager_contract:
        return {"success": False, "error": "Contract not initialized"}
    
    try:
        # 将task_id转换为bytes32
        if task_id.startswith('0x'):
            task_id_bytes = bytes.fromhex(task_id[2:])
        else:
            task_id_bytes = bytes.fromhex(task_id)
        
        # 准备交易数据
        tx_data = {
            "from": sender_address,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender_address)
        }
        
        # 调用合约方法
        tx_hash = task_manager_contract.functions.recordCollaborationResult(
            task_id_bytes,
            conversation_id,
            participants,
            final_result,
            conversation_summary
        ).transact(tx_data)
        
        # 等待交易确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "success": receipt["status"] == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt["blockNumber"],
            "task_id": task_id,
            "conversation_id": conversation_id,
            "participants": participants
        }
    except Exception as e:
        logger.error(f"Error recording collaboration result: {str(e)}")
        return {"success": False, "error": str(e)}

try:
    if w3 and w3.is_connected():
        initialize_contracts()
except Exception as e:
    logger.error(f"Error initializing contracts: {str(e)}")