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
}