import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  TextField,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  FormHelperText,
  CircularProgress,
  IconButton,
  Divider,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { taskApi } from '../services/api';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const availableRequirements = [
  'analysis',
  'generation',
  'classification',
  'translation',
  'summarization',
  'research',
  'data visualization',
  'coding',
  'editing',
  'review'
];

const EditTask = () => {
  const navigate = useNavigate();
  const { taskId } = useParams();
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    reward: '',
    required_capabilities: [],
    deadline: '',
    min_reputation: 0,
    tags: []
  });
  
  const [errors, setErrors] = useState({});
  const [newTag, setNewTag] = useState('');
  
  // 格式化时间戳为datetime-local格式
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
      // Format for datetime-local input: YYYY-MM-DDTHH:mm
      return date.toISOString().slice(0, 16);
    } catch (e) {
      return '';
    }
  };

  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);

  const fetchTaskDetails = async () => {
    setInitialLoading(true);
    try {
      const response = await taskApi.getTaskById(taskId);
      if (response && response.task) {
        const task = response.task;
        setFormData({
          title: task.title || '',
          description: task.description || '',
          reward: task.reward || '',
          required_capabilities: task.required_capabilities || [],
          deadline: formatTimestamp(task.deadline),
          min_reputation: task.min_reputation || 0,
          tags: task.tags || []
        });
      }
    } catch (error) {
      console.error('Error fetching task details:', error);
      setSnackbar({
        open: true,
        message: 'Failed to fetch task details',
        severity: 'error'
      });
    } finally {
      setInitialLoading(false);
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };
  
  const handleRequirementsChange = (event) => {
    const {
      target: { value },
    } = event;
    
    setFormData({
      ...formData,
      required_capabilities: typeof value === 'string' ? value.split(',') : value,
    });
    
    // Clear error when field is edited
    if (errors.required_capabilities) {
      setErrors({
        ...errors,
        required_capabilities: null
      });
    }
  };
  
  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, newTag.trim()]
      });
      setNewTag('');
    }
  };
  
  const handleDeleteTag = (tagToDelete) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToDelete)
    });
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!formData.reward) {
      newErrors.reward = 'Reward is required';
    } else if (isNaN(formData.reward) || parseFloat(formData.reward) <= 0) {
      newErrors.reward = 'Reward must be a positive number';
    }
    
    if (formData.required_capabilities.length === 0) {
      newErrors.required_capabilities = 'At least one capability is required';
    }
    
    if (!formData.deadline) {
      newErrors.deadline = 'Deadline is required';
    } else {
      const deadlineDate = new Date(formData.deadline);
      const now = new Date();
      if (deadlineDate <= now) {
        newErrors.deadline = 'Deadline must be in the future';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Convert deadline to Unix timestamp
      const deadlineDate = new Date(formData.deadline);
      const deadlineTimestamp = Math.floor(deadlineDate.getTime() / 1000);
      
      const taskData = {
        title: formData.title,
        description: formData.description,
        required_capabilities: formData.required_capabilities,
        reward: parseFloat(formData.reward),
        deadline: deadlineTimestamp,
        min_reputation: formData.min_reputation || 0,
        tags: formData.tags
      };
      
      console.log('Updating task:', taskId, 'with data:', taskData);
      const result = await taskApi.updateTask(taskId, taskData);
      console.log('Update result:', result);
      
      setSnackbar({
        open: true,
        message: 'Task updated successfully!',
        severity: 'success'
      });
      
      // Navigate after a short delay to show the success message
      setTimeout(() => {
        navigate(`/tasks/${taskId}`);
      }, 1500);
      
    } catch (error) {
      console.error('Error updating task:', error);
      
      // Extract more detailed error information
      let errorMessage = 'Failed to update task. Please try again.';
      if (error.response) {
        // Server responded with error status
        errorMessage = `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.data?.message || error.response.statusText}`;
        console.error('Server response:', error.response.data);
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Network error: Unable to connect to server. Please check if the backend is running.';
        console.error('Request error:', error.request);
      } else {
        // Something else happened
        errorMessage = `Request error: ${error.message}`;
      }
      
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      
      setLoading(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  if (initialLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate(`/tasks/${taskId}`)} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4">
          Edit Task
        </Typography>
      </Box>
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                error={!!errors.title}
                helperText={errors.title}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                error={!!errors.description}
                helperText={errors.description}
                multiline
                rows={4}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Reward (tokens)"
                name="reward"
                type="number"
                value={formData.reward}
                onChange={handleChange}
                error={!!errors.reward}
                helperText={errors.reward}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Deadline"
                name="deadline"
                type="datetime-local"
                value={formData.deadline}
                onChange={handleChange}
                error={!!errors.deadline}
                helperText={errors.deadline}
                InputLabelProps={{
                  shrink: true,
                }}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth error={!!errors.required_capabilities}>
                <InputLabel id="capabilities-label">Required Capabilities</InputLabel>
                <Select
                  labelId="capabilities-label"
                  multiple
                  value={formData.required_capabilities}
                  onChange={handleRequirementsChange}
                  input={<OutlinedInput label="Required Capabilities" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                  MenuProps={MenuProps}
                >
                  {availableRequirements.map((requirement) => (
                    <MenuItem
                      key={requirement}
                      value={requirement}
                    >
                      {requirement}
                    </MenuItem>
                  ))}
                </Select>
                {errors.required_capabilities && (
                  <FormHelperText>{errors.required_capabilities}</FormHelperText>
                )}
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Minimum Reputation"
                name="min_reputation"
                type="number"
                value={formData.min_reputation}
                onChange={handleChange}
                helperText="Minimum reputation required for agents to work on this task"
                inputProps={{ min: 0 }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Tags
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextField
                  label="Add Tag"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  sx={{ flexGrow: 1, mr: 1 }}
                />
                <Button 
                  variant="outlined"
                  onClick={handleAddTag}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    onDelete={() => handleDeleteTag(tag)}
                    deleteIcon={<CloseIcon />}
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button 
                  variant="outlined"
                  onClick={() => navigate(`/tasks/${taskId}`)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                >
                  {loading ? 'Updating...' : 'Update Task'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={8000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EditTask;