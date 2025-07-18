import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
// Timeline component uses simple alternative to avoid @mui/lab dependency
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
      console.log('🔍 Fetching task conversations for task:', taskId);
      
      // First, try to get the task details to check if it's completed and has results
      const apiClient = axios.create({
        baseURL: 'http://localhost:8001',
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      // Get task details
      const taskResponse = await apiClient.get(`/tasks/${taskId}`);
      console.log('📄 Task details:', taskResponse.data);
      
      if (taskResponse.data?.task?.status === 'completed' && taskResponse.data?.task?.result) {
        console.log('✅ Task is completed, fetching collaboration result directly');
        
        // Try to get IPFS CID from our new API endpoint
        try {
          const ipfsCidResponse = await apiClient.get(`/collaboration/task/${taskId}/ipfs-cid`);
          if (ipfsCidResponse.data.success && ipfsCidResponse.data.ipfs_cid) {
            const ipfsCid = ipfsCidResponse.data.ipfs_cid;
            console.log('🎯 Got IPFS CID:', ipfsCid);
            
            // Fetch the actual collaboration data from IPFS
            const ipfsResponse = await apiClient.get(`/collaboration/ipfs/${ipfsCid}`);
            console.log('📋 IPFS collaboration data:', ipfsResponse.data);
            
            // Process the IPFS data similar to TaskDetails.js
            const processedConversation = (ipfsResponse.data.conversation || []).map((message, index) => {
              if (message.role === 'assistant' && message.content) {
                const agentMatch = message.content.match(/^(Agent\d+):\s/) || 
                                 message.content.match(/^(Agent\s+\d+):\s/) ||
                                 message.content.match(/^(\w+Agent\d*):\s/);
                
                if (agentMatch) {
                  const agentName = agentMatch[1];
                  const agentInfo = ipfsResponse.data.agents?.find(agent => 
                    agent.name === agentName || agent.agent_id === agentName
                  );
                  
                  return {
                    ...message,
                    sender_address: agentInfo?.agent_id || agentName,
                    agent_name: agentName,
                    agent_capabilities: agentInfo?.capabilities || [],
                    timestamp: ipfsResponse.data.timestamp || new Date().toISOString(),
                    round_number: Math.floor((index - 1) / 4) + 1,
                    message_index: index
                  };
                } else {
                  return {
                    ...message,
                    sender_address: 'assistant',
                    agent_name: 'AI Collaboration Summary',
                    timestamp: ipfsResponse.data.timestamp || new Date().toISOString(),
                    message_index: index
                  };
                }
              }
              
              return {
                ...message,
                sender_address: message.role,
                agent_name: message.role === 'system' ? 'System' : message.role === 'user' ? 'User' : 'Unknown',
                timestamp: ipfsResponse.data.timestamp || new Date().toISOString(),
                message_index: index
              };
            });
            
            // Set up conversation data
            setConversation({
              task_id: taskId,
              task_description: taskResponse.data.task.title,
              collaboration_id: ipfsResponse.data.collaboration_id,
              status: 'completed',
              participants: ipfsResponse.data.agents?.map(agent => agent.agent_id) || [],
              agent_roles: ipfsResponse.data.agents?.reduce((acc, agent) => {
                acc[agent.agent_id] = {
                  agent_name: agent.name,
                  capabilities: agent.capabilities
                };
                return acc;
              }, {}) || {},
              messages: processedConversation,
              result: {
                success: true,
                final_result: ipfsResponse.data.conversation?.[ipfsResponse.data.conversation.length - 1]?.content || 'Collaboration completed successfully',
                conversation_summary: 'Multi-agent collaboration completed with real AI interactions',
                message_count: processedConversation.length,
                completed_at: ipfsResponse.data.timestamp
              },
              final_result: {
                final_result: ipfsResponse.data.conversation?.[ipfsResponse.data.conversation.length - 1]?.content || 'Collaboration completed successfully',
                conversation_summary: 'Multi-agent collaboration completed with real AI interactions',
                completed_at: ipfsResponse.data.timestamp
              }
            });
            
            return;
          }
        } catch (ipfsError) {
          console.log('⚠️ Failed to get IPFS data, falling back to task result parsing');
        }
        
        // Fallback: try to parse task result JSON
        try {
          const resultData = JSON.parse(taskResponse.data.task.result);
          if (resultData.collaboration_id) {
            // Create a basic conversation structure from parsed result
            setConversation({
              task_id: taskId,
              task_description: taskResponse.data.task.title,
              collaboration_id: resultData.collaboration_id,
              status: 'completed',
              participants: resultData.participants?.map(p => p.agent_id) || [],
              agent_roles: {},
              messages: [{
                role: 'system',
                content: 'Task completed successfully, but detailed conversation data is not available.',
                sender_address: 'system',
                agent_name: 'System',
                timestamp: resultData.completed_at
              }],
              result: {
                success: true,
                final_result: 'Task completed successfully',
                conversation_summary: 'Task completed but conversation details are not available',
                completed_at: resultData.completed_at
              }
            });
            return;
          }
        } catch (parseError) {
          console.log('Failed to parse task result JSON:', parseError);
        }
      }
      
      // If task is not completed or no result, show empty state
      setConversation(null);
      
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
        // Navigate to the newly created conversation
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
          No Task Results Available
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          This task hasn't been completed yet.
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
            Task Results
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
                  <Box key={message.id || index} sx={{ mb: 2 }}>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar 
                            sx={{ 
                              width: 32, 
                              height: 32, 
                              mr: 1.5,
                              bgcolor: isSystemMessage ? '#9e9e9e' : generateAvatarColor(message.sender_address || message.sender)
                            }}
                          >
                            {isSystemMessage ? <ScheduleIcon fontSize="small" /> : (message.sender_address || message.sender).substring(2, 4)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2">
                              {isSystemMessage 
                                ? 'System' 
                                : message.agent_name || agentRole?.agent_name || `Agent ${message.message_index + 1}`
                              }
                            </Typography>
                            {!isSystemMessage && (
                              <Typography variant="caption" color="textSecondary">
                                {formatAddress(message.sender_address || message.sender)}
                              </Typography>
                            )}
                          </Box>
                          {(message.round || message.round_number) && (
                            <Chip 
                              label={`Round ${message.round || message.round_number}`}
                              size="small"
                              sx={{ ml: 2 }}
                              color="primary"
                              variant="outlined"
                            />
                          )}
                          {message.agent_capabilities && message.agent_capabilities.length > 0 && (
                            <Box sx={{ ml: 2, display: 'flex', gap: 0.5 }}>
                              {message.agent_capabilities.slice(0, 2).map((capability, idx) => (
                                <Chip 
                                  key={idx}
                                  label={capability}
                                  size="small"
                                  variant="outlined"
                                  color="secondary"
                                />
                              ))}
                              {message.agent_capabilities.length > 2 && (
                                <Chip 
                                  label={`+${message.agent_capabilities.length - 2}`}
                                  size="small"
                                  variant="outlined"
                                  color="secondary"
                                />
                              )}
                            </Box>
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
      {(conversation.result || conversation.final_result) && (
        <Card>
          <CardHeader 
            title="Distributed Collaboration Result"
            avatar={<CheckCircleIcon color="success" />}
          />
          <CardContent>
            {/* Agent Collaboration Summary */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI Agent Collaboration Summary
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                This task was completed through distributed AI agent collaboration using real GPT API calls.
                Each agent contributed based on their unique capabilities.
              </Alert>
            </Box>

            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">📋 Quick Summary</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {(conversation.result?.conversation_summary || conversation.final_result?.conversation_summary) || 
                   'Multiple AI agents collaborated to analyze and solve this task using their specialized capabilities.'}
                </Typography>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">🔍 Detailed Analysis & Solution</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {(conversation.result?.final_result || conversation.final_result?.final_result) || 
                   'Check the conversation messages above to see the detailed collaboration between agents.'}
                </Typography>
              </AccordionDetails>
            </Accordion>

            {/* Collaboration Statistics */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                📊 Collaboration Statistics
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Participants: {conversation.participants?.length || 'N/A'} agents
                  </Typography>
                  <br />
                  <Typography variant="caption" color="textSecondary">
                    Total Messages: {conversation.result?.message_count || conversation.messages?.length || 'N/A'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Completed: {formatTimestamp(conversation.result?.completed_at || conversation.final_result?.completed_at || conversation.result?.created_at)}
                  </Typography>
                  <br />
                  <Typography variant="caption" color="textSecondary">
                    Collaboration Rounds: {Math.max(...(conversation.messages?.map(m => m.round || m.round_number || 0).filter(r => r > 0) || [0]))} rounds
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label="Distributed AI Collaboration"
                  color="primary"
                  size="small"
                  icon={<PsychologyIcon />}
                />
                <Chip 
                  label={conversation.result?.success !== false ? 'Success' : 'Failed'}
                  color={conversation.result?.success !== false ? 'success' : 'error'}
                  size="small"
                />
              </Box>
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