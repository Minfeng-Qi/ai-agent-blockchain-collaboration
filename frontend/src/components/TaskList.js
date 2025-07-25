import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  Chip, 
  CircularProgress,
  TextField,
  InputAdornment,
  IconButton,
  Tabs,
  Tab,
  Menu,
  MenuItem,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Alert,
  Snackbar
} from '@mui/material';
import { 
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { taskApi } from '../services/api';

const TaskStatusChip = ({ status }) => {
  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return { icon: <CheckCircleIcon fontSize="small" />, color: 'success' };
      case 'failed':
        return { icon: <ErrorIcon fontSize="small" />, color: 'error' };
      case 'cancelled':
        return { icon: <ErrorIcon fontSize="small" />, color: 'error' };
      case 'assigned':
        return { icon: <HourglassEmptyIcon fontSize="small" />, color: 'warning' };
      case 'open':
      case 'available':
      default:
        return { icon: <AssignmentIcon fontSize="small" />, color: 'info' };
    }
  };
  
  const { icon, color } = getStatusConfig(status);
  const displayStatus = status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Unknown';
  
  return (
    <Chip 
      icon={icon} 
      label={displayStatus} 
      color={color} 
      size="small" 
      variant="outlined"
    />
  );
};

const TaskList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarSeverity, setSnackbarSeverity] = useState('warning');
  
  // Get agent filter from URL if present
  const queryParams = new URLSearchParams(location.search);
  const agentFilter = queryParams.get('agent');
  
  useEffect(() => {
    fetchTasks();
  }, [agentFilter, tabValue]);

  // Handle navigation state for refreshing after deletion
  useEffect(() => {
    if (location.state?.refreshTasks) {
      console.log('🔄 Refreshing tasks after deletion:', location.state.deletedTaskId);
      fetchTasks();
      
      // Show success message if provided
      if (location.state.successMessage) {
        setError(location.state.successMessage);
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
      }
      
      // Clear the state to prevent multiple refreshes
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Refresh data when page regains focus
  useEffect(() => {
    const handleFocus = () => {
      fetchTasks();
    };
    
    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, []);
  
  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get task list with filters
      const params = {};
      if (tabValue > 0) {
        const statusFilters = ['open', 'assigned', 'completed', 'failed'];
        params.status = statusFilters[tabValue - 1];
      }
      
      // Add cache buster to ensure fresh data
      params.t = Date.now();
      
      console.log('Fetching tasks with params:', params);
      const data = await taskApi.getTasks(params);
      
      // Filter by agent if specified
      let filteredTasks = data.tasks || [];
      if (agentFilter && filteredTasks.length > 0) {
        filteredTasks = filteredTasks.filter(task => 
          task.assigned_agent === agentFilter || task.assigned_to === agentFilter
        );
      }
      
      setTasks(filteredTasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setError('Failed to fetch tasks. Using sample data instead.');
      setSnackbarSeverity('warning');
      setSnackbarOpen(true);
      
      // Use sample data as fallback
      const mockTasks = [
        {
          task_id: '1',
          title: 'Analyze market trends',
          description: 'Analyze market trends for Q3 2023',
          type: 'data_analysis',
          status: 'completed',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          completed_at: new Date(Date.now() - 43200000).toISOString(),
          assigned_agent: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
          required_capabilities: ['data_analysis'],
          reward: 0.5
        },
        {
          task_id: '2',
          title: 'Generate quarterly report',
          description: 'Generate quarterly financial report',
          type: 'text_generation',
          status: 'assigned',
          created_at: new Date(Date.now() - 43200000).toISOString(),
          assigned_agent: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
          required_capabilities: ['text_generation', 'data_analysis'],
          reward: 0.3
        },
        {
          task_id: '3',
          title: 'Classify customer feedback',
          description: 'Classify customer feedback into categories',
          type: 'classification',
          status: 'open',
          created_at: new Date(Date.now() - 21600000).toISOString(),
          required_capabilities: ['classification'],
          reward: 0.15
        }
      ];
      
      // Apply status filter to mock data
      let filteredMockTasks = mockTasks;
      if (tabValue > 0) {
        const statusFilters = ['open', 'assigned', 'completed', 'failed'];
        const statusFilter = statusFilters[tabValue - 1];
        filteredMockTasks = mockTasks.filter(task => task.status === statusFilter);
      }
      
      // Apply agent filter if it exists
      if (agentFilter) {
        filteredMockTasks = filteredMockTasks.filter(task => task.assigned_agent === agentFilter);
      }
      
      setTasks(filteredMockTasks);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    // No need to call fetchTasks() here as it will be triggered by the useEffect
  };
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  // Filter tasks by search term - exclude cancelled/deleted tasks
  const filteredTasks = tasks.filter(task => {
    // First filter out cancelled status tasks
    if (task.status === 'cancelled' || task.status === 'canceled') {
      return false;
    }
    
    const titleMatch = task.title?.toLowerCase().includes(searchTerm.toLowerCase()) || false;
    const descMatch = task.description?.toLowerCase().includes(searchTerm.toLowerCase()) || false;
    const idMatch = task.task_id?.toLowerCase().includes(searchTerm.toLowerCase()) || false;
    
    return titleMatch || descMatch || idMatch;
  });
  
  // Paginate tasks
  const paginatedTasks = filteredTasks.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  // Format date
  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      // If Unix timestamp (number), convert to milliseconds
      const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  // Format Task ID - show only first 8 and last 4 characters
  const formatTaskId = (taskId) => {
    if (!taskId) return 'N/A';
    if (taskId.length <= 12) return taskId;
    return `${taskId.substring(0, 8)}...${taskId.substring(taskId.length - 4)}`;
  };
  
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
        <Typography variant="h4">
          Tasks {agentFilter ? '(Filtered by Agent)' : ''}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => navigate('/tasks/new')}
          >
            Create Task
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<RefreshIcon />}
            onClick={fetchTasks}
          >
            Refresh
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search tasks by title, description or ID"
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={handleMenuOpen}>
                  <FilterListIcon />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleMenuClose}>
                    <Typography variant="body2">Sort by Date (Newest)</Typography>
                  </MenuItem>
                  <MenuItem onClick={handleMenuClose}>
                    <Typography variant="body2">Sort by Date (Oldest)</Typography>
                  </MenuItem>
                  <MenuItem onClick={handleMenuClose}>
                    <Typography variant="body2">Sort by Reward (Highest)</Typography>
                  </MenuItem>
                  <MenuItem onClick={handleMenuClose}>
                    <Typography variant="body2">Sort by Reward (Lowest)</Typography>
                  </MenuItem>
                </Menu>
              </InputAdornment>
            )
          }}
          variant="outlined"
        />
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="All" />
          <Tab label="Open" />
          <Tab label="Assigned" />
          <Tab label="Completed" />
          <Tab label="Failed" />
        </Tabs>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
          <CircularProgress />
        </Box>
      ) : (
        filteredTasks.length > 0 ? (
          <Paper variant="outlined">
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Task ID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Required Capabilities</TableCell>
                    <TableCell>Reward</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paginatedTasks.map((task) => (
                    <TableRow 
                      key={task.task_id}
                      hover
                      onClick={() => navigate(`/tasks/${task.task_id}`)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell title={task.task_id}>{formatTaskId(task.task_id)}</TableCell>
                      <TableCell>{task.title || task.description}</TableCell>
                      <TableCell>
                        <TaskStatusChip status={task.status} />
                      </TableCell>
                      <TableCell>
                        {task.required_capabilities && task.required_capabilities.map((req) => (
                          <Chip 
                            key={req} 
                            label={req} 
                            size="small" 
                            sx={{ mr: 0.5, mb: 0.5 }} 
                          />
                        ))}
                      </TableCell>
                      <TableCell>{task.reward}</TableCell>
                      <TableCell>
                        {formatDate(task.created_at)}
                      </TableCell>
                      <TableCell>
                        {task.status === 'completed' ? (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/tasks/${task.task_id}/conversations`);
                            }}
                            sx={{ mr: 1 }}
                          >
                            View Result
                          </Button>
                        ) : task.status === 'open' ? (
                          <Button
                            size="small"
                            variant="contained"
                            onClick={async (e) => {
                              e.stopPropagation();
                              try {
                                // Smart assign the task (will trigger automatic collaboration)
                                const response = await taskApi.smartAssignTask(task.task_id, true, 3);
                                if (response.success) {
                                  // Show success message and navigate to task details
                                  navigate(`/tasks/${task.task_id}`);
                                }
                              } catch (error) {
                                console.error('Error assigning task:', error);
                              }
                            }}
                            sx={{ mr: 1 }}
                          >
                            Assign & Start
                          </Button>
                        ) : (
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/tasks/${task.task_id}`);
                            }}
                          >
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={filteredTasks.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </Paper>
        ) : (
          <Box sx={{ textAlign: 'center', py: 5 }}>
            <Typography variant="h6" color="textSecondary">
              No tasks found
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {searchTerm ? 'Try a different search term' : 'Create a new task to get started'}
            </Typography>
          </Box>
        )
      )}
    </Box>
  );
};

export default TaskList;