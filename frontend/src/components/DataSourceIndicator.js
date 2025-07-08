import React, { useState, useEffect } from 'react';
import { 
  Chip, 
  Tooltip, 
  IconButton, 
  Box, 
  Alert,
  Collapse,
  Typography,
  LinearProgress
} from '@mui/material';
import {
  Cloud as CloudIcon,
  CloudOff as CloudOffIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Storage as StorageIcon,
  Computer as ComputerIcon
} from '@mui/icons-material';
import { api, serviceMonitor } from '../services/api';

/**
 * 数据源状态指示器组件
 * 显示当前使用的数据源（后端/Mock）和连接状态
 */
const DataSourceIndicator = ({ 
  showDetails = false, 
  onStatusChange = null,
  style = {},
  variant = 'outlined' // 'filled' | 'outlined'
}) => {
  const [serviceStatus, setServiceStatus] = useState({
    backend_available: null,
    data_source: 'unknown',
    last_check: null
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showDetailPanel, setShowDetailPanel] = useState(false);

  useEffect(() => {
    // 获取初始状态
    updateServiceStatus();

    // 监听服务状态变化
    const removeListener = serviceMonitor.addStatusListener((isAvailable, previousStatus) => {
      setServiceStatus({
        backend_available: isAvailable,
        data_source: isAvailable ? 'backend' : 'mock',
        last_check: Date.now()
      });

      // 通知父组件状态变化
      if (onStatusChange) {
        onStatusChange(isAvailable, previousStatus);
      }
    });

    return () => {
      removeListener();
    };
  }, [onStatusChange]);

  const updateServiceStatus = () => {
    const status = api.getServiceStatus();
    setServiceStatus({
      backend_available: status.backend_available,
      data_source: status.data_source,
      last_check: status.status_info.lastCheck
    });
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await api.refreshServiceStatus();
      updateServiceStatus();
    } catch (error) {
      console.error('Failed to refresh service status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusChipProps = () => {
    const { backend_available, data_source } = serviceStatus;
    
    if (backend_available === null) {
      return {
        label: 'Checking...',
        color: 'default',
        icon: <ComputerIcon />,
        variant: variant
      };
    }
    
    if (backend_available) {
      return {
        label: 'Backend Connected',
        color: 'success',
        icon: <CloudIcon />,
        variant: variant
      };
    } else {
      return {
        label: 'Demo Mode (Mock Data)',
        color: 'warning',
        icon: <StorageIcon />,
        variant: variant
      };
    }
  };

  const getTooltipTitle = () => {
    const { backend_available, data_source, last_check } = serviceStatus;
    
    if (backend_available === null) {
      return 'Checking backend service status...';
    }
    
    const lastCheckTime = last_check ? new Date(last_check).toLocaleTimeString() : 'Never';
    
    if (backend_available) {
      return `Connected to backend service\nData source: Real-time data\nLast check: ${lastCheckTime}`;
    } else {
      return `Backend service unavailable\nData source: Enhanced demo data\nLast check: ${lastCheckTime}\n\nClick refresh to retry connection`;
    }
  };

  const chipProps = getStatusChipProps();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ...style }}>
      <Tooltip title={getTooltipTitle()} arrow>
        <Chip
          {...chipProps}
          size="small"
          onClick={() => setShowDetailPanel(!showDetailPanel)}
          sx={{ 
            cursor: 'pointer',
            '& .MuiChip-icon': {
              fontSize: '1rem'
            }
          }}
        />
      </Tooltip>

      <Tooltip title="Refresh connection status">
        <IconButton 
          size="small" 
          onClick={handleRefresh}
          disabled={isRefreshing}
          sx={{ opacity: isRefreshing ? 0.6 : 1 }}
        >
          {isRefreshing ? (
            <RefreshIcon sx={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <RefreshIcon />
          )}
        </IconButton>
      </Tooltip>

      {showDetails && (
        <Tooltip title="Show connection details">
          <IconButton 
            size="small" 
            onClick={() => setShowDetailPanel(!showDetailPanel)}
            color={showDetailPanel ? 'primary' : 'default'}
          >
            <InfoIcon />
          </IconButton>
        </Tooltip>
      )}

      {/* 详细信息面板 */}
      {showDetails && (
        <Collapse in={showDetailPanel} sx={{ position: 'absolute', top: '100%', left: 0, zIndex: 1000, mt: 1 }}>
          <Alert 
            severity={serviceStatus.backend_available ? 'success' : 'info'}
            sx={{ minWidth: 300 }}
          >
            <Typography variant="subtitle2" gutterBottom>
              Service Status Details
            </Typography>
            
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>Backend:</strong> {serviceStatus.backend_available ? 'Available' : 'Unavailable'}
              </Typography>
              <Typography variant="body2">
                <strong>Data Source:</strong> {serviceStatus.data_source === 'backend' ? 'Real-time API' : 'Enhanced Demo Data'}
              </Typography>
              <Typography variant="body2">
                <strong>Last Check:</strong> {
                  serviceStatus.last_check 
                    ? new Date(serviceStatus.last_check).toLocaleString()
                    : 'Never'
                }
              </Typography>
            </Box>

            {!serviceStatus.backend_available && (
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  Don't worry! The demo mode provides rich, realistic data to showcase all system features.
                </Typography>
              </Box>
            )}
          </Alert>
        </Collapse>
      )}

      {/* 加载进度指示器 */}
      {isRefreshing && (
        <Box sx={{ position: 'absolute', top: '100%', left: 0, right: 0, mt: 0.5 }}>
          <LinearProgress size="small" />
        </Box>
      )}

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </Box>
  );
};

export default DataSourceIndicator;