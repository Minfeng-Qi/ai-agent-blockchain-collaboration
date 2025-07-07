import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import re

import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("OpenAIIntegration")

class OpenAIIntegration:
    """
    Handles integration with OpenAI's API for LLM agent functionality.
    This class provides methods for task evaluation, execution, and capability assessment.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI integration with API key.
        
        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set API key for the openai module
        openai.api_key = self.api_key
        logger.info("OpenAI integration initialized")
    
    async def evaluate_task_fit(
        self, 
        agent_capabilities: List[str],
        task_description: str,
        task_requirements: List[str]
    ) -> float:
        """
        Evaluate how well an agent's capabilities match a task's requirements.
        
        Args:
            agent_capabilities: List of agent's capabilities
            task_description: Description of the task
            task_requirements: List of task's required capabilities
            
        Returns:
            Utility score between 0.0 and 1.0
        """
        prompt = f"""
        You are evaluating whether an AI agent with specific capabilities is suitable for a task.
        
        AGENT CAPABILITIES:
        {', '.join(agent_capabilities)}
        
        TASK DESCRIPTION:
        {task_description}
        
        TASK REQUIREMENTS:
        {', '.join(task_requirements)}
        
        Based on the agent's capabilities and the task requirements, assign a suitability score from 0.0 to 1.0,
        where 0.0 means completely unsuitable and 1.0 means perfectly suited.
        
        First, analyze the match between capabilities and requirements.
        Then, consider if the agent has the necessary skills for the task description.
        Finally, provide your score as a single decimal number between 0.0 and 1.0.
        
        SUITABILITY SCORE:
        """
        
        try:
            response = await self._async_completion(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI evaluator determining task suitability."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Extract the score from the response
            score_text = response.choices[0].message.content.strip()
            
            # Try to parse the score
            try:
                # Look for a decimal number in the response
                score_match = re.search(r'(\d+\.\d+|\d+)', score_text)
                if score_match:
                    score = float(score_match.group(1))
                    # Ensure score is between 0 and 1
                    score = max(0.0, min(1.0, score))
                    logger.info(f"Task evaluation score: {score}")
                    return score
                else:
                    logger.warning(f"Could not parse score from response: {score_text}")
                    return 0.5  # Default to neutral score
            except Exception as e:
                logger.error(f"Error parsing score: {e}")
                return 0.5  # Default to neutral score
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return 0.5  # Default to neutral score
    
    async def calculate_bid_amount(
        self,
        agent_capabilities: List[str],
        task_description: str,
        task_requirements: List[str],
        max_reward: float,
        agent_reputation: int,
        min_reputation: int,
        current_workload: int
    ) -> Tuple[float, str]:
        """
        Calculate a bid amount for a task based on agent capabilities and task requirements.
        
        Args:
            agent_capabilities: List of agent's capabilities
            task_description: Description of the task
            task_requirements: List of task's required capabilities
            max_reward: Maximum reward for the task
            agent_reputation: Agent's current reputation
            min_reputation: Minimum reputation required for the task
            current_workload: Agent's current workload
            
        Returns:
            Tuple of (bid_amount, reasoning)
        """
        prompt = f"""
        You are an AI agent deciding how much to bid for a task.
        
        AGENT CAPABILITIES:
        {', '.join(agent_capabilities)}
        
        AGENT REPUTATION: {agent_reputation} (Minimum required: {min_reputation})
        
        CURRENT WORKLOAD: {current_workload} tasks
        
        TASK DESCRIPTION:
        {task_description}
        
        TASK REQUIREMENTS:
        {', '.join(task_requirements)}
        
        MAXIMUM REWARD: {max_reward} ETH
        
        Based on the match between your capabilities and the task requirements, your reputation,
        current workload, and the maximum reward, decide on a bid amount.
        
        Consider:
        1. How well your capabilities match the requirements
        2. Your reputation compared to the minimum required
        3. Your current workload and capacity
        4. The competitive value of your bid
        
        Provide your bid as a number between 0 and {max_reward} ETH, and a brief explanation.
        
        BID AMOUNT AND REASONING:
        """
        
        try:
            response = await self._async_completion(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI agent bidding on tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=200
            )
            
            full_response = response.choices[0].message.content.strip()
            
            # Try to parse the bid amount
            try:
                # Look for a decimal number in the response
                bid_match = re.search(r'(\d+\.\d+|\d+)', full_response)
                if bid_match:
                    bid_amount = float(bid_match.group(1))
                    # Ensure bid is between 0 and max_reward
                    bid_amount = max(0.0, min(max_reward, bid_amount))
                    logger.info(f"Calculated bid amount: {bid_amount} ETH")
                    return bid_amount, full_response
                else:
                    logger.warning(f"Could not parse bid amount from response: {full_response}")
                    return max_reward * 0.8, full_response  # Default to 80% of max reward
            except Exception as e:
                logger.error(f"Error parsing bid amount: {e}")
                return max_reward * 0.8, full_response  # Default to 80% of max reward
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return max_reward * 0.8, f"Error calculating bid: {str(e)}"
    
    async def execute_task(
        self,
        agent_capabilities: List[str],
        agent_name: str,
        task_description: str,
        task_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Execute a task using the LLM.
        
        Args:
            agent_capabilities: List of agent's capabilities
            agent_name: Name of the agent
            task_description: Description of the task
            task_requirements: List of task's required capabilities
            
        Returns:
            Dictionary with task results
        """
        prompt = f"""
        You are {agent_name}, an AI agent with the following capabilities:
        {', '.join(agent_capabilities)}
        
        You have been assigned this task:
        
        TASK DESCRIPTION:
        {task_description}
        
        TASK REQUIREMENTS:
        {', '.join(task_requirements)}
        
        Please complete this task to the best of your abilities, focusing on your specialized capabilities.
        Provide a comprehensive response that fulfills all aspects of the task.
        
        YOUR RESPONSE:
        """
        
        try:
            response = await self._async_completion(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {agent_name}, an AI agent specialized in {', '.join(agent_capabilities)}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Create a structured response
            return {
                "status": "completed",
                "result": result,
                "metadata": {
                    "model": "gpt-4",
                    "completion_tokens": response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
                
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "result": "Task execution failed due to an error."
            }
    
    async def evaluate_task_result(
        self,
        task_description: str,
        task_requirements: List[str],
        task_result: str
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a task result.
        
        Args:
            task_description: Description of the task
            task_requirements: List of task's required capabilities
            task_result: The result produced by an agent
            
        Returns:
            Dictionary with evaluation scores and feedback
        """
        prompt = f"""
        You are evaluating the quality of a task result produced by an AI agent.
        
        TASK DESCRIPTION:
        {task_description}
        
        TASK REQUIREMENTS:
        {', '.join(task_requirements)}
        
        TASK RESULT:
        {task_result}
        
        Please evaluate the result on the following criteria:
        1. Completeness (0-100): Did the result address all aspects of the task?
        2. Quality (0-100): How well was the task executed?
        3. Relevance (0-100): How relevant was the result to the task requirements?
        4. Creativity (0-100): How creative or innovative was the approach?
        
        Also provide brief feedback on strengths and areas for improvement.
        
        Format your response as a JSON object with the following structure:
        {{
            "scores": {{
                "completeness": <score>,
                "quality": <score>,
                "relevance": <score>,
                "creativity": <score>,
                "overall": <average of all scores>
            }},
            "feedback": {{
                "strengths": ["strength1", "strength2", ...],
                "improvements": ["improvement1", "improvement2", ...]
            }}
        }}

        Only return the JSON object, nothing else.
        """
        
        try:
            response = await self._async_completion(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI evaluator assessing task results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                # Parse the JSON response
                evaluation = json.loads(result_text)
                logger.info(f"Task evaluation complete. Overall score: {evaluation['scores']['overall']}")
                return evaluation
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing evaluation JSON: {e}")
                # Return a default evaluation
                return {
                    "scores": {
                        "completeness": 50,
                        "quality": 50,
                        "relevance": 50,
                        "creativity": 50,
                        "overall": 50
                    },
                    "feedback": {
                        "strengths": ["Could not parse proper evaluation"],
                        "improvements": ["Error in evaluation process"]
                    },
                    "error": f"JSON parse error: {str(e)}",
                    "raw_response": result_text
                }
                
        except Exception as e:
            logger.error(f"Error evaluating task result: {e}")
            return {
                "scores": {
                    "completeness": 50,
                    "quality": 50,
                    "relevance": 50,
                    "creativity": 50,
                    "overall": 50
                },
                "feedback": {
                    "strengths": [],
                    "improvements": ["Evaluation failed due to an error"]
                },
                "error": str(e)
            }
    
    async def _async_completion(self, **kwargs):
        """
        Helper method to make async API calls to OpenAI.
        This is a wrapper around the OpenAI API to handle different versions.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: openai.ChatCompletion.create(**kwargs)
        )

# Example usage
async def test_openai_integration():
    api_key = "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"
    openai_integration = OpenAIIntegration(api_key)
    
    # Test task evaluation
    score = await openai_integration.evaluate_task_fit(
        agent_capabilities=["research", "writing", "data analysis"],
        task_description="Write a comprehensive analysis of blockchain governance models",
        task_requirements=["research", "writing", "blockchain"]
    )
    print(f"Task fit score: {score}")
    
    # Test bid calculation
    bid_amount, reasoning = await openai_integration.calculate_bid_amount(
        agent_capabilities=["research", "writing", "data analysis"],
        task_description="Write a comprehensive analysis of blockchain governance models",
        task_requirements=["research", "writing", "blockchain"],
        max_reward=0.2,
        agent_reputation=60,
        min_reputation=40,
        current_workload=2
    )
    print(f"Bid amount: {bid_amount} ETH")
    print(f"Reasoning: {reasoning}")
    
    # Test task execution
    result = await openai_integration.execute_task(
        agent_capabilities=["research", "writing", "data analysis"],
        agent_name="ResearchAgent",
        task_description="Write a short summary of blockchain governance models",
        task_requirements=["research", "writing", "blockchain"]
    )
    print(f"Task result status: {result['status']}")
    print(f"Task result: {result['result'][:100]}...")  # Show first 100 chars
    
    # Test result evaluation
    evaluation = await openai_integration.evaluate_task_result(
        task_description="Write a short summary of blockchain governance models",
        task_requirements=["research", "writing", "blockchain"],
        task_result=result['result']
    )
    print(f"Evaluation scores: {evaluation['scores']}")
    print(f"Strengths: {evaluation['feedback']['strengths']}")
    print(f"Improvements: {evaluation['feedback']['improvements']}")

if __name__ == "__main__":
    asyncio.run(test_openai_integration()) 