"""
Service for agent-related operations.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.agent import AgentCreate, AgentUpdate, AgentResponse, AgentList
from app.services.blockchain import blockchain_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentService:
    """
    Service for agent-related operations.
    """

    async def get_agents(self, skip: int = 0, limit: int = 100) -> AgentList:
        """
        Get a list of agents.
        
        Args:
            skip: Number of agents to skip.
            limit: Maximum number of agents to return.
            
        Returns:
            List of agents.
        """
        try:
            # Get agent addresses from registry
            agent_addresses = await blockchain_service.call_contract(
                'AgentRegistry',
                'getAllAgents'
            )
            
            total = len(agent_addresses)
            
            # Apply pagination
            agent_addresses = agent_addresses[skip:skip + limit]
            
            # Get agent details
            agents = []
            for address in agent_addresses:
                agent_info = await blockchain_service.get_agent_info(address)
                if 'error' not in agent_info:
                    agents.append(self._format_agent_response(agent_info))
            
            return AgentList(agents=agents, total=total)
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return AgentList(agents=[], total=0)
    
    async def get_agent(self, agent_address: str) -> Optional[AgentResponse]:
        """
        Get an agent by address.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Agent information or None if not found.
        """
        try:
            agent_info = await blockchain_service.get_agent_info(agent_address)
            if 'error' in agent_info:
                return None
                
            return self._format_agent_response(agent_info)
        except Exception as e:
            logger.error(f"Error getting agent {agent_address}: {e}")
            return None
    
    async def create_agent(self, agent_data: AgentCreate) -> Optional[AgentResponse]:
        """
        Register a new agent.
        
        Args:
            agent_data: Agent data for registration.
            
        Returns:
            Registered agent information or None if registration fails.
        """
        try:
            # Extract capability tags and weights
            tags = list(agent_data.capabilities.keys())
            weights = list(agent_data.capabilities.values())
            
            # Register agent on blockchain
            tx_receipt = await blockchain_service.send_transaction(
                'AgentRegistry',
                'registerAgent',
                agent_data.address,
                agent_data.public_key,
                tags,
                weights
            )
            
            if tx_receipt['status'] == 1:
                # Get the registered agent
                agent_info = await blockchain_service.get_agent_info(agent_data.address)
                
                # Update confidence factor and risk tolerance
                if agent_data.confidence_factor is not None or agent_data.risk_tolerance is not None:
                    await blockchain_service.send_transaction(
                        'AgentRegistry',
                        'updateAgentParameters',
                        agent_data.address,
                        agent_data.confidence_factor or 50,
                        agent_data.risk_tolerance or 50
                    )
                
                return self._format_agent_response(agent_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    async def update_agent(self, agent_address: str, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """
        Update an agent.
        
        Args:
            agent_address: The address of the agent to update.
            agent_data: Updated agent data.
            
        Returns:
            Updated agent information or None if update fails.
        """
        try:
            # Update capabilities if provided
            if agent_data.capabilities is not None:
                tags = list(agent_data.capabilities.keys())
                weights = list(agent_data.capabilities.values())
                
                await blockchain_service.send_transaction(
                    'AgentRegistry',
                    'updateCapabilities',
                    agent_address,
                    tags,
                    weights
                )
            
            # Update parameters if provided
            if agent_data.confidence_factor is not None or agent_data.risk_tolerance is not None:
                current_agent = await self.get_agent(agent_address)
                if current_agent:
                    await blockchain_service.send_transaction(
                        'AgentRegistry',
                        'updateAgentParameters',
                        agent_address,
                        agent_data.confidence_factor or current_agent.confidence_factor,
                        agent_data.risk_tolerance or current_agent.risk_tolerance
                    )
            
            # Get updated agent info
            agent_info = await blockchain_service.get_agent_info(agent_address)
            return self._format_agent_response(agent_info)
        except Exception as e:
            logger.error(f"Error updating agent {agent_address}: {e}")
            return None
    
    async def update_agent_capabilities(
        self, 
        agent_address: str, 
        capabilities: Dict[str, int]
    ) -> Optional[AgentResponse]:
        """
        Update agent capabilities.
        
        Args:
            agent_address: The address of the agent.
            capabilities: Dictionary mapping capability names to weights.
            
        Returns:
            Updated agent information or None if update fails.
        """
        try:
            tags = list(capabilities.keys())
            weights = list(capabilities.values())
            
            tx_receipt = await blockchain_service.send_transaction(
                'AgentRegistry',
                'updateCapabilities',
                agent_address,
                tags,
                weights
            )
            
            if tx_receipt['status'] == 1:
                agent_info = await blockchain_service.get_agent_info(agent_address)
                return self._format_agent_response(agent_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error updating capabilities for agent {agent_address}: {e}")
            return None
    
    async def get_agent_capabilities(self, agent_address: str) -> Dict[str, int]:
        """
        Get agent capabilities.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Dictionary mapping capability names to weights.
        """
        try:
            capabilities = await blockchain_service.call_contract(
                'AgentRegistry',
                'getCapabilities',
                agent_address
            )
            
            return blockchain_service._parse_capabilities(capabilities)
        except Exception as e:
            logger.error(f"Error getting capabilities for agent {agent_address}: {e}")
            return {}
    
    def _format_agent_response(self, agent_info: Dict[str, Any]) -> AgentResponse:
        """
        Format agent information for API response.
        
        Args:
            agent_info: Raw agent information.
            
        Returns:
            Formatted agent response.
        """
        # Calculate derived metrics
        total_tasks = agent_info.get('tasks_completed', 0) + agent_info.get('tasks_failed', 0)
        average_score = 0
        average_reward = 0
        
        if total_tasks > 0:
            average_score = agent_info.get('total_score', 0) / total_tasks
            average_reward = agent_info.get('total_rewards', 0) / total_tasks
        
        # Create response object
        return AgentResponse(
            address=agent_info['address'],
            public_key=agent_info['public_key'],
            capabilities=agent_info['capabilities'],
            reputation=agent_info.get('reputation', 50),
            workload=agent_info.get('workload', 0),
            confidence_factor=agent_info.get('confidence_factor', 50),
            risk_tolerance=agent_info.get('risk_tolerance', 50),
            tasks_completed=agent_info.get('tasks_completed', 0),
            tasks_failed=agent_info.get('tasks_failed', 0),
            total_rewards=agent_info.get('total_rewards', 0),
            registration_date=datetime.fromtimestamp(agent_info.get('registration_timestamp', 0)),
            last_updated=datetime.fromtimestamp(agent_info.get('last_updated_timestamp', 0)),
            average_score=average_score,
            average_reward=average_reward,
            task_type_distribution=agent_info.get('task_type_distribution', {}),
            learning_metrics=agent_info.get('learning_metrics', {})
        )


# Create a singleton instance
agent_service = AgentService()