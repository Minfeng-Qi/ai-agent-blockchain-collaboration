"""
ChatGPT API 集成服务 - 用于agent协作对话
"""
from openai import OpenAI
import json
import uuid
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import concurrent.futures
import threading
import sys
import os

# Add the parent directory to the path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OPENAI_API_KEY

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置OpenAI客户端
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

class AgentCollaborationService:
    """Agent协作服务类"""
    
    def __init__(self):
        self.conversations = {}  # 存储活跃的对话
        self.conversation_history = {}  # 存储对话历史
        
    def create_conversation(self, task_id: str, agents: List[Dict], task_description: str) -> str:
        """
        创建新的协作对话
        
        Args:
            task_id: 任务ID
            agents: 参与的agent列表
            task_description: 任务描述
            
        Returns:
            conversation_id: 对话ID
        """
        conversation_id = str(uuid.uuid4())
        
        # 为每个agent创建角色设定
        agent_roles = self._create_agent_roles(agents, task_description)
        
        conversation = {
            "id": conversation_id,
            "task_id": task_id,
            "agents": agents,
            "agent_roles": agent_roles,
            "task_description": task_description,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.conversations[conversation_id] = conversation
        logger.info(f"Created conversation {conversation_id} for task {task_id}")
        
        return conversation_id
    
    def _create_agent_roles(self, agents: List[Dict], task_description: str) -> Dict:
        """
        为每个agent创建角色设定
        
        Args:
            agents: agent列表
            task_description: 任务描述
            
        Returns:
            agent_roles: 每个agent的角色设定
        """
        agent_roles = {}
        
        for i, agent in enumerate(agents):
            capabilities = agent.get('capabilities', [])
            
            # 基于能力创建角色
            role_description = f"""
            你是一个专业的AI助手，参与团队协作完成任务。
            
            任务描述：{task_description}
            
            你的专业能力：{', '.join(capabilities)}
            
            协作规则：
            1. 积极参与讨论，提供专业建议
            2. 与其他团队成员友好协作
            3. 根据你的能力领域提供具体帮助
            4. 保持专业和建设性的态度
            5. 最终目标是高质量完成任务
            
            请根据任务需求和你的专业能力，积极参与协作对话。
            """
            
            agent_roles[agent['address']] = {
                "role": "assistant",
                "description": role_description,
                "capabilities": capabilities,
                "agent_name": f"Agent-{i+1}"
            }
        
        return agent_roles
    
    async def start_distributed_collaboration(self, conversation_id: str) -> List[Dict]:
        """
        启动分布式agent协作对话 - 每个agent独立调用GPT API
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            messages: 对话消息列表
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        agents = conversation["agents"]
        task_description = conversation["task_description"]
        
        # 启动对话
        initial_message = f"""
        欢迎参与分布式AI Agent任务协作！
        
        任务：{task_description}
        
        参与的Agent数量：{len(agents)}
        
        每个Agent将独立思考并基于自己的专业能力提供协作建议。
        """
        
        # 记录初始消息
        self._add_message(conversation_id, "system", initial_message)
        
        # 并发执行所有agent的API调用
        messages = await self._execute_distributed_collaboration(conversation_id)
        
        return messages
    
    async def _execute_distributed_collaboration(self, conversation_id: str) -> List[Dict]:
        """
        执行分布式协作 - 每个agent独立并发调用GPT API
        """
        conversation = self.conversations[conversation_id]
        agents = conversation["agents"]
        
        # 创建协程列表，每个agent一个协程
        tasks = [
            self._single_agent_collaboration(conversation_id, agent)
            for agent in agents
        ]
        
        # 并发执行所有agent任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集所有消息
        all_messages = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agents[i]['address']} collaboration failed: {result}")
                continue
            
            if isinstance(result, list):
                all_messages.extend(result)
            else:
                all_messages.append(result)
        
        # 按时间戳排序
        all_messages.sort(key=lambda x: x.get("timestamp", ""))
        
        return all_messages
    
    async def _single_agent_collaboration(self, conversation_id: str, agent: Dict) -> List[Dict]:
        """
        单个agent的独立协作处理
        """
        conversation = self.conversations[conversation_id]
        agent_address = agent['address']
        agent_role = conversation["agent_roles"][agent_address]
        
        messages = []
        
        # 多轮对话
        for round_num in range(3):  # 3轮对话
            try:
                # 构建对话历史
                conversation_history = self._build_conversation_history(conversation_id)
                
                # 基于agent能力的专业提示
                round_prompt = self._generate_capability_based_prompt(agent, round_num)
                
                # 独立调用GPT API
                response = await self._call_distributed_agent_api(
                    agent_role["description"],
                    conversation_history,
                    round_prompt,
                    agent_address
                )
                
                # 创建消息
                message = {
                    "sender": agent_address,
                    "agent_name": agent_role["agent_name"],
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "message_index": len(conversation["messages"]),
                    "round": round_num + 1,
                    "agent_capabilities": agent.get("capabilities", [])
                }
                
                # 保存消息
                self._add_message(conversation_id, agent_address, response)
                messages.append(message)
                
                # 添加延迟避免API限制
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in distributed collaboration for agent {agent_address} round {round_num+1}: {e}")
                continue
        
        return messages
    
    def _generate_capability_based_prompt(self, agent: Dict, round_num: int) -> str:
        """
        基于agent能力生成专业提示
        """
        capabilities = agent.get("capabilities", [])
        
        if round_num == 0:
            # 第一轮：介绍和分析
            return f"""
            作为具有{', '.join(capabilities)}能力的专业Agent，请：
            1. 简要介绍你的专业能力和如何应用到当前任务
            2. 基于你的专业角度分析这个任务的关键要点
            3. 提出你认为最重要的执行步骤
            """
        elif round_num == 1:
            # 第二轮：深入分析和建议
            return f"""
            基于前面的讨论，作为{', '.join(capabilities)}专家，请：
            1. 深入分析其他Agent的观点，找出你认为正确和需要补充的地方
            2. 基于你的专业能力，提供具体的技术方案或执行建议
            3. 识别可能的风险和挑战，并提出解决方案
            """
        else:
            # 第三轮：总结和整合
            return f"""
            作为{', '.join(capabilities)}专家，请：
            1. 总结整个讨论中最有价值的观点
            2. 提出一个综合性的解决方案，整合各Agent的专业建议
            3. 给出具体的实施步骤和成功指标
            """
    
    async def _call_distributed_agent_api(self, system_prompt: str, conversation_history: List[Dict], 
                                        user_prompt: str, agent_id: str) -> str:
        """
        为分布式agent调用ChatGPT API - 每个agent独立调用
        """
        # 创建专属于这个agent的消息历史
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\n[Agent ID: {agent_id}]"}
        ]
        
        # 添加对话历史（最近的8条消息）
        recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
        messages.extend(recent_history)
        
        # 添加当前提示
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # 检查OpenAI客户端是否可用
            if client is None:
                raise Exception("OpenAI client not initialized. Please check your API key.")
            
            # 调用OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=600,
                temperature=0.8,  # 增加创造性
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Agent {agent_id} API call successful, response length: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Distributed Agent {agent_id} API error: {e}")
            return f"[Agent {agent_id} Error: Unable to generate response - {str(e)}]"

    async def start_collaboration(self, conversation_id: str) -> List[Dict]:
        """
        开始agent协作对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            messages: 对话消息列表
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        agents = conversation["agents"]
        task_description = conversation["task_description"]
        
        # 启动对话
        initial_message = f"""
        欢迎参与任务协作！
        
        任务：{task_description}
        
        参与的Agent数量：{len(agents)}
        
        请各位Agent介绍自己的能力，并开始讨论如何协作完成这个任务。
        """
        
        # 记录初始消息
        self._add_message(conversation_id, "system", initial_message)
        
        # 让每个agent依次发言
        messages = []
        for i, agent in enumerate(agents):
            agent_address = agent['address']
            agent_role = conversation["agent_roles"][agent_address]
            
            # 构建对话历史
            conversation_history = self._build_conversation_history(conversation_id)
            
            # 调用ChatGPT API
            try:
                response = await self._call_chatgpt_api(
                    agent_role["description"],
                    conversation_history,
                    f"请{agent_role['agent_name']}介绍自己的能力并提出协作建议"
                )
                
                # 记录消息
                message = {
                    "sender": agent_address,
                    "agent_name": agent_role["agent_name"],
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "message_index": len(conversation["messages"])
                }
                
                self._add_message(conversation_id, agent_address, response)
                messages.append(message)
                
                # 添加延迟避免API限制
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error calling ChatGPT API for agent {agent_address}: {e}")
                continue
        
        # 进行更深入的协作对话
        collaboration_messages = await self._conduct_collaboration_rounds(conversation_id, rounds=3)
        messages.extend(collaboration_messages)
        
        return messages
    
    async def _conduct_collaboration_rounds(self, conversation_id: str, rounds: int = 3) -> List[Dict]:
        """
        进行多轮协作对话
        
        Args:
            conversation_id: 对话ID
            rounds: 对话轮数
            
        Returns:
            messages: 对话消息列表
        """
        conversation = self.conversations[conversation_id]
        agents = conversation["agents"]
        messages = []
        
        for round_num in range(rounds):
            round_messages = []
            
            for agent in agents:
                agent_address = agent['address']
                agent_role = conversation["agent_roles"][agent_address]
                
                # 构建对话历史
                conversation_history = self._build_conversation_history(conversation_id)
                
                # 为每轮对话设定不同的引导提示
                if round_num == 0:
                    prompt = "基于前面的讨论，请详细说明你将如何贡献完成这个任务"
                elif round_num == 1:
                    prompt = "请分析前面的建议，提出具体的执行步骤和方法"
                else:
                    prompt = "请总结讨论结果，提出最终的解决方案"
                
                try:
                    response = await self._call_chatgpt_api(
                        agent_role["description"],
                        conversation_history,
                        prompt
                    )
                    
                    message = {
                        "sender": agent_address,
                        "agent_name": agent_role["agent_name"],
                        "content": response,
                        "timestamp": datetime.now().isoformat(),
                        "message_index": len(conversation["messages"]),
                        "round": round_num + 1
                    }
                    
                    self._add_message(conversation_id, agent_address, response)
                    round_messages.append(message)
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in collaboration round {round_num+1} for agent {agent_address}: {e}")
                    continue
            
            messages.extend(round_messages)
        
        return messages
    
    async def _call_chatgpt_api(self, system_prompt: str, conversation_history: List[Dict], user_prompt: str) -> str:
        """
        调用ChatGPT API
        
        Args:
            system_prompt: 系统提示
            conversation_history: 对话历史
            user_prompt: 用户提示
            
        Returns:
            response: API响应
        """
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加对话历史（最近的10条消息）
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        messages.extend(recent_history)
        
        # 添加当前提示
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # 检查OpenAI客户端是否可用
            if client is None:
                raise Exception("OpenAI client not initialized. Please check your API key.")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return f"[Error: Unable to generate response - {str(e)}]"
    
    def _build_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        构建对话历史
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            history: 对话历史
        """
        if conversation_id not in self.conversations:
            return []
        
        conversation = self.conversations[conversation_id]
        history = []
        
        for msg in conversation["messages"]:
            if msg["sender"] == "system":
                history.append({"role": "system", "content": msg["content"]})
            else:
                # 获取agent名称
                agent_name = "Unknown"
                if msg["sender"] in conversation["agent_roles"]:
                    agent_name = conversation["agent_roles"][msg["sender"]]["agent_name"]
                
                history.append({
                    "role": "assistant",
                    "content": f"[{agent_name}]: {msg['content']}"
                })
        
        return history
    
    def _add_message(self, conversation_id: str, sender: str, content: str):
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话ID
            sender: 发送者
            content: 消息内容
        """
        if conversation_id not in self.conversations:
            return
        
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "message_index": len(self.conversations[conversation_id]["messages"])
        }
        
        self.conversations[conversation_id]["messages"].append(message)
    
    async def finalize_collaboration(self, conversation_id: str) -> Dict:
        """
        完成协作并生成最终结果
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            result: 协作结果
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        
        # 构建完整的对话历史
        conversation_history = self._build_conversation_history(conversation_id)
        
        # 生成最终总结
        summary_prompt = f"""
        基于以上的完整协作对话，请生成一个专业的任务完成报告，包括：
        
        1. 任务描述总结
        2. 各个Agent的贡献
        3. 解决方案的详细步骤
        4. 最终结果
        5. 建议和改进点
        
        请确保报告专业、详细且实用。
        """
        
        try:
            final_result = await self._call_chatgpt_api(
                "你是一个专业的项目总结专家，擅长分析团队协作过程并生成高质量的项目报告。",
                conversation_history,
                summary_prompt
            )
            
            # 生成对话摘要
            summary_prompt_short = "请用1-2句话总结这次协作对话的主要内容和结果。"
            conversation_summary = await self._call_chatgpt_api(
                "你是一个专业的内容总结专家。",
                conversation_history,
                summary_prompt_short
            )
            
            result = {
                "conversation_id": conversation_id,
                "task_id": conversation["task_id"],
                "final_result": final_result,
                "conversation_summary": conversation_summary,
                "participants": [agent["address"] for agent in conversation["agents"]],
                "message_count": len(conversation["messages"]),
                "completed_at": datetime.now().isoformat()
            }
            
            # 标记对话为完成
            conversation["status"] = "completed"
            conversation["final_result"] = result
            
            # 保存到历史记录
            self.conversation_history[conversation_id] = conversation
            
            return result
            
        except Exception as e:
            logger.error(f"Error finalizing collaboration: {e}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        获取对话信息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            conversation: 对话信息
        """
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        elif conversation_id in self.conversation_history:
            return self.conversation_history[conversation_id]
        else:
            return None
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """
        获取对话消息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            messages: 消息列表
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            return conversation.get("messages", [])
        return []


# 全局服务实例
collaboration_service = AgentCollaborationService()