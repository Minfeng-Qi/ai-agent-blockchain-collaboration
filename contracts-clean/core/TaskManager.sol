// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./AgentRegistry.sol";
import "./BidAuction.sol";
import "./IncentiveEngine.sol";

/**
 * @title TaskManager
 * @dev Contract to submit tasks, store metadata, and enforce capability/reputation-based assignment
 */
contract TaskManager is Ownable {
    // Reference to other contracts
    AgentRegistry public agentRegistry;
    BidAuction public bidAuction;
    IncentiveEngine public incentiveEngine;
    
    // Task statuses
    enum TaskStatus { Created, Open, Assigned, InProgress, Completed, Failed, Cancelled }
    
    struct Task {
        bytes32 taskId;
        address creator;
        string metadataURI;  // IPFS URI for task details
        string[] capabilities;  // Required capabilities
        uint256 minReputation;  // Minimum reputation required
        uint256 reward;  // Reward amount in tokens
        uint256 deadline;  // Deadline timestamp
        TaskStatus status;
        address assignedAgent;
        uint256 createdAt;
        uint256 assignedAt;
        uint256 completedAt;
        string resultURI;  // IPFS URI for task result
        bool isEvaluated;  // Whether the task has been evaluated
    }
    
    // Maps task ID to Task struct
    mapping(bytes32 => Task) public tasks;
    
    // List of all task IDs
    bytes32[] public taskIds;
    
    // Maps agent address to assigned task IDs
    mapping(address => bytes32[]) public agentTasks;
    
    // Events
    event TaskCreated(
        bytes32 indexed taskId,
        address indexed creator,
        string metadataURI,
        string[] capabilities,
        uint256 minReputation,
        uint256 reward,
        uint256 deadline
    );
    
    event TaskStatusUpdated(
        bytes32 indexed taskId,
        TaskStatus indexed status,
        address indexed agent,
        uint256 timestamp
    );
    
    event TaskAssigned(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 timestamp
    );
    
    event TaskCompleted(
        bytes32 indexed taskId,
        address indexed agent,
        string resultURI,
        uint256 timestamp
    );
    
    event TaskFailed(
        bytes32 indexed taskId,
        address indexed agent,
        string reason,
        uint256 timestamp
    );
    
    // New event for task evaluation
    event TaskEvaluated(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 qualityScore,
        uint256 delayRatio,
        uint256 finalScore,
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
     * @dev Set BidAuction contract address
     * @param _bidAuctionAddress Address of the BidAuction contract
     */
    function setBidAuction(address _bidAuctionAddress) external onlyOwner {
        bidAuction = BidAuction(_bidAuctionAddress);
    }
    
    /**
     * @dev Set IncentiveEngine contract address
     * @param _incentiveEngineAddress Address of the IncentiveEngine contract
     */
    function setIncentiveEngine(address _incentiveEngineAddress) external onlyOwner {
        incentiveEngine = IncentiveEngine(_incentiveEngineAddress);
    }
    
    /**
     * @dev Create a new task
     * @param metadataURI IPFS URI for task details
     * @param capabilities Required capabilities
     * @param minReputation Minimum reputation required
     * @param reward Reward amount in tokens
     * @param deadline Deadline timestamp
     * @return Task ID
     */
    function createTask(
        string memory metadataURI,
        string[] memory capabilities,
        uint256 minReputation,
        uint256 reward,
        uint256 deadline
    ) external returns (bytes32) {
        require(capabilities.length > 0, "At least one capability required");
        require(deadline > block.timestamp, "Deadline must be in the future");
        
        // Generate task ID
        bytes32 taskId = keccak256(abi.encodePacked(
            msg.sender,
            metadataURI,
            block.timestamp,
            taskIds.length
        ));
        
        // Create task
        tasks[taskId] = Task({
            taskId: taskId,
            creator: msg.sender,
            metadataURI: metadataURI,
            capabilities: capabilities,
            minReputation: minReputation,
            reward: reward,
            deadline: deadline,
            status: TaskStatus.Created,
            assignedAgent: address(0),
            createdAt: block.timestamp,
            assignedAt: 0,
            completedAt: 0,
            resultURI: "",
            isEvaluated: false
        });
        
        // Add to task list
        taskIds.push(taskId);
        
        // Emit event
        emit TaskCreated(
            taskId,
            msg.sender,
            metadataURI,
            capabilities,
            minReputation,
            reward,
            deadline
        );
        
        return taskId;
    }
    
    /**
     * @dev Open a task for bidding
     * @param taskId ID of the task to open
     */
    function openTask(bytes32 taskId) external {
        Task storage task = tasks[taskId];
        
        require(task.creator == msg.sender || owner() == msg.sender, "Not authorized");
        require(task.status == TaskStatus.Created, "Task not in Created state");
        
        task.status = TaskStatus.Open;
        
        // Emit event
        emit TaskStatusUpdated(
            taskId,
            TaskStatus.Open,
            address(0),
            block.timestamp
        );
    }
    
    /**
     * @dev Assign a task to an agent (called by BidAuction)
     * @param taskId ID of the task to assign
     * @param agent Address of the agent to assign
     */
    function assignTask(bytes32 taskId, address agent) external {
        require(address(bidAuction) == msg.sender, "Only BidAuction can assign tasks");
        
        Task storage task = tasks[taskId];
        require(task.status == TaskStatus.Open, "Task not open for assignment");
        require(agentRegistry.isActiveAgent(agent), "Not a registered active agent");
        
        // Check reputation requirement
        uint256 agentReputation = agentRegistry.getAgentLearningState(agent).reputation;
        require(agentReputation >= task.minReputation, "Agent reputation too low");
        
        // Assign task
        task.status = TaskStatus.Assigned;
        task.assignedAgent = agent;
        task.assignedAt = block.timestamp;
        
        // Add to agent's task list
        agentTasks[agent].push(taskId);
        
        // Emit events
        emit TaskAssigned(taskId, agent, block.timestamp);
        emit TaskStatusUpdated(taskId, TaskStatus.Assigned, agent, block.timestamp);
    }
    
    /**
     * @dev Start working on a task
     * @param taskId ID of the task to start
     */
    function startTask(bytes32 taskId) external {
        Task storage task = tasks[taskId];
        
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.Assigned, "Task not in Assigned state");
        
        task.status = TaskStatus.InProgress;
        
        // Emit event
        emit TaskStatusUpdated(taskId, TaskStatus.InProgress, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Complete a task
     * @param taskId ID of the task to complete
     * @param resultURI IPFS URI for task result
     */
    function completeTask(bytes32 taskId, string memory resultURI) external {
        Task storage task = tasks[taskId];
        
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.InProgress, "Task not in InProgress state");
        
        task.status = TaskStatus.Completed;
        task.completedAt = block.timestamp;
        task.resultURI = resultURI;
        
        // Emit events
        emit TaskCompleted(taskId, msg.sender, resultURI, block.timestamp);
        emit TaskStatusUpdated(taskId, TaskStatus.Completed, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Report task failure
     * @param taskId ID of the failed task
     * @param reason Reason for failure
     */
    function failTask(bytes32 taskId, string memory reason) external {
        Task storage task = tasks[taskId];
        
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.InProgress, "Task not in InProgress state");
        
        task.status = TaskStatus.Failed;
        
        // Emit events
        emit TaskFailed(taskId, msg.sender, reason, block.timestamp);
        emit TaskStatusUpdated(taskId, TaskStatus.Failed, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Cancel a task (only creator or owner)
     * @param taskId ID of the task to cancel
     */
    function cancelTask(bytes32 taskId) external {
        Task storage task = tasks[taskId];
        
        require(task.creator == msg.sender || owner() == msg.sender, "Not authorized");
        require(task.status != TaskStatus.Completed, "Cannot cancel completed task");
        require(task.status != TaskStatus.Cancelled, "Task already cancelled");
        
        task.status = TaskStatus.Cancelled;
        
        // Emit event
        emit TaskStatusUpdated(taskId, TaskStatus.Cancelled, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get all tasks
     * @return Array of task IDs
     */
    function getAllTasks() external view returns (bytes32[] memory) {
        return taskIds;
    }
    
    /**
     * @dev Get tasks assigned to an agent
     * @param agent Address of the agent
     * @return Array of task IDs
     */
    function getAgentTasks(address agent) external view returns (bytes32[] memory) {
        return agentTasks[agent];
    }
    
    /**
     * @dev Get tasks with specific status
     * @param status Task status to filter by
     * @return Array of task IDs
     */
    function getTasksByStatus(TaskStatus status) external view returns (bytes32[] memory) {
        // First, count tasks with the specified status
        uint256 count = 0;
        for (uint256 i = 0; i < taskIds.length; i++) {
            if (tasks[taskIds[i]].status == status) {
                count++;
            }
        }
        
        // Create array of the right size
        bytes32[] memory result = new bytes32[](count);
        
        // Fill the array
        uint256 index = 0;
        for (uint256 i = 0; i < taskIds.length; i++) {
            if (tasks[taskIds[i]].status == status) {
                result[index] = taskIds[i];
                index++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Evaluate task outcome and update agent reputation/capabilities
     * @param taskId ID of the completed task
     * @param qualityScore Quality score (0-100)
     * @param delayRatio Delay ratio (0-100, where 0 = no delay)
     * @param tags Array of capability tags relevant to the task
     * @param tagScores Array of scores for each tag (0-100)
     * @return Final score computed by IncentiveEngine
     */
    function evaluateTaskOutcome(
        bytes32 taskId,
        uint256 qualityScore,
        uint256 delayRatio,
        string[] memory tags,
        uint256[] memory tagScores
    ) external onlyOwner returns (uint256) {
        Task storage task = tasks[taskId];
        
        require(task.status == TaskStatus.Completed, "Task not completed");
        require(!task.isEvaluated, "Task already evaluated");
        require(qualityScore <= 100, "Quality score must be 0-100");
        require(delayRatio <= 100, "Delay ratio must be 0-100");
        require(tags.length == tagScores.length, "Tags and scores must have same length");
        
        // Mark task as evaluated
        task.isEvaluated = true;
        
        // Compute task score via IncentiveEngine
        uint256 finalScore = incentiveEngine.computeTaskScore(
            task.assignedAgent,
            taskId,
            qualityScore,
            delayRatio
        );
        
        // Update capability-specific weights
        incentiveEngine.updateSpecificCapabilityWeights(
            task.assignedAgent,
            taskId,
            tags,
            tagScores
        );
        
        // Record task quality
        incentiveEngine.recordTaskQuality(
            taskId,
            task.assignedAgent,
            qualityScore
        );
        
        // Emit evaluation event
        emit TaskEvaluated(
            taskId,
            task.assignedAgent,
            qualityScore,
            delayRatio,
            finalScore,
            block.timestamp
        );
        
        return finalScore;
    }
    
    /**
     * @dev Get task execution information for incentive calculations
     * @param taskId ID of the task
     * @return agent Address of the assigned agent
     * @return reward Task reward amount
     * @return capabilities Required capabilities
     * @return deadline Task deadline
     * @return assignedAt When the task was assigned
     * @return completedAt When the task was completed
     */
    function getTaskExecutionInfo(bytes32 taskId) external view returns (
        address agent,
        uint256 reward,
        string[] memory capabilities,
        uint256 deadline,
        uint256 assignedAt,
        uint256 completedAt
    ) {
        Task storage task = tasks[taskId];
        
        return (
            task.assignedAgent,
            task.reward,
            task.capabilities,
            task.deadline,
            task.assignedAt,
            task.completedAt
        );
    }
    
    /**
     * @dev Check if an agent has the required capabilities for a task
     * @param taskId ID of the task
     * @param agent Address of the agent
     * @return True if agent has all required capabilities
     */
    function agentHasCapabilities(bytes32 taskId, address agent) external view returns (bool) {
        // Get agent capabilities from AgentRegistry
        (string[] memory tags, ) = agentRegistry.getCapabilities(agent);
        
        // This is a simplified check - in a real implementation, 
        // you would compare the agent's capabilities against the task's required capabilities
        
        // For now, just return true if the agent has any capabilities
        return tags.length > 0;
    }
    
    /**
     * @dev Get the status of a task
     * @param taskId ID of the task
     * @return Status of the task
     */
    function getTaskStatus(bytes32 taskId) external view returns (TaskStatus) {
        return tasks[taskId].status;
    }
    
    /**
     * @dev Get the creator of a task
     * @param taskId ID of the task
     * @return Address of the task creator
     */
    function getTaskCreator(bytes32 taskId) external view returns (address) {
        return tasks[taskId].creator;
    }
    
    /**
     * @dev Get the minimum reputation required for a task
     * @param taskId ID of the task
     * @return Minimum reputation required
     */
    function getTaskMinReputation(bytes32 taskId) external view returns (uint256) {
        return tasks[taskId].minReputation;
    }
}