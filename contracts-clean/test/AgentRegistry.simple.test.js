const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentRegistry", function () {
  let AgentRegistry;
  let agentRegistry;
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

    // Register an agent for testing
    await agentRegistry.connect(addr1).registerAgent(
      "Test Agent",
      "ipfs://testmetadata",
      1 // AgentType.LLM
    );
  });

  describe("Basic Functionality", function () {
    it("should register a new agent", async function () {
      await agentRegistry.connect(addr2).registerAgent(
        "Agent 2",
        "ipfs://agent2metadata",
        2 // AgentType.Orchestrator
      );

      const isActive = await agentRegistry.isActiveAgent(addr2.address);
      expect(isActive).to.equal(true);
    });

    it("should get agent count", async function () {
      const count = await agentRegistry.getAgentCount();
      expect(count).to.equal(1); // One agent registered in beforeEach
    });

    it("should set and get reputation", async function () {
      await agentRegistry.connect(owner).setReputation(addr1.address, 75);
      const reputation = await agentRegistry.getReputation(addr1.address);
      expect(reputation).to.equal(75);
    });

    it("should get all agents", async function () {
      // Register another agent
      await agentRegistry.connect(addr2).registerAgent(
        "Agent 2",
        "ipfs://agent2metadata",
        2 // AgentType.Orchestrator
      );

      const allAgents = await agentRegistry.getAllAgents();
      expect(allAgents.length).to.equal(2);
      expect(allAgents[0]).to.equal(addr1.address);
      expect(allAgents[1]).to.equal(addr2.address);
    });
  });
});
