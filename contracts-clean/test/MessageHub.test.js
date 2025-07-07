const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MessageHub Contract Tests", function () {
  // Test accounts
  let owner, agent1, agent2, nonAgent;
  
  // Contract instances
  let agentRegistry;
  let messageHub;
  
  // Test data
  const messageURI = "ipfs://QmMessageContent123456";
  const messageHash = ethers.id("test-message-content");
  const conversationId = ethers.id("test-conversation");
  let testMessageHash;
  
  before(async function () {
    // Get signers
    [owner, agent1, agent2, nonAgent] = await ethers.getSigners();
    
    // Deploy AgentRegistry
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();
    
    // Register agents
    await agentRegistry.registerAgent(
      agent1.address,
      "Agent 1",
      "ipfs://agent1",
      "https://agent1.example.com",
      1 // LLM agent
    );
    
    await agentRegistry.registerAgent(
      agent2.address,
      "Agent 2",
      "ipfs://agent2",
      "https://agent2.example.com",
      1 // LLM agent
    );
    
    // Deploy MessageHub
    const MessageHub = await ethers.getContractFactory("MessageHub");
    messageHub = await MessageHub.deploy(agentRegistry.target);
    await messageHub.waitForDeployment();
    
    console.log("Contracts deployed and configured for testing");
  });
  
  describe("Message Sending", function () {
    it("Should allow registered agents to send messages", async function () {
      const nonce = 1;
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [messageHash, agent2.address, nonce]
      );
      const signature = await agent1.signMessage(ethers.getBytes(signedHash));
      
      // Send message
      await messageHub.connect(agent1).sendMessage(
        agent2.address,
        messageURI,
        messageHash,
        conversationId,
        previousMessageHash,
        signature,
        nonce
      );
      
      // Verify message was stored
      const message = await messageHub.messages(messageHash);
      expect(message.sender).to.equal(agent1.address);
      expect(message.recipient).to.equal(agent2.address);
      expect(message.messageURI).to.equal(messageURI);
      expect(message.previousMessageHash).to.equal(previousMessageHash);
      expect(message.verified).to.be.false;
    });
    
    it("Should emit MessageSent event when sending a message", async function () {
      const nonce = 20; // New nonce
      const newMessageHash = ethers.id("event-test-message");
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [newMessageHash, agent2.address, nonce]
      );
      const signature = await agent1.signMessage(ethers.getBytes(signedHash));
      
      // Send message and check for event
      const tx = await messageHub.connect(agent1).sendMessage(
        agent2.address,
        messageURI,
        newMessageHash,
        conversationId,
        previousMessageHash,
        signature,
        nonce
      );
      
      // Wait for transaction to be mined
      const receipt = await tx.wait();
      
      // Check for event
      const event = receipt.logs.find(
        log => log.fragment && log.fragment.name === 'MessageSent'
      );
      
      expect(event).to.not.be.undefined;
      expect(event.args[0]).to.equal(newMessageHash); // messageHash
      expect(event.args[1]).to.equal(agent1.address); // sender
      expect(event.args[2]).to.equal(agent2.address); // recipient
      expect(event.args[3]).to.equal(messageURI); // messageURI
      // Skip timestamp check as it's dynamic
      expect(event.args[5]).to.equal(conversationId); // conversationId
    });
    
    it("Should prevent non-registered agents from sending messages", async function () {
      const nonce = 2;
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [messageHash, agent2.address, nonce]
      );
      const signature = await nonAgent.signMessage(ethers.getBytes(signedHash));
      
      // Try to send message
      await expect(
        messageHub.connect(nonAgent).sendMessage(
          agent2.address,
          messageURI,
          messageHash,
          conversationId,
          previousMessageHash,
          signature,
          nonce
        )
      ).to.be.revertedWith("Sender is not a registered agent");
    });
    
    it("Should prevent reuse of nonces", async function () {
      const nonce = 1; // Already used
      const newMessageHash = ethers.id("another-message");
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [newMessageHash, agent2.address, nonce]
      );
      const signature = await agent1.signMessage(ethers.getBytes(signedHash));
      
      // Try to send message with used nonce
      await expect(
        messageHub.connect(agent1).sendMessage(
          agent2.address,
          messageURI,
          newMessageHash,
          conversationId,
          previousMessageHash,
          signature,
          nonce
        )
      ).to.be.revertedWith("Nonce already used");
    });
    
    it("Should verify signature correctly", async function () {
      const nonce = 3;
      const newMessageHash = ethers.id("another-message");
      const previousMessageHash = ethers.ZeroHash;
      
      // Create invalid signature (signed by different account)
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [newMessageHash, agent2.address, nonce]
      );
      const signature = await agent2.signMessage(ethers.getBytes(signedHash));
      
      // Try to send message with invalid signature
      await expect(
        messageHub.connect(agent1).sendMessage(
          agent2.address,
          messageURI,
          newMessageHash,
          conversationId,
          previousMessageHash,
          signature,
          nonce
        )
      ).to.be.revertedWith("Invalid signature");
    });
  });
  
  describe("Message Verification", function () {
    before(async function () {
      // Send a new message for verification tests
      const nonce = 4;
      testMessageHash = ethers.id("verification-test-message");
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [testMessageHash, agent2.address, nonce]
      );
      const signature = await agent1.signMessage(ethers.getBytes(signedHash));
      
      // Send message
      await messageHub.connect(agent1).sendMessage(
        agent2.address,
        messageURI,
        testMessageHash,
        conversationId,
        previousMessageHash,
        signature,
        nonce
      );
    });
    
    it("Should allow recipient to verify message", async function () {
      const nonce = 5;
      
      // Create verification signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "string", "uint256"],
        [testMessageHash, "VERIFIED", nonce]
      );
      const signature = await agent2.signMessage(ethers.getBytes(signedHash));
      
      // Verify message
      await messageHub.connect(agent2).verifyMessage(
        testMessageHash,
        signature,
        nonce
      );
      
      // Check message is verified
      expect(await messageHub.isMessageVerified(testMessageHash)).to.be.true;
    });
    
    it("Should emit MessageVerified event when verifying a message", async function () {
      // Create a new message for this test
      const nonce1 = 30;
      const verifyMessageHash = ethers.id("verify-event-test-message");
      const previousMessageHash = ethers.ZeroHash;
      
      // Create signature for sending
      const signedHash1 = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [verifyMessageHash, agent2.address, nonce1]
      );
      const signature1 = await agent1.signMessage(ethers.getBytes(signedHash1));
      
      // Send message
      await messageHub.connect(agent1).sendMessage(
        agent2.address,
        messageURI,
        verifyMessageHash,
        conversationId,
        previousMessageHash,
        signature1,
        nonce1
      );
      
      // Create verification signature
      const nonce2 = 31;
      const signedHash2 = ethers.solidityPackedKeccak256(
        ["bytes32", "string", "uint256"],
        [verifyMessageHash, "VERIFIED", nonce2]
      );
      const signature2 = await agent2.signMessage(ethers.getBytes(signedHash2));
      
      // Verify message
      const tx = await messageHub.connect(agent2).verifyMessage(
        verifyMessageHash,
        signature2,
        nonce2
      );
      
      // Wait for transaction to be mined
      const receipt = await tx.wait();
      
      // Check for event
      const event = receipt.logs.find(
        log => log.fragment && log.fragment.name === 'MessageVerified'
      );
      
      expect(event).to.not.be.undefined;
      expect(event.args[0]).to.equal(verifyMessageHash); // messageHash
      expect(event.args[1]).to.equal(agent2.address); // verifier
      // Skip timestamp check as it's dynamic
      
      // Double-check message is verified
      expect(await messageHub.isMessageVerified(verifyMessageHash)).to.be.true;
    });
    
    it("Should prevent non-recipients from verifying messages", async function () {
      const nonce = 6;
      
      // Create verification signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "string", "uint256"],
        [testMessageHash, "VERIFIED", nonce]
      );
      const signature = await agent1.signMessage(ethers.getBytes(signedHash));
      
      // Try to verify message as non-recipient
      await expect(
        messageHub.connect(agent1).verifyMessage(
          testMessageHash,
          signature,
          nonce
        )
      ).to.be.revertedWith("Only recipient can verify");
    });
    
    it("Should prevent verifying non-existent messages", async function () {
      const nonce = 7;
      const nonExistentHash = ethers.id("non-existent-message");
      
      // Create verification signature
      const signedHash = ethers.solidityPackedKeccak256(
        ["bytes32", "string", "uint256"],
        [nonExistentHash, "VERIFIED", nonce]
      );
      const signature = await agent2.signMessage(ethers.getBytes(signedHash));
      
      // Try to verify non-existent message
      await expect(
        messageHub.connect(agent2).verifyMessage(
          nonExistentHash,
          signature,
          nonce
        )
      ).to.be.revertedWith("Message does not exist");
    });
  });
  
  describe("Message Queries", function () {
    let messageHash1, messageHash2;
    
    before(async function () {
      // Send additional messages for query tests
      const nonce1 = 10;
      const nonce2 = 11;
      messageHash1 = ethers.id("query-test-message-1");
      messageHash2 = ethers.id("query-test-message-2");
      const conversationId2 = ethers.id("test-conversation-2");
      
      // Create signatures
      const signedHash1 = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [messageHash1, agent2.address, nonce1]
      );
      const signature1 = await agent1.signMessage(ethers.getBytes(signedHash1));
      
      const signedHash2 = ethers.solidityPackedKeccak256(
        ["bytes32", "address", "uint256"],
        [messageHash2, agent1.address, nonce2]
      );
      const signature2 = await agent2.signMessage(ethers.getBytes(signedHash2));
      
      // Send messages
      await messageHub.connect(agent1).sendMessage(
        agent2.address,
        "ipfs://message1",
        messageHash1,
        conversationId,
        ethers.ZeroHash,
        signature1,
        nonce1
      );
      
      await messageHub.connect(agent2).sendMessage(
        agent1.address,
        "ipfs://message2",
        messageHash2,
        conversationId2,
        ethers.ZeroHash,
        signature2,
        nonce2
      );
    });
    
    it("Should retrieve conversation messages", async function () {
      // Get messages for first conversation
      const messages = await messageHub.getConversationMessages(conversationId);
      
      // Should include our messages
      expect(messages).to.include(messageHash);
      expect(messages).to.include(messageHash1);
      expect(messages).to.not.include(messageHash2); // In different conversation
    });
    
    it("Should retrieve agent messages", async function () {
      // Get agent1's messages
      const agent1Messages = await messageHub.getAgentMessages(agent1.address);
      
      // Should include messages sent by agent1
      expect(agent1Messages).to.include(messageHash);
      expect(agent1Messages).to.include(messageHash1);
      expect(agent1Messages).to.not.include(messageHash2); // Sent by agent2
      
      // Get agent2's messages
      const agent2Messages = await messageHub.getAgentMessages(agent2.address);
      
      // Should include messages sent by agent2
      expect(agent2Messages).to.include(messageHash2);
      expect(agent2Messages).to.not.include(messageHash); // Sent by agent1
    });
    
    it("Should check if message is verified", async function () {
      // messageHash was verified in previous test
      expect(await messageHub.isMessageVerified(testMessageHash)).to.be.true;
      
      // These messages haven't been verified
      expect(await messageHub.isMessageVerified(messageHash1)).to.be.false;
      expect(await messageHub.isMessageVerified(messageHash2)).to.be.false;
    });
  });
  
  describe("Contract Management", function () {
    it("Should allow owner to transfer ownership", async function () {
      // Transfer ownership to agent1
      await messageHub.transferOwnership(agent1.address);
      
      // Verify new owner
      expect(await messageHub.owner()).to.equal(agent1.address);
      
      // Transfer back to original owner for other tests
      await messageHub.connect(agent1).transferOwnership(owner.address);
    });
  });
}); 