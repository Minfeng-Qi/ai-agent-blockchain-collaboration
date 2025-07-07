const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LLM Multi-Agent System Integration Tests (ethers v6)", function () {
  // Set longer timeout for integration tests
  this.timeout(120000);
  
  // Test accounts
  let owner, agent1, agent2, agent3, evaluator, user1, user2;
  
  // Contract instances
  let agentRegistry;
  let actionLogger;
  let incentiveEngine;
  let bidAuction;
  let taskManager;
  let taskMarketplace;
  let messageHub;
  
  // Test data
  const taskDeadline = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
  
  // Helper function - convert uint256 to bytes32
  function toBytes32(value) {
    return ethers.zeroPadValue(ethers.toBeHex(value), 32);
  }
  
  before(async function () {
    // Get signers
    [owner, agent1, agent2, agent3, evaluator, user1, user2] = await ethers.getSigners();
    
    // Deploy contracts
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();
    console.log("AgentRegistry deployed at:", agentRegistry.target);
    
    const ActionLogger = await ethers.getContractFactory("ActionLogger");
    actionLogger = await ActionLogger.deploy(agentRegistry.target);
    await actionLogger.waitForDeployment();
    console.log("ActionLogger deployed at:", actionLogger.target);
    
    const IncentiveEngine = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngine.deploy(agentRegistry.target);
    await incentiveEngine.waitForDeployment();
    console.log("IncentiveEngine deployed at:", incentiveEngine.target);
    
    const TaskManager = await ethers.getContractFactory("TaskManager");
    taskManager = await TaskManager.deploy(agentRegistry.target);
    await taskManager.waitForDeployment();
    console.log("TaskManager deployed at:", taskManager.target);
    
    const BidAuction = await ethers.getContractFactory("BidAuction");
    bidAuction = await BidAuction.deploy(agentRegistry.target, taskManager.target);
    await bidAuction.waitForDeployment();
    console.log("BidAuction deployed at:", bidAuction.target);
    
    // Set contract connections
    await taskManager.setBidAuction(bidAuction.target);
    await taskManager.setIncentiveEngine(incentiveEngine.target);
    
    const TaskMarketplace = await ethers.getContractFactory("TaskMarketplace");
    taskMarketplace = await TaskMarketplace.deploy(
      taskManager.target,
      bidAuction.target,
      agentRegistry.target,
      incentiveEngine.target
    );
    await taskMarketplace.waitForDeployment();
    console.log("TaskMarketplace deployed at:", taskMarketplace.target);
    
    const MessageHub = await ethers.getContractFactory("MessageHub");
    messageHub = await MessageHub.deploy(agentRegistry.target);
    await messageHub.waitForDeployment();
    console.log("MessageHub deployed at:", messageHub.target);
    
    // Set contract connections
    await incentiveEngine.setActionLogger(actionLogger.target);
    await bidAuction.setIncentiveEngine(incentiveEngine.target);
    
    console.log("All contracts deployed and connected");
    
    // Register agents
    await agentRegistry.connect(owner).registerAgent(
      agent1.address,
      "Research Agent",
      "ipfs://agent1-metadata",
      "http://agent1-api.example.com",
      0 // LLM agent type
    );
    
    await agentRegistry.connect(owner).registerAgent(
      agent2.address,
      "Development Agent",
      "ipfs://agent2-metadata",
      "http://agent2-api.example.com",
      0 // LLM agent type
    );
    
    await agentRegistry.connect(owner).registerAgent(
      agent3.address,
      "Evaluation Agent",
      "ipfs://agent3-metadata",
      "http://agent3-api.example.com",
      0 // LLM agent type
    );
    
    // Set agent capabilities
    const agent1Capabilities = ["research", "writing", "analysis", "blockchain"];
    const agent1Weights = Array(agent1Capabilities.length).fill(50);
    await agentRegistry.connect(owner).setCapabilities(
      agent1.address,
      agent1Capabilities,
      agent1Weights
    );
    
    const agent2Capabilities = ["coding", "analysis", "testing", "blockchain"];
    const agent2Weights = Array(agent2Capabilities.length).fill(50);
    await agentRegistry.connect(owner).setCapabilities(
      agent2.address,
      agent2Capabilities,
      agent2Weights
    );
    
    const agent3Capabilities = ["evaluation", "analysis", "quality"];
    const agent3Weights = Array(agent3Capabilities.length).fill(50);
    await agentRegistry.connect(owner).setCapabilities(
      agent3.address,
      agent3Capabilities,
      agent3Weights
    );
  });
  
  describe("Agent Registration and Capabilities", function () {
    it("should register agents with different capabilities", async function () {
      // Verify agent registration
      const agent1Info = await agentRegistry.agents(agent1.address);
      expect(agent1Info.name).to.equal("Research Agent");
      expect(agent1Info.active).to.be.true;
      
      const agent2Info = await agentRegistry.agents(agent2.address);
      expect(agent2Info.name).to.equal("Development Agent");
      expect(agent2Info.active).to.be.true;
      
      // Verify capabilities
      const [agent1Tags, agent1WeightsResult] = await agentRegistry.getCapabilities(agent1.address);
      const [agent2Tags, agent2WeightsResult] = await agentRegistry.getCapabilities(agent2.address);
      
      expect(agent1Tags).to.include("research");
      expect(agent1Tags).to.include("writing");
      expect(agent2Tags).to.include("coding");
      expect(agent2Tags).to.include("testing");
      
      // Verify weights - default should be 50
      for (let i = 0; i < agent1WeightsResult.length; i++) {
        expect(agent1WeightsResult[i]).to.equal(50);
      }
    });
  });
  
  describe("Task Creation and Management", function () {
    let taskId;
    let taskIdBytes32;
    
    it("should create and open tasks", async function () {
      // Create task
      const tx = await taskManager.connect(user1).createTask(
        "Research on ZK-rollups and their applications",
        ["research", "blockchain", "writing"],
        40, // min reputation
        ethers.parseEther("0.2"), // reward
        taskDeadline
      );
      
      const receipt = await tx.wait();
      const event = receipt.logs.find(
        log => log.fragment && log.fragment.name === "TaskCreated"
      );
      
      expect(event).to.not.be.undefined;
      taskId = event.args[0];
      taskIdBytes32 = toBytes32(taskId);
      
      // Verify task creation
      const task = await taskManager.tasks(taskIdBytes32);
      expect(task.minReputation).to.equal(40);
      
      // Open task
      await taskManager.connect(owner).openTask(taskIdBytes32);
      
      // Verify task status
      const updatedTask = await taskManager.tasks(taskIdBytes32);
      expect(updatedTask.status).to.equal(1); // Open status
    });
    
    it("should calculate agent utility scores", async function () {
      // Calculate utility scores
      const agent1Utility = await bidAuction.calculateAgentUtility(taskIdBytes32, agent1.address);
      const agent2Utility = await bidAuction.calculateAgentUtility(taskIdBytes32, agent2.address);
      
      // Both should have some utility score since they have relevant capabilities
      expect(agent1Utility).to.be.gt(0);
      expect(agent2Utility).to.be.gt(0);
    });
  });
  
  describe("TaskMarketplace Functionality", function () {
    it("should list open tasks", async function () {
      // Create additional tasks
      const tx1 = await taskMarketplace.connect(user1).createTask(
        "Research task",
        ["research", "writing"],
        30,
        ethers.parseEther("0.05"),
        taskDeadline
      );
      
      const tx2 = await taskMarketplace.connect(user1).createTask(
        "Development task",
        ["coding", "testing"],
        30,
        ethers.parseEther("0.05"),
        taskDeadline
      );
      
      // Open the tasks
      const receipt1 = await tx1.wait();
      const event1 = receipt1.logs.find(log => log.fragment && log.fragment.name === "TaskCreated");
      const taskId1 = event1.args[0];
      const taskIdBytes1 = toBytes32(taskId1);
      
      const receipt2 = await tx2.wait();
      const event2 = receipt2.logs.find(log => log.fragment && log.fragment.name === "TaskCreated");
      const taskId2 = event2.args[0];
      const taskIdBytes2 = toBytes32(taskId2);
      
      await taskManager.connect(owner).openTask(taskIdBytes1);
      await taskManager.connect(owner).openTask(taskIdBytes2);
      
      // Check if tasks are listed in marketplace
      const openTasks = await taskMarketplace.getOpenTasks();
      console.log("Open tasks:", openTasks.length);
      
      // We should have at least the tasks we just created
      expect(openTasks.length).to.be.gte(2);
    });
  });
  
  describe("Agent Workload Management", function () {
    it("should track agent workload", async function () {
      // Check initial workload
      const initialWorkload = await agentRegistry.agentWorkload(agent1.address);
      
      // Increment workload
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      
      // Verify workload increased
      const updatedWorkload = await agentRegistry.agentWorkload(agent1.address);
      expect(updatedWorkload).to.equal(Number(initialWorkload) + 1);
      
      // Reset workload
      await agentRegistry.connect(owner).resetWorkload(agent1.address);
      
      // Verify workload reset
      const resetWorkload = await agentRegistry.agentWorkload(agent1.address);
      expect(resetWorkload).to.equal(0);
    });
  });
}); 