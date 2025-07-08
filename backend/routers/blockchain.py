"""
区块链数据API路由
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from services import contract_service

router = APIRouter()

# 模拟数据，用于开发测试
mock_transactions = [
    {
        "tx_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234",
        "block_number": 123456,
        "timestamp": "2023-05-15T10:30:00Z",
        "from_address": "0x1234567890123456789012345678901234567890",
        "to_address": "0x0987654321098765432109876543210987654321",
        "value": "1.5 ETH",
        "gas_used": 21000,
        "status": "confirmed",
        "event_type": "TaskCreated",
        "event_data": { "task_id": "task-123", "reward": "1.5 ETH" }
    },
    {
        "tx_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678",
        "block_number": 123455,
        "timestamp": "2023-05-15T09:45:00Z",
        "from_address": "0x2345678901234567890123456789012345678901",
        "to_address": "0x1234567890123456789012345678901234567890",
        "value": "0.5 ETH",
        "gas_used": 35000,
        "status": "confirmed",
        "event_type": "AgentRegistered",
        "event_data": { "agent_id": "agent-456" }
    }
]

mock_blocks = [
    {
        "number": 123456,
        "hash": "0xblock1234block1234block1234block1234block1234block1234block1234block1234",
        "parent_hash": "0xblock0000block0000block0000block0000block0000block0000block0000block0000",
        "timestamp": "2023-05-15T10:30:00Z",
        "transactions": 35,
        "miner": "0x4567890123456789012345678901234567890123",
        "gas_used": 1500000,
        "gas_limit": 3000000,
        "difficulty": "2500000000000000",
        "total_difficulty": "985000000000000000000",
        "size": 25000,
        "extra_data": "0x4d696e65642062792045746865726d696e65",
        "nonce": "0x7a1b2c3d4e5f6789"
    },
    {
        "number": 123455,
        "hash": "0xblock5678block5678block5678block5678block5678block5678block5678block5678",
        "parent_hash": "0xblock0000block0000block0000block0000block0000block0000block0000block0000",
        "timestamp": "2023-05-15T09:45:00Z",
        "transactions": 28,
        "miner": "0x5678901234567890123456789012345678901234",
        "gas_used": 1200000,
        "gas_limit": 3000000,
        "difficulty": "2500000000000000",
        "total_difficulty": "985000000000000000000",
        "size": 22000,
        "extra_data": "0x4d696e65642062792045746865726d696e65",
        "nonce": "0x7a1b2c3d4e5f6789"
    }
]

# 模型定义
class TransactionFilter(BaseModel):
    event_type: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    block_number: Optional[int] = None

class BlockchainStats(BaseModel):
    transaction_count: int
    block_count: int
    latest_block: int
    avg_block_time: Optional[float] = None
    avg_transactions_per_block: Optional[float] = None
    agent_count: Optional[int] = None
    task_count: Optional[int] = None
    learning_event_count: Optional[int] = None
    connected: bool

# 路由定义
@router.get("/transactions")
async def get_transactions(
    event_type: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    block_number: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_mock: bool = Query(False, description="强制使用模拟数据")
):
    """
    获取区块链交易列表，支持过滤和分页
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"] or use_mock:
        # 如果区块链未连接或强制使用模拟数据，返回模拟数据
        filtered_tx = mock_transactions
        
        if event_type:
            filtered_tx = [tx for tx in filtered_tx if tx["event_type"] == event_type]
        if from_address:
            filtered_tx = [tx for tx in filtered_tx if tx["from_address"].lower() == from_address.lower()]
        if to_address:
            filtered_tx = [tx for tx in filtered_tx if tx["to_address"].lower() == to_address.lower()]
        if block_number is not None:
            filtered_tx = [tx for tx in filtered_tx if tx["block_number"] == block_number]
        
        paginated_tx = filtered_tx[offset:offset+limit]
        
        return {
            "transactions": paginated_tx,
            "total": len(filtered_tx),
            "limit": limit,
            "offset": offset,
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if from_address:
        filters["from_address"] = from_address
    if to_address:
        filters["to_address"] = to_address
    if block_number is not None:
        filters["block_number"] = block_number
    
    try:
        result = contract_service.get_transactions(filters, limit, offset)
        
        if not result["success"]:
            # 如果获取失败，返回模拟数据
            filtered_tx = mock_transactions
            
            if event_type:
                filtered_tx = [tx for tx in filtered_tx if tx["event_type"] == event_type]
            if from_address:
                filtered_tx = [tx for tx in filtered_tx if tx["from_address"].lower() == from_address.lower()]
            if to_address:
                filtered_tx = [tx for tx in filtered_tx if tx["to_address"].lower() == to_address.lower()]
            if block_number is not None:
                filtered_tx = [tx for tx in filtered_tx if tx["block_number"] == block_number]
            
            paginated_tx = filtered_tx[offset:offset+limit]
            
            return {
                "transactions": paginated_tx,
                "total": len(filtered_tx),
                "limit": limit,
                "offset": offset,
                "note": "Using mock data - failed to fetch from blockchain"
            }
        
        return {
            "transactions": result["transactions"],
            "total": result.get("total", len(result["transactions"])),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        # 发生异常，返回模拟数据
        filtered_tx = mock_transactions
        
        if event_type:
            filtered_tx = [tx for tx in filtered_tx if tx["event_type"] == event_type]
        if from_address:
            filtered_tx = [tx for tx in filtered_tx if tx["from_address"].lower() == from_address.lower()]
        if to_address:
            filtered_tx = [tx for tx in filtered_tx if tx["to_address"].lower() == to_address.lower()]
        if block_number is not None:
            filtered_tx = [tx for tx in filtered_tx if tx["block_number"] == block_number]
        
        paginated_tx = filtered_tx[offset:offset+limit]
        
        return {
            "transactions": paginated_tx,
            "total": len(filtered_tx),
            "limit": limit,
            "offset": offset,
            "note": f"Using mock data - error: {str(e)}"
        }

@router.get("/transactions/{tx_hash}")
async def get_transaction(tx_hash: str):
    """
    获取单个交易的详细信息
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"]:
        # 如果区块链未连接，返回模拟数据
        for tx in mock_transactions:
            if tx["tx_hash"] == tx_hash:
                return tx
        
        # 如果未找到匹配的交易，生成一个模拟交易
        return {
            "tx_hash": tx_hash,
            "block_number": 123456,
            "timestamp": "2023-05-15T10:30:00Z",
            "from_address": "0x1234567890123456789012345678901234567890",
            "to_address": "0x0987654321098765432109876543210987654321",
            "value": "1.5 ETH",
            "gas_used": 21000,
            "gas_price": "20 Gwei",
            "total_fee": "0.00042 ETH",
            "status": "confirmed",
            "event_type": "TaskCreated",
            "event_data": { 
                "task_id": "task-123", 
                "reward": "1.5 ETH",
                "description": "Analyze market data and provide investment recommendations"
            },
            "input_data": "0x7b2274617...",
            "confirmations": 10,
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    result = contract_service.get_transaction(tx_hash)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=f"Transaction {tx_hash} not found")
    
    return result

@router.get("/blocks")
async def get_blocks(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_mock: bool = Query(False, description="强制使用模拟数据")
):
    """
    获取区块列表，支持分页
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"] or use_mock:
        # 如果区块链未连接或强制使用模拟数据，返回模拟数据
        filtered_blocks = mock_blocks
        
        # 应用分页
        paginated_blocks = filtered_blocks[offset:offset+limit]
        
        return {
            "blocks": paginated_blocks,
            "total": len(filtered_blocks),
            "limit": limit,
            "offset": offset,
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    try:
        result = contract_service.get_blocks(limit, offset)
        
        if not result["success"]:
            # 如果获取失败，返回模拟数据
            filtered_blocks = mock_blocks
            paginated_blocks = filtered_blocks[offset:offset+limit]
            
            return {
                "blocks": paginated_blocks,
                "total": len(filtered_blocks),
                "limit": limit,
                "offset": offset,
                "note": "Using mock data - failed to fetch from blockchain"
            }
        
        return {
            "blocks": result["blocks"],
            "total": result.get("total", len(result["blocks"])),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        # 发生异常，返回模拟数据
        filtered_blocks = mock_blocks
        paginated_blocks = filtered_blocks[offset:offset+limit]
        
        return {
            "blocks": paginated_blocks,
            "total": len(filtered_blocks),
            "limit": limit,
            "offset": offset,
            "note": f"Using mock data - error: {str(e)}"
        }

@router.get("/blocks/{block_number}")
async def get_block(block_number: int):
    """
    获取区块详细信息
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"]:
        # 如果区块链未连接，返回模拟数据
        for block in mock_blocks:
            if block["number"] == block_number:
                return block
        
        # 如果未找到匹配的区块，生成一个模拟区块
        return {
            "number": block_number,
            "hash": f"0xblock{block_number}block{block_number}block{block_number}block{block_number}",
            "parent_hash": f"0xblock{block_number-1}block{block_number-1}block{block_number-1}block{block_number-1}",
            "timestamp": "2023-05-15T10:30:00Z",
            "transactions": 35,
            "miner": "0x4567890123456789012345678901234567890123",
            "gas_used": 1500000,
            "gas_limit": 3000000,
            "difficulty": "2500000000000000",
            "total_difficulty": "985000000000000000000",
            "size": 25000,
            "extra_data": "0x4d696e65642062792045746865726d696e65",
            "nonce": "0x7a1b2c3d4e5f6789",
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    result = contract_service.get_block(block_number)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=f"Block {block_number} not found")
    
    return result

@router.get("/events/{contract_address}/{event_name}")
async def get_contract_events(
    contract_address: str,
    event_name: str,
    from_block: Optional[int] = None,
    to_block: Optional[int] = None
):
    """
    获取合约事件
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"]:
        # 如果区块链未连接，返回模拟数据
        return {
            "events": [
                {
                    "event_name": event_name,
                    "block_number": 123456,
                    "tx_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234",
                    "timestamp": "2023-05-15T10:30:00Z",
                    "contract_address": contract_address,
                    "parameters": { 
                        "task_id": "task-123", 
                        "reward": "1.5 ETH",
                        "creator": "0x1234567890123456789012345678901234567890"
                    }
                },
                {
                    "event_name": event_name,
                    "block_number": 123455,
                    "tx_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678",
                    "timestamp": "2023-05-15T09:45:00Z",
                    "contract_address": contract_address,
                    "parameters": { 
                        "agent_id": "agent-456",
                        "name": "DataAnalysisAgent",
                        "owner": "0x2345678901234567890123456789012345678901"
                    }
                }
            ],
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    filters = {}
    if from_block is not None:
        filters["from_block"] = from_block
    if to_block is not None:
        filters["to_block"] = to_block
    
    result = contract_service.get_contract_events(contract_address, event_name, filters)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch events"))
    
    return {
        "events": result["events"]
    }

@router.get("/events")
async def get_events(
    contract_address: Optional[str] = None,
    event_name: Optional[str] = None,
    from_block: Optional[int] = None,
    to_block: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_mock: bool = Query(False, description="强制使用模拟数据")
):
    """
    获取合约事件列表，支持过滤和分页
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"] or use_mock:
        # 如果区块链未连接或强制使用模拟数据，返回模拟数据
        mock_events = [
            {
                "event_id": "event_001",
                "contract_address": "0x0987654321098765432109876543210987654321",
                "event_name": "TaskCreated",
                "block_number": 123456,
                "tx_hash": "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234",
                "timestamp": "2023-05-15T10:30:00Z",
                "data": { 
                    "task_id": "task-123", 
                    "reward": "1.5 ETH",
                    "creator": "0x1234567890123456789012345678901234567890"
                }
            },
            {
                "event_id": "event_002",
                "contract_address": "0x0987654321098765432109876543210987654321",
                "event_name": "AgentRegistered",
                "block_number": 123455,
                "tx_hash": "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678",
                "timestamp": "2023-05-15T09:45:00Z",
                "data": { 
                    "agent_id": "agent-456",
                    "name": "DataAnalysisAgent",
                    "owner": "0x2345678901234567890123456789012345678901"
                }
            },
            {
                "event_id": "event_003",
                "contract_address": "0x0987654321098765432109876543210987654321",
                "event_name": "TaskCompleted",
                "block_number": 123457,
                "tx_hash": "0x1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd",
                "timestamp": "2023-05-15T11:15:00Z",
                "data": { 
                    "task_id": "task-123",
                    "agent_id": "agent-456",
                    "score": 4.8
                }
            }
        ]
        
        # 应用过滤器
        filtered_events = mock_events
        if contract_address:
            filtered_events = [e for e in filtered_events if e["contract_address"].lower() == contract_address.lower()]
        if event_name:
            filtered_events = [e for e in filtered_events if e["event_name"] == event_name]
        if from_block is not None:
            filtered_events = [e for e in filtered_events if e["block_number"] >= from_block]
        if to_block is not None:
            filtered_events = [e for e in filtered_events if e["block_number"] <= to_block]
        
        # 应用分页
        paginated_events = filtered_events[offset:offset+limit]
        
        return {
            "events": paginated_events,
            "total": len(filtered_events),
            "limit": limit,
            "offset": offset,
            "note": "Using mock data - blockchain not connected"
        }
    
    # 区块链已连接，从合约服务获取数据
    filters = {}
    if contract_address:
        filters["contract_address"] = contract_address
    if event_name:
        filters["event_name"] = event_name
    if from_block is not None:
        filters["from_block"] = from_block
    if to_block is not None:
        filters["to_block"] = to_block
    
    try:
        result = contract_service.get_all_events(filters, limit, offset)
        
        if not result["success"]:
            # 如果获取失败，返回空列表
            return {
                "events": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "note": "Failed to fetch events from blockchain"
            }
        
        return {
            "events": result["events"],
            "total": result.get("total", len(result["events"])),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        # 发生异常，返回空列表
        return {
            "events": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "note": f"Error fetching events: {str(e)}"
        }

@router.get("/stats", response_model=BlockchainStats)
async def get_blockchain_stats():
    """
    获取区块链统计数据
    """
    # 检查区块链连接
    connection_status = contract_service.get_connection_status()
    if not connection_status["connected"]:
        # 如果区块链未连接，返回模拟数据
        return {
            "transaction_count": len(mock_transactions),
            "block_count": max([block["number"] for block in mock_blocks]) if mock_blocks else 0,
            "latest_block": max([block["number"] for block in mock_blocks]) if mock_blocks else 0,
            "avg_block_time": 15.0,
            "avg_transactions_per_block": 30.0,
            "agent_count": 10,
            "task_count": 25,
            "learning_event_count": 50,
            "connected": False
        }
    
    # 区块链已连接，从合约服务获取数据
    result = contract_service.get_blockchain_stats()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch blockchain stats"))
    
    return {
        "transaction_count": result.get("transaction_count", 0),
        "block_count": result.get("latest_block", 0),
        "latest_block": result.get("latest_block", 0),
        "avg_block_time": result.get("avg_block_time", 0),
        "avg_transactions_per_block": result.get("avg_transactions_per_block", 0),
        "agent_count": result.get("agent_count", 0),
        "task_count": result.get("task_count", 0),
        "learning_event_count": result.get("learning_event_count", 0),
        "connected": result.get("connected", True)
    }