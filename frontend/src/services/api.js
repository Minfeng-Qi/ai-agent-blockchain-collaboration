import axios from 'axios';
import { serviceMonitor } from './serviceMonitor';
import { enhancedMockData } from './enhancedMockData';

// API 基础URL
const API_BASE_URL = 'http://localhost:8001';

// 智能Mock数据配置
let USE_MOCK_DATA = false; // 初始状态，将由服务监控器动态控制

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10秒超时
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理错误响应
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 模拟数据生成器
const mockDataGenerator = {
  // 生成模拟代理数据
  generateMockAgents() {
    const currentDate = new Date();
    return {
      agents: [
        {
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          name: 'DataAnalysisAgent',
          reputation: 85,
          capabilities: ['data_analysis', 'text_generation', 'classification'],
          tasks_completed: 42,
          average_score: 4.7,
          registration_date: new Date(currentDate.getTime() - 90 * 86400000).toISOString()
        },
        {
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          name: 'TextGenerationAgent',
          reputation: 75,
          capabilities: ['text_generation', 'translation', 'summarization'],
          tasks_completed: 28,
          average_score: 4.3,
          registration_date: new Date(currentDate.getTime() - 60 * 86400000).toISOString()
        },
        {
          agent_id: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
          name: 'ClassificationAgent',
          reputation: 80,
          capabilities: ['classification', 'data_analysis'],
          tasks_completed: 35,
          average_score: 4.5,
          registration_date: new Date(currentDate.getTime() - 75 * 86400000).toISOString()
        },
        {
          agent_id: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65',
          name: 'TranslationAgent',
          reputation: 78,
          capabilities: ['translation', 'text_generation'],
          tasks_completed: 31,
          average_score: 4.4,
          registration_date: new Date(currentDate.getTime() - 45 * 86400000).toISOString()
        },
        {
          agent_id: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc',
          name: 'ImageRecognitionAgent',
          reputation: 82,
          capabilities: ['image_recognition', 'classification'],
          tasks_completed: 37,
          average_score: 4.6,
          registration_date: new Date(currentDate.getTime() - 30 * 86400000).toISOString()
        }
      ],
      total: 5
    };
  },

  // 生成模拟代理详情
  generateMockAgentDetails(agentId) {
    const mockAgents = this.generateMockAgents().agents;
    const agent = mockAgents.find(a => a.agent_id === agentId) || mockAgents[0];
    
    return {
      ...agent,
      description: `${agent.name} specializes in ${agent.capabilities.join(', ')}.`,
      confidence_factor: 0.85,
      risk_tolerance: 0.6,
      task_history: [
        {
          task_id: 'task_123',
          title: 'Market Analysis',
          completed_at: new Date(Date.now() - 2 * 86400000).toISOString(),
          score: 4.9
        },
        {
          task_id: 'task_456',
          title: 'Customer Feedback Analysis',
          completed_at: new Date(Date.now() - 7 * 86400000).toISOString(),
          score: 4.7
        },
        {
          task_id: 'task_789',
          title: 'Product Classification',
          completed_at: new Date(Date.now() - 14 * 86400000).toISOString(),
          score: 4.5
        }
      ],
      learning_events: [
        {
          event_id: 'event_789',
          event_type: 'task_completion',
          timestamp: new Date(Date.now() - 2 * 86400000).toISOString(),
          data: 'Completed task with high accuracy'
        },
        {
          event_id: 'event_012',
          event_type: 'capability_acquisition',
          timestamp: new Date(Date.now() - 20 * 86400000).toISOString(),
          data: `Acquired new capability: ${agent.capabilities[0]}`
        }
      ]
    };
  },

  // 生成模拟任务数据
  generateMockTasks() {
    const currentDate = new Date();
    const tasks = [
      {
        task_id: 'task_123',
        title: 'Analyze market trends',
        description: 'Analyze market trends for Q3 2023',
        type: 'data_analysis',
        status: 'completed',
        created_at: new Date(currentDate.getTime() - 7 * 86400000).toISOString(),
        completed_at: new Date(currentDate.getTime() - 5 * 86400000).toISOString(),
        assigned_agent: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        required_capabilities: ['data_analysis'],
        reward: 0.5
      },
      {
        task_id: 'task_456',
        title: 'Generate quarterly report',
        description: 'Generate quarterly financial report',
        type: 'text_generation',
        status: 'assigned',
        created_at: new Date(currentDate.getTime() - 5 * 86400000).toISOString(),
        assigned_agent: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        required_capabilities: ['text_generation', 'data_analysis'],
        reward: 0.3
      },
      {
        task_id: 'task_789',
        title: 'Classify customer feedback',
        description: 'Classify customer feedback into categories',
        type: 'classification',
        status: 'open',
        created_at: new Date(currentDate.getTime() - 3 * 86400000).toISOString(),
        required_capabilities: ['classification'],
        reward: 0.15
      },
      {
        task_id: 'task_101',
        title: 'Translate product documentation',
        description: 'Translate product documentation from English to Spanish',
        type: 'translation',
        status: 'completed',
        created_at: new Date(currentDate.getTime() - 10 * 86400000).toISOString(),
        completed_at: new Date(currentDate.getTime() - 8 * 86400000).toISOString(),
        assigned_agent: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65',
        required_capabilities: ['translation'],
        reward: 0.25
      },
      {
        task_id: 'task_102',
        title: 'Identify objects in images',
        description: 'Identify and label objects in a set of product images',
        type: 'image_recognition',
        status: 'assigned',
        created_at: new Date(currentDate.getTime() - 4 * 86400000).toISOString(),
        assigned_agent: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc',
        required_capabilities: ['image_recognition'],
        reward: 0.35
      },
      {
        task_id: 'task_103',
        title: 'Summarize research papers',
        description: 'Create concise summaries of AI research papers',
        type: 'summarization',
        status: 'open',
        created_at: new Date(currentDate.getTime() - 2 * 86400000).toISOString(),
        required_capabilities: ['text_generation', 'summarization'],
        reward: 0.4
      },
      {
        task_id: 'task_104',
        title: 'Analyze customer sentiment',
        description: 'Analyze sentiment in customer reviews',
        type: 'data_analysis',
        status: 'completed',
        created_at: new Date(currentDate.getTime() - 15 * 86400000).toISOString(),
        completed_at: new Date(currentDate.getTime() - 14 * 86400000).toISOString(),
        assigned_agent: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        required_capabilities: ['data_analysis', 'classification'],
        reward: 0.45
      },
      {
        task_id: 'task_105',
        title: 'Generate product descriptions',
        description: 'Create engaging descriptions for new products',
        type: 'text_generation',
        status: 'completed',
        created_at: new Date(currentDate.getTime() - 20 * 86400000).toISOString(),
        completed_at: new Date(currentDate.getTime() - 19 * 86400000).toISOString(),
        assigned_agent: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        required_capabilities: ['text_generation'],
        reward: 0.3
      }
    ];

    return { tasks, total: tasks.length };
  },

  // 生成模拟任务详情
  generateMockTaskDetails(taskId) {
    const mockTasks = this.generateMockTasks().tasks;
    const task = mockTasks.find(t => t.task_id === taskId) || mockTasks[0];
    
    return {
      ...task,
      deadline: new Date(Date.now() + 7 * 86400000).toISOString(),
      complexity: Math.floor(Math.random() * 5) + 1,
      tags: task.required_capabilities,
      bids: [
        {
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          bid_amount: task.reward * 0.9,
          timestamp: new Date(Date.now() - 1 * 86400000).toISOString(),
          confidence: 0.85
        },
        {
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          bid_amount: task.reward * 0.95,
          timestamp: new Date(Date.now() - 1.5 * 86400000).toISOString(),
          confidence: 0.8
        }
      ],
      history: [
        {
          action: 'created',
          timestamp: task.created_at,
          details: 'Task created'
        },
        {
          action: 'bid_placed',
          timestamp: new Date(Date.now() - 1.5 * 86400000).toISOString(),
          details: 'Bid placed by agent 0x3C44...',
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
        },
        {
          action: 'bid_placed',
          timestamp: new Date(Date.now() - 1 * 86400000).toISOString(),
          details: 'Bid placed by agent 0x7099...',
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
        }
      ]
    };
  },

  // 生成模拟学习事件数据
  generateMockLearningEvents() {
    const currentDate = new Date();
    const events = [
      {
        event_id: 'event_001',
        agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        event_type: 'task_completion',
        data: {
          task_id: 'task_123',
          performance_score: 4.8,
          insights_gained: ['market trend analysis improved', 'sentiment detection enhanced']
        },
        timestamp: new Date(currentDate.getTime() - 5 * 86400000).toISOString(),
        transaction_hash: '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234'
      },
      {
        event_id: 'event_002',
        agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        event_type: 'training',
        data: {
          model_version: 'v2.1',
          training_duration: 3600,
          performance_improvement: 0.15
        },
        timestamp: new Date(currentDate.getTime() - 7 * 86400000).toISOString(),
        transaction_hash: '0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678'
      },
      {
        event_id: 'event_003',
        agent_id: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
        event_type: 'capability_acquisition',
        data: {
          capability: 'image_recognition',
          source: 'marketplace',
          cost: 0.25
        },
        timestamp: new Date(currentDate.getTime() - 10 * 86400000).toISOString(),
        transaction_hash: '0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012'
      }
    ];

    return { events, total: events.length };
  },
  
  // 生成模拟协作对话数据
  generateMockCollaborationConversation(collaborationId) {
    const mockAgents = this.generateMockAgents().agents;
    const mockTasks = this.generateMockTasks().tasks;
    const task = mockTasks[0];
    
    return {
      collaboration_id: collaborationId || "collab_" + Math.random().toString(36).substring(2, 15),
      task_id: task.task_id,
      task_title: task.title,
      status: "completed",
      agents: mockAgents.slice(0, 4).map(agent => ({
        agent_id: agent.agent_id,
        name: agent.name,
        capabilities: agent.capabilities,
        reputation: agent.reputation
      })),
      conversation: [
        {
          role: "system",
          content: "你们是一个多智能体协作团队，需要共同完成用户指定的任务。每个智能体都有自己的专长和能力。请根据任务需求，进行合理分工，并通过协作完成任务。"
        },
        {
          role: "user",
          content: `任务: ${task.title}\n\n${task.description}`
        },
        {
          role: "assistant",
          content: `Agent1: 大家好，我们收到了一个新任务："${task.title}"。任务描述是："${task.description}"。让我们先分析一下这个任务需要哪些能力，然后进行分工。\n\nAgent2: 我擅长文本生成和总结，可以负责最终报告的撰写。\n\nAgent3: 我的专长是数据分析和分类，可以处理数据分析部分。\n\nAgent4: 我可以提供翻译支持，如果需要处理多语言内容的话。`
        },
        {
          role: "user",
          content: "请继续讨论，直到解决任务。当前进度: 20%"
        },
        {
          role: "assistant",
          content: `Agent1: 好的，让我们开始工作。首先，我们需要收集相关数据。Agent3，你能开始进行初步数据收集和分析吗？\n\nAgent3: 已经开始收集数据。初步分析显示，我们有以下几个关键点需要关注：[数据点1]、[数据点2]和[数据点3]。这些数据显示出明显的趋势。\n\nAgent2: 根据Agent3提供的数据点，我可以开始构建报告框架。我建议我们将报告分为以下几个部分：背景介绍、数据分析、结论和建议。\n\nAgent4: 我注意到有些参考资料是其他语言的，我已经将它们翻译成中文，以便我们所有人都能理解。`
        },
        {
          role: "user",
          content: "请继续讨论，直到解决任务。当前进度: 40%"
        },
        {
          role: "assistant",
          content: `Agent3: 我已经完成了深入数据分析，发现了几个重要模式：首先，[发现1]；其次，[发现2]；最后，[发现3]。这些发现对我们的任务有重要意义。\n\nAgent1: 非常好的分析，Agent3。基于这些发现，我认为我们应该重点关注[重点领域]，这将帮助我们更有效地解决问题。\n\nAgent2: 我已经根据Agent3的分析和Agent1的建议，完成了报告的初稿。报告包含了所有关键发现和建议。\n\nAgent4: 我检查了报告中的专业术语，确保它们使用正确且一致。同时，我准备了一个术语表，以便于理解。`
        },
        {
          role: "user",
          content: "请继续讨论，直到解决任务。当前进度: 60%"
        },
        {
          role: "assistant",
          content: `Agent1: 我们已经取得了很好的进展。现在让我们审查一下报告，确保没有遗漏任何重要内容。\n\nAgent2: 我刚刚完成了报告的修订版本，增加了更多详细的分析和具体建议。\n\nAgent3: 我检查了报告中的数据分析部分，所有数据和图表都是准确的，解释也很清晰。\n\nAgent4: 我对整个报告进行了语言润色，确保表达清晰、专业且易于理解。同时，我还准备了一个执行摘要，突出报告的主要发现和建议。`
        },
        {
          role: "user",
          content: "请继续讨论，直到解决任务。当前进度: 80%"
        },
        {
          role: "assistant",
          content: `Agent1: 我们的报告已经接近完成。让我们做最后的检查和完善。\n\nAgent2: 我已经添加了结论部分，总结了我们的主要发现和建议。我认为报告现在已经很全面了。\n\nAgent3: 我再次验证了所有数据和分析，确保准确无误。同时，我添加了一些补充图表，使数据更直观。\n\nAgent4: 我完成了最终的校对和格式调整，确保报告的专业性和一致性。\n\nAgent1: 非常好！我认为我们已经成功完成了任务。最终报告全面分析了${task.title}，提供了有价值的见解和可行的建议。感谢大家的协作！`
        }
      ],
      ipfs_cid: "Qm" + Math.random().toString(36).substring(2, 46),
      ipfs_url: `http://localhost:8080/ipfs/Qm${Math.random().toString(36).substring(2, 46)}`,
      tx_hash: "0x" + Math.random().toString(36).substring(2, 66),
      timestamp: Date.now() / 1000
    };
  },

  // 生成模拟系统状态
  generateMockSystemStatus() {
    return {
      status: 'healthy',
      services: {
        api: 'up',
        blockchain: 'up'
      },
      blockchain_details: {
        connected: true,
        network_id: 1337,
        latest_block: 12345,
        contracts: {
          agent_registry: true,
          task_manager: true,
          learning: true
        }
      }
    };
  },

  // 生成模拟系统统计数据
  generateMockSystemStats() {
    return {
      agents: {
        total: 5,
        capabilities: {
          data_analysis: 2,
          text_generation: 2,
          image_recognition: 1,
          classification: 2,
          translation: 1,
          summarization: 1
        }
      },
      tasks: {
        total: 8,
        open: 2,
        assigned: 2,
        completed: 4
      },
      learning: {
        total_events: 3,
        event_types: {
          task_completion: 1,
          training: 1,
          capability_acquisition: 1
        }
      },
      blockchain: {
        transaction_count: 45,
        block_count: 12345,
        latest_block: 12345
      },
      timestamp: new Date().toISOString()
    };
  },

  // 生成模拟区块链交易数据
  generateMockTransactions() {
    const currentDate = new Date();
    const transactions = [
      {
        tx_hash: '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234',
        block_number: 12345,
        timestamp: new Date(currentDate.getTime() - 1 * 86400000).toISOString(),
        from_address: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        to_address: '0x0987654321098765432109876543210987654321',
        value: '1.5 ETH',
        gas_used: 21000,
        status: 'confirmed',
        event_type: 'TaskCreated',
        event_data: { task_id: 'task-123', reward: '1.5 ETH' }
      },
      {
        tx_hash: '0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678',
        block_number: 12344,
        timestamp: new Date(currentDate.getTime() - 2 * 86400000).toISOString(),
        from_address: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        to_address: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        value: '0.5 ETH',
        gas_used: 35000,
        status: 'confirmed',
        event_type: 'AgentRegistered',
        event_data: { agent_id: 'agent-456' }
      },
      {
        tx_hash: '0x1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d',
        block_number: 12343,
        timestamp: new Date(currentDate.getTime() - 3 * 86400000).toISOString(),
        from_address: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
        to_address: '0x0987654321098765432109876543210987654321',
        value: '0.2 ETH',
        gas_used: 45000,
        status: 'confirmed',
        event_type: 'TaskCompleted',
        event_data: { task_id: 'task-122', agent_id: 'agent-456' }
      },
      {
        tx_hash: '0x5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h',
        block_number: 12342,
        timestamp: new Date(currentDate.getTime() - 4 * 86400000).toISOString(),
        from_address: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65',
        to_address: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        value: '0.3 ETH',
        gas_used: 30000,
        status: 'confirmed',
        event_type: 'LearningEvent',
        event_data: { agent_id: 'agent-456', event_type: 'training' }
      },
      {
        tx_hash: '0x9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l',
        block_number: 12341,
        timestamp: new Date(currentDate.getTime() - 5 * 86400000).toISOString(),
        from_address: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc',
        to_address: '0x0987654321098765432109876543210987654321',
        value: '0.1 ETH',
        gas_used: 25000,
        status: 'confirmed',
        event_type: 'TaskAssigned',
        event_data: { task_id: 'task-124', agent_id: 'agent-789' }
      }
    ];

    return { transactions, total: transactions.length };
  },
  
  // Generate mock blocks data
  generateMockBlocks() {
    const currentDate = new Date();
    const blocks = [
      {
        block_number: 12345,
        timestamp: new Date(currentDate.getTime() - 1 * 60000).toISOString(),
        hash: '0xb1ock12345b1ock12345b1ock12345b1ock12345b1ock12345b1ock12345b1ock',
        parent_hash: '0xb1ock12344b1ock12344b1ock12344b1ock12344b1ock12344b1ock12344b1ock',
        miner: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        size: 24680,
        gas_used: 120000,
        gas_limit: 8000000,
        transaction_count: 3,
        transactions: [
          '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234'
        ]
      },
      {
        block_number: 12344,
        timestamp: new Date(currentDate.getTime() - 2 * 60000).toISOString(),
        hash: '0xb1ock12344b1ock12344b1ock12344b1ock12344b1ock12344b1ock12344b1ock',
        parent_hash: '0xb1ock12343b1ock12343b1ock12343b1ock12343b1ock12343b1ock12343b1ock',
        miner: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        size: 18540,
        gas_used: 95000,
        gas_limit: 8000000,
        transaction_count: 2,
        transactions: [
          '0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678'
        ]
      },
      {
        block_number: 12343,
        timestamp: new Date(currentDate.getTime() - 3 * 60000).toISOString(),
        hash: '0xb1ock12343b1ock12343b1ock12343b1ock12343b1ock12343b1ock12343b1ock',
        parent_hash: '0xb1ock12342b1ock12342b1ock12342b1ock12342b1ock12342b1ock12342b1ock',
        miner: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
        size: 22560,
        gas_used: 110000,
        gas_limit: 8000000,
        transaction_count: 1,
        transactions: [
          '0x1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d'
        ]
      },
      {
        block_number: 12342,
        timestamp: new Date(currentDate.getTime() - 4 * 60000).toISOString(),
        hash: '0xb1ock12342b1ock12342b1ock12342b1ock12342b1ock12342b1ock12342b1ock',
        parent_hash: '0xb1ock12341b1ock12341b1ock12341b1ock12341b1ock12341b1ock12341b1ock',
        miner: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65',
        size: 16780,
        gas_used: 85000,
        gas_limit: 8000000,
        transaction_count: 1,
        transactions: [
          '0x5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h'
        ]
      },
      {
        block_number: 12341,
        timestamp: new Date(currentDate.getTime() - 5 * 60000).toISOString(),
        hash: '0xb1ock12341b1ock12341b1ock12341b1ock12341b1ock12341b1ock12341b1ock',
        parent_hash: '0xb1ock12340b1ock12340b1ock12340b1ock12340b1ock12340b1ock12340b1ock',
        miner: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc',
        size: 14320,
        gas_used: 75000,
        gas_limit: 8000000,
        transaction_count: 1,
        transactions: [
          '0x9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l'
        ]
      }
    ];
    
    return { blocks, total: blocks.length };
  },
  
  // Generate mock events data
  generateMockEvents() {
    const currentDate = new Date();
    const events = [
      {
        event_id: 'event_001',
        contract_address: '0x0987654321098765432109876543210987654321',
        event_name: 'TaskCreated',
        block_number: 12345,
        tx_hash: '0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234',
        timestamp: new Date(currentDate.getTime() - 1 * 86400000).toISOString(),
        data: { task_id: 'task-123', reward: '1.5 ETH' }
      },
      {
        event_id: 'event_002',
        contract_address: '0x0987654321098765432109876543210987654321',
        event_name: 'AgentRegistered',
        block_number: 12344,
        tx_hash: '0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678',
        timestamp: new Date(currentDate.getTime() - 2 * 86400000).toISOString(),
        data: { agent_id: 'agent-456' }
      },
      {
        event_id: 'event_003',
        contract_address: '0x0987654321098765432109876543210987654321',
        event_name: 'TaskCompleted',
        block_number: 12343,
        tx_hash: '0x1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d',
        timestamp: new Date(currentDate.getTime() - 3 * 86400000).toISOString(),
        data: { task_id: 'task-122', agent_id: 'agent-456' }
      },
      {
        event_id: 'event_004',
        contract_address: '0x0987654321098765432109876543210987654321',
        event_name: 'LearningEvent',
        block_number: 12342,
        tx_hash: '0x5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h5e6f7g8h',
        timestamp: new Date(currentDate.getTime() - 4 * 86400000).toISOString(),
        data: { agent_id: 'agent-456', event_type: 'training' }
      },
      {
        event_id: 'event_005',
        contract_address: '0x0987654321098765432109876543210987654321',
        event_name: 'TaskAssigned',
        block_number: 12341,
        tx_hash: '0x9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l9i8j7k6l',
        timestamp: new Date(currentDate.getTime() - 5 * 86400000).toISOString(),
        data: { task_id: 'task-124', agent_id: 'agent-789' }
      }
    ];
    
    return { events, total: events.length };
  }
};

// 服务状态监控和智能回退
serviceMonitor.addStatusListener((isAvailable, previousStatus) => {
  USE_MOCK_DATA = !isAvailable;
  console.log(`API service status changed: Backend ${isAvailable ? 'available' : 'unavailable'}, using ${USE_MOCK_DATA ? 'mock' : 'real'} data`);
});

// 智能API请求包装器
class SmartAPIClient {
  async request(requestFn, mockFallback, options = {}) {
    const { useCache = false, cacheKey = '', forceReal = false } = options;
    
    // 如果强制使用真实API或者服务可用，尝试真实请求
    if (forceReal || serviceMonitor.isBackendAvailable()) {
      try {
        const result = await requestFn();
        // 在结果中标记数据源
        if (result && typeof result === 'object') {
          result._dataSource = 'backend';
          result._timestamp = new Date().toISOString();
        }
        return result;
      } catch (error) {
        console.warn('Backend request failed, falling back to mock data:', error.message);
        // 实时更新服务状态
        serviceMonitor.updateServiceStatus(false);
      }
    }
    
    // 使用Mock数据回退
    console.log('Using enhanced mock data fallback');
    const mockResult = await mockFallback();
    if (mockResult && typeof mockResult === 'object') {
      mockResult._dataSource = 'mock';
      mockResult._timestamp = new Date().toISOString();
    }
    return mockResult;
  }
  
  // 批量请求处理
  async batchRequest(requests) {
    const results = await Promise.allSettled(requests.map(req => 
      this.request(req.requestFn, req.mockFallback, req.options)
    ));
    
    return results.map((result, index) => ({
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason : null,
      request: requests[index]
    }));
  }
}

const smartAPI = new SmartAPIClient();

// 统一API服务
export const api = {
  // 代理协作相关
  createCollaboration: async (collaborationData) => {
    try {
      const response = await apiClient.post('/collaboration/collaboration', collaborationData);
      return response.data;
    } catch (error) {
      console.error('Error creating collaboration:', error);
      throw error;
    }
  },
  
  runCollaboration: async (collaborationId, collaborationData) => {
    try {
      const response = await apiClient.post(`/collaboration/collaboration/${collaborationId}/run`, collaborationData);
      return response.data;
    } catch (error) {
      console.error(`Error running collaboration ${collaborationId}:`, error);
      throw error;
    }
  },
  
  getCollaboration: async (collaborationId) => {
    try {
      const response = await apiClient.get(`/collaboration/collaboration/${collaborationId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching collaboration ${collaborationId}:`, error);
      throw error;
    }
  },
  
  getCollaborationConversation: async (collaborationId) => {
    try {
      const response = await apiClient.get(`/collaboration/collaboration/${collaborationId}/conversation`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching conversation for collaboration ${collaborationId}:`, error);
      if (USE_MOCK_DATA) {
        console.log(`Using mock conversation data for collaboration ${collaborationId}`);
        return mockDataGenerator.generateMockCollaborationConversation(collaborationId);
      }
      throw error;
    }
  },
  
  getConversationByIpfs: async (ipfsCid) => {
    try {
      const response = await apiClient.get(`/collaboration/collaboration/ipfs/${ipfsCid}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching conversation from IPFS ${ipfsCid}:`, error);
      if (USE_MOCK_DATA) {
        console.log(`Using mock conversation data for IPFS CID ${ipfsCid}`);
        return mockDataGenerator.generateMockCollaborationConversation();
      }
      throw error;
    }
  },
  // 代理相关
  getAgents: async (options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get('/agents/');
        return response.data;
      },
      async () => enhancedMockData.generateEnhancedAgents(),
      options
    );
  },
  
  getAgentById: async (agentId, options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get(`/agents/${agentId}`);
        return response.data;
      },
      async () => enhancedMockData.generateAgentStatistics(agentId),
      options
    );
  },
  
  createAgent: async (agentData) => {
    try {
      const response = await apiClient.post('/agents/', agentData);
      return response.data;
    } catch (error) {
      console.error('Error creating agent:', error);
      throw error;
    }
  },
  
  updateAgent: async (agentId, agentData) => {
    try {
      const response = await apiClient.put(`/agents/${agentId}`, agentData);
      return response.data;
    } catch (error) {
      console.error(`Error updating agent ${agentId}:`, error);
      throw error;
    }
  },
  
  deleteAgent: async (agentId) => {
    try {
      const response = await apiClient.delete(`/agents/${agentId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting agent ${agentId}:`, error);
      throw error;
    }
  },

  // 新增的Agent详细信息API
  getAgentStatistics: async (agentId, options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get(`/agents/${agentId}/statistics`);
        return response.data;
      },
      async () => enhancedMockData.generateAgentStatistics(agentId),
      options
    );
  },

  getAgentPerformanceHistory: async (agentId, period = '7d', metric = null, options = {}) => {
    return smartAPI.request(
      async () => {
        const params = { period };
        if (metric) params.metric = metric;
        const response = await apiClient.get(`/agents/${agentId}/performance-history`, { params });
        return response.data;
      },
      async () => ({
        agent_id: agentId,
        period,
        data: enhancedMockData.generatePerformanceHistory(30),
        source: 'enhanced_mock'
      }),
      options
    );
  },

  getAgentTaskTypes: async (agentId, options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get(`/agents/${agentId}/task-types`);
        return response.data;
      },
      async () => enhancedMockData.generateTaskTypeDistribution(agentId),
      options
    );
  },

  getAgentTasks: async (agentId, filters = {}) => {
    try {
      const response = await apiClient.get(`/agents/${agentId}/tasks`, { params: filters });
      return response.data;
    } catch (error) {
      console.error(`Error fetching agent tasks for ${agentId}:`, error);
      throw error;
    }
  },

  getAgentLearning: async (agentId, filters = {}, options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get(`/agents/${agentId}/learning`, { params: filters });
        return response.data;
      },
      async () => enhancedMockData.generateLearningEvents(agentId),
      options
    );
  },
  
  // 任务相关
  getTasks: async (filters = {}, options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get('/tasks/', { params: filters });
        return response.data;
      },
      async () => enhancedMockData.generateEnhancedTasks(),
      options
    );
  },
  
  getTaskById: async (taskId) => {
    try {
      const response = await apiClient.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching task ${taskId}:`, error);
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for task ${taskId}`);
        return mockDataGenerator.generateMockTaskDetails(taskId);
      }
      throw error;
    }
  },
  
  createTask: async (taskData) => {
    try {
      const response = await apiClient.post('/tasks', taskData);
      return response.data;
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },
  
  updateTask: async (taskId, taskData) => {
    try {
      const response = await apiClient.put(`/tasks/${taskId}`, taskData);
      return response.data;
    } catch (error) {
      console.error(`Error updating task ${taskId}:`, error);
      throw error;
    }
  },
  
  deleteTask: async (taskId) => {
    try {
      const response = await apiClient.delete(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting task ${taskId}:`, error);
      throw error;
    }
  },
  
  assignTask: async (taskId, agentId) => {
    try {
      const response = await apiClient.post(`/tasks/${taskId}/assign`, { agent_id: agentId });
      return response.data;
    } catch (error) {
      console.error(`Error assigning task ${taskId} to agent ${agentId}:`, error);
      throw error;
    }
  },
  
  completeTask: async (taskId, resultData) => {
    try {
      const response = await apiClient.post(`/tasks/${taskId}/complete`, resultData);
      return response.data;
    } catch (error) {
      console.error(`Error completing task ${taskId}:`, error);
      throw error;
    }
  },
  
  // 学习相关
  getLearningEvents: async (filters = {}) => {
    try {
      const response = await apiClient.get('/learning', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching learning events:', error);
      if (USE_MOCK_DATA) {
        console.log('Using mock learning events data');
        return mockDataGenerator.generateMockLearningEvents();
      }
      throw error;
    }
  },
  
  getLearningEventById: async (eventId) => {
    try {
      const response = await apiClient.get(`/learning/${eventId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching learning event ${eventId}:`, error);
      throw error;
    }
  },
  
  createLearningEvent: async (eventData) => {
    try {
      const response = await apiClient.post('/learning', eventData);
      return response.data;
    } catch (error) {
      console.error('Error creating learning event:', error);
      throw error;
    }
  },
  
  // 区块链交易相关
  getTransactions: async (filters = {}) => {
    try {
      const response = await apiClient.get('/blockchain/transactions', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      console.log('Using mock transactions data due to connection error');
      return mockDataGenerator.generateMockTransactions();
    }
  },
  
  getTransactionByHash: async (hash) => {
    try {
      const response = await apiClient.get(`/blockchain/transactions/${hash}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching transaction ${hash}:`, error);
      throw error;
    }
  },
  
  getBlockByNumber: async (blockNumber) => {
    try {
      const response = await apiClient.get(`/blockchain/blocks/${blockNumber}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching block ${blockNumber}:`, error);
      throw error;
    }
  },
  
  getContractEvents: async (contractAddress, eventName, filters = {}) => {
    try {
      const response = await apiClient.get(`/blockchain/events/${contractAddress}/${eventName}`, { params: filters });
      return response.data;
    } catch (error) {
      console.error(`Error fetching events for contract ${contractAddress}:`, error);
      throw error;
    }
  },
  
  getBlockchainStats: async () => {
    try {
      const response = await apiClient.get('/blockchain/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching blockchain stats:', error);
      console.log('Using mock blockchain stats data due to connection error');
      // 返回mock数据，表示未连接状态
      return {
        transaction_count: 0,
        block_count: 0,
        latest_block: 0,
        avg_block_time: 0.0,
        avg_transactions_per_block: 0.0,
        agent_count: 0,
        task_count: 0,
        learning_event_count: 0,
        connected: false
      };
    }
  },
  
  // 系统相关
  getSystemStatus: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system status:', error);
      if (USE_MOCK_DATA) {
        console.log('Using mock system status data');
        return mockDataGenerator.generateMockSystemStatus();
      }
      throw error;
    }
  },

  getSystemStats: async (options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get('/stats');
        return response.data;
      },
      async () => enhancedMockData.generateSystemAnalytics(),
      options
    );
  },

  // 服务监控和状态管理
  getServiceStatus: () => {
    return {
      backend_available: serviceMonitor.isBackendAvailable(),
      status_info: serviceMonitor.getStatusInfo(),
      data_source: serviceMonitor.isBackendAvailable() ? 'backend' : 'mock'
    };
  },

  refreshServiceStatus: async () => {
    return await serviceMonitor.refreshStatus();
  },

  // 系统分析和监控
  getSystemAnalytics: async (options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get('/analytics/overview');
        return response.data;
      },
      async () => enhancedMockData.generateSystemAnalytics(),
      options
    );
  },

  // 协作功能增强
  getCollaborations: async (options = {}) => {
    return smartAPI.request(
      async () => {
        const response = await apiClient.get('/collaboration/collaborations');
        return response.data;
      },
      async () => enhancedMockData.generateCollaborationData(),
      options
    );
  },

  // 批量数据获取 - 用于Dashboard等需要多种数据的页面
  getDashboardData: async () => {
    const requests = [
      {
        requestFn: async () => {
          const response = await apiClient.get('/agents/');
          return response.data;
        },
        mockFallback: async () => enhancedMockData.generateEnhancedAgents()
      },
      {
        requestFn: async () => {
          const response = await apiClient.get('/tasks/');
          return response.data;
        },
        mockFallback: async () => enhancedMockData.generateEnhancedTasks()
      },
      {
        requestFn: async () => {
          const response = await apiClient.get('/stats');
          return response.data;
        },
        mockFallback: async () => enhancedMockData.generateSystemAnalytics()
      }
    ];

    const results = await smartAPI.batchRequest(requests);
    
    return {
      agents: results[0].success ? results[0].data : null,
      tasks: results[1].success ? results[1].data : null,
      analytics: results[2].success ? results[2].data : null,
      success_rate: results.filter(r => r.success).length / results.length,
      data_source: serviceMonitor.isBackendAvailable() ? 'backend' : 'mock',
      timestamp: new Date().toISOString()
    };
  },

  // 实时数据更新检查
  checkForUpdates: async () => {
    if (!serviceMonitor.isBackendAvailable()) {
      return { has_updates: false, source: 'mock' };
    }

    try {
      const response = await apiClient.get('/system/updates');
      return response.data;
    } catch (error) {
      console.warn('Failed to check for updates:', error.message);
      return { has_updates: false, source: 'backend_error' };
    }
  }
};

// 导出服务监控器供组件使用
export { serviceMonitor };

// 为了向后兼容，保留这些导出
export const agentApi = {
  getAgents: api.getAgents,
  getAgentById: api.getAgentById,
  createAgent: api.createAgent,
  updateAgent: api.updateAgent,
  deleteAgent: api.deleteAgent,
  
  // 新增的详细信息API
  getAgentStatistics: api.getAgentStatistics,
  getAgentPerformanceHistory: api.getAgentPerformanceHistory,
  getAgentTaskTypes: api.getAgentTaskTypes,
  getAgentTasks: api.getAgentTasks,
  getAgentLearning: api.getAgentLearning
};

export const taskApi = {
  getTasks: api.getTasks,
  getTaskById: api.getTaskById,
  createTask: api.createTask,
  updateTask: api.updateTask,
  deleteTask: api.deleteTask,
  assignTask: api.assignTask,
  completeTask: api.completeTask
};

export const learningApi = {
  getLearningEvents: api.getLearningEvents,
  getLearningEventById: api.getLearningEventById,
  createLearningEvent: api.createLearningEvent
};

export const blockchainApi = {
  getTransactions: api.getTransactions,
  getTransactionByHash: api.getTransactionByHash,
  getBlockByNumber: api.getBlockByNumber,
  getContractEvents: api.getContractEvents,
  getBlockchainStats: api.getBlockchainStats,
  // Add mock data generator functions
  generateMockTransactions: mockDataGenerator.generateMockTransactions.bind(mockDataGenerator),
  generateMockBlocks: mockDataGenerator.generateMockBlocks.bind(mockDataGenerator),
  generateMockEvents: mockDataGenerator.generateMockEvents.bind(mockDataGenerator),
  // Add missing API methods
  getBlocks: async (params) => {
    try {
      const response = await apiClient.get('/blockchain/blocks', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching blocks:', error);
      console.log('Using mock blocks data due to connection error');
      return mockDataGenerator.generateMockBlocks();
    }
  },
  getEvents: async (params) => {
    try {
      const response = await apiClient.get('/blockchain/events', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching events:', error);
      console.log('Using mock events data due to connection error');
      return mockDataGenerator.generateMockEvents();
    }
  }
};

export const systemApi = {
  getSystemStatus: api.getSystemStatus,
  getSystemStats: api.getSystemStats
};

export const collaborationApi = {
  createCollaboration: api.createCollaboration,
  runCollaboration: api.runCollaboration,
  getCollaboration: api.getCollaboration,
  getCollaborationConversation: api.getCollaborationConversation,
  getConversationByIpfs: api.getConversationByIpfs,
  // 添加模拟数据生成函数
  generateMockCollaborationConversation: mockDataGenerator.generateMockCollaborationConversation.bind(mockDataGenerator)
};