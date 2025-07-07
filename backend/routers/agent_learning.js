const express = require('express');
const router = express.Router();
const Web3 = require('web3');
const { getContracts } = require('../utils/contracts');

// Get agent learning state
router.get('/agents/:address/learning', async (req, res) => {
  try {
    const { address } = req.params;
    const { agentRegistry, incentiveEngine } = await getContracts();
    
    // Get agent learning state from AgentRegistry
    const learningState = await agentRegistry.methods.getAgentLearningState(address).call();
    
    // Get capability evolution history
    const capabilityEvolution = await agentRegistry.methods.getCapabilityEvolutionHistory(address).call();
    
    // Get bidding strategy evolution history
    const biddingStrategyEvolution = await incentiveEngine.methods.getBiddingStrategyEvolution(address).call();
    
    // Get learning curve
    const learningCurve = await agentRegistry.methods.getLearningCurve(address).call();
    
    // Get current bidding strategy
    const biddingStrategy = await agentRegistry.methods.getAgentBiddingStrategy(address).call();
    
    // Calculate capability changes (compare current weights with previous)
    const capabilities = learningState.capabilityTags.map((tag, index) => {
      const weight = parseInt(learningState.capabilityWeights[index]);
      
      // Find previous weight from evolution history
      let change = 0;
      if (capabilityEvolution.length > 0) {
        const previousEntries = capabilityEvolution.filter(entry => entry.tag === tag);
        if (previousEntries.length > 1) {
          const latestEntry = previousEntries[previousEntries.length - 1];
          const previousEntry = previousEntries[previousEntries.length - 2];
          change = parseInt(latestEntry.newWeight) - parseInt(previousEntry.newWeight);
        }
      }
      
      return {
        tag,
        weight,
        change
      };
    });
    
    // Calculate average score from recent tasks
    let averageScore = 0;
    if (learningState.recentScores && learningState.recentScores.length > 0) {
      const sum = learningState.recentScores.reduce((acc, score) => acc + parseInt(score), 0);
      averageScore = Math.round(sum / learningState.recentScores.length);
    }
    
    // Format response
    const response = {
      address,
      reputation: parseInt(learningState.reputation),
      workload: parseInt(learningState.workload),
      tasksCompleted: learningState.recentTaskIds.length,
      averageScore,
      capabilities,
      capabilityEvolution: capabilityEvolution.map(entry => ({
        tag: entry.tag,
        oldWeight: parseInt(entry.oldWeight),
        newWeight: parseInt(entry.newWeight),
        timestamp: parseInt(entry.timestamp),
        taskId: entry.taskId
      })),
      biddingStrategyEvolution: biddingStrategyEvolution.map(entry => ({
        oldConfidence: parseInt(entry.oldConfidence),
        newConfidence: parseInt(entry.newConfidence),
        oldRiskTolerance: parseInt(entry.oldRiskTolerance),
        newRiskTolerance: parseInt(entry.newRiskTolerance),
        taskId: entry.taskId,
        taskScore: parseInt(entry.taskScore),
        timestamp: parseInt(entry.timestamp)
      })),
      learningCurve: learningCurve.map(score => parseInt(score)),
      currentBiddingStrategy: {
        confidenceFactor: parseInt(biddingStrategy.confidenceFactor),
        riskTolerance: parseInt(biddingStrategy.riskTolerance),
        lastUpdated: parseInt(biddingStrategy.lastUpdated)
      }
    };
    
    res.json(response);
  } catch (error) {
    console.error('Error fetching agent learning data:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get all agents learning summary
router.get('/agents/learning/summary', async (req, res) => {
  try {
    const { agentRegistry } = await getContracts();
    
    // Get total number of agents
    const agentCount = await agentRegistry.methods.getAgentCount().call();
    
    // Get all agent addresses
    const agents = [];
    for (let i = 0; i < agentCount; i++) {
      const address = await agentRegistry.methods.agentAddresses(i).call();
      agents.push(address);
    }
    
    // Get learning summary for each agent
    const summaries = await Promise.all(agents.map(async (address) => {
      const learningState = await agentRegistry.methods.getAgentLearningState(address).call();
      const agent = await agentRegistry.methods.agents(address).call();
      
      // Calculate average score
      let averageScore = 0;
      if (learningState.recentScores && learningState.recentScores.length > 0) {
        const sum = learningState.recentScores.reduce((acc, score) => acc + parseInt(score), 0);
        averageScore = Math.round(sum / learningState.recentScores.length);
      }
      
      return {
        address,
        name: agent.name,
        reputation: parseInt(learningState.reputation),
        workload: parseInt(learningState.workload),
        tasksCompleted: learningState.recentTaskIds.length,
        averageScore,
        capabilityCount: learningState.capabilityTags.length
      };
    }));
    
    res.json(summaries);
  } catch (error) {
    console.error('Error fetching agent learning summaries:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get system-wide learning metrics
router.get('/learning/metrics', async (req, res) => {
  try {
    const { agentRegistry, incentiveEngine, taskManager } = await getContracts();
    
    // Get total number of agents
    const agentCount = await agentRegistry.methods.getAgentCount().call();
    
    // Get total number of tasks
    const openTasks = await taskManager.methods.getTasksByStatus(0).call(); // 0 = Open
    const assignedTasks = await taskManager.methods.getTasksByStatus(1).call(); // 1 = Assigned
    const completedTasks = await taskManager.methods.getTasksByStatus(2).call(); // 2 = Completed
    const cancelledTasks = await taskManager.methods.getTasksByStatus(3).call(); // 3 = Cancelled
    
    // Calculate average reputation across all agents
    let totalReputation = 0;
    for (let i = 0; i < agentCount; i++) {
      const address = await agentRegistry.methods.agentAddresses(i).call();
      const reputation = await agentRegistry.methods.getAgentReputation(address).call();
      totalReputation += parseInt(reputation);
    }
    const averageReputation = agentCount > 0 ? Math.round(totalReputation / agentCount) : 0;
    
    // Get learning parameters
    const learningRate = await incentiveEngine.methods.learningRate().call();
    const adaptationFactor = await incentiveEngine.methods.adaptationFactor().call();
    const confidenceAdjustRate = await incentiveEngine.methods.confidenceAdjustRate().call();
    const riskToleranceAdjustRate = await incentiveEngine.methods.riskToleranceAdjustRate().call();
    
    res.json({
      agentCount: parseInt(agentCount),
      taskCounts: {
        open: openTasks.length,
        assigned: assignedTasks.length,
        completed: completedTasks.length,
        cancelled: cancelledTasks.length,
        total: openTasks.length + assignedTasks.length + completedTasks.length + cancelledTasks.length
      },
      averageReputation,
      learningParameters: {
        learningRate: parseInt(learningRate),
        adaptationFactor: parseInt(adaptationFactor),
        confidenceAdjustRate: parseInt(confidenceAdjustRate),
        riskToleranceAdjustRate: parseInt(riskToleranceAdjustRate)
      }
    });
  } catch (error) {
    console.error('Error fetching learning metrics:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 