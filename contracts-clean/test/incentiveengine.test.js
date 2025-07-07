const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("IncentiveEngine", function () {
  let agentRegistry;
  let actionLogger;
  let incentiveEngine;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    // Deploy AgentRegistry
    const AgentRegistryFactory = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistryFactory.deploy();

    // Register an agent
    await agentRegistry.connect(addr1).registerAgent(
      "Test Agent",
      "ipfs://testmetadata",
      1 // AgentType.LLM
    );

    // Deploy ActionLogger
    const ActionLoggerFactory = await ethers.getContractFactory("ActionLogger");
    const agentRegistryAddress = await agentRegistry.getAddress();
    actionLogger = await ActionLoggerFactory.deploy(agentRegistryAddress);

    // Deploy IncentiveEngine
    const IncentiveEngineFactory = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngineFactory.deploy(agentRegistryAddress);

    // Set ActionLogger address
    await incentiveEngine.setActionLogger(await actionLogger.getAddress());

    // Set capabilities for the agent
    await agentRegistry.connect(owner).setCapabilities(
      addr1.address,
      ["math"],
      [80]
    );
  });

  it("should calculate utility correctly", async function () {
    const utility = await incentiveEngine.calculateUtility(
      addr1.address,
      ["math"],
      100, // reward
      0    // workload
    );

    // Utility calculation depends on implementation but should be non-zero for matching capability
    expect(Number(utility)).to.be.gt(0);
  });
});
