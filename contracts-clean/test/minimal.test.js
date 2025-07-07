const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Minimal Test", function () {
  let agentRegistry;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    // Deploy AgentRegistry
    const AgentRegistryFactory = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistryFactory.deploy();
  });

  it("should register an agent", async function () {
    await agentRegistry.connect(addr1).registerAgent(
      "Test Agent",
      "ipfs://testmetadata",
      1 // AgentType.LLM
    );

    const isActive = await agentRegistry.isActiveAgent(addr1.address);
    expect(isActive).to.equal(true);
  });
});
