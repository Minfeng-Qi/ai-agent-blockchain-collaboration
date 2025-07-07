// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title AgentRegistry
 * @dev Contract for registering and authenticating agents in the LLM multi-agent system
 */
contract AgentRegistry is Ownable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Agent types based on the paper's framework
    enum AgentType { Undefined, LLM, Orchestrator, Evaluator }

    struct Agent {
        string name;
        string metadataURI;  // URI pointing to agent capabilities (stored on IPFS)
        address owner;       // Address that can update agent info
        uint256 reputation;  // Agent reputation score (0-100)
        bool active;         // Whether the agent is currently active
        uint256 registeredAt;
        AgentType agentType; // Type of agent in the system
    }

    // Learning state structure for agents
    struct AgentLearningState {
        uint256 reputation;
        string[] capabilityTags;
        uint256[] capabilityWeights;
        uint256 workload;
        bytes32[] recentTaskIds;
        uint256[] recentScores;
    }

    // Capability evolution history entry
    struct CapabilityEvolution {
        string tag;
        uint256 oldWeight;
        uint256 newWeight;
        uint256 timestamp;
        bytes32 taskId;
    }

    // Bidding strategy parameters
    struct BiddingStrategy {
        uint256 confidenceFactor;  // 0-100, how confident agent is in capabilities
        uint256 riskTolerance;     // 0-100, how much risk agent is willing to take
        uint256 lastUpdated;
    }

    // Maps agent address to Agent struct
    mapping(address => Agent) public agents;
    
    // List of all registered agent addresses
    address[] public agentAddresses;
    
    // Mapping of nonces used for signature verification (prevents replay attacks)
    mapping(address => mapping(uint256 => bool)) private usedNonces;

    // Capability management
    mapping(address => mapping(string => uint256)) public capabilityWeights;
    mapping(address => string[]) private agentCapabilityTags;
    
    // Workload tracking
    mapping(address => uint256) public agentWorkload;

    // Recent task history for learning
    uint256 public constant MAX_RECENT_TASKS = 10;
    mapping(address => bytes32[]) private recentTaskIds;
    mapping(address => mapping(bytes32 => uint256)) private taskScores;

    // Capability evolution history
    mapping(address => CapabilityEvolution[]) private capabilityEvolutionHistory;
    uint256 public constant MAX_EVOLUTION_HISTORY = 50;

    // Bidding strategy tracking
    mapping(address => BiddingStrategy) public agentBiddingStrategies;

    // Learning curve metrics
    mapping(address => uint256[]) private learningCurveScores;
    uint256 public constant MAX_LEARNING_CURVE_POINTS = 100;

    // Events
    event AgentRegistered(
        address indexed agentAddress,
        string name,
        string metadataURI,
        uint256 timestamp
    );
    
    event AgentUpdated(
        address indexed agentAddress,
        string name,
        string metadataURI,
        uint256 timestamp
    );
    
    event AgentActivated(
        address indexed agentAddress,
        uint256 timestamp
    );
    
    event AgentDeactivated(
        address indexed agentAddress,
        uint256 timestamp
    );
    
    event CapabilitiesUpdated(
        address indexed agentAddress,
        string[] tags,
        uint256[] weights
    );
    
    event TaskScoreRecorded(
        address indexed agentAddress,
        bytes32 indexed taskId,
        uint256 score
    );

    event CapabilityEvolutionRecorded(
        address indexed agentAddress,
        string tag,
        uint256 oldWeight,
        uint256 newWeight,
        bytes32 indexed taskId,
        uint256 timestamp
    );

    event BiddingStrategyUpdated(
        address indexed agentAddress,
        uint256 confidenceFactor,
        uint256 riskTolerance,
        uint256 timestamp
    );

    event LearningCurveUpdated(
        address indexed agentAddress,
        uint256 averageScore,
        uint256 dataPoints,
        uint256 timestamp
    );

    /**
     * @dev Constructor
     */
    constructor() Ownable(msg.sender) {}

    /**
     * @dev Register a new agent
     * @param name Name of the agent
     * @param metadataURI URI pointing to agent capabilities
     * @param agentType Type of agent in the system
     */
    function registerAgent(
        string memory name,
        string memory metadataURI,
        AgentType agentType
    ) external {
        require(agents[msg.sender].registeredAt == 0, "Agent already registered");
        
        agents[msg.sender] = Agent({
            name: name,
            metadataURI: metadataURI,
            owner: msg.sender,
            reputation: 50,  // Default starting reputation
            active: true,    // Active by default
            registeredAt: block.timestamp,
            agentType: agentType
        });
        
        // Add to list of agents
        agentAddresses.push(msg.sender);

        // Initialize bidding strategy with default values
        agentBiddingStrategies[msg.sender] = BiddingStrategy({
            confidenceFactor: 80,  // 80% confidence
            riskTolerance: 50,     // 50% risk tolerance
            lastUpdated: block.timestamp
        });
        
        emit AgentRegistered(msg.sender, name, metadataURI, block.timestamp);
    }

    /**
     * @dev Update agent information
     * @param name New name of the agent
     * @param metadataURI New URI pointing to agent capabilities
     */
    function updateAgent(string memory name, string memory metadataURI) external {
        require(agents[msg.sender].registeredAt > 0, "Agent not registered");
        
        agents[msg.sender].name = name;
        agents[msg.sender].metadataURI = metadataURI;
        
        emit AgentUpdated(msg.sender, name, metadataURI, block.timestamp);
    }

    /**
     * @dev Activate an agent
     * @param agentAddress Address of the agent to activate
     */
    function activateAgent(address agentAddress) external {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(msg.sender == agentAddress || msg.sender == owner(), "Not authorized");
        require(!agents[agentAddress].active, "Agent already active");
        
        agents[agentAddress].active = true;
        
        emit AgentActivated(agentAddress, block.timestamp);
    }

    /**
     * @dev Deactivate an agent
     * @param agentAddress Address of the agent to deactivate
     */
    function deactivateAgent(address agentAddress) external {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(msg.sender == agentAddress || msg.sender == owner(), "Not authorized");
        require(agents[agentAddress].active, "Agent already inactive");
        
        agents[agentAddress].active = false;
        
        emit AgentDeactivated(agentAddress, block.timestamp);
    }

    /**
     * @dev Set agent capabilities
     * @param agentAddress Address of the agent
     * @param tags Array of capability tags
     * @param weights Array of corresponding weights
     */
    function setCapabilities(
        address agentAddress,
        string[] memory tags,
        uint256[] memory weights
    ) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(tags.length == weights.length, "Tags and weights must have same length");
        
        // Clear existing capabilities
        for (uint256 i = 0; i < agentCapabilityTags[agentAddress].length; i++) {
            string memory tag = agentCapabilityTags[agentAddress][i];
            capabilityWeights[agentAddress][tag] = 0;
        }
        
        // Set new capabilities
        delete agentCapabilityTags[agentAddress];
        for (uint256 i = 0; i < tags.length; i++) {
            require(weights[i] <= 100, "Weight must be between 0-100");
            
            // Only add non-zero weights
            if (weights[i] > 0) {
                // Record evolution if this capability existed before
                uint256 oldWeight = capabilityWeights[agentAddress][tags[i]];
                if (oldWeight > 0 && oldWeight != weights[i]) {
                    _recordCapabilityEvolution(
                        agentAddress,
                        tags[i],
                        oldWeight,
                        weights[i],
                        bytes32(0) // No specific task ID for manual updates
                    );
                }
                
                capabilityWeights[agentAddress][tags[i]] = weights[i];
                agentCapabilityTags[agentAddress].push(tags[i]);
            }
        }
        
        emit CapabilitiesUpdated(agentAddress, tags, weights);
    }
    
    /**
     * @dev Get agent capabilities and their weights
     * @param agentAddress Address of the agent
     * @return tags Array of capability tags
     * @return weights Array of corresponding weights
     */
    function getCapabilities(address agentAddress) external view returns (
        string[] memory tags,
        uint256[] memory weights
    ) {
        string[] memory storedTags = agentCapabilityTags[agentAddress];
        uint256 tagCount = storedTags.length;
        
        tags = new string[](tagCount);
        weights = new uint256[](tagCount);
        
        for (uint256 i = 0; i < tagCount; i++) {
            tags[i] = storedTags[i];
            weights[i] = capabilityWeights[agentAddress][tags[i]];
        }
        
        return (tags, weights);
    }
    
    /**
     * @dev Increment agent workload
     * @param agentAddress Address of the agent
     */
    function incrementWorkload(address agentAddress) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        agentWorkload[agentAddress]++;
    }
    
    /**
     * @dev Decrement agent workload
     * @param agentAddress Address of the agent
     */
    function decrementWorkload(address agentAddress) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        if (agentWorkload[agentAddress] > 0) {
            agentWorkload[agentAddress]--;
        }
    }
    
    /**
     * @dev Reset agent workload
     * @param agentAddress Address of the agent
     */
    function resetWorkload(address agentAddress) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        agentWorkload[agentAddress] = 0;
    }
    
    /**
     * @dev Check if an agent is registered and active
     * @param agentAddress Address of the agent to check
     * @return True if agent is registered and active
     */
    function isActiveAgent(address agentAddress) external view returns (bool) {
        return agents[agentAddress].registeredAt > 0 && agents[agentAddress].active;
    }
    
    /**
     * @dev Get total number of registered agents
     * @return Number of registered agents
     */
    function getAgentCount() external view returns (uint256) {
        return agentAddresses.length;
    }
    
    /**
     * @dev Set agent reputation
     * @param agentAddress Address of the agent
     * @param reputation New reputation score
     */
    function setReputation(address agentAddress, uint256 reputation) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(reputation <= 100, "Reputation must be between 0-100");
        
        agents[agentAddress].reputation = reputation;
    }
    
    /**
     * @dev Get agent reputation
     * @param agentAddress Address of the agent
     * @return Agent reputation score
     */
    function getReputation(address agentAddress) external view returns (uint256) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        return agents[agentAddress].reputation;
    }
    
    /**
     * @dev Record a task score for an agent
     * @param agentAddress Address of the agent
     * @param taskId ID of the task
     * @param score Task score (0-100)
     */
    function recordTaskScore(address agentAddress, bytes32 taskId, uint256 score) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(score <= 100, "Score must be between 0-100");
        
        // Store the score
        taskScores[agentAddress][taskId] = score;
        
        // Add to recent tasks, maintaining a fixed-size FIFO queue
        if (recentTaskIds[agentAddress].length >= MAX_RECENT_TASKS) {
            // Remove oldest task if we've reached the limit
            for (uint256 i = 0; i < recentTaskIds[agentAddress].length - 1; i++) {
                recentTaskIds[agentAddress][i] = recentTaskIds[agentAddress][i + 1];
            }
            recentTaskIds[agentAddress].pop();
        }
        
        // Add new task ID
        recentTaskIds[agentAddress].push(taskId);
        
        // Update learning curve
        _updateLearningCurve(agentAddress, score);
        
        emit TaskScoreRecorded(agentAddress, taskId, score);
    }
    
    /**
     * @dev Get agent's learning state including reputation, capabilities, workload, and recent scores
     * @param agentAddress Address of the agent
     * @return Learning state structure with all relevant data
     */
    function getAgentLearningState(address agentAddress) external view returns (AgentLearningState memory) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        
        // Get capabilities
        (string[] memory tags, uint256[] memory weights) = this.getCapabilities(agentAddress);
        
        // Get recent task scores
        bytes32[] memory taskIds = recentTaskIds[agentAddress];
        uint256[] memory scores = new uint256[](taskIds.length);
        
        for (uint256 i = 0; i < taskIds.length; i++) {
            scores[i] = taskScores[agentAddress][taskIds[i]];
        }
        
        // Return the complete learning state
        return AgentLearningState({
            reputation: agents[agentAddress].reputation,
            capabilityTags: tags,
            capabilityWeights: weights,
            workload: agentWorkload[agentAddress],
            recentTaskIds: taskIds,
            recentScores: scores
        });
    }
    
    /**
     * @dev Get agent's recent task history
     * @param agentAddress Address of the agent
     * @return taskIds Array of recent task IDs
     * @return scores Array of corresponding scores
     */
    function getAgentRecentTasks(address agentAddress) external view returns (
        bytes32[] memory taskIds,
        uint256[] memory scores
    ) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        
        taskIds = recentTaskIds[agentAddress];
        scores = new uint256[](taskIds.length);
        
        for (uint256 i = 0; i < taskIds.length; i++) {
            scores[i] = taskScores[agentAddress][taskIds[i]];
        }
        
        return (taskIds, scores);
    }

    /**
     * @dev Get agent reputation
     * @param agentAddress Address of the agent
     * @return Agent reputation score
     */
    function getAgentReputation(address agentAddress) external view returns (uint256) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        return agents[agentAddress].reputation;
    }

    /**
     * @dev Update agent bidding strategy
     * @param agentAddress Address of the agent
     * @param confidenceFactor New confidence factor (0-100)
     * @param riskTolerance New risk tolerance (0-100)
     */
    function updateBiddingStrategy(
        address agentAddress,
        uint256 confidenceFactor,
        uint256 riskTolerance
    ) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        require(confidenceFactor <= 100, "Confidence factor must be between 0-100");
        require(riskTolerance <= 100, "Risk tolerance must be between 0-100");
        
        agentBiddingStrategies[agentAddress] = BiddingStrategy({
            confidenceFactor: confidenceFactor,
            riskTolerance: riskTolerance,
            lastUpdated: block.timestamp
        });
        
        emit BiddingStrategyUpdated(
            agentAddress,
            confidenceFactor,
            riskTolerance,
            block.timestamp
        );
    }

    /**
     * @dev Get agent bidding strategy
     * @param agentAddress Address of the agent
     * @return confidenceFactor Confidence factor
     * @return riskTolerance Risk tolerance
     * @return lastUpdated Last update timestamp
     */
    function getAgentBiddingStrategy(address agentAddress) external view returns (
        uint256 confidenceFactor,
        uint256 riskTolerance,
        uint256 lastUpdated
    ) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        
        BiddingStrategy memory strategy = agentBiddingStrategies[agentAddress];
        return (
            strategy.confidenceFactor,
            strategy.riskTolerance,
            strategy.lastUpdated
        );
    }

    /**
     * @dev Get agent capability evolution history
     * @param agentAddress Address of the agent
     * @return Array of capability evolution entries
     */
    function getCapabilityEvolutionHistory(address agentAddress) external view returns (
        CapabilityEvolution[] memory
    ) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        return capabilityEvolutionHistory[agentAddress];
    }

    /**
     * @dev Get agent learning curve
     * @param agentAddress Address of the agent
     * @return Array of learning curve scores
     */
    function getLearningCurve(address agentAddress) external view returns (
        uint256[] memory
    ) {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        return learningCurveScores[agentAddress];
    }

    /**
     * @dev Record capability evolution
     * @param agentAddress Address of the agent
     * @param tag Capability tag
     * @param oldWeight Old capability weight
     * @param newWeight New capability weight
     * @param taskId Task ID that triggered the evolution
     */
    function recordCapabilityEvolution(
        address agentAddress,
        string memory tag,
        uint256 oldWeight,
        uint256 newWeight,
        bytes32 taskId
    ) external onlyOwner {
        require(agents[agentAddress].registeredAt > 0, "Agent not registered");
        _recordCapabilityEvolution(agentAddress, tag, oldWeight, newWeight, taskId);
    }

    /**
     * @dev Internal function to record capability evolution
     */
    function _recordCapabilityEvolution(
        address agentAddress,
        string memory tag,
        uint256 oldWeight,
        uint256 newWeight,
        bytes32 taskId
    ) internal {
        // Create evolution entry
        CapabilityEvolution memory evolution = CapabilityEvolution({
            tag: tag,
            oldWeight: oldWeight,
            newWeight: newWeight,
            timestamp: block.timestamp,
            taskId: taskId
        });
        
        // Maintain fixed-size FIFO queue for evolution history
        if (capabilityEvolutionHistory[agentAddress].length >= MAX_EVOLUTION_HISTORY) {
            // Remove oldest entry
            for (uint256 i = 0; i < capabilityEvolutionHistory[agentAddress].length - 1; i++) {
                capabilityEvolutionHistory[agentAddress][i] = capabilityEvolutionHistory[agentAddress][i + 1];
            }
            capabilityEvolutionHistory[agentAddress].pop();
        }
        
        // Add new entry
        capabilityEvolutionHistory[agentAddress].push(evolution);
        
        emit CapabilityEvolutionRecorded(
            agentAddress,
            tag,
            oldWeight,
            newWeight,
            taskId,
            block.timestamp
        );
    }

    /**
     * @dev Update agent learning curve with new score
     * @param agentAddress Address of the agent
     * @param score New score to add to learning curve
     */
    function _updateLearningCurve(address agentAddress, uint256 score) internal {
        // Add score to learning curve
        if (learningCurveScores[agentAddress].length >= MAX_LEARNING_CURVE_POINTS) {
            // Remove oldest score if we've reached the limit
            for (uint256 i = 0; i < learningCurveScores[agentAddress].length - 1; i++) {
                learningCurveScores[agentAddress][i] = learningCurveScores[agentAddress][i + 1];
            }
            learningCurveScores[agentAddress].pop();
        }
        
        // Add new score
        learningCurveScores[agentAddress].push(score);
        
        // Calculate average score
        uint256 sum = 0;
        for (uint256 i = 0; i < learningCurveScores[agentAddress].length; i++) {
            sum += learningCurveScores[agentAddress][i];
        }
        uint256 avgScore = sum / learningCurveScores[agentAddress].length;
        
        emit LearningCurveUpdated(
            agentAddress,
            avgScore,
            learningCurveScores[agentAddress].length,
            block.timestamp
        );
    }
    /**
     * @dev Get all registered agent addresses
     * @return Array of agent addresses
     */
    function getAllAgents() external view returns (address[] memory) {
        return agentAddresses;
    }
}
