// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./TaskManager.sol";
import "./BidAuction.sol";
import "./AgentRegistry.sol";
import "./IncentiveEngine.sol";

/**
 * @title TaskMarketplace
 * @dev Contract that provides a marketplace interface for task creation, bidding, and management
 */
contract TaskMarketplace is Ownable {
    // Contract references
    TaskManager public taskManager;
    BidAuction public bidAuction;
    AgentRegistry public agentRegistry;
    IncentiveEngine public incentiveEngine;
    
    // Events
    event TaskCreated(uint256 indexed taskId, address indexed creator);
    
    /**
     * @dev Constructor
     * @param _taskManagerAddress Address of the TaskManager contract
     * @param _bidAuctionAddress Address of the BidAuction contract
     * @param _agentRegistryAddress Address of the AgentRegistry contract
     * @param _incentiveEngineAddress Address of the IncentiveEngine contract
     */
    constructor(
        address _taskManagerAddress,
        address _bidAuctionAddress,
        address _agentRegistryAddress,
        address _incentiveEngineAddress
    ) Ownable(msg.sender) {
        taskManager = TaskManager(_taskManagerAddress);
        bidAuction = BidAuction(_bidAuctionAddress);
        agentRegistry = AgentRegistry(_agentRegistryAddress);
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
     */
    function createTask(
        string memory title,
        string memory description,
        string[] memory capabilities,
        uint256 minReputation,
        uint256 reward,
        uint256 deadline
    ) external returns (uint256) {
        bytes32 taskId = taskManager.createTask(
            title,
            description,
            capabilities,
            minReputation,
            reward,
            deadline
        );
        
        emit TaskCreated(uint256(taskId), msg.sender);
        return uint256(taskId);
    }
    
    /**
     * @dev Place a bid on a task
     * @param taskId ID of the task
     * @param utilityScore Self-reported utility score (0-100)
     * @param bidAmount Amount of tokens bid
     * @param signature Signature of the bid
     * @param nonce One-time use nonce to prevent replay attacks
     */
    function placeBid(
        uint256 taskId,
        uint256 utilityScore,
        uint256 bidAmount,
        bytes memory signature,
        uint256 nonce
    ) external {
        bytes32 taskIdBytes = bytes32(taskId);
        
        bidAuction.placeBidWithSignature(
            taskIdBytes,
            utilityScore,
            bidAmount,
            signature,
            nonce
        );
    }
    
    /**
     * @dev Place a simplified bid on a task (for testing)
     * @param taskId ID of the task
     * @param bidAmount Amount of tokens bid
     */
    function placeBidSimple(
        uint256 taskId,
        uint256 bidAmount
    ) external {
        bytes32 taskIdBytes = bytes32(taskId);
        
        bidAuction.placeBid(
            taskIdBytes,
            bidAmount
        );
    }
    
    /**
     * @dev Submit results for a task
     * @param taskId ID of the task
     * @param resultURI URI of the task results
     */
    function submitTaskResults(uint256 taskId, string memory resultURI) external {
        bytes32 taskIdBytes = bytes32(taskId);
        taskManager.completeTask(taskIdBytes, resultURI);
    }
    
    /**
     * @dev Complete a task
     * @param taskId ID of the task
     * @param resultURI URI of the task results
     */
    function completeTask(uint256 taskId, string memory resultURI) external {
        bytes32 taskIdBytes = bytes32(taskId);
        taskManager.completeTask(taskIdBytes, resultURI);
    }
    
    /**
     * @dev Cancel a task
     * @param taskId ID of the task
     */
    function cancelTask(uint256 taskId) external {
        bytes32 taskIdBytes = bytes32(taskId);
        taskManager.cancelTask(taskIdBytes);
    }
    
    /**
     * @dev Get all open tasks
     * @return Array of task IDs
     */
    function getOpenTasks() external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getTasksByStatus(TaskManager.TaskStatus.Open);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get all assigned tasks
     * @return Array of task IDs
     */
    function getAssignedTasks() external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getTasksByStatus(TaskManager.TaskStatus.Assigned);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get all submitted tasks
     * @return Array of task IDs
     */
    function getSubmittedTasks() external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getTasksByStatus(TaskManager.TaskStatus.InProgress);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get all completed tasks
     * @return Array of task IDs
     */
    function getCompletedTasks() external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getTasksByStatus(TaskManager.TaskStatus.Completed);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get all cancelled tasks
     * @return Array of task IDs
     */
    function getCancelledTasks() external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getTasksByStatus(TaskManager.TaskStatus.Cancelled);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Convert bytes32 array to uint256 array
     * @param bytesArray Array of bytes32 values
     * @return Array of uint256 values
     */
    function convertToUint256Array(bytes32[] memory bytesArray) internal pure returns (uint256[] memory) {
        uint256[] memory result = new uint256[](bytesArray.length);
        for (uint256 i = 0; i < bytesArray.length; i++) {
            result[i] = uint256(bytesArray[i]);
        }
        return result;
    }
    
    /**
     * @dev Get tasks by creator
     * @param creator Address of the creator
     * @return Array of task IDs
     */
    function getTasksByCreator(address creator) external view returns (uint256[] memory) {
        // Get all tasks
        bytes32[] memory allTaskIds = taskManager.getAllTasks();
        
        // Count tasks by creator
        uint256 count = 0;
        for (uint256 i = 0; i < allTaskIds.length; i++) {
            if (taskManager.getTaskCreator(allTaskIds[i]) == creator) {
                count++;
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allTaskIds.length; i++) {
            if (taskManager.getTaskCreator(allTaskIds[i]) == creator) {
                result[resultIndex] = uint256(allTaskIds[i]);
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get tasks by status
     * @param status Status code (1=Open, 2=Assigned, 3=InProgress, 4=Completed, 5=Cancelled)
     * @return Array of task IDs
     */
    function getTasksByStatus(uint8 status) external view returns (uint256[] memory) {
        TaskManager.TaskStatus taskStatus;
        
        if (status == 1) {
            taskStatus = TaskManager.TaskStatus.Open;
        } else if (status == 2) {
            taskStatus = TaskManager.TaskStatus.Assigned;
        } else if (status == 3) {
            taskStatus = TaskManager.TaskStatus.InProgress;
        } else if (status == 4) {
            taskStatus = TaskManager.TaskStatus.Completed;
        } else if (status == 5) {
            taskStatus = TaskManager.TaskStatus.Cancelled;
        } else {
            revert("Invalid status code");
        }
        
        bytes32[] memory taskIds = taskManager.getTasksByStatus(taskStatus);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get tasks by capability
     * @param capability Required capability
     * @return Array of task IDs
     */
    function getTasksByCapability(string memory capability) external view returns (uint256[] memory) {
        bytes32[] memory allOpenTasks = taskManager.getTasksByStatus(TaskManager.TaskStatus.Open);
        uint256 count = 0;
        
        // Count tasks with the required capability
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            (
                ,
                ,
                string[] memory capabilities,
                ,
                ,
            ) = taskManager.getTaskExecutionInfo(taskIdBytes);
            
            for (uint256 j = 0; j < capabilities.length; j++) {
                if (keccak256(bytes(capabilities[j])) == keccak256(bytes(capability))) {
                    count++;
                    break;
                }
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            (
                ,
                ,
                string[] memory capabilities,
                ,
                ,
            ) = taskManager.getTaskExecutionInfo(taskIdBytes);
            
            for (uint256 j = 0; j < capabilities.length; j++) {
                if (keccak256(bytes(capabilities[j])) == keccak256(bytes(capability))) {
                    result[resultIndex] = uint256(taskIdBytes);
                    resultIndex++;
                    break;
                }
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get tasks by minimum reputation
     * @param minReputation Minimum reputation required
     * @return Array of task IDs
     */
    function getTasksByMinReputation(uint256 minReputation) external view returns (uint256[] memory) {
        bytes32[] memory allOpenTasks = taskManager.getTasksByStatus(TaskManager.TaskStatus.Open);
        uint256 count = 0;
        
        // Count tasks with the required minimum reputation
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            uint256 taskMinRep = taskManager.getTaskMinReputation(taskIdBytes);
            if (taskMinRep <= minReputation) {
                count++;
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            uint256 taskMinRep = taskManager.getTaskMinReputation(taskIdBytes);
            if (taskMinRep <= minReputation) {
                result[resultIndex] = uint256(taskIdBytes);
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get tasks with open bidding
     * @return Array of task IDs
     */
    function getTasksWithOpenBidding() external view returns (uint256[] memory) {
        bytes32[] memory allOpenTasks = taskManager.getTasksByStatus(TaskManager.TaskStatus.Open);
        uint256 count = 0;
        
        // Count tasks with open bidding
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            bool isOpen = bidAuction.isBiddingOpen(taskIdBytes);
            if (isOpen) {
                count++;
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allOpenTasks.length; i++) {
            bytes32 taskIdBytes = allOpenTasks[i];
            bool isOpen = bidAuction.isBiddingOpen(taskIdBytes);
            if (isOpen) {
                result[resultIndex] = uint256(taskIdBytes);
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get bids for a task
     * @param taskId ID of the task
     * @return agents Array of bidding agent addresses
     * @return utilityScores Array of utility scores
     * @return bidAmounts Array of bid amounts
     * @return timestamps Array of bid timestamps
     */
    function getTaskBids(uint256 taskId) external view returns (
        address[] memory agents,
        uint256[] memory utilityScores,
        uint256[] memory bidAmounts,
        uint256[] memory timestamps
    ) {
        bytes32 taskIdBytes = bytes32(taskId);
        return bidAuction.getTaskBids(taskIdBytes);
    }
    
    /**
     * @dev Get tasks assigned to an agent
     * @param agent Address of the agent
     * @return Array of task IDs
     */
    function getAgentTasks(address agent) external view returns (uint256[] memory) {
        bytes32[] memory taskIds = taskManager.getAgentTasks(agent);
        return convertToUint256Array(taskIds);
    }
    
    /**
     * @dev Get detailed task information
     * @param taskId ID of the task
     * @return _taskId Task ID
     * @return description Task description
     * @return creator Task creator address
     * @return status Task status
     * @return capabilities Required capabilities
     * @return reward Task reward
     * @return minReputation Minimum reputation required
     * @return deadline Task deadline
     */
    function getTaskDetails(uint256 taskId) external view returns (
        uint256 _taskId,
        string memory description,
        address creator,
        uint8 status,
        string[] memory capabilities,
        uint256 reward,
        uint256 minReputation,
        uint256 deadline
    ) {
        bytes32 taskIdBytes = bytes32(taskId);
        
        // Get task information using getter functions
        creator = taskManager.getTaskCreator(taskIdBytes);
        minReputation = taskManager.getTaskMinReputation(taskIdBytes);
        TaskManager.TaskStatus taskStatus = taskManager.getTaskStatus(taskIdBytes);
        status = uint8(taskStatus);
        
        // Get execution info
        address agent;
        uint256 assignedAt;
        uint256 completedAt;
        (
            agent,
            reward,
            capabilities,
            deadline,
            assignedAt,
            completedAt
        ) = taskManager.getTaskExecutionInfo(taskIdBytes);
        
        // For description, use task ID as a placeholder since we don't have a getter for it
        description = string(abi.encodePacked("Task ", bytes32ToString(taskIdBytes)));
        
        return (
            taskId,
            description,
            creator,
            status,
            capabilities,
            reward,
            minReputation,
            deadline
        );
    }
    
    /**
     * @dev Convert bytes32 to string
     * @param _bytes32 The bytes32 value to convert
     * @return string representation
     */
    function bytes32ToString(bytes32 _bytes32) internal pure returns (string memory) {
        bytes memory bytesArray = new bytes(32);
        for (uint256 i = 0; i < 32; i++) {
            bytesArray[i] = _bytes32[i];
        }
        return string(bytesArray);
    }
    
    /**
     * @dev Get agents by capability
     * @param capability Required capability
     * @return Array of agent addresses
     */
    function getAgentsByCapability(string memory capability) external view returns (address[] memory) {
        address[] memory allAgents = agentRegistry.getAllAgents();
        uint256 count = 0;
        
        // Count agents with the required capability
        for (uint256 i = 0; i < allAgents.length; i++) {
            (string[] memory tags, ) = agentRegistry.getCapabilities(allAgents[i]);
            for (uint256 j = 0; j < tags.length; j++) {
                if (keccak256(bytes(tags[j])) == keccak256(bytes(capability))) {
                    count++;
                    break;
                }
            }
        }
        
        // Create result array
        address[] memory result = new address[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allAgents.length; i++) {
            (string[] memory tags, ) = agentRegistry.getCapabilities(allAgents[i]);
            for (uint256 j = 0; j < tags.length; j++) {
                if (keccak256(bytes(tags[j])) == keccak256(bytes(capability))) {
                    result[resultIndex] = allAgents[i];
                    resultIndex++;
                    break;
                }
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get agents by minimum reputation
     * @param minReputation Minimum reputation required
     * @return Array of agent addresses
     */
    function getAgentsByMinReputation(uint256 minReputation) external view returns (address[] memory) {
        address[] memory allAgents = agentRegistry.getAllAgents();
        uint256 count = 0;
        
        // Count agents with the required minimum reputation
        for (uint256 i = 0; i < allAgents.length; i++) {
            uint256 agentRep = incentiveEngine.getAgentReputation(allAgents[i]);
            if (agentRep >= minReputation) {
                count++;
            }
        }
        
        // Create result array
        address[] memory result = new address[](count);
        uint256 resultIndex = 0;
        
        // Fill result array
        for (uint256 i = 0; i < allAgents.length; i++) {
            uint256 agentRep = incentiveEngine.getAgentReputation(allAgents[i]);
            if (agentRep >= minReputation) {
                result[resultIndex] = allAgents[i];
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get agent details
     * @param agent Address of the agent
     * @return name Agent name
     * @return reputation Agent reputation
     * @return active Whether agent is active
     * @return workload Agent workload
     * @return capabilities Array of agent capabilities
     * @return weights Array of capability weights
     */
    function getAgentDetails(address agent) external view returns (
        string memory name,
        uint256 reputation,
        bool active,
        uint256 workload,
        string[] memory capabilities,
        uint256[] memory weights
    ) {
        // Get agent information
        reputation = incentiveEngine.getAgentReputation(agent);
        workload = incentiveEngine.getAgentWorkload(agent);
        active = agentRegistry.isActiveAgent(agent);
        name = "Agent"; // Default name since we don't have a getter for it
        
        // Get capabilities
        (capabilities, weights) = agentRegistry.getCapabilities(agent);
        
        return (name, reputation, active, workload, capabilities, weights);
    }
    
    /**
     * @dev Get agent capabilities
     * @param agent Address of the agent
     * @return Array of capability tags
     */
    function getAgentCapabilities(address agent) external view returns (string[] memory) {
        (string[] memory tags, ) = agentRegistry.getCapabilities(agent);
        return tags;
    }
} 