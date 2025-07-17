import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Alert,
  Paper,
  Tooltip,
  Avatar,
  CircularProgress,
  Snackbar,
  Badge,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Assignment as AssignmentIcon,
  AccountCircle as AccountCircleIcon,
  MonetizationOn as MonetizationOnIcon,
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CloudOff as CloudOffIcon,
  Cloud as CloudIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import { 
  TaskStatusChart, 
  AgentCapabilitiesChart, 
  TaskCompletionTrendChart,
  AgentPerformanceRadar,
  EarningsChart 
} from './charts';
import { enhancedMockData } from '../services/enhancedMockData';
import smartDataService from '../services/smartDataService';

const EnhancedDashboard = () => {
  // 状态管理
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30秒
  const [showDataSource, setShowDataSource] = useState(true);

  // 数据刷新函数
  const fetchDashboardData = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);

      console.log('🔄 Loading dashboard data from SmartDataService...');
      
      // 恢复使用SmartDataService，但添加稳定性处理
      const results = await Promise.allSettled([
        smartDataService.getSystemStatus(),
        smartDataService.getTaskStatusDistribution(),
        smartDataService.getAgentCapabilitiesDistribution(),
        smartDataService.getTaskCompletionTrend(),
        smartDataService.getEarningsAnalysis(),
        smartDataService.getAgentCapabilityRadar('top_agent'),
        smartDataService.getAgentPerformanceData(),
        smartDataService.getRealTimeMetrics(),
        smartDataService.getAgentLearningStatistics()
      ]);

      // 处理结果，确保数据结构正确
      const data = {};
      const dataKeys = [
        'systemStatus', 'taskStatusDistribution', 'agentCapabilities',
        'taskCompletionTrend', 'earningsAnalysis', 'agentCapabilityRadar',
        'agentPerformance', 'realTimeMetrics', 'agentLearningStatistics'
      ];

      let backendOnline = false;

      results.forEach((result, index) => {
        const key = dataKeys[index];
        if (result.status === 'fulfilled' && result.value) {
          // 解包SmartDataService返回的数据结构
          if (result.value.data !== undefined) {
            data[key] = result.value.data;
            if (result.value.source === 'backend' || result.value.source === 'contract') {
              backendOnline = true;
            }
          } else {
            data[key] = result.value;
          }
          
          console.log(`📊 ${key}:`, data[key], `(source: ${result.value.source || 'unknown'})`);
        } else {
          console.warn(`Failed to load ${key}:`, result.reason);
          // 使用fallback数据
          switch(key) {
            case 'systemStatus':
              data[key] = enhancedMockData.getSystemStatus();
              break;
            case 'taskStatusDistribution':
              data[key] = enhancedMockData.getTaskStatusDistribution();
              break;
            case 'agentCapabilities':
              data[key] = enhancedMockData.getAgentCapabilitiesDistribution();
              break;
            case 'taskCompletionTrend':
              data[key] = enhancedMockData.getTaskCompletionTrend();
              break;
            case 'earningsAnalysis':
              data[key] = enhancedMockData.getEarningsAnalysis();
              break;
            case 'agentCapabilityRadar':
              data[key] = enhancedMockData.getAgentCapabilityRadar('top_agent');
              break;
            case 'agentPerformance':
              data[key] = enhancedMockData.getAgentPerformanceData();
              break;
            case 'realTimeMetrics':
              data[key] = enhancedMockData.getRealTimeTaskExecution();
              break;
            case 'agentLearningStatistics':
              data[key] = enhancedMockData.getAgentLearningStatistics();
              break;
            default:
              data[key] = null;
          }
        }
      });

      data.isBackendOnline = backendOnline;
      data.lastUpdate = new Date().toISOString();
      
      setDashboardData(data);
      setIsBackendOnline(backendOnline);
      setLastUpdate(new Date().toISOString());

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
      // 完全fallback到mock数据
      const fallbackData = {
        systemStatus: enhancedMockData.getSystemStatus(),
        taskStatusDistribution: enhancedMockData.getTaskStatusDistribution(),
        agentCapabilities: enhancedMockData.getAgentCapabilitiesDistribution(),
        taskCompletionTrend: enhancedMockData.getTaskCompletionTrend(),
        earningsAnalysis: enhancedMockData.getEarningsAnalysis(),
        agentCapabilityRadar: enhancedMockData.getAgentCapabilityRadar('top_agent'),
        agentPerformance: enhancedMockData.getAgentPerformanceData(),
        realTimeMetrics: enhancedMockData.getRealTimeTaskExecution(),
        agentLearningStatistics: enhancedMockData.getAgentLearningStatistics(),
        isBackendOnline: false,
        lastUpdate: new Date().toISOString()
      };
      setDashboardData(fallbackData);
      setIsBackendOnline(false);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  // 初始化 - 恢复受控的自动刷新
  useEffect(() => {
    fetchDashboardData();
    
    // 添加状态监听器，但不触发立即刷新避免循环
    const removeListener = smartDataService.addStatusListener((status) => {
      console.log('📡 Backend status changed:', status.isOnline);
      setIsBackendOnline(status.isOnline);
      // 仅在状态变化时更新，避免频繁刷新
    });

    // 设置较长的自动刷新间隔，避免频繁请求
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        console.log('⏰ Auto refresh triggered');
        fetchDashboardData(false); // 不显示loading状态，避免闪烁
      }, 60000); // 改为60秒刷新一次
    }

    return () => {
      if (interval) clearInterval(interval);
      removeListener();
    };
  }, [autoRefresh, fetchDashboardData]); // 添加必要的依赖

  // 手动刷新
  const handleManualRefresh = () => {
    fetchDashboardData(true);
  };

  // 获取状态图标和颜色
  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'online':
      case 'active':
        return <CheckCircleIcon color="success" />;
      case 'error':
      case 'offline':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      connected: 'success',
      online: 'success',
      active: 'success',
      error: 'error',
      offline: 'error',
      warning: 'warning',
      pending: 'info',
      in_progress: 'primary'
    };
    return colors[status] || 'default';
  };

  // 渲染系统状态卡片
  const renderSystemStatusCards = () => {
    const systemStatus = dashboardData.systemStatus;
    if (!systemStatus) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* 后端连接状态 */}
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Badge
                    variant="dot"
                    color={isBackendOnline ? 'success' : 'error'}
                    sx={{ mr: 1 }}
                  >
                    {isBackendOnline ? <CloudIcon /> : <CloudOffIcon />}
                  </Badge>
                  <Typography variant="h6">
                    Backend Status
                  </Typography>
                </Box>
                <Typography variant="h4" color={isBackendOnline ? 'success.main' : 'error.main'}>
                  {isBackendOnline ? 'Online' : 'Offline'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {isBackendOnline ? 'Live Data' : 'Mock Data'}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* 活跃代理 */}
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccountCircleIcon sx={{ mr: 1 }} color="primary" />
                  <Typography variant="h6">Active Agents</Typography>
                </Box>
                <Typography variant="h4" component="div">
                  {systemStatus.agents?.active || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total: {systemStatus.agents?.total || 0}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* 任务统计 */}
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AssignmentIcon sx={{ mr: 1 }} color="secondary" />
                  <Typography variant="h6">Tasks</Typography>
                </Box>
                <Typography variant="h4" component="div">
                  {systemStatus.tasks?.completed || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Completed / {systemStatus.tasks?.total || 0} Total
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* 区块链状态 */}
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TimelineIcon sx={{ mr: 1 }} color="info" />
                  <Typography variant="h6">Blockchain</Typography>
                </Box>
                <Typography variant="h4" component="div">
                  {systemStatus.blockchain?.blockHeight ? 
                    `${Math.floor(systemStatus.blockchain.blockHeight / 1000)}K` : 
                    'N/A'
                  }
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Block Height
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    );
  };

  // 渲染图表部分
  const renderChartsSection = () => {
    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* 任务状态分布 */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <TaskStatusChart 
              data={dashboardData.taskStatusDistribution}
              loading={loading}
              title="Task Status Distribution"
            />
          </motion.div>
        </Grid>

        {/* 代理能力分布 */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <AgentCapabilitiesChart 
              data={dashboardData.agentCapabilities}
              loading={loading}
              title="Agent Capabilities Distribution"
            />
          </motion.div>
        </Grid>

        {/* 任务完成趋势 */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <TaskCompletionTrendChart 
              data={dashboardData.taskCompletionTrend}
              loading={loading}
              title="Task Completion Trend (Last 30 Days)"
            />
          </motion.div>
        </Grid>
      </Grid>
    );
  };

  // 渲染高级分析图表
  const renderAdvancedChartsSection = () => {
    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* 代理性能雷达图 */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <AgentPerformanceRadar 
              data={dashboardData.agentCapabilityRadar}
              agentName={Array.isArray(dashboardData.agentPerformance) && dashboardData.agentPerformance[0]?.name || "Top Agent"}
              loading={loading}
              title="Agent Performance Radar"
            />
          </motion.div>
        </Grid>

        {/* 收益分析图表 */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <EarningsChart 
              data={dashboardData.earningsAnalysis}
              loading={loading}
              title="Earnings Analysis"
            />
          </motion.div>
        </Grid>
      </Grid>
    );
  };

  // 渲染代理表现部分
  const renderAgentPerformanceSection = () => {
    const agentData = dashboardData.agentPerformance || [];
    
    // Debug logging
    console.log('🔍 Agent Performance Data:', agentData);
    console.log('🔍 Is Array:', Array.isArray(agentData));
    console.log('🔍 Type:', typeof agentData);
    
    // 确保agentData是数组
    const safeAgentData = Array.isArray(agentData) ? agentData : [];
    
    return (
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Agent Performance Overview
          </Typography>
          
          {safeAgentData.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3, width: '100%' }}>
              <Typography color="text.secondary">
                No agent performance data available
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {safeAgentData.slice(0, 6).map((agent, index) => (
                <Grid item xs={12} sm={6} md={4} key={agent.id || index}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                        {agent.name?.charAt(0) || 'A'}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2" noWrap>
                          {agent.name || 'Unknown Agent'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Reputation: {agent.reputation || 0}%
                        </Typography>
                      </Box>
                    </Box>
                    
                    <LinearProgress 
                      variant="determinate" 
                      value={agent.reputation || 0} 
                      sx={{ mb: 1, height: 6 }}
                    />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption">
                        Tasks: {agent.tasksCompleted || 0}
                      </Typography>
                      <Typography variant="caption">
                        Rate: {agent.successRate || 0}%
                      </Typography>
                    </Box>
                  </Paper>
                </motion.div>
              </Grid>
            ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    );
  };

  // 渲染实时指标
  const renderRealTimeMetrics = () => {
    const realTimeData = dashboardData.realTimeMetrics?.data;
    if (!realTimeData) return null;

    return (
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Real-Time Metrics
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Active Task Executions
              </Typography>
              {realTimeData.activeExecutions?.map((execution, index) => (
                <Box key={execution.taskId || index} sx={{ mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2">{execution.title}</Typography>
                    <Chip size="small" label={`${execution.progress}%`} color="primary" />
                  </Box>
                  <LinearProgress variant="determinate" value={execution.progress} sx={{ mb: 1 }} />
                  <Typography variant="caption" color="text.secondary">
                    Agent: {execution.agent} | Step: {execution.currentStep}
                  </Typography>
                </Box>
              )) || <Typography variant="body2" color="text.secondary">No active executions</Typography>}
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Queue Metrics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Tasks in Queue:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {realTimeData.queueMetrics?.totalInQueue || 0}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Avg Wait Time:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {realTimeData.queueMetrics?.avgWaitTime || 0}s
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Throughput/Hour:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {realTimeData.queueMetrics?.throughputPerHour || 0}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // 渲染学习仪表盘
  const renderLearningDashboard = () => {
    const learningData = dashboardData.agentLearningStatistics?.data || dashboardData.agentLearningStatistics;
    if (!learningData || !learningData.agents) return null;

    const { agents, summary } = learningData;

    return (
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Learning Dashboard
            <Chip
              size="small"
              label="Updated by Evaluations"
              color="primary"
              variant="outlined"
              sx={{ ml: 2 }}
            />
          </Typography>

          {/* 学习摘要 */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary.main">
                  {summary.total_agents}
                </Typography>
                <Typography variant="caption">Active Agents</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {summary.avg_reputation}%
                </Typography>
                <Typography variant="caption">Avg Reputation</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {summary.avg_success_rate}%
                </Typography>
                <Typography variant="caption">Success Rate</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {summary.total_evaluations}
                </Typography>
                <Typography variant="caption">Total Evaluations</Typography>
              </Paper>
            </Grid>
          </Grid>

          <Divider sx={{ mb: 3 }} />

          {/* Agent表现 */}
          <Typography variant="subtitle1" gutterBottom>
            Agent Performance (Updated by Task Evaluations)
          </Typography>
          
          <Grid container spacing={2}>
            {agents.slice(0, 6).map((agent, index) => (
              <Grid item xs={12} sm={6} md={4} key={agent.agent_id || index}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                        {agent.agent_name?.charAt(0) || 'A'}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2" noWrap>
                          {agent.agent_name || 'Unknown Agent'}
                        </Typography>
                        <Chip
                          size="small"
                          label={agent.performance_trend}
                          color={
                            agent.performance_trend === 'improving' ? 'success' :
                            agent.performance_trend === 'stable' ? 'primary' : 'warning'
                          }
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Reputation: {agent.reputation}% 
                        <Chip size="small" label={`+${agent.recent_evaluations} evals`} sx={{ ml: 1 }} />
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={agent.reputation} 
                        sx={{ mt: 0.5, height: 6 }}
                      />
                    </Box>
                    
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Success Rate
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {agent.success_rate}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Avg Score
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {agent.average_score?.toFixed(1) || 'N/A'}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Tasks Done
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {agent.tasks_completed}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Avg Reward
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {agent.average_reward?.toFixed(2) || 'N/A'} ETH
                        </Typography>
                      </Grid>
                    </Grid>

                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Last eval: {agent.last_evaluation ? new Date(agent.last_evaluation).toLocaleDateString() : 'N/A'}
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>
            ))}
          </Grid>

          {/* 表现趋势 */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Performance Distribution
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Improving: {summary.performance_distribution?.improving || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <InfoIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Stable: {summary.performance_distribution?.stable || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WarningIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Declining: {summary.performance_distribution?.declining || 0}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    );
  };

  if (loading && !dashboardData.systemStatus) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" gutterBottom>
            Enhanced AI Agent Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title={showDataSource ? "Hide Data Sources" : "Show Data Sources"}>
              <IconButton onClick={() => setShowDataSource(!showDataSource)}>
                {showDataSource ? <VisibilityIcon /> : <VisibilityOffIcon />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Refresh Dashboard">
              <IconButton onClick={handleManualRefresh} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            
            <Chip 
              icon={isBackendOnline ? <CloudIcon /> : <CloudOffIcon />}
              label={isBackendOnline ? 'Live Data' : 'Mock Data'}
              color={isBackendOnline ? 'success' : 'warning'}
              variant="outlined"
            />
          </Box>
        </Box>
        
        <Typography variant="subtitle1" color="text.secondary">
          Comprehensive AI Agent System Monitoring & Analytics
        </Typography>
        
        {lastUpdate && (
          <Typography variant="caption" color="text.secondary">
            Last updated: {new Date(lastUpdate).toLocaleTimeString()}
          </Typography>
        )}
      </Box>

      {/* Data Source Information */}
      <AnimatePresence>
        {showDataSource && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Alert severity={isBackendOnline ? 'success' : 'info'} sx={{ mb: 3 }}>
              <Typography variant="body2">
                {isBackendOnline 
                  ? 'Connected to live backend services. Data is real-time and synchronized.'
                  : 'Backend services are offline. Displaying comprehensive mock data for demonstration.'
                }
              </Typography>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* System Status Cards */}
      {renderSystemStatusCards()}

      {/* Charts Section */}
      {renderChartsSection()}

      {/* Advanced Charts Section */}
      {renderAdvancedChartsSection()}

      {/* Agent Performance Section */}
      {renderAgentPerformanceSection()}

      {/* Learning Dashboard */}
      {renderLearningDashboard()}

      {/* Real-Time Metrics */}
      {renderRealTimeMetrics()}

      {/* Error Snackbar */}
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EnhancedDashboard;