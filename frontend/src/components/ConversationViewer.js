import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  Chip,
  Paper,
  Divider,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Fab
} from '@mui/material';
// Timeline 组件使用简单的替代方案，避免依赖 @mui/lab
import {
  Chat as ChatIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  AutoAwesome as AutoAwesomeIcon,
  Psychology as PsychologyIcon,
  Groups as GroupsIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';

const ConversationViewer = () => {
  const { taskId, conversationId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [conversation, setConversation] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [error, setError] = useState(null);
  const [startingCollaboration, setStartingCollaboration] = useState(false);

  useEffect(() => {
    if (conversationId) {
      fetchConversationDetails();
    } else {
      fetchTaskConversations();
    }
  }, [taskId, conversationId]);

  const fetchConversationDetails = async () => {
    setLoading(true);
    try {
      const response = await taskApi.getConversationDetails(taskId, conversationId);
      if (response.success) {
        setConversation(response.conversation);
      } else {
        throw new Error('Failed to fetch conversation details');
      }
    } catch (error) {
      console.error('Error fetching conversation details:', error);
      setError('Failed to load conversation details');
    } finally {
      setLoading(false);
    }
  };

  const fetchTaskConversations = async () => {
    setLoading(true);
    try {
      const response = await taskApi.getTaskConversations(taskId);
      // 如果有对话，显示第一个对话的详情
      if (response.conversations && response.conversations.length > 0) {
        const firstConversation = response.conversations[0];
        navigate(`/tasks/${taskId}/conversations/${firstConversation.conversation_id}`);
      } else {
        setConversation(null);
      }
    } catch (error) {
      console.error('Error fetching task conversations:', error);
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleStartRealCollaboration = async () => {
    setStartingCollaboration(true);
    try {
      const response = await taskApi.startRealCollaboration(taskId);
      if (response.success) {
        // 跳转到新创建的对话
        navigate(`/tasks/${taskId}/conversations/${response.conversation_id}`);
      } else {
        throw new Error('Failed to start collaboration');
      }
    } catch (error) {
      console.error('Error starting real collaboration:', error);
      setError('Failed to start collaboration');
    } finally {
      setStartingCollaboration(false);
      setDialogOpen(false);
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

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button onClick={() => navigate(`/tasks/${taskId}`)}>
          Back to Task
        </Button>
      </Box>
    );
  }

  if (!conversation) {
    return (
      <Box sx={{ textAlign: 'center', py: 5 }}>
        <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary" gutterBottom>
          No Agent Collaboration Found
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          This task hasn't started agent collaboration yet.
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AutoAwesomeIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{ mr: 2 }}
        >
          Start AI Collaboration
        </Button>
        <Button onClick={() => navigate(`/tasks/${taskId}`)}>
          Back to Task
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Agent Collaboration
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Task: {conversation.task_description}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            label={conversation.status.charAt(0).toUpperCase() + conversation.status.slice(1)}
            color={conversation.status === 'completed' ? 'success' : 'primary'}
            icon={conversation.status === 'completed' ? <CheckCircleIcon /> : <ChatIcon />}
          />
          <Button onClick={() => navigate(`/tasks/${taskId}`)}>
            Back to Task
          </Button>
        </Box>
      </Box>

      {/* Participants */}
      <Card sx={{ mb: 3 }}>
        <CardHeader 
          title="Collaboration Participants"
          avatar={<GroupsIcon />}
        />
        <CardContent>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {conversation.participants.map((participant, index) => {
              const agentRole = conversation.agent_roles[participant];
              return (
                <Card key={participant} variant="outlined" sx={{ minWidth: 200 }}>
                  <CardContent sx={{ py: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Avatar 
                        sx={{ 
                          width: 32, 
                          height: 32, 
                          mr: 1,
                          bgcolor: generateAvatarColor(participant)
                        }}
                      >
                        {participant.substring(2, 4)}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {agentRole?.agent_name || `Agent ${index + 1}`}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {formatAddress(participant)}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {agentRole?.capabilities.map((capability) => (
                        <Chip 
                          key={capability}
                          label={capability}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              );
            })}
          </Box>
        </CardContent>
      </Card>

      {/* Conversation Messages */}
      <Card sx={{ mb: 3 }}>
        <CardHeader 
          title="Collaboration Messages"
          avatar={<ChatIcon />}
          action={
            <Typography variant="body2" color="textSecondary">
              {conversation.messages.length} messages
            </Typography>
          }
        />
        <CardContent>
          {conversation.messages.length > 0 ? (
            <Box>
              {conversation.messages.map((message, index) => {
                const agentRole = conversation.agent_roles[message.sender_address];
                const isSystemMessage = message.sender_address === 'system';
                
                return (
                  <Box key={message.id} sx={{ mb: 2 }}>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar 
                            sx={{ 
                              width: 32, 
                              height: 32, 
                              mr: 1.5,
                              bgcolor: isSystemMessage ? '#9e9e9e' : generateAvatarColor(message.sender_address)
                            }}
                          >
                            {isSystemMessage ? <ScheduleIcon fontSize="small" /> : message.sender_address.substring(2, 4)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2">
                              {isSystemMessage 
                                ? 'System' 
                                : agentRole?.agent_name || `Agent ${message.message_index + 1}`
                              }
                            </Typography>
                            {!isSystemMessage && (
                              <Typography variant="caption" color="textSecondary">
                                {formatAddress(message.sender_address)}
                              </Typography>
                            )}
                          </Box>
                          {message.round_number && (
                            <Chip 
                              label={`Round ${message.round_number}`}
                              size="small"
                              sx={{ ml: 2 }}
                              color="primary"
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          {formatTimestamp(message.timestamp)}
                        </Typography>
                      </Box>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', ml: 6 }}>
                        {message.content}
                      </Typography>
                    </Paper>
                  </Box>
                );
              })}
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body2" color="textSecondary">
                No messages in this conversation yet.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Final Result */}
      {conversation.result && (
        <Card>
          <CardHeader 
            title="Collaboration Result"
            avatar={<CheckCircleIcon color="success" />}
          />
          <CardContent>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">Final Result Summary</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {conversation.result.conversation_summary}
                </Typography>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">Detailed Result</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {conversation.result.final_result}
                </Typography>
              </AccordionDetails>
            </Accordion>

            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Completed: {formatTimestamp(conversation.result.created_at)}
                </Typography>
                <br />
                <Typography variant="caption" color="textSecondary">
                  Total Messages: {conversation.result.message_count}
                </Typography>
              </Box>
              <Chip 
                label={conversation.result.success ? 'Success' : 'Failed'}
                color={conversation.result.success ? 'success' : 'error'}
                size="small"
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Start Collaboration FAB */}
      {conversation.status !== 'completed' && (
        <Fab
          color="primary"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => setDialogOpen(true)}
        >
          <AutoAwesomeIcon />
        </Fab>
      )}

      {/* Start Collaboration Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AutoAwesomeIcon sx={{ mr: 1 }} />
            Start AI Agent Collaboration
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            This will start a real AI collaboration using ChatGPT where assigned agents will:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemAvatar>
                <Avatar sx={{ width: 32, height: 32 }}>
                  <PsychologyIcon fontSize="small" />
                </Avatar>
              </ListItemAvatar>
              <ListItemText 
                primary="Analyze the task requirements"
                secondary="Each agent will contribute based on their capabilities"
              />
            </ListItem>
            <ListItem>
              <ListItemAvatar>
                <Avatar sx={{ width: 32, height: 32 }}>
                  <ChatIcon fontSize="small" />
                </Avatar>
              </ListItemAvatar>
              <ListItemText 
                primary="Collaborate through multiple rounds"
                secondary="Agents will discuss and refine their approach"
              />
            </ListItem>
            <ListItem>
              <ListItemAvatar>
                <Avatar sx={{ width: 32, height: 32 }}>
                  <CheckCircleIcon fontSize="small" />
                </Avatar>
              </ListItemAvatar>
              <ListItemText 
                primary="Generate final result"
                secondary="A comprehensive solution will be produced"
              />
            </ListItem>
          </List>
          <Alert severity="info" sx={{ mt: 2 }}>
            This process may take a few minutes to complete and will be recorded on the blockchain.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleStartRealCollaboration}
            variant="contained"
            disabled={startingCollaboration}
            startIcon={startingCollaboration ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          >
            {startingCollaboration ? 'Starting...' : 'Start Collaboration'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConversationViewer;