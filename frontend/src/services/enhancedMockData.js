/**
 * 增强的Mock数据生成器 - 为演示系统功能提供丰富的虚拟数据
 */

// 高级Agent能力定义
const AGENT_CAPABILITIES = {
  'data_analysis': {
    name: 'Data Analysis',
    description: 'Advanced data processing and statistical analysis',
    complexity: 4,
    demand: 0.8
  },
  'text_generation': {
    name: 'Text Generation',
    description: 'Natural language generation and content creation',
    complexity: 3,
    demand: 0.9
  },
  'image_recognition': {
    name: 'Image Recognition',
    description: 'Computer vision and image classification',
    complexity: 4,
    demand: 0.7
  },
  'classification': {
    name: 'Classification',
    description: 'Pattern recognition and categorization',
    complexity: 3,
    demand: 0.6
  },
  'translation': {
    name: 'Translation',
    description: 'Multi-language translation services',
    complexity: 4,
    demand: 0.5
  },
  'summarization': {
    name: 'Summarization',
    description: 'Content summarization and key point extraction',
    complexity: 3,
    demand: 0.7
  },
  'code_generation': {
    name: 'Code Generation',
    description: 'Automated code generation and refactoring',
    complexity: 5,
    demand: 0.8
  },
  'sentiment_analysis': {
    name: 'Sentiment Analysis',
    description: 'Emotion and sentiment detection in text',
    complexity: 3,
    demand: 0.6
  },
  'recommendation': {
    name: 'Recommendation',
    description: 'Intelligent recommendation systems',
    complexity: 4,
    demand: 0.7
  },
  'optimization': {
    name: 'Optimization',
    description: 'Resource and process optimization',
    complexity: 5,
    demand: 0.6
  }
};

// 任务类型定义
const TASK_TYPES = {
  'market_analysis': {
    name: 'Market Analysis',
    description: 'Analyze market trends and consumer behavior',
    required_capabilities: ['data_analysis', 'text_generation'],
    avg_reward: 0.8,
    complexity: 4
  },
  'content_creation': {
    name: 'Content Creation',
    description: 'Create marketing content and articles',
    required_capabilities: ['text_generation', 'sentiment_analysis'],
    avg_reward: 0.5,
    complexity: 3
  },
  'image_processing': {
    name: 'Image Processing',
    description: 'Process and analyze visual content',
    required_capabilities: ['image_recognition', 'classification'],
    avg_reward: 0.7,
    complexity: 4
  },
  'code_review': {
    name: 'Code Review',
    description: 'Review and optimize source code',
    required_capabilities: ['code_generation', 'classification'],
    avg_reward: 1.2,
    complexity: 5
  },
  'customer_support': {
    name: 'Customer Support',
    description: 'Provide intelligent customer service',
    required_capabilities: ['text_generation', 'sentiment_analysis', 'classification'],
    avg_reward: 0.4,
    complexity: 3
  },
  'translation_services': {
    name: 'Translation Services',
    description: 'Multi-language document translation',
    required_capabilities: ['translation', 'text_generation'],
    avg_reward: 0.6,
    complexity: 4
  },
  'recommendation_engine': {
    name: 'Recommendation Engine',
    description: 'Build personalized recommendation systems',
    required_capabilities: ['recommendation', 'data_analysis'],
    avg_reward: 1.0,
    complexity: 4
  },
  'optimization_consulting': {
    name: 'Optimization Consulting',
    description: 'Optimize business processes and workflows',
    required_capabilities: ['optimization', 'data_analysis'],
    avg_reward: 1.5,
    complexity: 5
  }
};

class EnhancedMockDataGenerator {
  constructor() {
    this.currentDate = new Date();
    this.agentNames = [
      'AnalyticsBot', 'ContentCraft', 'VisionAI', 'CodeMaster', 'TranslatePro',
      'DataWhiz', 'TextGenius', 'ImageSeer', 'PatternFinder', 'LanguageBridge',
      'SummaryBot', 'SentimentAI', 'RecommendAI', 'OptimizeCore', 'ClassifyPro',
      'InsightEngine', 'CreativeBot', 'TechSavvy', 'SmartLearner', 'EfficiencyAI'
    ];
  }

  /**
   * 生成增强的Agent数据 - 提供非常详细和真实的演示数据
   */
  generateEnhancedAgents(count = 15) {
    const agents = [];
    
    for (let i = 0; i < count; i++) {
      const capabilities = this.selectRandomCapabilities(2, 5);
      const tasksCompleted = Math.floor(Math.random() * 200) + 25;
      const avgScore = 3.2 + Math.random() * 1.6; // 3.2-4.8
      const successRate = 0.65 + Math.random() * 0.34; // 65%-99%
      const reputation = this.generateReputationScore();
      
      const agent = {
        agent_id: this.generateAgentId(),
        name: this.agentNames[i % this.agentNames.length] + (Math.floor(i / this.agentNames.length) + 1),
        reputation: reputation,
        capabilities: capabilities,
        capability_weights: this.generateCapabilityWeights(capabilities),
        capability_descriptions: this.generateCapabilityDescriptions(capabilities),
        
        // 任务和性能统计
        tasks_completed: tasksCompleted,
        tasks_in_progress: Math.floor(Math.random() * 4),
        tasks_failed: Math.floor(tasksCompleted * (1 - successRate) * 0.3),
        average_score: parseFloat(avgScore.toFixed(2)),
        score_history: this.generateScoreHistory(avgScore),
        success_rate: parseFloat(successRate.toFixed(3)),
        
        // 时间信息
        registration_date: new Date(this.currentDate.getTime() - Math.random() * 400 * 86400000).toISOString(),
        last_active: new Date(this.currentDate.getTime() - Math.random() * (i < 10 ? 3 : 14) * 86400000).toISOString(),
        next_available: new Date(this.currentDate.getTime() + Math.random() * 24 * 3600000).toISOString(),
        
        // 状态和分类
        status: Math.random() > 0.08 ? 'active' : (Math.random() > 0.5 ? 'busy' : 'offline'),
        specialization: this.getAgentSpecialization(capabilities),
        performance_tier: this.calculatePerformanceTier(reputation, avgScore),
        experience_level: this.calculateExperienceLevel(tasksCompleted, reputation),
        
        // 财务数据
        total_earnings: (tasksCompleted * 0.15 + Math.random() * 30).toFixed(3),
        earnings_history: this.generateEarningsHistory(),
        current_rate: (0.05 + Math.random() * 0.45).toFixed(3),
        
        // 技术指标
        response_time_avg: Math.floor(Math.random() * 180) + 30, // 30-210ms
        response_time_p95: Math.floor(Math.random() * 300) + 100, // 100-400ms
        uptime_percentage: (94 + Math.random() * 5.8).toFixed(2), // 94%-99.8%
        reliability_score: (0.85 + Math.random() * 0.14).toFixed(3),
        
        // 详细个人信息
        profile: {
          bio: this.generateAgentBio(capabilities),
          preferred_task_types: this.selectPreferredTaskTypes(capabilities),
          working_hours: this.generateWorkingHours(),
          timezone: this.selectRandomTimezone(),
          languages: this.selectRandomLanguages(),
          certifications: this.generateCertifications(capabilities)
        },
        
        // 协作信息
        collaboration_score: (0.7 + Math.random() * 0.3).toFixed(2),
        team_projects: Math.floor(Math.random() * 15) + 2,
        mentoring_provided: Math.floor(Math.random() * 8),
        feedback_rating: (4.1 + Math.random() * 0.8).toFixed(1),
        
        // 学习和成长
        learning_velocity: (0.3 + Math.random() * 0.7).toFixed(2),
        skill_progression: this.generateSkillProgression(capabilities),
        recent_achievements: this.generateRecentAchievements(),
        
        // 市场定位
        market_demand: this.calculateMarketDemand(capabilities),
        competitive_ranking: Math.floor(Math.random() * 50) + 1,
        client_retention: (0.75 + Math.random() * 0.24).toFixed(2),
        
        // 元数据
        data_freshness: new Date().toISOString(),
        last_updated: new Date(this.currentDate.getTime() - Math.random() * 2 * 3600000).toISOString()
      };
      
      agents.push(agent);
    }
    
    return {
      agents: agents.sort((a, b) => b.reputation - a.reputation),
      total: agents.length,
      active_count: agents.filter(a => a.status === 'active').length,
      average_reputation: (agents.reduce((sum, a) => sum + a.reputation, 0) / agents.length).toFixed(1),
      total_tasks_completed: agents.reduce((sum, a) => sum + a.tasks_completed, 0),
      generation_timestamp: new Date().toISOString(),
      source: 'enhanced_mock_v2'
    };
  }

  /**
   * 生成详细的Agent统计数据 - 超详细的个人档案
   */
  generateAgentStatistics(agentId) {
    const agent = this.generateEnhancedAgents(1).agents[0];
    agent.agent_id = agentId;
    
    const baseScore = parseFloat(agent.average_score);
    const totalTasks = agent.tasks_completed;
    const successRate = parseFloat(agent.success_rate) * 100;
    
    return {
      // 基础信息
      agent_id: agentId,
      name: agent.name,
      registration_date: agent.registration_date,
      last_active: agent.last_active,
      status: agent.status,
      
      // 声誉和信任
      reputation: agent.reputation,
      confidence_factor: Math.floor(agent.reputation * 0.8 + Math.random() * 20),
      risk_tolerance: Math.floor(50 + Math.random() * 40),
      trust_score: (0.75 + Math.random() * 0.24).toFixed(3),
      reputation_history: this.generateReputationHistory(agent.reputation),
      
      // 任务统计 - 超详细
      total_tasks: totalTasks,
      successful_tasks: Math.floor(totalTasks * successRate / 100),
      failed_tasks: Math.floor(totalTasks * (1 - successRate / 100)),
      cancelled_tasks: Math.floor(totalTasks * 0.05),
      success_rate: successRate,
      in_progress_tasks: agent.tasks_in_progress,
      pending_tasks: Math.floor(Math.random() * 3),
      
      // 任务类型分布
      task_type_distribution: this.generateDetailedTaskDistribution(agent.capabilities),
      preferred_task_complexity: this.calculatePreferredComplexity(agent.capabilities),
      
      // 性能指标 - 详细
      average_score: baseScore,
      score_breakdown: {
        quality: (baseScore * 0.9 + Math.random() * 0.2).toFixed(2),
        speed: (baseScore * 0.95 + Math.random() * 0.1).toFixed(2),
        communication: (baseScore * 1.1 - Math.random() * 0.2).toFixed(2),
        innovation: (baseScore * 0.8 + Math.random() * 0.4).toFixed(2)
      },
      performance_trends: this.generatePerformanceTrends(),
      
      // 财务数据
      total_earnings: agent.total_earnings,
      average_reward: (parseFloat(agent.total_earnings) / totalTasks).toFixed(3),
      earning_potential: this.calculateEarningPotential(agent.capabilities, agent.reputation),
      pricing_strategy: this.generatePricingStrategy(agent.current_rate),
      
      // 技术性能
      response_time_avg: agent.response_time_avg,
      response_time_p95: agent.response_time_p95,
      uptime_percentage: parseFloat(agent.uptime_percentage),
      reliability_metrics: {
        availability: agent.uptime_percentage + '%',
        consistency: (85 + Math.random() * 14).toFixed(1) + '%',
        error_rate: (Math.random() * 2).toFixed(2) + '%',
        recovery_time: Math.floor(Math.random() * 30) + 10 + ' seconds'
      },
      
      // 历史数据
      history: this.generatePerformanceHistory(),
      activity_timeline: this.generateActivityTimeline(),
      milestone_history: this.generateMilestoneHistory(),
      
      // 能力信息 - 详细
      capabilities: agent.capabilities,
      capability_weights: agent.capability_weights,
      capability_descriptions: agent.capability_descriptions,
      specialization: agent.specialization,
      skill_matrix: this.generateSkillMatrix(agent.capabilities),
      learning_progress: agent.skill_progression,
      
      // 协作和社交
      collaboration_score: agent.collaboration_score,
      team_compatibility: this.generateTeamCompatibility(),
      communication_style: this.generateCommunicationStyle(),
      leadership_potential: (Math.random() * 100).toFixed(0),
      
      // 客户反馈
      client_feedback: this.generateClientFeedback(),
      testimonials: this.generateTestimonials(),
      repeat_client_rate: (0.4 + Math.random() * 0.5).toFixed(2),
      
      // 市场分析
      market_position: this.analyzeMarketPosition(agent.capabilities, agent.reputation),
      competitive_analysis: this.generateCompetitiveAnalysis(),
      growth_trajectory: this.predictGrowthTrajectory(agent.reputation, totalTasks),
      
      // 个人发展
      strengths: this.identifyStrengths(agent.capabilities, agent.reputation),
      improvement_areas: this.identifyImprovementAreas(),
      development_plan: this.generateDevelopmentPlan(agent.capabilities),
      
      // 风险评估
      risk_assessment: this.generateRiskAssessment(agent.success_rate, agent.uptime_percentage),
      stability_score: this.calculateStabilityScore(agent),
      
      // 预测和建议
      performance_prediction: this.generatePerformancePrediction(),
      optimization_suggestions: this.generateOptimizationSuggestions(agent.capabilities),
      
      // 详细个人资料
      profile: agent.profile,
      
      // 元数据
      profile_completeness: Math.floor(85 + Math.random() * 15) + '%',
      last_profile_update: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
      data_quality_score: (0.92 + Math.random() * 0.07).toFixed(3),
      
      source: 'enhanced_mock_v2',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 生成性能历史数据
   */
  generatePerformanceHistory(days = 30) {
    const history = {
      dates: [],
      reputation: [],
      tasks_completed: [],
      average_scores: [],
      rewards: []
    };
    
    const startDate = new Date(this.currentDate.getTime() - days * 86400000);
    let cumulativeTasks = 0;
    let baseReputation = 60 + Math.random() * 30;
    let baseScore = 3.5 + Math.random() * 1.0;
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate.getTime() + i * 86400000);
      history.dates.push(date.toISOString().split('T')[0]);
      
      // 添加趋势和随机变化
      const trend = i / days;
      const randomFactor = (Math.random() - 0.5) * 0.2;
      
      // 声誉：逐渐增长趋势
      const reputation = Math.max(0, Math.min(100, 
        baseReputation + trend * 20 + randomFactor * 10
      ));
      history.reputation.push(Math.floor(reputation));
      
      // 任务数：累积增长
      const dailyTasks = Math.floor(Math.random() * 3);
      cumulativeTasks += dailyTasks;
      history.tasks_completed.push(cumulativeTasks);
      
      // 分数：小幅波动
      const score = Math.max(2.0, Math.min(5.0,
        baseScore + trend * 0.5 + randomFactor * 0.3
      ));
      history.average_scores.push(parseFloat(score.toFixed(1)));
      
      // 奖励：基于任务数
      const reward = (cumulativeTasks * 0.1 + Math.random() * 0.5).toFixed(2);
      history.rewards.push(parseFloat(reward));
    }
    
    return history;
  }

  /**
   * 生成增强的任务数据
   */
  generateEnhancedTasks(count = 20) {
    const tasks = [];
    const taskTypeKeys = Object.keys(TASK_TYPES);
    
    for (let i = 0; i < count; i++) {
      const taskType = taskTypeKeys[Math.floor(Math.random() * taskTypeKeys.length)];
      const taskInfo = TASK_TYPES[taskType];
      const status = this.selectTaskStatus();
      
      const task = {
        task_id: `task_${Date.now()}_${i}`,
        title: this.generateTaskTitle(taskInfo.name),
        description: this.generateTaskDescription(taskInfo.description),
        type: taskType,
        category: taskInfo.name,
        status: status,
        priority: this.selectTaskPriority(),
        complexity: taskInfo.complexity,
        estimated_duration: this.estimateTaskDuration(taskInfo.complexity),
        created_at: new Date(this.currentDate.getTime() - Math.random() * 30 * 86400000).toISOString(),
        deadline: new Date(this.currentDate.getTime() + Math.random() * 14 * 86400000).toISOString(),
        required_capabilities: taskInfo.required_capabilities,
        reward: (taskInfo.avg_reward * (0.8 + Math.random() * 0.4)).toFixed(3),
        creator_id: this.generateAgentId(),
        tags: this.generateTaskTags(taskInfo.required_capabilities),
        difficulty_score: Math.floor(Math.random() * 10) + 1
      };
      
      // 根据状态添加额外信息
      if (status === 'assigned' || status === 'completed') {
        task.assigned_agent = this.generateAgentId();
        task.assigned_at = new Date(task.created_at).getTime() + Math.random() * 86400000;
      }
      
      if (status === 'completed') {
        task.completed_at = new Date(task.assigned_at + Math.random() * 7 * 86400000).toISOString();
        task.score = 3.0 + Math.random() * 2.0;
        task.feedback = this.generateTaskFeedback();
      }
      
      tasks.push(task);
    }
    
    return {
      tasks: tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),
      total: tasks.length,
      source: 'enhanced_mock'
    };
  }

  /**
   * 生成详细的任务类型分布数据
   */
  generateTaskTypeDistribution(agentId) {
    const capabilities = this.selectRandomCapabilities(2, 4);
    const distribution = {};
    let totalTasks = 0;
    
    capabilities.forEach(capability => {
      const taskCount = Math.floor(Math.random() * 15) + 5;
      distribution[AGENT_CAPABILITIES[capability].name] = taskCount;
      totalTasks += taskCount;
    });
    
    return {
      agent_id: agentId,
      task_types: distribution,
      total_tasks: totalTasks,
      capabilities,
      specialization_ratio: this.calculateSpecializationRatio(distribution),
      source: 'enhanced_mock',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 生成学习事件数据
   */
  generateLearningEvents(agentId, count = 15) {
    const events = [];
    const eventTypes = [
      'task_completion', 'capability_acquisition', 'training', 
      'performance_improvement', 'collaboration', 'error_correction',
      'skill_enhancement', 'knowledge_update'
    ];
    
    for (let i = 0; i < count; i++) {
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const event = {
        event_id: `event_${Date.now()}_${i}`,
        agent_id: agentId,
        event_type: eventType,
        timestamp: new Date(this.currentDate.getTime() - Math.random() * 90 * 86400000).toISOString(),
        data: this.generateEventData(eventType),
        impact_score: Math.random() * 10,
        confidence: 0.7 + Math.random() * 0.3,
        metadata: {
          source: 'enhanced_mock',
          version: '1.0'
        }
      };
      
      events.push(event);
    }
    
    return {
      agent_id: agentId,
      events: events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
      total: events.length,
      summary: this.generateLearningEventsSummary(events),
      source: 'enhanced_mock'
    };
  }

  /**
   * 生成系统分析数据
   */
  generateSystemAnalytics() {
    const agents = this.generateEnhancedAgents(12).agents;
    const tasks = this.generateEnhancedTasks(20).tasks;
    
    return {
      overview: {
        total_agents: agents.length,
        active_agents: agents.filter(a => a.status === 'active').length,
        total_tasks: tasks.length,
        completed_tasks: tasks.filter(t => t.status === 'completed').length,
        success_rate: this.calculateOverallSuccessRate(tasks),
        avg_response_time: this.calculateAverageResponseTime(agents),
        system_efficiency: this.calculateSystemEfficiency()
      },
      capability_distribution: this.analyzeCapabilityDistribution(agents),
      task_completion_trends: this.generateTaskCompletionTrends(),
      performance_metrics: this.generatePerformanceMetrics(agents),
      network_health: this.generateNetworkHealthMetrics(),
      predictive_insights: this.generatePredictiveInsights(),
      timestamp: new Date().toISOString(),
      source: 'enhanced_mock'
    };
  }

  /**
   * 生成协作数据
   */
  generateCollaborationData() {
    const collaborations = [];
    const collaborationTypes = [
      'multi_agent_task', 'knowledge_sharing', 'peer_review',
      'joint_problem_solving', 'skill_transfer', 'quality_assurance'
    ];
    
    for (let i = 0; i < 8; i++) {
      const type = collaborationTypes[Math.floor(Math.random() * collaborationTypes.length)];
      const collaboration = {
        collaboration_id: `collab_${Date.now()}_${i}`,
        type: type,
        title: this.generateCollaborationTitle(type),
        participants: this.generateCollaborationParticipants(),
        status: this.selectCollaborationStatus(),
        created_at: new Date(this.currentDate.getTime() - Math.random() * 15 * 86400000).toISOString(),
        objective: this.generateCollaborationObjective(type),
        progress: Math.floor(Math.random() * 100),
        expected_completion: new Date(this.currentDate.getTime() + Math.random() * 10 * 86400000).toISOString(),
        success_metrics: this.generateSuccessMetrics()
      };
      
      collaborations.push(collaboration);
    }
    
    return {
      collaborations,
      total: collaborations.length,
      active_collaborations: collaborations.filter(c => c.status === 'active').length,
      collaboration_network: this.generateCollaborationNetwork(),
      source: 'enhanced_mock'
    };
  }

  // ========== 辅助方法 ==========

  generateAgentId() {
    return '0x' + Array.from({length: 40}, () => 
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }

  generateCapabilityDescriptions(capabilities) {
    return capabilities.map(cap => {
      const info = AGENT_CAPABILITIES[cap];
      return {
        capability: cap,
        name: info.name,
        description: info.description,
        proficiency: (0.6 + Math.random() * 0.4).toFixed(2),
        years_experience: Math.floor(Math.random() * 5) + 1,
        projects_completed: Math.floor(Math.random() * 30) + 5
      };
    });
  }

  generateScoreHistory(avgScore) {
    const history = [];
    const points = 10;
    let currentScore = avgScore;
    
    for (let i = 0; i < points; i++) {
      const variation = (Math.random() - 0.5) * 0.4;
      currentScore = Math.max(2.0, Math.min(5.0, currentScore + variation));
      history.push({
        period: `Week ${points - i}`,
        score: parseFloat(currentScore.toFixed(1)),
        tasks_count: Math.floor(Math.random() * 8) + 2
      });
    }
    
    return history.reverse();
  }

  generateEarningsHistory() {
    const history = [];
    const months = 6;
    let cumulative = 0;
    
    for (let i = 0; i < months; i++) {
      const monthlyEarning = (Math.random() * 8 + 2).toFixed(2);
      cumulative += parseFloat(monthlyEarning);
      
      const date = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - months + i + 1, 1);
      history.push({
        month: date.toISOString().substr(0, 7),
        earnings: monthlyEarning,
        cumulative: cumulative.toFixed(2),
        tasks_completed: Math.floor(Math.random() * 25) + 5
      });
    }
    
    return history;
  }

  generateAgentBio(capabilities) {
    const templates = [
      `Specialized AI agent with expertise in ${capabilities.join(', ')}. Proven track record of delivering high-quality results in complex projects.`,
      `Professional agent focused on ${capabilities[0]} with ${Math.floor(Math.random() * 4) + 2} years of experience. Committed to excellence and continuous learning.`,
      `Advanced AI assistant specializing in ${capabilities.slice(0, 2).join(' and ')}. Known for innovative problem-solving and reliable performance.`,
      `Experienced ${capabilities[0]} specialist with a passion for delivering exceptional results. Proven ability to work in collaborative environments.`
    ];
    
    return templates[Math.floor(Math.random() * templates.length)];
  }

  selectPreferredTaskTypes(capabilities) {
    const allTypes = Object.keys(TASK_TYPES);
    const preferred = allTypes.filter(type => {
      const taskInfo = TASK_TYPES[type];
      return capabilities.some(cap => taskInfo.required_capabilities.includes(cap));
    });
    
    return preferred.slice(0, Math.min(3, preferred.length));
  }

  generateWorkingHours() {
    const startHour = Math.floor(Math.random() * 6) + 6; // 6-11 AM
    const duration = Math.floor(Math.random() * 4) + 8; // 8-11 hours
    return {
      start: `${startHour.toString().padStart(2, '0')}:00`,
      end: `${((startHour + duration) % 24).toString().padStart(2, '0')}:00`,
      timezone: 'UTC'
    };
  }

  selectRandomTimezone() {
    const timezones = ['UTC', 'UTC+1', 'UTC+2', 'UTC-5', 'UTC-8', 'UTC+8', 'UTC+9'];
    return timezones[Math.floor(Math.random() * timezones.length)];
  }

  selectRandomLanguages() {
    const languages = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Korean', 'Russian'];
    const count = Math.floor(Math.random() * 3) + 1;
    const selected = ['English']; // Always include English
    
    while (selected.length < count && selected.length < languages.length) {
      const lang = languages[Math.floor(Math.random() * languages.length)];
      if (!selected.includes(lang)) {
        selected.push(lang);
      }
    }
    
    return selected;
  }

  generateCertifications(capabilities) {
    const certTemplates = {
      'data_analysis': ['Certified Data Analyst', 'Advanced Statistics Certification'],
      'text_generation': ['Natural Language Processing Certificate', 'Content Creation Professional'],
      'image_recognition': ['Computer Vision Specialist', 'Machine Learning in Vision'],
      'code_generation': ['Software Development Professional', 'Code Quality Assurance']
    };
    
    const certs = [];
    capabilities.forEach(cap => {
      if (certTemplates[cap] && Math.random() > 0.3) {
        const templates = certTemplates[cap];
        certs.push(templates[Math.floor(Math.random() * templates.length)]);
      }
    });
    
    return certs;
  }

  generateSkillProgression(capabilities) {
    return capabilities.map(cap => ({
      capability: cap,
      current_level: (60 + Math.random() * 35).toFixed(0),
      growth_rate: (Math.random() * 15 + 5).toFixed(1) + '%/month',
      next_milestone: Math.floor(Math.random() * 30) + 10 + ' tasks',
      proficiency_trend: Math.random() > 0.7 ? 'accelerating' : 'steady',
      time_invested: Math.floor(Math.random() * 200) + 50 + ' hours'
    }));
  }

  generateRecentAchievements() {
    const achievements = [
      'Completed 10 consecutive high-rated tasks',
      'Achieved 99% uptime for 30 days',
      'Received "Excellence in Innovation" recognition',
      'Successfully mentored 3 junior agents',
      'Contributed to major system optimization',
      'Delivered project 2 days ahead of schedule'
    ];
    
    const count = Math.floor(Math.random() * 3) + 1;
    const selected = [];
    
    while (selected.length < count) {
      const achievement = achievements[Math.floor(Math.random() * achievements.length)];
      if (!selected.includes(achievement)) {
        selected.push(achievement);
      }
    }
    
    return selected;
  }

  calculateMarketDemand(capabilities) {
    const demands = capabilities.map(cap => AGENT_CAPABILITIES[cap].demand);
    const avgDemand = demands.reduce((sum, d) => sum + d, 0) / demands.length;
    
    if (avgDemand >= 0.8) return 'Very High';
    if (avgDemand >= 0.7) return 'High';
    if (avgDemand >= 0.6) return 'Medium';
    if (avgDemand >= 0.5) return 'Low';
    return 'Very Low';
  }

  calculateExperienceLevel(tasksCompleted, reputation) {
    if (tasksCompleted >= 150 && reputation >= 90) return 'Expert';
    if (tasksCompleted >= 100 && reputation >= 80) return 'Senior';
    if (tasksCompleted >= 50 && reputation >= 70) return 'Intermediate';
    if (tasksCompleted >= 20 && reputation >= 60) return 'Junior';
    return 'Beginner';
  }

  generateReputationScore() {
    // 生成更真实的声誉分布
    const base = Math.random();
    if (base < 0.1) return Math.floor(Math.random() * 30) + 20; // 20-50: 新手
    if (base < 0.3) return Math.floor(Math.random() * 25) + 50; // 50-75: 普通
    if (base < 0.7) return Math.floor(Math.random() * 20) + 75; // 75-95: 优秀
    return Math.floor(Math.random() * 5) + 95; // 95-100: 专家
  }

  selectRandomCapabilities(min = 2, max = 4) {
    const capabilities = Object.keys(AGENT_CAPABILITIES);
    const count = Math.floor(Math.random() * (max - min + 1)) + min;
    const selected = [];
    
    while (selected.length < count) {
      const capability = capabilities[Math.floor(Math.random() * capabilities.length)];
      if (!selected.includes(capability)) {
        selected.push(capability);
      }
    }
    
    return selected;
  }

  generateCapabilityWeights(capabilities) {
    const weights = [];
    const sum = capabilities.length;
    
    capabilities.forEach(() => {
      weights.push((0.5 + Math.random() * 0.5).toFixed(2));
    });
    
    return weights;
  }

  getAgentSpecialization(capabilities) {
    if (capabilities.length === 1) return 'Specialist';
    if (capabilities.length <= 2) return 'Expert';
    if (capabilities.length <= 3) return 'Versatile';
    return 'Generalist';
  }

  calculatePerformanceTier(reputation, avgScore) {
    const combinedScore = (reputation * 0.6) + (avgScore * 20 * 0.4);
    
    if (combinedScore >= 95) return 'Diamond';
    if (combinedScore >= 85) return 'Platinum';
    if (combinedScore >= 75) return 'Gold';
    if (combinedScore >= 65) return 'Silver';
    return 'Bronze';
  }

  selectTaskStatus() {
    const rand = Math.random();
    if (rand < 0.3) return 'open';
    if (rand < 0.5) return 'assigned';
    if (rand < 0.7) return 'in_progress';
    if (rand < 0.9) return 'completed';
    return 'cancelled';
  }

  selectTaskPriority() {
    const rand = Math.random();
    if (rand < 0.2) return 'low';
    if (rand < 0.6) return 'medium';
    if (rand < 0.9) return 'high';
    return 'urgent';
  }

  estimateTaskDuration(complexity) {
    const baseDuration = complexity * 2; // 基础小时数
    const variation = Math.random() * complexity;
    return Math.floor(baseDuration + variation);
  }

  generateTaskTitle(taskType) {
    const titles = {
      'Market Analysis': [
        'Q4 Consumer Behavior Analysis',
        'Competitive Landscape Assessment',
        'Market Trend Forecasting',
        'Customer Segmentation Study'
      ],
      'Content Creation': [
        'Product Launch Campaign Content',
        'Blog Article Series Development',
        'Social Media Content Strategy',
        'Brand Messaging Framework'
      ],
      'Image Processing': [
        'Product Catalog Image Enhancement',
        'Visual Content Categorization',
        'Brand Asset Recognition System',
        'Quality Control Visual Inspection'
      ],
      'Code Review': [
        'API Security Assessment',
        'Performance Optimization Review',
        'Code Quality Standards Audit',
        'Architecture Design Review'
      ]
    };
    
    const options = titles[taskType] || ['Generic Task'];
    return options[Math.floor(Math.random() * options.length)];
  }

  generateTaskDescription(baseDescription) {
    const extensions = [
      'with detailed reporting and recommendations',
      'including comprehensive documentation',
      'with performance benchmarking',
      'following industry best practices',
      'with stakeholder presentation materials',
      'including risk assessment analysis'
    ];
    
    const extension = extensions[Math.floor(Math.random() * extensions.length)];
    return `${baseDescription} ${extension}.`;
  }

  generateTaskTags(capabilities) {
    const additionalTags = ['urgent', 'high-priority', 'research', 'analysis', 'creative', 'technical'];
    const tags = [...capabilities];
    
    // 添加1-2个额外标签
    const extraCount = Math.floor(Math.random() * 3);
    for (let i = 0; i < extraCount; i++) {
      const tag = additionalTags[Math.floor(Math.random() * additionalTags.length)];
      if (!tags.includes(tag)) {
        tags.push(tag);
      }
    }
    
    return tags;
  }

  generateTaskFeedback() {
    const feedbacks = [
      'Excellent work, exceeded expectations',
      'Good quality output, minor revisions needed',
      'Satisfactory completion, met all requirements',
      'Outstanding analysis and insights provided',
      'Professional delivery, would recommend',
      'Innovative approach to problem solving'
    ];
    
    return feedbacks[Math.floor(Math.random() * feedbacks.length)];
  }

  calculateSpecializationRatio(distribution) {
    const values = Object.values(distribution);
    const max = Math.max(...values);
    const total = values.reduce((sum, val) => sum + val, 0);
    return (max / total).toFixed(2);
  }

  generateEventData(eventType) {
    const eventData = {
      'task_completion': () => `Successfully completed ${this.selectRandomCapabilities(1)[0]} task with ${(3.5 + Math.random() * 1.5).toFixed(1)} rating`,
      'capability_acquisition': () => `Acquired new capability: ${this.selectRandomCapabilities(1)[0]}`,
      'training': () => `Completed advanced training in ${this.selectRandomCapabilities(1)[0]}`,
      'performance_improvement': () => `Performance increased by ${(Math.random() * 15 + 5).toFixed(1)}%`,
      'collaboration': () => `Successful collaboration with ${Math.floor(Math.random() * 3) + 2} other agents`,
      'error_correction': () => `Self-corrected error in ${this.selectRandomCapabilities(1)[0]} processing`,
      'skill_enhancement': () => `Enhanced proficiency in ${this.selectRandomCapabilities(1)[0]}`,
      'knowledge_update': () => `Updated knowledge base with latest ${this.selectRandomCapabilities(1)[0]} patterns`
    };
    
    return eventData[eventType] ? eventData[eventType]() : 'General learning event';
  }

  generateLearningEventsSummary(events) {
    const typeCount = {};
    events.forEach(event => {
      typeCount[event.event_type] = (typeCount[event.event_type] || 0) + 1;
    });
    
    return {
      total_events: events.length,
      event_types: typeCount,
      learning_velocity: (events.length / 90).toFixed(2), // events per day over 90 days
      improvement_trend: Math.random() > 0.5 ? 'increasing' : 'stable'
    };
  }

  /**
   * 生成Agent学习数据（来自任务评估系统）
   */
  getAgentLearningData(agentId) {
    const learningEvents = [];
    const eventTypes = ['task_evaluation', 'task_completion', 'performance_feedback'];
    
    // 生成最近的学习事件（来自任务评估）
    for (let i = 0; i < 10; i++) {
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      const event = {
        event_id: `learn_${Date.now()}_${i}`,
        agent_id: agentId,
        event_type: eventType,
        timestamp: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
        data: {
          task_id: `task_${Math.random().toString(36).substring(2, 10)}`,
          evaluation_result: Math.random() > 0.7 ? 'success' : 'failure',
          rating: Math.floor(Math.random() * 5) + 1,
          feedback: eventType === 'task_evaluation' ? 'User evaluated task' : 'System feedback',
          reputation_change: (Math.random() - 0.5) * 10,
          capability_improvements: this.generateCapabilityImprovements(),
          score_change: (Math.random() - 0.5) * 0.5
        },
        source: 'evaluation_system'
      };
      learningEvents.push(event);
    }

    return {
      agent_id: agentId,
      learning_events: learningEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
      total: learningEvents.length,
      source: 'enhanced_mock'
    };
  }

  /**
   * 生成能力改进数据
   */
  generateCapabilityImprovements() {
    const capabilities = Object.keys(AGENT_CAPABILITIES);
    const improvements = {};
    
    // 随机选择1-2个能力进行改进
    const numImprovements = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < numImprovements; i++) {
      const capability = capabilities[Math.floor(Math.random() * capabilities.length)];
      improvements[capability] = {
        previous_score: Math.random() * 100,
        new_score: Math.random() * 100,
        improvement: (Math.random() - 0.5) * 20
      };
    }
    
    return improvements;
  }

  /**
   * 生成所有Agent的学习统计数据（用于Learning Dashboard）
   */
  getAgentLearningStatistics() {
    const agents = this.generateEnhancedAgents(8).agents;
    
    const statistics = agents.map(agent => {
      // 基于任务评估系统更新的数据
      const recentEvaluations = Math.floor(Math.random() * 10) + 5;
      const successfulEvaluations = Math.floor(recentEvaluations * (0.6 + Math.random() * 0.3));
      
      return {
        agent_id: agent.agent_id,
        agent_name: agent.name,
        reputation: Math.floor(agent.reputation + (Math.random() - 0.5) * 10), // 评估系统更新后的声誉
        average_score: agent.average_score + (Math.random() - 0.5) * 0.5, // 评估系统更新后的平均分
        average_reward: agent.average_reward + (Math.random() - 0.5) * 0.2, // 评估系统更新后的平均奖励
        tasks_completed: agent.tasks_completed + Math.floor(Math.random() * 5), // 新完成的任务
        success_rate: ((successfulEvaluations / recentEvaluations) * 100).toFixed(1),
        recent_evaluations: recentEvaluations,
        successful_evaluations: successfulEvaluations,
        failed_evaluations: recentEvaluations - successfulEvaluations,
        capability_scores: this.generateUpdatedCapabilityScores(agent.capabilities),
        learning_velocity: (Math.random() * 2 + 0.5).toFixed(2), // 学习速度
        performance_trend: Math.random() > 0.6 ? 'improving' : (Math.random() > 0.3 ? 'stable' : 'declining'),
        last_evaluation: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
        total_learning_events: Math.floor(Math.random() * 20) + 10,
        source: 'evaluation_system'
      };
    });

    return {
      agents: statistics,
      summary: {
        total_agents: statistics.length,
        avg_reputation: (statistics.reduce((sum, a) => sum + a.reputation, 0) / statistics.length).toFixed(1),
        avg_success_rate: (statistics.reduce((sum, a) => sum + parseFloat(a.success_rate), 0) / statistics.length).toFixed(1),
        total_evaluations: statistics.reduce((sum, a) => sum + a.recent_evaluations, 0),
        total_learning_events: statistics.reduce((sum, a) => sum + a.total_learning_events, 0),
        performance_distribution: {
          improving: statistics.filter(a => a.performance_trend === 'improving').length,
          stable: statistics.filter(a => a.performance_trend === 'stable').length,
          declining: statistics.filter(a => a.performance_trend === 'declining').length
        }
      },
      timestamp: new Date().toISOString(),
      source: 'enhanced_mock'
    };
  }

  /**
   * 生成更新后的能力分数
   */
  generateUpdatedCapabilityScores(capabilities) {
    const scores = {};
    capabilities.forEach(capability => {
      scores[capability] = {
        current_score: Math.floor(Math.random() * 30) + 70, // 70-100分
        previous_score: Math.floor(Math.random() * 30) + 60, // 60-90分
        improvement: Math.random() * 10 - 2, // -2到+8的改进
        evaluation_count: Math.floor(Math.random() * 5) + 1
      };
    });
    return scores;
  }

  calculateOverallSuccessRate(tasks) {
    const completed = tasks.filter(t => t.status === 'completed').length;
    const total = tasks.filter(t => t.status !== 'open').length;
    return total > 0 ? ((completed / total) * 100).toFixed(1) : '0.0';
  }

  calculateAverageResponseTime(agents) {
    const times = agents.map(a => a.response_time_avg);
    const average = times.reduce((sum, time) => sum + time, 0) / times.length;
    return Math.floor(average);
  }

  calculateSystemEfficiency() {
    return (75 + Math.random() * 20).toFixed(1); // 75-95%
  }

  analyzeCapabilityDistribution(agents) {
    const distribution = {};
    agents.forEach(agent => {
      agent.capabilities.forEach(cap => {
        distribution[cap] = (distribution[cap] || 0) + 1;
      });
    });
    
    return Object.entries(distribution).map(([capability, count]) => ({
      capability: AGENT_CAPABILITIES[capability].name,
      count,
      percentage: ((count / agents.length) * 100).toFixed(1),
      demand: AGENT_CAPABILITIES[capability].demand
    }));
  }

  generateTaskCompletionTrends() {
    const trends = [];
    const days = 30;
    
    for (let i = 0; i < days; i++) {
      const date = new Date(this.currentDate.getTime() - (days - i) * 86400000);
      trends.push({
        date: date.toISOString().split('T')[0],
        completed_tasks: Math.floor(Math.random() * 10) + 5,
        created_tasks: Math.floor(Math.random() * 12) + 6,
        success_rate: (70 + Math.random() * 25).toFixed(1)
      });
    }
    
    return trends;
  }

  generatePerformanceMetrics(agents) {
    return {
      average_reputation: (agents.reduce((sum, a) => sum + a.reputation, 0) / agents.length).toFixed(1),
      top_performers: agents
        .sort((a, b) => b.reputation - a.reputation)
        .slice(0, 5)
        .map(a => ({ agent_id: a.agent_id, name: a.name, reputation: a.reputation })),
      capability_leaders: this.findCapabilityLeaders(agents),
      performance_distribution: this.calculatePerformanceDistribution(agents)
    };
  }

  generateNetworkHealthMetrics() {
    return {
      connectivity_score: (85 + Math.random() * 15).toFixed(1),
      throughput: `${(50 + Math.random() * 100).toFixed(0)} tasks/hour`,
      latency: `${(20 + Math.random() * 30).toFixed(0)}ms`,
      reliability: (95 + Math.random() * 5).toFixed(1) + '%',
      load_balance: (80 + Math.random() * 20).toFixed(1) + '%'
    };
  }

  generatePredictiveInsights() {
    return {
      demand_forecast: 'Increasing demand for data_analysis and code_generation capabilities',
      capacity_recommendations: 'Consider recruiting 2-3 additional agents with optimization skills',
      market_opportunities: 'High-value tasks in AI model training and deployment consulting',
      risk_assessment: 'Low risk of system overload in next 30 days'
    };
  }

  findCapabilityLeaders(agents) {
    const leaders = {};
    Object.keys(AGENT_CAPABILITIES).forEach(capability => {
      const capableAgents = agents.filter(a => a.capabilities.includes(capability));
      if (capableAgents.length > 0) {
        const leader = capableAgents.reduce((best, current) => 
          current.reputation > best.reputation ? current : best
        );
        leaders[capability] = {
          agent_id: leader.agent_id,
          name: leader.name,
          reputation: leader.reputation
        };
      }
    });
    return leaders;
  }

  calculatePerformanceDistribution(agents) {
    const tiers = { Bronze: 0, Silver: 0, Gold: 0, Platinum: 0, Diamond: 0 };
    agents.forEach(agent => {
      tiers[agent.performance_tier]++;
    });
    return tiers;
  }

  generateCollaborationTitle(type) {
    const titles = {
      'multi_agent_task': ['Complex Data Pipeline Development', 'Enterprise AI Solution Design'],
      'knowledge_sharing': ['Best Practices Workshop', 'Technical Knowledge Transfer'],
      'peer_review': ['Code Quality Assessment', 'Solution Architecture Review'],
      'joint_problem_solving': ['Cross-Domain Problem Analysis', 'Innovative Solution Discovery'],
      'skill_transfer': ['Capability Enhancement Program', 'Expert Mentorship Initiative'],
      'quality_assurance': ['Output Quality Verification', 'Performance Standards Validation']
    };
    
    const options = titles[type] || ['General Collaboration'];
    return options[Math.floor(Math.random() * options.length)];
  }

  generateCollaborationParticipants() {
    const count = Math.floor(Math.random() * 4) + 2; // 2-5 participants
    const participants = [];
    
    for (let i = 0; i < count; i++) {
      participants.push({
        agent_id: this.generateAgentId(),
        role: this.selectParticipantRole(),
        contribution_score: Math.random().toFixed(2)
      });
    }
    
    return participants;
  }

  selectParticipantRole() {
    const roles = ['lead', 'contributor', 'reviewer', 'specialist', 'coordinator'];
    return roles[Math.floor(Math.random() * roles.length)];
  }

  selectCollaborationStatus() {
    const statuses = ['planning', 'active', 'review', 'completed', 'paused'];
    return statuses[Math.floor(Math.random() * statuses.length)];
  }

  generateCollaborationObjective(type) {
    const objectives = {
      'multi_agent_task': 'Combine diverse capabilities to solve complex multi-faceted problems',
      'knowledge_sharing': 'Transfer specialized knowledge and best practices across the network',
      'peer_review': 'Ensure quality and accuracy through collaborative validation',
      'joint_problem_solving': 'Leverage collective intelligence for innovative solutions',
      'skill_transfer': 'Enhance overall network capabilities through peer learning',
      'quality_assurance': 'Maintain high standards through systematic review processes'
    };
    
    return objectives[type] || 'Collaborative problem solving and knowledge enhancement';
  }

  generateSuccessMetrics() {
    return {
      quality_score: (7 + Math.random() * 3).toFixed(1),
      efficiency_gain: `${(10 + Math.random() * 40).toFixed(0)}%`,
      knowledge_transfer: (0.6 + Math.random() * 0.4).toFixed(2),
      participant_satisfaction: (4.0 + Math.random() * 1.0).toFixed(1)
    };
  }

  generateCollaborationNetwork() {
    return {
      total_connections: Math.floor(Math.random() * 50) + 30,
      active_collaborations: Math.floor(Math.random() * 8) + 5,
      collaboration_efficiency: (80 + Math.random() * 15).toFixed(1) + '%',
      network_density: (0.3 + Math.random() * 0.4).toFixed(2)
    };
  }

  // ========== 新增辅助方法 - 生成更详细的数据 ==========

  generateReputationHistory(currentReputation) {
    const history = [];
    let reputation = Math.max(20, currentReputation - 30);
    
    for (let i = 0; i < 12; i++) {
      const change = Math.random() * 5 - 1; // -1 到 +4 的变化
      reputation = Math.min(100, Math.max(0, reputation + change));
      
      const date = new Date(this.currentDate.getTime() - (12 - i) * 30 * 86400000);
      history.push({
        month: date.toISOString().substr(0, 7),
        reputation: Math.floor(reputation),
        change: i === 0 ? 0 : Math.floor(reputation - history[i-1]?.reputation || 0)
      });
    }
    
    return history;
  }

  generateDetailedTaskDistribution(capabilities) {
    const distribution = {};
    let totalTasks = 0;
    
    Object.keys(TASK_TYPES).forEach(taskType => {
      const taskInfo = TASK_TYPES[taskType];
      const hasCapability = capabilities.some(cap => taskInfo.required_capabilities.includes(cap));
      
      if (hasCapability) {
        const count = Math.floor(Math.random() * 25) + 5;
        distribution[taskType] = {
          count: count,
          success_rate: (0.7 + Math.random() * 0.29).toFixed(2),
          avg_score: (3.5 + Math.random() * 1.3).toFixed(1),
          total_earnings: (count * taskInfo.avg_reward * (0.8 + Math.random() * 0.4)).toFixed(2)
        };
        totalTasks += count;
      }
    });
    
    return { distribution, totalTasks };
  }

  calculatePreferredComplexity(capabilities) {
    const complexities = capabilities.map(cap => AGENT_CAPABILITIES[cap].complexity);
    const avgComplexity = complexities.reduce((sum, c) => sum + c, 0) / complexities.length;
    
    if (avgComplexity >= 4.5) return 'Expert Level';
    if (avgComplexity >= 3.5) return 'Advanced';
    if (avgComplexity >= 2.5) return 'Intermediate';
    return 'Basic';
  }

  generatePerformanceTrends() {
    const trends = [];
    const metrics = ['quality', 'speed', 'communication', 'innovation'];
    
    metrics.forEach(metric => {
      const trend = Math.random() > 0.3 ? 'improving' : (Math.random() > 0.5 ? 'stable' : 'declining');
      const rate = (Math.random() * 10 + 2).toFixed(1);
      
      trends.push({
        metric: metric,
        trend: trend,
        change_rate: `${rate}%`,
        confidence: (0.7 + Math.random() * 0.3).toFixed(2)
      });
    });
    
    return trends;
  }

  calculateEarningPotential(capabilities, reputation) {
    const baseRate = 0.5;
    const capabilityBonus = capabilities.length * 0.1;
    const reputationBonus = (reputation / 100) * 0.3;
    
    return (baseRate + capabilityBonus + reputationBonus).toFixed(3);
  }

  generatePricingStrategy(currentRate) {
    return {
      current_rate: currentRate,
      market_position: Math.random() > 0.5 ? 'competitive' : 'premium',
      price_flexibility: (Math.random() * 0.3 + 0.1).toFixed(2),
      minimum_rate: (parseFloat(currentRate) * 0.8).toFixed(3),
      maximum_rate: (parseFloat(currentRate) * 1.5).toFixed(3)
    };
  }

  generateActivityTimeline() {
    const timeline = [];
    const activities = [
      'Task Completion', 'Learning Session', 'Collaboration', 'Training',
      'Performance Review', 'Skill Assessment', 'System Update', 'Client Meeting'
    ];
    
    for (let i = 0; i < 15; i++) {
      const date = new Date(this.currentDate.getTime() - i * 12 * 3600000);
      timeline.push({
        timestamp: date.toISOString(),
        activity: activities[Math.floor(Math.random() * activities.length)],
        duration: Math.floor(Math.random() * 180) + 30 + ' minutes',
        outcome: Math.random() > 0.2 ? 'successful' : 'needs_improvement'
      });
    }
    
    return timeline.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  generateMilestoneHistory() {
    const milestones = [
      'First 10 tasks completed',
      'Achieved 90% success rate',
      'Reached 1000 reputation points',
      'Completed advanced training',
      'Joined expert tier',
      'Earned specialization certificate'
    ];
    
    return milestones.map((milestone, index) => ({
      milestone: milestone,
      achieved_date: new Date(this.currentDate.getTime() - (milestones.length - index) * 45 * 86400000).toISOString().split('T')[0],
      impact_score: (Math.random() * 5 + 5).toFixed(1)
    }));
  }

  generateSkillMatrix(capabilities) {
    const matrix = {};
    
    capabilities.forEach(cap => {
      const capInfo = AGENT_CAPABILITIES[cap];
      matrix[cap] = {
        name: capInfo.name,
        proficiency: (0.6 + Math.random() * 0.4).toFixed(2),
        experience_months: Math.floor(Math.random() * 24) + 6,
        certification_level: this.generateCertificationLevel(),
        market_demand: capInfo.demand,
        growth_potential: (Math.random() * 0.5 + 0.3).toFixed(2),
        related_skills: this.findRelatedSkills(cap)
      };
    });
    
    return matrix;
  }

  generateCertificationLevel() {
    const levels = ['Basic', 'Intermediate', 'Advanced', 'Expert', 'Master'];
    const weights = [0.1, 0.2, 0.3, 0.3, 0.1];
    
    let random = Math.random();
    for (let i = 0; i < levels.length; i++) {
      random -= weights[i];
      if (random <= 0) return levels[i];
    }
    return levels[levels.length - 1];
  }

  findRelatedSkills(capability) {
    const relations = {
      'data_analysis': ['classification', 'optimization'],
      'text_generation': ['summarization', 'translation'],
      'image_recognition': ['classification', 'optimization'],
      'code_generation': ['optimization', 'classification']
    };
    
    return relations[capability] || [];
  }

  generateTeamCompatibility() {
    const roles = ['Leader', 'Collaborator', 'Specialist', 'Supporter', 'Innovator'];
    const compatibility = {};
    
    roles.forEach(role => {
      compatibility[role] = (Math.random() * 0.4 + 0.6).toFixed(2);
    });
    
    return compatibility;
  }

  generateCommunicationStyle() {
    const styles = {
      directness: (Math.random() * 0.6 + 0.4).toFixed(2),
      formality: (Math.random() * 0.8 + 0.2).toFixed(2),
      responsiveness: (Math.random() * 0.3 + 0.7).toFixed(2),
      clarity: (Math.random() * 0.2 + 0.8).toFixed(2)
    };
    
    return styles;
  }

  generateClientFeedback() {
    const feedback = [];
    const templates = [
      'Excellent attention to detail and professional communication',
      'Delivered high-quality results ahead of schedule',
      'Great collaboration skills and technical expertise',
      'Innovative approach to problem-solving',
      'Reliable and consistent performance'
    ];
    
    for (let i = 0; i < 5; i++) {
      feedback.push({
        rating: (4.0 + Math.random() * 1.0).toFixed(1),
        comment: templates[i],
        date: new Date(this.currentDate.getTime() - Math.random() * 90 * 86400000).toISOString().split('T')[0],
        client_id: this.generateAgentId().substr(0, 10)
      });
    }
    
    return feedback;
  }

  generateTestimonials() {
    const testimonials = [
      'Outstanding agent with exceptional problem-solving abilities.',
      'Highly recommend for complex analytical tasks.',
      'Professional, reliable, and delivers excellent results.',
      'Great communication and technical skills.'
    ];
    
    return testimonials.map((text, index) => ({
      text: text,
      author: `Client ${index + 1}`,
      rating: (4.2 + Math.random() * 0.8).toFixed(1),
      date: new Date(this.currentDate.getTime() - Math.random() * 120 * 86400000).toISOString().split('T')[0]
    }));
  }

  analyzeMarketPosition(capabilities, reputation) {
    const position = {};
    
    capabilities.forEach(cap => {
      const demand = AGENT_CAPABILITIES[cap].demand;
      const competition = Math.random() * 0.8 + 0.2;
      
      position[cap] = {
        market_demand: demand,
        competition_level: competition.toFixed(2),
        market_share: (Math.random() * 0.1 + 0.05).toFixed(3),
        growth_opportunity: (demand / competition).toFixed(2)
      };
    });
    
    return position;
  }

  generateCompetitiveAnalysis() {
    return {
      market_ranking: Math.floor(Math.random() * 100) + 1,
      peer_comparison: {
        above_average: Math.floor(Math.random() * 5) + 3,
        below_average: Math.floor(Math.random() * 3) + 1,
        similar_level: Math.floor(Math.random() * 4) + 2
      },
      competitive_advantages: [
        'High reliability score',
        'Excellent communication skills',
        'Fast response time'
      ],
      improvement_opportunities: [
        'Expand capability portfolio',
        'Increase market presence',
        'Develop niche expertise'
      ]
    };
  }

  predictGrowthTrajectory(reputation, totalTasks) {
    const growthRate = (reputation / 100) * 0.2 + (totalTasks / 1000) * 0.1;
    
    return {
      current_trajectory: growthRate > 0.15 ? 'accelerating' : (growthRate > 0.05 ? 'steady' : 'slow'),
      predicted_6_month: {
        reputation: Math.min(100, Math.floor(reputation + growthRate * 100)),
        task_completion: Math.floor(totalTasks * 1.3),
        earning_potential: (growthRate * 10).toFixed(2)
      },
      growth_drivers: [
        'Consistent high performance',
        'Positive client feedback',
        'Skill development'
      ]
    };
  }

  identifyStrengths(capabilities, reputation) {
    const strengths = [];
    
    if (reputation >= 90) strengths.push('Exceptional reputation');
    if (capabilities.length >= 4) strengths.push('Versatile skill set');
    if (Math.random() > 0.5) strengths.push('Strong problem-solving ability');
    if (Math.random() > 0.6) strengths.push('Excellent communication');
    if (Math.random() > 0.7) strengths.push('Leadership potential');
    
    return strengths.length > 0 ? strengths : ['Reliable performance'];
  }

  identifyImprovementAreas() {
    const areas = [
      'Response time optimization',
      'Skill diversification',
      'Market expansion',
      'Client relationship building',
      'Technical depth enhancement'
    ];
    
    return areas.slice(0, Math.floor(Math.random() * 3) + 2);
  }

  generateDevelopmentPlan(capabilities) {
    const plan = [];
    
    capabilities.forEach(cap => {
      plan.push({
        capability: cap,
        current_level: Math.floor(Math.random() * 30) + 70,
        target_level: Math.floor(Math.random() * 10) + 90,
        timeline: Math.floor(Math.random() * 6) + 3 + ' months',
        recommended_actions: [
          'Complete advanced training',
          'Take on challenging projects',
          'Seek mentorship'
        ]
      });
    });
    
    return plan;
  }

  generateRiskAssessment(successRate, uptime) {
    const riskFactors = [];
    
    if (successRate < 0.8) riskFactors.push('Below average success rate');
    if (uptime < 95) riskFactors.push('Reliability concerns');
    if (Math.random() > 0.8) riskFactors.push('Limited capability diversity');
    
    return {
      overall_risk: riskFactors.length > 2 ? 'High' : (riskFactors.length > 0 ? 'Medium' : 'Low'),
      risk_factors: riskFactors,
      mitigation_strategies: [
        'Implement quality control measures',
        'Provide additional training',
        'Monitor performance closely'
      ]
    };
  }

  calculateStabilityScore(agent) {
    const factors = [
      agent.success_rate,
      agent.uptime_percentage / 100,
      agent.reputation / 100,
      Math.min(1, agent.tasks_completed / 50)
    ];
    
    const score = factors.reduce((sum, factor) => sum + factor, 0) / factors.length;
    return (score * 100).toFixed(1);
  }

  generatePerformancePrediction() {
    const prediction = {
      next_30_days: {
        expected_tasks: Math.floor(Math.random() * 15) + 10,
        predicted_success_rate: (0.8 + Math.random() * 0.19).toFixed(2),
        confidence: (0.75 + Math.random() * 0.24).toFixed(2)
      },
      next_quarter: {
        reputation_change: Math.floor(Math.random() * 10) - 3,
        earning_potential: (Math.random() * 20 + 10).toFixed(2),
        market_position: Math.random() > 0.5 ? 'improving' : 'stable'
      }
    };
    
    return prediction;
  }

  generateOptimizationSuggestions(capabilities) {
    const suggestions = [];
    
    if (capabilities.length < 3) {
      suggestions.push('Consider expanding capability portfolio');
    }
    
    if (Math.random() > 0.5) {
      suggestions.push('Focus on high-demand capabilities');
    }
    
    suggestions.push('Maintain consistent performance');
    suggestions.push('Engage in continuous learning');
    suggestions.push('Build strong client relationships');
    
    return suggestions.slice(0, 3);
  }

  /**
   * 生成任务状态分布数据
   */
  getTaskStatusDistribution() {
    return [
      {
        id: 'open',
        label: 'Open',
        value: Math.floor(Math.random() * 10) + 5,
        color: '#2196F3'
      },
      {
        id: 'assigned', 
        label: 'Assigned',
        value: Math.floor(Math.random() * 8) + 3,
        color: '#FF9800'
      },
      {
        id: 'completed',
        label: 'Completed', 
        value: Math.floor(Math.random() * 15) + 10,
        color: '#4CAF50'
      },
      {
        id: 'failed',
        label: 'Failed',
        value: Math.floor(Math.random() * 3) + 1,
        color: '#F44336'
      }
    ];
  }

  /**
   * 生成代理能力分布数据
   */
  getAgentCapabilitiesDistribution() {
    const capabilities = Object.keys(AGENT_CAPABILITIES);
    return capabilities.map(cap => {
      const capInfo = AGENT_CAPABILITIES[cap];
      return {
        capability: capInfo.name,
        count: Math.floor(Math.random() * 8) + 2,
        percentage: Math.floor(Math.random() * 30) + 10
      };
    });
  }

  /**
   * 生成任务完成趋势数据
   */
  getTaskCompletionTrend() {
    const trend = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);

    for (let i = 0; i < 30; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;
      const baseCompleted = isWeekend ? 2 : 5;
      const baseCreated = isWeekend ? 3 : 7;
      
      trend.push({
        date: date.toISOString().split('T')[0],
        completed: baseCompleted + Math.floor(Math.random() * 4),
        created: baseCreated + Math.floor(Math.random() * 5),
        failed: Math.floor(Math.random() * 2)
      });
    }

    return trend;
  }

  /**
   * 生成系统状态数据
   */
  getSystemStatus() {
    return {
      agents: {
        total: Math.floor(Math.random() * 20) + 15,
        active: Math.floor(Math.random() * 15) + 10,
        online: Math.floor(Math.random() * 12) + 8
      },
      tasks: {
        total: Math.floor(Math.random() * 50) + 30,
        completed: Math.floor(Math.random() * 25) + 15,
        pending: Math.floor(Math.random() * 10) + 5
      },
      blockchain: {
        blockHeight: Math.floor(Math.random() * 10000) + 50000,
        transactionCount: Math.floor(Math.random() * 1000) + 500,
        connected: true
      },
      performance: {
        averageResponseTime: (Math.random() * 2 + 0.5).toFixed(2),
        successRate: (0.85 + Math.random() * 0.14).toFixed(3),
        uptime: (0.95 + Math.random() * 0.049).toFixed(3)
      }
    };
  }

  /**
   * 生成代理能力雷达图数据
   */
  getAgentCapabilityRadar(agentId) {
    const capabilities = Object.keys(AGENT_CAPABILITIES).slice(0, 6);
    return capabilities.map(cap => ({
      capability: AGENT_CAPABILITIES[cap].name,
      current: Math.floor(Math.random() * 40) + 60,
      potential: Math.floor(Math.random() * 20) + 80
    }));
  }

  /**
   * 生成收益分析数据
   */
  getEarningsAnalysis() {
    // Generate daily earnings data for the past 14 days
    const dailyEarnings = [];
    const currentDate = new Date();
    
    for (let i = 13; i >= 0; i--) {
      const date = new Date(currentDate);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD format
      
      const totalEarnings = (Math.random() * 5 + 2).toFixed(2); // 2-7 ETH per day
      const agentEarnings = (totalEarnings * (0.6 + Math.random() * 0.3)).toFixed(2); // 60-90% of total
      
      dailyEarnings.push({
        date: dateStr,
        totalEarnings: parseFloat(totalEarnings),
        agentEarnings: parseFloat(agentEarnings)
      });
    }
    
    // Generate top earners data
    const agentNames = ['Agent Alpha', 'Agent Beta', 'Agent Gamma', 'Agent Delta', 'Agent Echo'];
    const topEarners = agentNames.map(agent => ({
      agent,
      earnings: (Math.random() * 20 + 10).toFixed(2) // 10-30 ETH total
    })).sort((a, b) => parseFloat(b.earnings) - parseFloat(a.earnings));
    
    return {
      dailyEarnings,
      topEarners
    };
  }

  /**
   * 生成实时任务执行数据  
   */
  getRealTimeTaskExecution() {
    const executions = [];
    for (let i = 0; i < 3; i++) {
      executions.push({
        taskId: `task_${Math.random().toString(36).substring(2, 8)}`,
        title: `AI Task ${i + 1}`,
        agent: `Agent ${String.fromCharCode(65 + i)}`,
        progress: Math.floor(Math.random() * 80) + 20,
        currentStep: ['Analysis', 'Processing', 'Validation', 'Completion'][Math.floor(Math.random() * 4)]
      });
    }

    return {
      data: {
        activeExecutions: executions,
        queueMetrics: {
          totalInQueue: Math.floor(Math.random() * 8) + 2,
          avgWaitTime: Math.floor(Math.random() * 30) + 10,
          throughputPerHour: Math.floor(Math.random() * 20) + 15
        }
      }
    };
  }

  /**
   * 生成代理性能数据
   */
  getAgentPerformanceData() {
    const agents = [];
    for (let i = 0; i < 6; i++) {
      agents.push({
        id: `agent_${i}`,
        name: `Agent ${String.fromCharCode(65 + i)}`,
        reputation: Math.floor(Math.random() * 30) + 70,
        tasksCompleted: Math.floor(Math.random() * 50) + 10,
        successRate: Math.floor(Math.random() * 20) + 80
      });
    }
    return agents;
  }
}

// 创建全局实例
export const enhancedMockData = new EnhancedMockDataGenerator();

// 导出类
export { EnhancedMockDataGenerator };

// 导出能力定义供其他模块使用
export { AGENT_CAPABILITIES, TASK_TYPES };