// Earnings Analysis Chart Component
import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Box, Typography, Paper, useTheme, Grid, Chip } from '@mui/material';

const EarningsChart = ({ data, loading = false, title = "Earnings Analysis" }) => {
  const theme = useTheme();

  if (loading) {
    return (
      <Paper sx={{ p: 3, height: 450 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: 350 
        }}>
          Loading...
        </Box>
      </Paper>
    );
  }

  // Debug logging
  console.log('📊 EarningsChart received data:', data);
  console.log('📊 Data type:', typeof data);

  if (!data || !data.dailyEarnings || !Array.isArray(data.dailyEarnings) || data.dailyEarnings.length === 0) {
    return (
      <Paper sx={{ p: 3, height: 450 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: 350 
        }}>
          <Typography color="text.secondary">
            No earnings data available (received: {typeof data})
          </Typography>
        </Box>
      </Paper>
    );
  }

  // 准备图表数据
  const chartData = [
    {
      id: 'Total Earnings',
      color: theme.palette.primary.main,
      data: data.dailyEarnings.map(item => ({
        x: item.date,
        y: item.totalEarnings
      }))
    },
    {
      id: 'Agent Earnings',
      color: theme.palette.secondary.main,
      data: data.dailyEarnings.map(item => ({
        x: item.date,
        y: item.agentEarnings
      }))
    }
  ];

  return (
    <Paper sx={{ p: 3, height: 450 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      {/* Top Earners */}
      {data.topEarners && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Top Earners:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {data.topEarners.slice(0, 4).map((earner, index) => (
              <Chip
                key={index}
                label={`${earner.agent}: ${earner.earnings} ETH`}
                size="small"
                color={index === 0 ? 'primary' : 'default'}
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      )}

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
          yFormat=" >-.2f"
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
            legend: 'Earnings (ETH)',
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          colors={{ scheme: 'paired' }}
          pointSize={8}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabelYOffset={-12}
          useMesh={true}
          enableArea={true}
          areaOpacity={0.1}
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
                <strong>{point.serieId}</strong>: {point.data.yFormatted} ETH
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

export default EarningsChart;