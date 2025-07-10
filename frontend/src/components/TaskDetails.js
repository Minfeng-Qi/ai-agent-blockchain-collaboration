import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Stepper,
  Step,
  StepLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  Assignment as AssignmentIcon,
  AttachMoney as AttachMoneyIcon,
  CalendarToday as CalendarTodayIcon,
  Person as PersonIcon,
  AccessTime as AccessTimeIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Group as GroupIcon
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { taskApi } from '../services/api';

const TaskDetails = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [task, setTask] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [collaborationLoading, setCollaborationLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  
  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);
  
  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      // 如果是Unix timestamp (数字)，转换为毫秒
      const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  const fetchTaskDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await taskApi.getTaskById(taskId);
      if (response && response.task) {
        setTask(response.task);
      } else {
        throw new Error('Task data not found');
      }
    } catch (error) {
      console.error('Error fetching task details:', error);
      setError('Failed to fetch task details. Using sample data instead.');
      setSnackbarOpen(true);
      
      // Mock data for development
      const mockTask = {
        task_id: taskId,
        title: 'Market Trend Analysis',
        description: 'Analyze market trends for Q3 2023 and provide insights on consumer behavior patterns in the technology sector.',
        status: 'assigned',
        created_at: Math.floor(Date.now() / 1000) - 86400,
        deadline: Math.floor(Date.now() / 1000) + 172800,
        assigned_agent: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        assigned_at: Math.floor(Date.now() / 1000) - 43200,
        required_capabilities: ['analysis', 'research', 'data_visualization'],
        reward: 0.5,
        complexity: 'medium',
        tags: ['market research', 'technology', 'consumer behavior'],
        history: [
          {
            event: 'created',
            timestamp: Math.floor(Date.now() / 1000) - 86400,
            details: 'Task created'
          },
          {
            event: 'collaboration_started',
            timestamp: Math.floor(Date.now() / 1000) - 43200,
            details: 'Agent collaboration started with 3 selected agents'
          },
          {
            event: 'assigned',
            timestamp: Math.floor(Date.now() / 1000) - 43200,
            details: 'Task assigned to agent collaboration team'
          }
        ]
      };
      
      setTask(mockTask);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  const handleDeleteTask = async () => {
    try {
      await taskApi.deleteTask(taskId);
      setDeleteDialogOpen(false);
      navigate('/tasks');
    } catch (error) {
      console.error('Error deleting task:', error);
      setDeleteDialogOpen(false);
      setError('Failed to delete task');
      setSnackbarOpen(true);
    }
  };
  
  const handleStartCollaboration = async () => {
    setCollaborationLoading(true);
    try {
      const response = await taskApi.startCollaboration(taskId, {});
      if (response.success) {
        setError(`Collaboration started successfully! ID: ${response.collaboration_id}`);
        setSnackbarOpen(true);
        fetchTaskDetails(); // Refresh task data
      } else {
        setError('Failed to start collaboration: ' + response.error);
        setSnackbarOpen(true);
      }
    } catch (error) {
      console.error('Error starting collaboration:', error);
      setError('Failed to start collaboration');
      setSnackbarOpen(true);
    } finally {
      setCollaborationLoading(false);
    }
  };
  
  const getTaskStatusStep = (status) => {
    switch (status) {
      case 'open':
        return 0;
      case 'assigned':
        return 1;
      case 'completed':
        return 2;
      case 'failed':
        return 3;
      default:
        return 0;
    }
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
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!task) {
    return (
      <Box sx={{ textAlign: 'center', py: 5 }}>
        <Typography variant="h6" color="textSecondary">
          Task not found
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
        <Alert onClose={handleSnackbarClose} severity="warning" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => navigate('/tasks')} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4">
            Task Details
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={fetchTaskDetails}
          >
            Refresh
          </Button>
          {task.status === 'open' && (
            <Button 
              variant="contained" 
              color="primary"
              onClick={handleStartCollaboration}
              disabled={collaborationLoading}
              startIcon={collaborationLoading ? <CircularProgress size={20} /> : null}
            >
              {collaborationLoading ? 'Starting...' : 'Start Agent Collaboration'}
            </Button>
          )}
          <Button 
            variant="outlined" 
            startIcon={<EditIcon />}
            onClick={() => navigate(`/tasks/${taskId}/edit`)}
          >
            Edit
          </Button>
          <Button 
            variant="outlined" 
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => setDeleteDialogOpen(true)}
          >
            Delete
          </Button>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {task.title}
                </Typography>
                <Typography variant="body1">
                  {task.description}
                </Typography>
              </Box>
              <Chip 
                label={task.status.charAt(0).toUpperCase() + task.status.slice(1)} 
                color={
                  task.status === 'completed' ? 'success' : 
                  task.status === 'failed' ? 'error' : 
                  task.status === 'assigned' ? 'warning' : 'info'
                }
              />
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Task Progress
              </Typography>
              <Stepper activeStep={getTaskStatusStep(task.status)}>
                <Step>
                  <StepLabel>Open</StepLabel>
                </Step>
                <Step>
                  <StepLabel>Assigned</StepLabel>
                </Step>
                <Step>
                  <StepLabel>Completed</StepLabel>
                </Step>
              </Stepper>
            </Box>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <List>
                  <ListItem sx={{ pb: 2 }}>
                    <ListItemIcon>
                      <AssignmentIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Task ID" 
                      secondary={
                        <Box sx={{ mt: 0.5, wordBreak: 'break-all' }}>
                          {task.task_id}
                        </Box>
                      } 
                    />
                  </ListItem>
                  <ListItem sx={{ pb: 2 }}>
                    <ListItemIcon>
                      <AttachMoneyIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Reward" 
                      secondary={`${task.reward} ETH`} 
                    />
                  </ListItem>
                  <ListItem sx={{ pb: 2 }}>
                    <ListItemIcon>
                      <CalendarTodayIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Created" 
                      secondary={formatTimestamp(task.created_at)} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} sm={6}>
                <List>
                  {task.assigned_agent && (
                    <ListItem sx={{ pb: 2 }}>
                      <ListItemIcon>
                        <PersonIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Assigned To" 
                        secondary={
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center',
                              cursor: 'pointer',
                              mt: 0.5
                            }}
                            onClick={() => navigate(`/agents/${task.assigned_agent}`)}
                          >
                            <Avatar 
                              sx={{ 
                                width: 24, 
                                height: 24, 
                                mr: 1, 
                                bgcolor: generateAvatarColor(task.assigned_agent) 
                              }}
                            >
                              {task.assigned_agent.substring(2, 4)}
                            </Avatar>
                            {formatAddress(task.assigned_agent)}
                          </Box>
                        } 
                      />
                    </ListItem>
                  )}
                  {task.deadline && (
                    <ListItem sx={{ pb: 2 }}>
                      <ListItemIcon>
                        <AccessTimeIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Deadline" 
                        secondary={formatTimestamp(task.deadline)} 
                      />
                    </ListItem>
                  )}
                  {task.complexity && (
                    <ListItem sx={{ pb: 2 }}>
                      <ListItemIcon>
                        <AssignmentIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Complexity" 
                        secondary={task.complexity.charAt(0).toUpperCase() + task.complexity.slice(1)} 
                      />
                    </ListItem>
                  )}
                </List>
              </Grid>
            </Grid>
            
            {task.required_capabilities && task.required_capabilities.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Required Capabilities
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {task.required_capabilities.map((capability, index) => (
                    <Chip 
                      key={index}
                      label={capability}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
            
            {task.tags && task.tags.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Tags
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {task.tags.map((tag, index) => (
                    <Chip 
                      key={index}
                      label={tag}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
          
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Task History
            </Typography>
            {task.history && task.history.length > 0 ? (
              <List dense>
                {task.history.map((event, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {event.event === 'created' && <AssignmentIcon color="primary" />}
                      {event.event === 'bid' && <AttachMoneyIcon color="secondary" />}
                      {event.event === 'assigned' && <PersonIcon color="warning" />}
                      {event.event === 'completed' && <CheckCircleIcon color="success" />}
                      {event.event === 'failed' && <CancelIcon color="error" />}
                    </ListItemIcon>
                    <ListItemText 
                      primary={event.details}
                      secondary={new Date(event.timestamp * 1000).toLocaleString()}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No history available
              </Typography>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {task.status === 'open' ? 'Required Capabilities' : 'Assigned Agents'}
            </Typography>
            {task.status === 'open' ? (
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Agents with these capabilities will be automatically selected:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                  {task.required_capabilities && task.required_capabilities.map((capability, index) => (
                    <Chip 
                      key={index}
                      label={capability}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            ) : task.assigned_agent ? (
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Avatar 
                      sx={{ 
                        bgcolor: generateAvatarColor(task.assigned_agent) 
                      }}
                    >
                      {task.assigned_agent.substring(2, 4)}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText 
                    primary={
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          cursor: 'pointer'
                        }}
                        onClick={() => navigate(`/agents/${task.assigned_agent}`)}
                      >
                        {formatAddress(task.assigned_agent)}
                      </Box>
                    }
                    secondary="Primary assigned agent"
                  />
                </ListItem>
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No agents assigned yet
              </Typography>
            )}
          </Paper>
          
          {task.status === 'assigned' && (
            <Paper variant="outlined" sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Task Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button 
                  component={Link}
                  to={`/tasks/${taskId}/collaborate`}
                  color="primary"
                  variant="contained"
                  startIcon={<GroupIcon />}
                >
                  Start Agent Collaboration
                </Button>
                <Button 
                  variant="contained" 
                  color="success"
                  startIcon={<CheckCircleIcon />}
                  onClick={async () => {
                    try {
                      await taskApi.completeTask(task.task_id, { status: 'completed' });
                      fetchTaskDetails();
                    } catch (error) {
                      console.error('Error completing task:', error);
                      setError('Failed to complete task');
                      setSnackbarOpen(true);
                    }
                  }}
                >
                  Mark as Completed
                </Button>
                <Button 
                  variant="contained" 
                  color="error"
                  startIcon={<CancelIcon />}
                  onClick={async () => {
                    try {
                      await taskApi.completeTask(task.task_id, { status: 'failed' });
                      fetchTaskDetails();
                    } catch (error) {
                      console.error('Error marking task as failed:', error);
                      setError('Failed to update task status');
                      setSnackbarOpen(true);
                    }
                  }}
                >
                  Mark as Failed
                </Button>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Task</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this task? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleDeleteTask} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskDetails;