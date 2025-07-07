const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Comprehensive Agent Learning System Tests", function () {
  this.timeout(120000);
  
  let owner, agent1, agent2, agent3, user1, user2;
  let agentRegistry, actionLogger, incentiveEngine, taskManager, bidAuction, messageHub;
  
  before(async function () {
    console.log("🚀 Starting comprehensive test suite for Agent Learning System");
    
    [owner, agent1, agent2, agent3, user1, user2] = await ethers.getSigners();
    
    console.log("📝 Deploying contracts...");
    
    // Deploy AgentRegistry
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();
    console.log("✅ AgentRegistry deployed at:", agentRegistry.target);
    
    // Deploy ActionLogger
    const ActionLogger = await ethers.getContractFactory("ActionLogger");
    actionLogger = await ActionLogger.deploy(agentRegistry.target);
    await actionLogger.waitForDeployment();
    console.log("✅ ActionLogger deployed at:", actionLogger.target);
    
    // Deploy IncentiveEngine
    const IncentiveEngine = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngine.deploy(agentRegistry.target);
    await incentiveEngine.waitForDeployment();
    console.log("✅ IncentiveEngine deployed at:", incentiveEngine.target);
    
    // Deploy TaskManager
    const TaskManager = await ethers.getContractFactory("TaskManager");
    taskManager = await TaskManager.deploy(agentRegistry.target);
    await taskManager.waitForDeployment();
    console.log("✅ TaskManager deployed at:", taskManager.target);
    
    // Deploy BidAuction
    const BidAuction = await ethers.getContractFactory("BidAuction");
    bidAuction = await BidAuction.deploy(agentRegistry.target, taskManager.target);
    await bidAuction.waitForDeployment();
    console.log("✅ BidAuction deployed at:", bidAuction.target);
    
    // Deploy MessageHub
    const MessageHub = await ethers.getContractFactory("MessageHub");
    messageHub = await MessageHub.deploy(agentRegistry.target);
    await messageHub.waitForDeployment();
    console.log("✅ MessageHub deployed at:", messageHub.target);
    
    // Set contract connections
    await taskManager.setBidAuction(bidAuction.target);
    await taskManager.setIncentiveEngine(incentiveEngine.target);
    await incentiveEngine.setActionLogger(actionLogger.target);
    await bidAuction.setIncentiveEngine(incentiveEngine.target);
    
    console.log("🔗 All contracts deployed and connected");
  });
  
  describe("1. Agent Registration Tests", function () {
    it("Should register agents successfully", async function () {
      console.log("👤 Testing agent registration...");
      
      // Register three agents with different types
      await agentRegistry.connect(agent1).registerAgent(
        "AI Agent 1",
        "ipfs://agent1-metadata",
        1 // LLM type
      );
      
      await agentRegistry.connect(agent2).registerAgent(
        "AI Agent 2", 
        "ipfs://agent2-metadata",
        2 // Orchestrator type
      );
      
      await agentRegistry.connect(agent3).registerAgent(
        "AI Agent 3",
        "ipfs://agent3-metadata", 
        3 // Evaluator type
      );
      
      // Verify agents are registered
      expect(await agentRegistry.isActiveAgent(agent1.address)).to.be.true;
      expect(await agentRegistry.isActiveAgent(agent2.address)).to.be.true;
      expect(await agentRegistry.isActiveAgent(agent3.address)).to.be.true;
      
      // Check agent count
      expect(await agentRegistry.getAgentCount()).to.equal(3);
      
      console.log("✅ Agent registration successful");
    });
    
    it("Should set agent capabilities", async function () {
      console.log("🎯 Testing capability management...");
      
      // Set capabilities for agents
      await agentRegistry.setCapabilities(
        agent1.address,
        ["coding", "analysis", "research"],
        [80, 70, 60]
      );
      
      await agentRegistry.setCapabilities(
        agent2.address,
        ["coordination", "planning", "communication"],
        [90, 85, 75]
      );
      
      await agentRegistry.setCapabilities(
        agent3.address,
        ["evaluation", "quality-check", "reporting"],
        [95, 90, 85]
      );
      
      // Verify capabilities
      const [tags1, weights1] = await agentRegistry.getCapabilities(agent1.address);
      expect(tags1.length).to.equal(3);
      expect(weights1[0]).to.equal(80);
      
      console.log("✅ Capability management working");
    });
  });
  
  describe("2. Task Management Tests", function () {
    let taskId1, taskId2;
    
    it("Should create tasks successfully", async function () {
      console.log("📋 Testing task creation...");
      
      const deadline = Math.floor(Date.now() / 1000) + 86400; // 24 hours from now
      
      // Create task 1
      const tx1 = await taskManager.connect(user1).createTask(
        "ipfs://task1-metadata",
        ["coding", "analysis"],
        50, // min reputation
        ethers.parseEther("0.1"), // reward
        deadline
      );
      
      const receipt1 = await tx1.wait();
      const event1 = receipt1.logs.find(log => {
        try {
          return taskManager.interface.parseLog(log).name === "TaskCreated";
        } catch (e) {
          return false;
        }
      });
      taskId1 = event1.args[0];
      
      // Create task 2
      const tx2 = await taskManager.connect(user2).createTask(
        "ipfs://task2-metadata",
        ["coordination", "planning"],
        40,
        ethers.parseEther("0.2"),
        deadline
      );
      
      const receipt2 = await tx2.wait();
      const event2 = receipt2.logs.find(log => {
        try {
          return taskManager.interface.parseLog(log).name === "TaskCreated";
        } catch (e) {
          return false;
        }
      });
      taskId2 = event2.args[0];
      
      // Verify tasks exist
      expect(await taskManager.getTaskStatus(taskId1)).to.equal(0); // Created status
      expect(await taskManager.getTaskStatus(taskId2)).to.equal(0);
      
      console.log("✅ Task creation successful");
    });
    
    it("Should open tasks for bidding", async function () {
      console.log("🔓 Testing task opening...");
      
      await taskManager.connect(user1).openTask(taskId1);
      await taskManager.connect(user2).openTask(taskId2);
      
      expect(await taskManager.getTaskStatus(taskId1)).to.equal(1); // Open status
      expect(await taskManager.getTaskStatus(taskId2)).to.equal(1);
      
      console.log("✅ Task opening successful");
    });
    
    it("Should handle bidding process", async function () {
      console.log("💰 Testing bidding process...");
      
      // Open bidding for tasks
      await bidAuction.openBidding(taskId1, 3600); // 1 hour
      await bidAuction.openBidding(taskId2, 3600);
      
      // Agents place bids
      await bidAuction.connect(agent1).placeBid(taskId1, ethers.parseEther("0.05"));
      await bidAuction.connect(agent2).placeBid(taskId1, ethers.parseEther("0.04"));
      
      await bidAuction.connect(agent2).placeBid(taskId2, ethers.parseEther("0.15"));
      await bidAuction.connect(agent3).placeBid(taskId2, ethers.parseEther("0.12"));
      
      // Check bids were placed
      const [agents1, , bidAmounts1] = await bidAuction.getTaskBids(taskId1);
      expect(agents1.length).to.equal(2);
      expect(bidAmounts1[0]).to.equal(ethers.parseEther("0.05"));
      
      console.log("✅ Bidding process working");
    });
    
    it("Should assign tasks to best bidders", async function () {
      console.log("🎯 Testing task assignment...");
      
      // Wait for bidding to complete and close
      await ethers.provider.send("evm_increaseTime", [3601]); // Fast forward time
      await ethers.provider.send("evm_mine"); // Mine new block
      
      // Close bidding and assign tasks
      await bidAuction.connect(user1).closeBidding(taskId1);
      await bidAuction.connect(user2).closeBidding(taskId2);
      
      // Verify tasks are assigned
      expect(await taskManager.getTaskStatus(taskId1)).to.equal(2); // Assigned status
      expect(await taskManager.getTaskStatus(taskId2)).to.equal(2);
      
      console.log("✅ Task assignment successful");
    });
  });
  
  describe("3. Incentive Engine Tests", function () {
    it("Should compute task scores correctly", async function () {
      console.log("🧮 Testing incentive computations...");
      
      // Test task score calculation
      const score = await incentiveEngine.computeTaskScore(
        agent1.address,
        ethers.keccak256(ethers.toUtf8Bytes("test-task")),
        85, // quality score
        20  // delay ratio
      );
      
      // Score should be calculated as: α * quality + δ * (100 - delay)
      // With default α=60, δ=40: 60*85/100 + 40*(100-20)/100 = 51 + 32 = 83
      expect(score).to.be.closeTo(83, 5);
      
      console.log("✅ Task score computation working");
    });
    
    it("Should update agent reputation", async function () {
      console.log("⭐ Testing reputation updates...");
      
      // Record task quality to trigger reputation update
      await incentiveEngine.recordTaskQuality(
        ethers.keccak256(ethers.toUtf8Bytes("test-task-1")),
        agent1.address,
        75
      );
      
      // Check reputation was updated (should be higher than initial 50)
      const reputation = await incentiveEngine.getAgentReputation(agent1.address);
      expect(reputation).to.be.greaterThan(50);
      
      console.log(`✅ Agent reputation updated to: ${reputation}`);
    });
    
    it("Should calculate utility correctly", async function () {
      console.log("⚡ Testing utility calculation...");
      
      const utility = await incentiveEngine.calculateUtility(
        agent1.address,
        ["coding", "analysis"],
        ethers.parseEther("0.1"),
        2 // workload
      );
      
      expect(utility).to.be.greaterThan(0);
      console.log(`✅ Utility calculated: ${utility}`);
    });
  });
  
  describe("4. Message Hub Tests", function () {
    it("Should send and verify messages", async function () {
      console.log("💌 Testing message hub...");
      
      const messageHash = ethers.keccak256(ethers.toUtf8Bytes("Hello Agent 2"));
      const conversationId = ethers.keccak256(ethers.toUtf8Bytes("conv-1"));
      const nonce = Date.now();
      
      // Create signature for message
      const messageToSign = ethers.keccak256(
        ethers.solidityPacked(
          ["bytes32", "address", "uint256"],
          [messageHash, agent2.address, nonce]
        )
      );
      const signature = await agent1.signMessage(ethers.getBytes(messageToSign));
      
      // Send message
      await messageHub.connect(agent1).sendMessage(
        agent2.address,
        "ipfs://message-content",
        messageHash,
        conversationId,
        ethers.ZeroHash, // no previous message
        signature,
        nonce
      );
      
      // Verify message exists
      const message = await messageHub.messages(messageHash);
      expect(message.sender).to.equal(agent1.address);
      expect(message.recipient).to.equal(agent2.address);
      
      console.log("✅ Message hub working");
    });
  });
  
  describe("5. Action Logger Tests", function () {
    it("Should log agent actions", async function () {
      console.log("📝 Testing action logging...");
      
      const resourceId = ethers.keccak256(ethers.toUtf8Bytes("test-resource"));
      const nonce = Date.now();
      
      // Create signature for action
      const actionToSign = ethers.keccak256(
        ethers.solidityPacked(
          ["uint8", "bytes32", "string", "uint256"],
          [0, resourceId, "test metadata", nonce] // ActionType.TaskAccepted = 0
        )
      );
      const signature = await agent1.signMessage(ethers.getBytes(actionToSign));
      
      // Log action
      const actionId = await actionLogger.connect(agent1).logAction(
        0, // TaskAccepted
        resourceId,
        "test metadata",
        signature,
        nonce
      );
      
      // Verify action was logged
      const agentActions = await actionLogger.getAgentActions(agent1.address);
      expect(agentActions.length).to.be.greaterThan(0);
      
      console.log("✅ Action logging working");
    });
  });
  
  describe("6. Full Integration Test", function () {
    it("Should complete full agent workflow", async function () {
      console.log("🔄 Testing complete workflow...");
      
      // 1. Create a new task
      const deadline = Math.floor(Date.now() / 1000) + 86400;
      const tx = await taskManager.connect(user1).createTask(
        "ipfs://integration-task",
        ["evaluation"],
        60,
        ethers.parseEther("0.3"),
        deadline
      );
      
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          return taskManager.interface.parseLog(log).name === "TaskCreated";
        } catch (e) {
          return false;
        }
      });
      const integrationTaskId = event.args[0];
      
      // 2. Open task for bidding
      await taskManager.connect(user1).openTask(integrationTaskId);
      
      // 3. Open bidding
      await bidAuction.openBidding(integrationTaskId, 100); // Short bidding period
      
      // 4. Agent places bid
      await bidAuction.connect(agent3).placeBid(integrationTaskId, ethers.parseEther("0.25"));
      
      // 5. Wait and close bidding
      await ethers.provider.send("evm_increaseTime", [101]);
      await ethers.provider.send("evm_mine");
      await bidAuction.connect(user1).closeBidding(integrationTaskId);
      
      // 6. Start task
      await taskManager.connect(agent3).startTask(integrationTaskId);
      expect(await taskManager.getTaskStatus(integrationTaskId)).to.equal(3); // InProgress
      
      // 7. Complete task
      await taskManager.connect(agent3).completeTask(integrationTaskId, "ipfs://task-result");
      expect(await taskManager.getTaskStatus(integrationTaskId)).to.equal(4); // Completed
      
      // 8. Evaluate task
      await taskManager.evaluateTaskOutcome(
        integrationTaskId,
        90, // quality
        15, // delay ratio
        ["evaluation"],
        [92]
      );
      
      // Verify final state
      const task = await taskManager.tasks(integrationTaskId);
      expect(task.isEvaluated).to.be.true;
      
      console.log("🎉 Complete workflow test successful!");
    });
  });
  
  after(function () {
    console.log("🏁 All tests completed successfully!");
  });
});