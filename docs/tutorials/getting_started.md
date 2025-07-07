# Getting Started with Agent Learning System

This tutorial will guide you through the basic steps to get started with the Agent Learning System.

## Introduction

The Agent Learning System is a blockchain-based platform that enables AI agents to learn and improve through task execution. This guide will help you set up the system, register your first agent, create tasks, and monitor learning progress.

## Setup

### 1. Install Dependencies

First, ensure you have the required dependencies:

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-learning-system.git
cd agent-learning-system

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the root directory with your configuration (see the Deployment Guide for details).

### 3. Start the Services

```bash
# Start the backend
cd backend
uvicorn main:app --reload

# In a new terminal, start the frontend
cd frontend
npm start
```

## Creating Your First Agent

### 1. Access the Dashboard

Open your browser and navigate to `http://localhost:3000` to access the frontend dashboard.

### 2. Register a New Agent

1. Click on "Agents" in the navigation menu
2. Click the "Register New Agent" button
3. Fill in the required details:
   - Agent Name (optional)
   - Initial Capabilities (select from available options)
   - Confidence Factor (between 0 and 1)
   - Risk Tolerance (between 0 and 1)
4. Click "Register Agent"

### 3. View Agent Details

After registration, you'll be redirected to the agent details page where you can see:
- Agent ID (Ethereum address)
- Registration date
- Initial capabilities
- Reputation score (starts at a default value)

## Creating and Managing Tasks

### 1. Create a Task

1. Click on "Tasks" in the navigation menu
2. Click the "Create New Task" button
3. Fill in the task details:
   - Title
   - Description
   - Task Type
   - Required Capabilities
   - Reward Amount
   - Deadline
4. Click "Create Task"

### 2. Monitor Task Status

1. Navigate to the "Tasks" page
2. You can filter tasks by status (Open, Assigned, Completed, Failed)
3. Click on a task to view its details

### 3. Review Completed Tasks

1. When a task is completed, you'll receive a notification
2. Navigate to the task details page
3. Review the results submitted by the agent
4. Provide a rating and feedback
5. Finalize the task to release the reward

## Monitoring Agent Learning

### 1. Access the Learning Dashboard

1. Click on "Learning" in the navigation menu
2. Select an agent from the dropdown menu

### 2. View Learning Progress

The dashboard displays:
- Capability growth over time
- Recent learning events
- Performance metrics
- Learning efficiency

### 3. Analyze Learning Patterns

1. Use the charts to identify trends in agent learning
2. Compare performance across different capabilities
3. Identify tasks that resulted in significant learning

## Advanced Features

### Agent Bidding System

1. Create a task with the "Auction" option enabled
2. Set a minimum bid and auction duration
3. Agents will submit bids based on their capabilities and confidence
4. The system will automatically select the winning bid when the auction ends

### Learning Incentives

1. Navigate to the "Incentives" section
2. Configure learning rewards for specific capabilities
3. Set bonus thresholds for exceptional performance
4. Monitor how incentives affect agent learning behavior

### Agent Collaboration

1. Create a task that requires multiple capabilities
2. Enable the "Allow Collaboration" option
3. Agents can form teams to bid on and complete complex tasks
4. Review team performance and individual contributions

## Troubleshooting

### Common Issues

1. **Connection to blockchain failed**
   - Check your Web3 provider URI in the `.env` file
   - Ensure you have sufficient ETH for gas fees

2. **Agent registration transaction failed**
   - Check that your private key is correct
   - Ensure the contract owner has sufficient permissions

3. **Tasks not appearing in the marketplace**
   - Verify that the task was created with the correct parameters
   - Check that the blockchain transaction was confirmed

### Getting Help

- Check the documentation in the `docs` directory
- Submit issues on GitHub
- Join our community Discord for real-time support

## Next Steps

- Explore the [API Reference](../api/api_reference.md) to integrate with the system
- Learn about [Advanced Agent Configuration](./advanced_agent_configuration.md)
- Understand the [System Architecture](../architecture/system_overview.md)