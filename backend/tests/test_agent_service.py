"""
Tests for the agent service.
"""
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.models.agent import AgentCreate, AgentUpdate, AgentCapabilitiesUpdate
from app.services.agent_service import AgentService


@pytest.fixture
def agent_service():
    return AgentService()


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
        'tasks_completed': 10,
        'tasks_failed': 2,
        'total_rewards': 500,
        'registration_timestamp': 1625097600,
        'last_updated_timestamp': 1625184000
    }


@pytest.mark.asyncio
async def test_get_agents(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.call_contract', new_callable=AsyncMock) as mock_call:
        with patch('app.services.blockchain.blockchain_service.get_agent_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_call.return_value = [
                '0x1234567890123456789012345678901234567890',
                '0x2345678901234567890123456789012345678901'
            ]
            mock_get.return_value = mock_agent_info
            
            # Call the service method
            result = await agent_service.get_agents(skip=0, limit=10)
            
            # Check the result
            assert result.total == 2
            assert len(result.agents) == 2
            assert result.agents[0].address == mock_agent_info['address']
            assert result.agents[0].capabilities == mock_agent_info['capabilities']
            assert result.agents[0].reputation == mock_agent_info['reputation']


@pytest.mark.asyncio
async def test_get_agent(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.get_agent_info', new_callable=AsyncMock) as mock_get:
        # Mock the blockchain service call
        mock_get.return_value = mock_agent_info
        
        # Call the service method
        result = await agent_service.get_agent(mock_agent_info['address'])
        
        # Check the result
        assert result is not None
        assert result.address == mock_agent_info['address']
        assert result.capabilities == mock_agent_info['capabilities']
        assert result.reputation == mock_agent_info['reputation']


@pytest.mark.asyncio
async def test_create_agent(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_agent_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
            mock_get.return_value = mock_agent_info
            
            # Create agent data
            agent_data = AgentCreate(
                address=mock_agent_info['address'],
                public_key=mock_agent_info['public_key'],
                capabilities=mock_agent_info['capabilities'],
                confidence_factor=70,
                risk_tolerance=60
            )
            
            # Call the service method
            result = await agent_service.create_agent(agent_data)
            
            # Check the result
            assert result is not None
            assert result.address == mock_agent_info['address']
            assert result.capabilities == mock_agent_info['capabilities']
            assert result.reputation == mock_agent_info['reputation']


@pytest.mark.asyncio
async def test_update_agent(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_agent_info', new_callable=AsyncMock) as mock_get:
            with patch('app.services.agent_service.agent_service.get_agent', new_callable=AsyncMock) as mock_get_agent:
                # Mock the blockchain service calls
                mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
                mock_get.return_value = mock_agent_info
                mock_get_agent.return_value = mock_agent_info
                
                # Create update data
                update_data = AgentUpdate(
                    capabilities={
                        'analysis': 75,
                        'generation': 65,
                        'classification': 55
                    },
                    confidence_factor=75,
                    risk_tolerance=65
                )
                
                # Call the service method
                result = await agent_service.update_agent(mock_agent_info['address'], update_data)
                
                # Check the result
                assert result is not None
                assert result.address == mock_agent_info['address']


@pytest.mark.asyncio
async def test_update_agent_capabilities(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.send_transaction', new_callable=AsyncMock) as mock_tx:
        with patch('app.services.blockchain.blockchain_service.get_agent_info', new_callable=AsyncMock) as mock_get:
            # Mock the blockchain service calls
            mock_tx.return_value = {'status': 1, 'transaction_hash': '0xabc'}
            mock_get.return_value = mock_agent_info
            
            # Create capabilities data
            capabilities = {
                'analysis': 75,
                'generation': 65,
                'classification': 55
            }
            
            # Call the service method
            result = await agent_service.update_agent_capabilities(mock_agent_info['address'], capabilities)
            
            # Check the result
            assert result is not None
            assert result.address == mock_agent_info['address']


@pytest.mark.asyncio
async def test_get_agent_capabilities(agent_service, mock_agent_info):
    with patch('app.services.blockchain.blockchain_service.call_contract', new_callable=AsyncMock) as mock_call:
        # Mock the blockchain service call
        mock_call.return_value = (
            ['analysis', 'generation', 'classification'],
            [70, 60, 50]
        )
        
        # Call the service method
        result = await agent_service.get_agent_capabilities(mock_agent_info['address'])
        
        # Check the result
        assert result == {
            'analysis': 70,
            'generation': 60,
            'classification': 50
        }