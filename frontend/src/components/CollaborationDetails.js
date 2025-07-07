import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Container, Typography, Box, Paper, Divider, Chip, 
  CircularProgress, Button, Card, CardContent, 
  List, ListItem, ListItemText, Accordion, AccordionSummary, 
  AccordionDetails, Grid, Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { api, collaborationApi } from '../services/api';
import ReactMarkdown from 'react-markdown';

// Color mapping for message roles
const roleColors = {
  system: "#6c757d",
  user: "#007bff",
  assistant: "#28a745"
};

// Agent message component
const AgentMessage = ({ message }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Detect if message is from a specific agent
  const detectAgent = (content) => {
    // 匹配多种代理格式: Agent1, DataAnalyst, Agent1 (DataAnalyst), 协作总结
    const agentRegex = /^(Agent\d+(?:\s*\([^)]+\))?|[\w\s]+Agent|协作总结|[A-Za-z][A-Za-z0-9]*|[\u4e00-\u9fa5]+):\s*/;
    const match = content.match(agentRegex);
    if (match) {
      return {
        agentName: match[1].trim(),
        content: content.replace(agentRegex, '').trim()
      };
    }
    return null;
  };
  
  const agentInfo = message.role === 'assistant' ? detectAgent(message.content) : null;
  
  return (
    <Box 
      sx={{ 
        mb: 2, 
        p: 2, 
        borderRadius: 2,
        backgroundColor: agentInfo ? '#f0f7ff' : `${roleColors[message.role]}22`,
        borderLeft: `4px solid ${roleColors[message.role]}`
      }}
    >
      {message.role === 'system' && (
        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
          System
        </Typography>
      )}
      
      {message.role === 'user' && (
        <Typography variant="subtitle2" color="primary" gutterBottom>
          User
        </Typography>
      )}
      
      {message.role === 'assistant' && agentInfo && (
        <Typography variant="subtitle2" color="success.main" gutterBottom>
          {agentInfo.agentName}
        </Typography>
      )}
      
      {message.role === 'assistant' && !agentInfo && (
        <Typography variant="subtitle2" color="success.main" gutterBottom>
          Assistant
        </Typography>
      )}
      
      <Box>
        {message.content.length > 300 && !expanded ? (
          <>
            <ReactMarkdown>{message.content.substring(0, 300) + '...'}</ReactMarkdown>
            <Button 
              variant="text" 
              size="small" 
              onClick={() => setExpanded(true)}
            >
              Show More
            </Button>
          </>
        ) : (
          <>
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {expanded && (
              <Button 
                variant="text" 
                size="small" 
                onClick={() => setExpanded(false)}
              >
                Show Less
              </Button>
            )}
          </>
        )}
      </Box>
    </Box>
  );
};

const CollaborationDetails = () => {
  const { collaborationId } = useParams();
  const [collaboration, setCollaboration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchCollaborationDetails = async () => {
      try {
        setLoading(true);
        const data = await collaborationApi.getCollaborationConversation(collaborationId);
        setCollaboration(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching collaboration details:', err);
        setError('Unable to load collaboration details. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchCollaborationDetails();
  }, [collaborationId]);
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        alert('Copied to clipboard');
      })
      .catch(err => {
        console.error('Unable to copy:', err);
      });
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>
      </Container>
    );
  }
  
  if (!collaboration) {
    return (
      <Container maxWidth="lg">
        <Alert severity="info" sx={{ mt: 4 }}>No collaboration data found</Alert>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Agent Collaboration Details
        </Typography>
        
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Task Information
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1">
                <strong>Task ID:</strong> {collaboration.task_id}
              </Typography>
              <Typography variant="subtitle1">
                <strong>Task Title:</strong> {collaboration.task_title}
              </Typography>
              <Typography variant="subtitle1">
                <strong>Collaboration ID:</strong> {collaboration.collaboration_id}
              </Typography>
              {collaboration.api_mode && (
                <Typography variant="subtitle1">
                  <strong>API Mode:</strong> 
                  <Chip 
                    label={collaboration.api_mode === 'real' ? 'Real OpenAI API' : 'Mock Mode'} 
                    size="small" 
                    color={collaboration.api_mode === 'real' ? 'success' : 'default'}
                    sx={{ ml: 1 }}
                  />
                </Typography>
              )}
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1">
                <strong>IPFS CID:</strong> 
                <Chip 
                  label={collaboration.ipfs_cid} 
                  size="small" 
                  icon={<ContentCopyIcon fontSize="small" />}
                  onClick={() => copyToClipboard(collaboration.ipfs_cid)}
                  sx={{ ml: 1, cursor: 'pointer' }}
                />
              </Typography>
              {collaboration.ipfs_url && (
                <Typography variant="subtitle1">
                  <strong>IPFS URL:</strong> 
                  <Link to={collaboration.ipfs_url} target="_blank" rel="noopener noreferrer">
                    {collaboration.ipfs_url}
                  </Link>
                </Typography>
              )}
              {collaboration.tx_hash && (
                <Typography variant="subtitle1">
                  <strong>Blockchain Transaction Hash:</strong> 
                  <Chip 
                    label={collaboration.tx_hash} 
                    size="small" 
                    icon={<ContentCopyIcon fontSize="small" />}
                    onClick={() => copyToClipboard(collaboration.tx_hash)}
                    sx={{ ml: 1, cursor: 'pointer' }}
                  />
                </Typography>
              )}
            </Grid>
          </Grid>
        </Paper>
        
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Automatically Selected Agents
          </Typography>
          
          <Grid container spacing={2}>
            {collaboration.agents && collaboration.agents.map((agent, index) => (
              <Grid item xs={12} sm={6} md={4} key={agent.agent_id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">
                      {agent.name || `Agent${index + 1}`}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      ID: {agent.agent_id}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Specialties:</strong> {agent.capabilities.join(', ')}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Reputation:</strong> {agent.reputation}
                    </Typography>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      component={Link} 
                      to={`/agents/${agent.agent_id}`}
                      sx={{ mt: 1 }}
                    >
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
        
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Collaboration Conversation
          </Typography>
          
          <Divider sx={{ mb: 3 }} />
          
          {collaboration.conversation && collaboration.conversation.map((message, index) => (
            <AgentMessage key={index} message={message} />
          ))}
          
          {(!collaboration.conversation || collaboration.conversation.length === 0) && (
            <Alert severity="info">No conversation records available</Alert>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default CollaborationDetails;