import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  CardHeader,
  Typography, 
  Grid, 
  Avatar, 
  Chip, 
  LinearProgress, 
  Divider, 
  Button, 
  IconButton, 
  Tab, 
  Tabs, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  CircularProgress,
  useTheme,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Slider,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  Psychology as PsychologyIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as HourglassEmptyIcon,
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  AccessTime as AccessTimeIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { ResponsiveRadar } from '@nivo/radar';
import { ResponsiveLine } from '@nivo/line';
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
import { Radar, Line, Bar } from 'react-chartjs-2';
import { agentApi } from '../services/api';

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

const AgentDetails = () => {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  
  useEffect(() => {
    fetchAgentDetails();
  }, [agentId]);
  
  // 生成模拟任务数据
  const generateMockRecentTasks = (agentId) => {
    return [
      {
        task_id: '1',
        description: 'Analyze market trends for Q3 2023',
        status: 'completed',
        score: 85,
        reward: 0.5,
        completed_at: Math.floor(Date.now() / 1000) - 86400
      },
      {
        task_id: '2',
        description: 'Generate quarterly financial report',
        status: 'assigned',
        score: null,
        reward: 0.3,
        completed_at: null
      },
      {
        task_id: '3',
        description: 'Classify customer feedback into categories',
        status: 'failed',
        score: 45,
        reward: 0.15,
        completed_at: Math.floor(Date.now() / 1000) - 259200
      }
    ];
  };
  
  // 生成模拟学习事件
  const generateMockLearningEvents = (agentId) => {
    return [
      {
        event_id: '1',
        description: 'Improved classification accuracy by 5%',
        timestamp: Math.floor(Date.now() / 1000) - 172800,
        impact: 'positive',
        affected_capability: 'classification',
        score_change: 5
      },
      {
        event_id: '2',
        description: 'Expanded vocabulary for text generation',
        timestamp: Math.floor(Date.now() / 1000) - 345600,
        impact: 'positive',
        affected_capability: 'generation',
        score_change: 3
      }
    ];
  };
  
  // 生成模拟任务类型统计
  const generateMockTaskTypes = (capabilities) => {
    if (!capabilities || capabilities.length === 0) {
      return {
        analysis: 18,
        generation: 12,
        classification: 8,
        translation: 2,
        summarization: 2
      };
    }
    
    const taskTypes = {};
    capabilities.forEach((cap, index) => {
      const count = Math.floor(Math.random() * 15) + 5;
      taskTypes[cap] = count;
    });
    
    return taskTypes;
  };

  const fetchAgentDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      // 从API获取代理详情
      const response = await agentApi.getAgentById(agentId);
      console.log('Agent API response:', response);
      
      if (response && (response.agent_id || response.name)) {
        console.log('Raw API response:', response);
        
        // 检查是否是增强Mock数据（含有详细信息）
        if (response.source === 'enhanced_mock_v2' || response.profile || response.capability_descriptions) {
          console.log('Using enhanced mock data format');
          
          // 直接使用增强Mock数据的完整格式
          const mappedAgent = {
            ...response, // 保留所有原始数据
            
            // 确保时间格式正确
            registration_date: response.registration_date ? 
              (typeof response.registration_date === 'string' ? 
                new Date(response.registration_date).getTime() / 1000 : 
                response.registration_date) : 
              Math.floor(Date.now() / 1000),
              
            // 使用真实的任务数据，不再生成mock数据
            recent_tasks: response.recent_tasks || [],
            learning_events: response.learning_events || generateMockLearningEvents(response.agent_id),
            task_types: response.task_types || generateMockTaskTypes(response.capabilities),
            
            // 使用增强历史数据或生成默认数据
            history: response.history || {
              dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
              reputation: [60, 70, 75, 80, 85, response.reputation || 50],
              tasks_completed: [5, 10, 15, 20, 25, response.total_tasks || 30],
              average_scores: [3.2, 3.5, 3.8, 4.0, 4.2, response.average_score || 4.0],
              rewards: [0, 50, 100, 150, 200, parseFloat(response.total_earnings || 250)]
            }
          };
          
          console.log('Enhanced mapped agent:', mappedAgent);
          setAgent(mappedAgent);
        } else {
          console.log('Using standard backend data format');
          
          // 传统后端数据格式
          const mappedAgent = {
            agent_id: response.agent_id,
            name: response.name || `Agent ${response.agent_id?.slice(-4)}`,
            registration_date: response.registeredAt || response.registration_date,
            reputation: response.reputation || 0,
            confidence_factor: response.confidence_factor || 50,
            risk_tolerance: response.risk_tolerance || 50,
            total_tasks: response.workload || response.total_tasks || 0,
            successful_tasks: response.workload || response.successful_tasks || 0,
            failed_tasks: response.failed_tasks || 0,
            average_score: response.average_score || 0,
            average_reward: response.average_reward || 0,
            capabilities: response.capabilities || [],
            capability_weights: response.capability_weights || [],
            task_history: response.task_history || [],
            learning_events: response.learning_events || [],
            active: response.active !== false,
            metadataURI: response.metadataURI,
            agentType: response.agentType,
            owner: response.owner,
            
            // 使用真实的任务数据，不再生成mock数据
            recent_tasks: response.recent_tasks || [],
            task_types: generateMockTaskTypes(response.capabilities),
            
            // 为图表生成一些模拟历史数据
            history: {
              dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
              reputation: [Math.max(0, (response.reputation || 0) - 25), Math.max(0, (response.reputation || 0) - 20), Math.max(0, (response.reputation || 0) - 15), Math.max(0, (response.reputation || 0) - 10), Math.max(0, (response.reputation || 0) - 5), response.reputation || 0],
              tasks_completed: [0, 1, 2, 3, Math.max(0, (response.workload || 0) - 2), response.workload || 0],
              average_scores: [70, 75, 78, 80, 82, 85],
              rewards: [0, 50, 100, 150, 200, 250]
            }
          };
          
          console.log('Standard mapped agent:', mappedAgent);
          setAgent(mappedAgent);
        }
      } else {
        throw new Error('Agent data not found or failed to load');
      }
    } catch (error) {
      console.error('Error fetching agent details:', error);
      setError('Failed to fetch agent details. Using sample data instead.');
      setSnackbarOpen(true);
      
      // 使用示例数据作为后备
      const mockAgent = {
        agent_id: agentId,
        registration_date: Math.floor(Date.now() / 1000) - 2592000, // 30 days ago
        reputation: 85,
        confidence_factor: 75,
        risk_tolerance: 60,
        total_tasks: 42,
        successful_tasks: 38,
        failed_tasks: 4,
        average_score: 82,
        average_reward: 245,
        capabilities: {
          analysis: 80,
          generation: 65,
          classification: 90,
          translation: 50,
          summarization: 70
        },
        history: {
          dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          reputation: [60, 65, 70, 75, 80, 85],
          tasks_completed: [5, 8, 6, 7, 10, 12],
          average_scores: [70, 75, 78, 80, 82, 85],
          rewards: [180, 200, 220, 230, 240, 245]
        },
        task_types: {
          analysis: 18,
          generation: 12,
          classification: 8,
          translation: 2,
          summarization: 2
        },
        recent_tasks: [
          {
            task_id: '1',
            description: 'Analyze market trends for Q3 2023',
            status: 'completed',
            score: 85,
            reward: 0.5,
            completed_at: Math.floor(Date.now() / 1000) - 86400 // 1 day ago
          },
          {
            task_id: '2',
            description: 'Generate quarterly financial report',
            status: 'assigned',
            score: null,
            reward: 0.3,
            completed_at: null
          },
          {
            task_id: '3',
            description: 'Classify customer feedback into categories',
            status: 'failed',
            score: 45,
            reward: 0.15,
            completed_at: Math.floor(Date.now() / 1000) - 259200 // 3 days ago
          }
        ],
        learning_events: [
          {
            event_id: '1',
            description: 'Improved classification accuracy by 5%',
            timestamp: Math.floor(Date.now() / 1000) - 172800, // 2 days ago
            impact: 'positive',
            affected_capability: 'classification',
            score_change: 5
          },
          {
            event_id: '2',
            description: 'Expanded vocabulary for text generation',
            timestamp: Math.floor(Date.now() / 1000) - 345600, // 4 days ago
            impact: 'positive',
            affected_capability: 'generation',
            score_change: 3
          },
          {
            event_id: '3',
            description: 'Failed to properly analyze complex data patterns',
            timestamp: Math.floor(Date.now() / 1000) - 518400, // 6 days ago
            impact: 'negative',
            affected_capability: 'analysis',
            score_change: -2
          }
        ]
      };
      
      setAgent(mockAgent);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Format address to show only first and last few characters
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };
  
  // Generate avatar color based on address
  const generateAvatarColor = (address) => {
    if (!address) return '#9e9e9e';
    const hash = address.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0);
    }, 0);
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
  };
  
  // 定义标准的capabilities列表
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

  // 处理能力数据 - 始终使用雷达图，未选中的能力设为0
  const processCapabilitiesData = () => {
    console.log('Processing capabilities data:', {
      capabilities: agent?.capabilities,
      capability_weights: agent?.capability_weights
    });
    
    // 初始化所有标准capabilities为0
    const capabilityMap = {};
    standardCapabilities.forEach(cap => {
      capabilityMap[cap] = 0;
    });
    
    // 如果agent有capabilities数据，填入对应的值
    if (agent && agent.capabilities && Array.isArray(agent.capabilities) && agent.capabilities.length > 0) {
      agent.capabilities.forEach((capability, index) => {
        if (standardCapabilities.includes(capability)) {
          const weight = agent.capability_weights && agent.capability_weights[index] !== undefined 
            ? agent.capability_weights[index] 
            : 75; // 默认权重
          capabilityMap[capability] = weight;
        }
      });
    } else if (agent && agent.capabilities && typeof agent.capabilities === 'object') {
      // 如果是对象格式
      Object.entries(agent.capabilities).forEach(([capability, weight]) => {
        if (standardCapabilities.includes(capability)) {
          capabilityMap[capability] = weight;
        }
      });
    }
    
    // 转换为图表数据格式
    const labels = standardCapabilities.map(cap => {
      // 处理capability名称，使其更可读
      return cap.replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    });
    
    const scores = standardCapabilities.map(cap => capabilityMap[cap]);
    
    console.log('Chart data prepared:', { labels, scores, capabilityMap });
    
    return {
      type: 'radar',
      labels: labels,
      datasets: [{
        label: 'Capability Score',
        data: scores,
        backgroundColor: 'rgba(58, 134, 255, 0.2)',
        borderColor: '#3a86ff',
        borderWidth: 2,
        pointBackgroundColor: '#3a86ff',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3a86ff'
      }]
    };
  };
  
  // 处理声誉历史数据 - 基于真实注册时间和当前时间
  const processReputationData = () => {
    console.log('Processing reputation data:', {
      agent_history: agent?.history,
      registration_date: agent?.registration_date,
      current_reputation: agent?.reputation
    });
    
    if (!agent) {
      return {
        labels: [],
        datasets: [{
          label: 'Reputation',
          data: [],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4
        }]
      };
    }
    
    // 基于真实的注册时间创建时间轴
    const currentTime = Date.now() / 1000;
    const registrationTime = agent.registration_date || (currentTime - 30 * 24 * 3600); // 默认30天前
    const timeDiff = currentTime - registrationTime;
    const daysDiff = Math.max(1, Math.floor(timeDiff / (24 * 3600)));
    
    console.log('Time analysis:', {
      currentTime,
      registrationTime,
      daysDiff,
      registrationDate: new Date(registrationTime * 1000).toLocaleDateString()
    });
    
    // 创建基于实际时间的标签和数据点
    let labels = [];
    let reputationHistory = [];
    const currentRep = agent.reputation || 50;
    
    if (daysDiff <= 7) {
      // 注册不到一周 - 按天显示
      for (let i = 0; i <= Math.min(daysDiff, 6); i++) {
        const date = new Date((registrationTime + i * 24 * 3600) * 1000);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // 声誉增长模式：从初始值逐渐增长到当前值
        const progress = i / Math.max(1, daysDiff);
        const initialRep = Math.max(10, currentRep - 40);
        const repValue = Math.round(initialRep + (currentRep - initialRep) * progress);
        reputationHistory.push(repValue);
      }
    } else if (daysDiff <= 30) {
      // 注册1周到1个月 - 按周显示
      const weeks = Math.ceil(daysDiff / 7);
      for (let i = 0; i < weeks; i++) {
        const date = new Date((registrationTime + i * 7 * 24 * 3600) * 1000);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        const progress = i / Math.max(1, weeks - 1);
        const initialRep = Math.max(10, currentRep - 35);
        const repValue = Math.round(initialRep + (currentRep - initialRep) * progress);
        reputationHistory.push(repValue);
      }
    } else {
      // 注册超过1个月 - 按月显示
      const months = Math.min(6, Math.ceil(daysDiff / 30));
      for (let i = 0; i < months; i++) {
        const date = new Date((registrationTime + i * 30 * 24 * 3600) * 1000);
        labels.push(date.toLocaleDateString('en-US', { month: 'short' }));
        
        const progress = i / Math.max(1, months - 1);
        const initialRep = Math.max(10, currentRep - 30);
        const repValue = Math.round(initialRep + (currentRep - initialRep) * progress);
        reputationHistory.push(repValue);
      }
    }
    
    // 确保最后一个点是当前声誉值
    if (reputationHistory.length > 0) {
      reputationHistory[reputationHistory.length - 1] = currentRep;
    }
    
    console.log('Generated reputation history:', { labels, reputationHistory });
    
    return {
      labels: labels,
      datasets: [{
        label: 'Reputation',
        data: reputationHistory,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    };
  };
  
  const capabilitiesData = processCapabilitiesData();
  const reputationData = processReputationData();
  
  // Chart options
  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        pointLabels: {
          color: '#d1d5db'
        },
        ticks: {
          color: '#d1d5db',
          backdropColor: 'transparent',
          beginAtZero: true,
          max: 100
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
        max: 100,
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
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!agent) {
    return (
      <Box sx={{ textAlign: 'center', py: 5 }}>
        <Typography variant="h6" color="text.secondary">
          Agent not found
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/agents')}
          sx={{ mt: 2 }}
        >
          Back to Agents
        </Button>
      </Box>
    );
  }
  
  return (
    <Box>
      <Snackbar 
        open={snackbarOpen} 
        autoHideDuration={6000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity="warning" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/agents')} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4">
          Agent Details
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchAgentDetails}
          sx={{ mr: 1 }}
        >
          Refresh
        </Button>
      </Box>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Avatar 
            sx={{ 
              width: 64, 
              height: 64, 
              bgcolor: generateAvatarColor(agent.agent_id),
              mr: 2
            }}
          >
            {agent.agent_id.substring(2, 4)}
          </Avatar>
          <Box>
            <Typography variant="h5">
              {agent.name || formatAddress(agent.agent_id)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatAddress(agent.agent_id)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Registered on {agent.registration_date ? 
                new Date(typeof agent.registration_date === 'string' ? 
                  new Date(agent.registration_date) : 
                  agent.registration_date * 1000).toLocaleDateString() : 
                'Unknown'}
            </Typography>
            {agent.experience_level && (
              <Typography variant="body2" color="text.secondary">
                Experience: {agent.experience_level} | Tier: {agent.performance_tier}
              </Typography>
            )}
            {agent.status && (
              <Chip 
                label={agent.status.charAt(0).toUpperCase() + agent.status.slice(1)} 
                size="small" 
                color={agent.status === 'active' ? 'success' : agent.status === 'busy' ? 'warning' : 'default'}
                sx={{ mt: 0.5 }}
              />
            )}
            {agent.metadataURI && (
              <Typography variant="body2" color="text.secondary">
                Type: {agent.agentType === 1 ? 'LLM' : agent.agentType === 2 ? 'Orchestrator' : agent.agentType === 3 ? 'Evaluator' : 'Unknown'}
              </Typography>
            )}
          </Box>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Reputation
              </Typography>
              <Typography variant="h4">
                {agent.reputation}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Tasks Completed
              </Typography>
              <Typography variant="h4">
                {agent.successful_tasks}/{agent.total_tasks}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Average Score
              </Typography>
              <Typography variant="h4">
                {typeof agent.average_score === 'number' ? agent.average_score.toFixed(1) : agent.average_score}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {agent.total_earnings ? 'Total Earnings' : 'Average Reward'}
              </Typography>
              <Typography variant="h4">
                {agent.total_earnings || agent.average_reward}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      <Box sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" />
          <Tab label="Capabilities" />
          <Tab label="Tasks" />
          <Tab label="Learning" />
        </Tabs>
      </Box>
      
      {/* Overview Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Capabilities" />
              <Divider />
              <CardContent sx={{ height: 300 }}>
                <Radar data={capabilitiesData} options={radarOptions} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Reputation History" />
              <Divider />
              <CardContent sx={{ height: 300 }}>
                <Line data={reputationData} options={lineOptions} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Agent Parameters" />
              <Divider />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Confidence Factor
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ flexGrow: 1, mr: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={agent.confidence_factor} 
                            sx={{ height: 10, borderRadius: 5 }}
                          />
                        </Box>
                        <Typography variant="body2">
                          {agent.confidence_factor}%
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Risk Tolerance
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ flexGrow: 1, mr: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={agent.risk_tolerance} 
                            sx={{ height: 10, borderRadius: 5 }}
                          />
                        </Box>
                        <Typography variant="body2">
                          {agent.risk_tolerance}%
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                      <Typography variant="body2">
                        {Math.round((agent.successful_tasks / agent.total_tasks) * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(agent.successful_tasks / agent.total_tasks) * 100} 
                      color="success"
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader 
                title="Recent Tasks" 
                action={
                  <Button 
                    size="small" 
                    onClick={() => navigate(`/tasks?agent=${agent.agent_id}`)}
                  >
                    View All
                  </Button>
                }
              />
              <Divider />
              <List>
                {agent.recent_tasks && agent.recent_tasks.slice(0, 3).map((task) => (
                  <React.Fragment key={task.task_id}>
                    <ListItem 
                      button 
                      onClick={() => navigate(`/tasks/${task.task_id}`)}
                    >
                      <ListItemIcon>
                        {task.status === 'completed' && <CheckCircleIcon color="success" />}
                        {task.status === 'assigned' && <AccessTimeIcon color="warning" />}
                        {task.status === 'failed' && <ErrorIcon color="error" />}
                      </ListItemIcon>
                      <ListItemText 
                        primary={task.title || task.description}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {task.description && task.title ? task.description : ''}
                            </Typography>
                            <Typography variant="caption">
                              Reward: {task.reward} ETH
                              {task.score && ` • Score: ${task.score}`}
                              {task.is_collaboration && ` • ${task.role === 'primary' ? 'Lead Agent' : 'Collaborator'} in team`}
                            </Typography>
                          </Box>
                        }
                      />
                      <Chip 
                        label={task.status.charAt(0).toUpperCase() + task.status.slice(1)} 
                        size="small"
                        color={
                          task.status === 'completed' ? 'success' : 
                          task.status === 'failed' ? 'error' : 'warning'
                        }
                        variant="outlined"
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
                {(!agent.recent_tasks || agent.recent_tasks.length === 0) && (
                  <ListItem>
                    <ListItemText primary="No recent tasks" />
                  </ListItem>
                )}
              </List>
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
                <Radar data={capabilitiesData} options={radarOptions} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Capability Details" />
              <Divider />
              <CardContent>
                {(() => {
                  // 使用与雷达图相同的逻辑来处理capabilities
                  const capabilityMap = {};
                  standardCapabilities.forEach(cap => {
                    capabilityMap[cap] = 0;
                  });
                  
                  // 填入agent的实际capabilities数据
                  if (agent && agent.capabilities && Array.isArray(agent.capabilities) && agent.capabilities.length > 0) {
                    agent.capabilities.forEach((capability, index) => {
                      if (standardCapabilities.includes(capability)) {
                        const weight = agent.capability_weights && agent.capability_weights[index] !== undefined 
                          ? agent.capability_weights[index] 
                          : 75;
                        capabilityMap[capability] = weight;
                      }
                    });
                  } else if (agent && agent.capabilities && typeof agent.capabilities === 'object') {
                    Object.entries(agent.capabilities).forEach(([capability, weight]) => {
                      if (standardCapabilities.includes(capability)) {
                        capabilityMap[capability] = weight;
                      }
                    });
                  }
                  
                  // 渲染所有标准capabilities
                  return standardCapabilities.map((capability, index) => {
                    const weight = capabilityMap[capability];
                    const formattedCapability = capability.replace(/_/g, ' ')
                      .split(' ')
                      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                      .join(' ');
                    
                    return (
                      <Box key={index} sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body1" sx={{ opacity: weight > 0 ? 1 : 0.5 }}>
                            {formattedCapability}
                          </Typography>
                          <Typography variant="body1" fontWeight="bold" sx={{ opacity: weight > 0 ? 1 : 0.5 }}>
                            {weight}/100
                          </Typography>
                        </Box>
                        <Slider
                          value={weight}
                          min={0}
                          max={100}
                          valueLabelDisplay="auto"
                          disabled
                          sx={{
                            '& .MuiSlider-thumb': {
                              display: 'none',
                            },
                            '& .MuiSlider-track': {
                              backgroundColor: weight === 0 ? '#e0e0e0' : weight >= 80 ? '#4caf50' : weight >= 60 ? '#2196f3' : '#ff9800',
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            },
                            opacity: weight > 0 ? 1 : 0.5,
                          }}
                        />
                      </Box>
                    );
                  });
                })()}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Task Type Distribution" />
              <Divider />
              <CardContent>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Task Type</TableCell>
                        <TableCell align="right">Count</TableCell>
                        <TableCell align="right">Percentage</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {agent.task_types && Object.entries(agent.task_types).map(([type, count]) => {
                        const percentage = agent.total_tasks > 0 
                          ? Math.round((count / agent.total_tasks) * 100) 
                          : 0;
                        
                        return (
                          <TableRow key={type}>
                            <TableCell sx={{ textTransform: 'capitalize' }}>{type}</TableCell>
                            <TableCell align="right">{count}</TableCell>
                            <TableCell align="right">{percentage}%</TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {/* Tasks Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader 
                title="Task History" 
                action={
                  <Button 
                    variant="outlined"
                    size="small"
                    onClick={() => navigate(`/tasks?agent=${agent.agent_id}`)}
                  >
                    View All Tasks
                  </Button>
                }
              />
              <Divider />
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Task ID</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Reward</TableCell>
                      <TableCell>Created</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {agent.recent_tasks && agent.recent_tasks.map((task) => (
                      <TableRow 
                        key={task.task_id}
                        hover
                        onClick={() => navigate(`/tasks/${task.task_id}`)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {task.task_id.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {task.title || task.description}
                          </Typography>
                          {task.description && task.title && (
                            <Typography variant="caption" color="textSecondary">
                              {task.description.substring(0, 50)}...
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={task.status.charAt(0).toUpperCase() + task.status.slice(1)} 
                            size="small"
                            color={
                              task.status === 'completed' ? 'success' : 
                              task.status === 'failed' ? 'error' : 'warning'
                            }
                          />
                        </TableCell>
                        <TableCell>
                          {task.is_collaboration ? (
                            <Chip 
                              label={task.role === 'primary' ? 'Lead Agent' : 'Collaborator'}
                              size="small"
                              variant="outlined"
                              color={task.role === 'primary' ? 'primary' : 'secondary'}
                            />
                          ) : (
                            <Typography variant="body2" color="textSecondary">Solo</Typography>
                          )}
                        </TableCell>
                        <TableCell>{task.reward} ETH</TableCell>
                        <TableCell>
                          {task.created_at 
                            ? new Date(task.created_at).toLocaleDateString() 
                            : 'N/A'
                          }
                        </TableCell>
                      </TableRow>
                    ))}
                    {(!agent.recent_tasks || agent.recent_tasks.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={6} align="center">No tasks found</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {/* Learning Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Learning Events" />
              <Divider />
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Event</TableCell>
                      <TableCell>Affected Capability</TableCell>
                      <TableCell>Impact</TableCell>
                      <TableCell>Score Change</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {agent.learning_events && agent.learning_events.map((event) => (
                      <TableRow key={event.event_id}>
                        <TableCell>{event.description || event.data}</TableCell>
                        <TableCell sx={{ textTransform: 'capitalize' }}>
                          {event.affected_capability || 'General'}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={event.impact ? event.impact.charAt(0).toUpperCase() + event.impact.slice(1) : 'Positive'} 
                            size="small"
                            color={event.impact === 'positive' || !event.impact ? 'success' : 'error'}
                          />
                        </TableCell>
                        <TableCell sx={{ 
                          color: (event.score_change || event.impact_score || 0) > 0 ? 'success.main' : 'error.main',
                          fontWeight: 'bold'
                        }}>
                          {event.score_change ? 
                            (event.score_change > 0 ? `+${event.score_change}` : event.score_change) :
                            event.impact_score ? `+${event.impact_score.toFixed(1)}` : '+1'
                          }
                        </TableCell>
                        <TableCell>
                          {event.timestamp ? 
                            new Date(typeof event.timestamp === 'string' ? event.timestamp : event.timestamp * 1000).toLocaleString() :
                            'Recent'
                          }
                        </TableCell>
                      </TableRow>
                    ))}
                    {(!agent.learning_events || agent.learning_events.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={5} align="center">No learning events found</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Card>
          </Grid>
        </Grid>
      )}
      
    </Box>
  );
};

export default AgentDetails;