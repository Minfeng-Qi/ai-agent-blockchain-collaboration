// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "./AgentRegistry.sol";

/**
 * @title MessageHub
 * @dev Contract for verifiable message passing and on-chain audit logging
 */
contract MessageHub is Ownable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Reference to AgentRegistry contract
    AgentRegistry public agentRegistry;
    
    struct Message {
        address sender;
        address recipient;
        bytes32 messageHash;
        string messageURI;  // IPFS URI for message content
        uint256 timestamp;
        bytes32 previousMessageHash;  // For message chaining
        bool verified;
    }
    
    // Maps message hash to Message struct
    mapping(bytes32 => Message) public messages;
    
    // Maps agent address to their message hashes (for querying history)
    mapping(address => bytes32[]) public agentMessages;
    
    // Maps conversation ID to message hashes
    mapping(bytes32 => bytes32[]) public conversationMessages;
    
    // Mapping of nonces used for signature verification (prevents replay attacks)
    mapping(address => mapping(uint256 => bool)) private usedNonces;

    // Events
    event MessageSent(
        bytes32 indexed messageHash,
        address indexed sender,
        address indexed recipient,
        string messageURI,
        uint256 timestamp,
        bytes32 conversationId
    );
    
    event MessageVerified(
        bytes32 indexed messageHash,
        address indexed verifier,
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
     * @dev Send a message and log it on-chain
     * @param recipient Address of the recipient
     * @param messageURI IPFS URI of the message content
     * @param messageHash Hash of the message content
     * @param conversationId ID of the conversation this message belongs to
     * @param previousMessageHash Hash of the previous message in the conversation
     * @param signature Signature of the message hash
     * @param nonce One-time use nonce to prevent replay attacks
     */
    function sendMessage(
        address recipient,
        string memory messageURI,
        bytes32 messageHash,
        bytes32 conversationId,
        bytes32 previousMessageHash,
        bytes memory signature,
        uint256 nonce
    ) external {
        // Verify sender is a registered agent
        require(agentRegistry.isActiveAgent(msg.sender), "Sender is not a registered agent");
        
        // Verify nonce hasn't been used
        require(!usedNonces[msg.sender][nonce], "Nonce already used");
        usedNonces[msg.sender][nonce] = true;
        
        // Verify signature
        bytes32 signedHash = keccak256(abi.encodePacked(messageHash, recipient, nonce)).toEthSignedMessageHash();
        address signer = signedHash.recover(signature);
        require(signer == msg.sender, "Invalid signature");
        
        // Store message
        messages[messageHash] = Message({
            sender: msg.sender,
            recipient: recipient,
            messageHash: messageHash,
            messageURI: messageURI,
            timestamp: block.timestamp,
            previousMessageHash: previousMessageHash,
            verified: false
        });
        
        // Add to agent's message history
        agentMessages[msg.sender].push(messageHash);
        
        // Add to conversation history
        conversationMessages[conversationId].push(messageHash);
        
        // Emit event
        emit MessageSent(
            messageHash,
            msg.sender,
            recipient,
            messageURI,
            block.timestamp,
            conversationId
        );
    }
    
    /**
     * @dev Verify a message was received and processed
     * @param messageHash Hash of the message to verify
     * @param signature Signature proving receipt
     * @param nonce One-time use nonce
     */
    function verifyMessage(
        bytes32 messageHash,
        bytes memory signature,
        uint256 nonce
    ) external {
        // Ensure message exists
        require(messages[messageHash].timestamp > 0, "Message does not exist");
        
        // Ensure recipient is verifying
        require(messages[messageHash].recipient == msg.sender, "Only recipient can verify");
        
        // Verify nonce hasn't been used
        require(!usedNonces[msg.sender][nonce], "Nonce already used");
        usedNonces[msg.sender][nonce] = true;
        
        // Verify signature
        bytes32 signedHash = keccak256(abi.encodePacked(messageHash, "VERIFIED", nonce)).toEthSignedMessageHash();
        address signer = signedHash.recover(signature);
        require(signer == msg.sender, "Invalid signature");
        
        // Mark message as verified
        messages[messageHash].verified = true;
        
        // Emit event
        emit MessageVerified(
            messageHash,
            msg.sender,
            block.timestamp
        );
    }
    
    /**
     * @dev Get all message hashes in a conversation
     * @param conversationId ID of the conversation
     * @return Array of message hashes
     */
    function getConversationMessages(bytes32 conversationId) external view returns (bytes32[] memory) {
        return conversationMessages[conversationId];
    }
    
    /**
     * @dev Get all message hashes for an agent
     * @param agentAddress Address of the agent
     * @return Array of message hashes
     */
    function getAgentMessages(address agentAddress) external view returns (bytes32[] memory) {
        return agentMessages[agentAddress];
    }
    
    /**
     * @dev Check if a message has been verified
     * @param messageHash Hash of the message to check
     * @return True if message has been verified
     */
    function isMessageVerified(bytes32 messageHash) external view returns (bool) {
        return messages[messageHash].verified;
    }
}