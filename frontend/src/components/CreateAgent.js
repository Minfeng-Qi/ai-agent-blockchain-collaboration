import React, { useState } from 'react';
import {
  Box, Typography, Button, TextField, Grid, Paper, FormControl, InputLabel, Select, MenuItem, Chip, OutlinedInput, Snackbar, Alert, CircularProgress, Slider, FormHelperText
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { agentApi } from '../services/api';

// 使用与AgentDetails相同的标准capabilities列表
const availableCapabilities = [
  'data_analysis',
  'text_generation', 
  'classification',
  'translation',
  'summarization',
  'image_recognition',
  'sentiment_analysis',
  'code_generation'
];

const agentTypes = [
  { value: 0, label: 'Undefined' },
  { value: 1, label: 'LLM' },
  { value: 2, label: 'Orchestrator' },
  { value: 3, label: 'Evaluator' }
];

const CreateAgent = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    capabilities: [],
    capabilityWeights: {},
    reputation: 50,
    confidence_factor: 80,
    agentType: 1
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: null });
  };

  const handleCapabilitiesChange = (event) => {
    const { value } = event.target;
    const capabilities = typeof value === 'string' ? value.split(',') : value;
    
    // Initialize weights for new capabilities
    const newWeights = { ...formData.capabilityWeights };
    capabilities.forEach(cap => {
      if (!newWeights[cap]) {
        newWeights[cap] = 70; // Default weight
      }
    });
    
    // Remove weights for removed capabilities
    Object.keys(newWeights).forEach(cap => {
      if (!capabilities.includes(cap)) {
        delete newWeights[cap];
      }
    });
    
    setFormData({ 
      ...formData, 
      capabilities,
      capabilityWeights: newWeights
    });
    if (errors.capabilities) setErrors({ ...errors, capabilities: null });
  };

  const handleCapabilityWeightChange = (capability, weight) => {
    const newWeights = { ...formData.capabilityWeights };
    newWeights[capability] = Math.max(0, Math.min(100, parseInt(weight) || 0));
    setFormData({ ...formData, capabilityWeights: newWeights });
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.capabilities.length) newErrors.capabilities = 'At least one capability is required';
    if (formData.reputation < 0 || formData.reputation > 100) newErrors.reputation = 'Reputation must be between 0-100';
    if (formData.confidence_factor < 0 || formData.confidence_factor > 100) newErrors.confidence_factor = 'Confidence factor must be between 0-100';
    
    // Validate capability weights
    for (const cap of formData.capabilities) {
      const weight = formData.capabilityWeights[cap];
      if (!weight || weight < 1 || weight > 100) {
        newErrors.capabilityWeights = 'All capability weights must be between 1-100';
        break;
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    try {
      // Prepare capability tags and weights for smart contract
      const capabilityTags = formData.capabilities;
      const capabilityWeights = capabilityTags.map(cap => formData.capabilityWeights[cap]);
      
      const agentData = {
        name: formData.name,
        agent_type: formData.agentType,
        capabilities: capabilityTags,
        capabilityWeights: capabilityWeights,
        reputation: Number(formData.reputation),
        confidence_factor: Number(formData.confidence_factor)
      };
      
      console.log('Registering agent with data:', agentData);
      const response = await agentApi.createAgent(agentData);
      console.log('Registration response:', response);
      
      if (response.success && response.source === 'blockchain') {
        const message = response.action === 'reactivated' 
          ? `Agent reactivated successfully on blockchain! TX: ${response.transaction_hash.substring(0, 10)}...`
          : `Agent registered successfully on blockchain! TX: ${response.transaction_hash.substring(0, 10)}...`;
        
        setSnackbar({ 
          open: true, 
          message: message, 
          severity: 'success' 
        });
        setTimeout(() => navigate('/agents'), 2000);
      } else if (response.success && response.source === 'mock') {
        setSnackbar({ 
          open: true, 
          message: 'Agent registered (fallback mode). Blockchain may be unavailable.', 
          severity: 'warning' 
        });
        setTimeout(() => navigate('/agents'), 2000);
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error) {
      console.error('Error registering agent:', error);
      let errorMessage = 'Failed to register agent. ';
      if (error.message && error.message.includes('Agent already registered')) {
        errorMessage += 'This agent address is already registered.';
      } else if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else {
        errorMessage += 'Please try again.';
      }
      setSnackbar({ open: true, message: errorMessage, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => setSnackbar({ ...snackbar, open: false });

  return (
    <Box maxWidth={600} mx="auto" mt={4}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" mb={3}>Register New Agent</Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                fullWidth
                required
                error={!!errors.name}
                helperText={errors.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Agent Type</InputLabel>
                <Select
                  name="agentType"
                  value={formData.agentType}
                  onChange={handleChange}
                  label="Agent Type"
                >
                  {agentTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth required error={!!errors.capabilities}>
                <InputLabel>Capabilities</InputLabel>
                <Select
                  multiple
                  name="capabilities"
                  value={formData.capabilities}
                  onChange={handleCapabilitiesChange}
                  input={<OutlinedInput label="Capabilities" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={`${value} (${formData.capabilityWeights[value] || 0})`} />
                      ))}
                    </Box>
                  )}
                >
                  {availableCapabilities.map((cap) => (
                    <MenuItem key={cap} value={cap}>{cap}</MenuItem>
                  ))}
                </Select>
                {errors.capabilities && <FormHelperText>{errors.capabilities}</FormHelperText>}
                {errors.capabilityWeights && <FormHelperText>{errors.capabilityWeights}</FormHelperText>}
              </FormControl>
            </Grid>
            {formData.capabilities.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Capability Weights (1-100)
                </Typography>
                {formData.capabilities.map((capability) => (
                  <Box key={capability} sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      {capability}: {formData.capabilityWeights[capability] || 70}
                    </Typography>
                    <Slider
                      value={formData.capabilityWeights[capability] || 70}
                      onChange={(e, value) => handleCapabilityWeightChange(capability, value)}
                      min={1}
                      max={100}
                      step={1}
                      marks={[
                        { value: 1, label: '1' },
                        { value: 50, label: '50' },
                        { value: 100, label: '100' }
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                ))}
              </Grid>
            )}
            <Grid item xs={12} sm={6}>
              <TextField
                label="Initial Reputation (0-100)"
                name="reputation"
                value={formData.reputation}
                onChange={handleChange}
                type="number"
                fullWidth
                inputProps={{ min: 0, max: 100 }}
                error={!!errors.reputation}
                helperText={errors.reputation || "Initial reputation score (default: 50)"}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Confidence Factor (0-100)"
                name="confidence_factor"
                value={formData.confidence_factor}
                onChange={handleChange}
                type="number"
                fullWidth
                inputProps={{ min: 0, max: 100 }}
                error={!!errors.confidence_factor}
                helperText={errors.confidence_factor || "Agent's confidence in its capabilities (default: 80)"}
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Register Agent'}
                </Button>
                <Button variant="outlined" onClick={() => navigate('/agents')}>Cancel</Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CreateAgent;
