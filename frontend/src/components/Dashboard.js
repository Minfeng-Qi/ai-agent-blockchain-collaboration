import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  CircularProgress, 
  Paper, 
  Chip,
  Button,
  IconButton,
  Divider,
  useTheme,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Alert,
  Snackbar
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Assignment as AssignmentIcon,
  People as PeopleIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { ResponsivePie } from '@nivo/pie';
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveBar } from '@nivo/bar';
import { ResponsiveRadar } from '@nivo/radar';
import { useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { agentApi, taskApi, systemApi } from '../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const StatCard = ({ title, value, icon, color, trend, trendValue }) => {
  const theme = useTheme();
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle2" color="textSecondary">
            {title}
          </Typography>
          <Box 
            sx={{ 
              backgroundColor: `${color}.lighter`, 
              borderRadius: '50%', 
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {value}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {trend === 'up' ? (
            <TrendingUpIcon sx={{ color: theme.palette.success.main, fontSize: 16, mr: 0.5 }} />
          ) : (
            <TrendingDownIcon sx={{ color: theme.palette.error.main, fontSize: 16, mr: 0.5 }} />
          )}
          <Typography 
            variant="body2" 
            color={trend === 'up' ? 'success.main' : 'error.main'}
          >
            {trendValue}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const TaskStatusCard = ({ tasks }) => {
  const theme = useTheme();
  
  // 统计任务状态
  const statusCounts = {
    open: tasks.filter(task => task.status === 'open').length,
    assigned: tasks.filter(task => task.status === 'assigned').length,
    completed: tasks.filter(task => task.status === 'completed').length,
    failed: tasks.filter(task => task.status === 'failed').length
  };
  
  const data = [
    {
      id: 'Open',
      label: 'Open',
      value: statusCounts.open || 0,
      color: theme.palette.info.main
    },
    {
      id: 'Assigned',
      label: 'Assigned',
      value: statusCounts.assigned || 0,
      color: theme.palette.warning.main
    },
    {
      id: 'Completed',
      label: 'Completed',
      value: statusCounts.completed || 0,
      color: theme.palette.success.main
    },
    {
      id: 'Failed',
      label: 'Failed',
      value: statusCounts.failed || 0,
      color: theme.palette.error.main
    }
  ];
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Task Status</Typography>
          <IconButton size="small">
            <MoreVertIcon />
          </IconButton>
        </Box>
        <Box sx={{ height: 300 }}>
          <ResponsivePie
            data={data}
            margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
            innerRadius={0.5}
            padAngle={0.7}
            cornerRadius={3}
            activeOuterRadiusOffset={8}
            colors={{ datum: 'data.color' }}
            borderWidth={1}
            borderColor={{ from: 'color', modifiers: [['darker', 0.2]] }}
            arcLinkLabelsSkipAngle={10}
            arcLinkLabelsTextColor={theme.palette.text.primary}
            arcLinkLabelsThickness={2}
            arcLinkLabelsColor={{ from: 'color' }}
            arcLabelsSkipAngle={10}
            arcLabelsTextColor={theme.palette.text.primary}
            legends={[
              {
                anchor: 'bottom',
                direction: 'row',
                justify: false,
                translateX: 0,
                translateY: 56,
                itemsSpacing: 0,
                itemWidth: 100,
                itemHeight: 18,
                itemTextColor: theme.palette.text.secondary,
                itemDirection: 'left-to-right',
                itemOpacity: 1,
                symbolSize: 18,
                symbolShape: 'circle'
              }
            ]}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

const AgentCapabilitiesCard = ({ agents }) => {
  const theme = useTheme();
  
  // 计算所有代理的平均能力分数
  const calculateAverageCapabilities = () => {
    if (!agents || agents.length === 0) return [];
    
    const capabilities = {};
    let capabilityCount = {};
    
    agents.forEach(agent => {
      if (agent.capabilities && Array.isArray(agent.capabilities)) {
        // 如果capabilities是字符串数组
        agent.capabilities.forEach(cap => {
          capabilities[cap] = (capabilities[cap] || 0) + 1;
          capabilityCount[cap] = (capabilityCount[cap] || 0) + 1;
        });
      } else if (agent.capabilities && typeof agent.capabilities === 'object') {
        // 如果capabilities是对象
        Object.entries(agent.capabilities).forEach(([cap, score]) => {
          capabilities[cap] = (capabilities[cap] || 0) + score;
          capabilityCount[cap] = (capabilityCount[cap] || 0) + 1;
        });
      }
    });
    
    // 计算平均值
    return Object.keys(capabilities).map(cap => ({
      capability: cap,
      value: capabilities[cap] / (capabilityCount[cap] || 1)
    }));
  };
  
  const averageCapabilities = calculateAverageCapabilities();
  
  // 为雷达图准备数据
  const radarData = [
    {
      "capability": "Agent Capabilities",
      ...averageCapabilities.reduce((obj, item) => {
        obj[item.capability] = item.value;
        return obj;
      }, {})
    }
  ];
  
  const radarKeys = averageCapabilities.map(item => item.capability);
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Agent Capabilities</Typography>
          <IconButton size="small">
            <MoreVertIcon />
          </IconButton>
        </Box>
        <Box sx={{ height: 300 }}>
          {radarKeys.length > 0 ? (
            <ResponsiveRadar
              data={radarData}
              keys={radarKeys}
              indexBy="capability"
              maxValue="auto"
              margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
              curve="linearClosed"
              borderWidth={2}
              borderColor={{ from: 'color' }}
              gridLabelOffset={36}
              dotSize={10}
              dotColor={{ theme: 'background' }}
              dotBorderWidth={2}
              dotBorderColor={{ from: 'color' }}
              enableDotLabel={true}
              dotLabel="value"
              dotLabelYOffset={-12}
              colors={{ scheme: 'nivo' }}
              blendMode="multiply"
              motionConfig="wobbly"
            />
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Typography variant="body2" color="textSecondary">
                No capability data available
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

const TaskCompletionTrendCard = ({ tasks }) => {
  const theme = useTheme();
  
  // 处理任务趋势数据
  const processTaskTrends = () => {
    if (!tasks || tasks.length === 0) return [];
    
    // 获取最近30天的日期
    const dates = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }
    
    // 初始化计数
    const completedByDate = {};
    const failedByDate = {};
    
    dates.forEach(date => {
      completedByDate[date] = 0;
      failedByDate[date] = 0;
    });
    
    // 计算每天完成和失败的任务数量
    tasks.forEach(task => {
      if (!task.completed_at) return;
      
      const date = new Date(task.completed_at).toISOString().split('T')[0];
      if (completedByDate[date] !== undefined) {
        if (task.status === 'completed') {
          completedByDate[date]++;
        } else if (task.status === 'failed') {
          failedByDate[date]++;
        }
      }
    });
    
    // 转换为Nivo图表格式
    return [
      {
        id: 'Completed',
        color: theme.palette.success.main,
        data: Object.entries(completedByDate).map(([date, count]) => ({
          x: date,
          y: count
        }))
      },
      {
        id: 'Failed',
        color: theme.palette.error.main,
        data: Object.entries(failedByDate).map(([date, count]) => ({
          x: date,
          y: count
        }))
      }
    ];
  };
  
  const lineData = processTaskTrends();
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Task Completion Trend</Typography>
          <IconButton size="small">
            <MoreVertIcon />
          </IconButton>
        </Box>
        <Box sx={{ height: 300 }}>
          <ResponsiveLine
            data={lineData}
            margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
            xScale={{ type: 'point' }}
            yScale={{
              type: 'linear',
              min: 'auto',
              max: 'auto',
              stacked: false,
              reverse: false
            }}
            yFormat=" >-.2f"
            axisTop={null}
            axisRight={null}
            axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: -45,
              legend: 'Date',
              legendOffset: 36,
              legendPosition: 'middle',
              truncateTickAt: 0
            }}
            axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: 'Count',
              legendOffset: -40,
              legendPosition: 'middle',
              truncateTickAt: 0
            }}
            colors={{ datum: 'color' }}
            pointSize={10}
            pointColor={{ theme: 'background' }}
            pointBorderWidth={2}
            pointBorderColor={{ from: 'serieColor' }}
            pointLabelYOffset={-12}
            useMesh={true}
            legends={[
              {
                anchor: 'bottom-right',
                direction: 'column',
                justify: false,
                translateX: 100,
                translateY: 0,
                itemsSpacing: 0,
                itemDirection: 'left-to-right',
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: 'circle',
                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                effects: [
                  {
                    on: 'hover',
                    style: {
                      itemBackground: 'rgba(0, 0, 0, .03)',
                      itemOpacity: 1
                    }
                  }
                ]
              }
            ]}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

const RecentTasksCard = ({ tasks }) => {
  const navigate = useNavigate();
  
  // 获取状态图标
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon fontSize="small" color="success" />;
      case 'failed':
        return <ErrorIcon fontSize="small" color="error" />;
      case 'assigned':
        return <HourglassEmptyIcon fontSize="small" color="warning" />;
      case 'open':
      default:
        return <AssignmentIcon fontSize="small" color="info" />;
    }
  };
  
  // 格式化日期
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Recent Tasks</Typography>
          <Button 
            size="small" 
            onClick={() => navigate('/tasks')}
          >
            View All
          </Button>
        </Box>
        <List>
          {tasks.slice(0, 5).map((task) => (
            <React.Fragment key={task.task_id}>
              <ListItem 
                button 
                onClick={() => navigate(`/tasks/${task.task_id}`)}
              >
                <ListItemIcon>
                  {getStatusIcon(task.status)}
                </ListItemIcon>
                <ListItemText 
                  primary={task.title || task.description} 
                  secondary={`Created: ${formatDate(task.created_at)}`}
                />
                <Chip 
                  label={`${task.reward || 0} ETH`} 
                  size="small" 
                  color="primary" 
                  variant="outlined" 
                />
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
          {tasks.length === 0 && (
            <ListItem>
              <ListItemText 
                primary="No tasks available" 
                secondary="Create new tasks to see them here"
              />
            </ListItem>
          )}
        </List>
      </CardContent>
    </Card>
  );
};

const TopAgentsCard = ({ agents }) => {
  const navigate = useNavigate();
  
  // 生成头像颜色
  const getAvatarColor = (address) => {
    const colors = [
      '#3f51b5', '#f44336', '#009688', '#ff9800', '#9c27b0',
      '#2196f3', '#4caf50', '#ff5722', '#607d8b', '#e91e63'
    ];
    const index = parseInt(address?.slice(2, 4) || '0', 16) % colors.length;
    return colors[index];
  };
  
  // 格式化地址
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Top Agents</Typography>
          <Button 
            size="small" 
            onClick={() => navigate('/agents')}
          >
            View All
          </Button>
        </Box>
        <List>
          {agents.slice(0, 5).map((agent) => (
            <React.Fragment key={agent.agent_id}>
              <ListItem 
                button 
                onClick={() => navigate(`/agents/${agent.agent_id}`)}
              >
                <Avatar 
                  sx={{ 
                    bgcolor: getAvatarColor(agent.agent_id),
                    mr: 2
                  }}
                >
                  {agent.agent_id?.slice(2, 4).toUpperCase() || 'AG'}
                </Avatar>
                <ListItemText 
                  primary={formatAddress(agent.agent_id)} 
                  secondary={`Reputation: ${agent.reputation || 0}`}
                />
                <Chip 
                  label={`${agent.tasks_completed || agent.completed_tasks || 0} Tasks`} 
                  size="small" 
                  color="primary" 
                  variant="outlined" 
                />
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
          {agents.length === 0 && (
            <ListItem>
              <ListItemText 
                primary="No agents available" 
                secondary="Register new agents to see them here"
              />
            </ListItem>
          )}
        </List>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({
    totalAgents: 0,
    totalTasks: 0,
    completedTasks: 0,
    activeTasks: 0,
    averageReward: 0
  });
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 获取代理列表
      const agentsData = await agentApi.getAgents();
      if (agentsData && agentsData.agents) {
        setAgents(agentsData.agents);
        stats.totalAgents = agentsData.agents.length;
      }
      
      // 获取任务列表
      const tasksData = await taskApi.getTasks();
      if (tasksData && tasksData.tasks) {
        setTasks(tasksData.tasks);
        
        // 计算统计数据
        const completedTasks = tasksData.tasks.filter(task => task.status === 'completed');
        const activeTasks = tasksData.tasks.filter(task => task.status === 'open' || task.status === 'assigned');
        
        // 计算平均奖励
        const totalReward = tasksData.tasks.reduce((sum, task) => sum + (task.reward || 0), 0);
        const averageReward = tasksData.tasks.length > 0 ? totalReward / tasksData.tasks.length : 0;
        
        setStats({
          totalAgents: agentsData.agents?.length || 0,
          totalTasks: tasksData.tasks.length,
          completedTasks: completedTasks.length,
          activeTasks: activeTasks.length,
          averageReward: averageReward
        });
      }
      
      // 获取系统统计数据
      const systemStatsData = await systemApi.getSystemStats();
      if (systemStatsData) {
        // 如果有系统统计数据，可以更新其他统计信息
        console.log("System stats loaded:", systemStatsData);
      }
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to fetch dashboard data. Using sample data instead.');
      setSnackbarOpen(true);
      
      // 使用更丰富的示例数据作为后备
      const mockAgents = [
        {
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          name: 'DataAnalysisAgent',
          reputation: 85,
          tasks_completed: 42,
          capabilities: ['data_analysis', 'text_generation', 'classification'],
          average_score: 4.7
        },
        {
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          name: 'TextGenerationAgent',
          reputation: 75,
          tasks_completed: 28,
          capabilities: ['text_generation', 'translation', 'summarization'],
          average_score: 4.3
        },
        {
          agent_id: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
          name: 'ClassificationAgent',
          reputation: 80,
          tasks_completed: 35,
          capabilities: ['classification', 'data_analysis'],
          average_score: 4.5
        },
        {
          agent_id: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65',
          name: 'TranslationAgent',
          reputation: 78,
          tasks_completed: 31,
          capabilities: ['translation', 'text_generation'],
          average_score: 4.4
        },
        {
          agent_id: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc',
          name: 'ImageRecognitionAgent',
          reputation: 82,
          tasks_completed: 37,
          capabilities: ['image_recognition', 'classification'],
          average_score: 4.6
        }
      ];
      
      const currentDate = new Date();
      const mockTasks = [
        {
          task_id: 'task_123',
          title: 'Analyze market trends',
          description: 'Analyze market trends for Q3 2023',
          type: 'data_analysis',
          status: 'completed',
          created_at: new Date(currentDate.getTime() - 7 * 86400000).toISOString(), // 7 days ago
          completed_at: new Date(currentDate.getTime() - 5 * 86400000).toISOString(), // 5 days ago
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
          created_at: new Date(currentDate.getTime() - 5 * 86400000).toISOString(), // 5 days ago
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
          created_at: new Date(currentDate.getTime() - 3 * 86400000).toISOString(), // 3 days ago
          required_capabilities: ['classification'],
          reward: 0.15
        },
        {
          task_id: 'task_101',
          title: 'Translate product documentation',
          description: 'Translate product documentation from English to Spanish',
          type: 'translation',
          status: 'completed',
          created_at: new Date(currentDate.getTime() - 10 * 86400000).toISOString(), // 10 days ago
          completed_at: new Date(currentDate.getTime() - 8 * 86400000).toISOString(), // 8 days ago
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
          created_at: new Date(currentDate.getTime() - 4 * 86400000).toISOString(), // 4 days ago
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
          created_at: new Date(currentDate.getTime() - 2 * 86400000).toISOString(), // 2 days ago
          required_capabilities: ['text_generation', 'summarization'],
          reward: 0.4
        },
        {
          task_id: 'task_104',
          title: 'Analyze customer sentiment',
          description: 'Analyze sentiment in customer reviews',
          type: 'data_analysis',
          status: 'completed',
          created_at: new Date(currentDate.getTime() - 15 * 86400000).toISOString(), // 15 days ago
          completed_at: new Date(currentDate.getTime() - 14 * 86400000).toISOString(), // 14 days ago
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
          created_at: new Date(currentDate.getTime() - 20 * 86400000).toISOString(), // 20 days ago
          completed_at: new Date(currentDate.getTime() - 19 * 86400000).toISOString(), // 19 days ago
          assigned_agent: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          required_capabilities: ['text_generation'],
          reward: 0.3
        }
      ];
      
      setAgents(mockAgents);
      setTasks(mockTasks);
      
      // 计算更详细的统计数据
      const completedTasks = mockTasks.filter(task => task.status === 'completed');
      const activeTasks = mockTasks.filter(task => task.status === 'open' || task.status === 'assigned');
      const totalReward = mockTasks.reduce((sum, task) => sum + (task.reward || 0), 0);
      const averageReward = mockTasks.length > 0 ? totalReward / mockTasks.length : 0;
      
      setStats({
        totalAgents: mockAgents.length,
        totalTasks: mockTasks.length,
        completedTasks: completedTasks.length,
        activeTasks: activeTasks.length,
        averageReward: averageReward
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  useEffect(() => {
    fetchData();
    
    // 设置轮询间隔
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
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
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Button 
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={() => fetchData()}
        >
          Refresh
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {/* 统计卡片 */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Tasks" 
            value={stats.totalTasks} 
            icon={<AssignmentIcon fontSize="small" color="primary" />}
            color="primary"
            trend="up"
            trendValue={`+${Math.floor(stats.totalTasks * 0.1)} (10%)`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Completed Tasks" 
            value={stats.completedTasks} 
            icon={<CheckCircleIcon fontSize="small" color="success" />}
            color="success"
            trend="up"
            trendValue={`+${Math.floor(stats.completedTasks * 0.15)} (15%)`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Active Tasks" 
            value={stats.activeTasks} 
            icon={<HourglassEmptyIcon fontSize="small" color="warning" />}
            color="warning"
            trend="up"
            trendValue={`+${Math.floor(stats.activeTasks * 0.05)} (5%)`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Average Reward" 
            value={stats.averageReward.toFixed(2)} 
            icon={<PeopleIcon fontSize="small" color="info" />}
            color="info"
            trend="up"
            trendValue={`+${(stats.averageReward * 0.02).toFixed(2)} (2%)`}
          />
        </Grid>
        
        {/* 图表 */}
        <Grid item xs={12} md={6}>
          <TaskStatusCard tasks={tasks} />
        </Grid>
        <Grid item xs={12} md={6}>
          <AgentCapabilitiesCard agents={agents} />
        </Grid>
        <Grid item xs={12}>
          <TaskCompletionTrendCard tasks={tasks} />
        </Grid>
        
        {/* 列表 */}
        <Grid item xs={12} md={6}>
          <RecentTasksCard tasks={tasks} />
        </Grid>
        <Grid item xs={12} md={6}>
          <TopAgentsCard agents={agents} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;