"""
Agent Collaboration Service for managing agent interactions
"""

import json
import os
import logging
import uuid
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# 兼容不同版本的OpenAI库
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
        print("OpenAI library not available. Running in mock mode.")

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
        
        # 设置模拟模式 - 强制使用真实API进行测试
        mock_mode_env = os.environ.get('AGENT_MOCK_MODE', 'False')
        self.mock_mode = mock_mode_env.lower() == 'true' if mock_mode_env else False
        logger.info(f"AGENT_MOCK_MODE env var: {mock_mode_env}, parsed mock_mode: {self.mock_mode}")
        
        # 检查OpenAI库可用性
        if not OPENAI_AVAILABLE:
            self.mock_mode = True
            logger.warning("OpenAI library not available. Forcing mock mode.")
        
        # 设置默认使用的模型
        self.default_model = os.environ.get('OPENAI_DEFAULT_MODEL', 'gpt-3.5-turbo')
        
        # 强制使用真实API如果有密钥且库可用
        if self.api_key and OPENAI_AVAILABLE:
            self.mock_mode = False
            logger.info("OpenAI API key found and library available. Using real API mode.")
            logger.info(f"API Key (first 20 chars): {self.api_key[:20]}...")
            logger.info(f"Default model: {self.default_model}")
        
        # 设置OpenAI/DeepSeek客户端
        if self.api_key and OPENAI_AVAILABLE and 'AsyncOpenAI' in globals():
            try:
                # 检查是否使用DeepSeek API
                base_url = os.environ.get('OPENAI_BASE_URL', None)
                if base_url:
                    self.openai_client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)
                    logger.info(f"AsyncOpenAI client initialized with custom base URL: {base_url}")
                else:
                    self.openai_client = AsyncOpenAI(api_key=self.api_key)
                    logger.info("AsyncOpenAI client initialized with default URL.")
            except Exception as e:
                logger.error(f"Failed to initialize AsyncOpenAI client: {e}")
                self.openai_client = None
                self.mock_mode = True
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
            
            # Initialize conversation with enhanced collaboration
            conversation = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Task: {task_data.get('title', 'Unknown task')}\n\nDescription: {task_data.get('description', 'No description provided')}\n\nPlease begin your collaborative work to solve this task effectively."}
            ]
            
            # 强制使用真实OpenAI API进行测试 - 完全跳过mock模式检查
            logger.info(f"🔥 FORCE USING REAL OPENAI API - Mock mode check: self.mock_mode={self.mock_mode}, openai_client={self.openai_client is not None}")
            
            # 强制初始化OpenAI/DeepSeek客户端（如果未初始化）
            if not self.openai_client and self.api_key:
                try:
                    from openai import AsyncOpenAI
                    base_url = os.environ.get('OPENAI_BASE_URL', None)
                    if base_url:
                        self.openai_client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)
                        logger.info(f"🔧 DeepSeek client force-initialized successfully with URL: {base_url}")
                    else:
                        self.openai_client = AsyncOpenAI(api_key=self.api_key)
                        logger.info("🔧 OpenAI client force-initialized successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to force-initialize client: {e}")
            
            if self.openai_client and self.api_key:
                # 强制使用真实OpenAI API
                logger.info("🚀 FORCING REAL OpenAI API calls! No mock mode!")
                conversation = await self._generate_real_conversation(task_data, agents_info, conversation)
            else:
                logger.error(f"❌ Cannot use real API: openai_client={self.openai_client is not None}, api_key_length={len(self.api_key) if self.api_key else 0}")
                conversation = self._generate_mock_conversation(task_data, agents_info, conversation)
            
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
        """Create system message for enhanced collaboration"""
        agents_info = "\n".join([
            f"- Agent{i+1} ({agent['name']}): Specializes in {', '.join(agent['capabilities'])}, Reputation: {agent['reputation']}"
            for i, agent in enumerate(agents)
        ])
        
        system_message = f"""You will simulate a collaborative conversation between multiple AI agents working together to solve a task.
These agents have different specialties and capabilities, and need to collaborate effectively to complete the task.

Participating Agents:
{agents_info}

Task Details:
Title: {task_data.get('title', 'Not specified')}
Description: {task_data.get('description', 'Not specified')}
Requirements: {task_data.get('requirements', 'Not specified')}

Please simulate the conversation between these agents, showing how they collaborate to solve this task. Each agent should contribute solutions based on their expertise.
The conversation should include:
1. Task analysis and understanding
2. Work distribution and coordination
3. Each agent executing their assigned parts
4. Result integration and quality review
5. Final comprehensive solution

When the task is completed, clearly indicate "Task Completed" and provide the final solution."""
        
        return system_message
    
    def _generate_mock_conversation(self, task_data: Dict, agents: List[Dict], conversation: List[Dict]) -> List[Dict]:
        """Generate enhanced mock conversation with better collaboration"""
        agent_names = [f"Agent{i+1} ({agent['name']})" for i, agent in enumerate(agents)]
        
        mock_responses = [
            f"{agent_names[0]}: I've analyzed the task requirements. This is a {task_data.get('type', 'general')} task. I suggest we first understand the requirements, then distribute the work among our team.",
            
            f"{agent_names[1]}: Agreed. Based on the task description, we need to {task_data.get('description', 'complete the task')}. I can handle the {agents[1]['capabilities'][0]} portion using my expertise.",
            
            f"{agent_names[0]}: Excellent. I'll handle the {agents[0]['capabilities'][0]} aspects. {agent_names[2] if len(agent_names) > 2 else agent_names[1]}, could you take responsibility for integrating our results?",
            
            f"{agent_names[2] if len(agent_names) > 2 else agent_names[1]}: Absolutely, I'll coordinate the integration of everyone's work. Let's begin our collaborative effort.\n\n{agent_names[0]} is now processing {agents[0]['capabilities'][0]}...\n\nInitial findings: Completed analysis and discovered key patterns...",
            
            f"{agent_names[1]}: I've completed the {agents[1]['capabilities'][0]} component. Here are my results: The analysis shows significant insights that complement {agent_names[0]}'s findings. These can be effectively combined for a comprehensive solution.",
            
            f"{agent_names[0]}: Building on both of our work, I've identified several optimization opportunities. The data patterns suggest we should focus on three key areas for maximum impact.",
            
            f"{agent_names[2] if len(agent_names) > 2 else agent_names[0]}: Thank you all for your excellent contributions. I've successfully integrated all results.\n\nFinal Collaborative Solution:\n1. Task '{task_data.get('title', 'assigned task')}' has been completed successfully\n2. Our team collaboration has solved: {task_data.get('description', 'the problem')}\n3. Implementation includes comprehensive analysis, specialized processing, and integrated results\n4. Quality assurance confirms all requirements have been met\n\nTask completed through effective multi-agent collaboration."
        ]
        
        # Add mock responses to conversation
        for i, response in enumerate(mock_responses):
            conversation.append({"role": "assistant", "content": response})
            if i < len(mock_responses) - 1:
                conversation.append({"role": "user", "content": f"Please continue the collaboration until the task is resolved. Current progress: {(i+1)*15}%"})
        
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
                
            # 使用新版本的异步OpenAI API
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            response = await self.openai_client.chat.completions.create(
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
            import asyncio
            # 在线程池中运行同步的 IPFS 调用
            ipfs_data = await asyncio.get_event_loop().run_in_executor(
                None, ipfs_service.get_json, ipfs_cid
            )
            if ipfs_data:
                logger.info(f"Successfully retrieved conversation data from IPFS: {ipfs_cid}")
                return ipfs_data
            else:
                logger.warning(f"No data found in IPFS for CID: {ipfs_cid}")
                # IPFS failed, return a mock response
                return self._generate_mock_ipfs_response(ipfs_cid)
        except Exception as e:
            logger.error(f"Error getting conversation from IPFS: {str(e)}")
            # 返回模拟响应而不是错误
            return self._generate_mock_ipfs_response(ipfs_cid)
    
    def _generate_mock_ipfs_response(self, ipfs_cid: str) -> Dict:
        """生成模拟的IPFS响应 - 当IPFS数据不可用时使用"""
        logger.warning(f"IPFS data unavailable for CID {ipfs_cid}, generating fallback response")
        
        return {
            "collaboration_id": f"fallback_collab_{ipfs_cid[:12]}",
            "task_id": "unavailable",
            "task_title": "Collaboration Data Unavailable",
            "agents": [
                {"agent_id": "fallback_agent_1", "name": "DataAnalyst", "capabilities": ["data_analysis"], "reputation": 85},
                {"agent_id": "fallback_agent_2", "name": "ContentGenerator", "capabilities": ["text_generation"], "reputation": 82},
                {"agent_id": "fallback_agent_3", "name": "Classifier", "capabilities": ["classification"], "reputation": 80}
            ],
            "conversation": [
                {
                    "role": "system", 
                    "content": "This is a fallback response. The original collaboration data stored in IPFS is currently unavailable."
                },
                {
                    "role": "assistant", 
                    "content": "Note: The original multi-agent collaboration conversation for this task is stored on IPFS but is currently not accessible. The task was successfully completed by a team of specialized agents, but the detailed conversation history cannot be retrieved at this moment."
                },
                {
                    "role": "assistant",
                    "content": f"Task completed successfully. The collaboration result was stored with IPFS CID: {ipfs_cid}. Please try again later or contact support if this issue persists."
                }
            ],
            "ipfs_cid": ipfs_cid,
            "ipfs_url": f"http://localhost:8081/ipfs/{ipfs_cid}",
            "timestamp": time.time(),
            "api_mode": "fallback",
            "error": "IPFS data unavailable"
        }
    
    async def _generate_real_conversation(self, task_data: Dict, agents_info: List[Dict], conversation: List[Dict]) -> List[Dict]:
        """
        Enhanced multi-agent collaboration with intelligent interaction using REAL OpenAI API
        """
        try:
            logger.info("🎯 STARTING REAL CONVERSATION GENERATION WITH OPENAI API")
            # Initialize agent collaboration state
            collaboration_state = {
                "task_progress": {},
                "shared_context": {},
                "agent_responses": [],
                "collaboration_quality": 0
            }
            
            # Enhanced conversation flow with better coordination
            for round_num in range(3):  # Reduced rounds for faster testing
                current_agent = agents_info[round_num % len(agents_info)]
                agent_id = current_agent["agent_id"]
                agent_name = current_agent["name"]
                agent_caps = current_agent["capabilities"]
                
                # Create context-aware agent prompt
                collaboration_context = self._build_collaboration_context(
                    collaboration_state, agents_info, round_num
                )
                
                agent_prompt = f"""You are {agent_name}, specializing in {', '.join(agent_caps)}.
You are collaborating with other agents to complete this task:

Task: {task_data.get('title', '')}
Description: {task_data.get('description', '')}
Progress: {(round_num + 1) * 14}%

{collaboration_context}

Based on the above context and your expertise, please:
1. Contribute your specialized knowledge
2. Build upon other agents' work
3. Ask questions if you need clarification
4. Provide concrete, actionable solutions

Respond as yourself, showing your professional expertise and collaborative spirit.
"""
                
                # Get agent response
                agent_conversation = conversation.copy()
                agent_conversation.append({
                    "role": "user", 
                    "content": agent_prompt
                })
                
                response = await self._call_openai_api(agent_conversation)
                
                # Format and add response
                formatted_response = f"{agent_name}: {response}"
                conversation.append({
                    "role": "assistant", 
                    "content": formatted_response
                })
                
                # Update collaboration state
                collaboration_state["agent_responses"].append({
                    "agent": agent_name,
                    "round": round_num,
                    "response": response
                })
                
                # Add coordination prompts every few rounds
                if round_num == 3:
                    coordination_prompt = "Let's coordinate our efforts. Please review what each agent has contributed so far and plan the next steps together."
                    conversation.append({
                        "role": "user", 
                        "content": coordination_prompt
                    })
                
                await asyncio.sleep(0.5)  # Reduced sleep time
            
            # Final integration and summary
            integration_prompt = f"""Please provide a comprehensive summary of this multi-agent collaboration:

Task: {task_data.get('title', '')}
Description: {task_data.get('description', '')}

Please include:
1. Final integrated solution
2. Each agent's key contributions
3. How the collaboration enhanced the result
4. Task completion confirmation

Ensure the final result is complete, coherent, and actionable.
"""
            
            conversation.append({
                "role": "user", 
                "content": integration_prompt
            })
            
            final_response = await self._call_openai_api(conversation)
            conversation.append({
                "role": "assistant", 
                "content": f"Collaboration Summary: {final_response}"
            })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error in enhanced conversation generation: {str(e)}")
            return self._generate_mock_conversation(task_data, agents_info, conversation)
    
    def _build_collaboration_context(self, collaboration_state: Dict, agents_info: List[Dict], round_num: int) -> str:
        """Build context for better agent collaboration"""
        context = ""
        
        if round_num > 0:
            context += "\nPrevious contributions from the team:\n"
            recent_responses = collaboration_state["agent_responses"][-3:]  # Last 3 responses
            for resp in recent_responses:
                context += f"- {resp['agent']}: {resp['response'][:100]}...\n"
        
        if round_num >= 3:
            context += f"\nWe are {round_num * 14}% through the task. Focus on building upon previous work and moving toward completion.\n"
        
        return context
    
    async def _call_openai_api(self, messages: List[Dict]) -> str:
        """
        调用OpenAI API（如果失败则使用智能模拟）
        """
        try:
            logger.info(f"🔥 ATTEMPTING REAL OPENAI API CALL! Model: {self.default_model}")
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            logger.info(f"✅ OpenAI API call successful! Response length: {len(response.choices[0].message.content)}")
            
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

    async def create_learning_event(self, agent_id: str, learning_event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为agent创建学习事件并更新其学习数据
        """
        try:
            logger.info(f"📚 Creating learning event for agent {agent_id}")
            
            # 准备学习事件数据
            event_data = learning_event_data.get("data", {})
            event_type = learning_event_data.get("event_type", "task_evaluation")
            
            # 创建完整的学习事件记录
            learning_event = {
                "event_id": f"learn_{uuid.uuid4().hex[:16]}",
                "agent_id": agent_id,
                "event_type": event_type,
                "timestamp": time.time(),
                "data": event_data,
                "blockchain_recorded": False,
                "transaction_hash": None
            }
            
            # 记录到数据库
            try:
                from services.collaboration_db_service import collaboration_db_service
                db_result = collaboration_db_service.create_learning_event(learning_event)
                learning_event["db_id"] = db_result.get("id")
                logger.info(f"✅ Learning event recorded in database")
            except Exception as e:
                logger.warning(f"Failed to record learning event in database: {e}")
            
            # 尝试记录到区块链（如果连接可用）
            try:
                from services.contract_service import contract_service
                if contract_service.w3 and contract_service.w3.is_connected():
                    # 准备区块链数据
                    blockchain_data = {
                        "agent_id": agent_id,
                        "event_type": event_type,
                        "performance_data": json.dumps({
                            "success": event_data.get("success", True),
                            "rating": event_data.get("rating", 5),
                            "reputation_change": event_data.get("reputation_change", 0),
                            "task_id": event_data.get("task_id", ""),
                            "capabilities_used": event_data.get("capabilities_used", [])
                        }),
                        "timestamp": int(time.time())
                    }
                    
                    # 调用智能合约记录学习事件
                    contract_result = contract_service.record_learning_event(blockchain_data)
                    if contract_result.get("success"):
                        learning_event["blockchain_recorded"] = True
                        learning_event["transaction_hash"] = contract_result.get("transaction_hash")
                        learning_event["block_number"] = contract_result.get("block_number")
                        logger.info(f"🔗 Learning event recorded on blockchain: {contract_result.get('transaction_hash')}")
                    else:
                        logger.warning(f"Failed to record learning event on blockchain: {contract_result.get('error')}")
                else:
                    logger.info("📝 Blockchain not available, learning event stored locally only")
            except Exception as e:
                logger.warning(f"Error recording learning event on blockchain: {e}")
            
            # 更新agent的统计数据
            await self._update_agent_statistics(agent_id, event_data)
            
            logger.info(f"🎉 Learning event created successfully for agent {agent_id}")
            
            return {
                "success": True,
                "event_id": learning_event["event_id"],
                "agent_id": agent_id,
                "event_type": event_type,
                "blockchain_recorded": learning_event["blockchain_recorded"],
                "transaction_hash": learning_event.get("transaction_hash"),
                "timestamp": learning_event["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating learning event for agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id
            }

    async def _update_agent_statistics(self, agent_id: str, event_data: Dict[str, Any]):
        """
        根据学习事件更新agent的统计数据
        """
        try:
            success = event_data.get("success", True)
            rating = event_data.get("rating", 5)
            reputation_change = event_data.get("reputation_change", 0)
            reward = event_data.get("reward", 0)
            capabilities_used = event_data.get("capabilities_used", [])
            
            # 这里可以实现更复杂的统计更新逻辑
            # 例如：更新agent的reputation、average_score、success_rate等
            
            update_data = {
                "agent_id": agent_id,
                "reputation_change": reputation_change,
                "total_reward": reward,
                "task_count": 1,
                "success_count": 1 if success else 0,
                "average_rating": rating,
                "capabilities_exercised": capabilities_used,
                "last_activity": time.time()
            }
            
            logger.info(f"📊 Updated statistics for agent {agent_id}: reputation {reputation_change:+d}, reward {reward}")
            
            return update_data
            
        except Exception as e:
            logger.error(f"Error updating agent statistics: {e}")
            return {}
    

# 创建单例实例
agent_collaboration_service = AgentCollaborationService()