const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("IncentiveEngine", function () {
  let agentRegistry;
  let actionLogger;
  let incentiveEngine;
  let owner;
  let addr1;
  let addr2;
  let addrs;

  beforeEach(async function () {
    // Get signers
    [owner, addr1, addr2, ...addrs] = await ethers.getSigners();

    // Deploy AgentRegistry
    const AgentRegistryFactory = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistryFactory.deploy();

    // Register agents for testing
    await agentRegistry.connect(addr1).registerAgent(
      "Agent 1",
      "ipfs://agent1metadata",
      1 // AgentType.LLM
    );

    await agentRegistry.connect(addr2).registerAgent(
      "Agent 2",
      "ipfs://agent2metadata",
      2 // AgentType.Orchestrator
    );

    // Deploy ActionLogger
    const ActionLoggerFactory = await ethers.getContractFactory("ActionLogger");
    actionLogger = await ActionLoggerFactory.deploy(agentRegistry.target);

    // Deploy IncentiveEngine with only AgentRegistry address
    const IncentiveEngineFactory = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngineFactory.deploy(agentRegistry.target);
    
    // Set ActionLogger address separately
    await incentiveEngine.setActionLogger(actionLogger.target);

    // Set capabilities for agents
    await agentRegistry.connect(owner).setCapabilities(
      addr1.address,
      ["math", "coding"],
      [80, 90]
    );

    await agentRegistry.connect(owner).setCapabilities(
      addr2.address,
      ["writing", "translation"],
      [85, 95]
    );
  });

  describe("Basic Functionality", function () {
    it("should record task evaluation", async function () {
      const taskId = ethers.keccak256(ethers.toUtf8Bytes("task1"));
      
      await incentiveEngine.connect(owner).recordTaskEvaluation(
        taskId,
        addr1.address,
        90, // quality
        0,  // delay ratio
        ["math"],
        [85]
      );

      const evaluation = await incentiveEngine.getTaskEvaluation(taskId);
      expect(evaluation[0]).to.equal(90); // quality
      expect(evaluation[2]).to.equal(90); // finalScore (no delay)
    });

    it("should calculate utility correctly", async function () {
      const utility = await incentiveEngine.calculateUtility(
        addr1.address,
        ["math"],
        100, // reward
        0    // workload
      );

      // Utility calculation depends on implementation but should be non-zero for matching capability
      expect(utility).to.be.gt(0);
    });
  });
});
