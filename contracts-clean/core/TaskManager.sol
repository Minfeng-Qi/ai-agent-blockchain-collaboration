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
        string title;  // Task title
        string description;  // Task description
        string[] capabilities;  // Required capabilities
        uint256 minReputation;  // Minimum reputation required
        uint256 reward;  // Reward amount in tokens
        uint256 deadline;  // Deadline timestamp
        TaskStatus status;
        address assignedAgent;
        uint256 createdAt;
        uint256 assignedAt;
        uint256 completedAt;
        string result;  // Task result
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
        string title,
        string description,
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
        string result,
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
    
    // New event for agent collaboration start
    event AgentCollaborationStarted(
        bytes32 indexed taskId,
        address indexed creator,
        address[] selectedAgents,
        string collaborationId,
        uint256 timestamp
    );
    
    // Event for task cancelled
    event TaskCancelled(
        bytes32 indexed taskId,
        address indexed actor,
        string reason,
        uint256 timestamp
    );
    
    // Event for task updated
    event TaskUpdated(
        bytes32 indexed taskId,
        address indexed updater,
        string field,
        string oldValue,
        string newValue,
        uint256 timestamp
    );
    
    // Event for collaboration conversation start
    event CollaborationConversationStarted(
        bytes32 indexed taskId,
        string indexed conversationId,
        address[] participants,
        string conversationTopic,
        uint256 timestamp
    );
    
    // Event for collaboration message
    event CollaborationMessage(
        bytes32 indexed taskId,
        string indexed conversationId,
        address indexed sender,
        string message,
        uint256 messageIndex,
        uint256 timestamp
    );
    
    // Event for collaboration result
    event CollaborationResult(
        bytes32 indexed taskId,
        string indexed conversationId,
        address[] participants,
        string result,
        string conversationSummary,
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
     * @param title Task title
     * @param description Task description
     * @param capabilities Required capabilities
     * @param minReputation Minimum reputation required
     * @param reward Reward amount in tokens
     * @param deadline Deadline timestamp
     * @return Task ID
     */
    function createTask(
        string memory title,
        string memory description,
        string[] memory capabilities,
        uint256 minReputation,
        uint256 reward,
        uint256 deadline
    ) external returns (bytes32) {
        require(bytes(title).length > 0, "Title cannot be empty");
        require(bytes(description).length > 0, "Description cannot be empty");
        require(capabilities.length > 0, "At least one capability required");
        require(deadline > block.timestamp, "Deadline must be in the future");
        
        // Generate task ID
        bytes32 taskId = keccak256(abi.encodePacked(
            msg.sender,
            title,
            description,
            block.timestamp,
            taskIds.length
        ));
        
        // Create task
        tasks[taskId] = Task({
            taskId: taskId,
            creator: msg.sender,
            title: title,
            description: description,
            capabilities: capabilities,
            minReputation: minReputation,
            reward: reward,
            deadline: deadline,
            status: TaskStatus.Open,  // Directly set to Open
            assignedAgent: address(0),
            createdAt: block.timestamp,
            assignedAt: 0,
            completedAt: 0,
            result: "",
            isEvaluated: false
        });
        
        // Add to task list
        taskIds.push(taskId);
        
        // Emit event
        emit TaskCreated(
            taskId,
            msg.sender,
            title,
            description,
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
        // Allow owner or BidAuction to assign tasks for intelligent assignment system
        require(msg.sender == owner() || address(bidAuction) == msg.sender, "Only owner or BidAuction can assign tasks");
        
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
     * @param result Task result
     */
    function completeTask(bytes32 taskId, string memory result) external {
        Task storage task = tasks[taskId];
        
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.InProgress, "Task not in InProgress state");
        
        task.status = TaskStatus.Completed;
        task.completedAt = block.timestamp;
        task.result = result;
        
        // Emit events
        emit TaskCompleted(taskId, msg.sender, result, block.timestamp);
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
     * @dev Start agent collaboration for a task
     * @param taskId ID of the task to start collaboration for
     * @param selectedAgents Array of selected agent addresses
     * @param collaborationId Unique collaboration identifier
     */
    function startAgentCollaboration(
        bytes32 taskId, 
        address[] memory selectedAgents,
        string memory collaborationId
    ) external {
        Task storage task = tasks[taskId];
        
        require(task.creator == msg.sender || owner() == msg.sender, "Not authorized");
        require(task.status == TaskStatus.Open, "Task not in Open state");
        require(selectedAgents.length > 0, "At least one agent required");
        require(bytes(collaborationId).length > 0, "Collaboration ID required");
        
        // Verify all selected agents are active and have required capabilities
        for (uint256 i = 0; i < selectedAgents.length; i++) {
            require(agentRegistry.isActiveAgent(selectedAgents[i]), "Agent not active");
            // Additional capability verification could be added here
        }
        
        // Update task status to assigned (first agent becomes primary assignee)
        task.status = TaskStatus.Assigned;
        task.assignedAgent = selectedAgents[0]; // Primary agent
        task.assignedAt = block.timestamp;
        
        // Emit collaboration event
        emit AgentCollaborationStarted(
            taskId,
            msg.sender,
            selectedAgents,
            collaborationId,
            block.timestamp
        );
        
        // Emit standard assignment events
        emit TaskAssigned(taskId, selectedAgents[0], block.timestamp);
        emit TaskStatusUpdated(taskId, TaskStatus.Assigned, selectedAgents[0], block.timestamp);
    }
    
    /**
     * @dev Update task information (only creator)
     * @param taskId ID of the task to update
     * @param newTitle New title (empty string to keep current)
     * @param newDescription New description (empty string to keep current)
     * @param newDeadline New deadline (0 to keep current)
     * @param newReward New reward amount (0 to keep current)
     */
    function updateTask(
        bytes32 taskId,
        string memory newTitle,
        string memory newDescription,
        uint256 newDeadline,
        uint256 newReward
    ) external {
        Task storage task = tasks[taskId];
        
        require(task.creator == msg.sender, "Only creator can update task");
        require(task.status == TaskStatus.Open || task.status == TaskStatus.Created, "Task cannot be updated in current state");
        
        // Update title if provided
        if (bytes(newTitle).length > 0 && keccak256(bytes(task.title)) != keccak256(bytes(newTitle))) {
            string memory oldTitle = task.title;
            task.title = newTitle;
            emit TaskUpdated(taskId, msg.sender, "title", oldTitle, newTitle, block.timestamp);
        }
        
        // Update description if provided
        if (bytes(newDescription).length > 0 && keccak256(bytes(task.description)) != keccak256(bytes(newDescription))) {
            string memory oldDescription = task.description;
            task.description = newDescription;
            emit TaskUpdated(taskId, msg.sender, "description", oldDescription, newDescription, block.timestamp);
        }
        
        // Update deadline if provided and valid
        if (newDeadline > 0 && newDeadline != task.deadline) {
            require(newDeadline > block.timestamp, "New deadline must be in the future");
            string memory oldDeadline = uint2str(task.deadline);
            string memory newDeadlineStr = uint2str(newDeadline);
            task.deadline = newDeadline;
            emit TaskUpdated(taskId, msg.sender, "deadline", oldDeadline, newDeadlineStr, block.timestamp);
        }
        
        // Update reward if provided
        if (newReward > 0 && newReward != task.reward) {
            string memory oldReward = uint2str(task.reward);
            string memory newRewardStr = uint2str(newReward);
            task.reward = newReward;
            emit TaskUpdated(taskId, msg.sender, "reward", oldReward, newRewardStr, block.timestamp);
        }
    }
    
    /**
     * @dev Convert uint to string (helper function)
     */
    function uint2str(uint256 _i) internal pure returns (string memory str) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 length;
        while (j != 0) {
            length++;
            j /= 10;
        }
        bytes memory bstr = new bytes(length);
        uint256 k = length;
        j = _i;
        while (j != 0) {
            bstr[--k] = bytes1(uint8(48 + j % 10));
            j /= 10;
        }
        str = string(bstr);
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
        
        // Emit events
        emit TaskCancelled(taskId, msg.sender, "Task cancelled by creator", block.timestamp);
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
    
    /**
     * @dev Get total number of tasks
     * @return Total task count
     */
    function getTaskCount() external view returns (uint256) {
        return taskIds.length;
    }
    
    /**
     * @dev Get basic task info
     * @param taskId ID of the task
     * @return creator Task creator address
     * @return title Task title
     * @return description Task description
     * @return reward Task reward
     * @return deadline Task deadline
     * @return status Task status
     */
    function getTaskBasicInfo(bytes32 taskId) external view returns (
        address creator,
        string memory title,
        string memory description,
        uint256 reward,
        uint256 deadline,
        TaskStatus status
    ) {
        Task storage task = tasks[taskId];
        return (
            task.creator,
            task.title,
            task.description,
            task.reward,
            task.deadline,
            task.status
        );
    }
    
    /**
     * @dev Get task execution info
     * @param taskId ID of the task
     * @return capabilities Required capabilities
     * @return minReputation Minimum reputation required
     * @return assignedAgent Assigned agent address
     * @return createdAt Creation timestamp
     * @return completedAt Completion timestamp
     * @return result Task result
     */
    function getTaskExecutionDetails(bytes32 taskId) external view returns (
        string[] memory capabilities,
        uint256 minReputation,
        address assignedAgent,
        uint256 createdAt,
        uint256 completedAt,
        string memory result
    ) {
        Task storage task = tasks[taskId];
        return (
            task.capabilities,
            task.minReputation,
            task.assignedAgent,
            task.createdAt,
            task.completedAt,
            task.result
        );
    }
    
    /**
     * @dev Start collaboration conversation for a task
     * @param taskId ID of the task
     * @param conversationId Unique conversation identifier
     * @param participants Array of participant addresses
     * @param conversationTopic Topic of the conversation
     */
    function startCollaborationConversation(
        bytes32 taskId,
        string memory conversationId,
        address[] memory participants,
        string memory conversationTopic
    ) external {
        Task storage task = tasks[taskId];
        
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(participants.length > 0, "At least one participant required");
        require(bytes(conversationId).length > 0, "Conversation ID required");
        
        // Emit collaboration conversation started event
        emit CollaborationConversationStarted(
            taskId,
            conversationId,
            participants,
            conversationTopic,
            block.timestamp
        );
    }
    
    /**
     * @dev Record a collaboration message
     * @param taskId ID of the task
     * @param conversationId Unique conversation identifier
     * @param sender Address of the message sender
     * @param message The message content
     * @param messageIndex Index of the message in the conversation
     */
    function recordCollaborationMessage(
        bytes32 taskId,
        string memory conversationId,
        address sender,
        string memory message,
        uint256 messageIndex
    ) external {
        Task storage task = tasks[taskId];
        
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(bytes(conversationId).length > 0, "Conversation ID required");
        require(bytes(message).length > 0, "Message cannot be empty");
        
        // Emit collaboration message event
        emit CollaborationMessage(
            taskId,
            conversationId,
            sender,
            message,
            messageIndex,
            block.timestamp
        );
    }
    
    /**
     * @dev Record collaboration result
     * @param taskId ID of the task
     * @param conversationId Unique conversation identifier
     * @param participants Array of participant addresses
     * @param result The final result of the collaboration
     * @param conversationSummary Summary of the conversation
     */
    function recordCollaborationResult(
        bytes32 taskId,
        string memory conversationId,
        address[] memory participants,
        string memory result,
        string memory conversationSummary
    ) external {
        Task storage task = tasks[taskId];
        
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(bytes(conversationId).length > 0, "Conversation ID required");
        require(bytes(result).length > 0, "Result cannot be empty");
        
        // Update task result
        task.result = result;
        
        // Emit collaboration result event
        emit CollaborationResult(
            taskId,
            conversationId,
            participants,
            result,
            conversationSummary,
            block.timestamp
        );
    }
}