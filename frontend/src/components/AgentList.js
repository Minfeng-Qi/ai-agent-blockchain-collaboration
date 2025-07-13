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
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Psychology as PsychologyIcon,
  Assignment as AssignmentIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { agentApi } from '../services/api';
import { enhancedMockData } from '../services/enhancedMockData';

const AgentCard = ({ agent, onDelete, onStatusToggle }) => {
  const navigate = useNavigate();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  
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
    if (agent.capabilities && Array.isArray(agent.capabilities) && agent.capabilities.length > 0) {
      // If capabilities is an array of strings with weights
      const capabilityObj = {};
      agent.capabilities.forEach((cap, index) => {
        const weight = agent.capability_weights && agent.capability_weights[index] ? agent.capability_weights[index] : 50;
        capabilityObj[cap] = weight;
      });
      return capabilityObj;
    } else if (agent.capabilities && typeof agent.capabilities === 'object') {
      // If capabilities is already an object
      return agent.capabilities;
    }
    // 如果没有能力数据，返回默认显示
    return {};
  };
  
  const capabilities = getCapabilities();
  const agentId = agent.agent_id || agent.address;
  
  // Debug logging
  console.log('Agent data:', {
    name: agent.name,
    reputation: agent.reputation,
    tasks: agent.tasks_completed || agent.tasksCompleted || agent.workload,
    capabilities: agent.capabilities,
    capability_weights: agent.capability_weights,
    calculated_capabilities: capabilities
  });
  
  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };
  
  const handleDeleteConfirm = async () => {
    setDeleting(true);
    try {
      await agentApi.deleteAgent(agentId);
      setDeleteDialogOpen(false);
      onDelete && onDelete(agentId);
    } catch (error) {
      console.error('Error deleting agent:', error);
      // 这里可以添加错误提示
    } finally {
      setDeleting(false);
    }
  };
  
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };
  
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
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div">
              {agent.name || `Agent ${formatAddress(agentId)}`}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                size="small" 
                label={agent.active !== false ? 'Active' : 'Inactive'}
                color={agent.active !== false ? 'success' : 'default'}
                variant="outlined"
                clickable
                onClick={() => onStatusToggle && onStatusToggle(agentId, !agent.active)}
              />
              {agent.source === 'blockchain' && (
                <Chip 
                  size="small" 
                  label="On-Chain"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        </Box>
        
        <Typography variant="body2" color="textSecondary" gutterBottom noWrap>
          {agentId}
        </Typography>
        
        <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
          Type: {agent.agentType === 1 ? 'LLM' : agent.agentType === 2 ? 'Orchestrator' : agent.agentType === 3 ? 'Evaluator' : 'Unknown'}
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
              {agent.tasks_completed || agent.tasksCompleted || agent.workload || 0}
            </Typography>
          </Grid>
        </Grid>
        
        <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
          Top Capabilities
        </Typography>
        
        <Box>
          {Object.keys(capabilities).length > 0 ? (
            <>
              {Object.entries(capabilities)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3)
                .map(([capability, value]) => (
                  <Chip 
                    key={capability}
                    label={typeof value === 'number' ? `${capability}: ${value}` : capability}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                    color={value >= 80 ? 'success' : value >= 60 ? 'primary' : 'default'}
                  />
                ))
              }
              {Object.keys(capabilities).length > 3 && (
                <Chip 
                  label={`+${Object.keys(capabilities).length - 3} more`}
                  size="small"
                  variant="outlined"
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              )}
            </>
          ) : (
            <Typography variant="body2" color="textSecondary" fontStyle="italic">
              No capabilities configured
            </Typography>
          )}
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
        <IconButton 
          size="small" 
          color="error"
          onClick={handleDeleteClick}
          disabled={deleting}
          title="Delete Agent"
        >
          <DeleteIcon />
        </IconButton>
        <Button 
          size="small" 
          variant="contained"
          onClick={() => navigate(`/agents/${agentId}`)}
        >
          Details
        </Button>
      </CardActions>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Agent
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete agent "{agent.name || `Agent ${agentId?.slice(-4)}`}"? 
            This action will deactivate the agent on the blockchain and cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleting}>
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
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
  const [snackbarSeverity, setSnackbarSeverity] = useState('warning');
  const [dataSource, setDataSource] = useState('blockchain');
  
  useEffect(() => {
    fetchAgents();
  }, []);
  
  const fetchAgents = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching agents from API...', forceRefresh ? '(force refresh)' : '');
      const data = await agentApi.getAgents();
      console.log('API response:', data);
      
      if (data && data.agents) {
        setAgents(data.agents);
        setDataSource(data.source || 'blockchain');
        console.log(`Successfully loaded ${data.agents.length} agents from ${data.source}`);
      } else {
        // 处理意外的响应格式
        setAgents([]);
        setDataSource('unknown');
        setError('Unexpected response format from API');
        setSnackbarSeverity('warning');
        setSnackbarOpen(true);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
      
      // 使用 mock data fallback
      try {
        console.log('Backend offline, using mock data for agents...');
        const mockData = enhancedMockData.generateEnhancedAgents(12);
        setAgents(mockData.agents);
        setDataSource('mock');
        setError('Backend offline - showing mock data');
        setSnackbarSeverity('warning');
        setSnackbarOpen(true);
        console.log(`Successfully loaded ${mockData.agents.length} mock agents`);
      } catch (mockError) {
        console.error('Error generating mock agents:', mockError);
        setError('Failed to fetch agents and mock data unavailable.');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
        setAgents([]);
        setDataSource('error');
      }
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
  
  const handleAgentDelete = (agentId) => {
    // Remove the deleted agent from the local state immediately
    setAgents(prevAgents => prevAgents.filter(agent => 
      (agent.agent_id || agent.address) !== agentId
    ));
    
    // Show success message
    setError(`Agent ${agentId.slice(-4)} has been successfully deactivated`);
    setSnackbarSeverity('success');
    setSnackbarOpen(true);
    
    // Don't refresh automatically - the UI should reflect the immediate change
  };

  const handleStatusToggle = async (agentId, newStatus) => {
    try {
      if (newStatus) {
        await agentApi.activateAgent(agentId);
      } else {
        await agentApi.deactivateAgent(agentId);
      }
      
      // Update the local state immediately
      setAgents(prevAgents => prevAgents.map(agent => 
        (agent.agent_id || agent.address) === agentId 
          ? { ...agent, active: newStatus }
          : agent
      ));
      
      // Show success message
      setError(`Agent ${agentId.slice(-4)} has been ${newStatus ? 'activated' : 'deactivated'}`);
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
      
    } catch (error) {
      console.error('Error toggling agent status:', error);
      setError(`Failed to ${newStatus ? 'activate' : 'deactivate'} agent ${agentId.slice(-4)}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
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
        <Alert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4">
            Agents
          </Typography>
          <Chip 
            label={
              dataSource === 'blockchain' ? 'Blockchain Data' : 
              dataSource === 'mock' ? 'Mock Data' : 
              'Local Data'
            }
            color={
              dataSource === 'blockchain' ? 'success' : 
              dataSource === 'mock' ? 'warning' : 
              'default'
            }
            size="small"
            variant="outlined"
          />
        </Box>
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
            onClick={() => fetchAgents(true)}
            disabled={loading}
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
                <AgentCard agent={agent} onDelete={handleAgentDelete} onStatusToggle={handleStatusToggle} />
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