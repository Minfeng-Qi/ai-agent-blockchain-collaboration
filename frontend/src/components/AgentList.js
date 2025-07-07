import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  Avatar, 
  Chip, 
  CircularProgress,
  TextField,
  InputAdornment,
  IconButton,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Psychology as PsychologyIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { agentApi } from '../services/api';

const AgentCard = ({ agent }) => {
  const navigate = useNavigate();
  
  // Generate avatar color based on agent address
  const getAvatarColor = (address) => {
    const colors = [
      '#3f51b5', '#f44336', '#009688', '#ff9800', '#9c27b0',
      '#2196f3', '#4caf50', '#ff5722', '#607d8b', '#e91e63'
    ];
    const index = parseInt(address.slice(2, 4), 16) % colors.length;
    return colors[index];
  };
  
  // Format agent ID or address for display
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };
  
  // Get agent initials from ID
  const getInitials = (agentId) => {
    return agentId ? agentId.slice(2, 4).toUpperCase() : 'AG';
  };
  
  // Extract capabilities from agent data
  const getCapabilities = () => {
    if (agent.capabilities && Array.isArray(agent.capabilities)) {
      // If capabilities is an array of strings
      return agent.capabilities.reduce((obj, cap) => {
        obj[cap] = 1;
        return obj;
      }, {});
    } else if (agent.capabilities && typeof agent.capabilities === 'object') {
      // If capabilities is already an object
      return agent.capabilities;
    } else if (agent.capabilities && Array.isArray(agent.capabilities)) {
      // If capabilities is an array of objects with name and score
      return agent.capabilities.reduce((obj, cap) => {
        obj[cap.name] = cap.score;
        return obj;
      }, {});
    }
    return {};
  };
  
  const capabilities = getCapabilities();
  const agentId = agent.agent_id || agent.address;
  
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar 
            sx={{ 
              bgcolor: getAvatarColor(agentId),
              mr: 1
            }}
          >
            {getInitials(agentId)}
          </Avatar>
          <Typography variant="h6" component="div">
            Agent {formatAddress(agentId)}
          </Typography>
        </Box>
        
        <Typography variant="body2" color="textSecondary" gutterBottom noWrap>
          {agentId}
        </Typography>
        
        <Divider sx={{ my: 1 }} />
        
        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="caption" color="textSecondary">
              Reputation
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {agent.reputation || 0}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="textSecondary">
              Tasks
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {agent.tasks_completed || agent.tasksCompleted || 0}
            </Typography>
          </Grid>
        </Grid>
        
        <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
          Top Capabilities
        </Typography>
        
        <Box>
          {Object.entries(capabilities)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([capability, value]) => (
              <Chip 
                key={capability}
                label={typeof value === 'number' ? `${capability}: ${value}` : capability}
                size="small"
                sx={{ mr: 0.5, mb: 0.5 }}
              />
            ))
          }
        </Box>
      </CardContent>
      <CardActions>
        <Button 
          size="small" 
          startIcon={<PsychologyIcon />}
          onClick={() => navigate(`/learning?agent=${agentId}`)}
        >
          Learning
        </Button>
        <Button 
          size="small" 
          startIcon={<AssignmentIcon />}
          onClick={() => navigate(`/tasks?agent=${agentId}`)}
        >
          Tasks
        </Button>
        <Box sx={{ flexGrow: 1 }} />
        <Button 
          size="small" 
          variant="contained"
          onClick={() => navigate(`/agents/${agentId}`)}
        >
          Details
        </Button>
      </CardActions>
    </Card>
  );
};

const AgentList = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  
  useEffect(() => {
    fetchAgents();
  }, []);
  
  const fetchAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentApi.getAgents();
      if (data && data.agents) {
        setAgents(data.agents);
      } else {
        // 处理意外的响应格式
        setAgents([]);
        setError('Unexpected response format from API');
        setSnackbarOpen(true);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
      setError('Failed to fetch agents. Using sample data instead.');
      setSnackbarOpen(true);
      
      // 使用示例数据作为后备
      setAgents([
        {
          agent_id: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          reputation: 85,
          tasks_completed: 42,
          capabilities: ['analysis', 'generation', 'classification']
        },
        {
          agent_id: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          reputation: 75,
          tasks_completed: 28,
          capabilities: ['generation', 'translation', 'summarization']
        },
        {
          agent_id: '0x90F79bf6EB2c4f870365E785982E1f101E93b906',
          reputation: 80,
          tasks_completed: 35,
          capabilities: ['classification', 'analysis']
        }
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  const filteredAgents = agents.filter(agent => {
    const agentId = agent.agent_id || agent.address || '';
    return agentId.toLowerCase().includes(searchTerm.toLowerCase());
  });
  
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
        <Typography variant="h4">
          Agents
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => navigate('/agents/new')}
          >
            Register Agent
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<RefreshIcon />}
            onClick={fetchAgents}
          >
            Refresh
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search agents by address"
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            )
          }}
          variant="outlined"
        />
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
          <CircularProgress />
        </Box>
      ) : (
        filteredAgents.length > 0 ? (
          <Grid container spacing={3}>
            {filteredAgents.map((agent) => (
              <Grid item key={agent.agent_id || agent.address} xs={12} sm={6} md={4} lg={3}>
                <AgentCard agent={agent} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 5 }}>
            <Typography variant="h6" color="textSecondary">
              No agents found
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {searchTerm ? 'Try a different search term' : 'Register a new agent to get started'}
            </Typography>
          </Box>
        )
      )}
    </Box>
  );
};

export default AgentList;