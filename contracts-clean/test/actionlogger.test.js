const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ActionLogger", function () {
  let agentRegistry;
  let actionLogger;
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
  });

  it("should log a system action", async function () {
    const taskId = ethers.keccak256(ethers.toUtf8Bytes("task1"));
    
    await actionLogger.connect(owner).logSystemAction(
      addr1.address,
      0, // ActionType.TaskAccepted
      taskId,
      "Test action"
    );

    const actionIds = await actionLogger.getAgentActions(addr1.address);
    expect(actionIds.length).to.equal(1);
  });
});
