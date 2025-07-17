"""
数据库模型 - 协作对话相关
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    """对话表"""
    __tablename__ = 'conversations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(255), nullable=False, index=True)
    conversation_id = Column(String(255), unique=True, nullable=False, index=True)
    task_description = Column(Text, nullable=False)
    participants = Column(JSON, nullable=False)  # 参与者地址列表
    agent_roles = Column(JSON, nullable=False)   # agent角色配置
    status = Column(String(50), default='active')  # active, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 关联的消息
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    # 最终结果
    result = relationship("CollaborationResult", back_populates="conversation", uselist=False, cascade="all, delete-orphan")


class ConversationMessage(Base):
    """对话消息表"""
    __tablename__ = 'conversation_messages'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(255), ForeignKey('conversations.conversation_id'), nullable=False)
    sender_address = Column(String(255), nullable=False)  # 发送者地址，system为系统消息
    agent_name = Column(String(100), nullable=True)  # agent名称
    content = Column(Text, nullable=False)
    message_index = Column(Integer, nullable=False)  # 消息在对话中的序号
    round_number = Column(Integer, nullable=True)    # 对话轮次
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关联的对话
    conversation = relationship("Conversation", back_populates="messages")


class CollaborationResult(Base):
    """协作结果表"""
    __tablename__ = 'collaboration_results'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(255), ForeignKey('conversations.conversation_id'), nullable=False)
    task_id = Column(String(255), nullable=False, index=True)
    final_result = Column(Text, nullable=False)        # 最终结果
    conversation_summary = Column(Text, nullable=False) # 对话摘要
    participants = Column(JSON, nullable=False)        # 参与者列表
    message_count = Column(Integer, default=0)         # 消息总数
    success = Column(Boolean, default=True)            # 是否成功完成
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联的对话
    conversation = relationship("Conversation", back_populates="result")


class BlockchainEvent(Base):
    """区块链事件记录表"""
    __tablename__ = 'blockchain_events'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(255), nullable=True, index=True)  # 学习事件ID
    event_type = Column(String(100), nullable=False)   # 事件类型
    agent_id = Column(String(255), nullable=True, index=True)  # Agent ID for learning events
    task_id = Column(String(255), nullable=True, index=True)   # Made nullable for learning events
    conversation_id = Column(String(255), nullable=True, index=True)
    transaction_hash = Column(String(255), nullable=True)
    block_number = Column(Integer, nullable=True)
    event_data = Column(JSON, nullable=False)          # 事件数据
    data = Column(Text, nullable=True)                  # Additional data field for learning events
    timestamp = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)         # 是否已处理