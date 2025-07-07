// Task Status Distribution Chart Component
import React from 'react';
import { ResponsivePie } from '@nivo/pie';
import { Box, Typography, Paper, useTheme } from '@mui/material';

const TaskStatusChart = ({ data, loading = false, title = "Task Status Distribution" }) => {
  const theme = useTheme();

  if (loading) {
    return (
      <Paper sx={{ p: 3, height: 400 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: 300 
        }}>
          Loading...
        </Box>
      </Paper>
    );
  }

  // Debug logging
  console.log('📊 TaskStatusChart received data:', data);
  console.log('📊 Data type:', typeof data, 'Is Array:', Array.isArray(data));

  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <Paper sx={{ p: 3, height: 400 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: 300 
        }}>
          <Typography color="text.secondary">
            No data available (received: {typeof data})
          </Typography>
        </Box>
      </Paper>
    );
  }

  const chartData = data.map((item, index) => ({
    id: item.id,
    label: item.label,
    value: item.value
  }));

  // 自定义颜色映射
  const customColors = data.map(item => item.color || ['#4caf50', '#2196f3', '#ff9800', '#f44336'][data.indexOf(item) % 4]);

  return (
    <Paper sx={{ p: 3, height: 400 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ height: 300 }}>
        <ResponsivePie
          data={chartData}
          margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
          innerRadius={0.5}
          padAngle={0.7}
          cornerRadius={3}
          activeOuterRadiusOffset={8}
          colors={{ scheme: 'set2' }}
          borderWidth={1}
          borderColor={{
            from: 'color',
            modifiers: [['darker', 0.2]]
          }}
          arcLinkLabelsSkipAngle={10}
          arcLinkLabelsTextColor={theme.palette.text.primary}
          arcLinkLabelsThickness={2}
          arcLinkLabelsColor={{ from: 'color' }}
          arcLabelsSkipAngle={10}
          arcLabelsTextColor={{
            from: 'color',
            modifiers: [['darker', 2]]
          }}
          tooltip={({ datum }) => (
            <div
              style={{
                background: theme.palette.background.paper,
                padding: '9px 12px',
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: 4,
                boxShadow: theme.shadows[4]
              }}
            >
              <Typography variant="body2">
                <strong>{datum.label}</strong>: {datum.value}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {((datum.value / chartData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(1)}%
              </Typography>
            </div>
          )}
          legends={[
            {
              anchor: 'bottom',
              direction: 'row',
              justify: false,
              translateX: 0,
              translateY: 56,
              itemsSpacing: 0,
              itemWidth: 100,
              itemHeight: 18,
              itemTextColor: theme.palette.text.primary,
              itemDirection: 'left-to-right',
              itemOpacity: 1,
              symbolSize: 18,
              symbolShape: 'circle',
              effects: [
                {
                  on: 'hover',
                  style: {
                    itemTextColor: theme.palette.text.primary
                  }
                }
              ]
            }
          ]}
        />
      </Box>
    </Paper>
  );
};

export default TaskStatusChart;