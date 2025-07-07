import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  Button,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Tooltip
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
  Refresh as RefreshIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  Insights as InsightsIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { learningApi } from '../services/api';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// 格式化地址，只显示前6位和后4位
const formatAddress = (address) => {
  if (!address) return '';
  return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
};

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  if (typeof timestamp === 'string') {
    return new Date(timestamp).toLocaleString();
  }
  return new Date(timestamp * 1000).toLocaleString();
};

// 生成头像颜色
const generateAvatarColor = (address) => {
  if (!address) return '#9e9e9e';
  const hash = address.split('').reduce((acc, char) => {
    return acc + char.charCodeAt(0);
  }, 0);
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 50%)`;
};

// 获取事件图标
const getEventIcon = (eventType) => {
  switch (eventType) {
    case 'task_completion':
      return <AssignmentIcon />;
    case 'training':
      return <SchoolIcon />;
    case 'capability_acquisition':
      return <PsychologyIcon />;
    case 'insight_discovery':
      return <LightbulbIcon />;
    case 'performance_analysis':
      return <InsightsIcon />;
    default:
      return <BarChartIcon />;
  }
};

// 获取事件颜色
const getEventColor = (eventType) => {
  switch (eventType) {
    case 'task_completion':
      return 'primary';
    case 'training':
      return 'secondary';
    case 'capability_acquisition':
      return 'success';
    case 'insight_discovery':
      return 'warning';
    case 'performance_analysis':
      return 'info';
    default:
      return 'default';
  }
};

// 学习时间线组件
const LearningTimeline = ({ events }) => {
  const navigate = useNavigate();

  return (
    <Timeline position="alternate">
      {events.map((event, index) => (
        <TimelineItem key={event.event_id}>
          <TimelineSeparator>
            <TimelineDot color={getEventColor(event.event_type)}>
              {getEventIcon(event.event_type)}
            </TimelineDot>
            {index < events.length - 1 && <TimelineConnector />}
          </TimelineSeparator>
          <TimelineContent>
            <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" component="div">
                {event.event_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatTimestamp(event.timestamp)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Avatar 
                  sx={{ 
                    width: 24, 
                    height: 24, 
                    mr: 1, 
                    bgcolor: generateAvatarColor(event.agent_id) 
                  }}
                >
                  {event.agent_id.substring(2, 4)}
                </Avatar>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { textDecoration: 'underline' }
                  }}
                  onClick={() => navigate(`/agents/${event.agent_id}`)}
                >
                  {formatAddress(event.agent_id)}
                </Typography>
              </Box>
              {event.data && (
                <Box sx={{ mt: 1 }}>
                  {event.data.task_id && (
                    <Chip 
                      label={`Task: ${event.data.task_id}`}
                      size="small"
                      sx={{ mr: 1, mt: 1 }}
                      onClick={() => navigate(`/tasks/${event.data.task_id}`)}
                    />
                  )}
                  {event.data.performance_score && (
                    <Chip 
                      label={`Score: ${event.data.performance_score}`}
                      size="small"
                      color="primary"
                      sx={{ mr: 1, mt: 1 }}
                    />
                  )}
                  {event.data.capability && (
                    <Chip 
                      label={`Capability: ${event.data.capability}`}
                      size="small"
                      color="success"
                      sx={{ mr: 1, mt: 1 }}
                    />
                  )}
                  {event.data.insights_gained && event.data.insights_gained.map((insight, i) => (
                    <Chip 
                      key={i}
                      label={insight}
                      size="small"
                      color="warning"
                      sx={{ mr: 1, mt: 1 }}
                    />
                  ))}
                </Box>
              )}
            </Paper>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  );
};

// 性能趋势图组件
const PerformanceTrendChart = ({ events }) => {
  // 准备图表数据
  const chartData = events
    .filter(event => event.data && event.data.performance_score)
    .map(event => ({
      timestamp: new Date(event.timestamp).toLocaleDateString(),
      score: event.data.performance_score,
      eventType: event.event_type
    }))
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  return (
    <Card>
      <CardHeader title="Performance Trend" />
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis domain={[0, 5]} />
            <RechartsTooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#8884d8" 
              activeDot={{ r: 8 }} 
              name="Performance Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 能力分布图组件
const CapabilityDistributionChart = ({ events }) => {
  // 提取所有能力
  const capabilities = new Map();
  
  events.forEach(event => {
    if (event.data && event.data.capability) {
      const capability = event.data.capability;
      capabilities.set(capability, (capabilities.get(capability) || 0) + 1);
    }
  });
  
  // 准备图表数据
  const chartData = Array.from(capabilities.entries()).map(([name, value]) => ({
    name,
    value
  }));

  // 饼图颜色
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <Card>
      <CardHeader title="Capability Distribution" />
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <RechartsTooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 事件类型分布图组件
const EventTypeDistributionChart = ({ events }) => {
  // 计算每种事件类型的数量
  const eventTypes = new Map();
  
  events.forEach(event => {
    const type = event.event_type;
    eventTypes.set(type, (eventTypes.get(type) || 0) + 1);
  });
  
  // 准备图表数据
  const chartData = Array.from(eventTypes.entries()).map(([name, value]) => ({
    name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value
  }));

  return (
    <Card>
      <CardHeader title="Event Type Distribution" />
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            <Bar dataKey="value" fill="#8884d8" name="Count" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// 洞察列表组件
const InsightsList = ({ events }) => {
  // 提取所有洞察
  const insights = [];
  
  events.forEach(event => {
    if (event.data && event.data.insights_gained) {
      event.data.insights_gained.forEach(insight => {
        insights.push({
          insight,
          timestamp: event.timestamp,
          agent_id: event.agent_id,
          event_id: event.event_id
        });
      });
    }
  });
  
  // 按时间排序
  insights.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  return (
    <Card>
      <CardHeader title="Learning Insights" />
      <CardContent>
        <List>
          {insights.length > 0 ? (
            insights.map((item, index) => (
              <React.Fragment key={`${item.event_id}-${index}`}>
                <ListItem>
                  <ListItemIcon>
                    <LightbulbIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.insight}
                    secondary={`${formatTimestamp(item.timestamp)} by ${formatAddress(item.agent_id)}`}
                  />
                </ListItem>
                {index < insights.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))
          ) : (
            <Typography variant="body2" color="text.secondary" align="center">
              No insights available
            </Typography>
          )}
        </List>
      </CardContent>
    </Card>
  );
};

const LearningVisualizer = () => {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [selectedEventType, setSelectedEventType] = useState('all');
  const [agents, setAgents] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);

  useEffect(() => {
    fetchLearningEvents();
  }, []);

  const fetchLearningEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await learningApi.getLearningEvents();
      if (response && response.events) {
        setEvents(response.events);
        
        // 提取所有代理和事件类型
        const agentSet = new Set();
        const eventTypeSet = new Set();
        
        response.events.forEach(event => {
          agentSet.add(event.agent_id);
          eventTypeSet.add(event.event_type);
        });
        
        setAgents(Array.from(agentSet));
        setEventTypes(Array.from(eventTypeSet));
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching learning events:', error);
      setError('Failed to fetch learning events. Using sample data instead.');
      setSnackbarOpen(true);
      
      // 模拟数据
      const mockEvents = [
        {
          event_id: "event_001",
          agent_id: "0x1234567890123456789012345678901234567890",
          event_type: "task_completion",
          data: {
            task_id: "task_123",
            performance_score: 4.8,
            insights_gained: ["market trend analysis improved", "sentiment detection enhanced"]
          },
          timestamp: "2023-08-10T09:15:00Z",
          transaction_hash: "0xabcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"
        },
        {
          event_id: "event_002",
          agent_id: "0x2345678901234567890123456789012345678901",
          event_type: "training",
          data: {
            model_version: "v2.1",
            training_duration: 3600,
            performance_improvement: 0.15,
            insights_gained: ["attention mechanism optimized"]
          },
          timestamp: "2023-08-11T14:22:00Z",
          transaction_hash: "0xefgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678efgh5678"
        },
        {
          event_id: "event_003",
          agent_id: "0x3456789012345678901234567890123456789012",
          event_type: "capability_acquisition",
          data: {
            capability: "image_recognition",
            source: "marketplace",
            cost: 0.25
          },
          timestamp: "2023-08-09T11:45:00Z",
          transaction_hash: "0xijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012ijkl9012"
        },
        {
          event_id: "event_004",
          agent_id: "0x1234567890123456789012345678901234567890",
          event_type: "task_completion",
          data: {
            task_id: "task_456",
            performance_score: 4.5,
            insights_gained: ["text summarization improved"]
          },
          timestamp: "2023-08-12T10:30:00Z",
          transaction_hash: "0xmnop3456mnop3456mnop3456mnop3456mnop3456mnop3456mnop3456mnop3456"
        },
        {
          event_id: "event_005",
          agent_id: "0x2345678901234567890123456789012345678901",
          event_type: "insight_discovery",
          data: {
            insight_type: "pattern",
            description: "Correlation between market volatility and sentiment scores",
            confidence: 0.92,
            insights_gained: ["market correlation pattern discovered"]
          },
          timestamp: "2023-08-13T15:45:00Z",
          transaction_hash: "0xqrst7890qrst7890qrst7890qrst7890qrst7890qrst7890qrst7890qrst7890"
        },
        {
          event_id: "event_006",
          agent_id: "0x1234567890123456789012345678901234567890",
          event_type: "performance_analysis",
          data: {
            performance_metrics: {
              accuracy: 0.95,
              latency: 120,
              efficiency: 0.87
            },
            insights_gained: ["response time optimization identified"]
          },
          timestamp: "2023-08-14T08:20:00Z",
          transaction_hash: "0xuvwx1234uvwx1234uvwx1234uvwx1234uvwx1234uvwx1234uvwx1234uvwx1234"
        },
        {
          event_id: "event_007",
          agent_id: "0x3456789012345678901234567890123456789012",
          event_type: "capability_acquisition",
          data: {
            capability: "natural_language_processing",
            source: "training",
            cost: 0.4
          },
          timestamp: "2023-08-15T13:10:00Z",
          transaction_hash: "0xyzab5678yzab5678yzab5678yzab5678yzab5678yzab5678yzab5678yzab5678"
        }
      ];
      
      setEvents(mockEvents);
      
      // 提取所有代理和事件类型
      const agentSet = new Set();
      const eventTypeSet = new Set();
      
      mockEvents.forEach(event => {
        agentSet.add(event.agent_id);
        eventTypeSet.add(event.event_type);
      });
      
      setAgents(Array.from(agentSet));
      setEventTypes(Array.from(eventTypeSet));
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  // 过滤事件
  const filteredEvents = events.filter(event => {
    let matchesAgent = selectedAgent === 'all' || event.agent_id === selectedAgent;
    let matchesEventType = selectedEventType === 'all' || event.event_type === selectedEventType;
    return matchesAgent && matchesEventType;
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
        <Typography variant="h4">Learning Visualizer</Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchLearningEvents}
        >
          Refresh
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={5}>
            <FormControl fullWidth size="small">
              <InputLabel>Agent</InputLabel>
              <Select
                value={selectedAgent}
                label="Agent"
                onChange={(e) => setSelectedAgent(e.target.value)}
              >
                <MenuItem value="all">All Agents</MenuItem>
                {agents.map(agent => (
                  <MenuItem key={agent} value={agent}>
                    {formatAddress(agent)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={5}>
            <FormControl fullWidth size="small">
              <InputLabel>Event Type</InputLabel>
              <Select
                value={selectedEventType}
                label="Event Type"
                onChange={(e) => setSelectedEventType(e.target.value)}
              >
                <MenuItem value="all">All Event Types</MenuItem>
                {eventTypes.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Typography variant="body2" color="text.secondary">
              {filteredEvents.length} events found
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
          <CircularProgress />
        </Box>
      ) : filteredEvents.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 5 }}>
          <Typography variant="h6" color="text.secondary">
            No learning events found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Try changing your filters or create new learning events
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Learning Timeline
              </Typography>
              <LearningTimeline events={filteredEvents} />
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <PerformanceTrendChart events={filteredEvents} />
          </Grid>

          <Grid item xs={12} md={6}>
            <EventTypeDistributionChart events={filteredEvents} />
          </Grid>

          <Grid item xs={12} md={6}>
            <CapabilityDistributionChart events={filteredEvents} />
          </Grid>

          <Grid item xs={12} md={6}>
            <InsightsList events={filteredEvents} />
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default LearningVisualizer;