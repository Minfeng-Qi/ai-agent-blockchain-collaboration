import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TaskHistory from './TaskHistory';
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
  Alert,
  LinearProgress,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  DialogContentText,
  Rating,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio
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
  Group as GroupIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { taskApi } from '../services/api';

const TaskDetails = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [task, setTask] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarSeverity, setSnackbarSeverity] = useState('warning');
  const [taskStatus, setTaskStatus] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const [resultDialogOpen, setResultDialogOpen] = useState(false);
  const [collaborationResult, setCollaborationResult] = useState(null);
  const [loadingResult, setLoadingResult] = useState(false);
  const [assignmentResult, setAssignmentResult] = useState(null);
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  const [assignmentInProgress, setAssignmentInProgress] = useState(false);
  const [evaluationDialogOpen, setEvaluationDialogOpen] = useState(false);
  const [evaluationInProgress, setEvaluationInProgress] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);
  
  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);

  // 轮询任务状态，当任务处于assigned状态时
  useEffect(() => {
    if (task && task.status === 'assigned' && !isPolling) {
      setIsPolling(true);
      const interval = setInterval(async () => {
        try {
          const statusResponse = await taskApi.getTaskStatus(taskId);
          setTaskStatus(statusResponse);
          
          // 如果任务完成，停止轮询并刷新任务详情
          if (statusResponse.status === 'completed') {
            clearInterval(interval);
            setIsPolling(false);
            fetchTaskDetails();
          }
        } catch (error) {
          console.error('Error polling task status:', error);
        }
      }, 3000); // 每3秒轮询一次

      return () => {
        clearInterval(interval);
        setIsPolling(false);
      };
    }
  }, [task, taskId, isPolling]);

  // Refresh data when page regains focus (when returning from other pages)
  useEffect(() => {
    const handleFocus = () => {
      fetchTaskDetails();
    };
    
    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, []);
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      // If Unix timestamp (number), convert to milliseconds
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
      console.log('🔍 Fetching task details for ID:', taskId);
      
      // Force direct API call to bypass service monitor
      const apiClient = axios.create({
        baseURL: 'http://localhost:8001',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('🚀 Making direct API call to /tasks/' + taskId);
      const directResponse = await apiClient.get(`/tasks/${taskId}`);
      console.log('📄 Direct API response:', directResponse.data);
      
      if (directResponse.data && directResponse.data.task) {
        console.log('✅ Task data from direct API:', directResponse.data.task);
        console.log('Task status:', directResponse.data.task.status);
        console.log('Task result:', directResponse.data.task.result);
        setTask(directResponse.data.task);
        return; // Skip the regular API call
      }
      
      // Fallback to regular API call
      const response = await taskApi.getTaskById(taskId);
      console.log('📄 API response:', response);
      
      if (response && response.task) {
        console.log('✅ Task data:', response.task);
        console.log('Task status:', response.task.status);
        console.log('Task result:', response.task.result);
        setTask(response.task);
      } else {
        console.error('❌ No task data in response:', response);
        throw new Error('Task data not found');
      }
    } catch (error) {
      console.error('❌ Error fetching task details:', error);
      console.error('Error details:', error.message);
      console.error('Error stack:', error.stack);
      setError('Failed to fetch task details. Using sample data instead.');
      setSnackbarSeverity('warning');
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

  const fetchCollaborationResult = async () => {
    console.log('🔍 fetchCollaborationResult called');
    console.log('Task object:', task);
    console.log('Task result:', task?.result);
    
    if (!task) {
      setError('No task data available');
      return;
    }

    if (!task.result) {
      console.log('❌ No IPFS CID in task result field');
      setError('No collaboration result available for this task');
      return;
    }

    // First, try to get the real IPFS CID from the new API endpoint
    let ipfsCid = null;
    let resultData = null;
    
    try {
      setLoadingResult(true);
      
      // Force direct API call to get IPFS CID
      const apiClient = axios.create({
        baseURL: 'http://localhost:8001',
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('🚀 Getting IPFS CID for task:', taskId);
      const ipfsCidResponse = await apiClient.get(`/collaboration/task/${taskId}/ipfs-cid`);
      console.log('✅ IPFS CID API response:', ipfsCidResponse.data);
      
      if (ipfsCidResponse.data.success && ipfsCidResponse.data.ipfs_cid) {
        ipfsCid = ipfsCidResponse.data.ipfs_cid;
        console.log('✅ Got real IPFS CID from API:', ipfsCid);
      }
    } catch (ipfsError) {
      console.log('⚠️ Failed to get IPFS CID from API, falling back to parsing task.result');
      console.log('Error:', ipfsError.message);
    }
    
    // Fallback: Parse the result JSON to extract IPFS CID
    if (!ipfsCid) {
      try {
        // Try to parse result as JSON first
        resultData = JSON.parse(task.result);
        console.log('📋 Parsed result data:', resultData);
        
        // Look for IPFS CID in various possible fields
        ipfsCid = resultData.conversation_ipfs || 
                  resultData.ipfs_cid || 
                  resultData.final_result ||
                  (typeof resultData.final_result === 'string' && resultData.final_result.includes('Qm') 
                    ? resultData.final_result.match(/Qm[A-Za-z0-9]{44,}/)?.[0] 
                    : null);
        
        console.log('🔍 Extracted IPFS CID from result:', ipfsCid);
        
        // If no IPFS CID in parsed JSON, treat the whole result as potential CID
        if (!ipfsCid && typeof task.result === 'string' && task.result.startsWith('Qm')) {
          ipfsCid = task.result;
          console.log('🔍 Using task.result directly as IPFS CID:', ipfsCid);
        }
      } catch (parseError) {
        console.log('📋 Result is not JSON, treating as direct IPFS CID:', task.result);
        // If parsing fails, assume it's a direct IPFS CID
        if (typeof task.result === 'string' && task.result.startsWith('Qm')) {
          ipfsCid = task.result;
        }
      }
    }
    
    if (!ipfsCid) {
      console.log('❌ No valid IPFS CID found in result data');
      // If no IPFS CID found, show the parsed result data instead
      if (resultData) {
        setCollaborationResult({
          collaboration_id: resultData.collaboration_id || 'unknown',
          task_title: task.title,
          agents: resultData.participants || [],
          conversation: [{
            sender_address: 'system',
            content: 'Task completed successfully, but conversation data is not available.',
            timestamp: resultData.completed_at
          }],
          api_mode: 'fallback',
          ipfs_cid: null,
          timestamp: resultData.execution_time
        });
        return;
      } else {
        setError('No collaboration result available for this task');
        return;
      }
    }

    try {
      // setLoadingResult is already set to true above
      console.log('🚀 Fetching real IPFS data with CID:', ipfsCid);
      
      // Force direct API call to bypass service monitor  
      const apiClient = axios.create({
        baseURL: 'http://localhost:8001',
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('🚀 Making direct API call to /collaboration/ipfs/' + ipfsCid);
      const cacheBuster = Date.now();
      const directResponse = await apiClient.get(`/collaboration/ipfs/${ipfsCid}?t=${cacheBuster}`);
      console.log('✅ IPFS API response received');
      console.log('📄 Response data:', JSON.stringify(directResponse.data, null, 2));
      console.log('📋 Task title in response:', directResponse.data?.task_title);
      console.log('🗣️ First conversation message:', directResponse.data?.conversation?.[0]?.content?.substring(0, 100));
      
      if (directResponse.data && directResponse.data.conversation) {
        console.log('✅ Setting real IPFS collaboration result');
        console.log('📋 Raw conversation data:', directResponse.data.conversation);
        console.log('📋 Agents data:', directResponse.data.agents);
        
        // Process and format the IPFS data to match expected structure
        const processedConversation = (directResponse.data.conversation || []).map((message, index) => {
          // For assistant messages, try to extract agent name from content
          if (message.role === 'assistant' && message.content) {
            // Try to match different agent naming patterns
            const agentMatch = message.content.match(/^(Agent\d+):\s/) || 
                             message.content.match(/^(Agent\s+\d+):\s/) ||
                             message.content.match(/^(\w+Agent\d*):\s/);
            
            if (agentMatch) {
              const agentName = agentMatch[1];
              // Find the corresponding agent info
              const agentInfo = directResponse.data.agents?.find(agent => 
                agent.name === agentName || agent.agent_id === agentName
              );
              
              return {
                ...message,
                sender_address: agentInfo?.agent_id || agentName,
                agent_name: agentName,
                agent_capabilities: agentInfo?.capabilities || [],
                timestamp: directResponse.data.timestamp || new Date().toISOString(),
                round_number: Math.floor((index - 1) / 4) + 1, // Assuming 4 agents per round, skip system message
                message_index: index
              };
            } else {
              // If no agent pattern found, this might be a summary or final result
              return {
                ...message,
                sender_address: 'assistant',
                agent_name: 'AI Collaboration Summary',
                timestamp: directResponse.data.timestamp || new Date().toISOString(),
                message_index: index
              };
            }
          }
          
          // For system and user messages
          return {
            ...message,
            sender_address: message.role,
            agent_name: message.role === 'system' ? 'System' : message.role === 'user' ? 'User' : 'Unknown',
            timestamp: directResponse.data.timestamp || new Date().toISOString(),
            message_index: index
          };
        });

        console.log('🔧 Processed conversation:', processedConversation);
        console.log('🔧 Sample processed message:', processedConversation[1]); // Check first assistant message

        setCollaborationResult({
          collaboration_id: directResponse.data.collaboration_id || `ipfs_${ipfsCid}`,
          task_id: directResponse.data.task_id || taskId,
          task_title: directResponse.data.task_title || task.title,
          agents: directResponse.data.agents || [],
          conversation: processedConversation,
          result: null, // IPFS data doesn't have separate result field
          api_mode: directResponse.data.api_mode || 'real',
          ipfs_cid: ipfsCid,
          timestamp: directResponse.data.timestamp
        });
      } else {
        console.error('❌ Invalid IPFS response structure:', directResponse.data);
        setError('Invalid collaboration result format');
      }
    } catch (error) {
      console.error('❌ Error fetching IPFS collaboration result:', error);
      console.error('Error details:', error.message);
      console.error('Error response:', error.response?.data);
      setError(`Failed to fetch collaboration result: ${error.message}`);
    } finally {
      setLoadingResult(false);
    }
  };

  const handleViewResult = () => {
    setResultDialogOpen(true);
    fetchCollaborationResult();
  };

  const handleTaskEvaluation = async (success, rating = 5) => {
    try {
      setEvaluationInProgress(true);
      console.log(`🎯 Evaluating task as ${success ? 'successful' : 'failed'} with rating ${rating}`);
      
      const evaluationData = {
        task_id: taskId,
        success: success,
        rating: rating,
        evaluator: 'user', // 用户手动评估
        notes: success ? 'Task completed successfully by user evaluation' : 'Task marked as failed by user evaluation'
      };
      
      const response = await taskApi.evaluateTask(taskId, evaluationData);
      console.log('✅ Task evaluation result:', response);
      
      if (response.success) {
        setEvaluationResult(response);
        setError(`Task ${success ? 'completed' : 'failed'} successfully! Learning data updated.`);
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        
        // 刷新任务详情
        setTimeout(() => {
          fetchTaskDetails();
        }, 1000);
      } else {
        throw new Error(response.message || 'Failed to evaluate task');
      }
    } catch (error) {
      console.error('❌ Error evaluating task:', error);
      setError(`Failed to evaluate task: ${error.message}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setEvaluationInProgress(false);
      setEvaluationDialogOpen(false);
    }
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  const [deletionPreview, setDeletionPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  const handleDeleteTask = async () => {
    try {
      console.log('🗑️ Deleting task:', taskId);
      const result = await taskApi.deleteTask(taskId);
      console.log('✅ Task deletion result:', result);
      
      setDeleteDialogOpen(false);
      
      // Update the task object to reflect deletion
      if (task) {
        setTask({
          ...task,
          status: 'cancelled'
        });
      }
      
      // Immediately navigate back to tasks list with refresh parameter
      navigate('/tasks', { 
        replace: true,
        state: { 
          refreshTasks: true, 
          deletedTaskId: taskId,
          successMessage: 'Task deleted successfully!'
        }
      });
    } catch (error) {
      console.error('❌ Error deleting task:', error);
      setDeleteDialogOpen(false);
      setError(`Failed to delete task: ${error.response?.data?.detail || error.message}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleDeleteClick = async () => {
    try {
      setLoadingPreview(true);
      console.log('🔍 Fetching deletion preview for task:', taskId);
      
      const preview = await taskApi.previewTaskDeletion(taskId);
      console.log('📋 Deletion preview:', preview);
      
      setDeletionPreview(preview);
      setDeleteDialogOpen(true);
    } catch (error) {
      console.error('❌ Error fetching deletion preview:', error);
      setError(`Failed to preview deletion: ${error.message}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoadingPreview(false);
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
      case 'cancelled':
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
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
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
          {task.status === 'completed' && (
            <>
              <Button 
                variant="outlined" 
                color="info"
                onClick={handleViewResult}
                startIcon={<ChatIcon />}
              >
                View Result
              </Button>
              <Button 
                variant="outlined" 
                color="success"
                onClick={() => setEvaluationDialogOpen(true)}
                startIcon={<CheckCircleIcon />}
              >
                Evaluate Task
              </Button>
            </>
          )}
          <Button 
            variant="outlined" 
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteClick}
            disabled={loadingPreview}
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
                  <StepLabel>
                    {task.status === 'cancelled' ? 'Cancelled' : 
                     task.status === 'failed' ? 'Failed' : 'Completed'}
                  </StepLabel>
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
                  {(task.assigned_agents?.length > 0 || task.assigned_agent) && (
                    <ListItem sx={{ pb: 2 }}>
                      <ListItemIcon>
                        <PersonIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={task.assigned_agents?.length > 1 ? "Assigned Agents" : "Assigned To"} 
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {task.assigned_agents?.length > 0 ? (
                              task.assigned_agents.map((agent, index) => (
                                <Box 
                                  key={agent}
                                  sx={{ 
                                    display: 'flex', 
                                    alignItems: 'center',
                                    cursor: 'pointer',
                                    mb: index < task.assigned_agents.length - 1 ? 1 : 0
                                  }}
                                  onClick={() => navigate(`/agents/${agent}`)}
                                >
                                  <Avatar 
                                    sx={{ 
                                      width: 24, 
                                      height: 24, 
                                      mr: 1, 
                                      bgcolor: generateAvatarColor(agent) 
                                    }}
                                  >
                                    {agent.substring(2, 4)}
                                  </Avatar>
                                  {formatAddress(agent)}
                                  {index === 0 && task.assigned_agents.length > 1 && (
                                    <Chip 
                                      label="Primary" 
                                      size="small" 
                                      sx={{ ml: 1, fontSize: '0.7rem' }}
                                    />
                                  )}
                                </Box>
                              ))
                            ) : (
                              task.assigned_agent && (
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
                              )
                            )}
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
          
          {/* Task History with Real Blockchain Data */}
          <TaskHistory taskId={task.task_id} />
        </Grid>
        
        <Grid item xs={12} md={4}>
          {/* Status-specific Information Panel */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {task.status === 'open' && 'Required Capabilities'}
              {task.status === 'assigned' && 'Assigned Agents'}
              {task.status === 'completed' && 'Task Results'}
            </Typography>
            
            {task.status === 'open' && (
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
            )}
            
            {task.status === 'assigned' && (task.assigned_agents?.length > 0 || task.assigned_agent) && (
              <Box>
                <List>
                  {task.assigned_agents?.length > 0 ? (
                    task.assigned_agents.map((agent, index) => (
                      <ListItem key={agent}>
                        <ListItemIcon>
                          <Avatar 
                            sx={{ 
                              bgcolor: generateAvatarColor(agent) 
                            }}
                          >
                            {agent.substring(2, 4)}
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
                              onClick={() => navigate(`/agents/${agent}`)}
                            >
                              {formatAddress(agent)}
                              {index === 0 && (
                                <Chip 
                                  label="Primary" 
                                  size="small" 
                                  sx={{ ml: 1, fontSize: '0.7rem' }}
                                />
                              )}
                            </Box>
                          }
                          secondary={index === 0 ? "Primary assigned agent" : "Collaborating agent"}
                        />
                      </ListItem>
                    ))
                  ) : (
                    task.assigned_agent && (
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
                    )
                  )}
                </List>
                
                {/* 进度指示器 */}
                {taskStatus && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Collaboration Progress
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={taskStatus.collaboration_progress?.percentage || 0} 
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {taskStatus.collaboration_progress?.percentage || 0}%
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {taskStatus.collaboration_progress?.stage || 'Processing...'}
                    </Typography>
                    <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                      {taskStatus.message}
                    </Typography>
                  </Box>
                )}
                
                <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                  {task.assigned_agents?.length > 1 ? 
                    `${task.assigned_agents.length} agents collaborating on this task` : 
                    'Agent collaboration in progress...'
                  }
                </Typography>
              </Box>
            )}
            
            {task.status === 'completed' && (
              <Box>
                {(task.assigned_agents?.length > 0 || task.assigned_agent) && (
                  <List>
                    {task.assigned_agents?.length > 0 ? (
                      task.assigned_agents.map((agent, index) => (
                        <ListItem key={agent}>
                          <ListItemIcon>
                            <Avatar 
                              sx={{ 
                                bgcolor: generateAvatarColor(agent) 
                              }}
                            >
                              {agent.substring(2, 4)}
                            </Avatar>
                          </ListItemIcon>
                          <ListItemText 
                            primary={formatAddress(agent)}
                            secondary={index === 0 ? "Primary agent - Completed" : "Collaborating agent - Completed"}
                          />
                        </ListItem>
                      ))
                    ) : (
                      task.assigned_agent && (
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
                            primary={formatAddress(task.assigned_agent)}
                            secondary="Completed by agent"
                          />
                        </ListItem>
                      )
                    )}
                  </List>
                )}
                <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                  Task completed successfully. Click 'View Result' to see collaboration results.
                </Typography>
              </Box>
            )}
            
            {!task.assigned_agent && (!task.assigned_agents || task.assigned_agents.length === 0) && task.status !== 'open' && (
              <Typography variant="body2" color="textSecondary">
                No agents assigned yet
              </Typography>
            )}
          </Paper>
          
          {task.status === 'open' && (
            <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Task Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={async () => {
                    try {
                      setLoading(true);
                      setAssignmentInProgress(true);
                      console.log('🚀 Starting smart agent collaboration for task:', taskId);
                      console.log('🔧 Button clicked, calling taskApi.smartAssignTask...');
                      const result = await taskApi.smartAssignTask(taskId, true, 4);
                      console.log('✅ Smart assignment result:', result);
                      
                      if (result.success) {
                        // 显示详细的分配结果
                        setAssignmentResult(result);
                        setAssignmentDialogOpen(true);
                        
                        // 根据结果状态显示不同消息
                        const statusMessage = result.status === 'assigned' 
                          ? `Task assigned successfully! ${result.message || 'Agents are now working on this task.'}`
                          : `Agent collaboration started! ${result.message || 'Agents are now working on this task.'}`;
                        
                        setError(statusMessage);
                        setSnackbarSeverity('success');
                        setSnackbarOpen(true);
                        
                        // 立即刷新任务详情以显示新状态
                        setTimeout(() => {
                          fetchTaskDetails();
                        }, 1000);
                      } else {
                        throw new Error(result.message || 'Failed to start collaboration');
                      }
                    } catch (error) {
                      console.error('❌ Error starting collaboration:', error);
                      console.error('❌ Error details:', {
                        message: error.message,
                        stack: error.stack,
                        name: error.name
                      });
                      setError(`Failed to start collaboration: ${error.message}`);
                      setSnackbarSeverity('error');
                      setSnackbarOpen(true);
                    } finally {
                      setLoading(false);
                      setAssignmentInProgress(false);
                    }
                  }}
                  startIcon={<GroupIcon />}
                  disabled={loading}
                >
                  {loading ? 'Starting...' : 'Start Agent Collaboration'}
                </Button>
                
                {assignmentInProgress && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                    <Typography variant="body2" gutterBottom color="primary" fontWeight="medium">
                      🤖 Analyzing task requirements and selecting agents...
                    </Typography>
                    <LinearProgress sx={{ mt: 1 }} />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      This may take a few seconds while we find the best agents for your task.
                    </Typography>
                  </Box>
                )}
                <Button 
                  variant="outlined" 
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/tasks/${taskId}/edit`)}
                >
                  Edit Task
                </Button>
              </Box>
            </Paper>
          )}
          
          {task.status === 'assigned' && (
            <Paper variant="outlined" sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Task Status
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Agents are actively working on this task!</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    The collaboration started automatically when the task was assigned. 
                    You can monitor the progress above and wait for completion.
                  </Typography>
                </Alert>
                
                {taskStatus && taskStatus.estimated_completion && (
                  <Typography variant="body2" color="textSecondary">
                    <strong>Estimated completion:</strong> {new Date(taskStatus.estimated_completion).toLocaleString()}
                  </Typography>
                )}
                
                <Typography variant="body2" color="textSecondary">
                  The task will automatically change to "Completed" status when agents finish their collaboration.
                  You'll then be able to view the results.
                </Typography>
                
                {/* Optional manual controls for debugging/testing */}
                <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                  <Typography variant="caption" color="textSecondary" gutterBottom>
                    Manual Controls (for testing):
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button 
                      size="small"
                      variant="outlined" 
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={async () => {
                        try {
                          await taskApi.completeTask(task.task_id, { status: 'completed' });
                          fetchTaskDetails();
                        } catch (error) {
                          console.error('Error completing task:', error);
                          setError('Failed to complete task');
                          setSnackbarSeverity('error');
                          setSnackbarOpen(true);
                        }
                      }}
                    >
                      Force Complete
                    </Button>
                    <Button 
                      size="small"
                      variant="outlined" 
                      color="error"
                      startIcon={<CancelIcon />}
                      onClick={async () => {
                        try {
                          await taskApi.completeTask(task.task_id, { status: 'failed' });
                          fetchTaskDetails();
                        } catch (error) {
                          console.error('Error marking task as failed:', error);
                          setError('Failed to update task status');
                          setSnackbarSeverity('error');
                          setSnackbarOpen(true);
                        }
                      }}
                    >
                      Force Fail
                    </Button>
                  </Box>
                </Box>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
      
      {/* Agent Assignment Result Dialog */}
      <Dialog 
        open={assignmentDialogOpen} 
        onClose={() => setAssignmentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <GroupIcon color="primary" />
            Agent Collaboration Started
          </Box>
        </DialogTitle>
        <DialogContent>
          {assignmentResult && (
            <Box>
              <DialogContentText sx={{ mb: 3 }}>
                Task "{assignmentResult.task_title}" has been successfully assigned to {assignmentResult.selected_agents?.length || 0} agent(s). 
                Here are the details of the selected team:
              </DialogContentText>
              
              {/* Team Analysis Summary */}
              <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Typography variant="h6" gutterBottom>Team Analysis</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Team Size</Typography>
                    <Typography variant="h6">{assignmentResult.team_analysis?.team_size || 0}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Capability Coverage</Typography>
                    <Typography variant="h6" color={assignmentResult.team_analysis?.capability_coverage >= 80 ? 'success.main' : 'warning.main'}>
                      {assignmentResult.team_analysis?.capability_coverage || 0}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Average Reputation</Typography>
                    <Typography variant="h6">{assignmentResult.team_analysis?.average_reputation || 0}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Team Score</Typography>
                    <Typography variant="h6">{assignmentResult.team_analysis?.team_score || 0}</Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Required vs Covered Capabilities */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>Capability Requirements</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">Required:</Typography>
                  {assignmentResult.required_capabilities?.map((cap, index) => (
                    <Chip
                      key={index}
                      label={cap}
                      size="small"
                      color={assignmentResult.team_analysis?.covered_capabilities?.includes(cap) ? 'success' : 'default'}
                      variant={assignmentResult.team_analysis?.covered_capabilities?.includes(cap) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
                {assignmentResult.team_analysis?.missing_capabilities?.length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Typography variant="body2" color="error">Missing:</Typography>
                    {assignmentResult.team_analysis.missing_capabilities.map((cap, index) => (
                      <Chip
                        key={index}
                        label={cap}
                        size="small"
                        color="error"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                )}
              </Box>

              {/* Selected Agents Table */}
              <Typography variant="subtitle1" gutterBottom>Selected Agents</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Agent</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Capabilities</TableCell>
                    <TableCell align="right">Reputation</TableCell>
                    <TableCell align="right">Match Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {assignmentResult.selected_agents?.map((agent, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
                            {agent.name?.charAt(0) || 'A'}
                          </Avatar>
                          <Typography variant="body2">{agent.name || 'Unknown Agent'}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={agent.role || 'Agent'} 
                          size="small" 
                          color={agent.agent_type === 2 ? 'primary' : 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {agent.capabilities?.slice(0, 3).map((cap, capIndex) => (
                            <Chip
                              key={capIndex}
                              label={cap}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem', height: 20 }}
                            />
                          ))}
                          {agent.capabilities?.length > 3 && (
                            <Typography variant="caption" color="textSecondary">
                              +{agent.capabilities.length - 3} more
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {agent.reputation || 0}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          variant="body2" 
                          fontWeight="medium"
                          color={agent.match_score >= 80 ? 'success.main' : agent.match_score >= 60 ? 'warning.main' : 'text.secondary'}
                        >
                          {agent.match_score || 0}%
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                <Typography variant="body2" color="success.dark">
                  <strong>Status:</strong> {assignmentResult.message}
                </Typography>
                {assignmentResult.blockchain_updated && assignmentResult.transaction_hash && (
                  <Typography variant="caption" color="success.dark" sx={{ mt: 1, display: 'block' }}>
                    <strong>Blockchain Transaction:</strong> {assignmentResult.transaction_hash.substring(0, 10)}...
                  </Typography>
                )}
                {assignmentResult.status === 'assigned' && (
                  <Typography variant="caption" color="success.dark" sx={{ mt: 1, display: 'block' }}>
                    ✅ Task status updated to "Assigned". The collaboration will continue until completion.
                  </Typography>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignmentDialogOpen(false)} variant="outlined">
            Close
          </Button>
          {assignmentResult?.status === 'completed' ? (
            <Button 
              onClick={() => {
                setAssignmentDialogOpen(false);
                navigate(`/tasks/${taskId}/conversations`);
              }}
              variant="contained"
              startIcon={<ChatIcon />}
            >
              View Results
            </Button>
          ) : (
            <Button 
              onClick={() => {
                setAssignmentDialogOpen(false);
                // 刷新页面状态
                fetchTaskDetails();
              }}
              variant="contained"
              color="primary"
            >
              Monitor Progress
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <DeleteIcon sx={{ mr: 1, color: 'error.main' }} />
            Delete Task
          </Box>
        </DialogTitle>
        <DialogContent>
          {deletionPreview ? (
            <Box>
              <Alert severity={deletionPreview.can_delete ? "warning" : "error"} sx={{ mb: 2 }}>
                {deletionPreview.can_delete 
                  ? "This action will permanently delete the task and all related data. This cannot be undone."
                  : "This task cannot be deleted in its current state."
                }
              </Alert>
              
              <Typography variant="h6" gutterBottom>
                Data Impact Summary
              </Typography>
              
              {deletionPreview.data_impact && !deletionPreview.data_impact.error && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    The following data will be permanently deleted:
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2">• {deletionPreview.data_impact.conversations || 0} collaboration conversations</Typography>
                    <Typography variant="body2">• {deletionPreview.data_impact.messages || 0} conversation messages</Typography>
                    <Typography variant="body2">• {deletionPreview.data_impact.results || 0} collaboration results</Typography>
                    <Typography variant="body2">• {deletionPreview.data_impact.blockchain_events || 0} blockchain events</Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mt: 1, fontWeight: 'bold' }}>
                    Total records to be deleted: {deletionPreview.data_impact.total_records || 0}
                  </Typography>
                </Box>
              )}
              
              {deletionPreview.warnings && deletionPreview.warnings.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="error" gutterBottom>
                    Warnings:
                  </Typography>
                  {deletionPreview.warnings.map((warning, index) => (
                    <Typography key={index} variant="body2" color="error" sx={{ pl: 2 }}>
                      • {warning}
                    </Typography>
                  ))}
                </Box>
              )}
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Task Status: <Chip label={deletionPreview.task_status} size="small" />
                </Typography>
              </Box>
            </Box>
          ) : (
            <Typography>
              Loading deletion preview...
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteTask} 
            color="error" 
            variant="contained"
            disabled={!deletionPreview?.can_delete}
          >
            {deletionPreview?.can_delete ? 'Delete Permanently' : 'Cannot Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Collaboration Result Dialog */}
      <Dialog
        open={resultDialogOpen}
        onClose={() => setResultDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <ChatIcon sx={{ mr: 1 }} />
            Collaboration Result
          </Box>
        </DialogTitle>
        <DialogContent>
          {loadingResult ? (
            <Box display="flex" justifyContent="center" alignItems="center" p={3}>
              <CircularProgress />
              <Typography variant="body2" sx={{ ml: 2 }}>
                Loading collaboration result...
              </Typography>
            </Box>
          ) : collaborationResult ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                Task: {collaborationResult.task_title}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Collaboration ID: {collaborationResult.collaboration_id}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Agents: {collaborationResult.agents?.length || 0} participants
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                API Mode: {collaborationResult.api_mode || 'real'}
              </Typography>
              
              {collaborationResult.ipfs_cid && (
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  IPFS CID: {collaborationResult.ipfs_cid}
                </Typography>
              )}
              
              {collaborationResult.timestamp && (
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Completed: {new Date(collaborationResult.timestamp * 1000).toLocaleString()}
                </Typography>
              )}
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Conversation:
              </Typography>
              
              {collaborationResult.conversation && collaborationResult.conversation.length > 0 ? (
                <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
                  {collaborationResult.conversation.map((message, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="subtitle2" color="primary">
                            {message.sender_address === 'system' ? 'System' : 
                             message.sender_address === 'user' ? 'User' : 
                             message.agent_name || `Agent ${message.sender_address?.substring(0, 8)}...`}
                          </Typography>
                          {message.timestamp && (
                            <Typography variant="caption" color="textSecondary">
                              {new Date(message.timestamp).toLocaleString()}
                            </Typography>
                          )}
                        </Box>
                        <Typography variant="body2" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                          {message.content}
                        </Typography>
                        {message.round_number && (
                          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                            Round {message.round_number}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No conversation data available
                </Typography>
              )}
              
              <Divider sx={{ my: 2 }} />
              
              {collaborationResult.result && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Final Result:
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {typeof collaborationResult.result === 'string' 
                        ? collaborationResult.result 
                        : collaborationResult.result?.final_result || 'No final result available'}
                    </Typography>
                  </Paper>
                  
                  {collaborationResult.result?.conversation_summary && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Summary:
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {collaborationResult.result.conversation_summary}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
              
              <Typography variant="caption" color="textSecondary">
                {collaborationResult?.ipfs_cid ? `IPFS CID: ${collaborationResult.ipfs_cid}` : 'Source: Database/API'}
              </Typography>
            </Box>
          ) : (
            <Typography variant="body2" color="textSecondary">
              No collaboration result available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResultDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Evaluation Dialog */}
      <Dialog
        open={evaluationDialogOpen}
        onClose={() => setEvaluationDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" />
            Evaluate Task Completion
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Task: {task.title}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Please evaluate how well the agents completed this task. This will update their learning data and reputation.
            </Typography>
            
            <FormControl component="fieldset" sx={{ mt: 3 }}>
              <FormLabel component="legend">Task Outcome</FormLabel>
              <RadioGroup
                defaultValue="success"
                name="task-outcome"
              >
                <FormControlLabel 
                  value="success" 
                  control={<Radio />} 
                  label="✅ Task Completed Successfully - Agents performed well" 
                />
                <FormControlLabel 
                  value="failed" 
                  control={<Radio />} 
                  label="❌ Task Failed - Agents did not meet expectations" 
                />
              </RadioGroup>
            </FormControl>
            
            <Box sx={{ mt: 3 }}>
              <Typography component="legend">Overall Quality Rating</Typography>
              <Rating
                name="task-rating"
                defaultValue={4}
                precision={1}
                size="large"
                sx={{ mt: 1 }}
              />
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
                This rating will affect agent reputation and learning
              </Typography>
            </Box>

            {task.assigned_agents && task.assigned_agents.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Participating Agents:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {task.assigned_agents.map((agent, index) => (
                    <Chip
                      key={agent}
                      label={`Agent ${index + 1}: ${formatAddress(agent)}`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setEvaluationDialogOpen(false)}
            disabled={evaluationInProgress}
          >
            Cancel
          </Button>
          <Button 
            onClick={() => {
              const outcome = document.querySelector('input[name="task-outcome"]:checked')?.value || 'success';
              const rating = document.querySelector('input[name="task-rating"]')?.value || 4;
              handleTaskEvaluation(outcome === 'success', parseInt(rating));
            }}
            variant="contained"
            color="success"
            disabled={evaluationInProgress}
            startIcon={evaluationInProgress ? <CircularProgress size={20} /> : <CheckCircleIcon />}
          >
            {evaluationInProgress ? 'Evaluating...' : 'Submit Evaluation'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskDetails;