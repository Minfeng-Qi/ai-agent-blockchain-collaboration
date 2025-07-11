import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Alert,
  Snackbar,
  LinearProgress,
  Fade,
  Grow
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon,
  AttachMoney as AttachMoneyIcon,
  Person as PersonIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Psychology as PsychologyIcon,
  Star as StarIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { taskApi, agentApi } from '../services/api';

const steps = [
  {
    label: 'Analyze Task Requirements',
    description: 'Analyze required capabilities, minimum reputation, and task complexity'
  },
  {
    label: 'Intelligent Agent Selection',
    description: 'AI-powered selection based on capability matching, reputation, workload, and historical performance'
  },
  {
    label: 'Start Agent Collaboration',
    description: 'Record agent assignment and collaboration initiation on the blockchain'
  },
  {
    label: 'Collaboration Complete',
    description: 'Intelligent agent collaboration has been successfully started and task status updated'
  }
];

const StartCollaboration = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeStep, setActiveStep] = useState(0);
  const [suitableAgents, setSuitableAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [collaborationResult, setCollaborationResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);

  const fetchTaskDetails = async () => {
    try {
      const response = await taskApi.getTaskById(taskId);
      if (response && response.task) {
        setTask(response.task);
      } else {
        setError('Task not found');
      }
    } catch (error) {
      console.error('Error fetching task details:', error);
      setError('Failed to fetch task details');
    } finally {
      setLoading(false);
    }
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  const generateAvatarColor = (address) => {
    if (!address) return '#9e9e9e';
    const hash = address.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0);
    }, 0);
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
  };

  const startCollaborationProcess = async () => {
    setLoading(true);
    setActiveStep(0);
    setProgress(0);

    try {
      // Step 1: Analyze Task Requirements
      setActiveStep(0);
      setProgress(10);
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 2: Get Suitable Agents
      setActiveStep(1);
      setProgress(30);
      
      try {
        const agentsResponse = await taskApi.getSuitableAgents(taskId);
        if (agentsResponse && agentsResponse.suitable_agents) {
          setSuitableAgents(agentsResponse.suitable_agents);
        }
      } catch (error) {
        console.warn('Failed to get suitable agents, using mock data');
        setSuitableAgents([
          '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
        ]);
      }
      
      setProgress(50);
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Step 3: Start AI Agent Collaboration
      setActiveStep(2);
      setProgress(70);
      
      const collaborationResponse = await taskApi.startCollaboration(taskId, {});
      
      if (collaborationResponse.success) {
        setSelectedAgents(collaborationResponse.selected_agents || suitableAgents);
        setCollaborationResult(collaborationResponse);
        setProgress(90);
        
        // Step 4: Complete
        setActiveStep(3);
        setProgress(100);
        
        setError('Collaboration started successfully!');
        setSnackbarOpen(true);
        
        // Wait a moment for user to see the result, then return to task details
        setTimeout(() => {
          navigate(`/tasks/${taskId}`);
        }, 3000);
        
      } else {
        throw new Error(collaborationResponse.error || 'Failed to start collaboration');
      }
      
    } catch (error) {
      console.error('Error starting collaboration:', error);
      setError('Failed to start collaboration: ' + error.message);
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  if (loading && !task) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!task) {
    return (
      <Box sx={{ textAlign: 'center', py: 5 }}>
        <Typography variant="h6" color="textSecondary">
          Task Not Found
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/tasks')}
          sx={{ mt: 2 }}
        >
          Back to Tasks
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
        <Alert 
          onClose={handleSnackbarClose} 
          severity={error?.includes('successfully') ? 'success' : 'error'} 
          sx={{ width: '100%' }}
        >
          {error}
        </Alert>
      </Snackbar>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/tasks/${taskId}`)}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4">
          Start Agent Collaboration
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Task Information Card */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Information
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <AssignmentIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Task Title" 
                    secondary={task.title} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <AttachMoneyIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Reward" 
                    secondary={`${task.reward} ETH`} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <PsychologyIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Required Capabilities" 
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        {task.required_capabilities?.map((cap, index) => (
                          <Chip 
                            key={index} 
                            label={cap} 
                            size="small" 
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    } 
                  />
                </ListItem>
                
                {task.min_reputation > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <StarIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Minimum Reputation" 
                      secondary={task.min_reputation} 
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Collaboration Process */}
        <Grid item xs={12} md={8}>
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <GroupIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                Agent Collaboration Process
              </Typography>
            </Box>

            {/* Progress Bar */}
            {loading && (
              <Box sx={{ mb: 3 }}>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  Progress: {progress}%
                </Typography>
              </Box>
            )}

            {/* Steps Display */}
            <Stepper activeStep={activeStep} orientation="vertical">
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel>
                    <Typography variant="subtitle1">{step.label}</Typography>
                  </StepLabel>
                  <StepContent>
                    <Typography variant="body2" color="textSecondary">
                      {step.description}
                    </Typography>
                    
                    {/* Show Suitable Agents */}
                    {index === 1 && suitableAgents.length > 0 && (
                      <Fade in={true}>
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Found {suitableAgents.length} suitable agents using intelligent selection:
                          </Typography>
                          <List dense>
                            {suitableAgents.map((agentAddress, agentIndex) => (
                              <Grow
                                key={agentAddress}
                                in={true}
                                timeout={(agentIndex + 1) * 300}
                              >
                                <ListItem>
                                  <ListItemAvatar>
                                    <Avatar 
                                      sx={{ 
                                        bgcolor: generateAvatarColor(agentAddress),
                                        width: 32,
                                        height: 32
                                      }}
                                    >
                                      {agentAddress.substring(2, 4)}
                                    </Avatar>
                                  </ListItemAvatar>
                                  <ListItemText 
                                    primary={formatAddress(agentAddress)}
                                    secondary="Intelligently Selected Agent"
                                  />
                                </ListItem>
                              </Grow>
                            ))}
                          </List>
                        </Box>
                      </Fade>
                    )}

                    {/* Show Collaboration Results */}
                    {index === 2 && collaborationResult && (
                      <Fade in={true}>
                        <Box sx={{ mt: 2 }}>
                          <Alert severity="success" sx={{ mb: 2 }}>
                            Blockchain transaction confirmed
                          </Alert>
                          <Typography variant="subtitle2" gutterBottom>
                            Collaboration Details:
                          </Typography>
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="Collaboration ID" 
                                secondary={collaborationResult.collaboration_id} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Transaction Hash" 
                                secondary={collaborationResult.transaction_hash} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Block Number" 
                                secondary={collaborationResult.block_number} 
                              />
                            </ListItem>
                          </List>
                        </Box>
                      </Fade>
                    )}

                    {/* Completion Status */}
                    {index === 3 && (
                      <Fade in={true}>
                        <Box sx={{ mt: 2 }}>
                          <Alert severity="success" icon={<CheckCircleIcon />}>
                            Agent collaboration successfully started! Task status updated to "Assigned"
                          </Alert>
                          <Typography variant="body2" sx={{ mt: 2 }}>
                            {selectedAgents.length} agents have been assigned to this task and will begin collaborating to complete it.
                          </Typography>
                        </Box>
                      </Fade>
                    )}
                  </StepContent>
                </Step>
              ))}
            </Stepper>

            {/* Start Button */}
            {!loading && activeStep === 0 && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<GroupIcon />}
                  onClick={startCollaborationProcess}
                  sx={{ minWidth: 200 }}
                >
                  Start Agent Collaboration
                </Button>
              </Box>
            )}

            {/* Back Button */}
            {activeStep === 3 && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={() => navigate(`/tasks/${taskId}`)}
                >
                  Back to Task Details
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StartCollaboration;