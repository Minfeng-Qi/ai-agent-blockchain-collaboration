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
  });
  
  describe("TaskMarketplace Functionality", function () {
    it("should create tasks and verify their status", async function () {
      // Create tasks with different capabilities
      const tx1 = await taskMarketplace.connect(user1).createTask(
        "Research task",
        ["research", "writing"],
        30,
        ethers.parseEther("0.05"),
        taskDeadline
      );
      
      const receipt1 = await tx1.wait();
      const event1 = receipt1.logs.find(log => log.fragment && log.fragment.name === "TaskCreated");
      const taskId1 = event1.args[0];
      const taskIdBytes1 = toBytes32(taskId1);
      
      const tx2 = await taskMarketplace.connect(user1).createTask(
        "Development task",
        ["coding", "testing"],
        30,
        ethers.parseEther("0.05"),
        taskDeadline
      );
      
      const receipt2 = await tx2.wait();
      const event2 = receipt2.logs.find(log => log.fragment && log.fragment.name === "TaskCreated");
      const taskId2 = event2.args[0];
      const taskIdBytes2 = toBytes32(taskId2);
      
      // Open the tasks manually
      await taskManager.connect(owner).openTask(taskIdBytes1);
      await taskManager.connect(owner).openTask(taskIdBytes2);
      
      // Verify tasks were created and opened
      const task1 = await taskManager.tasks(taskIdBytes1);
      const task2 = await taskManager.tasks(taskIdBytes2);
      
      expect(task1.status).to.equal(1); // Open status
      expect(task2.status).to.equal(1); // Open status
      
      // Check if tasks are listed in marketplace
      const openTasks = await taskMarketplace.getOpenTasks();
      console.log("Open tasks:", openTasks.length);
      
      // We should have at least the tasks we just created
      expect(openTasks.length).to.be.gte(2);
    });
  });

  describe("TaskManager Functionality", function () {
    it("should create and manage tasks directly", async function () {
      // Create a task directly with TaskManager
      const tx = await taskManager.connect(user1).createTask(
        "Direct task creation test",
        ["research", "blockchain"],
        40, // min reputation
        ethers.parseEther("0.1"), // reward
        taskDeadline
      );
      
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.fragment && log.fragment.name === "TaskCreated");
      const taskId = event.args[0];
      const taskIdBytes = toBytes32(taskId);
      
      // Verify task was created
      const task = await taskManager.tasks(taskIdBytes);
      expect(task.creator).to.equal(user1.address);
      expect(task.reward).to.equal(ethers.parseEther("0.1"));
      expect(task.minReputation).to.equal(40);
      expect(task.status).to.equal(0); // Pending status
      
      // Open the task
      await taskManager.connect(owner).openTask(taskIdBytes);
      
      // Verify task status changed
      const openedTask = await taskManager.tasks(taskIdBytes);
      expect(openedTask.status).to.equal(1); // Open status
    });
  });
}); 