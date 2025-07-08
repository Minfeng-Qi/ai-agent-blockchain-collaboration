"""
Tests for the task service.
"""
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.models.task import TaskCreate, TaskUpdate, TaskAssign, TaskComplete, TaskStatus, TaskType
from app.services.task_service import TaskService


@pytest.fixture
def task_service():
    return TaskService()


@pytest.fixture
def mock_task_info():
    return {
        'task_id': '12345',
        'title': 'Test Task',
        'description': 'This is a test task',
        'task_type': 'analysis',
        'complexity': 70,
        'reward': 100,
        'tags': {
            'analysis': 80,
            'research': 70
        },
        'creator_address': '0x1234567890123456789012345678901234567890',
        'assigned_agent': None,
        'status': 'available',
        'created_at': 1625097600,
        'updated_at': 1625097600,
        'assigned_at': None,
        'completed_at': None,
        'result': None,
        'score': None,
        'bid_amount': None
    }


@pytest.mark.asyncio
async def test_get_tasks(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.call_contract', new_callable=AsyncMock) as mock_call:
        with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_call.return_value = ['12345', '67890']
            mock_get.return_value = mock_task_info
            
            # Call the service method
            result = await task_service.get_tasks(skip=0, limit=10)
            
            # Check the result
            assert result.total == 2
            assert len(result.tasks) == 2
            assert result.tasks[0].task_id == mock_task_info['task_id']
            assert result.tasks[0].title == mock_task_info['title']
            assert result.tasks[0].status == TaskStatus.AVAILABLE


@pytest.mark.asyncio
async def test_get_task(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
        # Mock the blockchain service call
        mock_get.return_value = mock_task_info
        
        # Call the service method
        result = await task_service.get_task(mock_task_info['task_id'])
        
        # Check the result
        assert result is not None
        assert result.task_id == mock_task_info['task_id']
        assert result.title == mock_task_info['title']
        assert result.status == TaskStatus.AVAILABLE


@pytest.mark.asyncio
async def test_create_task(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
            with patch('uuid.uuid4') as mock_uuid:
                # Mock the blockchain service calls
                mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
                mock_get.return_value = mock_task_info
                mock_uuid.return_value = mock_task_info['task_id']
                
                # Create task data
                task_data = TaskCreate(
                    title=mock_task_info['title'],
                    description=mock_task_info['description'],
                    task_type=TaskType.ANALYSIS,
                    complexity=mock_task_info['complexity'],
                    reward=mock_task_info['reward'],
                    tags=mock_task_info['tags'],
                    creator_address=mock_task_info['creator_address']
                )
                
                # Call the service method
                result = await task_service.create_task(task_data)
                
                # Check the result
                assert result is not None
                assert result.task_id == mock_task_info['task_id']
                assert result.title == mock_task_info['title']
                assert result.status == TaskStatus.AVAILABLE


@pytest.mark.asyncio
async def test_update_task(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
            with patch('app.services.task_service.task_service.get_task', new_callable=AsyncMock) as mock_get_task:
                # Mock the blockchain service calls
                mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
                mock_get.return_value = mock_task_info
                
                # Mock the current task
                current_task = TaskStatus.AVAILABLE
                mock_get_task.return_value.status = current_task
                
                # Create update data
                update_data = TaskUpdate(
                    title='Updated Task',
                    description='This is an updated task',
                    complexity=75,
                    reward=150
                )
                
                # Call the service method
                result = await task_service.update_task(mock_task_info['task_id'], update_data)
                
                # Check the result
                assert result is not None
                assert result.task_id == mock_task_info['task_id']


@pytest.mark.asyncio
async def test_assign_task(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
            mock_get.return_value = {
                **mock_task_info,
                'assigned_agent': '0x2345678901234567890123456789012345678901',
                'status': 'assigned'
            }
            
            # Create assign data
            assign_data = TaskAssign(
                agent_address='0x2345678901234567890123456789012345678901',
                bid_amount=90
            )
            
            # Call the service method
            result = await task_service.assign_task(mock_task_info['task_id'], assign_data)
            
            # Check the result
            assert result is not None
            assert result.task_id == mock_task_info['task_id']
            assert result.status == TaskStatus.ASSIGNED
            assert result.assigned_agent == '0x2345678901234567890123456789012345678901'


@pytest.mark.asyncio
async def test_complete_task(task_service, mock_task_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_task_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
            mock_get.return_value = {
                **mock_task_info,
                'assigned_agent': '0x2345678901234567890123456789012345678901',
                'status': 'completed',
                'result': 'Task completed successfully',
                'score': 85
            }
            
            # Create complete data
            complete_data = TaskComplete(
                result='Task completed successfully'
            )
            
            # Call the service method
            result = await task_service.complete_task(mock_task_info['task_id'], complete_data)
            
            # Check the result
            assert result is not None
            assert result.task_id == mock_task_info['task_id']
            assert result.status == TaskStatus.COMPLETED
            assert result.result == 'Task completed successfully'


@pytest.mark.asyncio
async def test_get_task_stats(task_service, mock_task_info):
    with patch('app.services.task_service.task_service.get_tasks', new_callable=AsyncMock) as mock_get_tasks:
        # Mock the get_tasks method
        mock_get_tasks.return_value.tasks = [
            # Available task
            type('obj', (object,), {
                'task_id': '12345',
                'status': TaskStatus.AVAILABLE,
                'task_type': 'analysis',
                'complexity': 70,
                'reward': 100,
                'created_at': datetime.now(),
                'assigned_agent': None
            }),
            # Assigned task
            type('obj', (object,), {
                'task_id': '67890',
                'status': TaskStatus.ASSIGNED,
                'task_type': 'generation',
                'complexity': 80,
                'reward': 150,
                'created_at': datetime.now(),
                'assigned_agent': '0x2345678901234567890123456789012345678901'
            }),
            # Completed task
            type('obj', (object,), {
                'task_id': '13579',
                'status': TaskStatus.COMPLETED,
                'task_type': 'analysis',
                'complexity': 60,
                'reward': 120,
                'created_at': datetime.now(),
                'assigned_agent': '0x2345678901234567890123456789012345678901',
                'assigned_at': datetime.now(),
                'completed_at': datetime.now(),
                'score': 85
            })
        ]
        mock_get_tasks.return_value.total = 3
        
        # Call the service method
        result = await task_service.get_task_stats()
        
        # Check the result
        assert result.total == 3
        assert result.available == 1
        assert result.assigned == 1
        assert result.completed == 1
        assert result.average_reward == (100 + 150 + 120) / 3
        assert result.average_complexity == (70 + 80 + 60) / 3
        assert len(result.recent_tasks) <= 5
        assert len(result.top_agents) <= 5