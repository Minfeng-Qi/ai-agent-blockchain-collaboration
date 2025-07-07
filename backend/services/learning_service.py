"""
Service for learning-related operations.
"""
import logging
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import sys

from app.models.learning import (
    LearningMetrics, LearningUpdate, TaskResult,
    LearningEvent, LearningReport
)
from app.services.blockchain import blockchain_service
from app.services.agent_service import agent_service
from app.config import MODELS_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add agents directory to path for importing learning modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class LearningService:
    """
    Service for learning-related operations.
    """

    def __init__(self):
        """
        Initialize the learning service.
        """
        self.learning_integrations = {}
        self.ensure_models_dir()
    
    def ensure_models_dir(self):
        """
        Ensure the models directory exists.
        """
        os.makedirs(MODELS_DIR, exist_ok=True)
    
    async def get_learning_metrics(self, agent_address: str) -> Optional[LearningMetrics]:
        """
        Get learning metrics for an agent.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Learning metrics or None if not found.
        """
        try:
            # Try to load from state file first
            metrics = self._load_metrics_from_state(agent_address)
            if metrics:
                return metrics
            
            # If not found, create from blockchain data
            agent_info = await agent_service.get_agent(agent_address)
            if not agent_info:
                return None
            
            # Create default metrics
            return LearningMetrics(
                agent_address=agent_address,
                total_tasks=agent_info.tasks_completed + agent_info.tasks_failed,
                successful_tasks=agent_info.tasks_completed,
                failed_tasks=agent_info.tasks_failed,
                average_score=agent_info.average_score or 0.0,
                average_reward=agent_info.average_reward or 0.0,
                capability_growth={},
                confidence_factor=agent_info.confidence_factor,
                risk_tolerance=agent_info.risk_tolerance,
                learning_rate=0.001,
                exploration_rate=0.1,
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting learning metrics for agent {agent_address}: {e}")
            return None
    
    async def update_learning_parameters(
        self, 
        agent_address: str, 
        update_data: LearningUpdate
    ) -> Optional[LearningMetrics]:
        """
        Update learning parameters for an agent.
        
        Args:
            agent_address: The address of the agent.
            update_data: Updated learning parameters.
            
        Returns:
            Updated learning metrics or None if update fails.
        """
        try:
            # Get current metrics
            metrics = await self.get_learning_metrics(agent_address)
            if not metrics:
                return None
            
            # Update parameters
            if update_data.learning_rate is not None:
                metrics.learning_rate = update_data.learning_rate
                
            if update_data.exploration_rate is not None:
                metrics.exploration_rate = update_data.exploration_rate
                
            if update_data.confidence_factor is not None:
                metrics.confidence_factor = update_data.confidence_factor
                
                # Update on blockchain
                await blockchain_service.send_transaction(
                    'AgentRegistry',
                    'updateAgentParameters',
                    agent_address,
                    update_data.confidence_factor,
                    metrics.risk_tolerance
                )
                
            if update_data.risk_tolerance is not None:
                metrics.risk_tolerance = update_data.risk_tolerance
                
                # Update on blockchain
                await blockchain_service.send_transaction(
                    'AgentRegistry',
                    'updateAgentParameters',
                    agent_address,
                    metrics.confidence_factor,
                    update_data.risk_tolerance
                )
            
            # Update timestamp
            metrics.last_updated = datetime.now()
            
            # Save updated metrics
            self._save_metrics_to_state(agent_address, metrics)
            
            return metrics
        except Exception as e:
            logger.error(f"Error updating learning parameters for agent {agent_address}: {e}")
            return None
    
    async def process_task_result(
        self, 
        agent_address: str, 
        task_result: TaskResult
    ) -> Optional[Dict[str, Any]]:
        """
        Process a task result for learning.
        
        Args:
            agent_address: The address of the agent.
            task_result: Task result data.
            
        Returns:
            Processing result or None if processing fails.
        """
        try:
            # Get learning integration
            integration = await self._get_learning_integration(agent_address)
            if not integration:
                return None
            
            # Process task result
            integration.process_task_result(
                task_id=task_result.task_id,
                task_type=task_result.task_type,
                score=task_result.score,
                reward=task_result.reward,
                tags=task_result.tags
            )
            
            # Get updated capabilities
            updated_capabilities = integration.get_capabilities()
            
            # Update capabilities on blockchain
            tags = list(updated_capabilities.keys())
            weights = list(updated_capabilities.values())
            
            try:
                await blockchain_service.send_transaction(
                    'AgentRegistry',
                    'updateCapabilities',
                    agent_address,
                    tags,
                    weights
                )
            except Exception as e:
                logger.warning(f"Failed to update capabilities on blockchain: {e}")
                logger.info("Continuing with local capability updates only")
            
            # Save state
            integration.save_state()
            
            # Record learning event
            event_id = str(uuid.uuid4())
            event = LearningEvent(
                event_id=event_id,
                agent_address=agent_address,
                event_type="task_result",
                task_id=task_result.task_id,
                timestamp=datetime.now(),
                details={
                    "task_type": task_result.task_type,
                    "score": task_result.score,
                    "reward": task_result.reward,
                    "tags": task_result.tags
                },
                capability_changes=self._calculate_capability_changes(
                    integration.initial_capabilities,
                    updated_capabilities
                )
            )
            
            # Save event
            self._save_learning_event(agent_address, event)
            
            return {
                "event_id": event_id,
                "updated_capabilities": updated_capabilities,
                "capability_changes": event.capability_changes
            }
        except Exception as e:
            logger.error(f"Error processing task result for agent {agent_address}: {e}")
            return None
    
    async def generate_learning_report(self, agent_address: str) -> Optional[LearningReport]:
        """
        Generate a learning report for an agent.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Learning report or None if generation fails.
        """
        try:
            # Get learning integration
            integration = await self._get_learning_integration(agent_address)
            if not integration:
                return None
            
            # Get metrics
            metrics = await self.get_learning_metrics(agent_address)
            if not metrics:
                return None
            
            # Get capabilities
            capabilities = integration.get_capabilities()
            
            # Get recent events
            events = self._load_learning_events(agent_address)
            recent_events = sorted(
                events,
                key=lambda e: e.timestamp,
                reverse=True
            )[:10]
            
            # Calculate capability changes
            capability_changes = self._calculate_capability_changes(
                integration.initial_capabilities,
                capabilities
            )
            
            # Get task type distribution
            task_type_distribution = {}
            for event in events:
                if event.event_type == "task_result" and "task_type" in event.details:
                    task_type = event.details["task_type"]
                    if task_type in task_type_distribution:
                        task_type_distribution[task_type] += 1
                    else:
                        task_type_distribution[task_type] = 1
            
            # Calculate performance trend
            performance_trend = self._calculate_performance_trend(events)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                integration, metrics, capability_changes, performance_trend
            )
            
            # Create report
            report_id = str(uuid.uuid4())
            report = LearningReport(
                agent_address=agent_address,
                report_id=report_id,
                timestamp=datetime.now(),
                metrics=metrics,
                capabilities=capabilities,
                capability_changes=capability_changes,
                recent_events=recent_events,
                task_type_distribution=task_type_distribution,
                performance_trend=performance_trend,
                recommendations=recommendations
            )
            
            return report
        except Exception as e:
            logger.error(f"Error generating learning report for agent {agent_address}: {e}")
            return None
    
    async def _get_learning_integration(self, agent_address: str):
        """
        Get or create a learning integration for an agent.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Learning integration or None if creation fails.
        """
        # Check if already loaded
        if agent_address in self.learning_integrations:
            return self.learning_integrations[agent_address]
        
        try:
            # Import here to avoid circular imports
            from agents.learning_integration import LearningIntegration
            
            # Try to load existing state
            integration = LearningIntegration.load_state(agent_address)
            if integration:
                self.learning_integrations[agent_address] = integration
                return integration
            
            # If not found, create new integration
            agent_info = await agent_service.get_agent(agent_address)
            if not agent_info:
                return None
            
            # Create new integration
            from agents.reinforcement_learning import ReinforcementLearning
            
            rl_model = ReinforcementLearning(
                agent_address=agent_address,
                learning_rate=0.001,
                discount_factor=0.95,
                exploration_rate=0.1
            )
            
            integration = LearningIntegration(
                agent_address=agent_address,
                initial_capabilities=agent_info.capabilities,
                rl_model=rl_model,
                reputation=agent_info.reputation,
                confidence_factor=agent_info.confidence_factor,
                risk_tolerance=agent_info.risk_tolerance
            )
            
            self.learning_integrations[agent_address] = integration
            return integration
        except ImportError:
            logger.error("Failed to import learning modules")
            return None
        except Exception as e:
            logger.error(f"Error creating learning integration for agent {agent_address}: {e}")
            return None
    
    def _load_metrics_from_state(self, agent_address: str) -> Optional[LearningMetrics]:
        """
        Load learning metrics from state file.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            Learning metrics or None if not found.
        """
        state_file = os.path.join(MODELS_DIR, f"{agent_address}_state.json")
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            metrics_data = state_data.get('learning_metrics', {})
            if not metrics_data:
                return None
            
            # Convert timestamp string to datetime
            last_updated = datetime.fromisoformat(metrics_data.get('last_updated', ''))
            
            return LearningMetrics(
                agent_address=agent_address,
                total_tasks=metrics_data.get('total_tasks', 0),
                successful_tasks=metrics_data.get('successful_tasks', 0),
                failed_tasks=metrics_data.get('failed_tasks', 0),
                average_score=metrics_data.get('average_score', 0.0),
                average_reward=metrics_data.get('average_reward', 0.0),
                capability_growth=metrics_data.get('capability_growth', {}),
                confidence_factor=metrics_data.get('confidence_factor', 50),
                risk_tolerance=metrics_data.get('risk_tolerance', 50),
                learning_rate=metrics_data.get('learning_rate', 0.001),
                exploration_rate=metrics_data.get('exploration_rate', 0.1),
                last_updated=last_updated
            )
        except Exception as e:
            logger.error(f"Error loading metrics from state for agent {agent_address}: {e}")
            return None
    
    def _save_metrics_to_state(self, agent_address: str, metrics: LearningMetrics) -> bool:
        """
        Save learning metrics to state file.
        
        Args:
            agent_address: The address of the agent.
            metrics: Learning metrics to save.
            
        Returns:
            True if successful, False otherwise.
        """
        state_file = os.path.join(MODELS_DIR, f"{agent_address}_state.json")
        
        try:
            # Load existing state or create new
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
            else:
                state_data = {}
            
            # Update metrics in state
            state_data['learning_metrics'] = {
                'total_tasks': metrics.total_tasks,
                'successful_tasks': metrics.successful_tasks,
                'failed_tasks': metrics.failed_tasks,
                'average_score': metrics.average_score,
                'average_reward': metrics.average_reward,
                'capability_growth': metrics.capability_growth,
                'confidence_factor': metrics.confidence_factor,
                'risk_tolerance': metrics.risk_tolerance,
                'learning_rate': metrics.learning_rate,
                'exploration_rate': metrics.exploration_rate,
                'last_updated': metrics.last_updated.isoformat()
            }
            
            # Save state
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving metrics to state for agent {agent_address}: {e}")
            return False
    
    def _save_learning_event(self, agent_address: str, event: LearningEvent) -> bool:
        """
        Save a learning event to file.
        
        Args:
            agent_address: The address of the agent.
            event: Learning event to save.
            
        Returns:
            True if successful, False otherwise.
        """
        events_file = os.path.join(MODELS_DIR, f"{agent_address}_events.json")
        
        try:
            # Load existing events or create new
            if os.path.exists(events_file):
                with open(events_file, 'r') as f:
                    events_data = json.load(f)
            else:
                events_data = []
            
            # Add new event
            events_data.append({
                'event_id': event.event_id,
                'agent_address': event.agent_address,
                'event_type': event.event_type,
                'task_id': event.task_id,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details,
                'capability_changes': event.capability_changes
            })
            
            # Save events
            with open(events_file, 'w') as f:
                json.dump(events_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving learning event for agent {agent_address}: {e}")
            return False
    
    def _load_learning_events(self, agent_address: str) -> List[LearningEvent]:
        """
        Load learning events from file.
        
        Args:
            agent_address: The address of the agent.
            
        Returns:
            List of learning events.
        """
        events_file = os.path.join(MODELS_DIR, f"{agent_address}_events.json")
        
        if not os.path.exists(events_file):
            return []
        
        try:
            with open(events_file, 'r') as f:
                events_data = json.load(f)
            
            events = []
            for event_data in events_data:
                # Convert timestamp string to datetime
                timestamp = datetime.fromisoformat(event_data.get('timestamp', ''))
                
                events.append(LearningEvent(
                    event_id=event_data.get('event_id', ''),
                    agent_address=event_data.get('agent_address', ''),
                    event_type=event_data.get('event_type', ''),
                    task_id=event_data.get('task_id'),
                    timestamp=timestamp,
                    details=event_data.get('details', {}),
                    capability_changes=event_data.get('capability_changes', {})
                ))
            
            return events
        except Exception as e:
            logger.error(f"Error loading learning events for agent {agent_address}: {e}")
            return []
    
    def _calculate_capability_changes(
        self, 
        initial_capabilities: Dict[str, int], 
        current_capabilities: Dict[str, int]
    ) -> Dict[str, float]:
        """
        Calculate capability changes from initial to current.
        
        Args:
            initial_capabilities: Initial capability weights.
            current_capabilities: Current capability weights.
            
        Returns:
            Dictionary mapping capability names to change values.
        """
        changes = {}
        
        # Calculate changes for all capabilities
        all_capabilities = set(list(initial_capabilities.keys()) + list(current_capabilities.keys()))
        for capability in all_capabilities:
            initial = initial_capabilities.get(capability, 0)
            current = current_capabilities.get(capability, 0)
            changes[capability] = current - initial
        
        return changes
    
    def _calculate_performance_trend(self, events: List[LearningEvent]) -> Dict[str, List[float]]:
        """
        Calculate performance trend from events.
        
        Args:
            events: List of learning events.
            
        Returns:
            Dictionary mapping metrics to trend values.
        """
        # Filter task result events
        task_events = [
            event for event in events 
            if event.event_type == "task_result" and "score" in event.details
        ]
        
        # Sort by timestamp
        task_events.sort(key=lambda e: e.timestamp)
        
        # Calculate trends
        scores = [event.details["score"] for event in task_events]
        rewards = [event.details["reward"] for event in task_events]
        
        # Calculate moving averages if enough data
        score_trend = []
        reward_trend = []
        window_size = 5
        
        if len(scores) >= window_size:
            for i in range(len(scores) - window_size + 1):
                score_trend.append(sum(scores[i:i+window_size]) / window_size)
                reward_trend.append(sum(rewards[i:i+window_size]) / window_size)
        else:
            score_trend = scores
            reward_trend = rewards
        
        return {
            "scores": scores,
            "rewards": rewards,
            "score_trend": score_trend,
            "reward_trend": reward_trend
        }
    
    def _generate_recommendations(
        self, 
        integration, 
        metrics: LearningMetrics,
        capability_changes: Dict[str, float],
        performance_trend: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on learning data.
        
        Args:
            integration: Learning integration.
            metrics: Learning metrics.
            capability_changes: Capability changes.
            performance_trend: Performance trend.
            
        Returns:
            Dictionary of recommendations.
        """
        recommendations = {}
        
        # Identify strongest and weakest capabilities
        capabilities = integration.get_capabilities()
        if capabilities:
            sorted_capabilities = sorted(
                capabilities.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            recommendations["strongest_capabilities"] = [
                cap[0] for cap in sorted_capabilities[:2]
            ]
            
            recommendations["weakest_capabilities"] = [
                cap[0] for cap in sorted_capabilities[-2:]
            ]
        
        # Recommend task types to focus on
        if "weakest_capabilities" in recommendations:
            recommendations["recommended_task_types"] = recommendations["weakest_capabilities"]
        
        # Recommend learning parameter adjustments
        if performance_trend.get("score_trend") and len(performance_trend["score_trend"]) > 2:
            recent_trend = performance_trend["score_trend"][-3:]
            if all(x < y for x, y in zip(recent_trend, recent_trend[1:])):
                # Scores improving, reduce exploration
                recommendations["learning_rate_adjustment"] = "decrease"
                recommendations["exploration_rate_adjustment"] = "decrease"
            elif all(x > y for x, y in zip(recent_trend, recent_trend[1:])):
                # Scores declining, increase exploration
                recommendations["learning_rate_adjustment"] = "increase"
                recommendations["exploration_rate_adjustment"] = "increase"
        
        # Recommend confidence factor adjustment
        if metrics.average_score > 80:
            recommendations["confidence_factor_adjustment"] = "increase"
        elif metrics.average_score < 50:
            recommendations["confidence_factor_adjustment"] = "decrease"
        
        return recommendations


# Create a singleton instance
learning_service = LearningService()