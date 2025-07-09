// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AgentRegistry.sol";

/**
 * @title Learning
 * @dev Contract for recording and managing agent learning events
 */
contract Learning {
    struct LearningEvent {
        address agentAddress;
        string eventType;
        string data; // JSON string with event details
        uint256 timestamp;
    }
    
    // Mapping from event ID to event details
    mapping(uint256 => LearningEvent) public events;
    
    // List of all event IDs
    uint256[] public eventIds;
    
    // Counter for generating event IDs
    uint256 private eventIdCounter;
    
    // Reference to the AgentRegistry contract
    AgentRegistry private agentRegistry;
    
    // Events
    event LearningEventRecorded(uint256 indexed eventId, address indexed agentAddress, string eventType, uint256 timestamp);
    
    event SkillImprovement(
        address indexed agentAddress,
        string indexed skillTag,
        uint256 oldScore,
        uint256 newScore,
        uint256 timestamp
    );
    
    event TaskCompletion(
        address indexed agentAddress,
        bytes32 indexed taskId,
        uint256 qualityScore,
        uint256 timeSpent,
        uint256 timestamp
    );
    
    event CollaborationEvent(
        address indexed agent1,
        address indexed agent2,
        bytes32 indexed collaborationId,
        string eventType,
        uint256 timestamp
    );
    
    event LearningMilestone(
        address indexed agentAddress,
        string milestoneType,
        uint256 value,
        uint256 timestamp
    );
    
    /**
     * @dev Constructor
     * @param _agentRegistryAddress Address of the AgentRegistry contract
     */
    constructor(address _agentRegistryAddress) {
        agentRegistry = AgentRegistry(_agentRegistryAddress);
        eventIdCounter = 1;
    }
    
    /**
     * @dev Record a new learning event
     * @param agentAddress Address of the agent
     * @param eventType Type of learning event
     * @param data JSON string with event details
     * @return Event ID
     */
    function recordEvent(
        address agentAddress,
        string memory eventType,
        string memory data
    ) public returns (uint256) {
        uint256 eventId = eventIdCounter++;
        
        LearningEvent storage newEvent = events[eventId];
        newEvent.agentAddress = agentAddress;
        newEvent.eventType = eventType;
        newEvent.data = data;
        newEvent.timestamp = block.timestamp;
        
        eventIds.push(eventId);
        
        emit LearningEventRecorded(eventId, agentAddress, eventType, block.timestamp);
        
        return eventId;
    }
    
    /**
     * @dev Get details of a specific event
     * @param eventId ID of the event
     * @return Event details
     */
    function getEventDetails(uint256 eventId) public view returns (LearningEvent memory) {
        return events[eventId];
    }
    
    /**
     * @dev Get events by agent
     * @param agentAddress Address of the agent
     * @return List of event IDs
     */
    function getAgentEvents(address agentAddress) public view returns (uint256[] memory) {
        uint256 count = 0;
        
        // Count events for the agent
        for (uint256 i = 0; i < eventIds.length; i++) {
            if (events[eventIds[i]].agentAddress == agentAddress) {
                count++;
            }
        }
        
        // Create array of the right size
        uint256[] memory agentEvents = new uint256[](count);
        
        // Fill the array
        uint256 index = 0;
        for (uint256 i = 0; i < eventIds.length; i++) {
            if (events[eventIds[i]].agentAddress == agentAddress) {
                agentEvents[index] = eventIds[i];
                index++;
            }
        }
        
        return agentEvents;
    }
    
    /**
     * @dev Get events by type
     * @param eventType Type of event
     * @return List of event IDs
     */
    function getEventsByType(string memory eventType) public view returns (uint256[] memory) {
        uint256 count = 0;
        
        // Count events of the given type
        for (uint256 i = 0; i < eventIds.length; i++) {
            if (keccak256(bytes(events[eventIds[i]].eventType)) == keccak256(bytes(eventType))) {
                count++;
            }
        }
        
        // Create array of the right size
        uint256[] memory filteredEvents = new uint256[](count);
        
        // Fill the array
        uint256 index = 0;
        for (uint256 i = 0; i < eventIds.length; i++) {
            if (keccak256(bytes(events[eventIds[i]].eventType)) == keccak256(bytes(eventType))) {
                filteredEvents[index] = eventIds[i];
                index++;
            }
        }
        
        return filteredEvents;
    }
    
    /**
     * @dev Get all events
     * @return List of event IDs
     */
    function getAllEvents() public view returns (uint256[] memory) {
        return eventIds;
    }
    
    /**
     * @dev Record skill improvement event
     * @param agentAddress Address of the agent
     * @param skillTag Skill tag that improved
     * @param oldScore Previous skill score
     * @param newScore New skill score
     */
    function recordSkillImprovement(
        address agentAddress,
        string memory skillTag,
        uint256 oldScore,
        uint256 newScore
    ) public {
        require(newScore > oldScore, "New score must be higher than old score");
        require(newScore <= 100, "Score must be between 0-100");
        
        // Record as general learning event
        string memory data = string(abi.encodePacked(
            '{"skillTag":"', skillTag, '","oldScore":', 
            _toString(oldScore), ',"newScore":', _toString(newScore), '}'
        ));
        
        recordEvent(agentAddress, "skill_improvement", data);
        
        // Emit specific event
        emit SkillImprovement(agentAddress, skillTag, oldScore, newScore, block.timestamp);
    }
    
    /**
     * @dev Record task completion event
     * @param agentAddress Address of the agent
     * @param taskId ID of the completed task
     * @param qualityScore Quality score of the task completion
     * @param timeSpent Time spent on the task (in seconds)
     */
    function recordTaskCompletion(
        address agentAddress,
        bytes32 taskId,
        uint256 qualityScore,
        uint256 timeSpent
    ) public {
        require(qualityScore <= 100, "Quality score must be between 0-100");
        
        // Record as general learning event
        string memory data = string(abi.encodePacked(
            '{"taskId":"', _bytes32ToString(taskId), '","qualityScore":', 
            _toString(qualityScore), ',"timeSpent":', _toString(timeSpent), '}'
        ));
        
        recordEvent(agentAddress, "task_completion", data);
        
        // Emit specific event
        emit TaskCompletion(agentAddress, taskId, qualityScore, timeSpent, block.timestamp);
    }
    
    /**
     * @dev Record collaboration event
     * @param agent1 Address of first agent
     * @param agent2 Address of second agent
     * @param collaborationId ID of the collaboration
     * @param eventType Type of collaboration event
     */
    function recordCollaboration(
        address agent1,
        address agent2,
        bytes32 collaborationId,
        string memory eventType
    ) public {
        // Record as general learning event for both agents
        string memory data = string(abi.encodePacked(
            '{"collaborationId":"', _bytes32ToString(collaborationId), 
            '","partner":"', _addressToString(agent2), 
            '","eventType":"', eventType, '"}'
        ));
        
        recordEvent(agent1, "collaboration", data);
        
        // Emit specific event
        emit CollaborationEvent(agent1, agent2, collaborationId, eventType, block.timestamp);
    }
    
    /**
     * @dev Record learning milestone
     * @param agentAddress Address of the agent
     * @param milestoneType Type of milestone (e.g., "tasks_completed", "reputation_threshold")
     * @param value Milestone value
     */
    function recordLearningMilestone(
        address agentAddress,
        string memory milestoneType,
        uint256 value
    ) public {
        // Record as general learning event
        string memory data = string(abi.encodePacked(
            '{"milestoneType":"', milestoneType, '","value":', _toString(value), '}'
        ));
        
        recordEvent(agentAddress, "milestone", data);
        
        // Emit specific event
        emit LearningMilestone(agentAddress, milestoneType, value, block.timestamp);
    }
    
    /**
     * @dev Get total number of learning events
     * @return Total event count
     */
    function getTotalEventCount() public view returns (uint256) {
        return eventIds.length;
    }
    
    // Helper functions
    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
    
    function _bytes32ToString(bytes32 _bytes32) internal pure returns (string memory) {
        uint8 i = 0;
        while(i < 32 && _bytes32[i] != 0) {
            i++;
        }
        bytes memory bytesArray = new bytes(i);
        for (i = 0; i < 32 && _bytes32[i] != 0; i++) {
            bytesArray[i] = _bytes32[i];
        }
        return string(bytesArray);
    }
    
    function _addressToString(address _addr) internal pure returns (string memory) {
        bytes32 value = bytes32(uint256(uint160(_addr)));
        bytes memory alphabet = "0123456789abcdef";
        
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2+i*2] = alphabet[uint8(value[i + 12] >> 4)];
            str[3+i*2] = alphabet[uint8(value[i + 12] & 0x0f)];
        }
        return string(str);
    }
}