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
import openai
from .ipfs_service import ipfs_service
# from .contract_service import contract_service  # 已彻底注释

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
        self.mock_mode = os.environ.get('AGENT_MOCK_MODE', 'True').lower() == 'true'
        
        # 设置默认使用的模型
        self.default_model = os.environ.get('OPENAI_DEFAULT_MODEL', 'gpt-3.5-turbo')
        
        # 设置OpenAI客户端
        if self.api_key:
            openai.api_key = self.api_key
    
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
                # 生成初始响应
                initial_response = await self._call_openai_api(conversation)
                conversation.append({"role": "assistant", "content": initial_response})
                
                # 模拟多轮对话，共进行5轮
                for i in range(4):
                    # 添加用户提示，要求继续讨论
                    progress = (i + 1) * 20
                    conversation.append({"role": "user", "content": f"请继续讨论，直到解决任务。当前进度: {progress}%"})
                    
                    # 获取下一轮响应
                    next_response = await self._call_openai_api(conversation)
                    conversation.append({"role": "assistant", "content": next_response})
            
            # 将对话存储到IPFS
            conversation_json = json.dumps({
                "task_id": task_data.get("task_id", ""),
                "task_title": task_data.get("title", ""),
                "conversation": conversation,
                "timestamp": time.time()
            }, ensure_ascii=False)
            
            # 在实际系统中，这里会将对话上传到IPFS
            # 这里我们模拟一个IPFS CID
            ipfs_cid = "Qm" + uuid.uuid4().hex[:44]
            
            # 将IPFS CID记录到区块链
            tx_hash = await self._record_to_blockchain(collaboration_id, ipfs_cid, task_data.get("task_id", ""))
            
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
                "timestamp": time.time()
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
        if not required_capabilities and "type" in task_data:
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
    
    async def _record_to_blockchain(self, collaboration_id: str, ipfs_cid: str, task_id: str) -> str:
        """将IPFS CID记录到区块链"""
        try:
            # 在实际系统中，这里会调用智能合约将CID记录到区块链
            # 这里我们暂时不使用contract_service，直接模拟
            tx_hash = "0x" + uuid.uuid4().hex
            logger.info(f"Recorded IPFS CID {ipfs_cid} to blockchain, tx_hash: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.error(f"Error recording to blockchain: {str(e)}")
            # 返回模拟的交易哈希
            return "0x" + uuid.uuid4().hex
    
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

# 创建单例实例
agent_collaboration_service = AgentCollaborationService()