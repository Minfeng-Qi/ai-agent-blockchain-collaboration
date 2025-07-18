"""
协作对话数据库服务
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json

from models.collaboration import Base, Conversation, ConversationMessage, CollaborationResult, BlockchainEvent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = "sqlite:///./collaboration.db"  # 使用SQLite作为示例
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

class CollaborationDBService:
    """协作对话数据库服务类"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_db(self) -> Session:
        """获取数据库会话"""
        db = self.SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    def create_conversation(self, conversation_id: str, task_id: str, task_description: str, 
                          participants: List[str], agent_roles: Dict) -> Conversation:
        """
        创建新的对话记录
        
        Args:
            conversation_id: 对话ID
            task_id: 任务ID
            task_description: 任务描述
            participants: 参与者地址列表
            agent_roles: agent角色配置
            
        Returns:
            conversation: 对话记录
        """
        db = self.get_db()
        try:
            conversation = Conversation(
                conversation_id=conversation_id,
                task_id=task_id,
                task_description=task_description,
                participants=participants,
                agent_roles=agent_roles,
                status='active'
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Created conversation record: {conversation_id}")
            return conversation
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise
        finally:
            db.close()
    
    def add_message(self, conversation_id: str, sender_address: str, content: str, 
                   message_index: int, agent_name: str = None, round_number: int = None) -> ConversationMessage:
        """
        添加对话消息
        
        Args:
            conversation_id: 对话ID
            sender_address: 发送者地址
            content: 消息内容
            message_index: 消息序号
            agent_name: agent名称
            round_number: 轮次号
            
        Returns:
            message: 消息记录
        """
        db = self.get_db()
        try:
            message = ConversationMessage(
                conversation_id=conversation_id,
                sender_address=sender_address,
                agent_name=agent_name,
                content=content,
                message_index=message_index,
                round_number=round_number
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            return message
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error adding message: {e}")
            raise
        finally:
            db.close()
    
    def save_collaboration_result(self, conversation_id: str, task_id: str, 
                                final_result: str, conversation_summary: str,
                                participants: List[str], message_count: int,
                                success: bool = True) -> CollaborationResult:
        """
        保存协作结果
        
        Args:
            conversation_id: 对话ID
            task_id: 任务ID
            final_result: 最终结果
            conversation_summary: 对话摘要
            participants: 参与者列表
            message_count: 消息总数
            success: 是否成功
            
        Returns:
            result: 结果记录
        """
        db = self.get_db()
        try:
            result = CollaborationResult(
                conversation_id=conversation_id,
                task_id=task_id,
                final_result=final_result,
                conversation_summary=conversation_summary,
                participants=participants,
                message_count=message_count,
                success=success
            )
            
            db.add(result)
            
            # 更新对话状态
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.status = 'completed'
                conversation.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(result)
            
            logger.info(f"Saved collaboration result for conversation: {conversation_id}")
            return result
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error saving collaboration result: {e}")
            raise
        finally:
            db.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        获取对话记录
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            conversation: 对话记录或None
        """
        db = self.get_db()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            
            return conversation
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting conversation: {e}")
            return None
        finally:
            db.close()
    
    def get_conversation_messages(self, conversation_id: str) -> List[ConversationMessage]:
        """
        获取对话消息列表
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            messages: 消息列表
        """
        db = self.get_db()
        try:
            messages = db.query(ConversationMessage).filter(
                ConversationMessage.conversation_id == conversation_id
            ).order_by(ConversationMessage.message_index).all()
            
            return messages
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
        finally:
            db.close()
    
    def get_task_conversations(self, task_id: str) -> List[Conversation]:
        """
        获取任务的所有对话
        
        Args:
            task_id: 任务ID
            
        Returns:
            conversations: 对话列表
        """
        db = self.get_db()
        try:
            conversations = db.query(Conversation).filter(
                Conversation.task_id == task_id
            ).order_by(desc(Conversation.created_at)).all()
            
            return conversations
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting task conversations: {e}")
            return []
        finally:
            db.close()
    
    def get_collaboration_result(self, conversation_id: str) -> Optional[CollaborationResult]:
        """
        获取协作结果
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            result: 协作结果或None
        """
        db = self.get_db()
        try:
            result = db.query(CollaborationResult).filter(
                CollaborationResult.conversation_id == conversation_id
            ).first()
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting collaboration result: {e}")
            return None
        finally:
            db.close()
    
    def record_blockchain_event(self, event_type: str, task_id: str, event_data: Dict,
                              conversation_id: str = None, transaction_hash: str = None,
                              block_number: int = None) -> BlockchainEvent:
        """
        记录区块链事件
        
        Args:
            event_type: 事件类型
            task_id: 任务ID
            event_data: 事件数据
            conversation_id: 对话ID
            transaction_hash: 交易哈希
            block_number: 区块号
            
        Returns:
            event: 事件记录
        """
        db = self.get_db()
        try:
            event = BlockchainEvent(
                event_type=event_type,
                task_id=task_id,
                conversation_id=conversation_id,
                transaction_hash=transaction_hash,
                block_number=block_number,
                event_data=event_data
            )
            
            db.add(event)
            db.commit()
            db.refresh(event)
            
            logger.info(f"Recorded blockchain event: {event_type} for task {task_id}")
            return event
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error recording blockchain event: {e}")
            raise
        finally:
            db.close()
    
    def get_conversation_with_details(self, conversation_id: str) -> Dict:
        """
        获取对话的完整信息（包括消息和结果）
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            conversation_details: 完整的对话信息
        """
        db = self.get_db()
        try:
            # 获取对话基本信息
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                return None
            
            # 获取消息
            messages = db.query(ConversationMessage).filter(
                ConversationMessage.conversation_id == conversation_id
            ).order_by(ConversationMessage.message_index).all()
            
            # 获取结果
            result = db.query(CollaborationResult).filter(
                CollaborationResult.conversation_id == conversation_id
            ).first()
            
            # 组装完整信息
            conversation_details = {
                "id": conversation.id,
                "conversation_id": conversation.conversation_id,
                "task_id": conversation.task_id,
                "task_description": conversation.task_description,
                "participants": conversation.participants,
                "agent_roles": conversation.agent_roles,
                "status": conversation.status,
                "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                "completed_at": conversation.completed_at.isoformat() if conversation.completed_at else None,
                "messages": [
                    {
                        "id": msg.id,
                        "sender_address": msg.sender_address,
                        "agent_name": msg.agent_name,
                        "content": msg.content,
                        "message_index": msg.message_index,
                        "round_number": msg.round_number,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                    }
                    for msg in messages
                ],
                "result": {
                    "id": result.id,
                    "final_result": result.final_result,
                    "conversation_summary": result.conversation_summary,
                    "participants": result.participants,
                    "message_count": result.message_count,
                    "success": result.success,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                } if result else None
            }
            
            return conversation_details
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting conversation details: {e}")
            return None
        finally:
            db.close()

    def create_learning_event(self, learning_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建学习事件记录
        
        Args:
            learning_event: 学习事件数据
            
        Returns:
            创建结果
        """
        db = self.get_db()
        try:
            # 创建区块链事件记录
            blockchain_event = BlockchainEvent(
                event_id=learning_event["event_id"],
                event_type=learning_event["event_type"],
                agent_id=learning_event["agent_id"],
                block_number=learning_event.get("block_number"),
                transaction_hash=learning_event.get("transaction_hash"),
                event_data=learning_event["data"],  # 设置必须的event_data字段
                data=json.dumps(learning_event["data"]),  # 保留data字段作为JSON字符串
                timestamp=datetime.fromtimestamp(learning_event["timestamp"])
            )
            
            db.add(blockchain_event)
            db.commit()
            db.refresh(blockchain_event)
            
            logger.info(f"Created learning event record: {learning_event['event_id']}")
            
            return {
                "id": blockchain_event.id,
                "event_id": blockchain_event.event_id,
                "success": True
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating learning event: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()

    def get_agent_learning_events(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取agent的学习事件
        
        Args:
            agent_id: agent ID
            limit: 返回记录数限制
            
        Returns:
            学习事件列表
        """
        db = self.get_db()
        try:
            events = db.query(BlockchainEvent).filter(
                BlockchainEvent.agent_id == agent_id,
                BlockchainEvent.event_type.in_(["task_evaluation", "task_completion", "training"])
            ).order_by(desc(BlockchainEvent.timestamp)).limit(limit).all()
            
            return [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "agent_id": event.agent_id,
                    "data": json.loads(event.data) if event.data else {},
                    "transaction_hash": event.transaction_hash,
                    "block_number": event.block_number,
                    "timestamp": event.timestamp.isoformat() if event.timestamp else None
                }
                for event in events
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting agent learning events: {e}")
            return []
        finally:
            db.close()


# 全局服务实例
collaboration_db_service = CollaborationDBService()