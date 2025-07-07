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
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Radar, Line } from 'react-chartjs-2';
import { agentApi } from '../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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
  
  const fetchAgentDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      // 从API获取代理详情
      const response = await agentApi.getAgentById(agentId);
      if (response && response.agent) {
        setAgent(response.agent);
      } else {
        throw new Error('Agent data not found');
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
  
  // 处理能力数据
  const processCapabilitiesData = () => {
    if (!agent || !agent.capabilities) {
      return {
        labels: [],
        datasets: [{
          label: 'Capability Score',
          data: [],
          backgroundColor: 'rgba(58, 134, 255, 0.2)',
          borderColor: '#3a86ff',
          borderWidth: 2,
          pointBackgroundColor: '#3a86ff',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#3a86ff'
        }]
      };
    }
    
    // 检查capabilities是数组还是对象
    if (Array.isArray(agent.capabilities)) {
      // 如果是数组，假设每个能力是一个字符串
      return {
        labels: agent.capabilities,
        datasets: [{
          label: 'Capability Score',
          data: agent.capabilities.map(() => 100), // 默认满分
          backgroundColor: 'rgba(58, 134, 255, 0.2)',
          borderColor: '#3a86ff',
          borderWidth: 2,
          pointBackgroundColor: '#3a86ff',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#3a86ff'
        }]
      };
    } else {
      // 如果是对象，使用键值对
      const labels = Object.keys(agent.capabilities);
      const scores = Object.values(agent.capabilities);
      
      return {
        labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
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
    }
  };
  
  // 处理声誉历史数据
  const processReputationData = () => {
    if (!agent || !agent.history) {
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
    
    return {
      labels: agent.history.dates || [],
      datasets: [{
        label: 'Reputation',
        data: agent.history.reputation || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
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
          backdropColor: 'transparent'
        }
      }
    },
    plugins: {
      legend: {
        display: false
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
              {formatAddress(agent.agent_id)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Registered on {new Date(agent.registration_date * 1000).toLocaleDateString()}
            </Typography>
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
                {agent.average_score}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Average Reward
              </Typography>
              <Typography variant="h4">
                {agent.average_reward}
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
                        primary={task.description}
                        secondary={`Score: ${task.score || 'N/A'} • Reward: ${task.reward}`}
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
                {agent.capabilities && typeof agent.capabilities === 'object' && !Array.isArray(agent.capabilities) && 
                  Object.entries(agent.capabilities).map(([capability, score]) => (
                    <Box key={capability} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                          {capability}
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
                  ))
                }
                {agent.capabilities && Array.isArray(agent.capabilities) && 
                  agent.capabilities.map((capability, index) => (
                    <Box key={index} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                          {capability}
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          Available
                        </Typography>
                      </Box>
                      <Chip 
                        label="Enabled" 
                        color="success" 
                        size="small" 
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  ))
                }
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
                      <TableCell>Description</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell>Reward</TableCell>
                      <TableCell>Completed</TableCell>
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
                        <TableCell>{task.task_id}</TableCell>
                        <TableCell>{task.description}</TableCell>
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
                        <TableCell>{task.score || 'N/A'}</TableCell>
                        <TableCell>{task.reward}</TableCell>
                        <TableCell>
                          {task.completed_at 
                            ? new Date(task.completed_at * 1000).toLocaleString() 
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
                        <TableCell>{event.description}</TableCell>
                        <TableCell sx={{ textTransform: 'capitalize' }}>
                          {event.affected_capability}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={event.impact.charAt(0).toUpperCase() + event.impact.slice(1)} 
                            size="small"
                            color={event.impact === 'positive' ? 'success' : 'error'}
                          />
                        </TableCell>
                        <TableCell sx={{ 
                          color: event.score_change > 0 ? 'success.main' : 'error.main',
                          fontWeight: 'bold'
                        }}>
                          {event.score_change > 0 ? `+${event.score_change}` : event.score_change}
                        </TableCell>
                        <TableCell>
                          {new Date(event.timestamp * 1000).toLocaleString()}
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