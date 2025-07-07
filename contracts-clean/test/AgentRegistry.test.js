const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentRegistry", function () {
  let AgentRegistry;
  let agentRegistry;
  let owner;
  let agent1;
  let agent2;
  let agent3;
  let user;

  beforeEach(async function () {
    // Get signers
    [owner, agent1, agent2, agent3, user] = await ethers.getSigners();

    // Deploy AgentRegistry
    AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();

    // Register agents for testing
    await agentRegistry.connect(owner).registerAgent(
      "Agent 1",
      "ipfs://agent1metadata",
      1 // AgentType.LLM
    );

    await agentRegistry.connect(owner).registerAgent(
      "Agent 2",
      "ipfs://agent2metadata",
      2 // AgentType.Orchestrator
    );
  });

  describe("Agent Type Management", function () {
    it("should register an agent with a specific type", async function () {
      await agentRegistry.connect(owner).registerAgent(
        "Agent 3",
        "ipfs://agent3metadata",
        3 // AgentType.Evaluator
      );

      const agentType = await agentRegistry.getAgentType(agent3.address);
      expect(agentType).to.equal(3); // AgentType.Evaluator
    });

    it("should allow self-registration with default LLM type", async function () {
      await agentRegistry.connect(agent3).registerAgent(
        "Self Agent",
        "ipfs://selfmetadata",
        "https://self.example.com"
      );

      const agentType = await agentRegistry.getAgentType(agent3.address);
      expect(agentType).to.equal(1); // AgentType.LLM
    });

    it("should retrieve the correct agent type", async function () {
      const type1 = await agentRegistry.getAgentType(agent1.address);
      const type2 = await agentRegistry.getAgentType(agent2.address);

      expect(type1).to.equal(1); // AgentType.LLM
      expect(type2).to.equal(2); // AgentType.Orchestrator
    });
  });

  describe("Capability Management", function () {
    it("should set and retrieve agent capabilities", async function () {
      const tags = ["math", "coding", "writing"];
      const weights = [80, 90, 70];

      await agentRegistry.connect(owner).setCapabilities(
        agent1.address,
        tags,
        weights
      );

      const capabilities = await agentRegistry.getCapabilities(agent1.address);
      
      expect(capabilities[0]).to.deep.equal(tags); // tags
      expect(capabilities[1].map(w => Number(w))).to.deep.equal(weights); // weights
    });

    it("should update existing capabilities", async function () {
      // Initial capabilities
      await agentRegistry.connect(owner).setCapabilities(
        agent1.address,
        ["math", "coding"],
        [80, 90]
      );

      // Updated capabilities
      await agentRegistry.connect(owner).setCapabilities(
        agent1.address,
        ["math", "writing"],
        [85, 75]
      );

      const capabilities = await agentRegistry.getCapabilities(agent1.address);
      
      expect(capabilities[0]).to.deep.equal(["math", "writing"]);
      expect(capabilities[1].map(w => Number(w))).to.deep.equal([85, 75]);
    });

    it("should emit CapabilitiesUpdated event", async function () {
      const tags = ["math", "coding"];
      const weights = [80, 90];

      await expect(
        agentRegistry.connect(owner).setCapabilities(agent1.address, tags, weights)
      )
        .to.emit(agentRegistry, "CapabilitiesUpdated")
        .withArgs(agent1.address, tags, weights);
    });

    it("should only allow owner to set capabilities", async function () {
      await expect(
        agentRegistry.connect(user).setCapabilities(
          agent1.address,
          ["math"],
          [80]
        )
      ).to.be.revertedWithCustomError(agentRegistry, "OwnableUnauthorizedAccount");
    });

    it("should ignore zero weights when setting capabilities", async function () {
      await agentRegistry.connect(owner).setCapabilities(
        agent1.address,
        ["math", "coding", "writing"],
        [80, 0, 70]
      );

      const capabilities = await agentRegistry.getCapabilities(agent1.address);
      
      // Should only include non-zero weights
      expect(capabilities[0]).to.deep.equal(["math", "writing"]);
      expect(capabilities[1].map(w => Number(w))).to.deep.equal([80, 70]);
    });
  });

  describe("Workload Management", function () {
    it("should increment agent workload", async function () {
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      
      const workload = await agentRegistry.agentWorkload(agent1.address);
      expect(workload).to.equal(1);
      
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      const updatedWorkload = await agentRegistry.agentWorkload(agent1.address);
      expect(updatedWorkload).to.equal(2);
    });

    it("should decrement agent workload", async function () {
      // First increment to 2
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      
      // Then decrement to 1
      await agentRegistry.connect(owner).decrementWorkload(agent1.address);
      
      const workload = await agentRegistry.agentWorkload(agent1.address);
      expect(workload).to.equal(1);
    });

    it("should not decrement workload below zero", async function () {
      await expect(
        agentRegistry.connect(owner).decrementWorkload(agent1.address)
      ).to.be.revertedWith("Workload already at minimum");
    });

    it("should reset agent workload", async function () {
      // First increment to 3
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      
      // Then reset to 0
      await agentRegistry.connect(owner).resetWorkload(agent1.address);
      
      const workload = await agentRegistry.agentWorkload(agent1.address);
      expect(workload).to.equal(0);
    });

    it("should emit WorkloadUpdated event", async function () {
      await expect(
        agentRegistry.connect(owner).incrementWorkload(agent1.address)
      )
        .to.emit(agentRegistry, "WorkloadUpdated")
        .withArgs(agent1.address, 1);

      await expect(
        agentRegistry.connect(owner).resetWorkload(agent1.address)
      )
        .to.emit(agentRegistry, "WorkloadUpdated")
        .withArgs(agent1.address, 0);
    });

    it("should only allow owner to manage workload", async function () {
      await expect(
        agentRegistry.connect(user).incrementWorkload(agent1.address)
      ).to.be.revertedWithCustomError(agentRegistry, "OwnableUnauthorizedAccount");

      await expect(
        agentRegistry.connect(user).decrementWorkload(agent1.address)
      ).to.be.revertedWithCustomError(agentRegistry, "OwnableUnauthorizedAccount");

      await expect(
        agentRegistry.connect(user).resetWorkload(agent1.address)
      ).to.be.revertedWithCustomError(agentRegistry, "OwnableUnauthorizedAccount");
    });
  });

  describe("Integration Tests", function () {
    it("should integrate capabilities with agent type", async function () {
      // Register an evaluator agent
      await agentRegistry.connect(owner).registerAgent(
        agent3.address,
        "Evaluator",
        "ipfs://evaluatormetadata",
        "https://evaluator.example.com",
        3 // AgentType.Evaluator
      );
      
      // Set evaluator-specific capabilities
      await agentRegistry.connect(owner).setCapabilities(
        agent3.address,
        ["assessment", "feedback", "quality"],
        [95, 90, 85]
      );
      
      // Verify agent type and capabilities
      const agentType = await agentRegistry.getAgentType(agent3.address);
      expect(agentType).to.equal(3); // AgentType.Evaluator
      
      const capabilities = await agentRegistry.getCapabilities(agent3.address);
      expect(capabilities[0]).to.deep.equal(["assessment", "feedback", "quality"]);
    });

    it("should track workload across multiple agents", async function () {
      // Increment workloads
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      await agentRegistry.connect(owner).incrementWorkload(agent1.address);
      await agentRegistry.connect(owner).incrementWorkload(agent2.address);
      
      // Verify workloads
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(2);
      expect(await agentRegistry.agentWorkload(agent2.address)).to.equal(1);
      
      // Reset one agent's workload
      await agentRegistry.connect(owner).resetWorkload(agent1.address);
      
      // Verify updated workloads
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
      expect(await agentRegistry.agentWorkload(agent2.address)).to.equal(1);
    });
  });
});

describe("AgentRegistry Contract Tests", function () {
  // Test accounts
  let owner, agent1, agent2, agent3, nonOwner;
  
  // Contract instance
  let agentRegistry;
  
  before(async function () {
    // Get signers
    [owner, agent1, agent2, agent3, nonOwner] = await ethers.getSigners();
    
    // Deploy contract
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    agentRegistry = await AgentRegistry.deploy();
    await agentRegistry.waitForDeployment();
    
    console.log("AgentRegistry deployed for testing");
  });
  
  describe("Agent Registration", function () {
    it("Should register an agent by owner", async function () {
      await agentRegistry.registerAgent(
        agent1.address,
        "Test Agent 1",
        "ipfs://QmAgentMetadata1",
        "https://api.agent1.example.com",
        1 // LLM agent type
      );
      
      // Verify registration
      const agent = await agentRegistry.agents(agent1.address);
      expect(agent.name).to.equal("Test Agent 1");
      expect(agent.metadataURI).to.equal("ipfs://QmAgentMetadata1");
      expect(agent.owner).to.equal(agent1.address);
      expect(agent.reputation).to.equal(50); // Default reputation
      expect(agent.active).to.be.true;
      expect(agent.agentType).to.equal(1); // LLM type
      
      // Verify agent was added to the list
      const agentAddresses = await agentRegistry.getAllAgents();
      expect(agentAddresses).to.include(agent1.address);
    });
    
    it("Should allow self-registration", async function () {
      await agentRegistry.connect(agent2).registerAgent(
        "Test Agent 2",
        "ipfs://QmAgentMetadata2",
        "https://api.agent2.example.com"
      );
      
      // Verify registration
      const agent = await agentRegistry.agents(agent2.address);
      expect(agent.name).to.equal("Test Agent 2");
      expect(agent.metadataURI).to.equal("ipfs://QmAgentMetadata2");
      expect(agent.owner).to.equal(agent2.address);
      expect(agent.reputation).to.equal(50); // Default reputation
      expect(agent.active).to.be.true;
      expect(agent.agentType).to.equal(1); // Default to LLM type
    });
    
    it("Should prevent duplicate registration", async function () {
      await expect(
        agentRegistry.registerAgent(
          agent1.address,
          "Duplicate Agent",
          "ipfs://QmDuplicate",
          "https://api.duplicate.example.com",
          1
        )
      ).to.be.revertedWith("Agent already registered");
      
      await expect(
        agentRegistry.connect(agent2).registerAgent(
          "Duplicate Self-Registration",
          "ipfs://QmDuplicateSelf",
          "https://api.duplicate-self.example.com"
        )
      ).to.be.revertedWith("Agent already registered");
    });
  });
  
  describe("Agent Information Updates", function () {
    it("Should update agent information", async function () {
      await agentRegistry.connect(agent1).updateAgent(
        "Updated Agent 1",
        "ipfs://QmUpdatedMetadata1"
      );
      
      // Verify update
      const agent = await agentRegistry.agents(agent1.address);
      expect(agent.name).to.equal("Updated Agent 1");
      expect(agent.metadataURI).to.equal("ipfs://QmUpdatedMetadata1");
    });
    
    it("Should prevent updates from non-registered agents", async function () {
      await expect(
        agentRegistry.connect(nonOwner).updateAgent(
          "Unauthorized Update",
          "ipfs://QmUnauthorized"
        )
      ).to.be.revertedWith("Agent not registered");
    });
    
    it("Should prevent updates from inactive agents", async function () {
      // Deactivate agent
      await agentRegistry.connect(agent1).deactivateAgent(agent1.address);
      
      // Verify agent is inactive
      const agent = await agentRegistry.agents(agent1.address);
      expect(agent.active).to.be.false;
      
      // Attempt update
      await expect(
        agentRegistry.connect(agent1).updateAgent(
          "Update from Inactive",
          "ipfs://QmInactive"
        )
      ).to.be.revertedWith("Agent not active");
      
      // Reactivate for further tests
      await agentRegistry.connect(agent1).activateAgent(agent1.address);
    });
  });
  
  describe("Agent Status Management", function () {
    it("Should deactivate an agent", async function () {
      // Deactivate by owner
      await agentRegistry.deactivateAgent(agent1.address);
      
      // Verify deactivation
      let agent = await agentRegistry.agents(agent1.address);
      expect(agent.active).to.be.false;
      
      // Reactivate for next test
      await agentRegistry.activateAgent(agent1.address);
      
      // Deactivate by self
      await agentRegistry.connect(agent1).deactivateAgent(agent1.address);
      
      // Verify deactivation
      agent = await agentRegistry.agents(agent1.address);
      expect(agent.active).to.be.false;
    });
    
    it("Should activate an agent", async function () {
      // Activate
      await agentRegistry.activateAgent(agent1.address);
      
      // Verify activation
      const agent = await agentRegistry.agents(agent1.address);
      expect(agent.active).to.be.true;
    });
    
    it("Should prevent unauthorized deactivation", async function () {
      await expect(
        agentRegistry.connect(nonOwner).deactivateAgent(agent2.address)
      ).to.be.revertedWith("Not authorized");
    });
    
    it("Should prevent unauthorized activation", async function () {
      // Deactivate first
      await agentRegistry.connect(agent2).deactivateAgent(agent2.address);
      
      // Attempt unauthorized activation
      await expect(
        agentRegistry.connect(nonOwner).activateAgent(agent2.address)
      ).to.be.revertedWith("Not authorized");
      
      // Reactivate for further tests
      await agentRegistry.connect(agent2).activateAgent(agent2.address);
    });
  });
  
  describe("Reputation Management", function () {
    it("Should update agent reputation", async function () {
      // Initial reputation should be 50
      let agent = await agentRegistry.agents(agent1.address);
      expect(agent.reputation).to.equal(50);
      
      // Update reputation
      await agentRegistry.updateReputation(agent1.address, 75);
      
      // Verify update
      agent = await agentRegistry.agents(agent1.address);
      expect(agent.reputation).to.equal(75);
    });
    
    it("Should enforce reputation bounds", async function () {
      await expect(
        agentRegistry.updateReputation(agent1.address, 101)
      ).to.be.revertedWith("Reputation must be between 0-100");
    });
    
    it("Should prevent unauthorized reputation updates", async function () {
      await expect(
        agentRegistry.connect(nonOwner).updateReputation(agent1.address, 60)
      ).to.be.revertedWithCustomError(agentRegistry, "OwnableUnauthorizedAccount");
    });
  });
  
  describe("Capability Management", function () {
    it("Should set agent capabilities with weights", async function () {
      await agentRegistry.setCapabilities(
        agent1.address,
        ["research", "writing", "coding"],
        [80, 70, 90]
      );
      
      // Verify capabilities
      const [tags, weights] = await agentRegistry.getCapabilities(agent1.address);
      
      expect(tags.length).to.equal(3);
      expect(weights.length).to.equal(3);
      
      expect(tags).to.include("research");
      expect(tags).to.include("writing");
      expect(tags).to.include("coding");
      
      // Find index for each tag
      const researchIndex = tags.findIndex(t => t === "research");
      const writingIndex = tags.findIndex(t => t === "writing");
      const codingIndex = tags.findIndex(t => t === "coding");
      
      // Verify weights
      expect(weights[researchIndex]).to.equal(80);
      expect(weights[writingIndex]).to.equal(70);
      expect(weights[codingIndex]).to.equal(90);
    });
    
    it("Should update existing capabilities", async function () {
      // Update capabilities
      await agentRegistry.setCapabilities(
        agent1.address,
        ["research", "writing", "analysis"],
        [85, 75, 65]
      );
      
      // Verify capabilities
      const [tags, weights] = await agentRegistry.getCapabilities(agent1.address);
      
      expect(tags.length).to.equal(3);
      expect(tags).to.include("research");
      expect(tags).to.include("writing");
      expect(tags).to.include("analysis");
      expect(tags).to.not.include("coding"); // Should be removed
      
      // Find index for each tag
      const researchIndex = tags.findIndex(t => t === "research");
      const writingIndex = tags.findIndex(t => t === "writing");
      const analysisIndex = tags.findIndex(t => t === "analysis");
      
      // Verify weights
      expect(weights[researchIndex]).to.equal(85);
      expect(weights[writingIndex]).to.equal(75);
      expect(weights[analysisIndex]).to.equal(65);
    });
    
    it("Should validate capability weights", async function () {
      await expect(
        agentRegistry.setCapabilities(
          agent1.address,
          ["research"],
          [101] // Invalid weight
        )
      ).to.be.revertedWith("Weight must be between 0-100");
    });
    
    it("Should require matching arrays", async function () {
      await expect(
        agentRegistry.setCapabilities(
          agent1.address,
          ["research", "writing"],
          [80] // Mismatched length
        )
      ).to.be.revertedWith("Tags and weights must have same length");
    });
  });
  
  describe("Workload Management", function () {
    it("Should increment agent workload", async function () {
      // Reset workload first
      await agentRegistry.resetWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
      
      // Increment workload
      await agentRegistry.incrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(1);
      
      // Increment again
      await agentRegistry.incrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(2);
    });
    
    it("Should decrement agent workload", async function () {
      // Decrement workload
      await agentRegistry.decrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(1);
      
      // Decrement again
      await agentRegistry.decrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
    });
    
    it("Should prevent decrementing zero workload", async function () {
      await expect(
        agentRegistry.decrementWorkload(agent1.address)
      ).to.be.revertedWith("Workload already at minimum");
    });
    
    it("Should reset agent workload", async function () {
      // Increment workload first
      await agentRegistry.incrementWorkload(agent1.address);
      await agentRegistry.incrementWorkload(agent1.address);
      await agentRegistry.incrementWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(3);
      
      // Reset workload
      await agentRegistry.resetWorkload(agent1.address);
      expect(await agentRegistry.agentWorkload(agent1.address)).to.equal(0);
    });
  });
  
  describe("Agent Queries", function () {
    it("Should get all registered agents", async function () {
      // Register another agent
      await agentRegistry.registerAgent(
        agent3.address,
        "Test Agent 3",
        "ipfs://QmAgentMetadata3",
        "https://api.agent3.example.com",
        3 // Evaluator type
      );
      
      // Get all agents
      const agents = await agentRegistry.getAllAgents();
      
      // Should include all registered agents
      expect(agents).to.include(agent1.address);
      expect(agents).to.include(agent2.address);
      expect(agents).to.include(agent3.address);
      
      // Should not include non-registered agents
      expect(agents).to.not.include(nonOwner.address);
    });
    
    it("Should get agent count", async function () {
      const count = await agentRegistry.getAgentCount();
      expect(count).to.equal(3); // Three agents registered so far
    });
    
    it("Should check if agent is active", async function () {
      // All agents should be active
      expect(await agentRegistry.isActiveAgent(agent1.address)).to.be.true;
      expect(await agentRegistry.isActiveAgent(agent2.address)).to.be.true;
      expect(await agentRegistry.isActiveAgent(agent3.address)).to.be.true;
      
      // Non-registered agent should not be active
      expect(await agentRegistry.isActiveAgent(nonOwner.address)).to.be.false;
      
      // Deactivate an agent
      await agentRegistry.deactivateAgent(agent3.address);
      expect(await agentRegistry.isActiveAgent(agent3.address)).to.be.false;
    });
    
    it("Should get agent type", async function () {
      expect(await agentRegistry.getAgentType(agent1.address)).to.equal(1); // LLM
      expect(await agentRegistry.getAgentType(agent2.address)).to.equal(1); // LLM
      expect(await agentRegistry.getAgentType(agent3.address)).to.equal(3); // Evaluator
      
      await expect(
        agentRegistry.getAgentType(nonOwner.address)
      ).to.be.revertedWith("Agent not registered");
    });
  });
  
  describe("Authentication", function () {
    it("Should authenticate agent with valid signature", async function () {
      const messageHash = ethers.id("test-message");
      const nonce = 123;
      
      // Sign message with agent1's private key
      const signature = await agent1.signMessage(ethers.getBytes(messageHash));
      
      // Authenticate
      const tx = await agentRegistry.authenticateAgent(messageHash, signature, nonce);
      const receipt = await tx.wait();
      
      // Since the function returns a boolean, we just verify it doesn't revert
      expect(receipt.status).to.equal(1);
    });
    
    it("Should prevent replay attacks", async function () {
      const messageHash = ethers.id("another-test-message");
      const nonce = 456;
      
      // Sign message with agent1's private key
      const signature = await agent1.signMessage(ethers.getBytes(messageHash));
      
      // First authentication should succeed
      await agentRegistry.authenticateAgent(messageHash, signature, nonce);
      
      // Second authentication with same nonce should fail
      await expect(
        agentRegistry.authenticateAgent(messageHash, signature, nonce)
      ).to.be.revertedWith("Nonce already used");
    });
  });
  
  describe("Learning State Management", function () {
    it("Should record task scores", async function () {
      const taskId = ethers.id("test-task-1");
      const score = 85;
      
      await agentRegistry.recordTaskScore(agent1.address, taskId, score);
      
      // Get recent tasks
      const [taskIds, scores] = await agentRegistry.getAgentRecentTasks(agent1.address);
      
      expect(taskIds).to.include(taskId);
      expect(scores[taskIds.indexOf(taskId)]).to.equal(score);
    });
    
    it("Should maintain a fixed-size FIFO queue for task history", async function () {
      // Get max recent tasks constant
      const maxTasks = await agentRegistry.MAX_RECENT_TASKS();
      
      // Fill the queue with more than the maximum
      for (let i = 0; i < Number(maxTasks) + 5; i++) {
        const taskId = ethers.id(`overflow-task-${i}`);
        await agentRegistry.recordTaskScore(agent1.address, taskId, 75);
      }
      
      // Get recent tasks
      const [taskIds, scores] = await agentRegistry.getAgentRecentTasks(agent1.address);
      
      // Should only have max tasks
      expect(taskIds.length).to.equal(Number(maxTasks));
      
      // First tasks should have been removed
      const firstTaskId = ethers.id("overflow-task-0");
      expect(taskIds).to.not.include(firstTaskId);
      
      // Last tasks should be present
      const lastTaskId = ethers.id(`overflow-task-${Number(maxTasks) + 4}`);
      expect(taskIds).to.include(lastTaskId);
    });
    
    it("Should get agent learning state", async function () {
      // Get learning state
      const learningState = await agentRegistry.getAgentLearningState(agent1.address);
      
      // Verify learning state structure
      expect(learningState.reputation).to.equal((await agentRegistry.agents(agent1.address)).reputation);
      expect(learningState.workload).to.equal(await agentRegistry.agentWorkload(agent1.address));
      
      // Verify capabilities
      const [tags, weights] = await agentRegistry.getCapabilities(agent1.address);
      expect(learningState.capabilityTags).to.deep.equal(tags);
      expect(learningState.capabilityWeights).to.deep.equal(weights);
      
      // Verify recent tasks
      const [recentTaskIds, recentScores] = await agentRegistry.getAgentRecentTasks(agent1.address);
      expect(learningState.recentTaskIds).to.deep.equal(recentTaskIds);
      expect(learningState.recentScores).to.deep.equal(recentScores);
    });
  });
});