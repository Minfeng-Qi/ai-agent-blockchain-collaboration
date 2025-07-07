// Agent Capabilities Distribution Chart Component
import React from 'react';
import { ResponsiveBar } from '@nivo/bar';
import { Box, Typography, Paper, useTheme } from '@mui/material';

const AgentCapabilitiesChart = ({ data, loading = false, title = "Agent Capabilities Distribution" }) => {
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
  console.log('📊 AgentCapabilitiesChart received data:', data);
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
    capability: item.capability.length > 15 
      ? item.capability.substring(0, 15) + '...' 
      : item.capability,
    fullCapability: item.capability,
    count: item.count,
    percentage: item.percentage
  }));

  return (
    <Paper sx={{ p: 3, height: 400 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ height: 300 }}>
        <ResponsiveBar
          data={chartData}
          keys={['count']}
          indexBy="capability"
          margin={{ top: 50, right: 60, bottom: 80, left: 80 }}
          padding={0.3}
          valueScale={{ type: 'linear' }}
          indexScale={{ type: 'band', round: true }}
          colors={{ scheme: 'set3' }}
          borderColor={{
            from: 'color',
            modifiers: [['darker', 1.6]]
          }}
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: -45,
            legend: 'Capabilities',
            legendPosition: 'middle',
            legendOffset: 60,
            format: value => value
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Number of Agents',
            legendPosition: 'middle',
            legendOffset: -60
          }}
          labelSkipWidth={12}
          labelSkipHeight={12}
          labelTextColor={{
            from: 'color',
            modifiers: [['darker', 1.6]]
          }}
          tooltip={({ data }) => (
            <div
              style={{
                background: theme.palette.background.paper,
                padding: '9px 12px',
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: 4,
                boxShadow: theme.shadows[4],
                maxWidth: 250
              }}
            >
              <Typography variant="body2">
                <strong>{data.fullCapability}</strong>
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Agents with this capability: {data.count}
              </Typography>
              <br />
              <Typography variant="caption" color="text.secondary">
                Percentage: {data.percentage}%
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
                  fill: theme.palette.text.secondary,
                  fontSize: 11
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
            }
          }}
          animate={true}
          motionStiffness={90}
          motionDamping={15}
        />
      </Box>
    </Paper>
  );
};

export default AgentCapabilitiesChart;