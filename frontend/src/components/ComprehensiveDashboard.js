import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Avatar,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Assignment as AssignmentIcon,
  AccountCircle as AccountCircleIcon,
  MonetizationOn as MonetizationOnIcon,
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Gavel as GavelIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const ComprehensiveDashboard = () => {
  const [systemStatus, setSystemStatus] = useState({
    blockchain: 'connected',
    contracts: 'deployed',
    backend: 'error',
    agents: 3,
    activeTasks: 2,
    completedTasks: 15
  });

  const [liveWorkflow, setLiveWorkflow] = useState({
    currentStep: 'task_creation',
    progress: 25,
    taskData: {
      title: 'Live Data Analysis Task',
      creator: '0x1234...5678',
      reward: '0.1 ETH',
      requirements: ['data_analysis', 'python']
    },
    bids: [
      { agent: 'Agent A', amount: '0.08 ETH', utility: 85 },
      { agent: 'Agent B', amount: '0.09 ETH', utility: 78 }
    ],
    executionData: null,
    evaluationData: null
  });

  const [agents, setAgents] = useState([
    {
      id: '0xAgent1',
      name: 'DataMaster AI',
      reputation: 88,
      capabilities: { 'data_analysis': 90, 'python': 85, 'ml': 80 },
      workload: 2,
      earnings: '2.5 ETH',
      tasksCompleted: 12,
      status: 'active'
    },
    {
      id: '0xAgent2', 
      name: 'CodeGenius Bot',
      reputation: 92,
      capabilities: { 'coding': 95, 'testing': 88, 'debugging': 90 },
      workload: 1,
      earnings: '3.2 ETH',
      tasksCompleted: 8,
      status: 'bidding'
    },
    {
      id: '0xAgent3',
      name: 'ResearchPro AI',
      reputation: 76,
      capabilities: { 'research': 85, 'writing': 78, 'analysis': 82 },
      workload: 0,
      earnings: '1.8 ETH',
      tasksCompleted: 15,
      status: 'idle'
    }
  ]);

  const [tasks, setTasks] = useState([
    {
      id: 'task_001',
      title: 'Market Analysis Report',
      status: 'completed',
      agent: 'DataMaster AI',
      reward: '0.15 ETH',
      quality: 94,
      completedAt: '2 hours ago'
    },
    {
      id: 'task_002',
      title: 'Bug Fix in Smart Contract',
      status: 'in_progress',
      agent: 'CodeGenius Bot',
      reward: '0.2 ETH',
      progress: 75,
      startedAt: '30 min ago'
    },
    {
      id: 'task_003',
      title: 'Research Paper Summary',
      status: 'bidding',
      reward: '0.1 ETH',
      bids: 3,
      deadline: '6 hours'
    }
  ]);

  const [showCreateTask, setShowCreateTask] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    reward: '',
    requirements: [],
    deadline: ''
  });

  const workflowSteps = [
    { id: 'task_creation', label: 'Task Creation', icon: <AssignmentIcon /> },
    { id: 'agent_discovery', label: 'Agent Discovery', icon: <AccountCircleIcon /> },
    { id: 'bidding', label: 'Bidding Process', icon: <GavelIcon /> },
    { id: 'assignment', label: 'Task Assignment', icon: <CheckCircleIcon /> },
    { id: 'execution', label: 'Task Execution', icon: <PlayArrowIcon /> },
    { id: 'evaluation', label: 'Evaluation & Learning', icon: <AssessmentIcon /> }
  ];

  const simulateWorkflow = () => {
    const steps = ['task_creation', 'agent_discovery', 'bidding', 'assignment', 'execution', 'evaluation'];
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      if (currentIndex < steps.length) {
        setLiveWorkflow(prev => ({
          ...prev,
          currentStep: steps[currentIndex],
          progress: ((currentIndex + 1) / steps.length) * 100
        }));
        currentIndex++;
      } else {
        clearInterval(interval);
        // Simulate completion
        setLiveWorkflow(prev => ({
          ...prev,
          currentStep: 'completed',
          progress: 100,
          executionData: {
            result: 'Analysis completed successfully',
            quality: 89,
            timeSpent: '2.3 hours'
          },
          evaluationData: {
            score: 87,
            reputationChange: +2,
            capabilityUpdates: { 'data_analysis': +1, 'python': +1 }
          }
        }));
      }
    }, 3000);
  };

  const getStatusColor = (status) => {
    const colors = {
      connected: 'success',
      deployed: 'success', 
      error: 'error',
      active: 'success',
      bidding: 'warning',
      idle: 'default',
      completed: 'success',
      in_progress: 'primary'
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status) => {
    const icons = {
      connected: <CheckCircleIcon />,
      deployed: <CheckCircleIcon />,
      error: <ErrorIcon />,
      active: <PlayArrowIcon />,
      bidding: <GavelIcon />,
      idle: <StopIcon />
    };
    return icons[status] || <InfoIcon />;
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Intelligent Agent Learning System - Comprehensive Console
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          End-to-End Workflow Monitoring and Management Platform
        </Typography>
      </Box>

      {/* System Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">System Status</Typography>
                <IconButton onClick={() => window.location.reload()}>
                  <RefreshIcon />
                </IconButton>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip 
                      icon={getStatusIcon(systemStatus.blockchain)}
                      label={`Blockchain: ${systemStatus.blockchain}`}
                      color={getStatusColor(systemStatus.blockchain)}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip 
                      icon={getStatusIcon(systemStatus.contracts)}
                      label={`Contracts: ${systemStatus.contracts}`}
                      color={getStatusColor(systemStatus.contracts)}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip 
                      icon={getStatusIcon(systemStatus.backend)}
                      label={`Backend: ${systemStatus.backend}`}
                      color={getStatusColor(systemStatus.backend)}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6">{systemStatus.agents}</Typography>
                    <Typography variant="caption">Active Agents</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Live Workflow Simulation */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Live Workflow Demo</Typography>
                <Button 
                  variant="contained" 
                  startIcon={<PlayArrowIcon />}
                  onClick={simulateWorkflow}
                  disabled={liveWorkflow.progress > 0 && liveWorkflow.progress < 100}
                >
                  {liveWorkflow.progress === 100 ? 'Restart' : 'Start Demo'}
                </Button>
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={liveWorkflow.progress} 
                sx={{ mb: 2, height: 8 }}
              />
              
              <Grid container spacing={1} sx={{ mb: 3 }}>
                {workflowSteps.map((step, index) => (
                  <Grid item xs={2} key={step.id}>
                    <Box sx={{ 
                      textAlign: 'center',
                      opacity: liveWorkflow.currentStep === step.id ? 1 : 0.5,
                      transform: liveWorkflow.currentStep === step.id ? 'scale(1.1)' : 'scale(1)',
                      transition: 'all 0.3s'
                    }}>
                      <Avatar sx={{ 
                        bgcolor: liveWorkflow.currentStep === step.id ? 'primary.main' : 'grey.300',
                        mx: 'auto', 
                        mb: 1 
                      }}>
                        {step.icon}
                      </Avatar>
                      <Typography variant="caption" display="block">
                        {step.label}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              {/* Current Step Details */}
              {liveWorkflow.currentStep === 'task_creation' && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Step 1: Task Creation</Typography>
                  <Typography variant="body2">
                    User created task: "{liveWorkflow.taskData.title}"
                    <br />Reward: {liveWorkflow.taskData.reward}
                    <br />Requirements: {liveWorkflow.taskData.requirements.join(', ')}
                  </Typography>
                </Alert>
              )}

              {liveWorkflow.currentStep === 'bidding' && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Step 3: Bidding in Progress</Typography>
                  <Typography variant="body2">
                    Current bids: {liveWorkflow.bids.length}
                    <br />Highest bid: {Math.max(...liveWorkflow.bids.map(b => parseFloat(b.amount)))} ETH
                    <br />Highest utility score: {Math.max(...liveWorkflow.bids.map(b => b.utility))}
                  </Typography>
                </Alert>
              )}

              {liveWorkflow.executionData && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Execution Complete</Typography>
                  <Typography variant="body2">
                    Result: {liveWorkflow.executionData.result}
                    <br />Quality score: {liveWorkflow.executionData.quality}/100
                    <br />Time spent: {liveWorkflow.executionData.timeSpent}
                  </Typography>
                </Alert>
              )}

              {liveWorkflow.evaluationData && (
                <Alert severity="success">
                  <Typography variant="subtitle2">Learning Update Complete</Typography>
                  <Typography variant="body2">
                    Final score: {liveWorkflow.evaluationData.score}/100
                    <br />Reputation change: {liveWorkflow.evaluationData.reputationChange > 0 ? '+' : ''}{liveWorkflow.evaluationData.reputationChange}
                    <br />Capability improvements: Data Analysis +{liveWorkflow.evaluationData.capabilityUpdates.data_analysis}, Python +{liveWorkflow.evaluationData.capabilityUpdates.python}
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Intelligent Agent Status
              </Typography>
              {agents.map((agent) => (
                <Box key={agent.id} sx={{ mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle1">{agent.name}</Typography>
                    <Chip 
                      label={agent.status} 
                      color={getStatusColor(agent.status)} 
                      size="small"
                    />
                  </Box>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption">Reputation: {agent.reputation}/100</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={agent.reputation} 
                        sx={{ height: 4 }}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption">Workload: {agent.workload}/5</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(agent.workload / 5) * 100} 
                        sx={{ height: 4 }}
                        color="warning"
                      />
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Earnings: {agent.earnings} | Tasks Completed: {agent.tasksCompleted}
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption">Core Capabilities:</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                      {Object.entries(agent.capabilities).map(([skill, level]) => (
                        <Chip 
                          key={skill}
                          label={`${skill}: ${level}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Task Management */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Task Management</Typography>
                <Button 
                  variant="contained" 
                  size="small"
                  onClick={() => setShowCreateTask(true)}
                >
                  Create Task
                </Button>
              </Box>
              
              {tasks.map((task) => (
                <Box key={task.id} sx={{ mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">{task.title}</Typography>
                    <Chip 
                      label={task.status} 
                      color={getStatusColor(task.status)} 
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Reward: {task.reward}
                  </Typography>
                  
                  {task.status === 'completed' && (
                    <Box>
                      <Typography variant="caption">
                        Agent: {task.agent} | Quality: {task.quality}/100 | Completed: {task.completedAt}
                      </Typography>
                    </Box>
                  )}
                  
                  {task.status === 'in_progress' && (
                    <Box>
                      <Typography variant="caption" gutterBottom>
                        Agent: {task.agent} | Started: {task.startedAt}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={task.progress} 
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  )}
                  
                  {task.status === 'bidding' && (
                    <Box>
                      <Typography variant="caption">
                        Bids: {task.bids} | Deadline: {task.deadline}
                      </Typography>
                    </Box>
                  )}
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Statistics and Analytics */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                System Statistics
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">Total Tasks: 18</Typography>
                <Typography variant="body2">Success Rate: 94.4%</Typography>
                <Typography variant="body2">Average Quality: 87.2/100</Typography>
                <Typography variant="body2">Total Reward Pool: 12.8 ETH</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance Metrics
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">Average Response Time: 2.3s</Typography>
                <Typography variant="body2">Contract Gas Usage: Normal</Typography>
                <Typography variant="body2">Agent Utilization: 76%</Typography>
                <Typography variant="body2">System Availability: 99.2%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Learning Progress
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">Agent Skill Improvement: +12%</Typography>
                <Typography variant="body2">Reputation Growth: +8.5%</Typography>
                <Typography variant="body2">Strategy Optimizations: 15 times</Typography>
                <Typography variant="body2">Model Updates: 3 times/day</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create Task Dialog */}
      <Dialog open={showCreateTask} onClose={() => setShowCreateTask(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Task Title"
              value={newTask.title}
              onChange={(e) => setNewTask({...newTask, title: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Task Description"
              multiline
              rows={3}
              value={newTask.description}
              onChange={(e) => setNewTask({...newTask, description: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Reward (ETH)"
              value={newTask.reward}
              onChange={(e) => setNewTask({...newTask, reward: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Skill Requirements (comma separated)"
              value={newTask.requirements.join(', ')}
              onChange={(e) => setNewTask({...newTask, requirements: e.target.value.split(', ')})}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="datetime-local"
              label="Deadline"
              value={newTask.deadline}
              onChange={(e) => setNewTask({...newTask, deadline: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateTask(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => {
            // Here would normally call API to create task
            console.log('Creating task:', newTask);
            setShowCreateTask(false);
            setNewTask({ title: '', description: '', reward: '', requirements: [], deadline: '' });
          }}>
            Create Task
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComprehensiveDashboard;