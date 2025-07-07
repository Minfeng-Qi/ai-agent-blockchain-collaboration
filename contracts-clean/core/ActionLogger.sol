// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "./AgentRegistry.sol";

/**
 * @title ActionLogger
 * @dev Contract to immutably log agent behaviors (accept, update, complete)
 */
contract ActionLogger is Ownable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Reference to AgentRegistry contract
    AgentRegistry public agentRegistry;
    
    // Action types
    enum ActionType { 
        TaskAccepted,
        TaskStarted,
        TaskUpdated,
        TaskCompleted,
        TaskFailed,
        MessageSent,
        MessageReceived,
        BidPlaced,
        BidWon,
        BidLost,
        ReputationUpdated,
        CapabilityUpdated
    }
    
    struct Action {
        bytes32 actionId;
        address agent;
        ActionType actionType;
        bytes32 resourceId;  // Task ID, message ID, etc.
        string metadataURI;  // IPFS URI for additional data
        uint256 timestamp;
        bytes signature;     // Signature of the action
    }
    
    // Maps action ID to Action struct
    mapping(bytes32 => Action) public actions;
    
    // Maps agent address to their action IDs
    mapping(address => bytes32[]) public agentActions;
    
    // Maps resource ID to related action IDs
    mapping(bytes32 => bytes32[]) public resourceActions;
    
    // Mapping of nonces used for signature verification (prevents replay attacks)
    mapping(address => mapping(uint256 => bool)) private usedNonces;
    
    // Events
    event ActionLogged(
        bytes32 indexed actionId,
        address indexed agent,
        ActionType indexed actionType,
        bytes32 resourceId,
        string metadataURI,
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
     * @dev Log an action performed by an agent
     * @param actionType Type of action performed
     * @param resourceId ID of the resource (task, message, etc.)
     * @param metadataURI IPFS URI for additional data
     * @param signature Signature of the action
     * @param nonce One-time use nonce to prevent replay attacks
     * @return Action ID
     */
    function logAction(
        ActionType actionType,
        bytes32 resourceId,
        string memory metadataURI,
        bytes memory signature,
        uint256 nonce
    ) external returns (bytes32) {
        // Verify agent is registered
        require(agentRegistry.isActiveAgent(msg.sender), "Not a registered active agent");
        
        // Verify nonce hasn't been used
        require(!usedNonces[msg.sender][nonce], "Nonce already used");
        usedNonces[msg.sender][nonce] = true;
        
        // Verify signature
        bytes32 signedHash = keccak256(abi.encodePacked(
            uint(actionType),
            resourceId,
            metadataURI,
            nonce
        )).toEthSignedMessageHash();
        
        address signer = signedHash.recover(signature);
        require(signer == msg.sender, "Invalid signature");
        
        // Generate action ID
        bytes32 actionId = keccak256(abi.encodePacked(
            msg.sender,
            uint(actionType),
            resourceId,
            block.timestamp,
            nonce
        ));
        
        // Store action
        actions[actionId] = Action({
            actionId: actionId,
            agent: msg.sender,
            actionType: actionType,
            resourceId: resourceId,
            metadataURI: metadataURI,
            timestamp: block.timestamp,
            signature: signature
        });
        
        // Add to agent's action history
        agentActions[msg.sender].push(actionId);
        
        // Add to resource's action history
        resourceActions[resourceId].push(actionId);
        
        // Emit event
        emit ActionLogged(
            actionId,
            msg.sender,
            actionType,
            resourceId,
            metadataURI,
            block.timestamp
        );
        
        return actionId;
    }
    
    /**
     * @dev Log an action on behalf of an agent (for system actions)
     * @param agent Address of the agent
     * @param actionType Type of action
     * @param resourceId ID of the resource
     * @param metadataURI IPFS URI for additional data
     * @return Action ID
     */
    function logSystemAction(
        address agent,
        ActionType actionType,
        bytes32 resourceId,
        string memory metadataURI
    ) external onlyOwner returns (bytes32) {
        // Generate action ID
        bytes32 actionId = keccak256(abi.encodePacked(
            agent,
            uint(actionType),
            resourceId,
            block.timestamp,
            "SYSTEM"
        ));
        
        // Store action
        actions[actionId] = Action({
            actionId: actionId,
            agent: agent,
            actionType: actionType,
            resourceId: resourceId,
            metadataURI: metadataURI,
            timestamp: block.timestamp,
            signature: bytes("") // No signature for system actions
        });
        
        // Add to agent's action history
        agentActions[agent].push(actionId);
        
        // Add to resource's action history
        resourceActions[resourceId].push(actionId);
        
        // Emit event
        emit ActionLogged(
            actionId,
            agent,
            actionType,
            resourceId,
            metadataURI,
            block.timestamp
        );
        
        return actionId;
    }
    
    /**
     * @dev Get all actions for an agent
     * @param agent Address of the agent
     * @return Array of action IDs
     */
    function getAgentActions(address agent) external view returns (bytes32[] memory) {
        return agentActions[agent];
    }
    
    /**
     * @dev Get all actions for a resource
     * @param resourceId ID of the resource
     * @return Array of action IDs
     */
    function getResourceActions(bytes32 resourceId) external view returns (bytes32[] memory) {
        return resourceActions[resourceId];
    }
    
    /**
     * @dev Get actions of a specific type for an agent
     * @param agent Address of the agent
     * @param actionType Type of action to filter by
     * @return Array of action IDs
     */
    function getAgentActionsByType(address agent, ActionType actionType) external view returns (bytes32[] memory) {
        // First, count actions of the specified type
        uint256 count = 0;
        for (uint256 i = 0; i < agentActions[agent].length; i++) {
            bytes32 actionId = agentActions[agent][i];
            if (actions[actionId].actionType == actionType) {
                count++;
            }
        }
        
        // Create array of the right size
        bytes32[] memory result = new bytes32[](count);
        
        // Fill the array
        uint256 index = 0;
        for (uint256 i = 0; i < agentActions[agent].length; i++) {
            bytes32 actionId = agentActions[agent][i];
            if (actions[actionId].actionType == actionType) {
                result[index] = actionId;
                index++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get actions of a specific type for a resource
     * @param resourceId ID of the resource
     * @param actionType Type of action to filter by
     * @return Array of action IDs
     */
    function getResourceActionsByType(bytes32 resourceId, ActionType actionType) external view returns (bytes32[] memory) {
        // First, count actions of the specified type
        uint256 count = 0;
        for (uint256 i = 0; i < resourceActions[resourceId].length; i++) {
            bytes32 actionId = resourceActions[resourceId][i];
            if (actions[actionId].actionType == actionType) {
                count++;
            }
        }
        
        // Create array of the right size
        bytes32[] memory result = new bytes32[](count);
        
        // Fill the array
        uint256 index = 0;
        for (uint256 i = 0; i < resourceActions[resourceId].length; i++) {
            bytes32 actionId = resourceActions[resourceId][i];
            if (actions[actionId].actionType == actionType) {
                result[index] = actionId;
                index++;
            }
        }
        
        return result;
    }
}