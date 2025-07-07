const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Core Functionality Tests", function () {
  this.timeout(60000);
  
  let owner, agent1, agent2, agent3, user1;
  let agentRegistry, taskManager, bidAuction, incentiveEngine;
  
  before(async function () {
    console.log("🚀 Starting core functionality tests");
    
    [owner, agent1, agent2, agent3, user1] = await ethers.getSigners();
    
    // Deploy core contracts
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();
    
    const IncentiveEngine = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngine.deploy(agentRegistry.target);
    await incentiveEngine.waitForDeployment();
    
    const TaskManager = await ethers.getContractFactory("TaskManager");
    taskManager = await TaskManager.deploy(agentRegistry.target);
    await taskManager.waitForDeployment();
    
    const BidAuction = await ethers.getContractFactory("BidAuction");
    bidAuction = await BidAuction.deploy(agentRegistry.target, taskManager.target);
    await bidAuction.waitForDeployment();
    
    // Set connections
    await taskManager.setBidAuction(bidAuction.target);
    await taskManager.setIncentiveEngine(incentiveEngine.target);
    await bidAuction.setIncentiveEngine(incentiveEngine.target);
    
    console.log("✅ Core contracts deployed and connected");
  });
  
  describe("AgentRegistry Core Functions", function () {
    it("Should handle agent registration lifecycle", async function () {
      console.log("👤 Testing agent registration lifecycle...");
      
      // Register agents
      await agentRegistry.connect(agent1).registerAgent("Agent 1", "ipfs://agent1", 1);
      await agentRegistry.connect(agent2).registerAgent("Agent 2", "ipfs://agent2", 2);
      await agentRegistry.connect(agent3).registerAgent("Agent 3", "ipfs://agent3", 3);
      
      // Verify registrations
      expect(await agentRegistry.isActiveAgent(agent1.address)).to.be.true;
      expect(await agentRegistry.getAgentCount()).to.equal(3);
      
      // Test deactivation/activation
      await agentRegistry.connect(agent1).deactivateAgent(agent1.address);
      expect(await agentRegistry.isActiveAgent(agent1.address)).to.be.false;
      
      await agentRegistry.connect(agent1).activateAgent(agent1.address);
      expect(await agentRegistry.isActiveAgent(agent1.address)).to.be.true;
      
      console.log("✅ Agent registration lifecycle working");
    });
    
    it("Should manage agent capabilities", async function () {
      console.log("🎯 Testing capability management...");
      
      // Set capabilities for agent1
      await agentRegistry.setCapabilities(
        agent1.address,
        ["coding", "testing", "documentation"],
        [85, 70, 60]
      );
      
      // Verify capabilities
      const [tags, weights] = await agentRegistry.getCapabilities(agent1.address);
      expect(tags.length).to.equal(3);
      expect(weights[0]).to.equal(85);
      expect(tags[0]).to.equal("coding");
      
      // Update capabilities
      await agentRegistry.setCapabilities(
        agent1.address,
        ["coding", "testing"],
        [90, 75]
      );
      
      const [newTags, newWeights] = await agentRegistry.getCapabilities(agent1.address);
      expect(newTags.length).to.equal(2);
      expect(newWeights[0]).to.equal(90);
      
      console.log("✅ Capability management working");
    });
    
    it("Should track workload", async function () {
      console.log("⚖️ Testing workload management...");
      
      // Initial workload should be 0
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
      
      // Increment workload
      await agentRegistry.incrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(1);
      
      await agentRegistry.incrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(2);
      
      // Decrement workload
      await agentRegistry.decrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(1);
      
      // Reset workload
      await agentRegistry.resetWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
      
      console.log("✅ Workload management working");
    });
  });
  
  describe("TaskManager Core Functions", function () {
    let taskId;
    
    it("Should create and manage tasks", async function () {
      console.log("📋 Testing task management...");
      
      const deadline = Math.floor(Date.now() / 1000) + 86400;
      
      // Create task
      const tx = await taskManager.connect(user1).createTask(
        "ipfs://task-metadata",
        ["coding", "testing"],
        45, // min reputation
        ethers.parseEther("0.1"),
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
      taskId = event.args[0];
      
      // Verify task creation
      expect(await taskManager.getTaskStatus(taskId)).to.equal(0); // Created
      expect(await taskManager.getTaskCreator(taskId)).to.equal(user1.address);
      expect(await taskManager.getTaskMinReputation(taskId)).to.equal(45);
      
      // Open task
      await taskManager.connect(user1).openTask(taskId);
      expect(await taskManager.getTaskStatus(taskId)).to.equal(1); // Open
      
      console.log("✅ Task management working");
    });
    
    it("Should handle task assignment", async function () {
      console.log("🎯 Testing task assignment...");
      
      // Assign task directly (bypass bidding for testing)
      await taskManager.assignTask(taskId, agent1.address);
      expect(await taskManager.getTaskStatus(taskId)).to.equal(2); // Assigned
      
      // Start task
      await taskManager.connect(agent1).startTask(taskId);
      expect(await taskManager.getTaskStatus(taskId)).to.equal(3); // InProgress
      
      // Complete task
      await taskManager.connect(agent1).completeTask(taskId, "ipfs://result");
      expect(await taskManager.getTaskStatus(taskId)).to.equal(4); // Completed
      
      console.log("✅ Task assignment working");
    });
    
    it("Should query tasks by status", async function () {
      console.log("🔍 Testing task queries...");
      
      // Get all tasks
      const allTasks = await taskManager.getAllTasks();
      expect(allTasks.length).to.be.greaterThan(0);
      
      // Get completed tasks
      const completedTasks = await taskManager.getTasksByStatus(4); // Completed
      expect(completedTasks.length).to.be.greaterThan(0);
      
      // Get agent tasks
      const agentTasks = await taskManager.getAgentTasks(agent1.address);
      expect(agentTasks.length).to.be.greaterThan(0);
      
      console.log("✅ Task queries working");
    });
  });
  
  describe("BidAuction Core Functions", function () {
    let newTaskId;
    
    it("Should handle bidding workflow", async function () {
      console.log("💰 Testing bidding workflow...");
      
      // Create a new task for bidding
      const deadline = Math.floor(Date.now() / 1000) + 86400;
      const tx = await taskManager.connect(user1).createTask(
        "ipfs://bidding-task",
        ["testing"],
        40,
        ethers.parseEther("0.2"),
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
      newTaskId = event.args[0];
      
      // Open task
      await taskManager.connect(user1).openTask(newTaskId);
      
      // Open bidding
      await bidAuction.connect(user1).openBidding(newTaskId, 3600);
      expect(await bidAuction.isBiddingOpen(newTaskId)).to.be.true;
      
      // Place bids
      await bidAuction.connect(agent1).placeBid(newTaskId, ethers.parseEther("0.15"));
      await bidAuction.connect(agent2).placeBid(newTaskId, ethers.parseEther("0.18"));
      
      // Check bids
      const [agents, , bidAmounts] = await bidAuction.getTaskBids(newTaskId);
      expect(agents.length).to.equal(2);
      expect(bidAmounts[0]).to.equal(ethers.parseEther("0.15"));
      
      // Check if agents have bid
      expect(await bidAuction.hasAgentBid(newTaskId, agent1.address)).to.be.true;
      expect(await bidAuction.hasAgentBid(newTaskId, agent3.address)).to.be.false;
      
      console.log("✅ Bidding workflow working");
    });
    
    it("Should calculate utility scores", async function () {
      console.log("⚡ Testing utility calculation...");
      
      // Calculate utility for agent1 on the task
      const utility = await bidAuction.calculateAgentUtility(newTaskId, agent1.address);
      expect(utility).to.be.greaterThan(0);
      
      console.log(`✅ Utility calculation working: ${utility}`);
    });
  });
  
  describe("IncentiveEngine Core Functions", function () {
    it("Should handle utility calculations", async function () {
      console.log("🧮 Testing incentive engine...");
      
      // Test utility calculation
      const utility = await incentiveEngine.calculateUtility(
        agent1.address,
        ["coding", "testing"],
        ethers.parseEther("0.1"),
        1 // workload
      );
      
      expect(utility).to.be.greaterThan(0);
      console.log(`Calculated utility: ${utility}`);
      
      // Test workload and reputation getters
      const workload = await incentiveEngine.getAgentWorkload(agent1.address);
      const reputation = await incentiveEngine.getAgentReputation(agent1.address);
      
      expect(workload).to.be.greaterThanOrEqual(0);
      expect(reputation).to.equal(50); // Default starting reputation
      
      console.log(`Agent workload: ${workload}, reputation: ${reputation}`);
      console.log("✅ Incentive engine basic functions working");
    });
  });
  
  describe("Integration Test", function () {
    it("Should demonstrate full system integration", async function () {
      console.log("🔄 Testing system integration...");
      
      // Create new task
      const deadline = Math.floor(Date.now() / 1000) + 86400;
      const tx = await taskManager.connect(user1).createTask(
        "ipfs://integration-test",
        ["coding"],
        30, // very low requirement
        ethers.parseEther("0.5"),
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
      
      // 1. Open task
      await taskManager.connect(user1).openTask(integrationTaskId);
      
      // 2. Assign directly to agent3
      await taskManager.assignTask(integrationTaskId, agent3.address);
      
      // 3. Agent starts task
      await taskManager.connect(agent3).startTask(integrationTaskId);
      
      // 4. Agent completes task
      await taskManager.connect(agent3).completeTask(integrationTaskId, "ipfs://integration-result");
      
      // 5. Verify final state
      expect(await taskManager.getTaskStatus(integrationTaskId)).to.equal(4); // Completed
      
      // 6. Check agent got the task
      const agentTasks = await taskManager.getAgentTasks(agent3.address);
      expect(agentTasks.length).to.be.greaterThan(0);
      
      console.log("🎉 System integration test successful!");
    });
  });
  
  after(function () {
    console.log("🏁 Core functionality tests completed!");
  });
});