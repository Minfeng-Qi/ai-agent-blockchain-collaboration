// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./AgentRegistry.sol";
import "./ActionLogger.sol";

/**
 * @title IncentiveEngine
 * @dev Contract to compute and update agent reputation and capability weights
 * based on "Towards Transparent and Incentive-Compatible Collaboration in LLM Multi-Agent Systems"
 */
contract IncentiveEngine is Ownable {
    // Reference to other contracts
    AgentRegistry public agentRegistry;
    ActionLogger public actionLogger;
    
    // Reputation update parameters
    uint256 public reputationAlpha = 80;  // Smoothing factor (0-100)
    uint256 public maxReputationChange = 10;  // Maximum change per update
    
    // Task score parameters (Section IV-B)
    uint256 public alpha = 60;  // Quality weight (0-100)
    uint256 public delta = 40;  // Delay penalty weight (0-100)
    
    // Capability weight update parameters (Section IV-C)
    uint256 public mu = 70;  // Capability weight smoothing factor (0-100)
    
    // Utility function parameters (Section IV-A)
    uint256 public beta = 10;  // Workload penalty weight (0-100)
    uint256 public gamma = 20;  // Capability mismatch penalty weight (0-100)
    
    // Penalty thresholds
    uint256 public penaltyThreshold = 30;  // Score below this triggers penalties
    uint256 public penaltyFactor = 20;     // Increased penalty factor (0-100)
    
    // Learning parameters
    uint256 public learningRate = 5;       // Base learning rate for adjustments (0-100)
    uint256 public adaptationFactor = 50;  // How quickly agents adapt to new scores (0-100)
    
    // Bidding strategy parameters
    uint256 public confidenceAdjustRate = 5;  // Rate at which confidence factor is adjusted (0-100)
    uint256 public riskToleranceAdjustRate = 3;  // Rate at which risk tolerance is adjusted (0-100)
    uint256 public minConfidence = 30;  // Minimum confidence factor (0-100)
    uint256 public maxConfidence = 95;  // Maximum confidence factor (0-100)
    uint256 public minRiskTolerance = 20;  // Minimum risk tolerance (0-100)
    uint256 public maxRiskTolerance = 80;  // Maximum risk tolerance (0-100)
    
    // Capability weights - kept for backward compatibility
    struct CapabilityWeight {
        string capability;
        uint256 weight;  // 0-100
        uint256 lastUpdated;
        bool penalized;  // Whether this capability is currently penalized
        uint256 penaltyEndTime;  // When the penalty period ends
    }
    
    // Maps agent address to capability weights - kept for backward compatibility
    mapping(address => mapping(string => CapabilityWeight)) public agentCapabilityWeights;
    
    // Maps agent address to list of capabilities - kept for backward compatibility
    mapping(address => string[]) public agentCapabilities;
    
    // Task completion history
    struct TaskCompletion {
        bytes32 taskId;
        address agent;
        uint256 quality;  // 0-100
        uint256 timestamp;
    }
    
    // Enhanced task evaluation structure
    struct TaskEvaluation {
        uint256 quality;         // 0-100
        uint256 delayRatio;      // 0-100 (0 = no delay)
        uint256 finalScore;      // Computed score
        mapping(string => uint256) tagScores;  // Per-tag scores
        string[] tags;           // List of tags evaluated
    }
    
    // Bidding strategy evolution
    struct BiddingStrategyEvolution {
        uint256 oldConfidence;
        uint256 newConfidence;
        uint256 oldRiskTolerance;
        uint256 newRiskTolerance;
        bytes32 taskId;
        uint256 taskScore;
        uint256 timestamp;
    }
    
    // Maps agent address to bidding strategy evolution history
    mapping(address => BiddingStrategyEvolution[]) public biddingStrategyEvolution;
    uint256 public constant MAX_STRATEGY_HISTORY = 20;
    
    // Maps task ID to completion record
    mapping(bytes32 => TaskCompletion) public taskCompletions;
    
    // Maps task ID to evaluation data
    mapping(bytes32 => TaskEvaluation) public taskEvaluations;
    
    // Events
    event ReputationUpdated(
        address indexed agent,
        uint256 oldReputation,
        uint256 newReputation,
        bytes32 indexed taskId,
        uint256 timestamp
    );
    
    event CapabilityWeightUpdated(
        address indexed agent,
        string capability,
        uint256 oldWeight,
        uint256 newWeight,
        bytes32 indexed taskId,
        uint256 timestamp
    );
    
    event TaskQualityRecorded(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 quality,
        uint256 timestamp
    );
    
    event BidWinRecorded(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 utilityScore,
        uint256 timestamp
    );
    
    // New events as requested
    event TaskScoreComputed(
        address indexed agent,
        bytes32 indexed taskId,
        uint256 score,
        uint256 quality,
        uint256 delayRatio,
        uint256 timestamp
    );
    
    event UtilityEvaluated(
        address indexed agent,
        bytes32 indexed taskId,
        uint256 score,
        uint256 timestamp
    );
    
    event CapabilityAdjusted(
        address indexed agent,
        string tag,
        uint256 newWeight,
        uint256 timestamp
    );
    
    event AgentPenalized(
        address indexed agent,
        bytes32 indexed taskId,
        string reason,
        uint256 timestamp
    );
    
    event LearningFeedbackProvided(
        address indexed agent,
        bytes32 indexed taskId,
        uint256 score,
        string[] tags,
        uint256[] tagScores,
        uint256 timestamp
    );
    
    event BiddingStrategyUpdated(
        address indexed agent,
        uint256 oldConfidence,
        uint256 newConfidence,
        uint256 oldRiskTolerance,
        uint256 newRiskTolerance,
        bytes32 indexed taskId,
        uint256 timestamp
    );

    /**
     * @dev Constructor
     * @param _agentRegistryAddress Address of the AgentRegistry contract
     */
    constructor(address _agentRegistryAddress) Ownable(msg.sender) {
        agentRegistry = AgentRegistry(_agentRegistryAddress);
    }
    
    /**
     * @dev Set ActionLogger contract address
     * @param _actionLoggerAddress Address of the ActionLogger contract
     */
    function setActionLogger(address _actionLoggerAddress) external onlyOwner {
        actionLogger = ActionLogger(_actionLoggerAddress);
    }
    
    /**
     * @dev Set reputation update parameters
     * @param _lambda Smoothing factor (0-100)
     * @param _maxChange Maximum change per update
     */
    function setReputationParameters(uint256 _lambda, uint256 _maxChange) external onlyOwner {
        require(_lambda <= 100, "Lambda must be between 0-100");
        reputationAlpha = _lambda;
        maxReputationChange = _maxChange;
    }
    
    /**
     * @dev Set task score parameters
     * @param _alpha Quality weight (0-100)
     * @param _delta Delay penalty weight (0-100)
     */
    function setScoreParameters(uint256 _alpha, uint256 _delta) external onlyOwner {
        require(_alpha + _delta == 100, "Alpha + Delta must equal 100");
        alpha = _alpha;
        delta = _delta;
    }
    
    /**
     * @dev Set capability weight update parameter
     * @param _mu Capability weight smoothing factor (0-100)
     */
    function setMu(uint256 _mu) external onlyOwner {
        require(_mu <= 100, "Mu must be between 0-100");
        mu = _mu;
    }
    
    /**
     * @dev Set utility function parameters
     * @param _beta Workload penalty weight (0-100)
     * @param _gamma Capability mismatch penalty weight (0-100)
     */
    function setUtilityParameters(uint256 _beta, uint256 _gamma) external onlyOwner {
        beta = _beta;
        gamma = _gamma;
    }
    
    /**
     * @dev Set bidding strategy adjustment parameters
     * @param _confidenceRate Rate at which confidence is adjusted (0-100)
     * @param _riskToleranceRate Rate at which risk tolerance is adjusted (0-100)
     * @param _minConfidence Minimum confidence factor (0-100)
     * @param _maxConfidence Maximum confidence factor (0-100)
     * @param _minRiskTolerance Minimum risk tolerance (0-100)
     * @param _maxRiskTolerance Maximum risk tolerance (0-100)
     */
    function setBiddingStrategyParameters(
        uint256 _confidenceRate,
        uint256 _riskToleranceRate,
        uint256 _minConfidence,
        uint256 _maxConfidence,
        uint256 _minRiskTolerance,
        uint256 _maxRiskTolerance
    ) external onlyOwner {
        require(_confidenceRate <= 100, "Confidence rate must be between 0-100");
        require(_riskToleranceRate <= 100, "Risk tolerance rate must be between 0-100");
        require(_minConfidence <= _maxConfidence, "Min confidence must be <= max confidence");
        require(_minRiskTolerance <= _maxRiskTolerance, "Min risk tolerance must be <= max risk tolerance");
        
        confidenceAdjustRate = _confidenceRate;
        riskToleranceAdjustRate = _riskToleranceRate;
        minConfidence = _minConfidence;
        maxConfidence = _maxConfidence;
        minRiskTolerance = _minRiskTolerance;
        maxRiskTolerance = _maxRiskTolerance;
    }
    
    /**
     * @dev Set penalty thresholds
     * @param _threshold Score below this triggers penalties (0-100)
     * @param _factor Increased penalty factor (0-100)
     */
    function setPenaltyThresholds(uint256 _threshold, uint256 _factor) external onlyOwner {
        require(_threshold <= 100, "Threshold must be between 0-100");
        require(_factor <= 100, "Factor must be between 0-100");
        penaltyThreshold = _threshold;
        penaltyFactor = _factor;
    }
    
    /**
     * @dev Set learning parameters
     * @param _learningRate Base learning rate (0-100)
     * @param _adaptationFactor How quickly agents adapt to new scores (0-100)
     */
    function setLearningParameters(uint256 _learningRate, uint256 _adaptationFactor) external onlyOwner {
        require(_learningRate <= 100, "Learning rate must be between 0-100");
        require(_adaptationFactor <= 100, "Adaptation factor must be between 0-100");
        learningRate = _learningRate;
        adaptationFactor = _adaptationFactor;
    }
    
    /**
     * @dev Update agent workload
     * @param agent Address of the agent
     * @param workload New workload value (0-100)
     */
    function updateAgentWorkload(address agent, uint256 workload) external onlyOwner {
        require(workload <= 100, "Workload must be between 0-100");
        
        // Reset workload in AgentRegistry
        agentRegistry.resetWorkload(agent);
        
        // Increment workload to match the requested value
        for (uint256 i = 0; i < workload; i++) {
            agentRegistry.incrementWorkload(agent);
        }
    }
    
    /**
     * @dev Register agent capabilities
     * @param agent Address of the agent
     * @param capabilities Array of capability tags
     */
    function registerCapabilities(address agent, string[] calldata capabilities) external {
        require(msg.sender == agent || owner() == msg.sender, "Not authorized");
        require(agentRegistry.isActiveAgent(agent), "Agent not active");
        
        // Clear existing capabilities
        for (uint256 i = 0; i < agentCapabilities[agent].length; i++) {
            string memory capability = agentCapabilities[agent][i];
            delete agentCapabilityWeights[agent][capability];
        }
        delete agentCapabilities[agent];
        
        // Initialize weights for new capabilities
        uint256[] memory weights = new uint256[](capabilities.length);
        for (uint256 i = 0; i < capabilities.length; i++) {
            agentCapabilities[agent].push(capabilities[i]);
            agentCapabilityWeights[agent][capabilities[i]] = CapabilityWeight({
                capability: capabilities[i],
                weight: 50,  // Default weight
                lastUpdated: block.timestamp,
                penalized: false,
                penaltyEndTime: 0
            });
            weights[i] = 50; // Default weight
        }
        
        // Update capabilities in AgentRegistry
        agentRegistry.setCapabilities(agent, capabilities, weights);
    }
    
    /**
     * @dev Record task completion quality
     * @param taskId ID of the completed task
     * @param agent Address of the agent who completed the task
     * @param quality Quality score (0-100)
     */
    function recordTaskQuality(bytes32 taskId, address agent, uint256 quality) external onlyOwner {
        require(quality <= 100, "Quality must be between 0-100");
        
        // Store task completion
        taskCompletions[taskId] = TaskCompletion({
            taskId: taskId,
            agent: agent,
            quality: quality,
            timestamp: block.timestamp
        });
        
        // Update agent reputation
        updateAgentReputation(agent, taskId, quality);
        
        // Update capability weights
        updateCapabilityWeights(agent, taskId, quality);
        
        // Update bidding strategy based on task performance
        updateBiddingStrategy(agent, taskId, quality);
        
        // Record task score in AgentRegistry for learning history
        agentRegistry.recordTaskScore(agent, taskId, quality);
        
        // Decrement workload when task is completed
        agentRegistry.decrementWorkload(agent);
        
        // Log action via ActionLogger if available
        if (address(actionLogger) != address(0)) {
            actionLogger.logSystemAction(
                agent,
                ActionLogger.ActionType.TaskCompleted,
                taskId,
                "Task quality recorded"
            );
        }
        
        // Emit event
        emit TaskQualityRecorded(taskId, agent, quality, block.timestamp);
    }
    
    /**
     * @dev Compute task score based on quality and delay ratio
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param quality Quality score (0-100)
     * @param delayRatio Delay ratio (0-100, where 0 = no delay)
     * @return Final score (0-100)
     */
    function computeTaskScore(
        address agent,
        bytes32 taskId,
        uint256 quality,
        uint256 delayRatio
    ) external onlyOwner returns (uint256) {
        require(quality <= 100, "Quality must be between 0-100");
        require(delayRatio <= 100, "Delay ratio must be between 0-100");
        
        // Calculate score using the formula: S_i^t = α * q_i^t + δ * (1 - d_i^t)
        uint256 score = (alpha * quality + delta * (100 - delayRatio)) / 100;
        
        // Store evaluation data
        TaskEvaluation storage eval = taskEvaluations[taskId];
        eval.quality = quality;
        eval.delayRatio = delayRatio;
        eval.finalScore = score;
        
        // Record task score in AgentRegistry for learning history
        agentRegistry.recordTaskScore(agent, taskId, score);
        
        // Update bidding strategy based on task performance
        updateBiddingStrategy(agent, taskId, score);
        
        // Check if score is below penalty threshold
        if (score < penaltyThreshold) {
            penalizeAgent(agent, taskId, "Low task score");
        }
        
        // Emit event
        emit TaskScoreComputed(agent, taskId, score, quality, delayRatio, block.timestamp);
        
        return score;
    }
    
    /**
     * @dev Record bid win for an agent
     * @param agent Address of the agent
     * @param taskId ID of the task
     */
    function recordBidWin(address agent, bytes32 taskId) external onlyOwner {
        require(agentRegistry.isActiveAgent(agent), "Agent not active");
        
        // Increment workload when task is assigned
        agentRegistry.incrementWorkload(agent);
        
        // Get agent's current reputation
        uint256 oldReputation = getAgentReputation(agent);
        
        // Small reputation boost for winning a bid (max 1 point)
        uint256 reputationBoost = 1;
        uint256 newReputation = oldReputation + reputationBoost > 100 ? 100 : oldReputation + reputationBoost;
        
        // Update reputation if changed
        if (newReputation != oldReputation) {
            agentRegistry.setReputation(agent, newReputation);
            
            emit ReputationUpdated(
                agent,
                oldReputation,
                newReputation,
                taskId,
                block.timestamp
            );
        }
        
        // Log action if logger is available
        if (address(actionLogger) != address(0)) {
            actionLogger.logSystemAction(
                agent,
                ActionLogger.ActionType.BidWon,
                taskId,
                "Bid won"
            );
        }
    }
    
    /**
     * @dev Update specific capability weights based on tag-specific scores
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param tags Array of capability tags
     * @param scores Array of corresponding scores (0-100)
     */
    function updateSpecificCapabilityWeights(
        address agent,
        bytes32 taskId,
        string[] memory tags,
        uint256[] memory scores
    ) external onlyOwner {
        require(tags.length == scores.length, "Tags and scores must have same length");
        
        // Get current capabilities and weights from AgentRegistry
        (string[] memory existingTags, uint256[] memory existingWeights) = agentRegistry.getCapabilities(agent);
        
        // Create mapping for easier access
        TaskEvaluation storage eval = taskEvaluations[taskId];
        
        // Store tags for future reference
        delete eval.tags;
        for (uint256 i = 0; i < tags.length; i++) {
            eval.tags.push(tags[i]);
            // Store tag score
            eval.tagScores[tags[i]] = scores[i];
        }
        
        // Prepare arrays for updated weights
        string[] memory updatedTags = new string[](existingTags.length);
        uint256[] memory updatedWeights = new uint256[](existingTags.length);
        
        // Copy existing tags and weights to new arrays
        for (uint256 i = 0; i < existingTags.length; i++) {
            updatedTags[i] = existingTags[i];
            updatedWeights[i] = existingWeights[i];
            
            // Check if this tag was evaluated
            for (uint256 j = 0; j < tags.length; j++) {
                if (keccak256(bytes(existingTags[i])) == keccak256(bytes(tags[j]))) {
                    uint256 oldWeight = existingWeights[i];
                    
                    // EMA formula: w_{i,k}^{t+1} = μ * w_{i,k}^t + (1-μ) * s_{i,k}^t
                    uint256 newWeight = (mu * oldWeight + (100 - mu) * scores[j]) / 100;
                    
                    // Apply learning rate adjustment based on score difference
                    if (scores[j] > oldWeight) {
                        // Positive reinforcement - faster learning for high scores
                        uint256 boost = (scores[j] - oldWeight) * learningRate / 100;
                        newWeight = newWeight + boost > 100 ? 100 : newWeight + boost;
                    } else if (oldWeight > scores[j]) {
                        // Negative reinforcement - faster decline for low scores
                        uint256 penalty = (oldWeight - scores[j]) * learningRate / 100;
                        newWeight = newWeight > penalty ? newWeight - penalty : 1;
                    }
                    
                    // Update weight in array
                    updatedWeights[i] = newWeight;
                    
                    // Emit event
                    emit CapabilityAdjusted(agent, tags[j], newWeight, block.timestamp);
                    break;
                }
            }
        }
        
        // Update capabilities in AgentRegistry
        agentRegistry.setCapabilities(agent, updatedTags, updatedWeights);
        
        // Emit learning feedback event
        emit LearningFeedbackProvided(
            agent,
            taskId,
            eval.finalScore,
            tags,
            scores,
            block.timestamp
        );
    }
    
    /**
     * @dev Get task evaluation details including tag-specific scores
     * @param taskId ID of the task
     * @return quality Overall quality score
     * @return delayRatio Delay ratio
     * @return finalScore Computed final score
     * @return tags Array of evaluated tags
     * @return scores Array of tag-specific scores
     */
    function getTaskEvaluation(bytes32 taskId) external view returns (
        uint256 quality,
        uint256 delayRatio,
        uint256 finalScore,
        string[] memory tags,
        uint256[] memory scores
    ) {
        TaskEvaluation storage eval = taskEvaluations[taskId];
        
        // Get stored tags
        tags = eval.tags;
        
        // Get scores for each tag
        scores = new uint256[](tags.length);
        for (uint256 i = 0; i < tags.length; i++) {
            scores[i] = eval.tagScores[tags[i]];
        }
        
        return (
            eval.quality,
            eval.delayRatio,
            eval.finalScore,
            tags,
            scores
        );
    }
    
    /**
     * @dev Calculate utility for an agent to perform a task
     * @param agent Address of the agent
     * @param requiredCapabilities Array of capabilities required for the task
     * @param reward Task reward
     * @param workload Current agent workload
     * @return Utility score (0-100)
     */
    function calculateUtility(
        address agent,
        string[] memory requiredCapabilities,
        uint256 reward,
        uint256 workload
    ) external view returns (uint256) {
        // Get agent capabilities from AgentRegistry
        (string[] memory agentTags, uint256[] memory agentWeights) = agentRegistry.getCapabilities(agent);
        
        // Calculate capability mismatch penalty
        uint256 mismatchPenalty = calculateCapabilityMismatch(requiredCapabilities, agentTags, agentWeights);
        
        // Get agent workload from AgentRegistry
        uint256 agentCurrentWorkload = agentRegistry.agentWorkload(agent);
        
        // Calculate workload penalty (linear penalty based on current workload)
        uint256 workloadPenalty = agentCurrentWorkload * beta / 10;
        
        // Calculate agent's expected profit (simplified)
        uint256 expectedProfit = reward;
        
        // Calculate utility using the formula:
        // U_i^t(T_j) = π_i^t(T_j) * R_j - β * ℓ_i^t - γ * ∥r_j - ẃ_i^t∥_1
        uint256 utility = 0;
        
        if (expectedProfit > workloadPenalty + mismatchPenalty) {
            utility = expectedProfit - workloadPenalty - mismatchPenalty;
        }
        
        // Scale utility to 0-100 range
        utility = utility > 100 ? 100 : utility;
        
        return utility;
    }
    
    /**
     * @dev Calculate capability mismatch between required capabilities and agent capabilities
     * @param requiredCapabilities Array of capabilities required for the task
     * @param agentTags Array of agent capability tags
     * @param agentWeights Array of agent capability weights
     * @return Mismatch penalty (higher means worse match)
     */
    function calculateCapabilityMismatch(
        string[] memory requiredCapabilities,
        string[] memory agentTags,
        uint256[] memory agentWeights
    ) internal view returns (uint256) {
        // If no capabilities required, no mismatch
        if (requiredCapabilities.length == 0) {
            return 0;
        }
        
        // If agent has no capabilities, maximum mismatch
        if (agentTags.length == 0) {
            return gamma * requiredCapabilities.length;
        }
        
        // Calculate total mismatch
        uint256 totalMismatch = 0;
        for (uint256 i = 0; i < requiredCapabilities.length; i++) {
            // Find the weight for this capability
            uint256 weight = 0;
            for (uint256 j = 0; j < agentTags.length; j++) {
                if (keccak256(bytes(agentTags[j])) == keccak256(bytes(requiredCapabilities[i]))) {
                    weight = agentWeights[j];
                    break;
                }
            }
            
            // If agent doesn't have the capability, add full penalty
            if (weight == 0) {
                totalMismatch += 100;
            } else {
                // Otherwise, add penalty based on weight difference (100 - weight)
                totalMismatch += (100 - weight);
            }
        }
        
        // Scale by gamma and normalize by number of required capabilities
        return (gamma * totalMismatch) / (100 * requiredCapabilities.length);
    }
    
    /**
     * @dev Update agent reputation based on task score
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param score Task score (0-100)
     */
    function updateAgentReputation(address agent, bytes32 taskId, uint256 score) internal {
        uint256 oldReputation = agentRegistry.getAgentLearningState(agent).reputation;
        
        // Exponential moving average: newRep = λ * ρ_i^t + (1-λ) * S_i^t
        uint256 newReputation = (reputationAlpha * oldReputation + (100 - reputationAlpha) * score) / 100;
        
        // Apply adaptation factor to accelerate learning
        if (score > oldReputation) {
            // Positive reinforcement - faster reputation gain for high scores
            uint256 boost = (score - oldReputation) * adaptationFactor / 1000;
            newReputation = newReputation + boost > 100 ? 100 : newReputation + boost;
        } else if (oldReputation > score) {
            // Negative reinforcement - faster reputation loss for low scores
            uint256 penalty = (oldReputation - score) * adaptationFactor / 1000;
            newReputation = newReputation > penalty ? newReputation - penalty : 1;
        }
        
        // Limit maximum change
        if (newReputation > oldReputation && newReputation - oldReputation > maxReputationChange) {
            newReputation = oldReputation + maxReputationChange;
        } else if (oldReputation > newReputation && oldReputation - newReputation > maxReputationChange) {
            newReputation = oldReputation - maxReputationChange;
        }
        
        // Ensure reputation is within bounds
        if (newReputation > 100) {
            newReputation = 100;
        }
        
        // Update reputation if changed
        if (newReputation != oldReputation) {
            agentRegistry.setReputation(agent, newReputation);
            
            emit ReputationUpdated(
                agent,
                oldReputation,
                newReputation,
                taskId,
                block.timestamp
            );
        }
    }
    
    /**
     * @dev Update capability weights based on task score
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param score Task score (0-100)
     */
    function updateCapabilityWeights(address agent, bytes32 taskId, uint256 score) internal {
        // Get capabilities from AgentRegistry
        (string[] memory tags, uint256[] memory weights) = agentRegistry.getCapabilities(agent);
        
        // If no capabilities registered, do nothing
        if (tags.length == 0) {
            return;
        }
        
        // Prepare arrays for updated weights
        uint256[] memory updatedWeights = new uint256[](tags.length);
        
        // Update each capability weight
        for (uint256 i = 0; i < tags.length; i++) {
            uint256 oldWeight = weights[i];
            
            // EMA formula: w_{i,k}^{t+1} = μ * w_{i,k}^t + (1-μ) * s_i^t
            uint256 newWeight = (mu * oldWeight + (100 - mu) * score) / 100;
            
            // Store updated weight
            updatedWeights[i] = newWeight;
            
            // Emit event
            emit CapabilityWeightUpdated(
                agent,
                tags[i],
                oldWeight,
                newWeight,
                taskId,
                block.timestamp
            );
        }
        
        // Update capabilities in AgentRegistry
        agentRegistry.setCapabilities(agent, tags, updatedWeights);
    }
    
    /**
     * @dev Penalize agent for poor performance
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param reason Reason for penalty
     */
    function penalizeAgent(address agent, bytes32 taskId, string memory reason) internal {
        // Get capabilities from AgentRegistry
        (string[] memory tags, uint256[] memory weights) = agentRegistry.getCapabilities(agent);
        
        // If no capabilities registered, do nothing
        if (tags.length == 0) {
            return;
        }
        
        // Prepare arrays for updated weights with penalties
        uint256[] memory updatedWeights = new uint256[](tags.length);
        
        // Apply penalty to each capability weight
        for (uint256 i = 0; i < tags.length; i++) {
            uint256 oldWeight = weights[i];
            
            // Apply penalty factor
            uint256 penalty = oldWeight * penaltyFactor / 100;
            uint256 newWeight = oldWeight > penalty ? oldWeight - penalty : 1; // Minimum weight of 1
            
            // Store updated weight
            updatedWeights[i] = newWeight;
        }
        
        // Update capabilities in AgentRegistry
        agentRegistry.setCapabilities(agent, tags, updatedWeights);
        
        // Emit event
        emit AgentPenalized(agent, taskId, reason, block.timestamp);
    }

    /**
     * @dev Get agent's reputation
     * @param agent Address of the agent
     * @return Agent's reputation score
     */
    function getAgentReputation(address agent) public view returns (uint256) {
        return agentRegistry.getAgentLearningState(agent).reputation;
    }

    /**
     * @dev Get agent's workload
     * @param agent Address of the agent
     * @return Agent's current workload
     */
    function getAgentWorkload(address agent) public view returns (uint256) {
        return agentRegistry.agentWorkload(agent);
    }

    /**
     * @dev Update bidding strategy based on task performance
     * @param agent Address of the agent
     * @param taskId ID of the task
     * @param score Task score (0-100)
     */
    function updateBiddingStrategy(address agent, bytes32 taskId, uint256 score) internal {
        // Get current bidding strategy
        (uint256 oldConfidence, uint256 oldRiskTolerance, ) = agentRegistry.getAgentBiddingStrategy(agent);
        
        // Calculate new confidence factor based on task score
        uint256 newConfidence;
        if (score >= 70) {
            // Good performance, increase confidence
            uint256 increase = (score - 70) * confidenceAdjustRate / 100;
            newConfidence = oldConfidence + increase;
            if (newConfidence > maxConfidence) newConfidence = maxConfidence;
        } else if (score <= 50) {
            // Poor performance, decrease confidence
            uint256 decrease = (50 - score) * confidenceAdjustRate / 100;
            newConfidence = oldConfidence > decrease ? oldConfidence - decrease : minConfidence;
        } else {
            // Neutral performance, no change
            newConfidence = oldConfidence;
        }
        
        // Calculate new risk tolerance based on task score and agent reputation
        uint256 reputation = agentRegistry.getAgentReputation(agent);
        uint256 newRiskTolerance;
        
        if (reputation >= 70 && score >= 70) {
            // High reputation and good performance, can take more risks
            uint256 increase = riskToleranceAdjustRate;
            newRiskTolerance = oldRiskTolerance + increase;
            if (newRiskTolerance > maxRiskTolerance) newRiskTolerance = maxRiskTolerance;
        } else if (reputation <= 40 || score <= 40) {
            // Low reputation or poor performance, be more conservative
            uint256 decrease = riskToleranceAdjustRate;
            newRiskTolerance = oldRiskTolerance > decrease ? oldRiskTolerance - decrease : minRiskTolerance;
        } else {
            // Neutral case, no change
            newRiskTolerance = oldRiskTolerance;
        }
        
        // Only update if there's a change
        if (newConfidence != oldConfidence || newRiskTolerance != oldRiskTolerance) {
            // Update bidding strategy in AgentRegistry
            agentRegistry.updateBiddingStrategy(agent, newConfidence, newRiskTolerance);
            
            // Record bidding strategy evolution
            recordBiddingStrategyEvolution(
                agent,
                oldConfidence,
                newConfidence,
                oldRiskTolerance,
                newRiskTolerance,
                taskId,
                score
            );
            
            // Emit event
            emit BiddingStrategyUpdated(
                agent,
                oldConfidence,
                newConfidence,
                oldRiskTolerance,
                newRiskTolerance,
                taskId,
                block.timestamp
            );
        }
    }
    
    /**
     * @dev Record bidding strategy evolution
     * @param agent Address of the agent
     * @param oldConfidence Old confidence factor
     * @param newConfidence New confidence factor
     * @param oldRiskTolerance Old risk tolerance
     * @param newRiskTolerance New risk tolerance
     * @param taskId ID of the task
     * @param taskScore Score of the task
     */
    function recordBiddingStrategyEvolution(
        address agent,
        uint256 oldConfidence,
        uint256 newConfidence,
        uint256 oldRiskTolerance,
        uint256 newRiskTolerance,
        bytes32 taskId,
        uint256 taskScore
    ) internal {
        // Create evolution entry
        BiddingStrategyEvolution memory evolution = BiddingStrategyEvolution({
            oldConfidence: oldConfidence,
            newConfidence: newConfidence,
            oldRiskTolerance: oldRiskTolerance,
            newRiskTolerance: newRiskTolerance,
            taskId: taskId,
            taskScore: taskScore,
            timestamp: block.timestamp
        });
        
        // Maintain fixed-size FIFO queue for evolution history
        if (biddingStrategyEvolution[agent].length >= MAX_STRATEGY_HISTORY) {
            // Remove oldest entry
            for (uint256 i = 0; i < biddingStrategyEvolution[agent].length - 1; i++) {
                biddingStrategyEvolution[agent][i] = biddingStrategyEvolution[agent][i + 1];
            }
            biddingStrategyEvolution[agent].pop();
        }
        
        // Add new entry
        biddingStrategyEvolution[agent].push(evolution);
    }
    
    /**
     * @dev Get bidding strategy evolution history for an agent
     * @param agent Address of the agent
     * @return Array of bidding strategy evolution entries
     */
    function getBiddingStrategyEvolution(address agent) external view returns (BiddingStrategyEvolution[] memory) {
        return biddingStrategyEvolution[agent];
    }
    
    /**
     * @dev Manually update agent bidding strategy
     * @param agent Address of the agent
     * @param confidence New confidence factor (0-100)
     * @param riskTolerance New risk tolerance (0-100)
     */
    function manuallyUpdateBiddingStrategy(
        address agent,
        uint256 confidence,
        uint256 riskTolerance
    ) external onlyOwner {
        require(confidence <= 100, "Confidence must be between 0-100");
        require(riskTolerance <= 100, "Risk tolerance must be between 0-100");
        
        // Get current bidding strategy
        (uint256 oldConfidence, uint256 oldRiskTolerance, ) = agentRegistry.getAgentBiddingStrategy(agent);
        
        // Update bidding strategy in AgentRegistry
        agentRegistry.updateBiddingStrategy(agent, confidence, riskTolerance);
        
        // Record bidding strategy evolution
        recordBiddingStrategyEvolution(
            agent,
            oldConfidence,
            confidence,
            oldRiskTolerance,
            riskTolerance,
            bytes32(0), // No specific task ID for manual updates
            0 // No specific task score for manual updates
        );
        
        // Emit event
        emit BiddingStrategyUpdated(
            agent,
            oldConfidence,
            confidence,
            oldRiskTolerance,
            riskTolerance,
            bytes32(0),
            block.timestamp
        );
    }
}