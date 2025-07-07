// Task Completion Trend Chart Component
import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Box, Typography, Paper, useTheme } from '@mui/material';

const TaskCompletionTrendChart = ({ data, loading = false, title = "Task Completion Trend" }) => {
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
  console.log('📊 TaskCompletionTrendChart received data:', data);
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

  // 转换数据格式为Nivo Line Chart所需格式
  const chartData = [
    {
      id: 'Completed',
      color: theme.palette.success.main,
      data: data.map(item => ({
        x: item.date,
        y: item.completed
      }))
    },
    {
      id: 'Created',
      color: theme.palette.primary.main,
      data: data.map(item => ({
        x: item.date,
        y: item.created
      }))
    },
    {
      id: 'Failed',
      color: theme.palette.error.main,
      data: data.map(item => ({
        x: item.date,
        y: item.failed || 0
      }))
    }
  ];

  return (
    <Paper sx={{ p: 3, height: 400 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ height: 300 }}>
        <ResponsiveLine
          data={chartData}
          margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
          xScale={{ 
            type: 'time', 
            format: '%Y-%m-%d',
            useUTC: false,
            precision: 'day'
          }}
          xFormat="time:%Y-%m-%d"
          yScale={{
            type: 'linear',
            min: 'auto',
            max: 'auto',
            stacked: false,
            reverse: false
          }}
          curve="cardinal"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            format: '%m/%d',
            tickValues: 'every 3 days',
            legend: 'Date',
            legendOffset: 36,
            legendPosition: 'middle'
          }}
          axisLeft={{
            legend: 'Number of Tasks',
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          colors={{ scheme: 'category10' }}
          pointSize={6}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          useMesh={true}
          legends={[
            {
              anchor: 'bottom-right',
              direction: 'column',
              justify: false,
              translateX: 100,
              translateY: 0,
              itemsSpacing: 0,
              itemDirection: 'left-to-right',
              itemWidth: 80,
              itemHeight: 20,
              itemOpacity: 0.75,
              symbolSize: 12,
              symbolShape: 'circle',
              symbolBorderColor: 'rgba(0, 0, 0, .5)',
              effects: [
                {
                  on: 'hover',
                  style: {
                    itemBackground: 'rgba(0, 0, 0, .03)',
                    itemOpacity: 1
                  }
                }
              ]
            }
          ]}
          tooltip={({ point }) => (
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
                <strong>{point.serieId}</strong>: {point.data.y}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Date: {point.data.xFormatted}
              </Typography>
            </div>
          )}
          theme={{
            axis: {
              domain: {
                line: {
                  stroke: theme.palette.divider
                }
              },
              ticks: {
                line: {
                  stroke: theme.palette.divider
                },
                text: {
                  fill: theme.palette.text.secondary
                }
              },
              legend: {
                text: {
                  fill: theme.palette.text.primary,
                  fontSize: 12,
                  fontWeight: 600
                }
              }
            },
            grid: {
              line: {
                stroke: theme.palette.divider,
                strokeDasharray: '4 4'
              }
            },
            legends: {
              text: {
                fill: theme.palette.text.primary
              }
            }
          }}
          animate={true}
          motionStiffness={120}
          motionDamping={50}
        />
      </Box>
    </Paper>
  );
};

export default TaskCompletionTrendChart;