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
  OpenInNew as ExternalLinkIcon,
  Star as EvaluateIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { taskApi } from '../services/api';

const TaskHistory = ({ taskId, refreshTrigger }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (taskId) {
      fetchTaskHistory();
    }
  }, [taskId, refreshTrigger]);

  const fetchTaskHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskApi.getTaskHistory(taskId);
      
      if (response.success && response.data) {
        const historyData = response.data.data || response.data;
        setHistory(historyData.history || []);
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
    const iconProps = { 
      sx: { 
        fontSize: 20,
        color: 'inherit'
      } 
    };
    
    switch (eventType) {
      case 'task_created':
      case 'created':
        return <TaskIcon {...iconProps} />;
      case 'collaboration_started':
        return <GroupIcon {...iconProps} />;
      case 'task_assigned':
      case 'assigned':
        return <PersonIcon {...iconProps} />;
      case 'task_completed':
      case 'completed':
        return <CompleteIcon {...iconProps} />;
      case 'evaluated':
        return <EvaluateIcon {...iconProps} />;
      case 'bid_placed':
        return <TimeIcon {...iconProps} />;
      default:
        return <TimeIcon {...iconProps} />;
    }
  };

  const getTimelineDotColor = (eventType) => {
    switch (eventType) {
      case 'task_created':
      case 'created':
        return 'primary';
      case 'collaboration_started':
        return 'secondary';
      case 'task_assigned':
      case 'assigned':
        return 'info';
      case 'task_completed':
      case 'completed':
        return 'success';
      case 'evaluated':
        return 'warning';
      case 'bid_placed':
        return 'info';
      default:
        return 'grey';
    }
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getEventTitle = (eventType) => {
    const eventTitles = {
      'task_created': 'Task Created',
      'created': 'Task Created',
      'collaboration_started': 'Collaboration Started',
      'task_assigned': 'Task Assigned',
      'assigned': 'Task Assigned',
      'task_completed': 'Task Completed',
      'completed': 'Task Completed',
      'evaluated': 'Task Evaluated',
      'bid_placed': 'Bid Placed'
    };
    
    return eventTitles[eventType] || (eventType ? eventType.charAt(0).toUpperCase() + eventType.slice(1) : 'Unknown Event');
  };

  const formatTimestamp = (timestamp) => {
    try {
      // 保持区块号格式
      if (typeof timestamp === 'string' && timestamp.includes('Block #')) {
        return timestamp;
      }
      // 如果是纯数字，转换为区块号格式
      if (typeof timestamp === 'number') {
        return `Block #${timestamp}`;
      }
      // 如果是时间戳但我们想显示为区块号，尝试从blockchain_data获取
      return timestamp || 'Unknown time';
    } catch (e) {
      return timestamp || 'Unknown time';
    }
  };

  const renderEventDetails = (event) => {
    const details = event.details || {};
    
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
              
              <Typography variant="body2" color="text.secondary">
                Actor: {formatAddress(event.actor)}
              </Typography>
              
              {event.event === 'evaluated' && event.evaluation_data && (
                <>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    <strong>Evaluation Details:</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Evaluator: {event.evaluation_data.evaluator}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Rating: {event.evaluation_data.rating}/5
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agent: {formatAddress(event.evaluation_data.agent_id)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reward: {event.evaluation_data.reward} ETH
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reputation Change: {event.evaluation_data.reputation_change > 0 ? '+' : ''}{event.evaluation_data.reputation_change}
                  </Typography>
                </>
              )}
              
              {event.event !== 'evaluated' && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Details: {typeof event.details === 'string' ? event.details : 'Standard event'}
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
        
        <Timeline sx={{ 
          padding: 0,
          margin: 0,
          '& .MuiTimelineItem-root': {
            '&:before': {
              content: 'none', // 移除Timeline默认的左侧间距
            },
            minHeight: 80,
            alignItems: 'flex-start',
          },
          '& .MuiTimelineSeparator-root': {
            flex: '0 0 auto',
            paddingTop: 0,
            paddingBottom: 0,
          },
          '& .MuiTimelineConnector-root': {
            width: 3,
            backgroundColor: 'grey.300',
          },
          '& .MuiTimelineContent-root': {
            paddingTop: 0,
            paddingBottom: 0,
          },
        }}>
          {history.map((event, index) => (
            <TimelineItem key={index} sx={{ alignItems: 'flex-start' }}>
              <TimelineSeparator>
                <TimelineDot 
                  color={getTimelineDotColor(event.event)}
                  sx={{ 
                    width: 48, 
                    height: 48,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '8px 0',
                    position: 'relative',
                    boxShadow: 2,
                  }}
                >
                  {getTimelineIcon(event.event)}
                </TimelineDot>
                {index < history.length - 1 && <TimelineConnector />}
              </TimelineSeparator>
              
              <TimelineContent sx={{ py: '20px', px: 2, mt: 0 }}>
                <Box sx={{ mb: 2 }}>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Typography variant="subtitle1" component="span" sx={{ fontWeight: 600 }}>
                      {getEventTitle(event.event)}
                    </Typography>
                    <Chip 
                      label={formatTimestamp(event.timestamp)} 
                      size="small" 
                      variant="outlined"
                      color={event.event === 'evaluated' ? 'warning' : 'primary'}
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {event.details || 'No details available'}
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