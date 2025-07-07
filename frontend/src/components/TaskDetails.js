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
  const [bidDialogOpen, setBidDialogOpen] = useState(false);
  const [bidAmount, setBidAmount] = useState('');
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  
  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);
  
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
        bids: [
          {
            agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
            amount: 0.45,
            timestamp: Math.floor(Date.now() / 1000) - 64800
          },
          {
            agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
            amount: 0.55,
            timestamp: Math.floor(Date.now() / 1000) - 75600
          }
        ],
        history: [
          {
            event: 'created',
            timestamp: Math.floor(Date.now() / 1000) - 86400,
            details: 'Task created'
          },
          {
            event: 'bid',
            timestamp: Math.floor(Date.now() / 1000) - 75600,
            details: 'Bid placed by 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
          },
          {
            event: 'bid',
            timestamp: Math.floor(Date.now() / 1000) - 64800,
            details: 'Bid placed by 0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
          },
          {
            event: 'assigned',
            timestamp: Math.floor(Date.now() / 1000) - 43200,
            details: 'Task assigned to 0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
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
  
  const handlePlaceBid = async () => {
    try {
      await taskApi.placeBid(taskId, {
        amount: parseFloat(bidAmount)
      });
      setBidDialogOpen(false);
      fetchTaskDetails(); // Refresh task data
    } catch (error) {
      console.error('Error placing bid:', error);
      setBidDialogOpen(false);
      setError('Failed to place bid');
      setSnackbarOpen(true);
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
              onClick={() => setBidDialogOpen(true)}
            >
              Place Bid
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
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <AssignmentIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Task ID" 
                      secondary={task.task_id} 
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
                      <CalendarTodayIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Created" 
                      secondary={new Date(task.created_at * 1000).toLocaleString()} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} sm={6}>
                <List dense>
                  {task.assigned_agent && (
                    <ListItem>
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
                              cursor: 'pointer'
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
                    <ListItem>
                      <ListItemIcon>
                        <AccessTimeIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Deadline" 
                        secondary={new Date(task.deadline * 1000).toLocaleString()} 
                      />
                    </ListItem>
                  )}
                  {task.complexity && (
                    <ListItem>
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
              Bids
            </Typography>
            {task.bids && task.bids.length > 0 ? (
              <List>
                {task.bids.map((bid, index) => (
                  <ListItem key={index} divider={index < task.bids.length - 1}>
                    <ListItemIcon>
                      <Avatar 
                        sx={{ 
                          bgcolor: generateAvatarColor(bid.agent_id) 
                        }}
                      >
                        {bid.agent_id.substring(2, 4)}
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
                          onClick={() => navigate(`/agents/${bid.agent_id}`)}
                        >
                          {formatAddress(bid.agent_id)}
                        </Box>
                      }
                      secondary={`Bid: ${bid.amount} ETH • ${new Date(bid.timestamp * 1000).toLocaleString()}`}
                    />
                    {task.status === 'open' && (
                      <Button 
                        variant="contained" 
                        size="small"
                        onClick={async () => {
                          try {
                            await taskApi.assignTask(task.task_id, bid.agent_id);
                            fetchTaskDetails();
                          } catch (error) {
                            console.error('Error assigning task:', error);
                            setError('Failed to assign task');
                            setSnackbarOpen(true);
                          }
                        }}
                      >
                        Accept
                      </Button>
                    )}
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No bids yet
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
      
      {/* Bid Dialog */}
      <Dialog
        open={bidDialogOpen}
        onClose={() => setBidDialogOpen(false)}
      >
        <DialogTitle>Place Bid</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Current reward: {task.reward} ETH
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Your Bid (ETH)"
            type="number"
            fullWidth
            value={bidAmount}
            onChange={(e) => setBidAmount(e.target.value)}
            inputProps={{ step: 0.01, min: 0 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBidDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handlePlaceBid} 
            color="primary" 
            variant="contained"
            disabled={!bidAmount || parseFloat(bidAmount) <= 0}
          >
            Submit Bid
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskDetails;