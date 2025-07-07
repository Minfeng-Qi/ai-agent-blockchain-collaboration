const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("IncentiveEngine Minimal Test", function () {
  let agentRegistry;
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

    // Deploy IncentiveEngine
    const IncentiveEngineFactory = await ethers.getContractFactory("IncentiveEngine");
    incentiveEngine = await IncentiveEngineFactory.deploy(agentRegistry.target);

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
    expect(utility).to.be.gt(0);
  });
});
