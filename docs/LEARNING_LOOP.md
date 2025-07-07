# Learning Loop for LLM Agents

This document explains the implementation of a full learning loop for LLM agents in our blockchain-based multi-agent system, based on the paper "Towards Transparent and Incentive-Compatible Collaboration in LLM Multi-Agent Systems."

## Overview

The learning loop enables agents to improve their capabilities, reputation, and bidding strategies over time based on task performance and feedback. This creates a self-improving system where agents become more effective at selecting and completing tasks that match their strengths.

## Key Components

### 1. Smart Contract Updates

#### AgentRegistry.sol
- Added `AgentLearningState` structure to encapsulate learning data
- Implemented task history tracking with a fixed-size FIFO queue
- Added `recordTaskScore` function to record task scores
- Added `getAgentLearningState` function to expose learning state
- Added `getAgentRecentTasks` function to retrieve task history

#### IncentiveEngine.sol
- Added learning parameters (`learningRate` and `adaptationFactor`)
- Enhanced `TaskEvaluation` structure to include per-tag scores
- Added `LearningFeedbackProvided` event for transparency
- Implemented `setLearningParameters` function for owner control
- Updated `recordTaskQuality` to record scores in AgentRegistry
- Enhanced capability weight updates with EMA calculations
- Added `getTaskEvaluation` function to retrieve evaluation details

### 2. Python Agent Module

Created a comprehensive agent learning module with the following components:

#### Core Learning Module (agent_learning.py)
- Implements the full learning loop for LLM agents
- Handles capability updates using EMA
- Tracks reputation changes and adapts accordingly
- Adjusts bidding strategies based on performance
- Makes intelligent task selection decisions
- Continuously monitors the blockchain for opportunities

#### Configuration (agent_config.py)
- Defines learning parameters and agent profiles
- Supports different agent personalities (aggressive, conservative, etc.)
- Allows customization of learning rates and bidding strategies

#### Utility Functions (agent_learning_utils.py)
- Provides mathematical functions for EMA calculations
- Implements utility calculation algorithms
- Supports bid positioning and workload management
- Handles task type preference tracking

#### Example Implementation (agent_learning_example.py)
- Demonstrates how to set up and run the learning module
- Shows integration with blockchain contracts
- Provides examples of utility calculation and bidding

## Learning Loop Process

1. **Capability Update via EMA**
   - The IncentiveEngine computes per-tag scores for completed tasks
   - Applies Exponential Moving Average updates to agent capabilities
   - Formula: `new_weight = (alpha * old_weight + (100 - alpha) * score) / 100`
   - The `adaptationFactor` parameter controls how quickly agents adapt

2. **Reputation Update**
   - Updates agent reputation based on task scores
   - Stores the update on-chain for transparency
   - Considers both overall quality and per-tag performance

3. **Agent-side Learning**
   - Adjusts bidding strategies based on past utilities and outcomes
   - Updates confidence factor, risk tolerance, and workload sensitivity
   - Maintains task type preferences based on historical performance
   - Implements exploration vs. exploitation trade-off

4. **Synchronization**
   - Agents periodically fetch on-chain capabilities and reputation
   - Combines local learning with on-chain EMA updates
   - Maintains consistency between on-chain and off-chain state

5. **Transparent Feedback**
   - Records task scores and evaluations on-chain
   - Emits events for learning-related updates
   - Provides access to learning state for analysis and verification

## Implementation Details

### Smart Contract Integration

The learning loop is deeply integrated with the existing smart contracts:

- **AgentRegistry**: Stores and exposes agent learning state
- **IncentiveEngine**: Computes scores and updates capabilities
- **BidAuction**: Uses updated capabilities for utility calculation
- **TaskManager**: Provides task details for learning context

### Agent Learning Parameters

The learning module uses several tunable parameters:

- `learningRate`: Controls how quickly agents adapt (5% default)
- `adaptationFactor`: Determines EMA weight for capability updates (50% default)
- `exploration_rate`: Probability of exploring new tasks (10% default)
- `confidence_factor`: Agent confidence in its capabilities (80% default)
- `risk_tolerance`: Willingness to take bidding risks (50% default)
- `workload_sensitivity`: How much workload affects decisions (20% default)

### Bidding Strategy

The agent uses a sophisticated bidding strategy that considers:

1. **Utility Calculation**:
   - Blockchain-computed utility (70% weight)
   - Capability match score (20% weight)
   - Task type preference boost/penalty (±10%)
   - Workload penalty (proportional to current workload)

2. **Bid Amount Decision**:
   - Utility factor (higher utility = lower bid)
   - Risk tolerance (higher risk = more aggressive bid)
   - Small random variation for tie-breaking

3. **Task Selection**:
   - Minimum reputation requirement
   - Utility threshold (30% default)
   - Workload capacity check
   - Task type preference consideration
   - Exploration probability

## Usage

To use the learning loop:

1. Deploy the updated smart contracts
2. Set up the Python agent with appropriate configuration
3. Start the monitoring and learning process
4. Agents will automatically adapt and improve over time

## Future Improvements

Potential enhancements to the learning loop:

1. **Advanced Learning Algorithms**:
   - Implement reinforcement learning for bidding strategies
   - Add predictive models for task success probability
   - Support multi-agent collaboration learning

2. **Performance Optimization**:
   - Reduce on-chain storage requirements
   - Optimize gas costs for learning-related transactions
   - Implement batched updates for efficiency

3. **Enhanced Analytics**:
   - Add visualization tools for learning progress
   - Implement comparative agent performance analysis
   - Support agent specialization tracking

## Conclusion

The implemented learning loop creates a self-improving multi-agent system where agents continuously adapt and specialize based on their performance. This leads to more efficient task allocation, higher quality outcomes, and better alignment between agent capabilities and task requirements. 