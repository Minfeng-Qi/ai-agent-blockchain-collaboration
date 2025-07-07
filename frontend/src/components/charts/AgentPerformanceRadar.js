// Agent Performance Radar Chart Component
import React from 'react';
import { ResponsiveRadar } from '@nivo/radar';
import { Box, Typography, Paper, useTheme } from '@mui/material';

const AgentPerformanceRadar = ({ data, agentName = "Agent", loading = false, title = "Agent Performance Overview" }) => {
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
  console.log('📊 AgentPerformanceRadar received data:', data);
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
            No performance data available (received: {typeof data})
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, height: 400 }}>
      <Typography variant="h6" gutterBottom>
        {title} - {agentName}
      </Typography>
      <Box sx={{ height: 300 }}>
        <ResponsiveRadar
          data={data}
          keys={['current', 'potential']}
          indexBy="capability"
          valueFormat=">-.2f"
          margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
          borderColor={{ from: 'color' }}
          gridLevels={5}
          gridShape="circular"
          gridLabelOffset={36}
          enableDots={true}
          dotSize={8}
          dotColor={{ theme: 'background' }}
          dotBorderWidth={2}
          colors={[theme.palette.primary.main, theme.palette.secondary.main]}
          blendMode="multiply"
          motionConfig="wobbly"
          legends={[
            {
              anchor: 'top-left',
              direction: 'column',
              translateX: -50,
              translateY: -40,
              itemWidth: 80,
              itemHeight: 20,
              itemTextColor: theme.palette.text.primary,
              symbolSize: 12,
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
          tooltip={({ data, indexValue }) => (
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
                <strong>{indexValue}</strong>
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Current: {data.current}% | Potential: {data.potential}%
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
              }
            },
            grid: {
              line: {
                stroke: theme.palette.divider
              }
            }
          }}
        />
      </Box>
    </Paper>
  );
};

export default AgentPerformanceRadar;