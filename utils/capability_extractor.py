import os
import logging
from typing import List, Dict, Any, Optional

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CapabilityExtractor:
    """
    Uses LLM to extract capabilities from agent descriptions or task requirements
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CapabilityExtractor
        
        Args:
            api_key: OpenAI API key (optional if set in environment)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        
        # Standard capability categories
        self.standard_capabilities = [
            "text_analysis",
            "code_generation",
            "data_processing",
            "language_translation",
            "summarization",
            "reasoning",
            "question_answering",
            "mathematical_reasoning",
            "problem_solving",
            "creative_writing",
            "dialogue_management",
            "information_retrieval",
            "knowledge_base_querying",
            "sentiment_analysis",
            "content_moderation",
            "image_understanding"
        ]
    
    async def extract_agent_capabilities(self, agent_description: str) -> List[str]:
        """
        Extract capabilities from an agent's description
        
        Args:
            agent_description: Text description of the agent's capabilities
            
        Returns:
            List of capability tags
        """
        prompt = f"""
        Given the following AI agent description, identify its capabilities from the standard list below.
        Return only the capability names as a comma-separated list, with no additional text.
        
        Standard capabilities:
        {", ".join(self.standard_capabilities)}
        
        Agent description:
        {agent_description}
        
        Capabilities (comma-separated list):
        """
        
        try:
            response = await openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=100
            )
            
            capabilities_text = response.choices[0].message.content.strip()
            capabilities = [c.strip() for c in capabilities_text.split(",")]
            
            # Filter to ensure only valid capabilities are returned
            valid_capabilities = [c for c in capabilities if c in self.standard_capabilities]
            
            logger.info(f"Extracted capabilities: {valid_capabilities}")
            return valid_capabilities
            
        except Exception as e:
            logger.error(f"Error extracting capabilities: {e}")
            # Return a subset of generic capabilities as fallback
            return ["text_analysis", "reasoning", "problem_solving"]
    
    async def extract_task_requirements(self, task_description: str) -> List[str]:
        """
        Extract capability requirements from a task description
        
        Args:
            task_description: Description of the task
            
        Returns:
            List of required capability tags
        """
        prompt = f"""
        Given the following task description, identify the capabilities an AI agent would need from the standard list below.
        Return only the capability names as a comma-separated list, with no additional text.
        
        Standard capabilities:
        {", ".join(self.standard_capabilities)}
        
        Task description:
        {task_description}
        
        Required capabilities (comma-separated list):
        """
        
        try:
            response = await openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=100
            )
            
            capabilities_text = response.choices[0].message.content.strip()
            capabilities = [c.strip() for c in capabilities_text.split(",")]
            
            # Filter to ensure only valid capabilities are returned
            valid_capabilities = [c for c in capabilities if c in self.standard_capabilities]
            
            logger.info(f"Extracted task requirements: {valid_capabilities}")
            return valid_capabilities
            
        except Exception as e:
            logger.error(f"Error extracting task requirements: {e}")
            # Return a subset of generic capabilities as fallback
            return ["text_analysis", "reasoning"]
    
    async def calculate_capability_match(
        self, agent_capabilities: List[str], task_requirements: List[str]
    ) -> float:
        """
        Calculate the match score between agent capabilities and task requirements
        
        Args:
            agent_capabilities: List of agent capabilities
            task_requirements: List of task requirements
            
        Returns:
            Match score from 0.0 to 1.0
        """
        # Simple matching algorithm - count how many requirements are satisfied by agent capabilities
        matched_requirements = [req for req in task_requirements if req in agent_capabilities]
        
        if not task_requirements:
            return 0.0
            
        match_score = len(matched_requirements) / len(task_requirements)
        
        logger.info(f"Capability match score: {match_score}")
        return match_score