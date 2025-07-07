"""
Service for task-related operations.
"""
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.task import (
    TaskCreate, TaskUpdate, TaskAssign, TaskComplete,
    TaskResponse, TaskList, TaskStats, TaskStatus
)
from app.services.blockchain import blockchain_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskService:
    """
    Service for task-related operations.
    """

    async def get_tasks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> TaskList:
        """
        Get a list of tasks.
        
        Args:
            skip: Number of tasks to skip.
            limit: Maximum number of tasks to return.
            status: Filter tasks by status.
            
        Returns:
            List of tasks.
        """
        try:
            # Get task IDs from contract
            if status == 'available':
                task_ids = await blockchain_service.call_contract(
                    'TaskManager',
                    'getAvailableTasks'
                )
            elif status == 'assigned':
                task_ids = await blockchain_service.call_contract(
                    'TaskManager',
                    'getAssignedTasks'
                )
            else:
                task_ids = await blockchain_service.call_contract(
                    'TaskManager',
                    'getAllTasks'
                )
            
            total = len(task_ids)
            
            # Apply pagination
            task_ids = task_ids[skip:skip + limit]
            
            # Get task details
            tasks = []
            for task_id in task_ids:
                task_info = await blockchain_service.get_task_info(task_id)
                if 'error' not in task_info:
                    # Filter by status if provided
                    if status and task_info['status'] != status:
                        continue
                    tasks.append(self._format_task_response(task_info))
            
            return TaskList(tasks=tasks, total=total)
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return TaskList(tasks=[], total=0)
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get a task by ID.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            Task information or None if not found.
        """
        try:
            task_info = await blockchain_service.get_task_info(task_id)
            if 'error' in task_info:
                return None
                
            return self._format_task_response(task_info)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    async def create_task(self, task_data: TaskCreate) -> Optional[TaskResponse]:
        """
        Create a new task.
        
        Args:
            task_data: Task data for creation.
            
        Returns:
            Created task information or None if creation fails.
        """
        try:
            # Generate a unique task ID
            task_id = str(uuid.uuid4())
            
            # Extract tags and weights
            tags = list(task_data.tags.keys())
            weights = list(task_data.tags.values())
            
            # Create task on blockchain
            tx_receipt = await blockchain_service.send_transaction(
                'TaskManager',
                'createTask',
                task_id,
                task_data.title,
                task_data.description,
                task_data.task_type.value,
                tags,
                weights,
                task_data.complexity,
                task_data.reward
            )
            
            if tx_receipt['status'] == 1:
                # Get the created task
                task_info = await blockchain_service.get_task_info(task_id)
                return self._format_task_response(task_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[TaskResponse]:
        """
        Update a task.
        
        Args:
            task_id: The ID of the task to update.
            task_data: Updated task data.
            
        Returns:
            Updated task information or None if update fails.
        """
        try:
            # Get current task
            current_task = await self.get_task(task_id)
            if not current_task:
                return None
                
            # Only available tasks can be updated
            if current_task.status != TaskStatus.AVAILABLE:
                logger.error(f"Cannot update task {task_id} with status {current_task.status}")
                return None
            
            # Update task on blockchain
            tx_receipt = await blockchain_service.send_transaction(
                'TaskManager',
                'updateTask',
                task_id,
                task_data.title or current_task.title,
                task_data.description or current_task.description,
                task_data.complexity or current_task.complexity,
                task_data.reward or current_task.reward
            )
            
            if tx_receipt['status'] == 1:
                # Get the updated task
                task_info = await blockchain_service.get_task_info(task_id)
                return self._format_task_response(task_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None
    
    async def assign_task(self, task_id: str, assign_data: TaskAssign) -> Optional[TaskResponse]:
        """
        Assign a task to an agent.
        
        Args:
            task_id: The ID of the task to assign.
            assign_data: Assignment data.
            
        Returns:
            Updated task information or None if assignment fails.
        """
        try:
            # Assign task on blockchain
            tx_receipt = await blockchain_service.send_transaction(
                'TaskManager',
                'assignTask',
                task_id,
                assign_data.agent_address,
                assign_data.bid_amount or 0
            )
            
            if tx_receipt['status'] == 1:
                # Get the updated task
                task_info = await blockchain_service.get_task_info(task_id)
                return self._format_task_response(task_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error assigning task {task_id}: {e}")
            return None
    
    async def complete_task(
        self, 
        task_id: str, 
        complete_data: TaskComplete
    ) -> Optional[TaskResponse]:
        """
        Mark a task as completed.
        
        Args:
            task_id: The ID of the task to complete.
            complete_data: Completion data.
            
        Returns:
            Updated task information or None if completion fails.
        """
        try:
            # Complete task on blockchain
            tx_receipt = await blockchain_service.send_transaction(
                'TaskManager',
                'completeTask',
                task_id,
                complete_data.result
            )
            
            if tx_receipt['status'] == 1:
                # Get the updated task
                task_info = await blockchain_service.get_task_info(task_id)
                return self._format_task_response(task_info)
            else:
                logger.error(f"Transaction failed: {tx_receipt}")
                return None
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return None
    
    async def get_task_stats(self) -> TaskStats:
        """
        Get task statistics.
        
        Returns:
            Task statistics.
        """
        try:
            # Get all tasks
            tasks = await self.get_tasks(limit=1000)
            
            # Calculate statistics
            total = len(tasks.tasks)
            available = sum(1 for task in tasks.tasks if task.status == TaskStatus.AVAILABLE)
            assigned = sum(1 for task in tasks.tasks if task.status == TaskStatus.ASSIGNED)
            completed = sum(1 for task in tasks.tasks if task.status == TaskStatus.COMPLETED)
            failed = sum(1 for task in tasks.tasks if task.status == TaskStatus.FAILED)
            cancelled = sum(1 for task in tasks.tasks if task.status == TaskStatus.CANCELLED)
            
            # Calculate averages
            avg_reward = sum(task.reward for task in tasks.tasks) / total if total > 0 else 0
            avg_complexity = sum(task.complexity for task in tasks.tasks) / total if total > 0 else 0
            
            # Calculate completion time average
            completed_tasks = [task for task in tasks.tasks if task.status == TaskStatus.COMPLETED]
            if completed_tasks:
                avg_completion_time = sum(
                    (task.completed_at - task.assigned_at).total_seconds() / 60
                    for task in completed_tasks
                    if task.completed_at and task.assigned_at
                ) / len(completed_tasks)
            else:
                avg_completion_time = None
            
            # Get task type distribution
            task_type_distribution = {}
            for task in tasks.tasks:
                task_type = task.task_type
                if task_type in task_type_distribution:
                    task_type_distribution[task_type] += 1
                else:
                    task_type_distribution[task_type] = 1
            
            # Get recent tasks
            recent_tasks = sorted(
                tasks.tasks,
                key=lambda t: t.created_at,
                reverse=True
            )[:5]
            
            # Get top agents
            agent_stats = {}
            for task in tasks.tasks:
                if task.status == TaskStatus.COMPLETED and task.assigned_agent:
                    if task.assigned_agent in agent_stats:
                        agent_stats[task.assigned_agent]['completed_tasks'] += 1
                        agent_stats[task.assigned_agent]['total_score'] += task.score or 0
                    else:
                        agent_stats[task.assigned_agent] = {
                            'agent_id': task.assigned_agent,
                            'completed_tasks': 1,
                            'total_score': task.score or 0
                        }
            
            top_agents = sorted(
                agent_stats.values(),
                key=lambda a: a['completed_tasks'],
                reverse=True
            )[:5]
            
            # Add average score to top agents
            for agent in top_agents:
                agent['average_score'] = agent['total_score'] / agent['completed_tasks']
            
            return TaskStats(
                total=total,
                available=available,
                assigned=assigned,
                completed=completed,
                failed=failed,
                cancelled=cancelled,
                average_reward=avg_reward,
                average_complexity=avg_complexity,
                average_completion_time=avg_completion_time,
                task_type_distribution=task_type_distribution,
                recent_tasks=recent_tasks,
                top_agents=top_agents
            )
        except Exception as e:
            logger.error(f"Error getting task stats: {e}")
            return TaskStats(
                total=0,
                available=0,
                assigned=0,
                completed=0,
                failed=0,
                cancelled=0,
                average_reward=0,
                average_complexity=0,
                task_type_distribution={},
                recent_tasks=[],
                top_agents=[]
            )
    
    def _format_task_response(self, task_info: Dict[str, Any]) -> TaskResponse:
        """
        Format task information for API response.
        
        Args:
            task_info: Raw task information.
            
        Returns:
            Formatted task response.
        """
        # Convert timestamps to datetime
        created_at = datetime.fromtimestamp(task_info.get('created_at', 0))
        updated_at = task_info.get('updated_at')
        if updated_at:
            updated_at = datetime.fromtimestamp(updated_at)
        else:
            updated_at = created_at
            
        assigned_at = task_info.get('assigned_at')
        if assigned_at:
            assigned_at = datetime.fromtimestamp(assigned_at)
            
        completed_at = task_info.get('completed_at')
        if completed_at:
            completed_at = datetime.fromtimestamp(completed_at)
        
        # Create response object
        return TaskResponse(
            task_id=task_info['task_id'],
            title=task_info['title'],
            description=task_info['description'],
            task_type=task_info.get('task_type', 'other'),
            complexity=task_info['complexity'],
            reward=task_info['reward'],
            deadline=None,  # Not implemented in contracts yet
            tags=task_info.get('tags', {}),
            metadata={},  # Not implemented in contracts yet
            creator_address=task_info['creator_address'],
            assigned_agent=task_info['assigned_agent'],
            status=TaskStatus(task_info['status']),
            created_at=created_at,
            updated_at=updated_at,
            assigned_at=assigned_at,
            completed_at=completed_at,
            result=task_info.get('result'),
            score=task_info.get('score'),
            bid_amount=task_info.get('bid_amount')
        )


# Create a singleton instance
task_service = TaskService()