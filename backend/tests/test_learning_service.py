"""
Tests for the learning service.
"""
import pytest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from datetime import datetime

from app.models.learning import LearningMetrics, LearningUpdate, TaskResult
from app.services.learning_service import LearningService


@pytest.fixture
def learning_service():
    service = LearningService()
    # Mock the models directory
    service.ensure_models_dir = MagicMock()
    return service


@pytest.fixture
def mock_agent_info():
    return {
        'address': '0x1234567890123456789012345678901234567890',
        'public_key': 'public_key',
        'capabilities': {
            'analysis': 70,
            'generation': 60,
            'classification': 50
        },
        'reputation': 80,
        'workload': 2,
        'confidence_factor': 70,
        'risk_tolerance': 60,
        'tasks_completed': 10,
        'tasks_failed': 2,
        'total_rewards': 500,
        'average_score': 85.0,
        'average_reward': 50.0
    }


@pytest.fixture
def mock_learning_metrics():
    return {
        'agent_address': '0x1234567890123456789012345678901234567890',
        'total_tasks': 12,
        'successful_tasks': 10,
        'failed_tasks': 2,
        'average_score': 85.0,
        'average_reward': 50.0,
        'capability_growth': {
            'analysis': 10.0,
            'generation': 5.0,
            'classification': 8.0
        },
        'confidence_factor': 70,
        'risk_tolerance': 60,
        'learning_rate': 0.001,
        'exploration_rate': 0.1,
        'last_updated': datetime.now().isoformat()
    }


@pytest.mark.asyncio
async def test_get_learning_metrics_from_state(learning_service, mock_learning_metrics):
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps({'learning_metrics': mock_learning_metrics}))):
            # Call the service method
            result = await learning_service.get_learning_metrics(mock_learning_metrics['agent_address'])
            
            # Check the result
            assert result is not None
            assert result.agent_address == mock_learning_metrics['agent_address']
            assert result.total_tasks == mock_learning_metrics['total_tasks']
            assert result.average_score == mock_learning_metrics['average_score']


@pytest.mark.asyncio
async def test_get_learning_metrics_from_blockchain(learning_service, mock_agent_info):
    with patch('os.path.exists', return_value=False):
        with patch('app.services.agent_service.agent_service.get_agent', new_callable=AsyncMock) as mock_get_agent:
            # Mock the agent service call
            mock_get_agent.return_value = mock_agent_info
            
            # Call the service method
            result = await learning_service.get_learning_metrics(mock_agent_info['address'])
            
            # Check the result
            assert result is not None
            assert result.agent_address == mock_agent_info['address']
            assert result.total_tasks == mock_agent_info['tasks_completed'] + mock_agent_info['tasks_failed']
            assert result.average_score == mock_agent_info['average_score']


@pytest.mark.asyncio
async def test_update_learning_parameters(learning_service, mock_learning_metrics):
    with patch('app.services.learning_service.learning_service.get_learning_metrics', new_callable=AsyncMock) as mock_get:
        with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
            with patch('app.services.learning_service.learning_service._save_metrics_to_state', return_value=True) as mock_save:
                # Mock the service calls
                mock_get.return_value = LearningMetrics(**mock_learning_metrics)
                mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
                
                # Create update data
                update_data = LearningUpdate(
                    learning_rate=0.002,
                    exploration_rate=0.15,
                    confidence_factor=75,
                    risk_tolerance=65
                )
                
                # Call the service method
                result = await learning_service.update_learning_parameters(
                    mock_learning_metrics['agent_address'],
                    update_data
                )
                
                # Check the result
                assert result is not None
                assert result.learning_rate == 0.002
                assert result.exploration_rate == 0.15
                assert result.confidence_factor == 75
                assert result.risk_tolerance == 65


@pytest.mark.asyncio
async def test_process_task_result(learning_service, mock_agent_info):
    mock_integration = MagicMock()
    mock_integration.initial_capabilities = {
        'analysis': 60,
        'generation': 55,
        'classification': 45
    }
    mock_integration.get_capabilities.return_value = {
        'analysis': 70,
        'generation': 60,
        'classification': 50
    }
    
    with patch('app.services.learning_service.learning_service._get_learning_integration', new_callable=AsyncMock) as mock_get:
        with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
            with patch('app.services.learning_service.learning_service._save_learning_event', return_value=True) as mock_save:
                # Mock the service calls
                mock_get.return_value = mock_integration
                mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
                
                # Create task result data
                task_result = TaskResult(
                    task_id='12345',
                    task_type='analysis',
                    score=85,
                    reward=100,
                    tags={
                        'analysis': 85,
                        'research': 80
                    }
                )
                
                # Call the service method
                result = await learning_service.process_task_result(
                    mock_agent_info['address'],
                    task_result
                )
                
                # Check the result
                assert result is not None
                assert 'updated_capabilities' in result
                assert 'capability_changes' in result
                assert result['updated_capabilities'] == mock_integration.get_capabilities.return_value


@pytest.mark.asyncio
async def test_generate_learning_report(learning_service, mock_agent_info, mock_learning_metrics):
    mock_integration = MagicMock()
    mock_integration.get_capabilities.return_value = {
        'analysis': 70,
        'generation': 60,
        'classification': 50
    }
    mock_integration.initial_capabilities = {
        'analysis': 60,
        'generation': 55,
        'classification': 45
    }
    
    with patch('app.services.learning_service.learning_service._get_learning_integration', new_callable=AsyncMock) as mock_get:
        with patch('app.services.learning_service.learning_service.get_learning_metrics', new_callable=AsyncMock) as mock_get_metrics:
            with patch('app.services.learning_service.learning_service._load_learning_events', return_value=[]) as mock_load:
                # Mock the service calls
                mock_get.return_value = mock_integration
                mock_get_metrics.return_value = LearningMetrics(**mock_learning_metrics)
                
                # Call the service method
                result = await learning_service.generate_learning_report(mock_agent_info['address'])
                
                # Check the result
                assert result is not None
                assert result.agent_address == mock_agent_info['address']
                assert result.metrics.total_tasks == mock_learning_metrics['total_tasks']
                assert result.capabilities == mock_integration.get_capabilities.return_value