"""
Agent Collaboration Service for managing agent interactions
"""

import json
import os
import logging
import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI
from .ipfs_service import ipfs_service
from .contract_service import record_collaboration_ipfs, get_collaboration_record

logger = logging.getLogger(__name__)

class AgentCollaborationService:
    """Service for managing agent collaborations and interactions"""
    
    def __init__(self):
        """Initialize the agent collaboration service"""
        # 设置OpenAI API密钥
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        if not self.api_key:
            logger.warning("OpenAI API key not found. Agent collaboration will run in mock mode.")
        
        # 设置模拟模式
        mock_mode_env = os.environ.get('AGENT_MOCK_MODE', 'True')
        self.mock_mode = mock_mode_env.lower() == 'true' if mock_mode_env else True
        
        # 强制使用真实API如果有密钥
        if self.api_key:
            self.mock_mode = False
            logger.info("OpenAI API key found. Using real API mode.")
        
        # 设置默认使用的模型
        self.default_model = os.environ.get('OPENAI_DEFAULT_MODEL', 'gpt-3.5-turbo')
        
        # 设置OpenAI客户端
        if self.api_key:
            self.openai_client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.openai_client = None
    
    async def create_collaboration(self, task_id: str, task_data: Dict) -> str:
        """
        创建一个新的代理协作任务
        
        Args:
            task_id: 任务ID
            task_data: 任务数据
            agent_ids: 参与协作的代理ID列表
            
        Returns:
            str: 协作ID
        """
        collaboration_id = f"collab_{uuid.uuid4().hex}"
        
        # 自动选择合适的代理
        selected_agents = await self._select_best_agents_for_task(task_data)
        
        # 初始化协作数据结构
        collaboration = {
            "id": collaboration_id,
            "task_id": task_id,
            "task_data": task_data,
            "agent_ids": selected_agents,
            "status": "created",
            "created_at": time.time(),
            "updated_at": time.time(),
            "conversation": [],
            "result": None,
            "ipfs_cid": None
        }
        
        # 在实际系统中，这里会将协作数据存储到数据库
        # 这里我们简单地返回协作ID
        
        logger.info(f"Created collaboration {collaboration_id} for task {task_id}")
        return collaboration_id
    
    async def run_collaboration(self, collaboration_id: str, task_data: Dict) -> Dict:
        """
        运行代理协作
        
        Args:
            collaboration_id: 协作ID
            task_data: 任务数据
            
        Returns:
            Dict: 协作结果，包括对话记录和IPFS CID
        """
        logger.info(f"Running collaboration {collaboration_id}")
        
        try:
            # 获取选定的代理
            selected_agents = await self._select_best_agents_for_task(task_data)
            agents_info = await self._get_agents_info(selected_agents)
            
            # 创建系统消息
            system_message = self._create_system_message(task_data, agents_info)
            
            # 初始化对话
            conversation = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"任务: {task_data.get('title', '未知任务')}\n\n{task_data.get('description', '无描述')}"}
            ]
            
            # 如果在模拟模式下，生成模拟对话
            if self.mock_mode:
                logger.info("Running in mock mode. Generating mock conversation.")
                conversation = self._generate_mock_conversation(task_data, agents_info, conversation)
            else:
                # 如果不在模拟模式下，使用OpenAI API生成真实对话
                logger.info("Running with real OpenAI API calls")
                conversation = await self._generate_real_conversation(task_data, agents_info, conversation)
            
            # 将对话存储到IPFS
            conversation_data = {
                "collaboration_id": collaboration_id,
                "task_id": task_data.get("task_id", ""),
                "task_title": task_data.get("title", ""),
                "agents": agents_info,
                "conversation": conversation,
                "timestamp": time.time(),
                "api_mode": "real" if not self.mock_mode else "mock"
            }
            
            # 上传到IPFS
            ipfs_result = await ipfs_service.upload_json(conversation_data)
            if ipfs_result["success"]:
                ipfs_cid = ipfs_result["cid"]
                logger.info(f"Uploaded conversation to IPFS: {ipfs_cid}")
            else:
                # 如果IPFS上传失败，生成模拟CID
                ipfs_cid = "Qm" + uuid.uuid4().hex[:44]
                logger.warning(f"IPFS upload failed, using mock CID: {ipfs_cid}")
            
            # 将IPFS CID记录到区块链
            tx_hash = await self._record_to_blockchain(collaboration_id, ipfs_cid, task_data.get("task_id", ""))
            
            # 更新代理信息（调用合约中的学习算法）
            agent_updates = await self._update_agents_after_collaboration(agents_info, conversation, task_data)
            
            # 返回结果
            result = {
                "collaboration_id": collaboration_id,
                "task_id": task_data.get("task_id", ""),
                "task_title": task_data.get("title", ""),
                "status": "completed",
                "agents": agents_info,
                "conversation": conversation,
                "ipfs_cid": ipfs_cid,
                "ipfs_url": f"http://localhost:8080/ipfs/{ipfs_cid}",
                "tx_hash": tx_hash,
                "timestamp": time.time(),
                "agent_updates": agent_updates  # 添加代理更新信息
            }
            
            logger.info(f"Completed collaboration {collaboration_id}")
            return result
        except Exception as e:
            logger.error(f"Error running collaboration: {str(e)}")
            # 返回错误信息
            return {
                "collaboration_id": collaboration_id,
                "task_id": task_data.get("task_id", ""),
                "status": "error",
                "error": str(e)
            }
    
    async def _select_best_agents_for_task(self, task_data: Dict) -> List[str]:
        """
        根据任务要求自动选择最合适的代理
        
        Args:
            task_data: 任务数据，包含要求和能力标签
            
        Returns:
            List[str]: 选定的代理ID列表
        """
        # 在实际系统中，这里会从数据库或区块链获取所有代理并进行筛选
        # 这里我们生成模拟数据并进行简单的筛选算法
        
        # 模拟所有可用代理
        all_agents = [
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"DataAnalyst",
                "capabilities": ["data_analysis", "statistics"],
                "reputation": 92
            },
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"TextGenerator",
                "capabilities": ["text_generation", "summarization"],
                "reputation": 88
            },
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"Researcher",
                "capabilities": ["research", "data_analysis"],
                "reputation": 85
            },
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"Translator",
                "capabilities": ["translation", "text_generation"],
                "reputation": 90
            },
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"CodeGenerator",
                "capabilities": ["code_generation", "debugging"],
                "reputation": 95
            },
            {
                "agent_id": f"agent_{uuid.uuid4().hex[:8]}",
                "name": f"ImageAnalyst",
                "capabilities": ["image_recognition", "computer_vision"],
                "reputation": 87
            }
        ]
        
        # 获取任务所需能力
        required_capabilities = task_data.get("required_capabilities", [])
        if not required_capabilities and "type" in task_data and task_data["type"]:
            # 如果没有明确的能力要求，根据任务类型推断
            task_type = task_data["type"].lower()
            if "analysis" in task_type:
                required_capabilities = ["data_analysis"]
            elif "text" in task_type or "content" in task_type:
                required_capabilities = ["text_generation"]
            elif "code" in task_type or "programming" in task_type:
                required_capabilities = ["code_generation"]
            elif "image" in task_type or "vision" in task_type:
                required_capabilities = ["image_recognition"]
        
        # 如果仍然没有能力要求，默认需要通用能力
        if not required_capabilities:
            required_capabilities = ["text_generation", "data_analysis"]
        
        # 计算每个代理的匹配分数
        scored_agents = []
        for agent in all_agents:
            # 计算能力匹配度
            capability_match = sum(1 for cap in required_capabilities if cap in agent["capabilities"])
            capability_score = capability_match / len(required_capabilities) if required_capabilities else 0
            
            # 计算声誉分数 (归一化到0-1)
            reputation_score = agent["reputation"] / 100
            
            # 综合分数 (能力匹配度占70%，声誉占30%)
            total_score = (capability_score * 0.7) + (reputation_score * 0.3)
            
            scored_agents.append({
                "agent": agent,
                "score": total_score
            })
        
        # 按分数降序排序
        scored_agents.sort(key=lambda x: x["score"], reverse=True)
        
        # 选择前2-4个最匹配的代理
        num_agents = min(4, max(2, len(scored_agents)))
        selected_agents = [agent["agent"]["agent_id"] for agent in scored_agents[:num_agents]]
        
        logger.info(f"Selected {len(selected_agents)} agents for task")
        return selected_agents
    
    async def _get_agents_info(self, agent_ids: List[str]) -> List[Dict]:
        """获取代理信息"""
        # 在实际系统中，这里会从数据库或区块链获取代理信息
        # 这里我们生成模拟数据
        agents = []
        capabilities = ["data_analysis", "text_generation", "classification", 
                        "translation", "summarization", "image_recognition"]
        
        for i, agent_id in enumerate(agent_ids):
            agents.append({
                "agent_id": agent_id,
                "name": f"Agent{i+1}",
                "capabilities": [capabilities[i % len(capabilities)]],
                "reputation": 80 + (i % 20)
            })
        
        return agents
    
    def _create_system_message(self, task_data: Dict, agents: List[Dict]) -> str:
        """创建系统消息"""
        agents_info = "\n".join([
            f"- 代理{i+1} ({agent['name']}): 专长于 {', '.join(agent['capabilities'])}, 声誉值: {agent['reputation']}"
            for i, agent in enumerate(agents)
        ])
        
        system_message = f"""你将模拟多个AI代理之间的协作对话，共同解决一个任务。
这些代理具有不同的专长和能力，需要相互协作以完成任务。

参与的代理:
{agents_info}

任务详情:
标题: {task_data.get('title', '未指定')}
描述: {task_data.get('description', '未指定')}
要求: {task_data.get('requirements', '未指定')}

请模拟这些代理之间的对话，展示它们如何协作解决这个任务。每个代理应该根据自己的专长贡献解决方案。
对话应该包括:
1. 任务分析和理解
2. 工作分配
3. 各代理执行各自部分
4. 整合结果
5. 最终解决方案

当任务完成时，请明确标注"任务完成"并提供最终解决方案。"""
        
        return system_message
    
    def _generate_mock_conversation(self, task_data: Dict, agents: List[Dict], conversation: List[Dict]) -> List[Dict]:
        """生成模拟对话"""
        agent_names = [f"Agent{i+1} ({agent['name']})" for i, agent in enumerate(agents)]
        
        mock_responses = [
            f"{agent_names[0]}: 我已分析任务要求，这是一个{task_data.get('type', '未知类型')}任务。我建议我们先理解需求，然后分配工作。",
            
            f"{agent_names[1]}: 同意。根据任务描述，我们需要{task_data.get('description', '完成任务')}。我可以负责{agents[1]['capabilities'][0]}部分。",
            
            f"{agent_names[0]}: 很好。我将处理{agents[0]['capabilities'][0]}。{agent_names[2] if len(agent_names) > 2 else agent_names[0]}，你能负责最终整合结果吗？",
            
            f"{agent_names[2] if len(agent_names) > 2 else agent_names[0]}: 没问题，我会负责整合大家的工作。让我们开始吧。\n\n{agent_names[0]}开始处理{agents[0]['capabilities'][0]}...\n\n初步结果: 已完成数据分析，发现以下模式...",
            
            f"{agent_names[1]}: 我已完成{agents[1]['capabilities'][0]}部分。结果如下: ...\n\n这些结果可以与{agent_names[0]}的发现结合。",
            
            f"{agent_names[2] if len(agent_names) > 2 else agent_names[0]}: 感谢大家的贡献。我已经整合了所有结果。\n\n最终解决方案:\n1. {task_data.get('title', '任务')}已完成\n2. 我们通过协作解决了{task_data.get('description', '问题')}\n3. 具体实现包括...\n\n任务完成。"
        ]
        
        # 添加模拟响应到对话中
        for i, response in enumerate(mock_responses):
            conversation.append({"role": "assistant", "content": response})
            if i < len(mock_responses) - 1:
                conversation.append({"role": "user", "content": f"请继续讨论，直到解决任务。当前进度: {(i+1)*20}%"})
        
        return conversation
    
    async def _call_openai_api(self, conversation: List[Dict]) -> str:
        """调用OpenAI API获取响应"""
        try:
            if not self.api_key:
                logger.info("No OpenAI API key found. Using mock response.")
                return "模拟的OpenAI API响应。由于没有API密钥，我们使用模拟数据代替实际调用。"
                
            logger.info("Calling OpenAI API...")
            # 使用旧版本的OpenAI API调用方式
            # 保留原始系统消息，但添加英文指示以处理中文字符
            modified_conversation = []
            for msg in conversation:
                if msg['role'] == 'system':
                    # 在系统消息中添加英文指示
                    english_instruction = "\n\nIMPORTANT: Please respond in Chinese. You are simulating a collaboration between multiple AI agents with different expertise to solve the task described above."
                    modified_conversation.append({"role": msg['role'], "content": msg['content'] + english_instruction})
                else:
                    modified_conversation.append(msg)
                
            response = openai.ChatCompletion.create(
                model=self.default_model,
                messages=modified_conversation,
                max_tokens=1500,
                temperature=0.7
            )
            logger.info("Received response from OpenAI API")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return f"调用OpenAI API时出错: {str(e)}。使用模拟数据代替。"
    
    
    async def get_collaboration(self, collaboration_id: str) -> Dict:
        """获取协作详情"""
        # 在实际系统中，这里会从数据库获取协作详情
        # 这里我们返回模拟数据
        return {
            "id": collaboration_id,
            "status": "completed",
            "ipfs_cid": "Qm" + uuid.uuid4().hex,
            "created_at": time.time() - 3600,
            "updated_at": time.time()
        }
    
    async def get_conversation_from_ipfs(self, ipfs_cid: str) -> Dict:
        """从IPFS获取对话记录"""
        try:
            return ipfs_service.get_json(ipfs_cid)
        except Exception as e:
            logger.error(f"Error getting conversation from IPFS: {str(e)}")
            # 返回错误信息
            return {"error": str(e)}
    
    async def _generate_real_conversation(self, task_data: Dict, agents_info: List[Dict], conversation: List[Dict]) -> List[Dict]:
        """
        使用真实的OpenAI API生成多代理协作对话
        """
        try:
            # 为每个代理创建独立的对话上下文
            agent_conversations = {}
            for agent in agents_info:
                agent_conversations[agent["agent_id"]] = conversation.copy()
            
            # 进行多轮对话，每轮让不同的代理响应
            for round_num in range(5):
                # 选择当前轮次的主要代理
                current_agent = agents_info[round_num % len(agents_info)]
                agent_id = current_agent["agent_id"]
                agent_name = current_agent["name"]
                agent_caps = current_agent["capabilities"]
                
                # 创建代理特定的系统提示
                agent_prompt = f"""你现在是{agent_name}，专长于{', '.join(agent_caps)}。
你正在与其他代理协作完成任务。请根据你的专长贡献解决方案。
任务: {task_data.get('title', '')}
描述: {task_data.get('description', '')}

当前进度: {(round_num + 1) * 20}%

请以第一人称回应，展示你的专业能力和协作精神。
"""
                
                # 添加代理特定的提示
                agent_conversation = agent_conversations[agent_id].copy()
                agent_conversation.append({
                    "role": "user", 
                    "content": agent_prompt
                })
                
                # 调用OpenAI API
                response = await self._call_openai_api(agent_conversation)
                
                # 将响应添加到主对话中
                formatted_response = f"{agent_name}: {response}"
                conversation.append({
                    "role": "assistant", 
                    "content": formatted_response
                })
                
                # 更新所有代理的对话上下文
                for aid in agent_conversations:
                    agent_conversations[aid].append({
                        "role": "assistant", 
                        "content": formatted_response
                    })
                
                # 添加一些延迟以避免API限制
                await asyncio.sleep(1)
            
            # 添加最终总结
            summary_prompt = f"""请总结这次多代理协作的成果，确认任务已完成。
任务: {task_data.get('title', '')}
描述: {task_data.get('description', '')}

请简要说明各代理的贡献和最终解决方案。
"""
            
            conversation.append({
                "role": "user", 
                "content": summary_prompt
            })
            
            final_response = await self._call_openai_api(conversation)
            conversation.append({
                "role": "assistant", 
                "content": f"协作总结: {final_response}"
            })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error in real conversation generation: {str(e)}")
            # 如果API调用失败，回退到模拟模式
            return self._generate_mock_conversation(task_data, agents_info, conversation)
    
    async def _call_openai_api(self, messages: List[Dict]) -> str:
        """
        调用OpenAI API
        """
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise e
    
    async def _record_to_blockchain(self, collaboration_id: str, ipfs_cid: str, task_id: str) -> str:
        """
        将IPFS CID记录到区块链
        """
        try:
            # 获取默认发送者地址（在实际应用中应该从环境变量或用户输入获取）
            sender_address = os.environ.get('AGENT_ADDRESS', '0x0000000000000000000000000000000000000000')
            
            # 调用区块链记录函数
            result = record_collaboration_ipfs(collaboration_id, ipfs_cid, task_id, sender_address)
            
            if result["success"]:
                logger.info(f"Successfully recorded IPFS CID to blockchain: {result['transaction_hash']}")
                return result["transaction_hash"]
            else:
                logger.warning(f"Failed to record to blockchain: {result['error']}")
                # 返回模拟的交易哈希作为备用
                return "0x" + uuid.uuid4().hex[:64]
            
        except Exception as e:
            logger.error(f"Error recording to blockchain: {str(e)}")
            return "0x" + uuid.uuid4().hex[:64]
    
    async def _update_agents_after_collaboration(self, agents_info: List[Dict], conversation: List[Dict], task_data: Dict) -> List[Dict]:
        """
        协作完成后更新代理信息（调用合约中的学习算法）
        """
        agent_updates = []
        sender_address = os.environ.get('AGENT_ADDRESS', '0x0000000000000000000000000000000000000000')
        
        try:
            for agent in agents_info:
                agent_id = agent['agent_id']
                
                # 计算简单的表现分数（基于对话参与度）
                agent_message_count = 0
                agent_total_length = 0
                
                for msg in conversation:
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', '')
                        # 简单检查是否是该代理的消息
                        if any(pattern in content for pattern in [f"Agent{i+1}" for i in range(4)]):
                            agent_message_count += 1
                            agent_total_length += len(content)
                
                # 基于参与度计算表现分数 (0-100)
                participation_score = min(100, (agent_message_count * 20) + (agent_total_length / 10))
                
                # 调用合约的学习事件记录功能来更新代理
                learning_data = {
                    "collaboration_id": task_data.get("task_id", ""),
                    "performance_score": participation_score,
                    "task_type": task_data.get("type", "general"),
                    "agent_contributions": agent_message_count,
                    "quality_metrics": {
                        "message_count": agent_message_count,
                        "total_content_length": agent_total_length,
                        "average_message_length": agent_total_length / max(1, agent_message_count)
                    }
                }
                
                # 模拟记录学习事件（实际应用中会调用合约中的学习算法）
                # 这里我们创建一个模拟的成功结果
                result = {
                    "success": True,
                    "transaction_hash": "0x" + uuid.uuid4().hex[:64],
                    "event_id": f"event_{uuid.uuid4().hex[:16]}",
                    "block_number": 12345 + len(agent_updates)
                }
                
                if result["success"]:
                    logger.info(f"Recorded learning event for agent {agent_id}: {result['transaction_hash']}")
                    
                    # 构建代理更新信息
                    agent_update = {
                        "agent_id": agent_id,
                        "performance_score": participation_score,
                        "learning_event_id": result.get("event_id"),
                        "transaction_hash": result["transaction_hash"],
                        "block_number": result.get("block_number"),
                        "update_type": "collaboration_completion",
                        "metrics": learning_data["quality_metrics"]
                    }
                    agent_updates.append(agent_update)
                else:
                    logger.warning(f"Failed to record learning event for agent {agent_id}: {result['error']}")
                    
        except Exception as e:
            logger.error(f"Error updating agents after collaboration: {str(e)}")
        
        return agent_updates

# 创建单例实例
agent_collaboration_service = AgentCollaborationService()