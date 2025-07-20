import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Slider,
  Tabs,
  Tab,
  Chip
} from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { Line, Radar, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import axios from 'axios';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

const LearningDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agents, setAgents] = useState([]);
  const [learningData, setLearningData] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  useEffect(() => {
    fetchAgents();
  }, []);
  
  useEffect(() => {
    if (selectedAgent) {
      fetchLearningData(selectedAgent);
    }
  }, [selectedAgent]);
  
  const fetchAgents = async () => {
    setAgentsLoading(true);
    try {
      // 首先尝试从API获取真实数据
      try {
        const response = await axios.get('http://localhost:8001/agents/');
        console.log('✅ Fetched real agents data from API:', response.data);
        
        if (response.data && response.data.agents && response.data.agents.length > 0) {
          // 转换API数据格式为前端需要的格式
          const realAgents = response.data.agents.map(agent => ({
            agent_id: agent.agent_id,
            name: agent.name,
            reputation: agent.reputation || 50,
            capabilities: agent.capabilities || [],
            capability_weights: agent.capability_weights || [],
            tasks_completed: agent.tasks_completed || 0,
            active: agent.active,
            source: 'blockchain'
          }));
          
          setAgents(realAgents);
          setAgentsLoading(false);
          
          // 自动选择第一个agent
          if (realAgents.length > 0) {
            console.log('🎯 Auto-selecting first agent:', realAgents[0].agent_id);
            setSelectedAgent(realAgents[0].agent_id);
          }
          return; // 成功获取真实数据，直接返回
        }
      } catch (apiError) {
        console.warn('⚠️ Failed to fetch real agents data, falling back to mock data:', apiError.message);
      }
      
      // 如果API调用失败，使用模拟数据
      console.log('📱 Using mock agents data');
      const mockAgents = [
        { 
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 
          name: 'DataAnalysisAgent',
          reputation: 85,
          capabilities: {
            data_analysis: 90,
            text_generation: 75,
            classification: 85
          }
        },
        { 
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC', 
          name: 'TextGenerationAgent',
          reputation: 75,
          capabilities: {
            text_generation: 95,
            translation: 80,
            summarization: 85
          }
        },
        { 
          agent_id: '0x90F79bf6EB2c4f870365E785982E1f101E93b906', 
          name: 'ClassificationAgent',
          reputation: 80,
          capabilities: {
            classification: 90,
            data_analysis: 70
          }
        },
        { 
          agent_id: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65', 
          name: 'TranslationAgent',
          reputation: 78,
          capabilities: {
            translation: 95,
            text_generation: 75
          }
        },
        { 
          agent_id: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc', 
          name: 'ImageRecognitionAgent',
          reputation: 82,
          capabilities: {
            image_recognition: 90,
            classification: 80
          }
        }
      ];
      
      setAgents(mockAgents);
      setAgentsLoading(false);
      setSelectedAgent(mockAgents[0].agent_id);
    } catch (error) {
      console.error('Error fetching agents:', error);
      // 即使在错误情况下也提供默认数据
      const defaultAgent = { 
        agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 
        name: 'DefaultAgent',
        reputation: 50
      };
      setAgents([defaultAgent]);
      setAgentsLoading(false);
      setSelectedAgent(defaultAgent.agent_id);
    }
  };
  
  const fetchLearningData = async (agentId) => {
    setLoading(true);
    console.log('🔄 Starting to fetch learning data for agent:', agentId);
    
    try {
      // 并行获取所有需要的数据，提高加载速度
      const [statsResponse, eventsResponse, agentsResponse, historyResponse, taskTypesResponse] = await Promise.all([
        axios.get('http://localhost:8001/tasks/learning/agent-statistics').catch(err => {
          console.warn('Stats API failed:', err.message);
          return null;
        }),
        axios.get(`http://localhost:8001/tasks/agents/${agentId}/learning-events`).catch(err => {
          console.warn('Events API failed:', err.message);
          return null;
        }),
        axios.get('http://localhost:8001/agents/').catch(err => {
          console.warn('Agents API failed:', err.message);
          return null;
        }),
        axios.get(`http://localhost:8001/tasks/agents/${agentId}/history`).catch(err => {
          console.warn('History API failed:', err.message);
          return null;
        }),
        axios.get(`http://localhost:8001/tasks/agents/${agentId}/task-types`).catch(err => {
          console.warn('Task types API failed:', err.message);
          return null;
        })
      ]);

      console.log('📊 API responses received:', {
        stats: !!statsResponse,
        events: !!eventsResponse,
        agents: !!agentsResponse,
        history: !!historyResponse,
        taskTypes: !!taskTypesResponse
      });

      // 检查是否至少有agents数据（最重要的基础数据）
      if (agentsResponse && agentsResponse.data && agentsResponse.data.agents) {
        const currentAgent = agentsResponse.data.agents.find(agent => agent.agent_id === agentId);
        
        if (currentAgent) {
          console.log('🎯 Found current agent:', currentAgent);
          
          // 从statistics API获取额外数据
          let agentStats = null;
          if (statsResponse && statsResponse.data && statsResponse.data.success) {
            agentStats = statsResponse.data.data.agents.find(agent => agent.agent_id === agentId);
            console.log('📈 Found agent stats:', agentStats);
          }
          
          // 从events API获取学习事件
          let learningEvents = [];
          if (eventsResponse && eventsResponse.data && eventsResponse.data.success) {
            learningEvents = eventsResponse.data.learning_events || [];
            console.log('📚 Found learning events:', learningEvents.length);
          }
          
          // 构建能力数据对象 - 使用标准能力集合，没有的设为0
          const standardCapabilities = [
            'data_analysis',
            'text_generation', 
            'classification',
            'translation',
            'summarization',
            'image_recognition',
            'sentiment_analysis',
            'code_generation'
          ];
          
          const capabilitiesData = {};
          
          // 初始化所有标准能力为0
          standardCapabilities.forEach(cap => {
            capabilitiesData[cap] = 0;
          });
          
          // 设置agent实际拥有的能力值
          if (currentAgent.capabilities && currentAgent.capability_weights) {
            currentAgent.capabilities.forEach((cap, index) => {
              if (standardCapabilities.includes(cap)) {
                capabilitiesData[cap] = currentAgent.capability_weights[index] || 50;
              }
            });
          }
          
          // 获取基础数据 - 使用真实的评价系统数据
          const reputation = currentAgent.reputation || 50;
          // 使用评价系统的真实completed tasks数据
          const tasksCompleted = agentStats?.recent_evaluations || currentAgent.tasks_completed || 0;
          // 使用评价系统的真实数据，而不是硬编码的默认值
          const avgScore = agentStats?.average_score || currentAgent.average_score || 0;
          const avgReward = agentStats?.average_reward || currentAgent.average_reward || 0;
          
          // 获取历史数据 - 优先使用API返回的真实历史数据
          let historyData = null;
          
          if (historyResponse && historyResponse.data && historyResponse.data.success) {
            historyData = historyResponse.data.data.history;
            console.log('📈 Using real history data with tasks:', historyData.tasks_completed);
          } else {
            // 如果没有历史数据API，基于当前真实数据生成合理的历史趋势
            console.log('⚠️ No real history data, generating realistic trend based on current data');
            historyData = {
              dates: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
              reputation: Array(6).fill(0).map((_, i) => Math.max(10, reputation - (5-i)*Math.floor(reputation/10))),
              tasks_completed: Array(6).fill(0).map((_, i) => Math.floor(tasksCompleted * (i+1)/6)),
              average_scores: Array(6).fill(0).map((_, i) => Math.max(50, avgScore - (5-i)*2)),
              rewards: Array(6).fill(0).map((_, i) => Math.max(0.1, avgReward - (5-i)*(avgReward/10)))
            };
          }
          
          // 获取任务类型分布 - 优先使用API返回的真实数据
          let taskTypesData = {};
          
          if (taskTypesResponse && taskTypesResponse.data && taskTypesResponse.data.success) {
            taskTypesData = taskTypesResponse.data.task_types;
            console.log('📊 Using real task types data:', taskTypesData);
          } else {
            // 如果没有任务类型数据，基于agent能力生成合理分布
            console.log('⚠️ No real task types data, generating based on agent capabilities');
            const agentCapabilities = currentAgent.capabilities || [];
            taskTypesData = {};
            agentCapabilities.forEach(cap => {
              taskTypesData[cap] = Math.floor(tasksCompleted * 0.2) || 1;
            });
            // 确保至少有一些基础数据
            if (Object.keys(taskTypesData).length === 0) {
              taskTypesData = {
                data_analysis: 0,
                text_generation: 0,
                classification: 0,
                translation: 0,
                summarization: 0
              };
            }
          }
          
          const realData = {
            agent_id: agentId,
            name: currentAgent.name || 'Unknown Agent',
            reputation: reputation,
            confidence_factor: agentStats?.confidence_factor || Math.min(100, reputation + 10),
            risk_tolerance: agentStats?.risk_tolerance || Math.max(30, reputation - 20),
            total_tasks: tasksCompleted,
            successful_tasks: agentStats?.successful_evaluations || 0,
            failed_tasks: agentStats?.failed_evaluations || 0,
            average_score: avgScore,
            average_reward: avgReward,
            capabilities: capabilitiesData,
            history: historyData,
            task_types: taskTypesData,
            recent_learning_events: learningEvents.length > 0 ? learningEvents.slice(0, 5).map(event => {
              // 处理真实学习事件数据结构
              const eventData = event.data || {};
              const timestamp = event.timestamp || event.created_at || Date.now();
              
              return {
                event_type: event.event_type || 'task_evaluation',
                task_id: eventData.task_id || event.task_id || 'N/A',
                score: eventData.rating || event.score || 'N/A',
                reward: eventData.reward || event.reward || 0,
                timestamp: timestamp,
                date: new Date(timestamp).toLocaleDateString(),
                description: eventData.task_title || event.description || `Learning event for ${currentAgent.name}`,
                impact: eventData.success ? 'performance_improvement' : 'performance_decline',
                changes: {
                  reputation: eventData.reputation_change || 0,
                  capabilities: (eventData.capabilities_used || []).length > 0 ? `Used: ${(eventData.capabilities_used || []).join(', ')}` : ''
                }
              };
            }) : [
              {
                event_type: 'agent_registered',
                task_id: null,
                score: null,
                reward: null,
                timestamp: (currentAgent.registered_at || Date.now()/1000) * 1000,
                date: new Date((currentAgent.registered_at || Date.now()/1000) * 1000).toLocaleDateString(),
                description: `${currentAgent.name} was registered in the system`,
                impact: 'system_registration',
                changes: {}
              }
            ],
            source: 'blockchain'
          };
          
          console.log('✅ Successfully built comprehensive real learning data:', realData);
          setLearningData(realData);
          setLoading(false);
          return; // 成功获取真实数据，提前返回
        } else {
          console.warn('⚠️ Agent not found in agents list, using mock data');
        }
      } else {
        console.warn('⚠️ No agents data available, using mock data');
      }
      
      // 使用模拟数据作为后备
      console.log('📱 Using mock learning data for agent:', agentId);
      // 立即显示模拟数据，不使用setTimeout
      // 为不同的代理生成不同的模拟数据
        let mockData;
        
        // 根据代理ID选择不同的数据模板
        switch(agentId) {
          case '0x70997970C51812dc3A010C7d01b50e0d17dc79C8': // DataAnalysisAgent
            mockData = {
              agent_id: agentId,
              name: 'DataAnalysisAgent',
              reputation: 85,
              confidence_factor: 75,
              risk_tolerance: 60,
              total_tasks: 42,
              successful_tasks: 38,
              failed_tasks: 4,
              average_score: 82,
              average_reward: 245,
              capabilities: {
                data_analysis: 90,
                text_generation: 75,
                classification: 85,
                translation: 40,
                summarization: 65,
                image_recognition: 0,
                sentiment_analysis: 0,
                code_generation: 0
              },
              history: {
                dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                reputation: [60, 65, 70, 75, 80, 85],
                tasks_completed: [5, 8, 6, 7, 10, 12],
                average_scores: [70, 75, 78, 80, 82, 85],
                rewards: [180, 200, 220, 230, 240, 245]
              },
              task_types: {
                data_analysis: 18,
                text_generation: 12,
                classification: 8,
                translation: 2,
                summarization: 2
              },
              recent_learning_events: [
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_123', 
                  score: 85, 
                  reward: 250,
                  timestamp: Date.now() - 86400000,
                  changes: { data_analysis: +2, confidence_factor: +1 }
                },
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_122', 
                  score: 92, 
                  reward: 300,
                  timestamp: Date.now() - 172800000,
                  changes: { text_generation: +3, confidence_factor: +2 }
                },
                { 
                  event_type: 'task_failed', 
                  task_id: 'task_121', 
                  score: 45, 
                  reward: 0,
                  timestamp: Date.now() - 259200000,
                  changes: { classification: -1, risk_tolerance: -2 }
                },
                { 
                  event_type: 'capability_acquired', 
                  task_id: null, 
                  score: null, 
                  reward: null,
                  timestamp: Date.now() - 345600000,
                  changes: { summarization: +10, confidence_factor: +3 }
                },
                { 
                  event_type: 'training_completed', 
                  task_id: null, 
                  score: 88, 
                  reward: 150,
                  timestamp: Date.now() - 432000000,
                  changes: { data_analysis: +5, risk_tolerance: +2 }
                }
              ]
            };
            break;
            
          case '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC': // TextGenerationAgent
            mockData = {
              agent_id: agentId,
              name: 'TextGenerationAgent',
              reputation: 75,
              confidence_factor: 80,
              risk_tolerance: 50,
              total_tasks: 28,
              successful_tasks: 25,
              failed_tasks: 3,
              average_score: 78,
              average_reward: 220,
              capabilities: {
                data_analysis: 55,
                text_generation: 95,
                classification: 60,
                translation: 80,
                summarization: 85,
                image_recognition: 0,
                sentiment_analysis: 0,
                code_generation: 0
              },
              history: {
                dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                reputation: [55, 60, 65, 70, 72, 75],
                tasks_completed: [3, 5, 4, 6, 5, 8],
                average_scores: [65, 70, 72, 75, 76, 78],
                rewards: [150, 175, 190, 200, 210, 220]
              },
              task_types: {
                data_analysis: 4,
                text_generation: 15,
                classification: 3,
                translation: 8,
                summarization: 10
              },
              recent_learning_events: [
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_105', 
                  score: 90, 
                  reward: 300,
                  timestamp: Date.now() - 43200000,
                  changes: { text_generation: +2, confidence_factor: +1 }
                },
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_103', 
                  score: 85, 
                  reward: 250,
                  timestamp: Date.now() - 129600000,
                  changes: { summarization: +3, confidence_factor: +1 }
                },
                { 
                  event_type: 'task_failed', 
                  task_id: 'task_098', 
                  score: 40, 
                  reward: 0,
                  timestamp: Date.now() - 216000000,
                  changes: { data_analysis: -2, risk_tolerance: -1 }
                },
                { 
                  event_type: 'capability_improved', 
                  task_id: null, 
                  score: null, 
                  reward: null,
                  timestamp: Date.now() - 302400000,
                  changes: { translation: +5, text_generation: +3 }
                }
              ]
            };
            break;
            
          default: // 默认数据模板
            mockData = {
              agent_id: agentId,
              name: 'Agent',
              reputation: 70,
              confidence_factor: 65,
              risk_tolerance: 55,
              total_tasks: 25,
              successful_tasks: 20,
              failed_tasks: 5,
              average_score: 75,
              average_reward: 200,
              capabilities: {
                data_analysis: 70,
                text_generation: 70,
                classification: 70,
                translation: 70,
                summarization: 70,
                image_recognition: 0,
                sentiment_analysis: 0,
                code_generation: 0
              },
              history: {
                dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                reputation: [50, 55, 60, 65, 68, 70],
                tasks_completed: [3, 4, 5, 6, 7, 8],
                average_scores: [65, 68, 70, 72, 74, 75],
                rewards: [150, 160, 175, 185, 195, 200]
              },
              task_types: {
                data_analysis: 5,
                text_generation: 5,
                classification: 5,
                translation: 5,
                summarization: 5
              },
              recent_learning_events: [
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_xyz', 
                  score: 75, 
                  reward: 200,
                  timestamp: Date.now() - 86400000,
                  changes: { data_analysis: +1, confidence_factor: +1 }
                },
                { 
                  event_type: 'task_completed', 
                  task_id: 'task_abc', 
                  score: 80, 
                  reward: 220,
                  timestamp: Date.now() - 172800000,
                  changes: { text_generation: +2, confidence_factor: +1 }
                },
                { 
                  event_type: 'task_failed', 
                  task_id: 'task_def', 
                  score: 40, 
                  reward: 0,
                  timestamp: Date.now() - 259200000,
                  changes: { classification: -1, risk_tolerance: -1 }
                }
              ]
            };
        }
        
        // 为所有mock数据添加source标识
        mockData.source = 'mock';
        setLearningData(mockData);
        setLoading(false);
      
    } catch (error) {
      console.error('Error fetching learning data:', error);
      setLoading(false);
      
      // 即使在错误情况下也提供默认数据
      const defaultData = {
        agent_id: agentId,
        name: 'Unknown Agent',
        reputation: 50,
        confidence_factor: 50,
        risk_tolerance: 50,
        total_tasks: 10,
        successful_tasks: 8,
        failed_tasks: 2,
        average_score: 70,
        average_reward: 150,
        capabilities: {
          data_analysis: 50,
          text_generation: 50,
          classification: 50,
          translation: 50,
          summarization: 50,
          image_recognition: 0,
          sentiment_analysis: 0,
          code_generation: 0
        },
        history: {
          dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          reputation: [40, 42, 45, 47, 49, 50],
          tasks_completed: [1, 2, 2, 2, 1, 2],
          average_scores: [60, 65, 67, 68, 69, 70],
          rewards: [100, 120, 130, 140, 145, 150]
        },
        task_types: {
          data_analysis: 2,
          text_generation: 2,
          classification: 2,
          translation: 2,
          summarization: 2
        },
        recent_learning_events: [
          { 
            event_type: 'task_completed', 
            task_id: 'task_default', 
            score: 70, 
            reward: 150,
            timestamp: Date.now() - 86400000,
            changes: { data_analysis: +1, confidence_factor: +1 }
          }
        ]
      };
      setLearningData(defaultData);
    }
  };
  
  const handleAgentChange = (event) => {
    setSelectedAgent(event.target.value);
  };
  
  const handleTabChange = (_, newValue) => {
    setTabValue(newValue);
  };
  
  // Format address to show only first and last few characters
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };
  
  // Chart data for capabilities - use standard capability set with 0 for missing ones
  const standardCapabilities = [
    'data_analysis',
    'text_generation', 
    'classification',
    'translation',
    'summarization',
    'image_recognition',
    'sentiment_analysis',
    'code_generation'
  ];
  
  const capabilitiesData = {
    labels: standardCapabilities.map(cap => 
      // Format capability names for display
      cap.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    ),
    datasets: [
      {
        label: 'Capability Score',
        data: learningData && learningData.capabilities ? standardCapabilities.map(cap => 
          learningData.capabilities[cap] || 0
        ) : Array(standardCapabilities.length).fill(0),
        backgroundColor: 'rgba(58, 134, 255, 0.2)',
        borderColor: '#3a86ff',
        borderWidth: 2,
        pointBackgroundColor: '#3a86ff',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3a86ff'
      }
    ]
  };
  
  // Chart data for reputation history
  const reputationData = {
    labels: learningData?.history.dates || [],
    datasets: [
      {
        label: 'Reputation',
        data: learningData?.history.reputation || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };
  
  // Chart data for task performance
  const taskPerformanceData = {
    labels: learningData?.history.dates || [],
    datasets: [
      {
        label: 'Tasks Completed',
        data: learningData?.history.tasks_completed || [],
        backgroundColor: '#3a86ff',
        borderColor: '#3a86ff',
        borderWidth: 1
      }
    ]
  };
  
  // Chart data for task types
  const taskTypesData = {
    labels: Object.keys(learningData?.task_types || {}),
    datasets: [
      {
        label: 'Number of Tasks',
        data: Object.values(learningData?.task_types || {}),
        backgroundColor: [
          '#3a86ff', 
          '#10b981', 
          '#f59e0b', 
          '#ef4444', 
          '#8b5cf6'
        ],
        borderWidth: 0
      }
    ]
  };
  
  // Chart options
  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#d1d5db'
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#d1d5db'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        ticks: {
          color: '#d1d5db'
        },
        grid: {
          display: false
        }
      }
    }
  };
  
  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 100,
        angleLines: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        pointLabels: {
          color: '#d1d5db',
          font: {
            size: 11
          }
        },
        ticks: {
          color: '#d1d5db',
          backdropColor: 'transparent',
          stepSize: 20
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };
  
  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#d1d5db'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        ticks: {
          color: '#d1d5db'
        },
        grid: {
          display: false
        }
      }
    }
  };
  
  if (!selectedAgent) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <Typography variant="h5" color="text.secondary">
          Select an agent to view learning data
        </Typography>
      </Box>
    );
  }
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4">Learning Dashboard</Typography>
          {learningData && (
            <Chip
              label={learningData.source === 'blockchain' ? 'Real Data' : 'Mock Data'}
              color={learningData.source === 'blockchain' ? 'success' : 'default'}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="agent-select-label">Select Agent</InputLabel>
          <Select
            labelId="agent-select-label"
            value={selectedAgent}
            label="Select Agent"
            onChange={handleAgentChange}
          >
            {agents.map((agent) => (
              <MenuItem key={agent.agent_id} value={agent.agent_id}>
                {agent.name || formatAddress(agent.agent_id)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      {agentsLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>Loading agents...</Typography>
        </Box>
      ) : !selectedAgent ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <Typography variant="h6">Select an agent to view learning data</Typography>
        </Box>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>Loading learning data...</Typography>
        </Box>
      ) : !learningData ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <Typography variant="h6">No learning data available</Typography>
        </Box>
      ) : (
        <>
          <Box sx={{ mb: 3 }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="Overview" />
              <Tab label="Capabilities" />
              <Tab label="Performance" />
              <Tab label="Learning Events" />
            </Tabs>
          </Box>
          
          {/* Overview Tab */}
          {tabValue === 0 && (
            <Grid container spacing={3}>
              {/* Stats Cards */}
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Reputation
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h3" component="div" sx={{ mr: 1 }}>
                        {learningData.reputation}
                      </Typography>
                      <TrendingUpIcon color="success" />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      +5 from last month
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Tasks Completed
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h3" component="div" sx={{ mr: 1 }}>
                        {learningData.total_tasks}
                      </Typography>
                      <TrendingUpIcon color="success" />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate: {learningData.total_tasks > 0 ? Math.round((learningData.successful_tasks / learningData.total_tasks) * 100) : 0}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Average Score
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h3" component="div" sx={{ mr: 1 }}>
                        {learningData.average_score}
                      </Typography>
                      <TrendingUpIcon color="success" />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      +3 from last month
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Average Reward
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h3" component="div" sx={{ mr: 1 }}>
                        {learningData.average_reward}
                      </Typography>
                      <TrendingUpIcon color="success" />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      +15 from last month
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Reputation Chart */}
              <Grid item xs={12} md={8}>
                <Card>
                  <CardHeader title="Reputation History" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {reputationData && reputationData.labels && reputationData.datasets ? (
                      <Line data={reputationData} options={lineOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Capabilities Chart */}
              <Grid item xs={12} md={4}>
                <Card>
                  <CardHeader title="Capabilities" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {capabilitiesData && capabilitiesData.labels && capabilitiesData.datasets ? (
                      <Radar data={capabilitiesData} options={radarOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Task Types Chart */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Task Types Distribution" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {taskTypesData && taskTypesData.labels && taskTypesData.datasets ? (
                      <Bar data={taskTypesData} options={barOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Task Performance Chart */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Task Performance" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {taskPerformanceData && taskPerformanceData.labels && taskPerformanceData.datasets ? (
                      <Bar data={taskPerformanceData} options={barOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          
          {/* Capabilities Tab */}
          {tabValue === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Capability Scores" />
                  <Divider />
                  <CardContent sx={{ height: 400 }}>
                    {capabilitiesData && capabilitiesData.labels && capabilitiesData.datasets ? (
                      <Radar data={capabilitiesData} options={radarOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Capability Details" />
                  <Divider />
                  <CardContent>
                    {Object.entries(learningData?.capabilities || {}).map(([capability, score]) => (
                      <Box key={capability} sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                            {capability.replace(/_/g, ' ')}
                          </Typography>
                          <Typography variant="body1" fontWeight="bold">
                            {score}/100
                          </Typography>
                        </Box>
                        <Slider
                          value={score}
                          min={0}
                          max={100}
                          valueLabelDisplay="auto"
                          disabled
                          sx={{
                            '& .MuiSlider-thumb': {
                              display: 'none',
                            },
                          }}
                        />
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="Task Type Distribution" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {taskTypesData && taskTypesData.labels && taskTypesData.datasets ? (
                      <Bar data={taskTypesData} options={barOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          
          {/* Performance Tab */}
          {tabValue === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Reputation Growth" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {reputationData && reputationData.labels && reputationData.datasets ? (
                      <Line data={reputationData} options={lineOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Tasks Completed" />
                  <Divider />
                  <CardContent sx={{ height: 300 }}>
                    {taskPerformanceData && taskPerformanceData.labels && taskPerformanceData.datasets ? (
                      <Bar data={taskPerformanceData} options={barOptions} />
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                        <CircularProgress />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="Agent Parameters" />
                  <Divider />
                  <CardContent>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={4}>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="body1" gutterBottom>
                            Confidence Factor
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Slider
                              value={learningData.confidence_factor}
                              min={0}
                              max={100}
                              valueLabelDisplay="auto"
                              disabled
                              sx={{ flexGrow: 1, mr: 2 }}
                            />
                            <Typography variant="body1" fontWeight="bold">
                              {learningData.confidence_factor}%
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} md={4}>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="body1" gutterBottom>
                            Risk Tolerance
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Slider
                              value={learningData.risk_tolerance}
                              min={0}
                              max={100}
                              valueLabelDisplay="auto"
                              disabled
                              sx={{ flexGrow: 1, mr: 2 }}
                            />
                            <Typography variant="body1" fontWeight="bold">
                              {learningData.risk_tolerance}%
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} md={4}>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="body1" gutterBottom>
                            Success Rate
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Slider
                              value={learningData.total_tasks > 0 ? Math.round((learningData.successful_tasks / learningData.total_tasks) * 100) : 0}
                              min={0}
                              max={100}
                              valueLabelDisplay="auto"
                              disabled
                              sx={{ flexGrow: 1, mr: 2 }}
                            />
                            <Typography variant="body1" fontWeight="bold">
                              {learningData.total_tasks > 0 ? Math.round((learningData.successful_tasks / learningData.total_tasks) * 100) : 0}%
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          
          {/* Learning Events Tab */}
          {tabValue === 3 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="Recent Learning Events" />
                  <Divider />
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Event Type</TableCell>
                          <TableCell>Task ID</TableCell>
                          <TableCell>Score</TableCell>
                          <TableCell>Reward</TableCell>
                          <TableCell>Date</TableCell>
                          <TableCell>Changes</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {learningData.recent_learning_events.map((event, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  textTransform: 'capitalize',
                                  color: event.event_type === 'task_evaluation' && event.score >= 1 ? 'success.main' : 
                                         event.event_type === 'task_evaluation' && event.score < 1 ? 'error.main' : 'info.main'
                                }}
                              >
                                {event.event_type === 'task_evaluation' ? 'Task Evaluation' : 
                                 event.event_type.replace('_', ' ')}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ mb: 0.5 }}>
                                {!event.task_id || event.task_id === 'N/A' ? 'N/A' : `${event.task_id.substring(0, 8)}...`}
                              </Typography>
                              {event.description && event.description !== `Learning event for ${learningData.name}` && (
                                <Typography variant="caption" color="text.secondary">
                                  {event.description}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>{event.score}</TableCell>
                            <TableCell>{event.reward}</TableCell>
                            <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                            <TableCell>
                              {Object.entries(event.changes || {}).map(([param, change]) => {
                                // 处理不同类型的变化数据
                                if (param === 'reputation' && typeof change === 'number' && change !== 0) {
                                  return (
                                    <Box key={param} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                                      <Typography variant="body2" sx={{ mr: 1, textTransform: 'capitalize' }}>
                                        Reputation:
                                      </Typography>
                                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        {change > 0 ? (
                                          <>
                                            <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                                            <Typography variant="body2" color="success.main">
                                              +{change}
                                            </Typography>
                                          </>
                                        ) : (
                                          <>
                                            <TrendingDownIcon color="error" fontSize="small" sx={{ mr: 0.5 }} />
                                            <Typography variant="body2" color="error.main">
                                              {change}
                                            </Typography>
                                          </>
                                        )}
                                      </Box>
                                    </Box>
                                  );
                                } else if (param === 'capabilities' && change && typeof change === 'string') {
                                  return (
                                    <Box key={param} sx={{ mb: 0.5 }}>
                                      <Typography variant="body2" color="text.secondary">
                                        {change}
                                      </Typography>
                                    </Box>
                                  );
                                }
                                return null;
                              })}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Card>
              </Grid>
            </Grid>
          )}
        </>
      )}
    </Box>
  );
};

export default LearningDashboard; 