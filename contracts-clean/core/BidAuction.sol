// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./AgentRegistry.sol";
import "./TaskManager.sol";
import "./IncentiveEngine.sol";

/**
 * @title BidAuction
 * @dev Contract for agent bidding, utility scoring, and fair assignment
 */
contract BidAuction is Ownable {
    // Reference to other contracts
    AgentRegistry public agentRegistry;
    TaskManager public taskManager;
    IncentiveEngine public incentiveEngine;
    
    struct Bid {
        address agent;
        bytes32 taskId;
        uint256 utilityScore;  // Self-reported utility score (0-100)
        uint256 bidAmount;     // Amount of tokens bid
        uint256 timestamp;
        bytes signature;       // Signature of the bid
        bool selected;         // Whether this bid was selected
    }
    
    // Maps task ID to array of bids
    mapping(bytes32 => Bid[]) public taskBids;
    
    // Maps task ID to bidding deadline
    mapping(bytes32 => uint256) public biddingDeadlines;
    
    // Maps task ID to whether it has been assigned
    mapping(bytes32 => bool) public taskAssigned;
    
    // Mapping of nonces used for signature verification (prevents replay attacks)
    mapping(address => mapping(uint256 => bool)) private usedNonces;
    
    // Events
    event BidPlaced(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 utilityScore,
        uint256 bidAmount,
        uint256 timestamp
    );
    
    event BiddingOpened(
        bytes32 indexed taskId,
        uint256 deadline,
        uint256 timestamp
    );
    
    event BiddingClosed(
        bytes32 indexed taskId,
        uint256 bidCount,
        uint256 timestamp
    );
    
    event TaskAssigned(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 utilityScore,
        uint256 bidAmount,
        uint256 timestamp
    );
    
    // New event for calculated utility
    event UtilityCalculated(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 calculatedUtility,
        uint256 timestamp
    );

    /**
     * @dev Constructor
     * @param _agentRegistryAddress Address of the AgentRegistry contract
     * @param _taskManagerAddress Address of the TaskManager contract
     */
    constructor(address _agentRegistryAddress, address _taskManagerAddress) Ownable(msg.sender) {
        agentRegistry = AgentRegistry(_agentRegistryAddress);
        taskManager = TaskManager(_taskManagerAddress);
    }
    
    /**
     * @dev Set IncentiveEngine contract address
     * @param _incentiveEngineAddress Address of the IncentiveEngine contract
     */
    function setIncentiveEngine(address _incentiveEngineAddress) external onlyOwner {
        incentiveEngine = IncentiveEngine(_incentiveEngineAddress);
    }
    
    /**
     * @dev Open bidding for a task
     * @param taskId ID of the task
     * @param biddingDuration Duration of bidding period in seconds (defaults to 3600 if not specified)
     */
    function openBidding(bytes32 taskId, uint256 biddingDuration) external {
        // If biddingDuration is 0, use the default of 1 hour
        if (biddingDuration == 0) {
            biddingDuration = 3600;
        }
        
        // Only task creator or contract owner can open bidding
        require(
            taskManager.getTaskCreator(taskId) == msg.sender || owner() == msg.sender,
            "Not authorized"
        );
        
        // Ensure task is in Open state
        require(
            taskManager.getTaskStatus(taskId) == TaskManager.TaskStatus.Open,
            "Task not in Open state"
        );
        
        // Set bidding deadline
        uint256 deadline = block.timestamp + biddingDuration;
        biddingDeadlines[taskId] = deadline;
        
        // Emit event
        emit BiddingOpened(taskId, deadline, block.timestamp);
    }
    
    /**
     * @dev Place a bid on a task (simplified version for testing)
     * @param taskId ID of the task
     * @param bidAmount Amount of tokens bid
     */
    function placeBid(
        bytes32 taskId,
        uint256 bidAmount
    ) external {
        // Verify agent is registered and active
        require(agentRegistry.isActiveAgent(msg.sender), "Not a registered active agent");
        
        // Verify bidding is open
        require(biddingDeadlines[taskId] > 0, "Bidding not open");
        require(block.timestamp < biddingDeadlines[taskId], "Bidding deadline passed");
        
        // Verify task is in Open state
        require(
            taskManager.getTaskStatus(taskId) == TaskManager.TaskStatus.Open,
            "Task not in Open state"
        );
        
        // Default values
        uint256 utilityScore = 50; // Default utility score
        bytes memory signature = ""; // Empty signature
        uint256 nonce = block.timestamp; // Use timestamp as nonce
        
        // Store bid
        taskBids[taskId].push(Bid({
            agent: msg.sender,
            taskId: taskId,
            utilityScore: utilityScore,
            bidAmount: bidAmount,
            timestamp: block.timestamp,
            signature: signature,
            selected: false
        }));
        
        // Emit event
        emit BidPlaced(
            taskId,
            msg.sender,
            utilityScore,
            bidAmount,
            block.timestamp
        );
    }
    
    /**
     * @dev Place a bid on a task
     * @param taskId ID of the task
     * @param utilityScore Self-reported utility score (0-100)
     * @param bidAmount Amount of tokens bid
     * @param signature Signature of the bid
     * @param nonce One-time use nonce to prevent replay attacks
     */
    function placeBidWithSignature(
        bytes32 taskId,
        uint256 utilityScore,
        uint256 bidAmount,
        bytes memory signature,
        uint256 nonce
    ) external {
        // Verify agent is registered and active
        require(agentRegistry.isActiveAgent(msg.sender), "Not a registered active agent");
        
        // Verify bidding is open
        require(biddingDeadlines[taskId] > 0, "Bidding not open");
        require(block.timestamp < biddingDeadlines[taskId], "Bidding deadline passed");
        
        // Verify task is in Open state
        require(
            taskManager.getTaskStatus(taskId) == TaskManager.TaskStatus.Open,
            "Task not in Open state"
        );
        
        // Verify nonce hasn't been used
        require(!usedNonces[msg.sender][nonce], "Nonce already used");
        usedNonces[msg.sender][nonce] = true;
        
        // Verify utility score is valid
        require(utilityScore <= 100, "Utility score must be between 0-100");
        
        // Store bid
        taskBids[taskId].push(Bid({
            agent: msg.sender,
            taskId: taskId,
            utilityScore: utilityScore,
            bidAmount: bidAmount,
            timestamp: block.timestamp,
            signature: signature,
            selected: false
        }));
        
        // Emit event
        emit BidPlaced(
            taskId,
            msg.sender,
            utilityScore,
            bidAmount,
            block.timestamp
        );
    }
    
    /**
     * @dev Calculate agent utility for a task using the IncentiveEngine
     * @param taskId ID of the task
     * @param agent Address of the agent
     * @return Calculated utility score (0-100)
     */
    function calculateAgentUtility(bytes32 taskId, address agent) public view returns (uint256) {
        // Get task information
        (
            ,
            uint256 reward,
            string[] memory capabilities,
            ,
            ,
        ) = taskManager.getTaskExecutionInfo(taskId);
        
        // Get agent workload
        uint256 agentWorkload = incentiveEngine.getAgentWorkload(agent);
        
        // Calculate utility using the enhanced formula from IncentiveEngine
        uint256 calculatedUtility = incentiveEngine.calculateUtility(
            agent,
            capabilities,
            reward,
            agentWorkload
        );
        
        return calculatedUtility;
    }
    
    /**
     * @dev Close bidding and assign task to best bidder
     * @param taskId ID of the task
     */
    function closeBidding(bytes32 taskId) external {
        // Only task creator or contract owner can close bidding
        require(
            taskManager.getTaskCreator(taskId) == msg.sender || owner() == msg.sender,
            "Not authorized"
        );
        
        // Verify bidding deadline has passed or is current
        require(biddingDeadlines[taskId] > 0, "Bidding not open");
        require(block.timestamp >= biddingDeadlines[taskId], "Bidding deadline not yet passed");
        
        // Verify task hasn't been assigned yet
        require(!taskAssigned[taskId], "Task already assigned");
        
        // Get bids for this task
        Bid[] storage bids = taskBids[taskId];
        require(bids.length > 0, "No bids received");
        
        // Find best bid using a weighted scoring system
        address bestBidder = address(0);
        uint256 highestScore = 0;
        uint256 bestBidIndex = 0;
        
        for (uint256 i = 0; i < bids.length; i++) {
            Bid storage bid = bids[i];
            
            // Get agent reputation
            uint256 reputation = incentiveEngine.getAgentReputation(bid.agent);
            
            // Calculate utility using IncentiveEngine if available
            uint256 calculatedUtility = bid.utilityScore; // Default to self-reported
            if (address(incentiveEngine) != address(0)) {
                calculatedUtility = calculateAgentUtility(taskId, bid.agent);
                
                // Emit utility calculation event
                emit UtilityCalculated(
                    taskId,
                    bid.agent,
                    calculatedUtility,
                    block.timestamp
                );
            }
            
            // Calculate weighted score (utility * reputation * bid amount)
            uint256 weightedScore = (calculatedUtility * reputation * bid.bidAmount) / 10000;
            
            if (weightedScore > highestScore) {
                highestScore = weightedScore;
                bestBidder = bid.agent;
                bestBidIndex = i;
            }
        }
        
        // Mark the winning bid
        bids[bestBidIndex].selected = true;
        
        // Mark task as assigned
        taskAssigned[taskId] = true;
        
        // Assign task to best bidder
        taskManager.assignTask(taskId, bestBidder);
        
        // Update agent reputation via IncentiveEngine
        if (address(incentiveEngine) != address(0)) {
            incentiveEngine.recordBidWin(bestBidder, taskId);
        }
        
        // Emit events
        emit BiddingClosed(taskId, bids.length, block.timestamp);
        emit TaskAssigned(
            taskId,
            bestBidder,
            bids[bestBidIndex].utilityScore,
            bids[bestBidIndex].bidAmount,
            block.timestamp
        );
    }
    
    /**
     * @dev Manually assign a task to an agent (for testing or emergency use)
     * @param taskId ID of the task
     * @param agent Address of the agent
     */
    function assignTaskManually(bytes32 taskId, address agent) external onlyOwner {
        // Verify task hasn't been assigned yet
        require(!taskAssigned[taskId], "Task already assigned");
        
        // Mark task as assigned
        taskAssigned[taskId] = true;
        
        // Assign task to agent
        taskManager.assignTask(taskId, agent);
        
        // Update agent reputation via IncentiveEngine
        if (address(incentiveEngine) != address(0)) {
            incentiveEngine.recordBidWin(agent, taskId);
        }
        
        // Emit event
        emit TaskAssigned(
            taskId,
            agent,
            50, // Default utility score
            0,  // No bid amount
            block.timestamp
        );
    }
    
    /**
     * @dev Get all bids for a task
     * @param taskId ID of the task
     * @return Array of bids
     */
    function getAllBids(bytes32 taskId) external view returns (Bid[] memory) {
        return taskBids[taskId];
    }
    
    /**
     * @dev Get the winning bid for a task
     * @param taskId ID of the task
     * @return agent Address of the winning agent
     * @return utilityScore Utility score of the winning bid
     * @return bidAmount Bid amount of the winning bid
     * @return timestamp Timestamp of the winning bid
     */
    function getWinningBid(bytes32 taskId) external view returns (
        address agent,
        uint256 utilityScore,
        uint256 bidAmount,
        uint256 timestamp
    ) {
        require(taskAssigned[taskId], "Task not assigned yet");
        
        Bid[] storage bids = taskBids[taskId];
        
        for (uint256 i = 0; i < bids.length; i++) {
            if (bids[i].selected) {
                return (
                    bids[i].agent,
                    bids[i].utilityScore,
                    bids[i].bidAmount,
                    bids[i].timestamp
                );
            }
        }
        
        revert("No winning bid found");
    }
    
    /**
     * @dev Check if an agent has bid on a task
     * @param taskId ID of the task
     * @param agent Address of the agent
     * @return True if agent has bid on the task
     */
    function hasAgentBid(bytes32 taskId, address agent) external view returns (bool) {
        Bid[] storage bids = taskBids[taskId];
        
        for (uint256 i = 0; i < bids.length; i++) {
            if (bids[i].agent == agent) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Check if bidding is open for a task
     * @param taskId ID of the task
     * @return True if bidding is open
     */
    function isBiddingOpen(bytes32 taskId) external view returns (bool) {
        return biddingDeadlines[taskId] > 0 && block.timestamp < biddingDeadlines[taskId];
    }
    
    /**
     * @dev Get all bids for a task
     * @param taskId ID of the task
     * @return agents Array of bidding agent addresses
     * @return utilityScores Array of utility scores
     * @return bidAmounts Array of bid amounts
     * @return timestamps Array of bid timestamps
     */
    function getTaskBids(bytes32 taskId) external view returns (
        address[] memory agents,
        uint256[] memory utilityScores,
        uint256[] memory bidAmounts,
        uint256[] memory timestamps
    ) {
        Bid[] storage bids = taskBids[taskId];
        uint256 bidCount = bids.length;
        
        agents = new address[](bidCount);
        utilityScores = new uint256[](bidCount);
        bidAmounts = new uint256[](bidCount);
        timestamps = new uint256[](bidCount);
        
        for (uint256 i = 0; i < bidCount; i++) {
            agents[i] = bids[i].agent;
            utilityScores[i] = bids[i].utilityScore;
            bidAmounts[i] = bids[i].bidAmount;
            timestamps[i] = bids[i].timestamp;
        }
        
        return (agents, utilityScores, bidAmounts, timestamps);
    }
}