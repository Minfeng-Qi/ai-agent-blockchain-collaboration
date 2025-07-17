import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  CircularProgress,
  Link,
  Grid,
  Paper,
  Divider
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot
} from '@mui/lab';
import {
  ExpandMore as ExpandMoreIcon,
  AccessTime as TimeIcon,
  Assignment as TaskIcon,
  Group as GroupIcon,
  CheckCircle as CompleteIcon,
  OpenInNew as ExternalLinkIcon
} from '@mui/icons-material';
import { taskApi } from '../services/api';

const TaskHistory = ({ taskId }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (taskId) {
      fetchTaskHistory();
    }
  }, [taskId]);

  const fetchTaskHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskApi.getTaskHistory(taskId);
      
      if (response.success && response.data) {
        setHistory(response.data.history || []);
      } else {
        setError(response.error || 'Failed to fetch task history');
      }
    } catch (err) {
      console.error('Error fetching task history:', err);
      setError('Failed to fetch task history');
    } finally {
      setLoading(false);
    }
  };

  const getTimelineIcon = (eventType) => {
    switch (eventType) {
      case 'task_created':
        return <TaskIcon />;
      case 'collaboration_started':
        return <GroupIcon />;
      case 'task_assigned':
        return <TimeIcon />;
      case 'task_completed':
        return <CompleteIcon />;
      default:
        return <TimeIcon />;
    }
  };

  const getTimelineDotColor = (eventType) => {
    switch (eventType) {
      case 'task_created':
        return 'primary';
      case 'collaboration_started':
        return 'secondary';
      case 'task_assigned':
        return 'info';
      case 'task_completed':
        return 'success';
      default:
        return 'grey';
    }
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatTimestamp = (timestamp) => {
    // 由于我们目前使用区块号作为时间戳，这里显示区块号
    return `Block #${timestamp}`;
  };

  const renderEventDetails = (event) => {
    const { details } = event;
    
    return (
      <Box sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Transaction Details
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hash: 
                <Link 
                  href={`https://etherscan.io/tx/${details.transaction_hash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ ml: 1 }}
                >
                  {formatAddress(details.transaction_hash)}
                  <ExternalLinkIcon sx={{ fontSize: 12, ml: 0.5 }} />
                </Link>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Block: #{details.block_number}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gas Used: {details.gas_used?.toLocaleString()}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Event Details
              </Typography>
              
              {event.type === 'task_created' && (
                <>
                  <Typography variant="body2" color="text.secondary">
                    Creator: {formatAddress(details.creator)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Task ID: {formatAddress(details.task_id)}
                  </Typography>
                </>
              )}
              
              {event.type === 'collaboration_started' && (
                <>
                  <Typography variant="body2" color="text.secondary">
                    Collaboration ID: {details.collaboration_id}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agent Count: {details.agent_count}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Selected Agents:
                    </Typography>
                    {details.selected_agents?.map((agent, index) => (
                      <Chip
                        key={index}
                        label={formatAddress(agent)}
                        size="small"
                        sx={{ ml: 0.5, mb: 0.5 }}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </>
              )}
              
              {event.type === 'task_assigned' && (
                <Typography variant="body2" color="text.secondary">
                  Assigned to: {formatAddress(details.agent)}
                </Typography>
              )}
              
              {event.type === 'task_completed' && (
                <Typography variant="body2" color="text.secondary">
                  Result: {details.result}
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading task history...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (history.length === 0) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        No history events found for this task.
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Task History
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Complete timeline of blockchain events for this task
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Timeline>
          {history.map((event, index) => (
            <TimelineItem key={index}>
              <TimelineSeparator>
                <TimelineDot color={getTimelineDotColor(event.type)}>
                  {getTimelineIcon(event.type)}
                </TimelineDot>
                {index < history.length - 1 && <TimelineConnector />}
              </TimelineSeparator>
              
              <TimelineContent>
                <Box sx={{ mb: 2 }}>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Typography variant="h6" component="span">
                      {event.icon}
                    </Typography>
                    <Typography variant="subtitle1" component="span">
                      {event.title}
                    </Typography>
                    <Chip 
                      label={formatTimestamp(event.timestamp)} 
                      size="small" 
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {event.description}
                  </Typography>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="body2">
                        View Details
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      {renderEventDetails(event)}
                    </AccordionDetails>
                  </Accordion>
                </Box>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
        
        <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Total Events: {history.length} | 
            Data Source: Blockchain (Real-time)
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default TaskHistory;